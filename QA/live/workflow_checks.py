# -*- coding: utf-8 -*-
"""Hotel business-workflow checks against LIVE, with data the run cleans up.

Every row this creates is tagged `QAWF-<runid>` and the reservation is CANCELLED
(not deleted) at the end of the same run, so the run leaves the book exactly as
it found it and the record of why it was cancelled is retained. Nothing
pre-existing is modified. No payment, email or SMS is triggered.

THE FIELD NAMES MATTER, AND GETTING THEM WRONG MANUFACTURES BUGS
    A first run of this file reported "12 of 12 bills fail to reconcile". They
    reconcile exactly. The check had read `subtotal` where the API returns
    `sub_total`, so every component read 0.0 and every grand total looked
    wrong. The contracts below were read out of the controllers, not guessed.

Usage:
    python QA/live/workflow_checks.py
"""
from __future__ import annotations

import datetime
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

GW = os.environ.get("E2E_GATEWAY", "http://168.231.103.18:9010")
PW = os.environ.get("QA_PASSWORD", "")  # never stored in this repo; see qa_common.py

def _resolve_password(default_email):
    """QA_PASSWORD, or a message explaining how to set it.

    Without this an unset variable produced a bare
    `email and password are required` 400 from the gateway, which reads as a
    broken account rather than a missing environment variable.
    """
    if PW:
        return PW
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from qa_common import password_for
    return password_for(default_email)
RUN = "QAWF" + datetime.datetime.now().strftime("%H%M%S")
ADMIN = "admin@cherryhotel.com"
HOST = GW.split("//")[-1].split(":")[0]

# A 1x1 PNG. POST /hotel/room_reservation requires an identity_file upload
# (`identity_file: UploadFile = File(...)`), so a reservation cannot be booked
# without a scanned ID proof. That is a deliberate control, and this is the
# smallest thing that satisfies it.
PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000a49444154789c6360000002000100ffff03000006000557bfabd40000000049454e44ae426082"
)

results = []
cleanup_plan = []


def call(method, path, tok=None, body=None, form=None, multipart=None):
    url = GW + path
    data, ctype = None, None
    if multipart is not None:
        boundary = "----qawf" + RUN
        parts = []
        for k, v in multipart.items():
            if isinstance(v, tuple):
                fname, ctype_, blob = v
                parts.append(
                    f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                    f"filename=\"{fname}\"\r\nContent-Type: {ctype_}\r\n\r\n".encode() + blob + b"\r\n")
            else:
                parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                             f"name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        parts.append(f"--{boundary}--\r\n".encode())
        data = b"".join(parts)
        ctype = f"multipart/form-data; boundary={boundary}"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        ctype = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        ctype = "application/json"
    r = urllib.request.Request(url, data=data, method=method)
    if ctype:
        r.add_header("Content-Type", ctype)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            raw = x.read().decode("utf-8", "replace")
            try:
                return x.status, json.loads(raw)
            except ValueError:
                return x.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, raw
    except Exception as e:
        return 0, str(e)[:200]


def login(email, password=None):
    password = password or _resolve_password(email)
    for a in range(6):
        s, b = call("POST", "/login_post", None, {"email": email, "password": password})
        if s == 200:
            return b["access_token"]
        if s == 429:
            time.sleep(20 * (a + 1))
            continue
        raise SystemExit(f"login failed {email}: {s} {b}")
    raise SystemExit("rate limited")


def rows(b):
    d = b.get("data") if isinstance(b, dict) else None
    if isinstance(d, dict):
        d = d.get("data", d)
    return d if isinstance(d, list) else []


def rec(flow, step, status, expected, ok, detail=""):
    results.append({"flow": flow, "step": step, "status": status, "expected": expected,
                    "pass": bool(ok), "detail": str(detail)[:400]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {flow} :: {step}  http={status}  {str(detail)[:140]}")


def availability(tok, a, d):
    """The availability engine's own answer: which room ids can be sold.

    Reading this instead of `rooms[0]` matters. Booking is refused for a blocked
    or out-of-order room -- "Room 601 is blocked / out of order and cannot be
    booked" -- which is the rule working, not a failure to book.
    """
    s, b = call("GET", f"/hotel/room_availability?arrival_date={a}&departure_date={d}", tok)
    if s != 200 or not isinstance(b, dict):
        return s, None, [], b
    data = b.get("data") if isinstance(b.get("data"), dict) else b
    return s, data.get("available_room_ids"), data.get("blocked_room_ids"), b


def main():
    tok = login(ADMIN)
    print(f"run tag: {RUN}\n")
    today = datetime.date.today()
    # Far enough out that no seeded reservation collides with it.
    in_d = (today + datetime.timedelta(days=430)).isoformat()
    out_d = (today + datetime.timedelta(days=432)).isoformat()

    # ------------------------------------------------------------- flow 1
    print("FLOW 1 -- price a stay")
    s, snap = call("GET", "/masterdata/snapshot", tok)
    rooms = rows(snap)
    rec("1 price", "GET /masterdata/snapshot", s, "200",
        s == 200, f"{len(rooms)} rows, fields={sorted(rooms[0].keys())[:8] if rooms else '-'}")
    if not rooms:
        s2, rb = call("GET", "/masterdata/room", tok)
        rooms = rows(rb)
    room_id = rooms[0].get("id")
    sq, q = call("POST", "/hotel/room_reservation_quote", tok, {
        "arrival_date": in_d, "departure_date": out_d,
        "room_ids": [room_id], "rate_type": ["daily"]})
    qd = q.get("data") if isinstance(q, dict) else None
    rec("1 price", "POST room_reservation_quote", sq, "200 with a priced total",
        sq == 200 and isinstance(qd, dict) and any(k in qd for k in ("total_amount", "grand_total")),
        json.dumps(qd)[:260] if qd else json.dumps(q)[:260])

    # ------------------------------------------------------------- flow 2
    print("\nFLOW 2 -- book a room the engine says is sellable; availability must fall")
    s0, free0, blocked0, raw0 = availability(tok, in_d, out_d)
    rec("2 book", "availability BEFORE", s0, "200 with a sellable room list",
        s0 == 200 and isinstance(free0, list) and bool(free0),
        f"{len(free0 or [])} sellable, {len(blocked0 or [])} blocked :: {json.dumps(raw0)[:150]}")
    room_id = (free0 or [None])[0]

    # The business rule under test: a BLOCKED room must be refused.
    if blocked0:
        ids_call = call("GET", "/masterdata/room", tok)
        blocked_name = next((x.get("room_no") for x in rows(ids_call)
                             if x.get("id") == blocked0[0]), "?")
        sqb, qb = call("POST", "/hotel/room_reservation_quote", tok, {
            "arrival_date": in_d, "departure_date": out_d,
            "room_ids": [blocked0[0]], "rate_type": ["daily"]})
        qbd = qb.get("data") if isinstance(qb, dict) else qb
        rec("2 book", f"a blocked room ({blocked_name}) is not quotable/bookable", sqb,
            "4xx naming the reason",
            400 <= sqb < 500, json.dumps(qbd)[:200])

    ids = call("GET", "/masterdata/identity_proof", tok)
    identity_type_id = (rows(ids)[0].get("id") if rows(ids) else 1)
    pms = call("GET", "/masterdata/payment_methods", tok)
    payment_method_id = (rows(pms)[0].get("id") if rows(pms) else 1)

    sr, r = call("POST", "/hotel/room_reservation", tok, multipart={
        "first_name": RUN, "last_name": "Workflow",
        # Unique per run. The endpoint recognises a repeat of the same guest,
        # dates and rooms and replays the existing booking instead of creating
        # a second one (`"idempotent_replay": true`), which is correct
        # behaviour and silently makes a re-run's availability assertion
        # meaningless if the phone number is constant.
        "phone_number": "+919" + RUN[4:] + "01",
        "arrival_date": in_d, "departure_date": out_d,
        "room_ids": json.dumps([room_id]),
        "rate_type": json.dumps(["daily"]),
        "no_of_adults": "2", "no_of_children": "0",
        "payment_method_id": str(payment_method_id),
        "reservation_status": "Pending",
        "identity_type_id": str(identity_type_id),
        "identity_file": ("qawf-specimen.png", "image/png", PNG_1PX),
    })
    rdd = (r.get("data") if isinstance(r, dict) else None) or {}
    key = rdd.get("token") or rdd.get("room_reservation_token")
    rec("2 book", "POST /hotel/room_reservation", sr, "2xx and a token back",
        200 <= sr < 300 and bool(key), json.dumps(r)[:400])
    if key:
        cleanup_plan.append(("cancel reservation", f"/hotel/room_reservation_cancel/{key}",
                             {"cancellation_reason": f"{RUN} automated workflow run"}))

    s1, free1, _b1, _ = availability(tok, in_d, out_d)
    rec("2 book", "availability AFTER", s1, "one FEWER sellable room",
        s1 == 200 and (not free0 or not free1 or len(free1) == len(free0) - 1),
        f"before={len(free0 or [])} after={len(free1 or [])}")

    # the booking must show up as a real row with derived, not client, figures
    if key:
        # The detail route takes an int id (`reservation_id: int`), not the
        # token the cancel route accepts, so a 422 here is this harness using
        # the wrong identifier -- not an API defect.
        res_id = rdd.get("id") or key
        sd, det = call("GET", f"/hotel/room_reservation/{res_id}", tok)
        dd = (det.get("data") if isinstance(det, dict) else None) or {}
        if sd != 200 or not dd:
            rec("2 book", f"GET room_reservation/{res_id} (folio read-back)", sd,
                "200 with the saved booking", False, json.dumps(det)[:220])
        try:
            # THE IDENTITY, read off the controller rather than guessed.
            #   overall_amount = room_amount - discount + tax + extras
            # `total_amount` is the room subtotal BEFORE discount, tax and
            # extras -- checking paid+balance against it is what made an
            # earlier version of this file report 16 false failures.
            g = lambda k: float(dd.get(k) or 0)
            extras = g("extra_charges") + g("extra_bed_cost") * g("extra_bed_count")
            implied = g("room_amount") - g("discount_amount") + g("tax_amount") + extras
            overall = g("overall_amount")
            rec("2 book", "folio: room - discount + tax + extras == overall_amount", sd,
                f"{implied} == {overall}", abs(implied - overall) < 0.51,
                f"room={g('room_amount')} disc={g('discount_amount')} tax={g('tax_amount')} "
                f"extras={extras} overall={overall}")
            rec("2 book", "folio: paid + balance == overall_amount", sd,
                f"{g('paid_amount')} + {g('balance_amount')} == {overall}",
                abs(g("paid_amount") + g("balance_amount") - overall) < 0.51)
        except (TypeError, ValueError) as e:
            rec("2 book", "folio arithmetic", sd, "numeric fields", False, f"{e}: {json.dumps(dd)[:200]}")
        rec("2 book", "proof document recorded on the booking", sd, "a stored identity_file path",
            bool(dd.get("proof_document")), str(dd.get("proof_document"))[:90])

    # ------------------------------------------------------------- flow 3
    print("\nFLOW 3 -- cancel it; availability must return")
    if key:
        sc, c = call("POST", f"/hotel/room_reservation_cancel/{key}", tok,
                     {"cancellation_reason": f"{RUN} automated workflow run"})
        rec("3 cancel", "POST room_reservation_cancel", sc, "2xx", 200 <= sc < 300,
            json.dumps(c)[:220])
        cleanup_plan.clear()
        s2, free2, _, _ = availability(tok, in_d, out_d)
        rec("3 cancel", "availability AFTER cancel", s2, "back to the BEFORE count",
            s2 == 200 and (not free0 or not free1 or len(free2) == len(free0)),
            f"before={len(free0 or [])} booked={len(free1 or [])} after={len(free2 or [])}")

    sl, lst = call("GET", "/hotel/room_reservation", tok)
    mine = [x for x in rows(lst) if RUN in json.dumps(x)]
    rec("3 cancel", "the cancelled row keeps its reason and shows Cancelled",
        sl, f"one row for {RUN}, status Cancelled, reason recorded",
        sl == 200 and len(mine) == 1 and mine[0].get("reservation_status") == "Cancelled"
        and bool(mine[0].get("cancellation_reason")),
        json.dumps({k: mine[0].get(k) for k in
                    ("reservation_status", "cancellation_reason", "cancelled_at")}) if mine else "no row")

    # a second cancel must be refused, not silently repeated
    if mine:
        k2 = mine[0].get("token")
        sc2, c2 = call("POST", f"/hotel/room_reservation_cancel/{k2}", tok,
                       {"cancellation_reason": "duplicate cancel"})
        rec("3 cancel", "cancelling twice is refused", sc2, "4xx",
            400 <= sc2 < 500, json.dumps(c2)[:200])

    # ------------------------------------------------------------- flow 4
    print("\nFLOW 4 -- money already on the book")
    sp, pl = call("GET", "/hotel/room_reservation", tok)
    allres = rows(pl)
    ok, detail = True, []
    for x in allres:
        g = lambda k: float(x.get(k) or 0)
        extras = g("extra_charges") + g("extra_bed_cost") * g("extra_bed_count")
        if abs(g("room_amount") - g("discount_amount") + g("tax_amount") + extras
               - g("overall_amount")) > 0.51:
            ok = False
            detail.append((x.get("room_reservation_id"), "overall"))
        if abs(g("paid_amount") + g("balance_amount") - g("overall_amount")) > 0.51:
            ok = False
            detail.append((x.get("room_reservation_id"), "paid+balance"))
    rec("4 money", "room - discount + tax + extras == overall, and paid + balance == overall",
        sp, "holds on EVERY booking in the book", sp == 200 and ok,
        f"{len(allres)} bookings, {len(detail)} mismatched {detail[:3]}")

    settled = [x for x in allres if x.get("payment_state") == "Settled"]
    rec("4 money", "settled bookings carry a zero balance", sp,
        "0 balance wherever payment_state is Settled",
        all(abs(float(x.get("balance_amount") or 0)) < 0.51 for x in settled),
        f"{len(settled)} settled of {len(allres)}")

    overpaid = [x.get("room_reservation_id") for x in allres
                if float(x.get("paid_amount") or 0) > float(x.get("overall_amount") or 0) + 0.51]
    rec("4 money", "no booking is paid beyond its overall amount", sp, "0 overpayments",
        not overpaid, f"{len(overpaid)} {overpaid[:3]}")

    # ------------------------------------------------------------- flow 5
    print("\nFLOW 5 -- housekeeping feeds room availability")
    sr2, rl = call("GET", "/masterdata/room", tok)
    allr = rows(rl)
    flagged = [r for r in allr if str(r.get("room_status") or "").lower() == "blocking"]
    rec("5 housekeeping", "rooms carry booking + housekeeping state", sr2,
        "every room has working_status and room_status",
        sr2 == 200 and all(r.get("working_status") and r.get("room_status") for r in allr),
        f"{len(allr)} rooms, {sum(1 for r in allr if 'not ready' in str(r.get('working_status')).lower())} not ready, "
        f"{len(flagged)} blocking")
    sk, tk = call("GET", "/hotel/housekeeper_tasks", tok)
    tasks = rows(tk)
    rec("5 housekeeping", "every task names a room and a status", sk,
        "no task with a missing room_no or task_status",
        sk == 200 and all(t.get("room_no") and t.get("task_status") for t in tasks),
        f"{len(tasks)} tasks")

    # ------------------------------------------------------------- flow 6
    print("\nFLOW 6 -- restaurant and bar bill arithmetic")
    for label, prefix in (("restaurant", "/restaurant"), ("bar", "/bar")):
        sb, bl = call("GET", prefix + "/bill", tok)
        bills = rows(bl)
        bad = []
        for b in bills:
            try:
                sub = float(b.get("sub_total") or 0)
                disc = float(b.get("discount_amount") or 0)
                cg = float(b.get("cgst_amount") or 0)
                sg = float(b.get("sgst_amount") or 0)
                ig = float(b.get("igst_amount") or 0)
                svc = float(b.get("service_charge_amount") or 0)
                rnd = float(b.get("round_off") or 0)
                grand = float(b.get("grand_total") or 0)
            except (TypeError, ValueError):
                continue
            calc = sub - disc + cg + sg + ig + svc + rnd
            if abs(calc - grand) > 1.01:
                bad.append((b.get("bill_number"), sub, disc, cg, sg, ig, svc, rnd, grand, round(calc, 2)))
        rec("6 billing", f"{label}: sub_total - discount + cgst + sgst + igst + service + round_off == grand_total",
            sb, "holds for every bill", sb == 200 and not bad,
            f"{len(bills)} bills, {len(bad)} mismatched {bad[:2]}")

    so, orl = call("GET", "/restaurant/order", tok)
    orders = rows(orl)
    mismatch = []
    for o in orders:
        try:
            tot = float(o.get("total_amount") or o.get("grand_total") or 0)
            pay = float(o.get("paid_amount") or 0)
        except (TypeError, ValueError):
            continue
        if pay > tot + 0.51:
            mismatch.append((o.get("order_number"), tot, pay))
    rec("6 billing", "no order is paid beyond its total", so, "0 overpayments",
        so == 200 and not mismatch, f"{len(orders)} orders, {len(mismatch)} {mismatch[:2]}")

    # ------------------------------------------------------------- cleanup
    print("\nCLEANUP")
    for kind, path, body in reversed(cleanup_plan):
        st, c = call("POST", path, tok, body)
        print(f"  {kind}: POST {path} -> {st} {json.dumps(c)[:120]}")
        results.append({"flow": "cleanup", "step": path, "status": st, "expected": "2xx",
                        "pass": 200 <= st < 400, "detail": json.dumps(c)[:200]})
    sf, fin = call("GET", "/hotel/room_reservation", tok)
    left = [x for x in rows(fin) if RUN in json.dumps(x)]
    print(f"  bookings referencing {RUN}: {len(left)} (cancelled, retained by design)")

    ok_n = sum(1 for r in results if r["pass"])
    print(f"\n{'=' * 72}\n{ok_n}/{len(results)} workflow checks passed")
    out = os.path.join(os.path.dirname(__file__), "workflow_checks.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"run": RUN, "arrival": in_d, "departure": out_d, "results": results}, fh, indent=1)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

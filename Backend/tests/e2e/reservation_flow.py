# -*- coding: utf-8 -*-
"""The reservation lifecycle, end to end, through the gateway.

Book -> read back -> check in -> take payment -> check out, plus the
cancel / no-show branches and the rules that must refuse.
Run from the repo root.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import GW, req, login, rows, refused  # noqa: E402

TOK = login("admin@cherryhotel.com")
FAILS, PASSES = [], 0


def check(label, cond, detail=""):
    global PASSES
    if cond:
        PASSES += 1
        print(f"  ok   {label}")
    else:
        FAILS.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")


PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
    "00000049454e44ae426082"
)

_phone_seq = [5000]


def next_phone():
    _phone_seq[0] += 1
    return f"98765{_phone_seq[0]:05d}"


def post_multipart(path, fields, files, tok):
    boundary = "----flow" + uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                 f"{v}\r\n").encode()
    for k, (fn, data, ct) in files.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                 f"filename=\"{fn}\"\r\nContent-Type: {ct}\r\n\r\n").encode() + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    r = urllib.request.Request(GW + path, data=body, method="POST")
    r.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, txt


# ---------------------------------------------------------------- reference --
s, b = req("GET", "/masterdata/payment_methods", TOK)
pay_row = rows(b)[0]
pay_id, pay_name = pay_row["id"], pay_row["payment_method"]
s, b = req("GET", "/masterdata/identity_proof", TOK)
id_type = rows(b)[0]["id"]
s, b = req("GET", "/masterdata/reservation_status", TOK)
statuses = rows(b)
confirmed = next((r["id"] for r in statuses
                  if "confirm" in str(r.get("reservation_status", "")).lower()), statuses[0]["id"])
s, b = req("GET", "/masterdata/tax", TOK)
tax_id = rows(b)[0]["id"] if rows(b) else None

today = dt.date.today()
arrive = today.isoformat()
depart = (today + dt.timedelta(days=2)).isoformat()

# --------------------------------------------------------------- availability --
s, b = req("GET", f"/hotel/room_availability?arrival_date={arrive}&departure_date={depart}", TOK)
check("availability -> 200", s == 200, f"{s} {str(b)[:150]}")
avail_data = (b.get("data") or {}) if s == 200 else {}
avail = avail_data.get("available_room_ids") or []
check("availability returns rooms", len(avail) > 0, str(avail_data)[:200])
check("availability excludes booked rooms",
      not (set(avail) & set(avail_data.get("booked_room_ids") or [])), "")
check("availability excludes blocked rooms",
      not (set(avail) & set(avail_data.get("blocked_room_ids") or [])), "")
room_id = avail[0]
spare_room = avail[1]
print(f"  rooms: main {room_id}, spare {spare_room}")

# ------------------------------------------------------------------- quote ----
quote_req = {
    "arrival_date": arrive, "departure_date": depart,
    "room_ids": [room_id], "rate_type": ["daily"],
    "room_occupancy": [{"room_id": room_id, "adults": 1, "children": 0}],
    "tax_type_id": tax_id, "extra_charges": 0, "extra_bed_count": 0,
}
s, b = req("POST", "/hotel/room_reservation_quote", TOK, quote_req)
check("quote -> 200", s == 200, f"{s} {str(b)[:200]}")
quote = (b.get("data") or {}) if s == 200 else {}
quoted_total = quote.get("total_amount")
print(f"  quoted total: {quoted_total}")


def booking_fields(room, phone, **over):
    f = {
        "salutation": "Mr", "first_name": "Flow", "last_name": "Test",
        "phone_number": phone, "email": f"flow{phone}@example.com",
        "arrival_date": arrive, "departure_date": depart,
        "room_ids": json.dumps([room]),
        "rate_type": json.dumps(["daily"]),
        "room_occupancy": json.dumps([{"room_id": room, "adults": 1, "children": 0}]),
        "payment_method_id": str(pay_id),
        "extra_charges": "0", "extra_bed_count": "0", "paying_amount": "0",
        "booking_status_id": str(confirmed),
        "reservation_type": "RESERVATION",
        "room_complementary": "", "common_complementary": "",
        "identity_type_id": str(id_type),
    }
    if tax_id:
        f["tax_type_id"] = str(tax_id)
    f.update(over)
    return f


def book(room, phone, **over):
    return post_multipart("/hotel/room_reservation", booking_fields(room, phone, **over),
                          {"identity_file": ("id-proof.png", PNG, "image/png")}, TOK)


# ------------------------------------------------------------------- create ---
main_phone = next_phone()
s, b = book(room_id, main_phone)
check("create reservation -> 201", s == 201, f"{s} {str(b)[:300]}")
created = (b.get("data") or {}) if s == 201 else {}
res_id, token = created.get("id"), created.get("token")
ref = created.get("room_reservation_id")
print(f"  reservation {ref} (id {res_id})")
check("server allocated a reference", bool(ref), str(created)[:150])
check("server issued a token", bool(token), str(created)[:150])

s, b = req("GET", "/hotel/room_reservation", TOK)
row = next((r for r in rows(b) if r.get("id") == res_id), {})
check("stored total matches the quote", str(row.get("total_amount")) == str(quoted_total),
      f"{row.get('total_amount')} vs {quoted_total}")

# ------------------------------------------------------ idempotent resubmit ---
s2, b2 = book(room_id, main_phone)
check("identical resubmit replays rather than double-booking",
      s2 == 200 and b2.get("idempotent_replay") and (b2.get("data") or {}).get("id") == res_id,
      f"{s2} {str(b2)[:180]}")

# -------------------------------------------------------- double-book refused --
s, b = book(room_id, next_phone())
check("a DIFFERENT guest, same room and dates -> 409", s == 409, f"{s} {str(b)[:200]}")

# ------------------------------------------------------------ invalid inputs ---
s, b = book(spare_room, next_phone(), arrival_date=depart, departure_date=arrive)
check("departure before arrival -> 400", s == 400, f"{s} {str(b)[:180]}")

s, b = book(spare_room, next_phone(), first_name="")
check("missing first name -> 400", s == 400, f"{s} {str(b)[:180]}")

s, b = book(spare_room, "")
check("missing phone -> 400/422", s in (400, 422), f"{s} {str(b)[:180]}")

s, b = book(spare_room, next_phone(), email="not-an-email")
check("malformed email -> 400", s == 400, f"{s} {str(b)[:180]}")
if s == 201:  # undo, so the run stays repeatable
    req("DELETE", f"/hotel/room_reservation/{(b.get('data') or {}).get('id')}", TOK)

ghost = next_phone()
s, b = book(999999, ghost,
            room_occupancy=json.dumps([{"room_id": 999999, "adults": 1, "children": 0}]))
check("unknown room -> 400/404", s in (400, 404), f"{s} {str(b)[:180]}")

s, b = book(spare_room, next_phone(),
            room_occupancy=json.dumps([{"room_id": spare_room, "adults": 99, "children": 0}]))
check("occupancy over the room limit -> 400", s == 400, f"{s} {str(b)[:180]}")

# ----------------------------------------------------------------- check in ----
s, b = req("POST", f"/hotel/room_reservation_checkin/{token}", TOK, {})
check("check in -> 200", s == 200, f"{s} {str(b)[:200]}")
# A self-transition is not a transition: reservation_rules.can_transition
# returns True when current == target, so a repeated check-in is a no-op
# rather than an error. What must not happen is the STATUS moving.
s, b = req("POST", f"/hotel/room_reservation_checkin/{token}", TOK, {})
check("check in twice is a no-op, not a second arrival",
      s == 200 and (b.get("data") or {}).get("reservation_status") == "Checked-In",
      f"{s} {str(b)[:150]}")

# ------------------------------------------------------------------ payment ----
s, b = req("GET", "/hotel/room_reservation", TOK)
row = next((r for r in rows(b) if r.get("id") == res_id), {})
balance = float(row.get("balance_amount") or 0)
print(f"  balance before payment: {balance}")

s, b = req("POST", f"/hotel/room_reservation_pay/{token}", TOK,
           {"paying_amount": -10, "payment_method": pay_name})
check("negative payment refused", refused(s), f"{s} {str(b)[:150]}")
s, b = req("POST", f"/hotel/room_reservation_pay/{token}", TOK,
           {"paying_amount": 0, "payment_method": pay_name})
check("zero payment refused", refused(s), f"{s} {str(b)[:150]}")
s, b = req("POST", f"/hotel/room_reservation_pay/{token}", TOK,
           {"paying_amount": balance + 1000, "payment_method": pay_name})
check("overpayment refused", refused(s), f"{s} {str(b)[:150]}")
s, b = req("POST", f"/hotel/room_reservation_pay/{token}", TOK,
           {"paying_amount": 100, "payment_method": "Not A Real Method"})
check("unknown payment method refused", refused(s), f"{s} {str(b)[:150]}")

half = round(balance / 2, 2)
s, b = req("POST", f"/hotel/room_reservation_pay/{token}", TOK,
           {"paying_amount": half, "payment_method": pay_name})
check("part payment -> 200", s == 200, f"{s} {str(b)[:200]}")

s, b = req("GET", f"/hotel/room_reservation_payments/{token}", TOK)
check("payment history readable", s == 200 and len(rows(b)) >= 1, f"{s} {len(rows(b))} rows")

s, b = req("GET", "/hotel/room_reservation", TOK)
row = next((r for r in rows(b) if r.get("id") == res_id), {})
check("balance reduced by the payment",
      abs(float(row.get("balance_amount") or 0) - (balance - half)) < 0.02,
      f"balance now {row.get('balance_amount')}, expected {balance - half}")

# ----------------------------------------------------------------- check out ---
s, b = req("GET", f"/hotel/room_reservation_checkout_preview/{token}", TOK)
check("checkout preview -> 200", s == 200, f"{s} {str(b)[:200]}")

s, b = req("POST", f"/hotel/room_reservation_checkout/{token}", TOK, {})
check("checkout with a balance outstanding is refused", refused(s), f"{s} {str(b)[:180]}")

s, b = req("POST", f"/hotel/room_reservation_pay/{token}", TOK,
           {"paying_amount": balance - half, "payment_method": pay_name})
check("settle the rest -> 200", s == 200, f"{s} {str(b)[:180]}")

s, b = req("POST", f"/hotel/room_reservation_checkout/{token}", TOK, {})
check("checkout once settled -> 200", s == 200, f"{s} {str(b)[:200]}")

s, b = req("GET", "/hotel/room_reservation", TOK)
row = next((r for r in rows(b) if r.get("id") == res_id), {})
print(f"  final status: {row.get('reservation_status')} terminal={row.get('is_terminal')}")
check("reservation is terminal after checkout", bool(row.get("is_terminal")), str(row)[:180])
check("balance is zero after checkout", float(row.get("balance_amount") or 0) == 0,
      str(row.get("balance_amount")))

s, b = req("POST", f"/hotel/room_reservation_checkin/{token}", TOK, {})
check("cannot check in a departed reservation", refused(s), f"{s} {str(b)[:150]}")
s, b = req("POST", f"/hotel/room_reservation_cancel/{token}", TOK, {"cancellation_reason": "test"})
check("cannot cancel a departed reservation", refused(s), f"{s} {str(b)[:150]}")
s, b = req("DELETE", f"/hotel/room_reservation/{res_id}", TOK)
check("cannot delete a paid reservation", refused(s), f"{s} {str(b)[:150]}")

# ---------------------------------------------- the room is freed for reuse ----
s, b = req("GET", f"/hotel/room_availability?arrival_date={arrive}&departure_date={depart}", TOK)
freed = (b.get("data") or {}).get("available_room_ids") or []
blocked = (b.get("data") or {}).get("blocked_room_ids") or []
check("departed room is now blocked for housekeeping, not silently re-bookable",
      room_id in blocked or room_id not in freed,
      f"room {room_id}: available={room_id in freed} blocked={room_id in blocked}")

# -------------------------------------------------------- cancel / no-show ----
cancel_phone = next_phone()
s, b = book(spare_room, cancel_phone)
check("second booking for the cancel branch -> 201", s == 201, f"{s} {str(b)[:200]}")
c = (b.get("data") or {}) if s == 201 else {}
c_id, c_token = c.get("id"), c.get("token")

if c_token:
    s, b = req("POST", f"/hotel/room_reservation_cancel/{c_token}", TOK, {"cancellation_reason": "Guest called"})
    check("cancel -> 200", s == 200, f"{s} {str(b)[:200]}")
    s, b = req("GET", "/hotel/room_reservation", TOK)
    row = next((r for r in rows(b) if r.get("id") == c_id), {})
    check("cancelled reservation is terminal", bool(row.get("is_terminal")), str(row)[:150])
    check("cancellation reason recorded",
          "Guest called" in json.dumps(row), "reason not stored")
    s, b = req("POST", f"/hotel/room_reservation_checkin/{c_token}", TOK, {})
    check("cannot check in a cancelled reservation", refused(s), f"{s} {str(b)[:150]}")

    s, b = req("GET", f"/hotel/room_availability?arrival_date={arrive}&departure_date={depart}", TOK)
    freed = (b.get("data") or {}).get("available_room_ids") or []
    check("cancelling releases the room", spare_room in freed,
          f"room {spare_room} not back in availability")

print(f"\n{PASSES} passed, {len(FAILS)} failed")
for f in FAILS:
    print("  -", f)
print(f"\nreservations created: {ref} (id {res_id}), cancel-branch id {c_id}")

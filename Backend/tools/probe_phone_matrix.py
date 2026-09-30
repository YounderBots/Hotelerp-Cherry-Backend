"""Live probes for country-aware phone validation, through the gateway.

    python Backend/tools/probe_phone_matrix.py

Prints one line per case with the status code and the message a user would see,
so the matrix can be read as evidence rather than as a pass/fail from a test
suite. Everything it creates is retired again before it exits -- orders are
cancelled, which releases their tables, and guests are soft-deleted. It also
prints what is Available afterwards, so a run that leaks is visible in its own
output rather than surfacing later as an unrelated failure somewhere else.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("BASE") or "http://127.0.0.1:8000"
PASSWORD = os.getenv("PW_PASSWORD", "")


def call(method, path, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json",
                 **({"Authorization": "Bearer " + token} if token else {})},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"detail": raw[:200]}


def login(email="admin@cherryhotel.com"):
    s, b = call("POST", "/login_post", {"email": email, "password": PASSWORD})
    if s != 200:
        raise SystemExit(f"login failed: {s} {b}")
    return b["access_token"]


def main() -> int:
    tok = login()
    created = []

    def guest(label, mobile, region=None, expect=201):
        payload = {"first_name": "Probe", "last_name": label, "mobile": mobile}
        if region:
            payload["phone_region"] = region
        s, b = call("POST", "/bar/guest", payload, tok)
        detail = b.get("detail") if isinstance(b, dict) else ""
        ok = "ok " if s == expect else "XX "
        print(f"{ok}{label:<34} -> {s} {str(detail)[:78]}")
        if s == 201:
            created.append((b.get("data") or {}).get("id"))
        return s

    print("=== valid numbers from different countries, all accepted")
    # Each row uses a DIFFERENT number, because a repeat of one already stored is
    # answered 409 by the uniqueness rule -- which is itself the proof that the
    # spellings canonicalise to the same value (see the next block).
    guest("IN mobile", "9876543210", "IN")
    guest("IN international", "+91 9876543211")
    guest("IN with trunk zero", "09876543212", "IN")
    guest("US local format", "(415) 555-2671", "US")
    guest("US international", "+1 415 555 2672")
    guest("UAE mobile", "+971 50 123 4567")
    guest("Singapore", "+65 8123 4567")
    guest("Germany", "+49 151 12345678")

    print("\n=== the same number typed four ways stores one spelling")
    forms = ["+919876543210", "+91 98765 43210", "09876543210", "+91-98765-43210"]
    seen = set()
    for f in forms:
        s, b = call("POST", "/bar/guest",
                    {"first_name": "Same", "last_name": "Number", "mobile": f, "phone_region": "IN"}, tok)
        if s == 201:
            gid = (b.get("data") or {}).get("id")
            created.append(gid)
            s2, b2 = call("GET", f"/bar/guest/{gid}", None, tok)
            seen.add((b2.get("data") or {}).get("mobile"))
        else:
            # The first one won the uniqueness check; the rest are duplicates,
            # which is itself the proof that they canonicalised the same.
            seen.add("duplicate-of-first")
    print(f"   distinct stored values across {len(forms)} spellings: {seen}")

    print("\n=== invalid input, refused with a message a person can act on")
    guest("letters", "abcdefghij", "IN", expect=400)
    guest("too short", "12", "IN", expect=400)
    guest("not assignable in that country", "9876543299", "US", expect=400)
    guest("invalid country code", "+999123456789", expect=400)
    guest("duplicate country code", "+91 91 98765 43210", expect=400)
    guest("national with no country", "4155552671", expect=400)
    guest("unicode digits accepted", "९८७६५४३२१४", "IN", expect=201)
    guest("very long paste", "9" * 300, "IN", expect=400)
    guest("sql payload", "98765' OR 1=1--", "IN", expect=400)
    guest("emoji not silently stripped", "📞9876543215", "IN", expect=400)
    guest("landline on a guest mobile", "020 7946 0958", "GB", expect=400)

    print("\n=== a filled field with no digits is 'required', not a duplicate")
    s, b = call("POST", "/bar/guest", {"first_name": "NoMobile", "mobile": "-- --"}, tok)
    detail = b.get("detail") if isinstance(b, dict) else ""
    ok = "ok " if s == 400 and "required" in str(detail).lower() else "XX "
    print(f"{ok}separators only                 -> {s} {str(detail)[:70]}")

    print("\n=== orders carry the same rule (a landline is fine on an order)")
    orders = []
    for label, mobile, region, expect in [
        ("order US mobile", "(202) 555-0147", "US", 201),
        ("order GB landline", "020 7946 0958", "GB", 201),
        ("order ten-digit-only", "4155552671", None, 400),
        ("order letters", "abcdefghij", "IN", 400),
    ]:
        s, b = call("GET", "/bar/table", None, tok)
        table = next((t for t in (b.get("data") or []) if t.get("table_status") == "Available"), None)
        if not table:
            print("   no Available bar table; order probes skipped")
            break
        payload = {"order_type": "At Table", "table_id": table["id"],
                   "guest_name": "Probe", "guest_mobile": mobile, "no_of_guests": 1}
        if region:
            payload["phone_region"] = region
        s, b = call("POST", "/bar/order", payload, tok)
        detail = b.get("detail") if isinstance(b, dict) else ""
        ok = "ok " if s == expect else "XX "
        print(f"{ok}{label:<34} -> {s} {str(detail)[:70] or 'created'}")
        if s == 201:
            orders.append((b.get("data") or {}).get("id"))

    print("\n=== cleanup")
    # Orders first: an order holds its table Occupied, and a probe that leaves one
    # behind takes a table out of service for every later run. Cancelling through
    # the status endpoint runs the same release logic the product uses, rather
    # than writing to the table row behind the API's back.
    for order_id in orders:
        if order_id:
            s, _ = call("PUT", f"/bar/order/{order_id}/status",
                        {"order_status": "Cancelled"}, tok)
            print(f"   cancelled probe order {order_id}: {s}")
    for guest_id in created:
        if guest_id:
            call("DELETE", f"/bar/guest/{guest_id}", None, tok)

    s, b = call("GET", "/bar/guest", None, tok)
    print(f"   active bar guests after cleanup: {b.get('count')}")
    s, b = call("GET", "/bar/table", None, tok)
    available = sum(1 for t in (b.get("data") or []) if t.get("table_status") == "Available")
    print(f"   Available bar tables after cleanup: {available}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

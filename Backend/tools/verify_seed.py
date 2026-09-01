#!/usr/bin/env python3
"""Assert that the seeded database is internally consistent.

    python Backend/tools/verify_seed.py

Checks the invariants the application relies on but the database cannot express
as constraints, because they span schemas: money that reconciles, rooms that
are never double-booked, room states that match the bookings, and -- the one
the previous dataset failed -- every stored image path having a real file
behind it.

Exit code 0 when everything holds, 1 otherwise.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlalchemy as sa                                       # noqa: E402

from seed.common import SERVICE_DIRS, SERVICES, engine_for    # noqa: E402

FAILS: list[str] = []
CHECKS = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    print(("  PASS  " if ok else "  FAIL  ") + label + (("  -- " + detail) if detail else ""))
    if not ok:
        FAILS.append(label)


def rows(schema, sql, **params):
    with engine_for(schema).connect() as c:
        return c.execute(sa.text(sql), params).fetchall()


def scalar(schema, sql, **params):
    with engine_for(schema).connect() as c:
        return c.execute(sa.text(sql), params).scalar()


def media_path(stored: str, schema: str, default_dir: str) -> str:
    """Resolve a stored image value to a path on disk.

    Two shapes are stored, both legitimate: a site-relative path under the
    service's static mount, and a bare filename for the reservation identity
    proofs (the endpoint that serves those builds the directory itself).
    """
    base = os.path.join(SERVICES, SERVICE_DIRS[schema])
    if stored.startswith("/templates/"):
        return os.path.join(base, stored.lstrip("/").replace("/", os.sep))
    return os.path.join(base, "templates", "static", default_dir, stored)


def main() -> int:
    print("=== 1. money reconciles on every folio ===")
    bad = rows("hotelerp_hotel", """
        SELECT room_reservation_id, room_amount, extra_bed_cost, extra_charges,
               discount_amount, tax_amount, overall_amount
        FROM room_reservation
        WHERE ABS((room_amount + extra_bed_cost + extra_charges
                   - discount_amount + tax_amount) - overall_amount) > 0.02
    """)
    check("overall = rooms + beds + extras - discount + tax", not bad,
          "; ".join(f"{r[0]}" for r in bad[:3]))

    bad = rows("hotelerp_hotel", """
        SELECT room_reservation_id, overall_amount, paid_amount, balance_amount
        FROM room_reservation
        WHERE ABS((overall_amount - paid_amount) - balance_amount) > 0.02
    """)
    check("balance = overall - paid", not bad, "; ".join(r[0] for r in bad[:3]))

    bad = rows("hotelerp_hotel", """
        SELECT r.room_reservation_id, r.paid_amount, COALESCE(SUM(h.amount), 0)
        FROM room_reservation r
        LEFT JOIN reservation_amount_paid_history h
               ON h.reservation_id = r.room_reservation_id AND h.status = 'ACTIVE'
        GROUP BY r.id, r.room_reservation_id, r.paid_amount
        HAVING ABS(r.paid_amount - COALESCE(SUM(h.amount), 0)) > 0.02
    """)
    check("paid_amount equals the sum of its payment history", not bad,
          "; ".join(f"{r[0]} {r[1]} vs {r[2]}" for r in bad[:3]))

    bad = rows("hotelerp_hotel", """
        SELECT room_reservation_id, balance_amount FROM room_reservation
        WHERE reservation_status = 'Checked-Out' AND balance_amount > 0.02
    """)
    check("no checked-out stay leaves a balance", not bad,
          "; ".join(f"{r[0]} owes {r[1]}" for r in bad[:3]))

    bad = rows("hotelerp_hotel", """
        SELECT room_reservation_id FROM room_reservation
        WHERE paid_amount > overall_amount + 0.02
    """)
    check("nobody is overpaid", not bad, "; ".join(r[0] for r in bad[:3]))

    print()
    print("=== 2. inventory is never double-booked ===")
    live = rows("hotelerp_hotel", """
        SELECT room_reservation_id, room_no, arrival_date, departure_date
        FROM room_reservation
        WHERE status = 'ACTIVE'
          AND reservation_status NOT IN ('Cancelled', 'No-Show')
    """)
    import json
    held: dict[str, list] = {}
    clashes = []
    for ref, room_json, arrival, departure in live:
        for no in (json.loads(room_json) if isinstance(room_json, str) else room_json) or []:
            for other_ref, o_arr, o_dep in held.get(str(no), []):
                if arrival < o_dep and departure > o_arr:
                    clashes.append(f"room {no}: {ref} vs {other_ref}")
            held.setdefault(str(no), []).append((ref, arrival, departure))
    check("no two live stays share a room on the same night", not clashes,
          "; ".join(clashes[:3]))

    print()
    print("=== 3. room state matches the bookings ===")
    occupied_rooms = set()
    for ref, room_json, arrival, departure in live:
        pass
    in_house = rows("hotelerp_hotel", """
        SELECT room_no FROM room_reservation
        WHERE reservation_status = 'Checked-In' AND status = 'ACTIVE'
    """)
    for (room_json,) in in_house:
        for no in (json.loads(room_json) if isinstance(room_json, str) else room_json) or []:
            occupied_rooms.add(str(no))

    flagged = {r[0] for r in rows(
        "hotelerp_masterdata",
        "SELECT Room_No FROM room WHERE Room_Booking_status = 'Occupied'")}
    check("every in-house room reads Occupied", occupied_rooms <= flagged,
          f"missing {sorted(occupied_rooms - flagged)}")
    check("no room reads Occupied without a guest in it", flagged <= occupied_rooms,
          f"spurious {sorted(flagged - occupied_rooms)}")

    dirty = {r[0] for r in rows(
        "hotelerp_masterdata",
        "SELECT Room_No FROM room WHERE Room_Working_status = 'Not Ready'")}
    check("departed rooms are queued for housekeeping", bool(dirty),
          f"{len(dirty)} awaiting cleaning")

    print()
    print("=== 4. every reference resolves ===")
    room_ids = {r[0] for r in rows("hotelerp_masterdata", "SELECT id FROM room")}
    type_ids = {r[0] for r in rows("hotelerp_masterdata", "SELECT id FROM room_type")}
    tax_ids = {r[0] for r in rows("hotelerp_masterdata", "SELECT id FROM tax_type")}
    disc_ids = {r[0] for r in rows("hotelerp_masterdata", "SELECT id FROM discount_data")}
    pm_ids = {r[0] for r in rows("hotelerp_masterdata", "SELECT id FROM payment_methods")}
    id_ids = {r[0] for r in rows("hotelerp_masterdata", "SELECT id FROM identity_proof")}
    statuses = {r[0] for r in rows(
        "hotelerp_masterdata",
        "SELECT Reservation_Status FROM reservation_status WHERE status='ACTIVE'")}

    dangling = []
    for ref, rid_json, tid_json, tax, disc, pm, ident, st in rows("hotelerp_hotel", """
        SELECT room_reservation_id, room_ids, room_type_ids, tax_type_id,
               discount_type_id, payment_method_id, identity_type_id,
               reservation_status
        FROM room_reservation
    """):
        for no in (json.loads(rid_json) if isinstance(rid_json, str) else rid_json) or []:
            if int(no) not in room_ids:
                dangling.append(f"{ref} room_id {no}")
        for t in (json.loads(tid_json) if isinstance(tid_json, str) else tid_json) or []:
            if int(t) not in type_ids:
                dangling.append(f"{ref} room_type_id {t}")
        if tax and tax not in tax_ids:
            dangling.append(f"{ref} tax {tax}")
        if disc and disc not in disc_ids:
            dangling.append(f"{ref} discount {disc}")
        if pm and pm not in pm_ids:
            dangling.append(f"{ref} payment_method {pm}")
        if ident and ident not in id_ids:
            dangling.append(f"{ref} identity {ident}")
        if st not in statuses:
            dangling.append(f"{ref} status {st!r}")
    check("reservations reference only real master data", not dangling,
          "; ".join(dangling[:4]))

    role_ids = {r[0] for r in rows("hotelerp_users", "SELECT id FROM roles")}
    bad_users = [r[0] for r in rows("hotelerp_users", "SELECT username, Role_ID FROM users")
                 if int(r[1]) not in role_ids]
    check("every user holds a real role", not bad_users, ", ".join(bad_users[:4]))

    menu_ids = {r[0] for r in rows("hotelerp_users", "SELECT id FROM menus")}
    sub_ids = {r[0] for r in rows("hotelerp_users", "SELECT id FROM submenus")}
    bad_perm = rows("hotelerp_users", "SELECT id, menu_id, submenu_id FROM role_permissions")
    orphan = [str(p[0]) for p in bad_perm
              if int(p[1]) not in menu_ids
              or (p[2] and int(p[2]) not in sub_ids)]
    check("every permission points at a real menu", not orphan, ", ".join(orphan[:4]))

    bad_sub = [r[1] for r in rows("hotelerp_users", "SELECT id, submenu_name, menu_id FROM submenus")
               if int(r[2]) not in menu_ids]
    check("every submenu hangs off a real menu", not bad_sub, ", ".join(bad_sub[:4]))

    print()
    print("=== 5. EVERY stored image has a file behind it ===")
    missing, total = [], 0
    for room_no, *shots in rows("hotelerp_masterdata", """
        SELECT Room_No, Room_Image_1, Room_Image_2, Room_Image_3, Room_Image_4 FROM room
    """):
        for i, shot in enumerate(shots, start=1):
            if not shot:
                missing.append(f"room {room_no} image {i} is empty")
                continue
            total += 1
            if not os.path.isfile(media_path(shot, "hotelerp_masterdata", "upload_image")):
                missing.append(f"room {room_no} image {i}: {shot}")
    check(f"all {total} room photographs exist on disk", not missing,
          "; ".join(missing[:3]))

    missing, total = [], 0
    for username, photo in rows("hotelerp_users", "SELECT username, Photo FROM users"):
        if not photo:
            missing.append(f"{username} has no photo")
            continue
        total += 1
        if not os.path.isfile(media_path(photo, "hotelerp_users", "users")):
            missing.append(f"{username}: {photo}")
    check(f"all {total} staff photos exist on disk", not missing, "; ".join(missing[:3]))

    missing, total = [], 0
    for ref, proof in rows("hotelerp_hotel", """
        SELECT room_reservation_id, proof_document FROM room_reservation
        WHERE proof_document IS NOT NULL AND proof_document <> ''
    """):
        total += 1
        if not os.path.isfile(media_path(proof, "hotelerp_hotel", "identity_proofs")):
            missing.append(f"{ref}: {proof}")
    check(f"all {total} identity proofs exist on disk", not missing, "; ".join(missing[:3]))

    missing, total = [], 0
    for rid, attach in rows("hotelerp_hotel", """
        SELECT id, attachment_file FROM hsk_room_incident
        WHERE attachment_file IS NOT NULL AND attachment_file <> ''
    """):
        total += 1
        if not os.path.isfile(media_path(attach, "hotelerp_hotel", "room_incidents")):
            missing.append(f"incident {rid}: {attach}")
    check(f"all {total} incident attachments exist on disk", not missing,
          "; ".join(missing[:3]))

    for schema, table, col, folder in [
        ("hotelerp_restaurant", "restaurant_menu", "item_image", "upload_image"),
        ("hotelerp_bar", "bar_menu_item", "item_image", "upload_image"),
    ]:
        found = rows(schema, f"SELECT id, {col} FROM {table} "
                             f"WHERE {col} IS NOT NULL AND {col} <> ''")
        gone = [f"{table} {r[0]}" for r in found
                if not os.path.isfile(media_path(r[1], schema, folder))]
        if found:
            check(f"all {len(found)} {table} images exist on disk", not gone,
                  "; ".join(gone[:3]))

    print()
    print("=== 5b. restaurant and bar money reconciles ===")
    for schema, bill, item, pay, igst in [
        ("hotelerp_restaurant", "restaurant_bill", "restaurant_bill_item",
         "restaurant_bill_payment", True),
        ("hotelerp_bar", "bar_bill", "bar_bill_item", "bar_bill_payment", False),
    ]:
        igst_col = " + igst_amount" if igst else ""
        bad = rows(schema, f"""
            SELECT bill_number FROM {bill}
            WHERE ABS((sub_total + cgst_amount + sgst_amount{igst_col}
                       + service_charge_amount - discount_amount + round_off)
                      - grand_total) > 0.02
        """)
        check(f"{bill}: grand total equals its own components", not bad,
              ", ".join(r[0] for r in bad[:3]))

        bad = rows(schema, f"""
            SELECT b.bill_number, b.sub_total, SUM(i.amount)
            FROM {bill} b JOIN {item} i ON i.bill_id = b.id
            GROUP BY b.id, b.bill_number, b.sub_total
            HAVING ABS(b.sub_total - SUM(i.amount)) > 0.02
        """)
        check(f"{bill}: subtotal equals the sum of its lines", not bad,
              ", ".join(r[0] for r in bad[:3]))

        bad = rows(schema, f"""
            SELECT b.bill_number FROM {bill} b
            LEFT JOIN {pay} p ON p.bill_id = b.id AND p.payment_status = 'Success'
            WHERE b.payment_status = 'Paid'
            GROUP BY b.id, b.bill_number, b.grand_total
            HAVING ABS(b.grand_total - COALESCE(SUM(p.paid_amount), 0)) > 0.02
        """)
        check(f"{bill}: every paid bill is settled in full", not bad,
              ", ".join(r[0] for r in bad[:3]))

        bad = rows(schema, f"""
            SELECT i.id FROM {item} i
            WHERE ABS((i.rate * i.quantity) - i.amount) > 0.02
        """)
        check(f"{item}: line amount equals rate x quantity", not bad,
              ", ".join(str(r[0]) for r in bad[:3]))

    print()
    print("=== 6. no orphaned image files ===")
    referenced = set()
    for _no, *shots in rows("hotelerp_masterdata", """
        SELECT Room_No, Room_Image_1, Room_Image_2, Room_Image_3, Room_Image_4 FROM room
    """):
        referenced.update(os.path.basename(s) for s in shots if s)
    on_disk = set(os.listdir(os.path.join(
        SERVICES, "MasterDataServices", "templates", "static", "upload_image")))
    check("no unreferenced room images left behind",
          not (on_disk - referenced),
          f"{len(on_disk - referenced)} orphan(s)")

    print()
    print("=== 7. the navigation resolves ===")
    import re
    app = os.path.join(os.path.dirname(SERVICES), "..", "Frontend", "src", "App.jsx")
    app = os.path.normpath(os.path.join(SERVICES, "..", "..", "Frontend", "src", "App.jsx"))
    with open(app, encoding="utf-8") as fh:
        routes = set(re.findall(r'path="([^"]+)"', fh.read()))
    dead = [r[0] for r in rows("hotelerp_users",
                               "SELECT menu_link FROM menus WHERE menu_link <> ''")
            if r[0] not in routes]
    dead += [r[0] for r in rows("hotelerp_users", "SELECT submenu_link FROM submenus")
             if r[0] not in routes]
    check("every menu link matches a route in App.jsx", not dead, ", ".join(dead[:4]))

    print()
    if FAILS:
        print(f"{len(FAILS)} of {CHECKS} checks FAILED:")
        for f in FAILS:
            print("   -", f)
        return 1
    print(f"All {CHECKS} consistency checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

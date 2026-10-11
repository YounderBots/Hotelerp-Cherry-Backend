"""Delete every row a QA run left behind, by its ZZQA / ZZCP / ZZCOLORPROBE marker.

The browser round-trip (Frontend/e2e/roundtrip.mjs) creates a row per page and
removes it again. A run that dies between the create and the cleanup leaves one
behind, and a later run then measures its row count against a baseline that
already contains the debris. This removes only rows carrying an explicit QA
marker -- it never touches seeded data.
"""
from __future__ import annotations

import sys

sys.path.insert(0, r".run-logs")
from dbq import conn  # noqa: E402

MARKERS = ("ZZQA", "ZZCP-", "ZZCOLORPROBE", "zzprobe", "ZZVIS", "ZZEDT",
           "ZZDIRECT", "QAZZQA", "QB ZZTEST", "ZZPG")

# A QA item with a stock row is referenced by it, so the child goes first.
# Order matters: deleting the parent first raises an FK error and the tool
# leaves the debris behind while reporting a traceback.
CHILD_OF = {
    "restaurant.inventory_item": [
        "inventory_stock_transaction", "inventory_purchase", "inventory_stock",
    ],
    "bar.bar_inventory_item": [
        "bar_inventory_stock_transaction", "bar_inventory_purchase", "bar_inventory_stock",
    ],
    "users.users": ["role_permissions"],
    # A floor and a table are referenced by the orders placed against them, and
    # a table by its reservations and merges. Deleting the parent first raises
    # 1451 and leaves everything behind.
    "restaurant.restaurant_table": [
        "restaurant_order_item", "restaurant_order", "restaurant_table_reservation",
        "restaurant_table_merge_detail", "restaurant_table_merge",
    ],
    "restaurant.restaurant_floor": ["restaurant_table"],
    "bar.bar_table": ["bar_order_item", "bar_order", "bar_table_reservation"],
    "bar.bar_floor": ["bar_table"],
}

# Rows with no textual marker to match. The round-trip generates a mobile from
# the run token, so every QA guest sits in the same numeric block; seeded
# mobiles do not.
BY_VALUE = {
    "restaurant.guest": ("mobile", ("+9196543", "+9198186", "+9190000")),
    "bar.bar_guest": ("mobile", ("+9196543", "+9198186", "+9190000")),
}

# table -> the text columns worth searching
TARGETS = {
    "users": [
        # The Employee screen writes to the USERS database, not the hotel one.
        # Missing it left sixteen QA accounts behind - and verify_seed.py then
        # failed on "all 10 staff photos exist on disk", because it counts every
        # ACTIVE user and the QA ones have no photo.
        ("users", ["First_Name", "Last_Name", "username", "Company_Email"]),
        ("department", ["department_name", "Department_Name"]),
        ("designation", ["designation_name", "Designation_Name"]),
        ("shift", ["shift_name", "Shift_Name"]),
    ],
    "masterdata": [
        ("bed_type", ["Type_Name"]),
        ("facility", ["Facility_Name"]),
        ("payment_methods", ["payment_method"]),
        ("identity_proof", ["proof_name"]),
        ("task_type", ["Type_Name"]),
        ("reservation_status", ["Reservation_Status"]),
        ("discount_data", ["Discount_Name"]),
        ("tax_type", ["Tax_Name"]),
        ("room", ["Room_Name", "Room_No"]),
        ("room_type", ["Type_Name"]),
        ("room_complementry", ["Complementry_Name"]),
        ("table_hall_names", ["hall_name", "Hall_Name"]),
        ("countries_currency", ["country_name", "currency_name"]),
    ],
    "hotel": [
        ("room_booking", ["first_name", "last_name", "guest_name", "Guest_Name"]),
        ("room_reservation", ["first_name", "last_name", "guest_name", "Guest_Name"]),
        ("inquiry", ["guest_name", "Guest_Name"]),
        ("hsk_room_incident", ["incident_description", "involved_staff", "witnesses"]),
        # housekeeper_task keeps the assigned staff's name, so a QA run that
        # created a throwaway employee leaves tasks behind that name - and they
        # then show up in Task Assign's list as real rows.
        ("housekeeper_task", ["first_name", "last_name", "lost_found"]),
    ],
    "restaurant": [
        # The item tables are named inventory_item / bar_inventory_item, NOT
        # stock_item. A wrong name here reads as "nothing left behind" while
        # fifteen QA rows sit in the database.
        ("inventory_item", ["item_name"]),
        ("menu_item", ["Item_Name"]),
        # Guest rows carry a generated mobile, not a name marker, so they are
        # found by the mobiles the round-trip used. Leaving them behind makes
        # the NEXT run collide with 409 "a guest with this mobile already
        # exists" and look like a product defect.
        ("guest", ["guest_name", "first_name", "last_name"]),
        ("restaurant_table", ["table_name", "Table_Name"]),
        ("restaurant_floor", ["floor_name", "Floor_Name"]),
    ],
    "bar": [
        ("bar_inventory_item", ["item_name"]),
        ("menu_item", ["Item_Name"]),
        ("bar_guest", ["guest_name", "first_name", "last_name"]),
        ("bar_table", ["table_name", "Table_Name"]),
        ("bar_floor", ["floor_name", "Floor_Name"]),
    ],
}


def columns(c, table):
    """Column names only.

    dbq.conn() hands back a DictCursor, so a row is a dict and r[0] raises --
    and the broad `except` around the caller would then skip the table in
    silence, which is exactly what happened the first time this ran.
    """
    cur = c.cursor()
    cur.execute("SHOW COLUMNS FROM `%s`" % table)
    return [next(iter(r.values())) if isinstance(r, dict) else r[0] for r in cur.fetchall()]


def first_value(row):
    return next(iter(row.values())) if isinstance(row, dict) else row[0]


def main() -> int:
    total = 0
    dry = "--apply" not in sys.argv

    # Pass 1: QA rows that nothing else references.
    found = {}
    for which, tables in TARGETS.items():
        try:
            c = conn(which)
        except Exception as e:  # a service database that is not running
            print(f"skip {which}: {e}")
            continue
        with c:
            cur = c.cursor()
            for table, cols in tables:
                try:
                    have = columns(c, table)
                except Exception:
                    continue
                pk = "id" if "id" in have else ("ID" if "ID" in have else None)
                usable = [x for x in cols if x in have]
                if not pk or not usable:
                    continue
                # One predicate per (column, marker) pair, so there is exactly
                # one placeholder per predicate.
                where = " OR ".join(
                    f"`{x}` LIKE %s" for x in usable for _ in MARKERS)
                args = [f"%{m}%" for _ in usable for m in MARKERS]
                cur.execute(f"SELECT `{pk}` FROM `{table}` WHERE {where}", args)
                ids = [first_value(r) for r in cur.fetchall()]

                key = f"{which}.{table}"
                if key in BY_VALUE:
                    col, values = BY_VALUE[key]
                    if col in have:
                        marks = ",".join(["%s"] * len(values))
                        cur.execute(
                            f"SELECT `{pk}` FROM `{table}` WHERE `{col}` IN ({marks})", values)
                        extra = [first_value(r) for r in cur.fetchall()]
                        if extra:
                            ids = sorted(set(ids) | set(extra))
                if ids:
                    found[(which, table)] = ids
        try:
            c.close()
        except Exception:
            pass          # `with c` already closed it on the way out

    if not found:
        print("no QA rows found")
        return 0

    for (which, table), ids in found.items():
        total += len(ids)
        print(f"  {which}.{table}: {len(ids)} QA row(s) -> {ids}")

    if dry:
        print(f"DRY RUN - {total} QA row(s)")
        return 0

    # Pass 2: delete children, then parents, in one transaction per database.
    # A QA item now carries a stock row (that was the fix), so removing the
    # parent first trips the foreign key and leaves the debris in place.
    for which in {w for w, _ in found}:
        c = conn(which)
        with c:
            cur = c.cursor()
            parents = {t: ids for (w, t), ids in found.items() if w == which}

            for table, ids in parents.items():
                for child in CHILD_OF.get(f"{which}.{table}", []):
                    try:
                        child_cols = columns(c, child)
                    except Exception:
                        continue
                    fk = next((x for x in ("inventory_item_id", "bar_inventory_item_id",
                                           "table_id", "bar_table_id", "floor_id",
                                           "bar_floor_id")
                               if x in child_cols), None)
                    pk = "id" if "id" in child_cols else None
                    if not fk or not pk:
                        continue
                    marks = ",".join(["%s"] * len(ids))
                    cur.execute(
                        f"DELETE FROM `{child}` WHERE `{fk}` IN ({marks})", ids)
                    if cur.rowcount:
                        print(f"    {which}.{child}: removed {cur.rowcount} child row(s)")

            for table, ids in parents.items():
                cur.execute(
                    f"DELETE FROM `{table}` WHERE `id` IN ({','.join(['%s'] * len(ids))})",
                    ids)
                if cur.rowcount != len(ids):
                    print(f"    {which}.{table}: removed {cur.rowcount} of {len(ids)}")
            c.commit()
        try:
            c.close()
        except Exception:
            pass

    print(f"DELETED {total} QA row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
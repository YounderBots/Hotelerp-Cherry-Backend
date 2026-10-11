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

MARKERS = ("ZZQA", "ZZCP-", "ZZCOLORPROBE", "zzprobe", "ZZVIS", "ZZEDT", "ZZDIRECT")

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
}

# table -> the text columns worth searching
TARGETS = {
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
        ("reservation", ["Guest_Name", "guest_name"]),
        ("guest_enquiry", ["Guest_Name", "guest_name"]),
        ("room_incident_log", ["incident_details", "title"]),
        ("employee", ["First_Name"]),
        ("department", ["Department_Name"]),
        ("designation", ["Designation_Name"]),
        ("shift", ["Shift_Name"]),
        ("task_type", ["Task_Type"]),
    ],
    "restaurant": [
        # The item tables are named inventory_item / bar_inventory_item, NOT
        # stock_item. A wrong name here reads as "nothing left behind" while
        # fifteen QA rows sit in the database.
        ("inventory_item", ["item_name"]),
        ("menu_item", ["Item_Name"]),
        ("restaurant_guest", ["Guest_Name"]),
        ("table_master", ["Table_Name"]),
    ],
    "bar": [
        ("bar_inventory_item", ["item_name"]),
        ("menu_item", ["Item_Name"]),
        ("bar_guest", ["Guest_Name"]),
        ("table_master", ["Table_Name"]),
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
                    fk = next((x for x in ("inventory_item_id", "bar_inventory_item_id")
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
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

MARKERS = ("ZZQA", "ZZCP-", "ZZCOLORPROBE", "zzprobe")

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
        ("menu_item", ["Item_Name"]),
        ("stock_item", ["item_name"]),
        ("restaurant_guest", ["Guest_Name"]),
        ("table_master", ["Table_Name"]),
    ],
    "bar": [
        ("menu_item", ["Item_Name"]),
        ("stock_item", ["item_name"]),
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
                if not pk:
                    continue
                usable = [x for x in cols if x in have]
                if not usable:
                    continue
                # One predicate per (column, marker) pair, so there is exactly one
                # placeholder per predicate.
                where = " OR ".join(
                    f"`{x}` LIKE %s" for x in usable for _ in MARKERS)
                args = [f"%{m}%" for _ in usable for m in MARKERS]
                cur.execute(f"SELECT `{pk}` FROM `{table}` WHERE {where}", args)
                ids = [first_value(r) for r in cur.fetchall()]
                if not ids:
                    continue
                total += len(ids)
                print(f"  {which}.{table}: {len(ids)} QA row(s) -> {ids}")
                if not dry:
                    cur.execute(
                        f"DELETE FROM `{table}` WHERE `{pk}` IN ({','.join(['%s'] * len(ids))})",
                        ids)
            if not dry:
                c.commit()
        try:
            c.close()
        except Exception:
            pass          # `with c` already closed it on the way out
    print(("DRY RUN - " if dry else "DELETED ") + f"{total} QA row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Rebuild every schema from scratch as a coherent, production-ready dataset.

    python Backend/tools/seed_demo_data.py --dry-run   # report only, no writes
    python Backend/tools/seed_demo_data.py --confirm   # wipe and rebuild

THIS DESTROYS DATA. `--confirm` is mandatory; there is no default that writes.

WHAT IT PRODUCES
    A property mid-operation: staff who can log in, a fully configured Master
    Data set, an inventory of rooms with real photographs, and a book of
    reservations spanning every status whose money, room states, housekeeping
    queue and night audit all agree with one another.

WHY A SCRIPT RATHER THAN A SQL DUMP
    A dump is a photograph of one moment: its dates rot, so a "checked-in
    today" guest becomes a guest who checked in eight months ago, and the
    dashboard that should show today's arrivals shows nothing. This regenerates
    the same story relative to the day it runs, and every image file it
    references is written at the same time, so no path can dangle.

    Take the dump AFTER running this, from a database it has just built.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlalchemy as sa                                          # noqa: E402

from seed import fnb, hotel, masterdata, users                   # noqa: E402
from seed.common import (                                        # noqa: E402
    SCHEMAS, TODAY, counts, engine_for, insert, report, upload_dir, wipe,
)

# Directories the seed owns. Cleared before writing so a rebuild cannot leave
# yesterday's orphaned images behind to be shipped with the database.
IMAGE_DIRS = [
    ("hotelerp_masterdata", ("upload_image",)),
    ("hotelerp_users", ("users",)),
    ("hotelerp_hotel", ("identity_proofs",)),
    ("hotelerp_hotel", ("room_incidents",)),
    ("hotelerp_restaurant", ("upload_image",)),
    ("hotelerp_bar", ("upload_image",)),
]


def clear_images() -> int:
    removed = 0
    for schema, parts in IMAGE_DIRS:
        d = upload_dir(schema, *parts)
        if os.path.isdir(d):
            for name in os.listdir(d):
                path = os.path.join(d, name)
                if os.path.isfile(path):
                    os.remove(path)
                    removed += 1
        os.makedirs(d, exist_ok=True)
    return removed


def image_counts() -> dict[str, int]:
    out = {}
    for schema, parts in IMAGE_DIRS:
        d = upload_dir(schema, *parts)
        out["/".join((schema,) + parts)] = (
            len(os.listdir(d)) if os.path.isdir(d) else 0
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true",
                    help="actually wipe and rebuild. Without it, nothing is written.")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what is there now and exit.")
    args = ap.parse_args()

    print(f"Business date anchor: {TODAY}")

    if args.dry_run or not args.confirm:
        print("\nCurrent contents (nothing will be changed):")
        total = 0
        for schema in SCHEMAS:
            with engine_for(schema).connect() as conn:
                c = counts(conn)
                filled = {k: v for k, v in c.items() if v}
                n = sum(filled.values())
                total += n
                print(f"  {schema:<24} {len(filled):>3} tables, {n:>6} rows")
        print(f"  {'TOTAL':<24} {'':>3}         {total:>6} rows")
        imgs = image_counts()
        print("\nImage files on disk:")
        for k, v in imgs.items():
            print(f"  {k:<48} {v:>5}")
        if not args.confirm:
            print("\nNothing written. Re-run with --confirm to rebuild.")
        return 0

    print("\nClearing generated images…")
    removed = clear_images()
    print(f"  removed {removed} file(s)")

    summary: dict[str, dict] = {}

    # ---- users ------------------------------------------------------------
    print("\nRebuilding hotelerp_users…")
    with engine_for("hotelerp_users").begin() as conn:
        emptied = wipe(conn, "hotelerp_users")
        print(f"  emptied {len(emptied)} tables")
        summary["users"] = users.seed(conn)
        report("hotelerp_users", counts(conn))

    # ---- master data ------------------------------------------------------
    print("\nRebuilding hotelerp_masterdata…")
    with engine_for("hotelerp_masterdata").begin() as conn:
        emptied = wipe(conn, "hotelerp_masterdata")
        print(f"  emptied {len(emptied)} tables")
        summary["masterdata"] = masterdata.seed(conn)
        report("hotelerp_masterdata", counts(conn))

    # ---- hotel ------------------------------------------------------------
    print("\nRebuilding hotelerp_hotel…")
    with engine_for("hotelerp_hotel").begin() as conn:
        emptied = wipe(conn, "hotelerp_hotel")
        print(f"  emptied {len(emptied)} tables")
        h = hotel.seed(conn, TODAY)
        ops = hotel.seed_operations(
            conn, TODAY, h["occupied_today"], h["dirty_rooms"], h["incident_dir"])
        summary["hotel"] = {**h, **ops}
        report("hotelerp_hotel", counts(conn))

    # ---- restaurant and bar ----------------------------------------------
    for label, schema, fn in (("hotelerp_restaurant", "hotelerp_restaurant", fnb.seed_restaurant),
                              ("hotelerp_bar", "hotelerp_bar", fnb.seed_bar)):
        print(f"\nRebuilding {label}…")
        with engine_for(schema).begin() as conn:
            emptied = wipe(conn, schema)
            print(f"  emptied {len(emptied)} tables")
            summary[schema] = fn(conn)
            report(label, counts(conn))

    # ---- room states, derived from the bookings ---------------------------
    # Occupancy is not typed in: it is what the reservations imply, which is
    # exactly what `sync_room_booking_status` recomputes at runtime. Setting it
    # here by hand would be a second opinion free to drift from the API's.
    print("\nReconciling room states from the bookings…")
    with engine_for("hotelerp_masterdata").begin() as conn:
        occupied = summary["hotel"]["occupied_today"]
        dirty = summary["hotel"]["dirty_rooms"]
        if occupied:
            conn.execute(
                sa.text("UPDATE room SET Room_Booking_status='Occupied' "
                        "WHERE Room_No IN :nos").bindparams(
                            sa.bindparam("nos", expanding=True)),
                {"nos": occupied})
        if dirty:
            conn.execute(
                sa.text("UPDATE room SET Room_Working_status='Not Ready' "
                        "WHERE Room_No IN :nos").bindparams(
                            sa.bindparam("nos", expanding=True)),
                {"nos": dirty})
        print(f"  {len(occupied)} occupied, {len(dirty)} awaiting cleaning")

    # ---- report -----------------------------------------------------------
    print("\n" + "=" * 66)
    print("REBUILD COMPLETE")
    print("=" * 66)
    u = summary["users"]
    print(f"  staff accounts     : {u['staff']}   (password: {u['password']})")
    print(f"  role permissions   : {u['permissions']}")
    m = summary["masterdata"]
    print(f"  rooms              : {m['rooms']} across {m['room_types']} types")
    h = summary["hotel"]
    print(f"  reservations       : {h['reservations']}")
    print(f"  payments recorded  : {h['payments']}")
    print(f"  housekeeping tasks : {h['tasks']}")
    print(f"  incidents logged   : {h['incidents']}")
    print(f"  guest enquiries    : {h['enquiries']}")
    for schema, label in (("hotelerp_restaurant", "restaurant"), ("hotelerp_bar", "bar")):
        f = summary[schema]
        print(f"  {label:<18} : {f['menu_items']} menu items, {f['tables']} tables, "
              f"{f['bills']} settled bills ({f['revenue']:,.2f})")

    print("\n  Images written:")
    for k, v in image_counts().items():
        print(f"    {k:<48} {v:>5}")

    print("\n  Next: regenerate the RBAC map, which reads the live menu table —")
    print("      python Backend/tools/build_rbac_map.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

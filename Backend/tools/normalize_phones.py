"""Rewrite stored phone numbers into canonical E.164.

    python Backend/tools/normalize_phones.py --dry-run
    python Backend/tools/normalize_phones.py --confirm

WHY THIS EXISTS
    Country-aware validation (C-086) stores every accepted number as E.164, so
    `+91 98765 43210`, `09876543210` and `9876543210` are one value and the
    uniqueness index on `mobile` can do its job. Rows written before that change
    still hold whatever the form sent -- the demo data holds bare ten-digit
    numbers -- so a fresh write and an old row for the same guest would not
    match, and the guest lookup that joins on `mobile` would miss.

    This walks the tables that hold a phone number and rewrites each value
    through the same `normalize_phone` the API now uses, so the script and the
    service cannot disagree about what a number is.

    IT IS SAFE TO RE-RUN
    A value already in E.164 parses to itself, so a second pass changes nothing.
    That is asserted by the idempotence check the script prints.

    WHAT IT CANNOT DO
    It does not invent a country. A bare national number is read in
    --default-region, which defaults to IN because this demo data is Indian; pass
    --default-region=GB for a property elsewhere. Anything that does not parse is
    reported and LEFT ALONE, never guessed: a wrong country code silently
    attached to a guest is worse than an unnormalised one.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Backend" / "Services" / "HotelServices"))

from fastapi import HTTPException  # noqa: E402
from resources.validation import normalize_phone  # noqa: E402

# (schema, table, column, label). Only the tables this application actually
# stores a person's or a guest's number in.
TARGETS = [
    ("hotelerp_hotel", "room_reservation", "phone_number", "reservations"),
    ("hotelerp_hotel", "room_booking", "phone_number", "booking enquiries"),
    ("hotelerp_users", "users", "Mobile", "employees"),
    ("hotelerp_users", "users", "Alternative_Mobile", "employee alternatives"),
    ("hotelerp_restaurant", "guest", "mobile", "restaurant guests"),
    ("hotelerp_bar", "bar_guest", "mobile", "bar guests"),
]


def engines():
    import sqlalchemy as sa
    from seed.common import engine_for  # the seed knows where the DBs live
    out = {}
    for schema, _table, _col, _label in TARGETS:
        if schema not in out:
            out[schema] = engine_for(schema)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", action="store_true",
                        help="write the changes (without it, nothing is written)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report only; the default when --confirm is absent")
    parser.add_argument("--default-region", default="IN",
                        help="country to read bare national numbers in (default IN)")
    parser.add_argument("--fix-fiction-range", action="store_true",
                        help="also replace the old seed's '+1555...' placeholders, which are "
                             "the US FICTION range and are not assignable numbers")
    args = parser.parse_args()

    import sqlalchemy as sa
    eng = engines()
    report = []
    skipped = []
    fiction_fixed = []

    for schema, table, column, label in TARGETS:
        engine = eng[schema]
        with engine.connect() as conn:
            rows = conn.execute(sa.text(
                f"SELECT id, `{column}` FROM `{table}` WHERE `{column}` IS NOT NULL"
                f" AND `{column}` <> ''"
            )).mappings().all()
            changed = 0
            for row in rows:
                current = str(row[column])
                # The previous seed wrote `+1 555 000 0000` and `+1 555 123 4567`.
                # 555-01xx is reserved for fiction, so no validator may accept it --
                # and a demo row the application would refuse to edit is worse than
                # a wrong one. Rewriting is opt-in and reported, never silent.
                if args.fix_fiction_range and re.sub(r"[^0-9]", "", current).startswith("1555"):
                    from seed.common import phone as _phone
                    replacement = _phone(row["id"] + 500)
                    fiction_fixed.append((label, table, row["id"], current, replacement))
                    if args.confirm:
                        conn.execute(
                            sa.text(f"UPDATE `{table}` SET `{column}` = :v WHERE id = :i"),
                            {"v": replacement, "i": row["id"]},
                        )
                    # Counted so the commit below fires: an UPDATE that is never
                    # committed is the kind of "it said it fixed them" that isn't.
                    changed += 1
                    continue
                try:
                    normalized = normalize_phone(current, field=column,
                                                 default_region=args.default_region)
                except HTTPException as exc:
                    skipped.append((label, row["id"], current, str(exc.detail)))
                    continue
                if normalized is None or normalized == current:
                    continue
                changed += 1
                if args.confirm:
                    conn.execute(
                        sa.text(f"UPDATE `{table}` SET `{column}` = :v WHERE id = :i"),
                        {"v": normalized, "i": row["id"]},
                    )
                report.append((label, table, row["id"], current, normalized))
            if args.confirm and changed:
                conn.commit()
            if changed:
                print(f"{label:22s} {table}.{column}: {changed} row(s)"
                      f"{'' if args.confirm else ' (dry run)'}")

    if report:
        print("\nExamples of what changed:")
        for label, table, rid, before, after in report[:8]:
            print(f"  {label:22s} id {rid:<5} {before:>18}  ->  {after}")
        if len(report) > 8:
            print(f"  ... and {len(report) - 8} more")

    if fiction_fixed:
        print("\nOld seed placeholders replaced (the 555 range is reserved for fiction):")
        for label, table, rid, before, after in fiction_fixed[:6]:
            print(f"  {label:22s} {table} id {rid:<4} {before!r:>18}  ->  {after}")
        if len(fiction_fixed) > 6:
            print(f"  ... and {len(fiction_fixed) - 6} more")

    if skipped:
        print("\nLeft alone because the value is not a usable number")
        print("(a wrong country code attached silently is worse than no rewrite):")
        for label, rid, value, why in skipped[:10]:
            print(f"  {label:22s} id {rid:<5} {value!r:>20}  {why}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")
        if not args.fix_fiction_range and any(v.startswith("+1555") for _l, _i, v, _w in skipped):
            print("  (some are the old seed's fiction-range placeholders;"
                  " re-run with --fix-fiction-range to replace them)")

    if not args.confirm and (report or fiction_fixed):
        print("\nDry run. Re-run with --confirm to write these changes.")
    elif args.confirm and (report or fiction_fixed):
        # Prove the second pass has nothing left to do.
        remaining = 0
        for schema, table, column, _label in TARGETS:
            with eng[schema].connect() as conn:
                for row in conn.execute(sa.text(
                    f"SELECT `{column}` FROM `{table}` WHERE `{column}` IS NOT NULL"
                )).mappings():
                    try:
                        if normalize_phone(str(row[column]), field=column,
                                           default_region=args.default_region) != str(row[column]):
                            remaining += 1
                    except HTTPException:
                        remaining += 1
        print(f"\nIdempotence check: {remaining} value(s) would still change on a second pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

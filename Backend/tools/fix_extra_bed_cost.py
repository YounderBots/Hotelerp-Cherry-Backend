#!/usr/bin/env python3
"""Correct reservations whose `extra_bed_cost` holds a total, not a rate.

    python Backend/tools/fix_extra_bed_cost.py             # report only
    python Backend/tools/fix_extra_bed_cost.py --confirm   # write the fix

WHY THIS EXISTS
    `room_reservation.extra_bed_cost` is the cost of ONE extra bed for the
    whole stay. The charge is that times `extra_bed_count`, and the reservation
    view draws the pair as "6,000.00 x 2". Two writers disagreed about it:

      * the API (reservation_rules.quote) always stored the rate -- correct;
      * the seed (tools/seed/hotel.folio) stored the TOTAL for all the beds,
        so a seeded two-bed booking rendered its folio line at twice what was
        billed, and the folio identity

            room + beds x count + extras - discount + tax = overall

        that verify_seed asserts could not hold for it.

    Both writers were fixed on 17 September 2026. Rows written before that
    still carry the old meaning, and a `git pull` does not change stored data
    -- which is what this tool is for. It is needed anywhere those rows live:
    a database seeded from an older build, a restore of the 15-Sept-2026
    release, and the live deployment.

WHAT IT CHANGES
    `room_reservation.extra_bed_cost`, and nothing else. No other column, no
    other table, and never `overall_amount` -- the money the guest was charged
    is not in question here and is never rewritten. Only the per-bed figure
    that describes it is.

HOW IT KNOWS THE RIGHT VALUE
    It does not guess or re-price from master data, which could have changed
    since the booking. It derives the answer from the row's own money:

        bed total = overall - tax + discount - extra charges - room
        per bed   = bed total / count

    Then it checks the identity holds with that value before writing, and
    refuses the row if it does not. A row whose totals are inconsistent for
    some *other* reason is reported and left alone: this tool corrects one
    known misunderstanding, and is not a general folio repair.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import pymysql
except ImportError:                                            # pragma: no cover
    print("ERROR: pymysql is not installed. "
          "pip install -r Backend/requirements.txt", file=sys.stderr)
    raise SystemExit(2)

REPO = Path(__file__).resolve().parents[2]
HOTEL_ENV = REPO / "Backend" / "Services" / "HotelServices" / ".env"

TOLERANCE = 0.02   # the same 2-paise tolerance verify_seed uses


def parse_dsn(uri: str) -> dict:
    m = re.match(
        r"^mysql(?:\+\w+)?://(?P<user>[^:/@]*)(?::(?P<pw>[^@]*))?@"
        r"(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<db>[^?]+)", uri.strip())
    if not m:
        raise SystemExit("ERROR: could not parse DB_URI")
    return {"user": unquote(m.group("user")), "password": unquote(m.group("pw") or ""),
            "host": m.group("host"), "port": int(m.group("port") or 3306),
            "db": m.group("db").strip()}


def dsn_from_env(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"ERROR: {path} not found. Pass --db-uri instead.")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("DB_URI="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"ERROR: no DB_URI in {path}")


def identity_gap(room, count, cost, extras, discount, tax, overall) -> float:
    """How far this row is from adding up. Zero means it balances."""
    return (room + count * cost + extras - discount + tax) - overall


def main() -> int:
    p = argparse.ArgumentParser(
        description="Correct extra_bed_cost rows written as a total.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--db-uri", help="Override the Hotel service's DB_URI")
    p.add_argument("--confirm", action="store_true",
                   help="Actually write. Without it nothing is changed.")
    args = p.parse_args()

    cfg = parse_dsn(args.db_uri or dsn_from_env(HOTEL_ENV))
    conn = pymysql.connect(host=cfg["host"], port=cfg["port"], user=cfg["user"],
                           password=cfg["password"], database=cfg["db"],
                           charset="utf8mb4")
    print(f"database: {cfg['db']} on {cfg['host']}:{cfg['port']}\n")

    # Which rows fail is decided BY MYSQL, with the same expression and the
    # same tolerance verify_seed uses.
    #
    # Not in Python, which would disagree with it. These money columns are
    # single-precision FLOAT, so a folio that reconciles exactly still
    # round-trips with a few paise of representational error: one row here
    # reads as off by 0.05 once the values are widened to Python doubles,
    # while MySQL -- evaluating the whole expression in the precision the data
    # is actually stored in -- puts it at 0.0005. Judging in Python would flag
    # rows this tool then could not correct, and would disagree with the check
    # it exists to satisfy.
    IDENTITY_GAP = """ABS((room_amount
            + COALESCE(extra_bed_count, 0) * COALESCE(extra_bed_cost, 0)
            + extra_charges - discount_amount + tax_amount) - overall_amount)"""
    COLUMNS = """id, room_reservation_id, room_amount,
                 COALESCE(extra_bed_count, 0), COALESCE(extra_bed_cost, 0),
                 extra_charges, discount_amount, tax_amount, overall_amount"""

    with conn.cursor() as cur:
        cur.execute(f"SELECT {COLUMNS} FROM room_reservation "
                    f"WHERE {IDENTITY_GAP} > %s", (TOLERANCE,))
        unbalanced = cur.fetchall()
        # Balances, but records a bed rate against a booking that took no bed.
        # Harmless to the arithmetic, because it is multiplied by zero, but it
        # draws "1,600.00 x 0" on the reservation view and reads as a charge in
        # an export.
        cur.execute(f"SELECT id, room_reservation_id, extra_bed_cost "
                    f"FROM room_reservation "
                    f"WHERE COALESCE(extra_bed_count, 0) = 0 "
                    f"  AND COALESCE(extra_bed_cost, 0) <> 0 "
                    f"  AND {IDENTITY_GAP} <= %s", (TOLERANCE,))
        cosmetic = [(pk, ref, float(cost or 0)) for pk, ref, cost in cur.fetchall()]

    fixes, refused = [], []
    for (pk, ref, room, count, cost, extras, discount, tax, overall) in unbalanced:
        room, extras, discount, tax, overall = (
            float(v or 0) for v in (room, extras, discount, tax, overall))
        count, cost = int(count or 0), float(cost or 0)

        bed_total = overall - tax + discount - extras - room
        if count == 0:
            want = 0.0
        elif bed_total < -TOLERANCE:
            refused.append((ref, f"implies a negative bed total of {bed_total:,.2f}"))
            continue
        else:
            want = round(bed_total / count, 2)

        if abs(identity_gap(room, count, want, extras, discount, tax, overall)) > TOLERANCE:
            refused.append((ref, "does not add up even with the bed cost corrected; "
                                 "this is not the bug this tool fixes"))
            continue
        fixes.append((pk, ref, cost, want, count))

    if fixes:
        print(f"=== {len(fixes)} row(s) storing a total where a rate belongs ===")
        for _pk, ref, was, want, count in fixes:
            print(f"  {ref}: {was:,.2f} -> {want:,.2f}  (x {count} beds "
                  f"= {want * count:,.2f}, unchanged)")
        print()
    if cosmetic:
        print(f"=== {len(cosmetic)} row(s) with a bed rate but no bed booked ===")
        for _pk, ref, was in cosmetic:
            print(f"  {ref}: {was:,.2f} -> 0.00  (count is 0; the folio already "
                  "balances, the figure is just wrong on screen)")
        print()
    if refused:
        print(f"=== {len(refused)} row(s) left alone ===")
        for ref, why in refused:
            print(f"  {ref}: {why}")
        print()

    if not fixes and not cosmetic:
        print("Nothing to correct." if not refused else
              "Nothing this tool can correct.")
        return 1 if refused else 0

    if not args.confirm:
        print("DRY RUN -- nothing written. Re-run with --confirm to apply.")
        return 1

    with conn.cursor() as cur:
        for pk, _ref, _was, want, _count in fixes:
            cur.execute("UPDATE room_reservation SET extra_bed_cost = %s WHERE id = %s",
                        (want, pk))
        for pk, _ref, _was in cosmetic:
            cur.execute("UPDATE room_reservation SET extra_bed_cost = 0 WHERE id = %s",
                        (pk,))
    conn.commit()
    print(f"corrected {len(fixes) + len(cosmetic)} row(s).")

    # Prove it, rather than announce it.
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM room_reservation
            WHERE ABS((room_amount
                       + COALESCE(extra_bed_count, 0) * COALESCE(extra_bed_cost, 0)
                       + extra_charges - discount_amount + tax_amount)
                      - overall_amount) > %s
        """, (TOLERANCE,))
        left = cur.fetchone()[0]
    print(f"reservations still failing the folio identity: {left}")
    if left:
        print("Those are a different problem; run Backend/tools/verify_seed.py.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

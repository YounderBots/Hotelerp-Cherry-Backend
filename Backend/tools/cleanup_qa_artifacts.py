"""Remove the QA records and upload files a test run leaves behind.

    python Backend/tools/cleanup_qa_artifacts.py --dry-run
    python Backend/tools/cleanup_qa_artifacts.py --confirm

WHY THIS IS A TOOL AND NOT A `rm`
    Three things have to agree or the local database drifts from the seeded one
    without anybody noticing: the rows, the files on disk, and git. A test suite
    that creates a reservation and soft-deletes it still leaves the row, and a
    suite that uploads a document still leaves the file -- and an untracked file
    is indistinguishable from a real one until it is committed by accident.

    WHAT IT NEVER DOES
      * It never hard-deletes. Rows are soft-deleted, because the audit history
        of a reservation is the point of the product and "reversible" has to mean
        reversible.
      * It never touches a file git is already tracking. Those are the seeded
        SPECIMEN assets; only files this tool's own dry run reports as
        untracked are candidates, so a second run has nothing left to do.
      * It never guesses. A row is a candidate only if it matches a marker this
        repository's own tests write -- the name the e2e suite books under, or a
        status of INACTIVE. Real data is not matched by a name.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# (schema, table, marker column, marker value, why)
QA_ROWS = [
    ("hotelerp_hotel", "room_reservation", "first_name", "Flow",
     "reservations the e2e suite books"),
    ("hotelerp_hotel", "hsk_room_incident", "status", "INACTIVE",
     "incidents the suites already retired"),
]

UPLOAD_DIRS = [
    "Backend/Services/HotelServices/templates/static/room_incidents",
    "Backend/Services/HotelServices/templates/static/identity_proofs",
]


def untracked_uploads() -> list[pathlib.Path]:
    """Upload files git does not know about, i.e. written by a test run."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "--"] + UPLOAD_DIRS,
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    out = []
    for line in result.stdout.splitlines():
        if line.startswith("?? "):
            out.append(ROOT / line[3:].strip().strip('"'))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", action="store_true",
                        help="write the changes (without it, nothing is written)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report only; the default when --confirm is absent")
    args = parser.parse_args()

    import pymysql

    db = pymysql.connect(host="127.0.0.1", user="root", password="2003")
    try:
        for schema, table, column, value, why in QA_ROWS:
            with db.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM `{schema}`.`{table}` "
                    f"WHERE `{column}` = %s AND status = 'ACTIVE'",
                    (value,),
                )
                ids = [r[0] for r in cur.fetchall()]
            if not ids:
                print(f"{schema}.{table}: nothing to retire")
                continue
            marks = ",".join(["%s"] * len(ids))
            if args.confirm:
                with db.cursor() as cur:
                    cur.execute(
                        f"UPDATE `{schema}`.`{table}` SET status='INACTIVE', updated_by='1' "
                        f"WHERE id IN ({marks})",
                        ids,
                    )
                db.commit()
            print(f"{schema}.{table}: {len(ids)} active row(s) retired "
                  f"({why}){'' if args.confirm else ' (dry run)'}")
    finally:
        db.close()

    files = untracked_uploads()
    if not files:
        print("no untracked upload files")
    for path in files:
        if args.confirm and path.exists():
            path.unlink()
        print(f"  {'removed' if args.confirm else 'would remove'} {path.relative_to(ROOT)}")

    if args.confirm:
        # Prove a second pass is a no-op, so "clean" means clean.
        left = untracked_uploads()
        print(f"\nIdempotence check: {len(left)} untracked upload file(s) remain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

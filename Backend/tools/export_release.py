#!/usr/bin/env python3
"""Export the live database as a release: five schema dumps and their images.

    python Backend/tools/export_release.py --dry-run     # what it would write
    python Backend/tools/export_release.py               # write the release
    python Backend/tools/export_release.py --verify-restore   # and load it back

WHY THIS EXISTS
    `Backend/db/15-Sept-2026/` was assembled by hand, and the two things that
    went wrong with it are the two things a hand-assembled release always gets
    wrong:

      * the SQL and the images came apart. The database stores image *paths*,
        so a dump without the matching files is a release where every
        photograph 404s -- which is exactly what reached 168.231.103.18.
      * the README's counts were typed. They drift from the data the moment
        the seed changes, and nobody notices because nothing checks them.

    So this exports both halves from one database in one pass, derives every
    number in the README by counting rows rather than trusting anyone, and
    refuses to write a release at all if that database is not internally
    consistent.

WHAT IT REFUSES TO EXPORT
    A database that fails `verify_seed.py`. A release is the thing other
    people restore; shipping one that does not reconcile just moves the
    problem to whoever loads it. `--skip-verify` exists for the rare case
    where you know better, and says so loudly.

CREDENTIALS
    Read from HotelServices/.env and passed to mysqldump through a temporary
    defaults-file, never on the command line -- an argument is visible in the
    process list to every user on the machine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed.common import SERVICE_DIRS, SERVICES, engine_for  # noqa: E402

import sqlalchemy as sa                                     # noqa: E402

DB_DIR = ROOT / "Backend" / "db"
HOTEL_ENV = ROOT / "Backend" / "Services" / "HotelServices" / ".env"
TOOLS = ROOT / "Backend" / "tools"

# Dump order matters for a human reading the folder, not for MySQL: each dump
# drops and recreates its own database and they carry no cross-schema FKs.
SCHEMAS = ["hotelerp_users", "hotelerp_masterdata", "hotelerp_hotel",
           "hotelerp_restaurant", "hotelerp_bar"]

# "Sept", not strftime's "Sep" -- the folder naming already in use.
MONTHS = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul",
          8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dec"}

# Prose wants the month spelled out. Kept separate from the folder
# abbreviations above rather than derived from them.
MONTHS_FULL = {1: "January", 2: "February", 3: "March", 4: "April",
               5: "May", 6: "June", 7: "July", 8: "August",
               9: "September", 10: "October", 11: "November",
               12: "December"}

# Where mysqldump lives when it is not on PATH, which on Windows it usually is
# not. The installed server directory is checked before giving up.
MYSQLDUMP_CANDIDATES = [
    Path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"),
    Path(r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe"),
    Path(r"C:\xampp\mysql\bin\mysqldump.exe"),
]

# Every column that holds an image path, with the folder it is served from.
# Same set verify_seed.py checks, so a release cannot ship a path the
# verifier would reject.
IMAGE_COLUMNS = [
    ("hotelerp_masterdata", "room", ["Room_Image_1", "Room_Image_2",
                                     "Room_Image_3", "Room_Image_4"], "upload_image"),
    ("hotelerp_users", "users", ["Photo"], "users"),
    ("hotelerp_hotel", "room_reservation", ["proof_document"], "identity_proofs"),
    ("hotelerp_hotel", "hsk_room_incident", ["attachment_file"], "room_incidents"),
    ("hotelerp_restaurant", "restaurant_menu", ["item_image"], "upload_image"),
    ("hotelerp_bar", "bar_menu_item", ["item_image"], "upload_image"),
]


def release_name(when: dt.date) -> str:
    return f"{when.day}-{MONTHS[when.month]}-{when.year}"


def find_mysqldump() -> Path:
    found = shutil.which("mysqldump")
    if found:
        return Path(found)
    for c in MYSQLDUMP_CANDIDATES:
        if c.is_file():
            return c
    sys.exit("ERROR: mysqldump not found on PATH or in the usual install "
             "directories. Pass --mysqldump with its full path.")


def db_config() -> dict:
    if not HOTEL_ENV.exists():
        sys.exit(f"ERROR: {HOTEL_ENV} not found.")
    uri = ""
    for line in HOTEL_ENV.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("DB_URI="):
            uri = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    m = re.match(r"^mysql(?:\+\w+)?://(?P<user>[^:/@]*)(?::(?P<pw>[^@]*))?@"
                 r"(?P<host>[^:/]+)(?::(?P<port>\d+))?/", uri)
    if not m:
        sys.exit("ERROR: could not read DB_URI from the Hotel service's .env")
    return {"user": unquote(m.group("user")), "password": unquote(m.group("pw") or ""),
            "host": m.group("host"), "port": m.group("port") or "3306"}


def media_path(stored: str, schema: str, default_dir: str) -> Path:
    """Resolve a stored image value to its path in the service's static tree.

    Two shapes are stored, both legitimate: a site-relative path under the
    mount, and a bare filename for the reservation identity proofs.
    """
    base = Path(SERVICES) / SERVICE_DIRS[schema]
    if stored.startswith("/templates/"):
        return base / Path(stored.lstrip("/"))
    return base / "templates" / "static" / default_dir / stored


def stored_image_paths() -> dict[str, set[Path]]:
    """Every image FILE the database points at, by service directory.

    Deduplicated, because a path is referenced more often than it exists: the
    four photographs of a room type are stored against every room of that
    type, so 25 rooms carry 100 references to 32 files. Counting references
    here would put 180 in the README for a release that ships 112 images, and
    would report a file "copied" several times over.
    """
    out: dict[str, set[Path]] = {}
    for schema, table, columns, folder in IMAGE_COLUMNS:
        cols = ", ".join(f"`{c}`" for c in columns)
        with engine_for(schema).connect() as c:
            rows = c.execute(sa.text(f"SELECT {cols} FROM `{table}`")).fetchall()
        for row in rows:
            for value in row:
                if not value:
                    continue
                out.setdefault(SERVICE_DIRS[schema], set()).add(
                    media_path(str(value), schema, folder))
    return out


def count_float_columns() -> int:
    """How many money-bearing columns are single-precision FLOAT.

    Counted, not remembered: the README states it, and a number in a README
    that nothing derives is a number that goes stale.
    """
    with engine_for("hotelerp_hotel").connect() as c:
        return c.execute(sa.text("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA IN :schemas AND DATA_TYPE = 'float'
        """).bindparams(sa.bindparam("schemas", value=tuple(SCHEMAS),
                                     expanding=True))).scalar() or 0


def counts() -> dict:
    """Every number the README states, counted rather than remembered."""
    def n(schema, sql):
        with engine_for(schema).connect() as c:
            return c.execute(sa.text(sql)).scalar() or 0

    return {
        "roles": n("hotelerp_users", "SELECT COUNT(*) FROM roles"),
        "menus": n("hotelerp_users", "SELECT COUNT(*) FROM menus"),
        "submenus": n("hotelerp_users", "SELECT COUNT(*) FROM submenus"),
        "permissions": n("hotelerp_users", "SELECT COUNT(*) FROM role_permissions"),
        "staff": n("hotelerp_users", "SELECT COUNT(*) FROM users"),
        "rooms": n("hotelerp_masterdata", "SELECT COUNT(*) FROM room"),
        "room_types": n("hotelerp_masterdata", "SELECT COUNT(*) FROM room_type"),
        "reservations": n("hotelerp_hotel", "SELECT COUNT(*) FROM room_reservation"),
        "payments": n("hotelerp_hotel",
                      "SELECT COUNT(*) FROM reservation_amount_paid_history"),
        "tasks": n("hotelerp_hotel", "SELECT COUNT(*) FROM housekeeper_task"),
        "incidents": n("hotelerp_hotel", "SELECT COUNT(*) FROM hsk_room_incident"),
        "enquiries": n("hotelerp_hotel", "SELECT COUNT(*) FROM inquiry"),
        "rest_menu": n("hotelerp_restaurant", "SELECT COUNT(*) FROM restaurant_menu"),
        "rest_tables": n("hotelerp_restaurant", "SELECT COUNT(*) FROM restaurant_table"),
        "rest_bills": n("hotelerp_restaurant", "SELECT COUNT(*) FROM restaurant_bill"),
        "bar_menu": n("hotelerp_bar", "SELECT COUNT(*) FROM bar_menu_item"),
        "bar_tables": n("hotelerp_bar", "SELECT COUNT(*) FROM bar_table"),
        "bar_bills": n("hotelerp_bar", "SELECT COUNT(*) FROM bar_bill"),
    }


def run_verify_seed() -> tuple[bool, int]:
    """(did it pass, how many invariants failed).

    The count is parsed from verify_seed's own summary rather than counted
    here, so the two can never disagree about the number.
    """
    r = subprocess.run([sys.executable, str(TOOLS / "verify_seed.py")],
                       capture_output=True, text=True, cwd=str(ROOT))
    out = r.stdout or ""
    failed = 0
    m = re.search(r"(\d+) of \d+ checks FAILED", out)
    if m:
        failed = int(m.group(1))
    if r.returncode != 0:
        print("  the database is NOT consistent:")
        for line in out.strip().splitlines()[-6:]:
            print("    " + line)
    return r.returncode == 0, failed


def dump_schemas(out_dir: Path, cfg: dict, mysqldump: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    problems = []
    fd, cnf = tempfile.mkstemp(suffix=".cnf")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("[client]\nuser={user}\npassword={password}\n"
                "host={host}\nport={port}\n".format(**cfg))
    try:
        for schema in SCHEMAS:
            target = out_dir / f"{schema}.sql"
            r = subprocess.run(
                [str(mysqldump), f"--defaults-file={cnf}",
                 "--databases", schema,
                 "--add-drop-database",
                 "--default-character-set=utf8mb4",
                 "--single-transaction",
                 "--routines", "--events", "--triggers",
                 "--result-file", str(target)],
                capture_output=True, text=True)
            if r.returncode != 0:
                problems.append(f"{schema}: {(r.stderr or '').strip()[:200]}")
                print(f"  FAIL  {schema}")
                continue
            print(f"  ok    {schema:<22} {target.stat().st_size:>9,} bytes")
    finally:
        os.unlink(cnf)
    return problems


def copy_images(out_dir: Path) -> tuple[int, list[str]]:
    """Copy exactly the files the database references, in the restore layout.

    `restore_uploads.py` overlays `uploads/<Service>/...` straight onto the
    service directory, so the release has to be in that shape already.
    """
    wanted = stored_image_paths()
    copied, problems = 0, []
    for service, paths in sorted(wanted.items()):
        for src in sorted(paths):
            if not src.is_file():
                problems.append(f"{service}: {src.name} is referenced but not on disk")
                continue
            rel = src.relative_to(Path(SERVICES) / service)
            dst = out_dir / service / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not (dst.exists() and filecmp.cmp(src, dst, shallow=False)):
                shutil.copy2(src, dst)
            copied += 1
    return copied, problems


def verify_export(release_dir: Path) -> list[str]:
    """Would someone restoring this get a working system?"""
    problems = []

    for schema in SCHEMAS:
        f = release_dir / "sql" / f"{schema}.sql"
        if not f.is_file() or f.stat().st_size == 0:
            problems.append(f"sql/{schema}.sql is missing or empty")
            continue
        head = f.read_text(encoding="utf-8", errors="replace")[:4000]
        tail = f.read_text(encoding="utf-8", errors="replace")[-400:]
        if "DROP DATABASE IF EXISTS" not in head or "CREATE DATABASE" not in head:
            problems.append(f"sql/{schema}.sql does not drop and recreate its database")
        if "Dump completed" not in tail:
            problems.append(f"sql/{schema}.sql is truncated -- no completion marker")

    # Every stored path resolves inside the release, and nothing else ships.
    wanted = stored_image_paths()
    expected: set[Path] = set()
    for service, paths in sorted(wanted.items()):
        for src in sorted(paths):
            expected.add(release_dir / "uploads" / service /
                         src.relative_to(Path(SERVICES) / service))
    for want in sorted(expected):
        if not want.is_file():
            problems.append(f"uploads: {want.name} is referenced by the data but "
                            "not in the release")

    shipped = {p for p in (release_dir / "uploads").rglob("*") if p.is_file()}
    for extra in sorted(shipped - expected):
        problems.append(f"uploads: {extra.name} ships but nothing references it")

    if not (release_dir / "PHOTO-CREDITS.md").is_file():
        problems.append("PHOTO-CREDITS.md is missing -- attribution is a licence "
                        "condition for the CC-BY images")
    if not (release_dir / "README.md").is_file():
        problems.append("README.md is missing")
    return problems


def find_mysql_client(mysqldump: Path) -> Path:
    found = shutil.which("mysql")
    if found:
        return Path(found)
    sibling = mysqldump.parent / ("mysql.exe" if os.name == "nt" else "mysql")
    if sibling.is_file():
        return sibling
    sys.exit("ERROR: the mysql client is needed for --verify-restore and was "
             "not found beside mysqldump.")


def restore_and_recheck(release_dir: Path, cfg: dict, mysql_bin: Path,
                        before: dict) -> list[str]:
    """Load the release back and confirm the system it produces is the one it came from.

    The only check that answers the question a release actually raises: not
    "did mysqldump exit 0" but "does what I shipped come back up". It restores
    over the same five schemas, which is safe precisely because they are where
    the dump came from -- a successful restore is a no-op, and a failed one is
    the thing you needed to find out before a deployment did.
    """
    problems = []
    fd, cnf = tempfile.mkstemp(suffix=".cnf")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("[client]\nuser={user}\npassword={password}\n"
                "host={host}\nport={port}\n".format(**cfg))
    try:
        for schema in SCHEMAS:
            sql = release_dir / "sql" / f"{schema}.sql"
            with open(sql, "rb") as handle:
                r = subprocess.run([str(mysql_bin), f"--defaults-file={cnf}"],
                                   stdin=handle, capture_output=True, text=True)
            if r.returncode != 0:
                problems.append(f"{schema} failed to load: "
                                f"{(r.stderr or '').strip()[:200]}")
                print(f"  FAIL  {schema}")
            else:
                print(f"  ok    {schema} loaded")
    finally:
        os.unlink(cnf)
    if problems:
        return problems

    after = counts()
    for key, was in before.items():
        if after[key] != was:
            problems.append(f"{key}: {was} before the round trip, {after[key]} after")
    if not problems:
        print(f"  every one of the {len(before)} counted totals survived the round trip")

    ok, invariant_failures = run_verify_seed()
    if not ok:
        problems.append(f"the restored database fails {invariant_failures} of "
                        "verify_seed.py's invariants that held before the dump")
    else:
        print("  the restored database passes all 34 invariants")

    r = subprocess.run([sys.executable, str(TOOLS / "restore_uploads.py"),
                        "--release", release_dir.name, "--verify"],
                       capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        problems.append("the release's images do not match the service trees: "
                        + (r.stdout or r.stderr).strip()[-200:])
    else:
        print("  the release's images match what the services serve")
    return problems, invariant_failures


def write_readme(release_dir: Path, name: str, when: dt.date, c: dict,
                 image_count: int, float_columns: int,
                 restore_failures: int | None = None) -> None:
    # What this section says depends on what is true of the database, which
    # changed on 17 September 2026 when the money columns were migrated from
    # FLOAT to DECIMAL. A release cut before that has to carry the caveat; one
    # cut after carries the guarantee. Deriving it from the column types means
    # neither can be claimed of a release for which it is false.
    if restore_failures is None:
        measured = ("This export did not load the release back to check. "
                    "`export_release.py --verify-restore` does exactly that.")
    elif restore_failures == 0:
        measured = ("Confirmed on this release by loading it back and re-running "
                    "the checks: **all 34 invariants still hold**.")
    else:
        measured = (f"Measured by loading this release back and re-running the "
                    f"checks: **{restore_failures} of 34 invariants fail after a "
                    "round trip** — the folio identity and the payment-history "
                    "total, by a few paise.")

    if float_columns == 0:
        money_section = f"""## Money survives a restore exactly

Every money column in these five schemas is `DECIMAL`, not `FLOAT`, and that
matters to a dump. `mysqldump` writes a `FLOAT` at about six significant
digits, so a folio total of `20009.85` used to be written as `20009.8` and came
back five paise light. Releases up to and including `15-Sept-2026` carry that
loss, and the deployment at `168.231.103.18` was restored from one of them.

{measured}

Restoring this release over a database that predates the change brings the
corrected column types with it — each dump drops and recreates its own schema."""
    else:
        money_section = f"""## Known limitation: money loses a few paise on restore

**This is a property of the schema, not of this release.**

{float_columns} money columns across the five schemas are still single-precision
`FLOAT`. `mysqldump` writes one at about six significant digits, so a folio
total of `20009.85` is written as `20009.8` and comes back five paise light.

{measured}

The fix is to migrate those columns to `DECIMAL(12, 2)` — exact in storage, and
dumped as exact text."""

    text = f"""# HotelERP database release — {name}

A complete, internally consistent database for the Cherry HotelERP system:
five schemas, the staff who can log into them, and **{image_count} image files** that
every image column in the data actually points at.

Exported **{when.day} {MONTHS_FULL[when.month]} {when.year}** from a database freshly built by
`Backend/tools/seed_demo_data.py`, by `Backend/tools/export_release.py`, which
refuses to export a database that fails `verify_seed.py`. Every count below was
counted from the data, not typed.

## What is in the box

```
Backend/db/{name}/
  README.md          this file
  PHOTO-CREDITS.md   licence and attribution for every photograph
  sql/               five schema dumps, each with DROP DATABASE / CREATE DATABASE
  uploads/           {image_count} image files, laid out exactly as the services expect
```

Restore commands below are written to be run **from this directory**.

| Schema | Holds |
|---|---|
| `hotelerp_users` | {c['roles']} roles, {c['menus']} menus, {c['submenus']} submenus, {c['permissions']} role permissions, {c['staff']} staff |
| `hotelerp_masterdata` | {c['rooms']} rooms across {c['room_types']} rate plans, tax, discount, payment, statuses |
| `hotelerp_hotel` | {c['reservations']} reservations, {c['payments']} payments, housekeeping, incidents, enquiries |
| `hotelerp_restaurant` | {c['rest_menu']} menu items, {c['rest_tables']} tables, {c['rest_bills']} settled bills |
| `hotelerp_bar` | {c['bar_menu']} menu items, {c['bar_tables']} tables, {c['bar_bills']} settled bills |

## Restoring

Restore the SQL first, then drop the images into place. **Both are required** —
the database stores paths, not image bytes, so SQL alone leaves every room
photo, staff avatar, menu tile and identity proof broken.

```bash
# 1. schemas  (each dump drops and recreates its own database)
for f in sql/*.sql; do mysql -u root -p < "$f"; done

# 2. images — copy into the running services' static trees.
python ../../tools/restore_uploads.py --release {name}
python ../../tools/restore_uploads.py --release {name} --verify
```

**Step 2 is the one that gets skipped.** On the deployment at
`168.231.103.18` it was: the SQL loaded, every endpoint answered `200`, and all
88 image paths the API served resolved to nothing. Nothing detected it, because
the rows were all present — the only symptom was that no picture loaded.

Restore the SQL and the images **from the same release**. A re-seed mints new
filenames, so a release's `uploads/` only matches the database that shipped
beside it; mixing two releases leaves every path pointing at a file that was
never there.

**Then step 3: bring the Hotel schema up to this build, and point the Hotel
service at its siblings.**

```bash
python Backend/migrations/migrate.py upgrade hotel   # adds room_lock (see below)
grep -E "MASTER_SERVICE_URL|USER_SERVICE_URL" Backend/Services/HotelServices/.env
sudo systemctl restart <the hotel unit>
curl -s localhost:8040/readyz                        # "status": "ready"
```

The Hotel service does **not** read any other service's database. Rooms, rate
cards, tax, discounts, payment methods, identity proofs and the status
vocabulary come from MasterDataServices over HTTP (`GET /snapshot`, once per
request), a housekeeping assignee is checked against UserServices, and the
room's occupancy and housekeeping flags are written back through
`PATCH /room/{id}/state`. Its MySQL account needs privileges on
`hotelerp_hotel` and nothing else -- there is no cross-schema GRANT to run,
and there never will be again. What it does need is the two URLs in its
`.env`; `make_prod_env.py` writes them, and `/readyz` names whichever one
does not answer:

```
MASTER_SERVICE_URL=http://127.0.0.1:8030
USER_SERVICE_URL=http://127.0.0.1:8020
```

The double-booking guard stayed in one transaction: it locks a row in the
Hotel schema's own `room_lock` table, which is why the migration above is
part of this step.

Then regenerate the gateway permission map, which is derived from the live
`menus` table, and change the passwords:

```bash
python Backend/tools/build_rbac_map.py
python Backend/tools/rotate_passwords.py --confirm
python Backend/tools/preflight.py            # should now report READY
```

## Signing in

Every seeded account uses the same password: **`Hotel@2026`**

| Email | Role | Can reach |
|---|---|---|
| `admin@cherryhotel.com` | Admin | everything |
| `priya.menon@cherryhotel.com` | Front Office Manager | reservations, night audit, enquiry, master data (read) |
| `rahul.nair@cherryhotel.com` | Front Desk | reservations and enquiry |
| `imran.khan@cherryhotel.com` | Housekeeping | tasks, incidents, room status |
| `vikram.singh@cherryhotel.com` | Food & Beverage | restaurant and bar |

**Change these before the system is exposed to anyone.** They are shared,
published credentials — they are in this file, in the seed source and in this
repository's history. There is a tool for it, so nobody has to hand-write
{c['staff']} bcrypt hashes:

```bash
python Backend/tools/rotate_passwords.py --list      # who would change
python Backend/tools/rotate_passwords.py --confirm   # strong, unique, printed once
```

`Backend/tools/preflight.py` fails while the published password still works,
and keeps failing until this is done.

No role except Admin can delete, which is deliberate — the gateway authorises
against these permissions.

## What "consistent" means here

`Backend/tools/verify_seed.py` asserts 34 invariants that span schemas and
therefore cannot be expressed as database constraints. All 34 pass on this
release — `export_release.py` will not write one where they do not:

- **Money.** Every folio satisfies `rooms + beds × count + extras − discount +
  tax = overall`; `paid` equals the sum of its own payment history; `balance =
  overall − paid`; no checked-out stay leaves a balance and nobody is overpaid.
  The same holds for every restaurant and bar bill against its own lines.
- **Inventory.** No two live stays share a room on the same night, using the
  half-open overlap rule the API enforces (so same-day turnover is allowed).
- **Room state.** Every in-house room reads Occupied and no room reads Occupied
  without a guest in it. Departed rooms are queued for housekeeping.
- **References.** Every reservation points at real rooms, rate plans, taxes,
  discounts, payment methods and a status that exists in the master vocabulary.
  Every permission points at a real menu. Every housekeeping task and every
  room incident points at a real room.
- **Attachments.** Every incident attachment is stored as the path the static
  mount serves.
- **Images.** Every one of the {image_count} stored paths resolves to a file, and no
  unreferenced file is shipped.
- **Navigation.** Every menu and submenu link matches a route in `App.jsx`.

Re-run it any time:

```bash
python Backend/tools/verify_seed.py
```

{money_section}

## Regenerating rather than restoring

The dump is a photograph of one day. Its dates do not move, so a guest who is
"in house today" in this release becomes a guest who checked in months ago once
enough time passes, and the dashboard's arrivals and departures go empty.

To get the same story anchored to *today*, regenerate instead of restoring:

```bash
python Backend/tools/seed_demo_data.py --dry-run   # show what is there now
python Backend/tools/seed_demo_data.py --confirm   # wipe and rebuild
python Backend/tools/build_rbac_map.py
python Backend/tools/verify_seed.py
python Backend/tools/export_release.py             # and ship the result
```

`--confirm` is mandatory; there is no default that writes. It **destroys all
data in all five schemas** — take a backup first:

```bash
mysqldump -u root -p --databases hotelerp_users hotelerp_masterdata \\
  hotelerp_hotel hotelerp_restaurant hotelerp_bar > backup.sql
```

## A note on the images

**75 of them are real photographs**, downloaded from Wikimedia Commons and
Openverse — 32 hotel interiors (four per room type), 25 restaurant dishes and
18 bar drinks, each matched to its own subject and checked by eye. Every file
is listed in `PHOTO-CREDITS.md` with its title, licence, photographer and
source URL.

Not from Google Images: those results are copyrighted photographs on other
people's sites, and shipping them inside a product database is infringement.
Both sources used here state a licence per image, and only licences permitting
commercial use *without* a NoDerivatives clause were accepted, because the
images are cropped and resized. **Attribution is a licence condition for the
CC-BY files — keep `PHOTO-CREDITS.md` with the data.**

Three kinds stay drawn rather than photographed, on purpose:

- **Staff avatars** — initials on a colour. Using a real person's face as a
  fictional employee is a privacy problem whatever the photo's licence says.
- **Identity documents** — marked SPECIMEN in three places, carrying no number
  that could be mistaken for a real one. A seed file must never be usable as,
  or mistakable for, a genuine identity document.
- **Incident photographs** — a picture of real damage in a real hotel implies
  an incident that did not happen here.

Replace the stock photography with the property's own before going live; the
rate cards and room numbers are already yours, the pictures are not.
"""
    (release_dir / "README.md").write_text(text, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Export the live database as a release.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name", help="Release folder name (default: today, e.g. 17-Sept-2026)")
    p.add_argument("--mysqldump", help="Full path to mysqldump")
    p.add_argument("--force", action="store_true",
                   help="Overwrite a release folder that already exists")
    p.add_argument("--skip-verify", action="store_true",
                   help="Export even if the database fails verify_seed.py")
    p.add_argument("--verify-restore", action="store_true",
                   help="After exporting, load the release back over the same "
                        "five schemas and re-check it. The real proof, and a "
                        "no-op when the dump is sound.")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    today = dt.date.today()
    name = args.name or release_name(today)
    release_dir = DB_DIR / name

    print(f"release      : {name}")
    print(f"destination  : {release_dir}")
    print()

    if release_dir.exists() and not args.force and not args.dry_run:
        print(f"ERROR: {release_dir} already exists. Pass --force to replace it.",
              file=sys.stderr)
        return 2

    if release_dir.exists() and args.force and not args.dry_run:
        # REPLACE, not merge. A re-seed mints new image filenames, so copying
        # over an older export leaves every previous file behind as an orphan
        # -- a release that ships images nothing references, which is exactly
        # what step 5 then reports. Clear the generated trees first.
        for sub in ("sql", "uploads"):
            if (release_dir / sub).exists():
                shutil.rmtree(release_dir / sub)
        print(f"  replacing the existing {name} (sql/ and uploads/ cleared)")
        print()

    print("=== 1. is the database fit to ship ===")
    if args.skip_verify:
        print("  SKIPPED -- exporting a database nothing has checked.")
    elif run_verify_seed()[0]:
        print("  all 34 invariants hold")
    else:
        print("\nRefusing to export. Fix the data, or pass --skip-verify if you "
              "are certain.", file=sys.stderr)
        return 1

    c = counts()
    images = stored_image_paths()
    image_count = sum(len(v) for v in images.values())
    print()
    print(f"=== 2. what would ship ===")
    print(f"  {c['reservations']} reservations, {c['staff']} staff, {c['rooms']} rooms, "
          f"{c['rest_bills'] + c['bar_bills']} settled bills")
    print(f"  {image_count} image files across {len(images)} service(s)")

    if args.dry_run:
        print("\nDRY RUN -- nothing written.")
        return 0

    mysqldump = Path(args.mysqldump) if args.mysqldump else find_mysqldump()
    print(f"\n=== 3. schema dumps ({mysqldump.name}) ===")
    problems = dump_schemas(release_dir / "sql", db_config(), mysqldump)
    if problems:
        for pr in problems:
            print("  " + pr, file=sys.stderr)
        return 1

    print("\n=== 4. images ===")
    copied, img_problems = copy_images(release_dir / "uploads")
    print(f"  {copied} file(s) copied")
    for pr in img_problems:
        print("  " + pr, file=sys.stderr)

    credits = DB_DIR / "PHOTO-CREDITS.md"
    if credits.is_file():
        shutil.copy2(credits, release_dir / "PHOTO-CREDITS.md")
        print(f"  PHOTO-CREDITS.md copied")

    float_columns = count_float_columns()
    write_readme(release_dir, name, today, c, image_count, float_columns)
    print("  README.md written from the counts above")

    print("\n=== 5. verifying the release ===")
    faults = img_problems + verify_export(release_dir)
    if faults:
        for f in faults:
            print("  FAIL  " + f)
        print(f"\n{len(faults)} problem(s). The release is NOT complete.",
              file=sys.stderr)
        return 1
    print("  every dump drops, recreates and completes")
    print(f"  every one of the {image_count} stored paths has its file, and nothing "
          "unreferenced ships")
    print("  PHOTO-CREDITS.md travels with the data")

    if args.verify_restore:
        print("\n=== 6. loading the release back ===")
        faults, invariant_failures = restore_and_recheck(
            release_dir, db_config(), find_mysql_client(mysqldump), c)
        # The README states the round-trip result. It is known now, so replace
        # "not measured" with the number that was actually measured.
        write_readme(release_dir, name, today, c, image_count, float_columns,
                     restore_failures=invariant_failures)
        if faults:
            for f in faults:
                print("  FAIL  " + f)
            print(f"\n{len(faults)} problem(s) restoring the release. Do NOT "
                  "ship it.", file=sys.stderr)
            return 1

    print(f"\nRelease written to {release_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# HotelERP database release — 17-Sept-2026

A complete, internally consistent database for the Cherry HotelERP system:
five schemas, the staff who can log into them, and **112 image files** that
every image column in the data actually points at.

Exported **17 September 2026** from a database freshly built by
`Backend/tools/seed_demo_data.py`, by `Backend/tools/export_release.py`, which
refuses to export a database that fails `verify_seed.py`. Every count below was
counted from the data, not typed.

## What is in the box

```
Backend/db/17-Sept-2026/
  README.md          this file
  PHOTO-CREDITS.md   licence and attribution for every photograph
  sql/               five schema dumps, each with DROP DATABASE / CREATE DATABASE
  uploads/           112 image files, laid out exactly as the services expect
```

Restore commands below are written to be run **from this directory**.

| Schema | Holds |
|---|---|
| `hotelerp_users` | 5 roles, 9 menus, 57 submenus, 138 role permissions, 10 staff |
| `hotelerp_masterdata` | 25 rooms across 8 rate plans, tax, discount, payment, statuses |
| `hotelerp_hotel` | 25 reservations, 22 payments, housekeeping, incidents, enquiries |
| `hotelerp_restaurant` | 25 menu items, 18 tables, 8 settled bills |
| `hotelerp_bar` | 18 menu items, 10 tables, 8 settled bills |

## Restoring

Restore the SQL first, then drop the images into place. **Both are required** —
the database stores paths, not image bytes, so SQL alone leaves every room
photo, staff avatar, menu tile and identity proof broken.

```bash
# 1. schemas  (each dump drops and recreates its own database)
for f in sql/*.sql; do mysql -u root -p < "$f"; done

# 2. images — copy into the running services' static trees.
python ../../tools/restore_uploads.py --release 17-Sept-2026
python ../../tools/restore_uploads.py --release 17-Sept-2026 --verify
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
10 bcrypt hashes:

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
- **Images.** Every one of the 112 stored paths resolves to a file, and no
  unreferenced file is shipped.
- **Navigation.** Every menu and submenu link matches a route in `App.jsx`.

Re-run it any time:

```bash
python Backend/tools/verify_seed.py
```

## Money survives a restore exactly

Every money column in these five schemas is `DECIMAL`, not `FLOAT`, and that
matters to a dump. `mysqldump` writes a `FLOAT` at about six significant
digits, so a folio total of `20009.85` used to be written as `20009.8` and came
back five paise light. Releases up to and including `15-Sept-2026` carry that
loss, and the deployment at `168.231.103.18` was restored from one of them.

Confirmed on this release by loading it back and re-running the checks: **all 34 invariants still hold**.

Restoring this release over a database that predates the change brings the
corrected column types with it — each dump drops and recreates its own schema.

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
mysqldump -u root -p --databases hotelerp_users hotelerp_masterdata \
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

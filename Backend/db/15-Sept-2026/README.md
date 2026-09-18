# HotelERP database release

A complete, internally consistent database for the Cherry HotelERP system:
five schemas, the staff who can log into them, and **112 image files** that
every image column in the data actually points at.

Exported **15 September 2026** from a database freshly built by
`Backend/tools/seed_demo_data.py`.

## What is in the box

```
Backend/db/15-Sept-2026/
  README.md  this file
  sql/       five schema dumps, each with DROP DATABASE / CREATE DATABASE
  uploads/   112 image files, laid out exactly as the services expect
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
python ../../tools/restore_uploads.py --release 15-Sept-2026
python ../../tools/restore_uploads.py --release 15-Sept-2026 --verify
```

**Step 2 is the one that gets skipped.** It used to be five hand-typed `cp -r`
lines, and on the deployment at `168.231.103.18` they were not run: the SQL
loaded, every endpoint answered `200`, and all 88 image paths the API served
resolved to nothing. Nothing detected it, because the rows were all present —
the only symptom was that no picture in the application loaded.

Restore the SQL and the images **from the same release**. A re-seed mints new
filenames, so a release's `uploads/` only matches the database that shipped
beside it; mixing two releases leaves every path pointing at a file that was
never there.

**Then step 3: bring the Hotel schema up to this build, and point the Hotel
service at the gateway.**

```bash
python Backend/migrations/migrate.py upgrade hotel   # adds room_lock (see below)
python Backend/tools/build_rbac_map.py               # the gateway's map gains the service routes
sudo systemctl restart <the gateway unit> <the masterdata unit> <the hotel unit>
curl -s localhost:8040/readyz                        # "status": "ready"
```

The Hotel service does **not** read any other service's database. Rooms, rate
cards, tax, discounts, payment methods, identity proofs and the status
vocabulary come from MasterDataServices (`GET /masterdata/snapshot`, once per
request), a housekeeping assignee is checked against UserServices, and the
room's occupancy and housekeeping flags are written back through
`PUT /masterdata/room/{id}/state`. **Every one of those calls goes through
the login gateway** -- the same address the frontend uses -- on the caller's
own token, so the gateway's authentication and permission map apply to them
exactly as to the browser's calls. Its MySQL account needs privileges on
`hotelerp_hotel` and nothing else; there is no cross-schema GRANT to run.

It finds the gateway on its own: the gateway writes its address into every
token it signs (the `gw` claim), and the Hotel service calls back through
that. So on a one-host deployment nothing has to be configured -- users just
sign in again after the deploy so their token carries the claim. When the
gateway is on another host, set the address explicitly and it wins:

```
API_GATEWAY_URL=http://gateway.internal:8000     # Hotel .env, optional
GATEWAY_SELF_URL=http://gateway.internal:8000    # gateway .env, optional
```

`/readyz` on the Hotel service reports which address it is using and where
that came from.

The gateway's permission map must carry the three service-to-service routes
(`masterdata/snapshot`, `masterdata/room/{id}/state`, `user/users/{id}`), which
`build_rbac_map.py` derives from the Hotel rows -- run it on the gateway's build
and restart the gateway, or under `RBAC_GATEWAY_MODE=enforce` every reservation
screen answers 503 naming the missing row.

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
repository's history. There is a tool for it, so nobody has to hand-write ten
bcrypt hashes:

```bash
python Backend/tools/rotate_passwords.py --list      # who would change
python Backend/tools/rotate_passwords.py --confirm   # strong, unique, printed once
```

`Backend/tools/preflight.py` fails while the published password still works, and
keeps failing until this is done.

No role except Admin can delete, which is deliberate — the gateway authorises
against these permissions.

## What "consistent" means here

`Backend/tools/verify_seed.py` asserts 34 invariants that span schemas and
therefore cannot be expressed as database constraints. All 29 pass on this
release:

- **Money.** Every folio satisfies `rooms + beds + extras − discount + tax =
  overall`; `paid` equals the sum of its own payment history; `balance =
  overall − paid`; no checked-out stay leaves a balance and nobody is overpaid.
  The same holds for every restaurant and bar bill against its own lines.
- **Inventory.** No two live stays share a room on the same night, using the
  half-open overlap rule the API enforces (so same-day turnover is allowed).
- **Room state.** Every in-house room reads Occupied and no room reads Occupied
  without a guest in it. Departed rooms are queued for housekeeping.
- **References.** Every reservation points at real rooms, rate plans, taxes,
  discounts, payment methods and a status that exists in the master vocabulary.
  Every permission points at a real menu. Every housekeeping task and every room
  incident points at a real room, and uses the task/room-status vocabulary the
  application actually accepts — the previous release wrote room *numbers* into
  columns the application reads as room *ids*, so the Room column was blank on
  every one of those rows, and wrote task statuses the Task Assign filter could
  not match.
- **Attachments.** Every incident attachment is stored as the path the static
  mount serves. The previous release stored a bare filename, so not one incident
  photograph could be opened.
- **Images.** Every one of the 112 stored paths resolves to a file, and no
  unreferenced file is shipped.
- **Navigation.** Every menu and submenu link matches a route in `App.jsx`.

Re-run it any time:

```bash
python Backend/tools/verify_seed.py
```

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

# Production readiness

Where this system actually stands, and what is left. Rewritten 16 September
2026; the previous version described the August `production-audit` branch and
had gone stale on every major point — it called gateway RBAC "the largest open
item" (it shipped), counted 23 backend tests (there are 321) and said there was
no CI (`.github/workflows/ci.yml`).

## What holds today

**Authorization.** The gateway authorises every request to the five
operational services against a generated route→page→action map
(`LoginServices/resources/rbac_map.py`, built by `Backend/tools/build_rbac_map.py`
from the live `menus` table). `RBAC_GATEWAY_MODE=enforce` denies with 403;
`audit` logs what it would deny, which is the rollout setting, not the
production one. This was the August audit's largest open item and the reason it
could not be closed then — the permission model is keyed by page link and the
services expose endpoint names — so the map is the mapping that was missing.

**Authentication.** Every service verifies the JWT itself. The gateway is
perimeter enforcement, not defence in depth: the five services bind to
127.0.0.1 so the perimeter is the only way in, and they keep their own auth for
when it is not.

**Tests.** 359 across 16 suites (`python Backend/tests/run_all.py`), one
subprocess per service because six services each define a top-level `configs`
package and a single pytest process would let the first one imported win.
Frontend: 100 tests over 8 files, lint at 12 warnings, build clean. CI runs all
of it plus `check_pins.py`, which fails if an install resolves anything other
than the pinned versions.

**Data.** `Backend/tools/verify_seed.py` asserts 34 invariants that span
schemas and so cannot be database constraints — money that reconciles, rooms
never double-booked, room state matching the bookings, every stored image path
resolving to a real file, every menu link matching a route in `App.jsx`.

**End-to-end.** Two suites against the running system, which catch what
in-process tests cannot: `Backend/tests/e2e/` over HTTP through the real
gateway and MySQL, and `Frontend/e2e/` in a real browser.

**Money.** Every money column in the five schemas is `DECIMAL`, not `FLOAT`
(147 of them, migrated 17 September 2026). It was single-precision float, which
cannot represent `20009.85` and which `mysqldump` writes at six significant
digits — so every release dump shipped money a few paise light and two of the
34 invariants failed on any restore. The models declare
`Numeric(asdecimal=False)`: the column is exact, while SQLAlchemy still hands
Python a float, so no arithmetic site had to change.

**Releases.** `Backend/tools/export_release.py` cuts a dated release —
five schema dumps, the images the data points at, and a README whose every
count is counted rather than typed. It refuses to export a database that fails
`verify_seed.py`, and `--verify-restore` loads the release back and re-runs the
checks. The current release is `Backend/db/17-Sept-2026/`.

**Deployment checks.** `Backend/tools/preflight.py` asks a *running*
deployment the six questions that no unit test can: is the gateway up, are the
services' own dependencies reachable, does RBAC actually refuse something, are
the internal ports exposed, does the seeded password still work, and do the
images the database points at actually serve.

## What is left

### 1. The live deployment is behind the repo — the largest open item

`168.231.103.18` runs a pre-hardening build. Verified 16 September 2026 by
sweeping all 153 live GET endpoints. Nothing here is a code defect: local
passes every suite and all 34 invariants.

| | Symptom | Fix, on the server |
|---|---|---|
| 1 | `/room_reservation` and `/room_reservation/{id}` answer 500 | Deploy the 18 Sept build: the Hotel service now reads Master Data and Users through the gateway and never touches their schemas, so no GRANT is needed. Run `python Backend/migrations/migrate.py upgrade hotel` (adds `room_lock`), set `API_GATEWAY_URL` in the Hotel `.env`, regenerate the gateway's map (`build_rbac_map.py`), restart both; `/readyz` names the address if it cannot reach the gateway |
| 2 | every stored image 404s — all 88 paths | `python Backend/tools/restore_uploads.py --release 15-Sept-2026` |
| 3 | RBAC in audit: every role reaches every endpoint | `RBAC_GATEWAY_MODE=enforce` |
| 4 | all five internal services reachable from the internet | bind `SERVICE_HOST=127.0.0.1`, or firewall |
| 5 | seeded password `Hotel@2026` still signs in as admin | `python Backend/tools/rotate_passwords.py --confirm` |
| 6 | `/readyz` 404s, `/healthz` returns the old flat body | deploy current `main` and restart |

**Row 1 has two traps, and the log only shows one of them.** The error reads
`SELECT command denied to user 'cherryhotel'@'localhost' for table 'room'`.

- *The account.* `'cherryhotel'@'%'` is a **different account** from
  `'cherryhotel'@'localhost'`. Granting to the first creates a second, empty
  account, answers `Query OK`, and leaves every 500 exactly where it was.
  The grant has to name what `SELECT CURRENT_USER()` returns on the service's
  own connection, which is what the tool reads rather than guesses.
- *The privilege.* SELECT is the only thing the error names, so SELECT is what
  gets granted — and then the reservation list works while no **booking**
  does. The reservation lifecycle writes `room.Room_Booking_status` back and
  `lock_rooms()` takes `SELECT … FOR UPDATE`, which MySQL refuses without
  UPDATE on top of SELECT. `hotelerp_users.users` is a third grant again:
  without it, assigning a housekeeping task 500s.

Restart the Hotel service after granting. MySQL applies a database-level
privilege change at a connection's next `USE`, and the service holds a
SQLAlchemy pool opened before the grant — so a fresh `mysql` client proves the
fix while the running process keeps failing.

A `git pull` alone does **not** fix the images. The live database references
the `15-Sept-2026` release filenames; a re-seed mints new UUIDs, so the two
sets have the same count and zero overlap. Restore SQL and images from the
**same** release — either put `15-Sept-2026`'s images back beside the data
already there, or restore `17-Sept-2026` whole, both halves together.
`preflight.py` is the check for all six:

```bash
python Backend/tools/preflight.py --host 168.231.103.18 --gateway 9010 \
  --services hotel=9005,user=9020,masterdata=9015,bar=9025,restaurant=9030
```

### 2. `react-hooks/set-state-in-effect` — 10 occurrences

React 19's compiler flags synchronous `setState` in an effect body; each costs
an extra render pass. Most are prop-to-state mirroring that should be derived
during render or keyed instead. Down from 75. The rest need per-case judgement:
several are load-then-populate flows where a blind rewrite changes behaviour,
so a codemod is the wrong tool. Two other warnings remain — one
`exhaustive-deps`, one `react-refresh/only-export-components`.

### 3. Defence in depth

Authorization is enforced once, at the gateway. Anything that reaches a service
on loopback still bypasses it. Pushing the same check into each service is a
later step, not a substitute — and it only matters once item 1.4 is closed,
since today the services are reachable directly from the internet anyway.

### 4. Smaller items

- `/authentication/otp` is intentionally unrouted: the page calls `/verify_otp`
  and `/resend_otp`, which no service implements. `App.jsx` says so beside the
  auth routes. Restore the route when the endpoints exist.
- The seeded dataset is a photograph of one day. Its dates do not move, so
  re-seed rather than restore when the dashboard's arrivals should be today's —
  see `Backend/db/17-Sept-2026/README.md`, the current release.
- Replace the stock room and menu photography with the property's own before
  go-live. The rate cards and room numbers are already yours; the pictures are
  not, and `PHOTO-CREDITS.md` has to travel with them while they are.

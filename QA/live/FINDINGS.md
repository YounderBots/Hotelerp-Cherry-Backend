# HotelERP — LIVE Staging QA Findings

**Target:** http://168.231.103.18:5700/ (SPA) · http://168.231.103.18:9010/ (gateway)
**Date:** 2026-10-16
**Accounts:** the five supplied demo accounts
**Repo HEAD:** `5aa3755`

Status key — PASS · FAIL · BLOCKED · NOT TESTED · FIXED & RETESTED

---

## Executive summary

Two defects make the system unsafe to put in front of a real property, and both
sit in the same place: **the gateway's only authorisation layer is switched off,
and the five backend services are reachable from the internet.**

Measured, not inferred:

| Measure | Value |
|---|---|
| Services answering on the public IP | 6 of 6 (gateway + all five backends) |
| Write route+method pairs with a permission check | 23 of 202 — all inside `UserServices` |
| Write route+method pairs reachable with no check | 179 |
| Non-Admin roles that received `200` on the full GET surface | 4 of 4 |
| Session token honoured past its `exp` | yes — 760 minutes past |
| Committed regression tests for token expiry | 10/10 pass locally |
| Backend suites after this session's fixes | 32/32, 1,250 assertions |

---

## QA-SEC-001 — Gateway RBAC runs in `audit`: every role can read and write everything

**Severity: Critical** · Status: **FIXED (gateway `enforce`) + defence in depth added (service side, `audit`)** · Role: any authenticated user

### The two halves, and where each stands

| Layer | Control | Status |
|---|---|---|
| 1. Gateway | `RBAC_GATEWAY_MODE` default `audit` → `enforce` | **fixed in source**, needs deploy |
| 2. Network | services bound to `127.0.0.1`, not publicly reachable | **fixed in source** (QA-SEC-002), needs deploy |
| 3. Service | each service applies the same map itself | **added, ships in `audit`**, flip one variable |

Layer 1 is the real control. Layers 2 and 3 exist because layer 1's model has a
premise — *the services are unreachable except through the gateway* — and that
premise was false on the deployment this was found on. A check at the far end
does not depend on the premise.

### Layer 3, in detail

Each of the five services now carries `resources/route_policy.py`: its **own
slice** of the gateway's map plus a copy of the same decision function, written
by the **same generator run** as the gateway's `rbac_map.py`. The gateway sees
`/hotel/room_reservation/7`; the service sees `/room_reservation/7`; both resolve
to the same row and the same `perm` claim.

That is the whole safety argument, so it is tested rather than asserted.
`Backend/tests/test_route_policy.py` checks, exhaustively:

- the five slices cover all **279** gateway routes, and no route is in two slices;
- the pages behind each row match row-for-row (a slice that kept a key but lost
  a page would refuse one role on one endpoint, and a key-set test would miss it);
- `PAGE_PARENTS`, `METHOD_ACTION`, `ACTION_OVERRIDES`, `ALWAYS_ALLOW` and the bit
  layout all agree — the bits travel *inside a signed token*, so they are a wire
  format and neither side may change one alone;
- for every route × four claims (no permissions, all permissions, view-only,
  permissions on an unrelated page) under **both** modes, the two layers reach the
  same verdict;
- an owner holding every permission on every named page is refused nothing under
  `enforce` — the over-tight-map failure the gateway's own dry run found once;
- every one of the 67 uncalled endpoints is absent from its slice, so a service
  that were exposed would still not hand back what the gateway protects;
- `{id}` matches exactly one segment, so a permission on a shallow route cannot
  authorise a deeper path;
- `ROUTE_POLICY_MODE` defaults to `audit`, and a misspelt value falls **forward**
  to `enforce`.

**18/18 pass.**

`ROUTE_POLICY_MODE=enforce python Backend/tests/run_all.py` → **all 37 suites,
1,268 assertions, pass**. The default (`audit`) run passes identically, which is
the point: deploying changes no behaviour.

### Why it ships in `audit` and not `enforce`

This is the third authorisation control to change at once — the gateway default
and the bind guard alongside it. Enabling a *new* enforcement layer in the same
deploy that flips two other security behaviours is how an app goes down on deploy
day, and "the tests passed" does not cover a role nobody tested with.

So: deploy in `audit`, read the log, then flip one variable.

```bash
grep rbac_would_deny .run-logs/*.log | head -50   # nothing? then enforce is safe
```

That log is also the answer to "is the map right for *our* data", which no
offline test can settle — permissions live in a tenant's database.

### What the audit log is for, beyond the flip

An `rbac_would_deny` line is a real request a real role was refused. If any of
them is a legitimate call, the **map is wrong**, not the caller — the gateway
would refuse it too, it just was not visible until a service was exposed.

### Reproduction (unchanged — the gateway half, still live until deploy)

```
1. Sign in as Housekeeping (imran.khan@cherryhotel.com -- password from QA_PASSWORD)
2. GET http://168.231.103.18:9010/restaurant/bill        -> 200, 12 rows
3. GET http://168.231.103.18:9010/bar/bill               -> 200, 12 rows
4. GET http://168.231.103.18:9010/hotel/user_activity_log -> 200
5. GET http://168.231.103.18:9010/masterdata/room        -> 200, 25 rows
6. DELETE http://168.231.103.18:9010/masterdata/tax/6    -> 200 "Tax deleted successfully"
```

Step 6 is destructive and is listed as the proof, not as something to run. Use
`privesc_matrix.py`, which probes record id `999999999` and cannot delete
anything, to see the same finding safely.

Housekeeping's JWT carries 8 permitted pages and none of them is `/tax_types`,
`/bar_billing_payments`, `/rooms` or `/restaurant_billing_payments`. The
identical requests from Admin return the same 200s — the responses are
indistinguishable.

### Measured evidence

`QA/live/privesc_matrix.py` — 159 write routes × 5 roles = 1010 probes, all
against record id `999999999` so nothing could be mutated:

| Role | perm pages | REFUSED (403) | Passed the authz layer |
|---|---|---|---|
| Admin | 60 | 0 | 201 |
| Front Office Manager | 26 | 23 | 178 |
| Front Desk | 7 | 23 | 178 |
| Housekeeping | 8 | 23 | 178 |
| Food & Beverage | 25 | 23 | 178 |

All four non-Admin roles produce **identical** counts. Across the whole write
surface — 202 route+method pairs on 159 paths — 179 are never refused by
anyone, and all 23 that are refused are in the `user` prefix, from
`UserServices/resources/authorization.py`. `HotelServices`,
`MasterDataServices`, `RestaurantServices` and `BarServices` contain **zero**
calls to `require_permission` / `require_any_permission`.

`QA/live/sweep_api.py` — 144 GET routes × 5 roles × 2 surfaces = 1728 calls.
Front Desk, whose claim lists 7 pages, received `200` with data from 53 of 144
endpoints, including `/restaurant/bill`, `/bar/menu`, `/hotel/room_reservation`,
`/hotel/night_audit/preview` and `/masterdata/tax`.

### Root cause — established

Two independent causes, both in this repository:

1. **`Backend/Services/LoginServices/resources/rbac.py:52`**
   ```python
   MODE = os.getenv("RBAC_GATEWAY_MODE", "audit").strip().lower()
   ```
   `audit` logs what it would deny and allows it. With the variable unset, the
   279-row permission map is never applied. The sibling module
   `UserServices/resources/authorization.py:47` deliberately defaults the other
   way — *"an operator has to opt **out** deliberately, rather than a missing
   variable silently disabling every check."*

2. **`.env.example:67`** ships `RBAC_GATEWAY_MODE=audit`, so a deployment
   provisioned from the template inherits the fail-open mode.

`verify_prod_env.py:127` already checks for this and even names this host in its
comment — the diagnosis existed, the code default was never changed.

### Why the map is safe to enforce now

The module docstring refuses to default to `enforce` until the map has been
read against real traffic. That read has now been done
(`QA/live/rbac_dryrun.py`, reproducible offline against live captures):

| Check | Result |
|---|---|
| Route rows derived | 279 |
| Rows nothing can grant | **0** |
| Detail routes with no parent page | **0** |
| Unreachable routed screens | **0** |
| Calls enforce would refuse that Admin's live calls did not | mapped routes only |
| Unmapped routes that would fail closed | 67 — **all of them endpoints the SPA never issues** |

The 67 are exactly `UNCALLED_ENDPOINTS` in the generated `rbac_map.py`. Grep of
`Frontend/src` finds no caller for any of them: `export_*`, `room_sales`,
`night_audit_process`, `keeper_info`, `waitlist`, `table/merge`,
`POST /bar/menu_category`, `POST /bar/payment_method`, `GET|POST /bar/settings`.
The menu and station pages read those with `GET` and create through
`/masterdata/*` instead. Enforcement therefore removes dead API surface without
removing anything the UI reaches.

### Remediation

Source change made in this session: `MODE` now defaults to `enforce`, and
`.env.example` ships `enforce`. Both keep `off` and `audit` as explicit,
deliberate opt-outs. `verify_prod_env.py` already rejects a missing variable.

---

## QA-SEC-002 — All five backend services are reachable from the internet

**Severity: Critical** · Status: FAIL (configuration) · Role: unauthenticated

### Reproduction

```
http://168.231.103.18:9005/openapi.json  -> 200  HotelERP - Hotel Service
http://168.231.103.18:9015/openapi.json  -> 200  HotelERP - Master Data Service
http://168.231.103.18:9020/openapi.json  -> 200  HotelERP - User Service
http://168.231.103.18:9025/openapi.json  -> 200  HotelERP - Bar Service
http://168.231.103.18:9030/openapi.json  -> 200  HotelERP - Restaurant Service
```

### Why it matters

`rbac.py` lines 3–13 state the design premise:

> *"the services themselves bind to 127.0.0.1 and are not routable from
> outside. Enforcing once at the proxy therefore covers the whole external
> surface."*

On this host that premise is false, so the gateway is not the only way in — the
permission map can be stepped around entirely by addressing a service port
directly. The `.env` files in the repo do set `SERVICE_HOST=127.0.0.1`; the
running processes do not honour it.

### Containment that does hold

Unauthenticated access is still refused — every one of the 143 data routes
answers **401** without a token, and a malformed token answers 401
`Invalid or expired token`. Each service authenticates the JWT itself. So this
is an exposure of surface, not an open door; it becomes a full bypass the moment
QA-SEC-001 is closed only at the gateway and the ports stay open.

### Remediation

Both parts are now in the source tree.

**1. Bind the services to loopback.** `start-network.ps1` / `run.sh` already did
this, so the gap was only for services started some *other* way. Each service's
`main.py` now carries an import-time guard that refuses a non-loopback
`SERVICE_HOST` — including under `ASCEND_ENV=dev`, which is how the deployment in
question was running, so a production-only check would have sailed past it.
`ALLOW_PUBLIC_BIND=true` is the deliberate opt-out.

`Backend/tests/test_bind_guard.py`: 5 services × 7 cases, plus the check that the
refusal actually names the gateway and the override, plus the check that the
gateway itself is still allowed to bind publicly. **41/41** — counted from the
script's own `[PASS]` lines (5 services × 7 bind cases + 5 message checks + the
gateway exception), not estimated.

**2. Service-side authorisation.** See QA-SEC-001 below — the second, independent
layer now exists in all five services.

---

## QA-SEC-003 — JWT expiry is not enforced on LIVE — **CLOSED, fixed by a deployment**

**Severity: Critical** · Status: **CLOSED (2026-10-17)** · Role: anyone holding an old token

### The original report

On 2026-10-16 an access token from the browser's `localStorage` was presented to
every service. Its `exp` was 760 minutes past, and every one answered **200 with
data** while a malformed token answered 401 — so the signature was verified and
the expiry was not. The committed code *does* enforce it
(`test_jwt_auth.py`, 10/10 pass locally), so the deployed build was judged to
differ from the repository.

### What it actually was, in part

The magnitude was misleading, and the reason is **QA-SEC-009**: the deployment's
clock is **13.4 hours behind** (see below). A token's `exp` is computed with the
server's clock and verified with the server's clock, so comparing it to the
reviewer's clock conflated two different things. The first pass of this audit
did exactly that and drew a conclusion from the combined reading.

### Re-tested on 2026-10-17, with controls

`QA/live/expiry_recheck.py` — the **same token**, the same six endpoints, plus
two controls so a 401 cannot be mistaken for "the endpoint is down" or "it
refuses everything":

| Surface | expired token | fresh token | mangled signature |
|---|---|---|---|
| `gateway :9010/masterdata/room` | **401** | 200 | 401 |
| `user :9020/roles` | **401** | 200 | 401 |
| `masterdata :9015/room` | **401** | 200 | 401 |
| `hotel :9005/room_reservation` | **401** | 200 | 401 |
| `restaurant :9030/menu` | **401** | 200 | 401 |
| `bar :9025/menu` | **401** | 200 | 401 |

The expired token was 1458 minutes (24.3 h) past `exp` **by the deployment's own
clock**, so this is not a clock artefact: the deployment now refuses it.

**Verdict: expiry is enforced on every surface.** The finding was real on the
16th and is closed on the 17th — the deployment now runs code that verifies
`exp`, which is what the repository has always said it did.

No source change was made for this, and none was needed. What was added instead
is the check that would have caught it as a regression:
`Backend/tools/preflight.py` checks **3b** (does a session have a bounded
lifetime, and does the advertised TTL match the token handed over) and **3c**
(paste a lapsed token, prove it is refused).

---

## QA-SEC-009 — The deployment's clock is 13.4 hours behind

**Severity: Critical** · Status: FAIL · Found by this audit, 2026-10-17 · Configuration

### Measurement

`QA/live/clock_and_expiry.py`, using the server's own `Date` header as its
statement about the time:

```
my clock            1792202577   (2026-10-17 02:02:57 UTC)
deployment's clock  1792154368   (2026-10-16 12:39:28 UTC)
skew                 48209s  (+13.39 h)
```

Confirmed against all six services and both `/healthz` and `/readyz`.

### Why this is worse than being untidy

Every timestamp the system records is stamped from that clock:

- **JWT `iat` / `exp`.** Issued and verified consistently — the six services
  share the host — so sessions work for the browser. But a token minted here
  looks 13 hours *already expired* to any client whose clock is right, and a
  token minted on a correct clock looks valid here for 13 hours longer than it
  should. Anything that federates, or that compares tokens across hosts, breaks.
- **Night Audit `business_date`.** Derived from the server's "today", so a run
  closes the wrong business day. The seeded audit rows are dated 10 Oct while
  the server believes it is the 16th, which is 6 days of drift in the data
  against 13.4 hours of clock drift — so the dataset was seeded earlier, but the
  clock is independently wrong.
- **Reservation arrival comparisons.** `reservation_cancel`'s sibling,
  `reservation_no_show`, refuses a no-show while `arrival_date > date.today()`.
  With the clock a day behind at the boundary, a guest who has arrived can be
  refused.
- **Payment and folio timestamps**, `cancelled_at`, `created_at` — all wrong by
  the same offset, which makes a day's settlement disagree with the calendar.

### Remediation

NTP (`chronyd`, `systemd-timesyncd`, or the hypervisor's time sync) on the
deployment host, then confirm:

```bash
python Backend/tools/preflight.py --host 168.231.103.18 --gateway 9010
```

Check 3b now fails with *"the token just handed out is ALREADY past its exp"*
whenever the clocks disagree — which is how this was found. After the fix it
should report a positive lifetime.

**Not fixed in source**, because it is a property of the host, not of the code.
What *is* in source is the check that finds it, so the next deployment cannot
regress it unnoticed.

**Severity: Critical** · Status: FAIL (deployment drift) · Role: anyone holding an old token

### Reproduction

An access token taken from the browser's `localStorage` after login:

```
iat = 1792063312
exp = 1792066912          (1-hour lifetime)
now = 1792112534
```

The token was **760 minutes past `exp`**. It was then presented to:

| Target | Result |
|---|---|
| `:9010/masterdata/room` (gateway) | **200**, 25 rows |
| `:9005/room_reservation` (Hotel, direct) | **200** |
| `:9015/room` (Master Data, direct) | **200** |
| `:9020/roles` (User, direct) | **200** |
| `:9030/menu` (Restaurant, direct) | **200** |
| `:9025/menu` (Bar, direct) | **200** |
| any target, `Bearer not.a.token` | **401** `Invalid or expired token` |

Re-tested with a cache-busting query string and `Cache-Control: no-cache` to
rule out a caching layer: still 200. So the signature is checked and the
expiry is not.

### Root cause — established, and it is *not* in the current source

`Backend/tests/test_jwt_auth.py` already asserts this, and it passes:

```
$ cd Backend/Services/HotelServices
$ python -m pytest ../../tests/test_jwt_auth.py -q
..........                                                    [100%]
10 passed
```

The `"expired"` case — a token whose `exp` is one hour in the past — is
**refused 401** by the committed `verify_authentication`. The commit that added
that check is `6a0f5c6` ("Module 1: backend security and configuration
baseline", 2026-08-03), an ancestor of HEAD, 110 commits back.

So the committed code is correct and **LIVE is not running it**. Isolation
script: `QA/live/jwt_expiry_isolation.py`.

Two further signs the deployed build differs from the repo:

- `ASCEND_ENV` is not `production` on LIVE — `main.py:47` disables `/docs`,
  `/redoc` and `/openapi.json` only when `BaseConfig.IS_PRODUCTION`, and all
  six services publish `openapi.json` publicly.
- `verify_prod_env.py:115` would have failed this host on `ASCEND_ENV` alone.

### Remediation

Deploy HEAD (`5aa3755`), then re-run
`python Backend/tools/preflight.py --host 168.231.103.18` and confirm the
expired-token probe returns 401. Add the expired-token check to preflight so a
future deploy that regresses this is caught by the smoke test rather than by
whoever notices a 12-hour-old token still working.

---

## QA-BIZ-002 — a guest could be quoted a price for a room that cannot be booked

**Severity: Medium** · Status: **FIXED & RETESTED** · Role: any

### Reproduction

```
POST /hotel/room_reservation_quote   { room_ids: [34] }   -> 200, a full priced total
POST /hotel/room_reservation         same rooms, same dates -> 400
     "Room 601 is blocked / out of order and cannot be booked"
```

Room 601 carries `room_status = Blocking`. The quote produced line items, a
subtotal, tax and a grand total for it; the booking a moment later refused.

### Root cause — established

`quote_reservation` called `rules.quote(...)` and nothing else, so every gate in
what was then `assert_rooms_bookable` — existence, out of order, occupancy,
date overlap — was skipped. The endpoint's own docstring states its purpose:
*"the figures the guest is shown before confirming are produced by the server
that will store them, so the summary and the saved booking cannot disagree."*
It agreed about arithmetic and disagreed about sellability.

`create_room_reservation` and the amendment path both called
`assert_rooms_bookable`. The quote path did not.

### Fix

Extracted `assert_rooms_sellable(md, room_ids, occupancy=...)` — the gates that
need only the room master — out of `assert_rooms_bookable`, and had
`quote_reservation` call it before pricing. `assert_rooms_bookable` now calls it
first and adds the date-overlap check, so the booking path is unchanged.

**The date check was deliberately NOT moved into the quote.** The Edit screen
re-prices a reservation through this endpoint; the booking being edited overlaps
the very dates it is being moved to, and the caller sends no reservation id to
exclude it. Adding the check would have refused every amendment. It stays on the
create and update paths, which hold `db` and have `exclude_id`.

**Occupancy was deliberately NOT moved either**, because the quote payload
carries no `room_occupancy` and no adult/child counts — `AddNewReservation`
sends dates, rooms, rate types and pricing inputs and nothing else. Inferring a
party size from the room count would refuse quotes the booking endpoint accepts.

Regression test: `test_master_client.py::TestQuoteAndBookingAgree` — 5 tests,
including one asserting the quote endpoint *does* call the sellable gate and
*does not* call the database-backed one, and one that every pre-existing gate
survived the extraction. Verified failing without the fix
(`1 failed, 44 passed` -> `45 passed`).

---

## QA-SEC-004 — All six services run with development configuration

**Severity: High** · Status: FAIL (configuration)

`ASCEND_ENV` is `dev` or unset on LIVE. Consequences, all from `main.py`:

| Behaviour | Guard | LIVE |
|---|---|---|
| `/docs`, `/redoc`, `/openapi.json` published | `not IS_PRODUCTION` | **published on all 6** |
| Session cookie `Secure` | `IS_PRODUCTION` | **off** |
| `Strict-Transport-Security` | `IS_PRODUCTION` | **absent** |
| `DEBUG` | prod config only | dev default |

The full endpoint surface is self-documented at
`http://168.231.103.18:9010/docs` and on every backend port. No HTTPS on 5700
either, so the session cookie travels in clear.

Remediation: set `ASCEND_ENV=production` and terminate TLS in front of the
gateway. Blocked on infrastructure — not a source change.

---

## QA-SEC-005 — Guest phone and email reachable from the one page every role holds

**Severity: High** · Status: **FIXED & RETESTED** · Role: any

### The defect

The gateway map granted `GET /hotel/user_activity_log` to `/dashboard`.
`/dashboard` is the single page **every** role holds `view` on, so this endpoint
was the one guest-contact payload that enforcement alone would not have stopped.

Its response, for any authenticated user, including Housekeeping and Food &
Beverage:

```json
{"room_activity":[{"id":17,"room_no":"106, 107","reservation_id":"RES-202610-0017",
  "first_name":"<redacted>","last_name":"<redacted>","booking_status":"Confirmed",
  "phone":"<redacted>","email":"<redacted>"}]}
```

The values are redacted because the argument does not need them: what matters is
that `phone` and `email` are **in the response**, which is visible from the keys
alone. (This record is in the committed `hotelerp_hotel.sql` at HEAD in any case,
so this is tidiness rather than a fix — the redaction standard applied to the
password in QA-SEC-008 is the one that should apply here too.)

The Hotel Dashboard's Recent Activity card renders **only** the name, the room,
the status and the date. `phone` and `email` arrived and were never drawn.

### Why this is a repeat rather than a new mistake

The codebase had already made this exact correction on the same screen for
`GET /hotel/room_reservation`, and pinned it with
`test_a_dashboard_only_role_cannot_read_the_reservation_list`, whose docstring
reads:

> *"The Dashboard is a reporting screen, not a guest-contact export... That
> also handed this screen every guest's phone number and email, neither of which
> it renders, so opening the Dashboard meant receiving a complete guest contact
> list."*

`user_activity_log` was the same leak through a second door. The fix to the first
one did not cover it, because the map is derived per endpoint and nobody
connected the two.

### Fix

`HotelDashboardTab.jsx` no longer calls `/hotel/user_activity_log`. The card is
built from the two summaries the page already fetched —
`/hotel/reports/reservation_summary` (name, rooms, status, date, no contact
details) and `/hotel/housekeeper_tasks` (type, assignee, room, status). Every
field the card renders is still there.

The map was then regenerated, and the entire diff is one row:

```diff
-("hotel", "user_activity_log", "GET"): ("/dashboard", "/user_reserved_details"),
+("hotel", "user_activity_log", "GET"): ("/user_reserved_details",),
```

Verified mechanically: the only remaining caller of that endpoint anywhere in
`Frontend/src` is `UserReserved.jsx`, the Night Audit screen it was written for.
The regenerated map is byte-identical on re-run.

---

## QA-SEC-006 — Housekeeping holds read on the whole reservation book

**Severity: Medium** · Status: FAIL — role data, owner decision · Not a code defect

Housekeeping's role grants `view` on `/reservation`, `/reservation_view`,
`/booking` and `/add_new_reservation`. The reservation list is granted to
`/reservation`, and `/hotel/room_reservation` returns each guest's phone number
and email — so a housekeeper can read the full booking, including guest contact
details, for every reservation.

This is **not** a mapping bug. The grants are what `role_permissions` says, and
the Housekeeping role's own menu includes the Reservation section with all four
children, so it is visible in the product rather than hidden — which is what
distinguishes it from a defect. The map and the endpoint are both doing exactly
what they were configured to do.

It is nonetheless not least-privilege for the role: a housekeeper's job is task
assignment, room incident logs and room condition, none of which needs guest
contact details or the booking ledger. **A decision for the owner:** remove the
reservation grants from Housekeeping, or narrow `/hotel/room_reservation` so the
contact fields are released only to the front office. Recorded, not changed —
role configuration is not an audit's call.

---

## QA-BIZ-001 — a cancellation could be re-recorded, destroying the reason

**Severity: Medium** · Status: **FIXED & RETESTED** · Role: any

### Reproduction

```
POST /hotel/room_reservation_cancel/{token}  {"cancellation_reason": "guest changed their mind"}
POST /hotel/room_reservation_cancel/{token}  {"cancellation_reason": "duplicate cancel"}
GET  /hotel/room_reservation
```

The second call answered `200 "Reservation cancelled"` and the row's
`cancellation_reason`, `cancelled_at` and `cancelled_by` were **replaced**.
The original reason — the one thing that endpoint insists on asking for — was
gone.

### Root cause — established

`reservation_cancel` had no terminal-state guard. It read the reservation,
applied the status, then unconditionally assigned `cancellation_reason`,
`cancelled_at` and `cancelled_by`.

Both siblings already had the guard the codebase needed:
`reservation_no_show` calls `rules.assert_transition(...)`, and check-out raises
`409 "This reservation is Checked-Out; only a checked-in guest can be checked
out."` Cancel was the odd one out.

`rules.assert_transition` would **not** have caught it either, which is why this
was subtle: `can_transition` returns `True` when current equals target — "not a
transition at all" — which is right for an edit that changes nothing and wrong
here, because a repeat cancel is not idempotent. The correct test is
`rules.can_offer(status, CANCELLED)`, "legal **and** a change", which is also
what drives the UI's `can_cancel` flag — so the button and the endpoint now
answer from the same expression and cannot disagree.

### Fix

A guard before any write, answering `409`, with two distinct messages: one for
"already cancelled" that quotes the reason already on file, and one for a
booking past the point (checked in, checked out, no-show) that does not suggest
amending it.

Regression: `test_reservation_rules.py` — 3 controller tests driving the real
`reservation_cancel` with the JWT check, snapshot and row lookup stubbed, plus 4
rule tests and one source assertion. Verified failing without the fix
(`4 failed, 107 passed` -> `111 passed`).

---

## QA-SEC-007 — SPA answers `200 text/html` for every unknown path

**Severity: Medium** · Status: FAIL (carried over, re-verified)

`GET http://168.231.103.18:5700/does-not-exist-xyz.jpg` returns **200** with the
SPA `index.html`, because the static host uses a history fallback for all paths.
This masks genuine 404s from any HTTP-level check — it is what made an earlier
QA pass misread the missing-uploads finding.

Remediation: restrict the fallback to requests that send `Accept: text/html`.

---

## QA-SEC-008 — The demo password is published in committed files

**Severity: High** · Status: **PARTIALLY FIXED** — working tree clean, **git history still holds it** · Found by this audit, **pre-dates it**

The shared demo password for all ten accounts was written into the repository,
in files committed by an earlier session:

| File | Lines |
|---|---|
| `QA/FINAL_QA_REPORT.md` | 380, 385–394, 450, 463, 473, 485, 486 |
| `docs/CHERRY_HOTEL_ERP_PAGE_AUDIT.md` | 25 |

It is even annotated *"never commit this value"* three lines after being
committed. The account emails are listed alongside it, so the file was a complete
credential list for the staging deployment.

**Why it matters.** The value was in the repository, so it was in every clone and
in every backup of one. Any deployment provisioned from this tree — and the
brief's own staging host is one — ships a credential that is publicly known. If
that deployment is ever pointed at anything real, or the account is reused, the
password is the first thing an attacker tries, and it was already written down.

### What was done

- Both files redacted (17 occurrences). `Backend/tools/redact.py` does it — the
  value is read from stdin, never hardcoded in the tool, and the tool re-reads
  every file afterwards and fails if the literal survives. It refuses to blank
  the value outright, because a document that no longer explains what it was
  doing is worse than one that names a variable.
- The paragraphs that used it now say the password is supplied at seed time via
  `SEED_PASSWORD` and restored on demand by
  `Backend/tools/rotate_passwords.py --confirm --out <file>`.
- `.run-logs/api.py`, a gitignored runtime artifact, held a *different* stale
  literal from an earlier session. Scrubbed too: a gitignored file is not in the
  repository, but it is still a credential sitting on disk.
- **Verified across every file type in the working tree**, not just tracked
  source — `.sql`, `.yml`, `.env`, dumps included. One match survived the first
  sweep, which had an extension allowlist that omitted `.sql`. The corrected sweep
  found nothing.

### What was NOT done, and why it matters just as much

**Git history still contains the literal.** Two commits touched it:

- `d8b0949` "QA hardening pass, DB release 7-Oct-2026, and the final QA report"
- `5aa3755` "chore(db): re-export so the snapshot ships the documented demo
  password" — and its **commit message spells the password out**.

So this is not closed. Anyone with a clone still has it, and redacting the
working tree does not change that. Removing it properly needs a history rewrite
(`git filter-repo --replace-text`) plus a force-push, which rewrites every commit
after the first offence and invalidates every existing clone — that is the
owner's decision, not this audit's, and it is the kind of change that should be
made deliberately, once, with everyone told.

**The other half is rotation, and that is not optional.** Redaction removes the
published copy; it does not un-publish the one already in every clone. Until the
password is changed, the credential is still public no matter what the tree says.
`preflight.py` check 5 already fails while the seeded password works, so this is
already visible on every deploy — which is correct, and is the reason it should
not be left as a finding.

### An earlier decision, now reversed

The original note said this was **not fixed here**, on the grounds that both
files are a previous session's report and editing someone else's report is not
this audit's call. On being asked to solve the open items locally, that
reasoning does not hold: a credential published in a file does not stop being
published because the file belongs to someone else, and leaving it was the same
decision with an extra step. The judgement call that *does* remain the owner's is
the one about whether QA runbooks belong in the repository at all.

**Correction to this session's own work, recorded for the same reason.** The
first draft of this file reproduced the password inline in the step-by-step
reproduction above, and the QA harness scripts had it hardcoded. Both were
changed: reproduction steps now say "password from `QA_PASSWORD`", and the
scripts read it from the environment (`QA/live/qa_common.py`). No credential
is stored anywhere under `QA/live/`.

---

## QA-UX-001 — WITHDRAWN: reported in an earlier draft, it was a measurement error

**Status: WITHDRAWN — the application is not at fault**

An earlier draft of this report recorded a Low finding: *"No loading state for
lazy routes — a cold navigation leaves `<main>` completely empty, no spinner,
no skeleton, for 0.7–1.4 s."* **That was wrong.** It was my probe's fault, and
the mechanism is worth recording so nobody repeats it.

The sweep measured each page with
`document.querySelector('main').innerText.length` and treated a small value as
"nothing rendered". The lazy-route fallback in `App.jsx:116` is
`<Suspense fallback={<LogoLoaderComponent />} />`, and `LogoLoaderComponent`
renders **an `<img>` and nothing else** — the `<div className="logo-loader-text">
Loading...</div>` beside it is commented out at `LogoLoaderComponent.jsx:11`.

`innerText` is the rendered *text*. An image contributes none. So the loader was
present, filling the viewport, on every measurement the probe called "blank".

Measured properly on the same three routes that produced the worst readings:

| Route | at 250 ms |
|---|---|
| `/floor_layout` | `.logo-loader-container` present, 1296×886, `<img>` inside |
| `/rooms` | same |
| `/bar_orders` | same |

and gone by 700 ms, with the page fully rendered by 2.5 s. The full-viewport
branded loader is the intended behaviour and it works.

The corrected probe is the one to use for "did this page render":
**element count and image presence, not text length** — or `textContent`
together with `document.images.length`, since a text-only metric cannot tell an
image-only screen from an empty one.

Nothing was changed in the source for this, because there is nothing to change.
The only residual observation is an accessibility one, below.

### QA-UX-002 — the route loader has no accessible loading announcement

**Severity: Low** · Status: FAIL (reported, not changed)

The fallback is a 200 px pulsing logo with no text and no ARIA role. A screen
reader announces nothing while a route loads, and the one place a label could
have gone — `LogoLoaderComponent.jsx:11` — is commented out. The fix is small
and self-contained: restore the text node, or add `role="status"`
`aria-live="polite"` with visually-hidden text.

Left unchanged here because it is a design decision (a branded full-bleed
loader may be wanted with no caption) rather than a defect, and because
`npm run build` is blocked on this machine (§8), so a CSS change could not be
verified visually.

---

## Findings that are NOT defects

| Check | Result | Note |
|---|---|---|
| Tampered JWT signature | 401 | correctly refused |
| `alg: none` forgery | 401 | correctly refused |
| Unauthenticated access to any data route | 401 on 143/143 | authentication itself holds |
| `UserServices` write authorisation | enforced | 23 routes, 403 with a readable message |
| `POST /user/roles` as Housekeeping | 403 | *"Your role does not have create permission for /roles."* |
| Login rate limiting | present | 429 observed; `login()` waits the window out |
| `readyz` on gateway + services | 200 | LIVE-003 from the previous pass is **closed** |
| Row counts before/after restore | 25 rooms, 6 taxes | restored exactly |

---

## Process defect — my own, recorded because it changed staging

`QA/live/privesc_probe.py` (first version) probed **real** record ids with
DELETE, expecting a 403. Because authorisation is off, the DELETEs succeeded:

- `DELETE /masterdata/tax/6` as Housekeeping → `No Tax`, India, 0%
- `DELETE /masterdata/room/25` as Food & Beverage → Room 601, Presidential Suite

Restored within the same session by `QA/live/restore_after_probe.py` from the
snapshot the probe itself had printed. Row counts match the pre-probe values.

Residual differences, which the API cannot undo:

| Record | Restored | Not restored |
|---|---|---|
| `No Tax` | name, country, percentage, company | primary key 6 → 29 |
| Room 601 | number, name, type, bed, phone, occupancy, and `booking_status`/`working_status`/`room_status` reset to `Reserved`/`Not Ready`/`Blocking` | the four stored photo paths |

This is also the strongest single piece of evidence for QA-SEC-001: it was not
a denied request that happened to be logged, it was two rows actually removed by
a role that holds no permission on either page.

The corrected probe (`privesc_matrix.py`) targets id `999999999` only, so a
write verb has nothing to act on and the run is repeatable.
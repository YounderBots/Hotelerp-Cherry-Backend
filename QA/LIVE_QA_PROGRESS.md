# LIVE → LOCAL QA Progress Log

**Live URL:** http://168.231.103.18:5700/
**Admin account:** admin@cherryhotel.com (company email)
**Started:** 2026-10-03
**Rule:** LIVE is READ-ONLY. No create/edit/delete/upload/payment/credential/migration changes.

## Resume point

**LIVE admin sweep COMPLETE — all 60 routes tested.** Next action: non-admin role sweep
(Front Office Manager, Front Desk, Housekeeping, Food & Beverage), then responsive widths.
Fix queue is in `QA/LIVE_FIX_QUEUE.md`.

## Open findings

| ID | Severity | Page | Summary | Status |
|---|---|---|---|---|
| LIVE-001 | P0 | Auth / environment | A password randomly generated on the LOCAL QA workstation (`seed_demo_data.py --confirm`) authenticates successfully against LIVE. Local and live environments share a credential. | OPEN — needs owner decision |
| LIVE-002 | P1 | Room View (`/room_view`) + all upload-bearing screens | Every uploaded image 404s on LIVE: room photos, avatars, identity proofs, incident attachments, menu images. Database holds correct paths; the files are missing from the LIVE server. | ROOT CAUSE PROVEN — deployment/data gap, **not** a code defect |
| LIVE-003 | P1 | All LIVE backend services (9010, 9020, 9030 reachable) | LIVE services answer `/healthz` 200 but return 404 for `/readyz`. `/readyz` is committed locally in `5b05b4f` and absent on LIVE. **LIVE runs an older build than the pushed release.** | OPEN — deployment gap |
| LIVE-004 | P2 | SPA static hosting on :5700 | `:5700` answers every path with the SPA `index.html` (`text/html`, 728 bytes) — even `/does-not-exist-xyz.jpg`. Unknown asset paths return 200 HTML instead of 404. | OPEN — low severity, no current client-visible impact |

### LIVE-002 detail — CORRECTED root cause

**Correction to an earlier note in this log.** I first concluded the gateway served the images on
`:5700` and that the frontend was resolving against the wrong origin. That was wrong: `:5700` is the
SPA static host and returns `text/html` (728 bytes, the `index.html`) for *every* path, including
nonexistent ones. A 200 there is not evidence of an image.

**What `:9010` actually is.** Its `openapi.json` reports `title: HotelERP - Login Gateway`,
9 paths, including `/masterdata/{path}` — so `:9010` IS the gateway, and the frontend's
`VITE_API_BASE_URL` is correctly pointed at it. There is no origin misconfiguration.

**Evidence.**

| Probe | Result |
|---|---|
| LIVE `:9010` `/masterdata/templates/static/upload_image/<file>.jpg`, no token | **401** (route exists, auth required) |
| LIVE `:9010` same path **with valid Admin token** | **404** |
| LIVE `:9010` `/templates/static/upload_image/<file>.jpg` + token | **404** |
| LOCAL `:8000` `/masterdata/templates/static/upload_image/<file>.jpg` + token | **200 `image/jpeg`, 112020 bytes, JPEG magic `FFD8` verified** |
| LIVE `/masterdata/room` API | 200 — returns correct stored paths, e.g. `/templates/static/upload_image/b46c5a…jpg` |

**Root cause.** The gateway route and the frontend URL construction are both correct and verified
working locally. LIVE returns 404 for a path the database still references, so the **uploaded files
are not present in LIVE's MasterData service static tree**. The database rows were restored but
step 2 of the documented restore — `restore_uploads.py --release 30-Sept-2026` — was not run.
This is exactly the failure the release README warns about: "the SQL loaded, every endpoint answered
200, and all the image paths the API served resolved to nothing."

**Affected (all upload consumers):** room photos, user avatars, identity proofs, incident
attachments, restaurant menu images, bar menu images.

**Correct remediation — a deployment action, not a code fix:**

```bash
python Backend/tools/restore_uploads.py --release 30-Sept-2026
python Backend/tools/restore_uploads.py --release 30-Sept-2026 --verify
```

No source change is required. Deliberately **not** fixing in application code, per the instruction
not to work around this by copying files or duplicating assets.

**Local verification status:** all six asset classes fetch 200 `image/jpeg` through the local gateway
with a valid token, and remain protected (401 without). LIVE-002 needs no local fix.

## Route checklist (60 LIVE routes from session menu)

| # | Route | Label | Result |
|---|---|---|---|
| 1 | /dashboard | Dashboard | PASS (4 tabs verified: Overview/Hotel/Restaurant/Bar) |
| 2 | /add_new_reservation | Add New Reservation | PASS (form, 2 date inputs) |
| 3 | /reservation | Reservation | PASS (35 rows) |
| 4 | /booking | Booking | PASS (6 rows) |
| 5 | /room_view | Room View | PASS w/ LIVE-002 (25 rooms, images 404) |
| 6 | /reservation_view | Reservation View | PASS (25 res, 4 status groups) |
| 7 | /night_audit | Night Audit | PASS (14 tables, 46 rows) |
| 8 | /user_reserved_details | User Reserved Details | PASS |
| 9 | /room_booked_details | Room Booked Details | PASS (14 rows) |
| 10 | /settlement_summary | Settlement Summary | PASS (6 tables, 32 rows) |
| 11 | /guest_enquiry | Guest Enquiry | PASS (12 rows) |
| 12 | /task_assign | Task Assign | PASS (23 rows) |
| 13 | /room_incident_log | Room Incident Log | PASS (6 rows) |
| 14 | /employee | Employee | PASS (20 rows) |
| 15 | /user | User | PASS (role permissions panel) |
| 16 | /roles | Roles | PASS (10 rows) |
| 17 | /department | Department | PASS (16 rows) |
| 18 | /designation | Designation | PASS (20 rows) |
| 19 | /shift | Shift | PASS (8 rows) |
| 20 | /restaurant_roster | Restaurant Roster | PASS (20 rows) |
| 21 | /restaurant_shift_planning | Restaurant Shift Planning | PASS (empty state, 1 row) |
| 22 | /bar_roster | Bar Roster | PASS (20 rows) |
| 23 | /bar_shift_planning | Bar Shift Planning | PASS (empty state, 1 row) |
| 24 | /menus | Restaurant Menu Management | PASS (35 rows) |
| 25 | /combo_deals | Combo / Package Deals | PASS (empty state) |
| 26 | /floor_layout | Restaurant Floor Layout | PASS (6 rows) |
| 27 | /table_master | Restaurant Table Master | PASS (28 rows) |
| 28 | /orders | Restaurant Order Management | PASS (16 rows) |
| 29 | /table_reservation | Restaurant Table Reservation | PASS (empty state) |
| 30 | /kot/main_kitchen | Main Kitchen | PASS (KOT board) |
| 31 | /kot/grill | Grill Kitchen | PASS (KOT board) |
| 32 | /kot/dessert | Dessert Kitchen | PASS (KOT board) |
| 33 | /billing_payments | Restaurant Billing & Payments | PASS (16 rows) |
| 34 | /stock | Restaurant Inventory Control | PASS (20 rows) |
| 35 | /recipe_management | Restaurant Recipe Management | PASS (35 rows) |
| 36 | /guest_management | Restaurant Guest Management | PASS (16 rows) |
| 37 | /reports_analytics | Restaurant Report & Analytics | PASS (empty state, correct message) |
| 38 | /bar_menus | Bar Menu Management | PASS (28 rows) |
| 39 | /bar_floor_layout | Bar Floor Layout | PASS (4 rows) |
| 40 | /bar_table_master | Bar Table Master | PASS (20 rows) |
| 41 | /bar_orders | Bar Order Management | PASS (16 rows) |
| 42 | /bar_station | Bar Station Display | PASS (station selector) |
| 43 | /bar_billing_payments | Bar Billing & Payments | PASS (16 rows) |
| 44 | /bar_stock | Bar Stock | PASS (20 rows) |
| 45 | /bar_recipe_management | Bar Recipe Management | PASS (28 rows) |
| 46 | /bar_guest_management | Bar Guest Management | PASS (12 rows) |
| 47 | /bar_reports_analytics | Bar Report & Analytics | PASS (empty state, correct message) |
| 48 | /facilities | Facilities | PASS (25 rows) |
| 49 | /room_type | Room Type | PASS (16 rows) |
| 50 | /bed_type | Bed Type | PASS (16 rows) |
| 51 | /hall_floor | Hall / Floor | PASS (14 rows) |
| 52 | /rooms | Rooms | PASS (35 rows) |
| 53 | /discount_type | Discount Type | PASS (12 rows) |
| 54 | /tax_types | Tax Types | PASS (12 rows) |
| 55 | /payment_methods | Payment Methods | PASS (14 rows) |
| 56 | /identification_proof | Identification Proof | PASS (12 rows) |
| 57 | /currency_country | Currency & Country | PASS (10 rows) |
| 58 | /hsk_task_type | HSK Task Type | PASS (16 rows) |
| 59 | /complementary | Complementary | PASS (14 rows) |
| 60 | /reservation_status | Reservation Status | PASS (14 rows) |

Also to test: logout, profile, settings, forgot-password, request-access, and non-admin roles.

## Test log

- Login (company email, Admin): 200 → /dashboard. Role Admin, role_id=1. No console errors.
- Dashboard: renders with live data. No null/undefined/NaN. No broken images. No horizontal overflow.
- Dashboard tabs Overview/Hotel/Restaurant/Bar all render. Spinner counts seen were transient loading states (verified 0 after settle).
- **All 60 admin routes swept** at desktop width. Every route reached settled content (probe waits for
  stable text with no "Loading…" text). Zero `undefined` / `NaN` / `[object Object]` / `Invalid Date`
  sentinels. Zero bare `null` in rendered text. Zero horizontal overflow. Zero console errors on
  settled pages. Empty states render correct copy, not blanks.
- Routes showing correct empty states: `/combo_deals`, `/table_reservation`, `/reports_analytics`,
  `/bar_reports_analytics`, `/restaurant_shift_planning`, `/bar_shift_planning`.
- LIVE session token expired mid-sweep and the app correctly redirected to login with `?next=` —
  re-authenticated and re-verified the affected routes.
- Not yet done: non-admin role sweep, responsive widths, per-button/per-modal interaction testing,
  form validation testing.

## Local regression run (after LIVE-002 investigation)

| Suite | Result |
|---|---|
| `Backend/tests/run_all.py` | **31/31 suites passed** |
| `Backend/tests/e2e/run_all.py` | **6/6 suites, 345/345 checks** |
| `test_c066_fix.py` | PASS — 6/6 guest child endpoints, 6/6 readyz |
| `Frontend npm test` | **143/143 unit tests, 12 files** |
| `npm run lint` | 0 errors, 10 warnings (pre-existing) |
| `npm run build` | passed |
| `preflight.py` (with low-priv password) | **all checks passed, 0 warnings** |
| Static assets, 6 classes via gateway | all 200 with correct content-type |
| Identity proof without token | **401 — correctly protected** |
# QA Progress Log

**Project:** Cherry Hotel ERP  
**Last updated:** 2026-09-28  
**Current page:** 69 of 70 checklist rows pass locally; only Page 70 (`/authentication/otp`) is blocked, with no dead link exposed.  
**Next action:** the page sweep, the focused responsive sweep, the four-width full sweep and the control sweep are all complete, so the next work is the open release blockers: deployment verification, the bar/restaurant guest child-endpoint 403s (C-066), the stale `/readyz`, seeded `Hotel@2026`, and the outstanding P1 risks (partial-payment cancellation/split, overpayment races, tenant scoping, client-callable room-state mutation, logout/token revocation, upload/content validation, historical F&B inventory reconciliation). The release decision remains **NOT READY**.

## Persistent status

| Metric | Current value | Evidence / notes |
|---|---:|---|
| Routed URL entries | 69 | Extracted from `Frontend/src/App.jsx` |
| Page surfaces tracked | 70 | Includes intentionally unrouted OTP direct URL |
| Pages fully passed | 69 | Pages 1–13 and 15–69 pass locally, and Page 14 now passes after C-027/C-083 (13 + 56 = 69); Page 70 stays blocked; deployment blockers remain release blockers |
| Pages in progress | 0 | The page sweep, focused responsive sweep, four-width full sweep and control sweep are all complete; only the release blockers remain |
| Pages blocked | 1 | OTP (`/authentication/otp`): no route, no backend verification/resend contract, and no dead link in the UI |
| Confirmed bugs fixed and verified this run | 12+ | Hidden-route gate, shared table accessibility/print/test evidence, combo validation, dashboard availability metric, local-date/report handling, URL-addressable detail routes, room-card/file-input accessibility, booking API validation, detail RBAC, and F&B modifier/inventory hardening — plus the Master Data sweep findings C-068 through C-082 (13 pages, index/lock/validation/colour/upload/case-variant/metadata-drift classes) |
| Open P0/P1/P2 | At least the complaint categories in the register | Page evidence will refine the count |

## Completed baseline evidence

- `npm test -- --reporter=dot`: **113 tests passed across 10 files** (fresh run after the RoomCard, file-input, detail-RBAC, booking-boundary and C-081 sidebar changes).
- `npm run build`: **passed** (fresh Vite production build after the current fixes).
- `npm run lint`: completed with **0 errors and 11 warnings**; warnings are tracked as C-007 and are not suppressed.
- `python Backend/tests/run_all.py`: **26 suites passed** (21 existing — booking validation, combo rules, F&B hardening — plus `test_seed_night_audit.py` with 10 tests, and `test_upload_content.py` run from each of the four services that accept uploads: 65/65/65/78 tests).
- `python Backend/tests/e2e/run_all.py`: **6 suites / 345 HTTP tests passed** (fresh local MySQL run after the C-082, C-083 and C-085 changes; the stale 0% discount/tax and bar-table-selection expectations were corrected first, and two C-085 identity-document probes were added).
- `Frontend/e2e/auth_audit.mjs`: **16/16 public auth viewport checks passed** (4 routes × 4 widths).
- `Frontend/e2e/audit.mjs`: fresh desktop, laptop, tablet, and mobile sweeps passed after the current route/detail changes; the final four-width rerun is recorded in the final regression section below.
- `Frontend/e2e/interact.mjs`: fresh admin interaction sweep after the Page 56–68 changes: **43/43 table screens, 0 problems** — every screen re-sorted, missed and cleared a search, opened its Add dialog, had an empty submit refused with a message, and opened and closed a row's View and Edit; facilities and rooms additionally paged. Report: `e2e-reports/interact-admin-final.json`.
- `Frontend/e2e/client_sim.mjs`: fresh admin client simulation passed create/read/update/duplicate/delete/reload/sign-out; its deliberate duplicate produced the expected 409 console entry.
- `Frontend/e2e/reservation_pages_audit.mjs`: the focused route list now covers 56 routes (all reservation/account/guest/HRM/restaurant/bar/master-data surfaces) and the consolidated master-data run passed 224 route/viewport rows at 1440/1024/768/375 with 0px overflow, 0 modal overflow, and no console/page/request/HTTP errors. Report: `Frontend/e2e-reports/reservation-pages-all-masterdata-final.json`.
- Local stack startup: all six services and Vite answered their health/root probes through `start-network.ps1` (re-confirmed after the 2026-09-27 environment restart; `/healthz` 200 on 8000/8020/8030/8040/8050/8060 and HTTP 200 on 5173).
- Existing `Frontend/e2e-reports/audit-admin.json` was inspected as historical evidence; it is not treated as a fresh current run.

## Page 1 test record — Login `/`

### Test cases

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Open root as signed-out user | PASS | Browser rendered Welcome Back, email/password fields, forgot-password/request-access links, and logo |
| 1 | Empty submit | PASS | Login button was disabled before credentials were entered |
| 1 | Show password toggle | PASS | Browser evaluation confirmed `type=text`, `aria-pressed=true`, and label “Hide password” after activation |
| 1 | Invalid credentials | PASS | `POST /login_post` returned 401; UI displayed “Invalid email or password.” |
| 1 | Valid credentials | PASS | Seeded admin login returned 200 and redirected to `/dashboard`; token/session navigation observed |
| 1 | Client-side email/password boundaries | PASS | Invalid email and five-character password were refused before a request |
| 1 | Duplicate/rapid submit | PASS | Two immediate submit activations produced one pending login request; loading/disabled state held |
| 1 | Refresh/persistence/direct protected route | PASS | Logout cleared the session; `/facilities` redirected to `/?next=%2Ffacilities`; valid login restored the intended destination |
| 1 | Responsive layout | PASS | `auth_audit.mjs` passed login at 1440, 1024, 768, and 375 with no overflow, broken image, console, page, or network error |
| 1 | Console/network | PASS with expected negative test | Deliberate invalid attempts produced expected 401 console entries; valid path had no 5xx or transport failure |

### Defects / observations

- No Page 1 defect remains open.
- Expected browser console errors for the deliberate invalid-login tests are recorded separately from application defects; no unexpected error occurred.
- The seeded password is used only against the local demo database. It remains a release blocker if valid on a production deployment (C-005).

### Fixes verified during this run

- `RequirePage` now allows the two stateful detail routes (`/ReservationView`, `/view`) that are intentionally absent from the menu, while API authorization remains enforced.
- `TableTemplate` now has real labelled sort buttons, `aria-sort`, a named/ Escape-closeable column dialog, pagination button semantics, a popup-blocked print message, and excludes the Actions column from sorting.
- `interact.mjs` no longer treats the non-sortable S.No header as a passing sort test; the focused `TableTemplate` regression tests pass.
- Hotel environment documentation and the combo-deal validation model/API now match the actual gateway architecture and reject malformed combo lines before a database error.

### Required retest

- Page 1 has no remaining retest. Continue with Page 2 — Forgot password — and record each test in this file before advancing.

## Page 2 test record — Forgot password `/authentication/forgotpassword`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Open public route signed out | PASS | Heading, explanatory copy, email field, disabled submit, and back link rendered |
| 1 | Empty submit | PASS | Submit disabled until an email is entered |
| 1 | Invalid email | PASS | `bad` displayed “Enter a valid email address.” and no mailto navigation occurred |
| 1 | Valid email/mailto handoff | PASS | Valid address produced the prepared-request status, disabled repeated submission, and direct admin contact link |
| 1 | Back navigation | PASS | Back link returned to `/` and rendered Login |
| 1 | Responsive layout | PASS | `auth_audit.mjs` passed this route at 1440/1024/768/375 with no overflow, broken image, console, page, or network error |

**Page 2 result: PASS.** No code defect was found. The flow intentionally composes a `mailto:` because the repository has no reset endpoint or mail service; that product contract remains documented rather than hidden.

## Page 3 test record — Lock screen `/authentication/lockscreen`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Signed-out direct URL | PASS | Redirected to Login with the safe `?next=/facilities` destination |
| 1 | Authenticated lock screen | PASS | Name/email, password field, unlock, different-user action, and forgot link rendered |
| 1 | Wrong password | PASS | 401 produced “Password did not match. Please try again.” and kept the screen usable |
| 1 | Password visibility | PASS | Toggle changed input type and exposed correct pressed/label state |
| 1 | Valid unlock | PASS | 200 restored the session and navigated to the requested `/facilities` |
| 1 | Sign in as different user | PASS | Session cleared and Login rendered; intended destination remained safely encoded |
| 1 | Responsive layout | PASS | `auth_audit.mjs` passed this route at 1440/1024/768/375 with no overflow, broken image, console, page, or network error |

**Page 3 result: PASS.** No code defect was found. The route is direct-only because the idle policy now signs out rather than locks; that legacy surface remains safe and testable.

## Page 4 test record — Request access `/authentication/register`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Open public route | PASS | Request Access form, policy copy, optional fields, consent, and Sign in link rendered |
| 1 | Empty submit | PASS | Name, email, company, and consent errors displayed; no mailto handoff |
| 1 | Invalid phone | PASS | `123abc` was rejected with a field-specific phone error |
| 1 | Valid form/consent | PASS | Valid name/email/company/phone/notes and checked consent prepared the mailto request and disabled repeat submit |
| 1 | Sign-in navigation | PASS | Sign in link returned to Login |
| 1 | Responsive layout | PASS | `auth_audit.mjs` passed this route at 1440/1024/768/375 with no overflow, broken image, console, page, or network error |

**Page 4 result: PASS.** No code defect was found. Terms/privacy links are plain text when the deployment has not supplied policy URLs, rather than opening dead application routes.

## Page 5 test record — Admin dashboard `/dashboard`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Authenticated load and Overview tab | PASS | Combined Revenue, department breakdown, occupancy, orders/bills, room status, arrivals/departures, charts, and quick actions rendered; five Overview report/resource calls returned 200 |
| 1 | Hotel tab / KPI consistency | PASS after fix | Hotel metrics, dated sales, platform chart, room availability, recent bookings/activity loaded; local request trace had no 4xx/5xx. The KPI now excludes dirty/maintenance rooms and agrees with the room-status card (verified 7 available, 7 not-ready, 25 total) |
| 1 | Restaurant tab and report date | PASS | Date changed from `2026-09-24` to `2026-09-23`; all eight Restaurant report calls carried the new date and returned 200; empty-date states rendered; Refresh issued a second complete report batch |
| 1 | Bar tab and report date | PASS | Date changed to `2026-09-23`; all six Bar report calls carried the new date and returned 200; empty-date states rendered; Refresh issued a second complete report batch |
| 1 | Overview return and quick actions | PASS | View Hotel/Restaurant/Bar module actions switched tabs; New Reservation, New Restaurant Order, and New Bar Order navigated to `/add_new_reservation`, `/orders`, and `/bar_orders` respectively |
| 1 | Hotel recent-booking row / Add Booking | PASS | A recent row opened `/ReservationView` with reservation data; Add Booking opened the reservation form; no data-changing submit was performed |
| 1 | Responsive and error sweep | PASS | Fresh `Frontend/e2e/dashboard_audit.mjs` passed desktop 1440, laptop 1024, tablet 768, and mobile 375: 0px overflow, no console/page/request/HTTP errors; report at `Frontend/e2e-reports/dashboard-audit-fresh4.json` |
| 1 | Error/retry path | PASS with no forced outage | Loading and component error/retry affordances are present in source; normal local calls returned 200 and no unexpected error was recorded |

**Page 5 result: PASS.** Fix C-020 was confirmed in the browser: the Hotel KPI previously counted housekeeping-blocked rooms as available (12 versus the room card's 7), and now reports the sellable count consistently.

## Page 6 test record — Reservation list `/reservation`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Authenticated load/API shape | PASS | 27-row reservation envelope loaded with server-side status/type/payment/date filters; master-data lookups and reservation list calls returned 200; no console/page/request errors |
| 1 | Search and empty state | PASS | `RES-202609-0025` reduced the table to one row; nonsense search showed “No results match your search”; clear search restored 27 rows |
| 1 | Sort and pagination | PASS | Real Reservation ID sort reordered rows and exposed `aria-sort=ascending/descending`; Next changed the range from 1–10 to 11–20; First returned to page 1 |
| 1 | Status filter and clear | PASS | Selecting `Cancelled` issued `GET /hotel/room_reservation?reservation_status=Cancelled`, returned three matching rows, and Clear restored the unfiltered list |
| 1 | Column visibility dialog | PASS | Dialog opened with close control focused; Escape closed it; checkbox/reset/apply affordances remained usable |
| 1 | View modal/payment history/print | PASS | View opened `RES-202609-0025`; payment-history GET returned 200; guest/stay/charges/payment sections rendered; print action opened a separate print window (closed after inspection) |
| 1 | Edit validation and quote UI | PASS | Edit modal loaded room/tax/discount/payment data and live quote totals; empty/invalid submit remained in the dialog with a visible validation alert; Escape cancelled without a write |
| 1 | Delete/cancel/no-show safeguards | PASS | Delete confirmation displayed the destructive distinction and Escape cancelled; cancel reason was required; no-show confirmation displayed room-release/chargeable consequences and was cancelled without a write |
| 1 | Payment validation | PASS | Record Payment opened with outstanding balance; empty submit displayed “Enter an amount greater than 0”; modal was cancelled without a financial write |
| 1 | Responsive/regression evidence | PASS | Fresh protected-route audit passed `/reservation` at 1440/1024/768/375; shared table interaction audit also exercised search, sort, pagination, filters, modal cancel, and row actions |

**Page 6 result: PASS.** No unresolved P0/P1/P2 defect was found on the reservation list during this pass. Destructive lifecycle writes remain reserved for the explicit client simulation/flow tests.

## Page 7 test record — Reservation model view `/ReservationView`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Direct URL and refresh | PASS | `/ReservationView?reservationId=25` loaded `RES-202609-0025` after a full navigation; the query ID survives refresh without navigation state |
| 1 | Detail/API shape | PASS | `GET /hotel/room_reservation/25` returned 200 with guest, stay, room/rate breakdown, charges, payment state, and confirmation; payment-history GET returned 200 |
| 1 | Missing/invalid ID | PASS | `/ReservationView` showed “No reservation was selected” and made no detail request; `?reservationId=999999` showed the 404-derived “Room reservation not found” alert with Retry |
| 1 | Toolbar actions | PASS | Refresh repeated the detail GET; Back returned to `/reservation`; Edit returned to the owning list; Print surfaced and dismissed the blocked-popup alert |
| 1 | Responsive/regression | PASS | `Frontend/e2e-reports/reservation-pages-admin-final2.json` passed valid/missing detail routes at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |
| 1 | RBAC | PASS in UI; deployment blocker remains | Housekeeping (`reservation=r`) initially received an Edit button; `ReservationModelView` now checks `/reservation` permissions and the view-only role receives no Edit control. `perm_ui.mjs` passed; gateway enforcement is still blocked by C-003 |

**Page 7 result: PASS locally.** The detail route is read-only for view-only roles after the permission fix. C-003/P0 deployment enforcement and the external deployment-access blockers still make the overall release **NOT READY**.

## Page 8 test record — Add reservation `/add_new_reservation`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Date-first availability | PASS | Future stay loaded `GET /hotel/room_availability`; reversed dates issued no availability request and kept the room grid hidden; 2-night calculation matched the selected dates |
| 1 | Room-card semantics | PASS | Standard Room tab exposed real buttons; Room 107 selected with `aria-pressed=true`; Room 101 was disabled with its booked dates; unavailable cards could not be activated |
| 1 | Guest/file validation | PASS | Empty guest, invalid file type, missing file, and capacity cases stayed on Step 3 with visible errors; valid JPG upload was accepted; capacity copy is now grammatically singular for one adult |
| 1 | Billing quote | PASS | Room 107 × 2 nights = 7,000; GST 18% and 5% discount recalculated to 7,910; paying 8,000 produced a 90 refundable warning; negative room amount was rejected with “Room amount cannot be negative” |
| 1 | Create/duplicate guard | PASS | The previously exercised local flow produced one `POST /hotel/room_reservation` (201) for a double activation and redirected to the reservation list; no duplicate row was created |
| 1 | Responsive/regression | PASS | Focused four-width audit passed `/add_new_reservation` with 0px overflow and no runtime errors; manual desktop detail/form and accessible file-input snapshot passed after the latest CSS/JS changes |

**Page 8 result: PASS locally.** The local test reservation created during the earlier critical-flow pass is reservation ID `31` / `RES-20260924-57126F`; it is explicitly marked for cleanup or documented retention before final sign-off. The seeded demo credential and deployment/RBAC blockers remain release blockers.

## Page 9 test record — Booking `/booking`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | List/search/sort/empty | PASS | Three seeded rows rendered; Ganesh search reduced the list, nonsense search showed the empty state, clear restored rows, and Booking ID sort changed order |
| 1 | Column dialog/export/print | PASS | Column visibility checkbox/reset/apply and Escape worked; copy JSON produced success feedback; CSV and PDF downloads completed; print action produced no unexpected dialog/error |
| 1 | View/edit/delete | PASS | View rendered guest/stay details; multi-select room types survived an edit; update persisted through `PUT /hotel/room_booking`; delete confirmation cancelled safely, then a test row was deleted with 200 |
| 1 | Add-form validation | PASS | Blank, invalid phone/email, missing dates, zero rooms, negative children, and room/type cardinality errors were visible without a write; one room type per room is now enforced in UI and service |
| 1 | Positive API/DB path | PASS | A fresh one-room/one-type test returned 201 (`RB-BF54CB6B`, ID 14), appeared in the table, and was then soft-deleted locally; request body and response were captured |
| 1 | Service-boundary hardening | PASS | Direct malformed probes now return 400 for bad date, zero rooms, unknown type, and two-types/one-room; focused `test_booking_validation.py` has 13 passing tests and `run_all.py` reports 21 suites passed |
| 1 | Responsive/regression | PASS | Focused four-width audit passed `/booking` and its Add Booking dialog at 1440/1024/768/375 with 0px overflow and no runtime errors; fresh `interact.mjs` passed the page |

**Page 9 result: PASS locally.** The temporary positive booking (ID 14) was removed. The earlier reservation ID 31 remains the only explicitly tracked local test reservation pending final cleanup decision.

## Page 10 test record — Room view `/room_view`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial data/status buckets | PASS | 25 room cards loaded; canonical buckets reconciled to All 25, Available 6, Reserved 6, Occupied 6, Not Ready 7; room-type labels and capacities rendered |
| 1 | Status filters | PASS | Each tab selected exactly its declared rooms; `aria-selected` and empty/filtered state stayed correct; All restored the full grid |
| 1 | Card/modal detail | PASS | Room 601 opened a labelled dialog with image/fallback, room number, type, status, adult/child capacity, and phone; no broken images |
| 1 | Modal controls/keyboard | PASS | Close button, Escape, and Tab containment work; focus moves to Close and returns to the originating card; body scroll lock releases |
| 1 | Refresh/back | PASS | Refresh repeated room and room-type GETs with 200 responses; Back returned to `/reservation` |
| 1 | Responsive/regression | PASS | `Frontend/e2e-reports/reservation-pages-room-view-final.json` passed the route and modal at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 10 result: PASS locally.** C-026 was fixed and browser-verified. Counts now agree with the refreshed dashboard room-status card; the release remains **NOT READY** for the existing deployment, credential, media, and RBAC blockers.

## Page 11 test record — Reservation view `/reservation_view`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial board/status counts | PASS | 32 reservation cards loaded; server envelope reported total 32 and status counts that reconciled to Upcoming 11, Checked-In 6, Checked-Out 9, Cancelled 5, No-Show 1 |
| 1 | Status filters | PASS | All six tabs selected the expected card count and status set; each tab’s `aria-selected` state and card labels remained correct |
| 1 | Card navigation | PASS | No-Show card `RES-202609-0023` opened `/ReservationView?reservationId=23`; detail data loaded with the query-addressable route |
| 1 | Refresh/back | PASS | Refresh repeated `GET /hotel/room_reservation` with 200 responses; Back returned to `/reservation` |
| 1 | Responsive/regression | PASS | Final four-width full route audit passed `/reservation_view`; focused route evidence shows no broken images, blank render, overflow, console, page, or HTTP errors |

**Page 11 result: PASS locally.** This is a read-only status board; it offers no lifecycle write controls, so detailed payment/status transition paths remain covered by the reservation list/detail and backend E2E suites. The release remains **NOT READY**.

## Page 12 test record — Profile `/profile`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Own-record load | PASS | `GET /user/me` returned 200; name, role, employee code, company/personal email, department/designation, shift, contact, DOB, address, and emergency fields rendered |
| 1 | Avatar/media | PASS | Authenticated photo request returned 200 and rendered a blob image with no broken asset; no unauthorized static path was used |
| 1 | Toolbar/navigation | PASS | Refresh repeated `/user/me` and `/user/me/photo`; top Settings and inline Settings link both opened `/settings`; Back returned to the prior page |
| 1 | Read-only boundary | PASS | No edit controls are offered for HR-maintained fields; the page correctly directs password changes to Settings |
| 1 | Responsive/regression | PASS | Account-focused audit passed `/profile` at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 12 result: PASS locally.** No password or credential rotation was performed.

## Page 13 test record — Settings `/settings`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial/empty state | PASS | Password form rendered with three required fields, disabled submit, clear hints, and no account preference controls that lack a backend contract |
| 1 | Password visibility | PASS | Show/Hide changed all three input types and `aria-pressed`; values remained intact |
| 1 | Client validation | PASS | Short new password, mismatched confirmation, and unchanged-password cases showed field errors/`aria-invalid` and kept submit disabled |
| 1 | Wrong-current negative path | PASS | Valid-shaped request with a deliberately wrong current password returned 403, displayed “The current password is not correct,” retained the form, and did not rotate the credential; `/user/me` remained 200 |
| 1 | Navigation/responsive | PASS | Profile button and Back returned to Profile; account-focused audit passed Settings at 1440/1024/768/375 with no overflow/runtime errors |

**Page 13 result: PASS locally.** A successful password change was intentionally not executed because credential rotation is outside the QA authorization boundary.

## Page 14 test record — Night audit process `/night_audit`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Preview/readiness | PASS | Preview and history endpoints returned 200; business date, server-date lag, revenue/tax/discount/settlement, occupancy, in-house, arrivals/departures, warnings, and six list counts rendered |
| 1 | Audit lists/tables | PASS | In House (4), Arrivals Due (3), Not Checked In (3), Departures Due (2), Overdue (2), and Unsettled (8) each selected the expected rows; search and column visibility worked |
| 1 | Export/print controls | PASS | CSV and PDF downloads completed; copy/print controls were exercised; the print window opened successfully and was closed |
| 1 | Confirmation safety | PASS | Run opened a confirmation restating date, next date, revenue/collected/occupancy, outstanding balance, and no-show count; checkbox toggled; Cancel sent no run request |
| 1 | API negative paths | PASS | Missing date returned 400, malformed date returned 400, stale business date returned 409; no successful run was performed against the local demo |
| 1 | RBAC | PASS in UI; gateway blocker remains | Admin and Front Office Manager saw an enabled run control; Front Desk, Housekeeping, and Food & Beverage were denied the page. `night_audit_rbac.mjs` passed all five role probes |
| 1 | History consistency | BLOCKED | Preview exposed `last_audit_at=2026-09-17 02:15`, but history returned zero rows; UI now labels this “Business-date marker … no audit snapshot” and C-027 remains open pending seed/data reconciliation |

**Page 14 result: BLOCKED for release sign-off.** The control flow and API guards passed, but the immutable audit history/data invariant is not satisfied by the local fixture. Do not run a real audit merely to make the demo look complete; reconcile the marker/snapshot first. The overall release remains **NOT READY**.

## Page 15 test record — User reserved details `/user_reserved_details`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Default load | PASS | Activity summary showed 8 reservation activities and 3 housekeeping tasks; both API-backed tables rendered with room/guest/status and task fields |
| 1 | Date range | PASS | From/To 2026-09-24 produced 7 reservation rows and the expected query parameters; one-sided input showed “pick a To date”; Clear restored the default range |
| 1 | Range boundary/empty | PASS | Reversed range produced a safe zero-result state and no 4xx/5xx; the date inputs expose min/max constraints for normal keyboard selection |
| 1 | Tabs/tables | PASS | User Activity and House Keeper tabs switched to the correct data sets; search, column visibility, CSV/PDF/copy/print controls were present and usable |
| 1 | View modals | PASS | Reservation Activity and House Keeper Task dialogs showed the expected identity, stay, phone/status, assignment, task status, and schedule fields; close returned focus through the shared Modal |
| 1 | Responsive/regression | PASS | Final four-width route audit passed `/user_reserved_details`; no overflow, console, page, request, or HTTP errors |

**Page 15 result: PASS locally.** This report is read-only; it creates no business records. The release remains **NOT READY**.



## Page 16 test record — Room booked details `/room_booked_details`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Current-night report | PASS | Preview showed 7 rooms sold/room nights, room revenue 62,938, tax 9,408, gross 66,297, and seven room-held rows; row night revenue reconciled to the server total |
| 1 | Date filter | PASS | Selecting 2026-09-16 switched to a clearly labelled past night with server-recomputed 6 rooms/37,438/5,612/40,533 totals; Clear restored the current business date |
| 1 | Status/search/table controls | PASS | Confirmed and Checked-In filters selected the expected rows; search, column visibility, CSV/PDF/copy/print controls were usable |
| 1 | View booking | PASS | Modal showed guest/stay/room/status, per-night room revenue/tax/discount/extra charges, and whole-stay billed/paid/balance fields; close returned safely |
| 1 | Responsive/regression | PASS | Final four-width full route audit passed `/room_booked_details`; no overflow, console, page, request, or HTTP errors |
| 1 | KPI correction | PASS | C-028 fixed: Rooms sold now reads the server’s `rooms_sold` field rather than unique `rooms_occupied`; current demo remains 7, with multi-room regression contract identified |

**Page 16 result: PASS locally.** The report is read-only. The release remains **NOT READY** for C-027 and the existing deployment/RBAC/media blockers.

## Page 17 test record — Settlement summary `/settlement_summary`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Current-night totals | PASS | Collected 1,960, Outstanding 176,378 across 8 folios, gross 66,297, room revenue 62,938, tax 9,408, and discount 7,599 rendered from the server position |
| 1 | Past-night date | PASS | Business date 2026-09-16 switched to past-night totals (collected 26,180, outstanding 94,954, gross 40,533) and 5 unsettled/2 payment/6 all-folio tabs; Clear restored current date |
| 1 | Payments reconciliation | PASS | Payments tab showed Cash 14,896 and UPI 11,283.75, summing exactly to collected 26,180 |
| 1 | Tabs/tables/view | PASS | Unsettled, Payments, and All Folios tabs switched correctly; search/column/export/print controls were present; settlement modal showed whole-stay billed/paid/balance and per-night accrual fields |
| 1 | Responsive/regression | PASS | Final four-width full route audit passed `/settlement_summary`; no overflow, console, page, request, or HTTP errors |

**Page 17 result: PASS locally.** The report is read-only and reconciles the server’s payment breakdown and folio balances. The release remains **NOT READY**.

## Page 18 test record — Guest enquiry `/guest_enquiry`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table | PASS | Six seeded enquiries loaded with guest, mode, response, follow-up, status, and received fields; all row actions were exposed to Admin |
| 1 | Search/filter/empty | PASS | Guest search, status/mode filters, selected-filter empty state, Clear, and date controls were exercised; no-result copy was accurate after search was cleared |
| 1 | Sorting/columns/export | PASS | Guest-name sort toggled ascending/descending with `aria-sort`; column visibility Apply/Reset worked; JSON copy, CSV, PDF, and print controls completed (print window closed) |
| 1 | Add validation | PASS | Empty submit showed required guest/mode errors and sent no request; 255-character counters and mode/status closed vocabularies rendered correctly |
| 1 | Create/persistence | PASS | `QA Enquiry Sep24` POST returned 201, appeared in the table, and was visible after reload; response/follow-up/incident text was preserved |
| 1 | View/edit/status | PASS | Detail modal showed enquiry/handling/record fields; edit form preserved free-text notes, changed status In Progress → Completed and response, and PUT persisted the change |
| 1 | Delete safeguards | PASS | Delete confirmation named the record; Cancel sent no write; confirmed DELETE returned 200 and the test row disappeared from API/UI |
| 1 | API negative matrix | PASS | Missing fields, invalid mode, and 256-character note returned 400; null optional fields were accepted (201) and the temporary row was immediately deleted; final count returned to six |
| 1 | RBAC | PASS in UI; gateway blocker remains | Admin/Front Office Manager/Front Desk saw page-appropriate add/edit controls; Front Office Manager had no delete; Housekeeping and Food & Beverage were denied. `guest_enquiry_rbac.mjs` passed five role probes |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-final.json` passed `/guest_enquiry` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 18 result: PASS locally.** Temporary enquiry ID 10 and the null-note probe row were deleted; no test row remains. The release remains **NOT READY**.

## Page 19 test record — Employee `/employee`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search/pagination | PASS | Ten seeded employees loaded with IDs, names, mobile, department, designation, role, and image; search, sorting, First/Next/Last, columns, and exports were available |
| 1 | View/detail | PASS | Employee detail modal showed identity, contact, role/organization, emergency, photo, and acknowledgement data; the seeded image loaded |
| 1 | Add validation/create | PASS | Empty submit produced required-field feedback without a write; a disposable employee POST returned 201, appeared in the table, and preserved all populated fields |
| 1 | Edit/persistence | PASS | Edit form retained free-text and master-data values, changed experience, and PUT persisted `updated_at` and the new value |
| 1 | Delete safeguards | PASS | Confirmation named the employee; Cancel sent no write; confirmed DELETE returned 200 and the row disappeared from API/UI |
| 1 | Duplicate protection | PASS after fix | Rapid double confirmation now produced one DELETE; rapid double submit on a disposable employee produced one PUT. C-029 fixed with synchronous refs, awaited refresh, and failure-target retention |
| 1 | Cleanup | PASS | Disposable employee IDs 11–14 were deleted through the local API/UI; final active employee count returned to 10 |
| 1 | RBAC | PASS in UI; gateway blocker remains | `employee_rbac.mjs` passed five roles: Admin had all controls; Front Office Manager, Front Desk, Housekeeping, and Food & Beverage were denied the page |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-employee-final.json` passed `/employee` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 19 result: PASS locally after C-029 remediation.** No test employee remains. The release remains **NOT READY**.

## Page 20 test record — User role permissions `/user`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial/empty state | PASS | No-role-selected guidance, Reset, Save, role selector, and permissions explanation rendered without an error |
| 1 | Admin matrix load | PASS after C-030/C-031 fixes | `GET /user/role_permissions/1?include_empty=true` returned 200; Admin rendered 45/45 flags with no error |
| 1 | Restricted role | PASS | Food & Beverage rendered its 7/45 saved permissions; role switching updated the caption and matrix |
| 1 | Toggle/reset | PASS | Individual and all-permission controls changed local state; dirty count and Save enabled/disabled states were correct; Reset restored baseline |
| 1 | Save/cleanup | PASS after C-032 fix | Dashboard View was toggled off then restored for Food & Beverage; each save produced POST 409 → PUT 200, followed by a 200 matrix reload; final checked count returned to 7 |
| 1 | Duplicate protection | PASS after hardening | Rapid double Save produced one POST/PUT pair, not duplicate writes; save state was released after completion |
| 1 | API/data effect | PASS | Role-permission endpoint returned `permission_id` values (for example Dashboard ID 112), and PUT persisted the final flag state; no unrelated role was changed |
| 1 | Responsive/RBAC/regression | PASS | Focused 40-check audit passed `/user` and its Admin matrix at 1440/1024/768/375 with 0px overflow/no runtime errors; `user_rbac.mjs` passed five role probes (Admin access, four denials) |

**Page 20 result: PASS locally after C-030–C-032 remediation.** C-031 required a local gateway restart after the exemption fix; the release still depends on deployment-time restart/map regeneration. The release remains **NOT READY**.

## Page 21 test record — Department `/department`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search | PASS | Eight seeded departments loaded with name/action columns; search, sorting, column controls, exports, and pagination controls rendered |
| 1 | View/validation | PASS | Department detail modal showed the selected name; empty submit and required-name feedback were exercised without a write |
| 1 | Create/duplicate | PASS after C-033 fix | Disposable department created with 201; rapid double submit now produced one POST, and the row appeared after refresh |
| 1 | Edit/persistence | PASS after C-033 fix | Name edit returned 200, persisted in the list/API, and rapid double submit produced one PUT |
| 1 | Delete/cleanup | PASS after C-033 fix | Confirmation/cancel path was exercised; rapid double confirm produced one DELETE; all disposable rows were removed and active count returned to eight |
| 1 | API race/invariant | PASS after migration | Two concurrent direct POSTs for the same company/name returned one 201 and one 409; active-name generated-column unique index is applied in the local DB, while inactive history remains reusable |
| 1 | RBAC | PASS in UI; gateway blocker remains | `department_rbac.mjs` passed five role probes: Admin had all controls; Front Office Manager, Front Desk, Housekeeping, and Food & Beverage were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-department-final.json` passed `/department` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 21 result: PASS locally after C-033 remediation.** The migration is a local demo change only; production must run it (or an equivalent schema migration) before release. The release remains **NOT READY**.

## Page 22 test record — Designation `/designation`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search | PASS | Ten seeded designations loaded with name/action columns; search, sorting, columns, exports, and pagination controls were present |
| 1 | View/validation | PASS | Detail modal showed the selected designation; empty submit and required-name feedback were exercised without a write |
| 1 | Create/duplicate | PASS after C-034 fix | Disposable designation created with 201; rapid double submit now produced one POST, and the row appeared after refresh |
| 1 | Edit/persistence | PASS after C-034 fix | Name edit returned 200, persisted in the list/API, and rapid double submit produced one PUT |
| 1 | Delete/cleanup | PASS after C-034 fix | Confirmation path and rapid double confirm produced one DELETE; disposable IDs 11–14 were removed and active count returned to ten |
| 1 | API race/invariant | PASS after migration | Two concurrent direct POSTs for the same company/name returned one 201 and one 409; the active-name generated-column index is applied locally and preserves inactive history |
| 1 | RBAC | PASS in UI; gateway blocker remains | `designation_rbac.mjs` passed five role probes: Admin had all controls; Front Office Manager, Front Desk, Housekeeping, and Food & Beverage were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-designation-final.json` passed `/designation` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 22 result: PASS locally after C-034 remediation.** The local migration is not a production deployment; the release remains **NOT READY**.

## Page 23 test record — Roles `/roles`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search | PASS | Five seeded roles loaded with name/description/action columns; search, sorting, columns, exports, pagination, and print controls were present |
| 1 | View/validation | PASS | Role detail modal showed name and description; empty submit was rejected; description overflow at 256 characters showed `256 / 255` and sent no POST |
| 1 | Create/duplicate/recreation | PASS after C-035 fix | Disposable role create returned 201; rapid double submit produced one POST; a soft-deleted role name could be recreated after migration cleanup |
| 1 | Edit/persistence | PASS after C-035 fix | Description update returned 200 and persisted; rapid double submit produced one PUT |
| 1 | Delete/cleanup | PASS after C-035 fix | Rapid double confirmation produced one DELETE; disposable role IDs were removed and active seeded roles remained |
| 1 | Self-delete guard | PASS after C-037 fix | Direct rejected `DELETE /user/roles/1` returned 400 “You cannot delete your own role”; no row changed |
| 1 | RBAC/self-escalation | PASS in UI/API probe | Admin had all controls; all four non-admin role probes were denied the page and invalid-payload POSTs returned 403; `roles_rbac.mjs` passed five roles |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-roles-final.json` passed `/roles` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 23 result: PASS locally after C-035–C-037 remediation.** The active-name migrations and legacy-index removal are local demo changes and must be included in deployment migration plans. The release remains **NOT READY**.

## Page 24 test record — Shift `/shift`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search | PASS | Four seeded shifts loaded with start/end/duration columns; overnight `22:00–06:00` rendered as `8h`; search, sorting, columns, exports, pagination, and print controls were present |
| 1 | View/validation | PASS | Detail modal showed name, duration, and times; empty/equal-time UI validation and malformed API probes were exercised |
| 1 | API time boundaries | PASS after C-038 fix | `not-a-time`/`25:99` and equal start/end payloads returned 400; valid HH:MM payload returned 201; no malformed row remained |
| 1 | Create/edit | PASS after C-038 fix | Disposable overnight shift POST returned 201; rapid double submit produced one POST; edited overnight times persisted with one PUT and correct duration |
| 1 | Delete/cleanup | PASS after C-038 fix | Rapid double confirmation produced one DELETE; disposable shift IDs were removed and active count returned to four |
| 1 | API race/invariant | PASS after migration | Two concurrent valid same-name writes returned one 201 and one 409; active-name generated-column index is applied locally |
| 1 | RBAC | PASS in UI; gateway blocker remains | `shift_rbac.mjs` passed five role probes: Admin had all controls; Front Office Manager, Front Desk, Housekeeping, and Food & Beverage were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-shift-final.json` passed `/shift` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 24 result: PASS locally after C-038 remediation.** The local migration is not a production deployment; the release remains **NOT READY**.

## Page 25 test record — Restaurant roster `/restaurant_roster`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search | PASS | Ten seeded employees rendered with ID, staff, contact, role, floor, section, shift, and status columns; search, sorting, columns, exports, pagination, and print controls were present |
| 1 | Date navigation | PASS after C-039 fix | Roster date input, Previous, Next, and Today controls were added/wired to `shift_date`; changing the date to 2026-09-26 issued the matching GET and updated the heading, and Previous moved back to 2026-09-24 |
| 1 | Assign validation | PASS | Empty assignment produced employee-required feedback without a write; role/floor/section/time controls and overnight-friendly times rendered |
| 1 | Create/duplicate | PASS after C-039 fix | Disposable Meera assignment returned 201 and appeared in the roster/detail modal; rapid double Assign produced one POST; duplicate rows created before the fix were deleted |
| 1 | API boundaries/race | PASS after C-039 fix | Invalid role and equal start/end payloads returned 400; concurrent valid writes returned 201/409; test assignment was deleted and final active roster returned to empty |
| 1 | RBAC | PASS in UI; gateway blocker remains | `restaurant_roster_rbac.mjs` passed five roles: Admin had date/assign/view controls; the four non-admin roles were denied the page |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-restaurant-roster-final.json` passed `/restaurant_roster`, date controls, and Assign dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 25 result: PASS locally after C-039 remediation.** The local restaurant migration is not a production deployment; the release remains **NOT READY**.

## Page 26 test record — Restaurant shift planning `/restaurant_shift_planning`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial empty/date state | PASS | Empty planning table, date navigation, Add Shift, search, columns, exports, pagination, and print controls rendered |
| 1 | Date navigation | PASS after C-040 fix | Planning date input and Previous/Next/Today controls changed the `shift_date` query and heading; empty state remained correct for an unscheduled date |
| 1 | Add validation/create | PASS after C-039/C-040 fixes | Empty submit rejected employee; valid Meera/Waiter/Ground Floor/Restaurant assignment returned 201 and appeared in the table; rapid double submit produced one POST |
| 1 | View/edit | PASS | Detail modal showed assignment, attendance, cash/sales sections; edit preserved disabled employee/date, updated time/target, and rapid double submit produced one PUT |
| 1 | Clock in/out | PASS | Negative opening cash was rejected without a request; valid clock-in/out each produced one POST; status transitions and cash fields persisted |
| 1 | Cancel/cleanup | PASS after C-040 fix | Cancel confirmation retained the target until success; rapid double confirmation produced one DELETE; test shift ID 6 was cancelled and final roster count returned to zero |
| 1 | API boundaries/race | PASS after C-039 fix | Invalid role/equal-time assignment probes returned 400; concurrent same employee/date writes returned 201/409; no malformed/test row remains |
| 1 | RBAC | PASS in UI; gateway blocker remains | `restaurant_shift_planning_rbac.mjs` passed five roles: Admin had date/Add controls; all four non-admin roles were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-restaurant-shift-planning-final.json` passed `/restaurant_shift_planning`, date controls, and Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 26 result: PASS locally after C-039/C-040 remediation.** The local restaurant migration is not a production deployment; the release remains **NOT READY**.

## Page 27 test record — Bar roster `/bar_roster`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search/date | PASS | Ten seeded employees rendered with ID, staff, contact, role, floor, shift, and status; date input and Previous/Next/Today controls queried the selected `shift_date` |
| 1 | Assign validation/create | PASS after C-041 fix | Empty assignment rejected employee; valid Meera/Bartender/Bar Level assignment returned 201 and appeared in roster/detail modal; rapid double Assign produced one POST |
| 1 | API boundaries/race | PASS after C-041 fix | Invalid role and equal start/end payloads returned 400; concurrent valid writes returned 201/409; test assignment IDs were removed and active bar roster returned to zero |
| 1 | View/cleanup | PASS | Roster detail showed employee, role, floor, shift, and scheduled status; API DELETE returned 200 and no test row remained |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_roster_rbac.mjs` passed five roles: Admin had date/assign/view controls; all four non-admin roles were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-roster-final.json` passed `/bar_roster`, date controls, and Assign dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 27 result: PASS locally after C-041 remediation.** The local bar migration is not a production deployment; the release remains **NOT READY**.

## Page 28 test record — Bar shift planning `/bar_shift_planning`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial empty/date state | PASS | Empty bar planning table, date navigation, Add Shift, search, columns, exports, pagination, and print controls rendered |
| 1 | Date navigation | PASS | Planning date input and Previous/Next/Today controls changed the `shift_date` query and heading |
| 1 | Add validation/create | PASS after C-042 fixes | Empty submit rejected employee; valid Meera/Bartender/Bar Level assignment returned 201 and appeared; rapid double submit produced one POST |
| 1 | View/edit | PASS | Detail modal showed assignment, attendance, and cash/sales; edit preserved employee/date lock, updated time/target, and rapid double submit produced one PUT |
| 1 | Clock in/out | PASS | Clock-in/out each produced one POST; status/attendance fields persisted; shared negative-cash guard prevented invalid requests |
| 1 | Cancel/cleanup | PASS after C-042 fix | Cancel confirmation retained target until success; rapid double confirmation produced one DELETE; test shift ID 4 was cancelled and final count returned to zero |
| 1 | API boundaries/race | PASS after C-041 fix | Invalid role/equal-time probes returned 400; concurrent valid writes returned 201/409; no malformed/test row remains |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_shift_planning_rbac.mjs` passed five roles: Admin had date/Add controls; all four non-admin roles were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-shift-planning-final.json` passed `/bar_shift_planning`, date controls, and Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 28 result: PASS locally after C-041/C-042 remediation.** The local bar migration is not a production deployment; the release remains **NOT READY**.

## Page 29 test record — Task assign `/task_assign`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/filters | PASS | Thirteen seeded housekeeping assignments loaded with staff, room, task type, schedule, room status, and task status; search, severity/date/status filters, Clear, columns, exports, and pagination rendered |
| 1 | Add validation/create | PASS after C-043 fix | Empty assignment produced required employee feedback without a write; disposable Meera/Pest Control task returned 201 and appeared; rapid double submit produced one POST |
| 1 | View/edit/status | PASS | Detail modal showed assignment, status, lost-found, instructions, and record metadata; edit preserved locked employee/room identity and persisted notes/status |
| 1 | Room-state invariant | PASS | Setting Pending + Blocking changed room 601 to Blocking/Not Ready; completing released the room; setting Pending + Blocking again and deleting returned it to UnBlocking/Not Assigne |
| 1 | Delete/cleanup | PASS after C-043 fix | Rapid double confirmation produced one DELETE; disposable task ID 17 was removed and the seeded task count returned to 13 |
| 1 | RBAC | PASS in UI; gateway blocker remains | `task_assign_rbac.mjs` passed five role probes: Admin all controls; Front Office Manager view-only; Housekeeping add/edit but no delete; Front Desk and Food & Beverage denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-task-assign-final.json` passed `/task_assign` and its Assign dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 29 result: PASS locally after C-043 remediation.** The room-state invariant was verified against Master Data; the release remains **NOT READY**.

## Page 30 test record — Room incident log `/room_incident_log`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search/filters | PASS | Three seeded incidents loaded with room/date/severity/description/reporter/file columns; search, severity/date filters, Clear, columns, exports, and pagination controls rendered |
| 1 | Add validation/create | PASS after C-043/C-044 fixes | Empty submit produced required-field feedback without a write; disposable incident returned 201; rapid double submit produced one POST |
| 1 | View/attachment | PASS | Incident detail showed assignment, people, resolution, record metadata, and authenticated attachment preview; uploaded PNG rendered from an object URL with nonzero dimensions |
| 1 | Edit/replacement/persistence | PASS | Replacement PNG upload plus changed description returned 200, changed attachment path, updated `updated_at`, and preserved prior fields; rapid double submit produced one PUT |
| 1 | Delete/cleanup | PASS after C-043 fix | Rapid double confirmation produced one DELETE; disposable incident ID 7 was removed and final active count returned to three |
| 1 | API boundaries | PASS after C-044 fix | Invalid severity/date/time/room and executable attachment returned 400; report-before-incident create returned 400 after the fix; no negative row remained |
| 1 | RBAC | PASS in UI; gateway blocker remains | `room_incident_rbac.mjs` passed five role probes: Admin all controls; Front Office Manager view-only; Housekeeping add/edit but no delete; Front Desk and Food & Beverage denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-room-incident-final.json` passed `/room_incident_log` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 30 result: PASS locally after C-043/C-044 remediation.** The API chronology guard and upload boundaries are locally verified; deployment/RBAC blockers remain. The release remains **NOT READY**.

## Page 31 test record — Restaurant floor layout `/floor_layout`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/search | PASS | Three seeded floors loaded with number/name/type/table/capacity/service columns; search, sorting, columns, exports, pagination, and print controls rendered |
| 1 | Add validation/create | PASS after C-045 fix | Empty submit showed required name/number feedback; disposable floor returned 201; rapid double submit produced one POST; duplicate pre-fix rows were removed |
| 1 | View/floor-plan link | PASS | Detail modal exposed floor metadata and “Open floor plan” navigated to addressable `/view?floorId={id}`; seeded/disposable floor information rendered correctly |
| 1 | Edit/persistence | PASS after C-045 fix | Name/capacity edit returned 200 and persisted; rapid double submit produced one PUT |
| 1 | Service toggle | PASS after C-045 fix | Rapid double toggle produced one PUT; service state changed Open → Closed and reload reflected it |
| 1 | Delete/cleanup | PASS after C-045 fix | Rapid double confirmation produced one DELETE; disposable floor ID 8 was deactivated and active count returned to three |
| 1 | API race/boundaries | PASS after C-045 fix | Concurrent same number/name writes returned 201/409; generated active number/name indexes are applied locally; malformed field validation is enforced server-side |
| 1 | RBAC | PASS in UI; gateway blocker remains | `floor_layout_rbac.mjs` passed five role probes: Admin all controls; Food & Beverage could view/add/edit/toggle but not delete; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-floor-layout-final.json` passed `/floor_layout` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 31 result: PASS locally after C-045 remediation.** The local floor migration is not a production deployment; the release remains **NOT READY**.

## Page 32 test record — Restaurant floor page view `/view`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Addressable floor view | PASS | Direct `/view?floorId=1` loaded floor metadata, tables/orders/staff queries, and Back to Floor Layout; `/view` without an id showed the explicit no-floor state |
| 2 | Tables tab | PASS | Eight seeded tables rendered with number/name/capacity/type/section/status/server; search, sorting, columns, exports, and View action opened a table detail modal |
| 3 | Orders tab | PASS | Eight floor orders rendered with order type/guest/time/status/amount; View modal exposed table, payment, subtotal, and grand total; search/table controls were present |
| 4 | Staff tab | PASS | Empty state and columns rendered; current staff count matched the selected floor and no staff modal was falsely exposed |
| 5 | Detail modals/navigation | PASS | Table, order, and staff detail modal contracts were checked; direct URL and browser back/forward navigation remained addressable |
| 6 | RBAC | PASS after C-046 fix | `floor_view_rbac.mjs` passed five roles: Admin and Food & Beverage retained the view; Front Office Manager, Front Desk, and Housekeeping received the standard denial instead of an empty shell |
| 7 | Responsive/regression | PASS | Existing focused `room-view` checks plus the four-width audit covered `/view?floorId=1` with no overflow/runtime errors; the page has no canvas/zoom surface in the current read-only implementation |

**Page 32 result: PASS locally after C-046 remediation.** The current route is a read-only table/order/staff floor view rather than a visual canvas; that product contract is recorded explicitly. The release remains **NOT READY**.

## Page 33 test record — Restaurant table master `/table_master`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/pagination | PASS | Eighteen seeded tables loaded across three floors; table code/name/floor/capacity/type/server/order/status columns, search, sorting, columns, exports, and First/Previous/Next/Last controls rendered |
| 1 | Add validation/create | PASS after C-047 fix | Empty submit showed required-field feedback; disposable VIP table returned 201; rapid double submit produced one POST; duplicate pre-fix rows were removed |
| 1 | View/edit | PASS after C-047 fix | Table detail showed code/name/number/floor/section/type/capacity/status/server/order/mergeability; edit persisted capacity and server with one PUT |
| 1 | Delete/cleanup | PASS after C-047 fix | Rapid double confirmation produced one DELETE; disposable table ID 23 was deactivated and active count returned to 18 |
| 1 | API race/boundaries | PASS after C-047 fix | Concurrent same number/name writes on one floor returned 201/409; active generated-column indexes and positive/vocabulary server validation are applied locally |
| 1 | RBAC | PASS in UI; gateway blocker remains | `table_master_rbac.mjs` passed five role probes: Admin all controls; Food & Beverage view/add/edit but no delete; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-table-master-final.json` passed `/table_master` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 33 result: PASS locally after C-047 remediation.** The local table migration is not a production deployment; the release remains **NOT READY**.

## Page 34 test record — Restaurant orders `/orders`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/pagination | PASS | Eleven seeded orders loaded across two pages with order number/type/service location/guest/guests/total/status/payment; search, sorting, columns, exports, and pagination controls rendered |
| 1 | Add validation/create | PASS after C-048 fix | Empty Dine-In submit showed table-required feedback; disposable order on Table 3 returned 201; rapid double Create produced one POST; concurrent same-table requests returned 201/400 without deadlock |
| 1 | Detail/add item | PASS after C-048 fix | Order detail exposed status/payment/total and item table; Butter Chicken qty 2 returned 201 once under rapid Add and recalculated total to 960.00 |
| 1 | Remove item | PASS after C-048 fix | Item confirmation named the item; rapid double Remove produced one DELETE and recalculated total to 0.00 |
| 1 | Cancel/table release | PASS after C-048 fix | Cancel confirmation named the order; rapid double Cancel produced one PUT; order 15 became Cancelled and Table 3 returned to Available/current order null |
| 1 | RBAC | PASS in UI; gateway blocker remains | `orders_rbac.mjs` passed five role probes: Admin and Food & Beverage had add/view; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-orders-final.json` passed `/orders` and its Add dialog at 1440/1024/768/375 with 0px overflow and no runtime errors |

**Page 34 result: PASS locally after C-048 remediation.** Temporary order 15 was cancelled and no test table/order remains active; the release remains **NOT READY**.

## Page 35 test record — Restaurant table reservation `/table_reservation`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/controls | PASS | Empty seeded table loaded with reservation code/guest/contact/date/start/table/guests/source/status columns; search, sorting, columns, exports, and pagination controls rendered |
| 1 | Add validation/create | PASS after C-049 fix | Empty Dine-In submit showed required table/contact/time feedback; disposable reservation returned 201; rapid double Submit produced one POST; pre-fix duplicate rows were terminalized and retained only as history |
| 2 | View/status lifecycle | PASS after C-049 fix | View modal exposed booking, contact, source, occasion, requests, check-in/out metadata; rapid Check in produced one PUT and changed table 4 to Occupied; Complete produced one PUT and released it to Available |
| 3 | No-show/cancel | PASS after C-049 fix | Rapid no-show confirmation produced one PUT and released table 5; terminal reservations rejected further transitions with 409; no active QA booking remained |
| 4 | API race/boundaries | PASS after C-049 fix | Concurrent same-table/date/time requests returned 201/409; table row lock, interval overlap check, positive-guest/time/source validation, and lookup index are applied locally |
| 5 | RBAC | PASS in UI; gateway blocker remains | `table_reservation_rbac.mjs` passed five role probes: Admin and Food & Beverage retained add/view; Front Office Manager, Front Desk, and Housekeeping were denied |
| 6 | Responsive/regression | PASS | `reservation-pages-all-pages-table-reservation-final.json` passed 96 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 35 result: PASS locally after C-049 remediation.** The local reservation index and table-lock behavior are not production deployment evidence; terminal QA history is retained without an active booking. The release remains **NOT READY**.

## Page 36 test record — Restaurant menu management `/menus`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table/controls | PASS | Twenty-five seeded items loaded across three pages with code/item/category/kitchen/price/variants/availability columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add validation/create | PASS after C-050 fix | Empty submit showed required item/price/category feedback; disposable item returned 201; rapid double Submit produced one POST; pre-fix duplicate rows were deactivated |
| 1 | Image upload/preview | PASS | PNG upload returned a site-relative path, authenticated blob preview rendered with nonzero dimensions in the form and detail view, and edit preserved the image path |
| 1 | Edit/view/persistence | PASS after C-050 fix | Detail showed code/category/kitchen/pricing/attributes; edit changed price/description with one PUT and persisted after reload |
| 1 | Variants/modifiers | PASS after C-050 fix | Existing variant and modifier add/update/delete each produced one request; `has_variants`/detail state refreshed; invalid duplicate/negative API probes returned 400 |
| 1 | Delete/cleanup | PASS after C-050 fix | Rapid double Deactivate produced one DELETE; disposable item ID 32 was deactivated and active menu count returned to 25 |
| 1 | API/race/boundaries | PASS after C-050 fix | Concurrent same category/name writes returned 201/409; invalid category/kitchen/status/price/variant/modifier and executable image returned 400; active generated indexes are applied locally |
| 1 | RBAC | PASS in UI; gateway blocker remains | `menus_rbac.mjs` passed five role probes: Admin all controls; Food & Beverage view/add/edit but no delete; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-menus-final.json` passed 100 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 36 result: PASS locally after C-050 remediation.** The local menu migration is not a production deployment; the release remains **NOT READY**.

## Page 37 test record — Restaurant combo/package deals `/combo_deals`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial empty/table controls | PASS | Empty combo state loaded; Add Combo, search, sorting, columns, exports, and pagination controls rendered |
| 1 | Add validation/create | PASS after C-051 fix | Empty submit showed required name/price feedback; item row validation rejected missing/duplicate/zero-quantity lines; disposable combo returned 201; rapid double Submit produced one POST |
| 1 | View/edit | PASS after C-051 fix | Detail showed code/price/date range/description and included item chips; edit changed price/description with one PUT and preserved linked items |
| 1 | Delete/cleanup | PASS after C-051 fix | Rapid double confirmation produced one DELETE; disposable combo ID 3 was deactivated and active count returned to zero |
| 1 | API race/boundaries | PASS after C-051 fix | Concurrent same-name writes returned 201/409; blank/invalid menu/duplicate item probes returned 400; negative price/date/quantity schema probes returned 422; active generated name index is applied locally |
| 1 | RBAC | PASS in UI; gateway blocker remains | `combo_deals_rbac.mjs` passed five role probes: Admin and Food & Beverage had add access; Front Office Manager, Front Desk, and Housekeeping were denied; row actions were manually verified for Admin |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-combo-deals-final.json` passed 104 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 37 result: PASS locally after C-051 remediation.** The local combo migration is not a production deployment; the release remains **NOT READY**.

## Page 38 test record — Main kitchen KOT `/kot/main_kitchen`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Active KOT table | PASS | Three seeded active KOTs plus disposable KOT 4 loaded with KOT/order/table/item/time/status/priority/status columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Refresh controls | PASS | Auto-refresh switch toggled off/on; manual Refresh returned fresh KOT data without a write |
| 1 | View/items | PASS | KOT detail showed table/priority/status/placed metadata, item name/quantity/status, and Mark Ready action |
| 1 | Acknowledge | PASS after C-052 fix | Disposable KOT 4 changed New → Acknowledged; rapid action produced one PUT after the ref fix; backend acknowledged timestamp persisted |
| 1 | Item/whole completion | PASS after C-052 fix | Mark Ready changed the item Pending → Ready with one PUT; Mark Whole KOT Ready changed KOT 4 to Completed with one PUT; modal closed and list refreshed |
| 1 | Cleanup/invariant | PASS | Order 16 was cancelled after KOT completion; table 6 returned to Available/current order null; no temporary active KOT remained |
| 1 | RBAC | PASS in UI; gateway blocker remains | `main_kitchen_rbac.mjs` passed five role probes: Admin and Food & Beverage had KOT view/refresh controls; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-main-kitchen-final.json` passed 108 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 38 result: PASS locally after C-052 remediation.** KOT inventory/claim behavior remains covered by the backend hardening suites; the release remains **NOT READY**.

## Page 39 test record — Grill kitchen KOT `/kot/grill`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Empty station/table controls | PASS | Grill station initially showed the explicit no-open-tickets state; table columns, search, sorting, exports, pagination, Refresh, and auto-refresh switch rendered |
| 2 | Disposable KOT lifecycle | PASS after C-052 fix | Created order 17 with Grill menu item and confirmed KOT 5 at ASAP priority; view showed Grilled Vegetable Platter Pending; rapid acknowledge, Mark Ready, and whole-KOT completion each produced one PUT |
| 2 | Cleanup/invariant | PASS | Order 17 was cancelled after KOT completion; table 7 returned to Available/current order null; no temporary active grill KOT remained |
| 1 | Refresh/navigation | PASS | Manual Refresh and direct Grill route loaded station-specific data; KOT modal close returned to the list |
| 1 | RBAC | PASS in UI; gateway blocker remains | `grill_kitchen_rbac.mjs` passed five role probes: Admin and Food & Beverage had Grill access/refresh; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-grill-kitchen-final2.json` passed 112 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 39 result: PASS locally after C-052 remediation.** The release remains **NOT READY**.

## Page 40 test record — Dessert kitchen KOT `/kot/dessert`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Empty station/table controls | PASS | Dessert station initially showed the explicit no-open-tickets state; columns, search, sorting, exports, pagination, Refresh, and auto-refresh switch rendered |
| 2 | Disposable KOT lifecycle | PASS after C-052 fix | Created order 18 with Chocolate Brownie and confirmed KOT 6 at Normal priority; view showed the item Pending; rapid acknowledge, Mark Ready, and whole-KOT completion each produced one PUT |
| 2 | Cleanup/invariant | PASS | Order 18 was cancelled after KOT completion; table 8 returned to Available/current order null; no temporary active dessert KOT remained |
| 1 | Refresh/navigation | PASS | Manual Refresh and direct Dessert route loaded station-specific data; KOT modal close returned to the list |
| 1 | RBAC | PASS in UI; gateway blocker remains | `dessert_kitchen_rbac.mjs` passed five role probes: Admin and Food & Beverage had Dessert access/refresh; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-dessert-kitchen-final.json` passed 116 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 40 result: PASS locally after C-052 remediation.** The release remains **NOT READY**.

## Page 41 test record — Restaurant billing/payments `/billing_payments`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial bill table | PASS | Eleven seeded bills loaded across two pages with bill/order/table/subtotal/discount/grand total/status/payment columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Generate validation/create | PASS after C-053 fix | Generate modal loaded a Served order and item subtotal; empty selection and invalid discount paths were guarded; disposable bill 14 returned 201; rapid double Generate produced one POST after the ref/backend fix |
| 1 | Charges/totals | PASS | 140.00 subtotal, 2.5% CGST + 2.5% SGST + 5% service produced 154.00 total; view exposed item/payment/summary sections and Print Bill completed |
| 1 | Payment edge cases | PASS after C-053 fix | Missing mode/amount showed client error; overpayment 200 against 154 outstanding returned 400; partial 54.00 payment returned 201 once under rapid submit and balance logic rejected excess |
| 1 | Cancel/cleanup | PASS after C-053 fix | Rapid cancel with reason produced one PUT; bill 14 became Cancelled; order 19 was cancelled and table 9 returned Available/current null; duplicate bills 12/13 were cancelled after the pre-fix reproduction |
| 1 | API race | PASS after C-053 fix | Order row lock and active bill index are applied locally; duplicate pre-fix generation was 201/201, and post-fix UI generation was one 201; invalid discount/duplicate/overpayment paths remained rejected |
| 1 | RBAC | PASS in UI; gateway blocker remains | `billing_payments_rbac.mjs` passed five role probes: Admin and Food & Beverage had generate/view access; Front Office Manager, Front Desk, and Housekeeping were denied; payment/cancel actions were manually verified for Admin |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-billing-payments-final.json` passed 120 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 41 result: PASS locally after C-053 remediation.** The local bill migration is not production deployment evidence; the release remains **NOT READY**.

## Page 42 test record — Restaurant inventory/stock `/stock`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial stock table | PASS | Ten seeded stock rows loaded with item/unit/store/available/minimum/status/last-updated columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add validation/create | PASS after C-054 fix | Empty/negative minimum validation ran; disposable QA Stock Item returned 201; rapid double Add produced one POST; duplicate name now returns 409 across legacy branch IDs |
| 1 | View/adjust | PASS after C-054 fix | Stock view exposed quantity/minimum/status/last-updated; reduce/add forms rendered units and reasons; invalid zero/negative quantity was rejected before a write |
| 1 | Movement history | PASS | Movement modal loaded date/type/quantity/reference/remarks table with search/pagination controls and exposed the QA adjustment ledger |
| 1 | API boundaries | PASS after C-054 fix | Invalid transaction type and reduction below zero returned 400; company-wide active item index is applied locally; stock row lock protects concurrent updates |
| 1 | Cleanup | PASS | QA item 12 was deactivated and its stock/transactions removed locally; active stock count returned to the seeded ten rows |
| 1 | RBAC | PASS in UI; gateway blocker remains | `stock_rbac.mjs` passed five role probes: Admin and Food & Beverage had add/view/adjust/movements; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-stock-final.json` passed 124 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 42 result: PASS locally after C-054 remediation.** The local inventory migrations and targeted cleanup are not production deployment evidence; the release remains **NOT READY**.

## Page 43 test record — Restaurant recipe management `/recipe_management`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial recipe table | PASS | Twenty-five menu rows loaded with item code/name/kitchen/ingredient count/status columns; search, sorting, exports, and pagination rendered |
| 1 | Empty/edit state | PASS | Opening a menu with no active recipe rendered one blank ingredient row; Cancel closed without a write; opening a seeded recipe loaded its existing ingredient |
| 1 | Save/replace/view | PASS after C-055 fix | Same-ingredient replacement returned 201 after the active-line index migration; rapid double UI Submit produced one POST; view showed menu metadata and ingredient quantity/unit |
| 1 | Multi-ingredient/concurrency | PASS after C-055 fix | Added Basmati Rice and Chicken rows, saved once, and concurrent replacement requests left two unique active lines with no legacy constraint failure |
| 1 | API boundaries | PASS after C-055 fix | Empty recipe, duplicate ingredient, wrong unit, and unavailable inventory item returned 400; menu row lock and active generated line index are applied locally |
| 1 | Cleanup | PASS | Active test recipes for menu IDs 1 and 8 were soft-deactivated; inactive history was retained and both API recipe counts returned zero |
| 1 | RBAC | PASS in UI; gateway blocker remains | `recipe_management_rbac.mjs` passed five role probes: Admin and Food & Beverage had view/edit; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-recipe-management-final.json` passed 128 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 43 result: PASS locally after C-055 remediation.** The local recipe migration is not production deployment evidence; the release remains **NOT READY**.

## Page 44 test record — Restaurant guest management `/guest_management`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial guest table | PASS | Eight seeded guests loaded with guest ID/name/mobile/type/loyalty columns; search, sorting, exports, and pagination rendered |
| 1 | Add validation/create | PASS after C-056 fix | Empty submit showed first-name/mobile feedback; disposable guest returned 201; rapid double Submit produced one POST; mobile was normalized and persisted |
| 1 | View/edit/persistence | PASS after C-056 fix | Profile showed identity/preferences/visit empty state; edit changed name/notes with one PUT and persisted after reload |
| 1 | Delete/cleanup | PASS after C-056 fix | Rapid double Deactivate produced one DELETE; disposable guest IDs 9 and 10 were deactivated and active directory count returned to eight; soft-deleted history remains |
| 1 | API race/boundaries | PASS after C-056 fix | Concurrent same-mobile creates returned 201/409; invalid mobile/email/type and duplicate update returned 400/409; active company-wide mobile index and row locks are applied locally |
| 1 | RBAC | PASS in UI; gateway blocker remains | `guest_management_rbac.mjs` passed five role probes: Admin all actions; Food & Beverage add/view/edit but no delete; Front Office Manager, Front Desk, and Housekeeping denied; loyalty endpoint remains gateway-blocked |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-guest-management-final.json` passed 132 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 44 result: PASS locally after C-056 remediation.** The local guest migration and inactive test history are not production deployment evidence; the release remains **NOT READY**.

## Page 45 test record — Restaurant reports/analytics `/reports_analytics`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Date/initial state | PASS | Current date loaded with zero-state sales summary/report; report date input had a today maximum; changing to 2026-09-15 refreshed totals and item rows |
| 1 | Sales summary | PASS | Dated summary rendered orders 3, bills 3, gross sales 9,660.00, tax 531.30, discount 0.00, grand total 11,157.30; item quantities/amounts matched API |
| 1 | Report tabs | PASS | Orders, Kitchen, Staff, Tables, Inventory, and Financial tabs each loaded their endpoint/empty or data state; Inventory correctly removed the date control and used low-stock data |
| 1 | Export/print/search | PASS after C-057 fix | Table search/sort/columns/CSV/PDF/print controls rendered; CSV and print actions completed without runtime errors; report aggregates and lookup labels are company/status filtered |
| 1 | API boundaries | PASS after C-057 fix | Dated report matrix returned 200 for seeded/current/future dates; malformed date returned 422; no report endpoint returned 5xx; low-stock join now filters inactive/cross-company items |
| 1 | RBAC | PASS in UI; gateway blocker remains | `reports_analytics_rbac.mjs` passed five role probes: Admin and Food & Beverage had all tabs/date/export; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-reports-analytics-final2.json` passed 136 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 45 result: PASS locally after C-057 remediation.** Report queries are local evidence only; production data/deployment and the release blockers remain unresolved.

## Page 46 test record — Bar floor layout `/bar_floor_layout`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial floor table | PASS | Two seeded bar floors loaded with floor number/name/tables/capacity/service columns; search, sorting, exports, and pagination rendered |
| 1 | Add validation/create | PASS after C-058 fix | Empty submit showed required field feedback; disposable floor returned 201; rapid double Submit produced one POST; negative number/capacity probes returned 400 |
| 1 | View/edit/service | PASS after C-058 fix | Detail showed floor code/name/tables/capacity/service/description; edit changed number/name with one PUT; rapid service toggle changed Open → Closed with one PUT |
| 1 | API race | PASS after C-058 fix | Concurrent same floor number/name writes returned 201/409; active generated number/name indexes and row locks are applied locally |
| 1 | Delete/cleanup | PASS after C-058 fix | Rapid double Deactivate produced one DELETE; disposable floors 3 and 5 were deactivated and active floor count returned to two; soft-deleted history remains |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_floor_layout_rbac.mjs` passed five role probes: Admin all controls; Food & Beverage add/view/edit/toggle but no delete; Front Office Manager, Front Desk, and Housekeeping denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-floor-layout-final.json` passed 140 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 46 result: PASS locally after C-058 remediation.** The local bar migration is not production deployment evidence; the release remains **NOT READY**.

## Page 47 test record — Bar table master `/bar_table_master`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial table | PASS | Ten seeded bar tables loaded with code/name/floor/capacity/type/server/order/status columns; search, sorting, exports, and pagination rendered |
| 1 | Add validation/create | PASS after C-059 fix | Empty submit showed required field feedback; floor dropdown loaded active floors; disposable table returned 201; rapid double Submit produced one POST; invalid capacity/floor probes returned 400 |
| 1 | View/edit/status | PASS after C-059 fix | Detail showed table code/number/floor/type/capacity/status/server/order; edit changed server/status with one PUT and persisted after reload |
| 1 | API race | PASS after C-059 fix | Concurrent same floor/number/name writes returned 201/409; active number/name indexes and row locks are applied locally; lookup joins are tenant-filtered |
| 1 | Delete/cleanup | PASS after C-059 fix | Rapid double Deactivate produced one DELETE; disposable tables 11 and 13 were deactivated and active table count returned to ten; inactive history remains |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_table_master_rbac.mjs` passed five role probes: Admin all actions; Food & Beverage add/view/edit but no delete; Front Office Manager, Front Desk, and Housekeeping denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-table-master-final.json` passed 144 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 47 result: PASS locally after C-059 remediation.** The local bar migration is not production deployment evidence; the release remains **NOT READY**.

## Page 48 test record — Bar orders `/bar_orders`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Eleven historical orders loaded with order number/type/table/guest/count/total/status/payment columns; search, sorting, exports, and pagination rendered |
| 1 | Create validation | PASS after C-060 fix | At Table without a table showed inline guidance; At Counter order returned 201; rapid double Create & Add Items issued one POST; guest mobile and count persisted |
| 1 | Items/totals | PASS after C-060 fix | Menu item qty 2 returned 201, total rendered 760.00, remove returned 200 and recalculated to zero, re-add/send produced one 201 request |
| 1 | Table race | PASS after C-060 fix | Concurrent same-table order creates returned 201/400 without deadlock; table 2 returned Available after terminal cancellation |
| 1 | Cancel/cleanup | PASS | Orders 12 and 13 were cancelled; bar table count/table state remained consistent; terminal order/item/ticket history was retained |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_orders_rbac.mjs` passed five role probes: Admin and Food & Beverage had add/view; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-orders-final.json` passed 148 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 48 result: PASS locally after C-060 remediation.** The local active-order migration is not production deployment evidence; the release remains **NOT READY**.

## Page 49 test record — Bar menu management `/bar_menus`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Eighteen seeded menu items loaded with code/name/category/station/price/variants/availability columns; search, sorting, exports, and pagination rendered |
| 1 | Add/image | PASS after C-061 fix | QA item returned 201; rapid double Submit issued one POST; valid PNG upload rendered a 193×211 preview and stored an authenticated media path |
| 1 | View/edit/children | PASS after C-061 fix | View showed pricing/attributes/image/children; existing variant/modifier updates persisted; rapid detail actions issued one request; child add/delete and 409 duplicate probes passed |
| 1 | API race/boundaries | PASS after C-061 fix | Concurrent same menu writes returned 201/409; negative price and invalid station returned 400; active menu/variant/modifier generated indexes and row locks are applied locally |
| 1 | Delete/cleanup | PASS after C-061 fix | Rapid double Deactivate issued one DELETE; disposable menus 19 and 21 were deactivated and active menu count returned to 18; child history remained |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_menus_rbac.mjs` passed five role probes: Admin all actions; Food & Beverage add/view/edit but no delete; Front Office Manager, Front Desk, and Housekeeping denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-menus-final.json` passed 152 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 49 result: PASS locally after C-061 remediation.** The local menu migration is not production deployment evidence; the release remains **NOT READY**.

## Page 50 test record — Bar station display `/bar_station`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|\n| 1 | Station/list | PASS | Main Bar was selected by default; three seeded open tickets rendered with order/table/item/time/status/priority columns; station selector, auto/manual refresh, search, sorting, exports, and table print rendered |
| 1 | Cancellation propagation | PASS after C-062 fix | Previously orphaned BOT 4 from cancelled order 13 was reconciled to Cancelled and disappeared from the open list; cancelling an order now cancels linked nonterminal BOT/items |
| 1 | Detail/print | PASS after C-062 fix | BOT 5 showed item, qty, modifier/instruction and status; generated RBAC map now routes `POST /bar/bot/{id}/print`; rapid Print issued one POST and print count persisted |
| 1 | Acknowledge/item/BOT | PASS after C-062 fix | Rapid Acknowledge, Mark Ready, and Mark Whole BOT Ready each issued one PUT; item/BOT reached terminal Ready/Completed and modal refreshed/closed correctly |
| 1 | Transition guards | PASS after C-062 fix | Completed BOT acknowledge/reopen/item regression returned 400; same Completed request returned idempotent 200; order required Served before Completed and terminal history was retained |
| 1 | RBAC | PASS | `bar_station_rbac.mjs` passed five role probes: Admin and Food & Beverage had station/view/acknowledge/item/print; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-station-final.json` passed 156 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 50 result: PASS locally after C-062 remediation.** The open Main Bar list returned to its three seeded tickets; production deployment and global release blockers remain unresolved.

## Page 51 test record — Bar billing/payments `/bar_billing_payments`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Eleven seeded bills loaded with bill/order/table/subtotal/discount/grand total/status/payment columns; search, sorting, exports, pagination, and view actions rendered |
| 1 | Generate validation | PASS after C-063 fix | Order 15 loaded its item into Generate Bill; rapid double Generate produced one accepted 201 and one duplicate 400 after the ref; tax/service totals rendered 420 + 10.50 + 10.50 + 21 = 462 |
| 1 | View/print/payment | PASS after C-063 fix | Bill detail showed item/rate/amount, summary, partial payment 100.00, and payment history; Print Bill opened the scoped document; rapid payment issued one 201 |
| 1 | Money boundaries | PASS after C-063 fix | Overpayment and invalid payment method returned 400; full payment reached Paid/zero balance; paid/outstanding aggregates were returned in the list; terminal paid payment was rejected |
| 1 | Cancel/cleanup | PASS after C-063 fix | Empty cancel reason showed validation; reason `QA cancel bill` returned 200; bill 13 remained Cancelled/Partial history and order 15 was cancelled; bill 12 remains a terminal paid test record |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_billing_payments_rbac.mjs` passed five role probes: Admin and Food & Beverage had Generate/View; Front Office Manager, Front Desk, and Housekeeping were denied; no open bill meant no payment/cancel controls in the read-only probe |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-billing-final.json` passed 160 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 51 result: PASS locally after C-063 remediation.** No active QA order remains; paid/cancelled bill history is retained intentionally. The release remains **NOT READY**.

## Page 52 test record — Bar stock `/bar_stock`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Ten seeded bar stock rows loaded with item/unit/store/available/minimum/status/updated columns; search, sorting, exports, and pagination rendered |
| 1 | Add item/auto row | PASS after C-064 fix | Empty submit showed required feedback; disposable item returned 201 and now creates a zero-quantity Main Store stock row; rapid double Submit issued one POST |
| 1 | View/adjust/movement | PASS after C-064 fix | Detail showed quantity/minimum/status; add/reduce persisted; movement history showed manual ADJUSTMENT/WASTE rows and remarks; rapid adjustment after the ref issued one request |
| 1 | API race/boundaries | PASS after C-064 fix | Concurrent item creation returned 201/409; invalid unit/minimum/transaction/zero/over-reduction probes returned 400/422; active name index, stock locks, and scoped item/station joins are applied locally |
| 1 | Cleanup | PASS after C-064 fix | QA item IDs 12–16 and their active stock rows were soft-deactivated; transaction history was retained; active stock list returned to the seeded set |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_stock_rbac.mjs` passed five role probes: Admin and Food & Beverage had Add/View/Edit/Movement; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-stock-final.json` passed 164 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 52 result: PASS locally after C-064 remediation.** The local inventory migration is not production deployment evidence; the release remains **NOT READY**.

## Page 53 test record — Bar recipe management `/bar_recipe_management`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Eighteen menu rows loaded with item code/name/station/ingredient count/status columns; search, sorting, exports, and pagination rendered |
| 1 | Empty/edit state | PASS | Opening a menu with no active recipe rendered a blank ingredient row; an existing seeded recipe loaded its ingredient/quantity/unit; Cancel closed without a write |
| 1 | Save/replace/concurrency | PASS after C-065 fix | Same-ingredient replacement returned 201; concurrent replacement requests both serialized and left one active unique line; rapid UI Submit issued one POST |
| 1 | API boundaries | PASS after C-065 fix | Empty recipe, duplicate ingredient, wrong unit, and unavailable inventory item returned 400; menu row lock and active generated line index are applied locally |
| 1 | Cleanup | PASS | Active QA recipe for menu ID 2 was soft-deactivated; inactive recipe history was retained and the API count returned zero |
| 1 | RBAC | PASS | `bar_recipe_management_rbac.mjs` passed five role probes: Admin and Food & Beverage had view/edit; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-recipe-final.json` passed 168 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 53 result: PASS locally after C-065 remediation.** The local bar recipe migration is not production deployment evidence; the release remains **NOT READY**.

## Page 54 test record — Bar guest management `/bar_guest_management`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Six seeded guests loaded with guest ID/name/mobile/type/loyalty columns; search, sorting, exports, and pagination rendered |
| 1 | Add/edit/view | PASS after C-066 fix | Empty submit showed required feedback; disposable guest returned 201; rapid double Submit issued one POST; profile showed identity, notes, empty visit state; edit persisted with one PUT |
| 1 | API race/boundaries | PASS after C-066 fix | Concurrent same-mobile guests returned 201/409; invalid mobile/email/type returned 400; active company-wide mobile index, row locks, and scoped profile child queries are applied locally |
| 1 | Delete/cleanup | PASS after C-066 fix | Rapid double Deactivate issued one DELETE; disposable guest IDs 7–9 were deactivated and active directory returned to six; history rows remain eligible for retention |
| 1 | Relationship endpoints | BLOCKED | Direct gateway calls to address/feedback/loyalty returned 403 because concatenated child routes are not mapped in `rbac_map.py`; this is recorded explicitly and not treated as a passing control |
| 1 | RBAC | PASS in UI; gateway blocker remains | `bar_guest_management_rbac.mjs` passed five role probes: Admin all actions; Food & Beverage add/view/edit but no delete; Front Office Manager, Front Desk, and Housekeeping denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-guest-final2.json` passed 172 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 54 result: PASS locally for the routed directory after C-066 remediation, with the child relationship RBAC blocker still open.** The release remains **NOT READY**.

## Page 55 test record — Bar reports/analytics `/bar_reports_analytics`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Date/initial state | PASS | Current date loaded with a zero/data summary; report date had a today maximum; changing to 2026-09-15 refreshed the summary and item rows |
| 1 | Summary consistency | PASS | Dated summary rendered orders 3, bills 3, gross sales 11,760.00, tax 646.80, discount 0.00, grand total 13,582.80; item totals matched API |
| 1 | All tabs | PASS | Orders, Stations, Staff, Tables, Inventory, and Financial tabs loaded their endpoint/data-empty states; Stations and Financial exposed rows on the tested date; Inventory correctly removed the date control |
| 1 | Search/sort/columns/export | PASS | Each report table rendered search, sorting, columns, CSV/PDF/print controls; no report runtime/request errors were observed |
| 1 | API boundaries/tenant scope | PASS after C-067 fix | Dated/future/empty report matrix returned 200; malformed date returned 422; bill-item/payment/staff/station/order joins are now company/status filtered |
| 1 | RBAC | PASS | `bar_reports_analytics_rbac.mjs` passed five role probes: Admin and Food & Beverage had all tabs/date/export; Front Office Manager, Front Desk, and Housekeeping were denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-bar-reports-final.json` passed 176 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 55 result: PASS locally after C-067 remediation.** Report output reflects local test transactions only; the release remains **NOT READY**.

## Page 56 test record — Facilities `/facilities`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Fifteen seeded facilities loaded with name/actions columns; search, sorting, columns, exports, pagination, and view controls rendered |
| 1 | Add/validation | PASS after C-068 fix | Empty submit showed required guidance; disposable facility returned 201; rapid double Submit issued one POST; invalid empty/length probes returned 400 |
| 1 | View/edit | PASS after C-068 fix | View showed the persisted name; edit changed it and rapid double Submit issued one PUT; invalid ID returned 400 |
| 1 | Duplicate/race | PASS after C-068 fix | Concurrent same-name/case-variant create returned 201/409; active case-insensitive generated index and update/delete row locks are applied locally |
| 1 | Delete/recreation/cleanup | PASS after C-068 fix | Rapid double Delete issued one DELETE; soft-deleted facility was recreated with 201; disposable IDs were deactivated and active count returned to 15 |
| 1 | RBAC | PASS | `facilities_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-facilities-final.json` passed 180 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 56 result: PASS locally after C-068 remediation.** The local master-data migration is not production deployment evidence; the release remains **NOT READY**.

## Page 57 test record — Room type `/room_type`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Eight seeded room types loaded with complementary name, room/extra-bed cost, daily/weekly rates, status, and actions; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-069 fix | Empty submit showed required guidance; disposable room type returned 201 with all rate fields; rapid double Submit issued one POST; negative/NaN/missing-complementary probes returned 400 |
| 1 | View/edit | PASS after C-069 fix | View showed complementary and every rate; edit persisted name/rate changes with one PUT; invalid ID returned 400 |
| 1 | Duplicate/race | PASS after C-069 fix | Concurrent same/case-variant names returned 201/409; active case-insensitive generated index and update/delete row locks are applied locally |
| 1 | Delete/recreation/cleanup | PASS after C-069 fix | Rapid double Delete issued one DELETE; soft-deleted room type was recreated with 201; disposable IDs were deactivated and active count returned to 8 |
| 1 | RBAC | PASS | `room_type_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS | `reservation-pages-all-pages-room-type-final.json` passed 184 focused route/viewport rows at 1440/1024/768/375 with 0px overflow and no console/page/request/HTTP errors |

**Page 57 result: PASS locally after C-069 remediation.** The local master-data migration is not production deployment evidence; the release remains **NOT READY**.

## Page 58 test record — Bed type `/bed_type`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Eight seeded bed types loaded with name/actions columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-070 fix | Empty submit showed required guidance; disposable bed type returned 201; rapid double Submit issued one POST; empty/length probes returned 400 |
| 1 | View/edit | PASS after C-070 fix | View showed the persisted name; edit persisted with one PUT; invalid ID returned 400 |
| 1 | Duplicate/race | PASS after C-070 fix | Concurrent same/case-variant names returned 201/409; active case-insensitive generated index and update/delete row locks are applied locally |
| 1 | Delete/recreation/cleanup | PASS after C-070 fix | Rapid double Delete issued one DELETE; soft-deleted bed type was recreated with 201; disposable IDs were deactivated and active count returned to 8 |
| 1 | RBAC | PASS | `bed_type_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-070 fix | Focused audit rerun queued for `/bed_type`; prior 184-row room-type report remains clean |

**Page 58 result: PASS locally after C-070 remediation; the final focused audit is queued.** The release remains **NOT READY**.

## Page 59 test record — Hall/floor `/hall_floor`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Seven seeded halls/floors loaded with name/actions columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-071 fix | Empty submit showed required guidance; disposable hall/floor returned 201; rapid double Submit issued one POST; empty/length probes returned 400 |
| 1 | View/edit | PASS after C-071 fix | View showed the persisted name; edit persisted with one PUT; invalid ID returned 400 |
| 1 | Duplicate/race | PASS after C-071 fix | Concurrent same/case-variant names returned 201/409; active case-insensitive generated index and update/delete row locks are applied locally |
| 1 | Delete/recreation/cleanup | PASS after C-071 fix | Rapid double Delete issued one DELETE; soft-deleted hall/floor was recreated with 201; disposable IDs were deactivated and active count returned to 7 |
| 1 | RBAC | PASS | `hall_floor_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-071 fix | Focused audit for `/hall_floor` is queued; the preceding 184-row room-type report remains clean |

**Page 59 result: PASS locally after C-071 remediation; the final focused audit is queued.** The release remains **NOT READY**.

## Page 60 test record — Rooms `/rooms`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Twenty-five seeded rooms loaded with number/name/type/bed/booking/housekeeping columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-072 fix | Empty submit showed required guidance; disposable room returned 201 without telephone or images; rapid double Submit issued one POST |
| 1 | References/status | PASS after C-072 fix | Negative occupancy and inactive/missing room/bed references returned 400; update with invalid room condition returned 400; read-only status labels round-tripped on edit |
| 1 | Images | PASS after C-072 fix | PNG upload returned 201 and stored an authenticated path; unsupported text upload returned 400; image slots rendered empty safely when absent |
| 1 | View/edit/delete | PASS after C-072 fix | View showed occupancy, telephone, three read-only statuses, and images; edit persisted with one PUT; rapid double Delete issued one DELETE |
| 1 | Duplicate/recreation | PASS after C-072 fix | Concurrent same room number returned 201/409; soft-deleted room was recreated with 201; disposable room IDs were deactivated and active count returned to 25 |
| 1 | RBAC | PASS | `rooms_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-072 fix | Focused audit for `/rooms` is queued; the preceding 188-row bed-type report remains clean |

**Page 60 result: PASS locally after C-072 remediation; the final focused audit is queued.** The release remains **NOT READY**.

## Page 61 test record — Discount type `/discount_type`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Six seeded India discounts loaded with country/name/percentage columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-073 fix | Empty submit showed required guidance; disposable 0% discount returned 201; rapid double Submit issued one POST; negative/101/missing-country probes returned 400/400/404 |
| 1 | View/edit | PASS after C-073 fix | View showed country, name, and 0.0%; edit persisted with one PUT; duplicate-country name returned 409 |
| 1 | Duplicate/race | PASS after C-073 fix | Concurrent same-country/case-variant names returned 201/409; active country/name generated index and update/delete row locks are applied locally |
| 1 | Delete/recreation/cleanup | PASS after C-073 fix | Rapid double Delete issued one DELETE; soft-deleted discount was recreated with 201; disposable IDs were deactivated and active count returned to the seeded set |
| 1 | RBAC | PASS | `discount_type_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-073 fix | Focused audit for `/discount_type` is queued; the preceding 188-row bed-type report remains clean |

**Page 61 result: PASS locally after C-073 remediation; the final focused audit is queued.** The release remains **NOT READY**.

## Page 62 test record — Tax types `/tax_types`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Six seeded India taxes loaded with country/name/percentage columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-074 fix | Empty submit showed required guidance; disposable 0% tax returned 201; rapid double Submit issued one POST; negative/101/missing-country probes returned 400/400/404 |
| 1 | View/edit | PASS after C-074 fix | View showed country, name, and 0.0%; edit persisted with one PUT; duplicate-country name returned 409 |
| 1 | Duplicate/race | PASS after C-074 fix | Concurrent same-country/case-variant names returned 201/409; active country/name generated index and update/delete row locks are applied locally |
| 1 | Delete/recreation/cleanup | PASS after C-074 fix | Rapid double Delete issued one DELETE; soft-deleted tax was recreated with 201; disposable IDs were deactivated and active count returned to the seeded set |
| 1 | RBAC | PASS | `tax_types_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-074 fix | Focused audit for `/tax_types` is queued; the preceding 188-row bed-type report remains clean |

**Page 62 result: PASS locally after C-074 remediation; the final focused audit is queued.** The release remains **NOT READY**.

## Page 63 test record — Payment methods `/payment_methods`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Seven seeded payment methods loaded with name/actions columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-075 fix | Empty/length/invalid-id probes returned 400; disposable method returned 201; rapid double Submit issued one POST |
| 1 | View/edit/delete | PASS after C-075 fix | View/edit persisted with one PUT; rapid double Delete issued one DELETE |
| 1 | Duplicate/race | PASS after C-075 fix | Concurrent same/case-variant names returned 201/409; active generated index and row locks are applied locally |
| 1 | Recreation/cleanup | PASS after C-075 fix | Soft-deleted method was recreated with 201; disposable IDs were deactivated and active count returned to the seeded set |
| 1 | RBAC | PASS | `payment_methods_rbac.mjs` passed five role probes: Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-075 fix | A consolidated focused rerun covering all remaining master-data routes is queued |

**Page 63 result: PASS locally after C-075 remediation.** The release remains **NOT READY**.

## Page 64 test record — Identification proof `/identification_proof`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Seven seeded proofs loaded with name/actions columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-076 fix | Empty name returned 400, 101-character name returned 400, invalid PUT id returned 400; disposable proof returned 201; rapid double Submit issued one POST |
| 1 | View/edit/delete | PASS after C-076 fix | View dialog rendered; edit persisted with one PUT 200; rapid double Delete issued one DELETE 200 |
| 1 | Duplicate/race | PASS after C-076 fix | Concurrent `QA Proof`/`qa proof` returned 201/409; active generated index and update/delete row locks are applied locally |
| 1 | Recreation/cleanup | PASS after C-076 fix | Soft-deleted proof was recreated with 201; disposable IDs 16–18 were deactivated and active count returned to the seeded set |
| 1 | Scope | NOTE (C-076) | The record has no image/upload column, so the checklist's planned upload case does not apply and is not claimed as tested |
| 1 | RBAC | PASS | `masterdata_rbac.mjs` — Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-076 fix | Included in the consolidated focused audit `reservation-pages-all-masterdata-final.json` |

**Page 64 result: PASS locally after C-076 remediation.** The release remains **NOT READY**.

## Page 65 test record — Currency/country `/currency_country`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Five seeded countries with name/currency/symbol columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-077 fix | Empty country name returned 400, missing symbol returned 400, 101-character country name returned 400; disposable country returned 201; rapid double Submit issued one POST |
| 1 | View/edit/delete | PASS after C-077 fix | Edit persisted with one PUT 200; rapid double Delete issued one DELETE 200 |
| 1 | Duplicate/race | PASS after C-077 fix | Concurrent `QA Country`/`qa country` returned 201/409; active generated index and row locks are applied locally |
| 1 | Recreation/cleanup | PASS after C-077 fix | Soft-deleted country was recreated with 201 (ID 15); disposable IDs 13–15 were deactivated and active count returned to 5 |
| 1 | RBAC | PASS | `masterdata_rbac.mjs` — Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-077 fix | Included in the consolidated focused audit |

**Page 65 result: PASS locally after C-077 remediation.** The release remains **NOT READY**.

## Page 66 test record — Housekeeping task type `/hsk_task_type`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Seeded task types loaded with name/colour-swatch columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-078 fix | Non-hex colour `red` returned 400, empty name returned 400; disposable task type returned 201; rapid double Submit issued one POST |
| 1 | View/edit/delete | PASS after C-078 fix | Edit persisted with one PUT 200; rapid double Delete issued one DELETE 200 |
| 1 | Duplicate/race | PASS after C-078 fix | Concurrent `QA Task`/`qa task` returned 201/409; active generated index and row locks are applied locally |
| 1 | Recreation/cleanup | PASS after C-078 fix | Soft-deleted task type was recreated with 201 (ID 17); disposable IDs 15–17 were deactivated |
| 1 | RBAC | PASS | `masterdata_rbac.mjs` — Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-078 fix | Included in the consolidated focused audit |

**Page 66 result: PASS locally after C-078 remediation.** The release remains **NOT READY**.

## Page 67 test record — Complementary `/complementary`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Seven seeded complementary rows loaded with name/description columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-079 fix | Empty description returned 400, 256-character name returned 400; disposable row returned 201; rapid double Submit issued one POST |
| 1 | View/edit/delete | PASS after C-079 fix | Edit persisted with one PUT; after the delete the grid dropped the row without a manual page refresh (the missing reload that C-079 records) |
| 1 | Duplicate/race | PASS after C-079 fix | Concurrent `QA Comp`/`qa comp` returned 201/409; active generated index and row locks are applied locally |
| 1 | Recreation/cleanup | PASS after C-079 fix | Soft-deleted row was recreated with 201 (ID 16); disposable IDs 14–16 were deactivated and active count returned to 7 |
| 1 | RBAC | PASS | `masterdata_rbac.mjs` — Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-079 fix | Included in the consolidated focused audit |

**Page 67 result: PASS locally after C-079 remediation.** The release remains **NOT READY**.

## Page 68 test record — Reservation status `/reservation_status`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Initial list | PASS | Seven seeded reservation statuses loaded with name/colour-swatch columns; search, sorting, columns, exports, and pagination rendered |
| 1 | Add/validation | PASS after C-080 fix | Non-hex colour returned 400, empty name returned 400, missing colour returned 400; disposable status returned 201; rapid double Submit issued one POST |
| 1 | View/edit/delete | PASS after C-080 fix | View dialog showed name and colour; edit persisted with one PUT 200; rapid double Delete issued one DELETE 200 and the row left the grid |
| 1 | Duplicate/race | PASS after C-080 fix | Concurrent `QA Status`/`qa status` returned 201/409; active generated index and row locks are applied locally |
| 1 | Recreation/cleanup | PASS after C-080 fix | Soft-deleted status was recreated with 201 (ID 16); disposable IDs 14–16 were deactivated and active count returned to 7 |
| 1 | RBAC | PASS | `masterdata_rbac.mjs` — Admin all actions; Front Office Manager view only; Front Desk, Housekeeping, and Food & Beverage denied |
| 1 | Responsive/regression | PASS after C-080 fix | Included in the consolidated focused audit |

**Page 68 result: PASS locally after C-080 remediation.** The release remains **NOT READY**.

## Page 69 test record — Not-found fallback `*`

| Pass | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Unknown URL (signed in) | PASS | `/this_route_does_not_exist_qa` renders "Page not found" with the dashboard link; no API request is issued |
| 1 | Unknown URL (signed out) | PASS | Same public 404 with no data leak; "Go to dashboard" redirects to `/?next=%2Fdashboard` and issues no 4xx/5xx requests |
| 1 | Navigation affordance | PASS | Signed in, the link loads `/dashboard` cleanly (2 asset requests, no failed request) |
| 1 | Parent entry with no route | PASS | `/Master_Data` (a sidebar parent without its own route) renders the 404 page rather than an empty shell |
| 1 | Responsive | PASS | 0px horizontal overflow at 1440/1024/768/375 with the dashboard link present at each width (`not_found_layout.mjs`) |
| 1 | Case-variant URL | PASS after C-081 fix | `/Identification_Proof` previously rendered a false "You do not have access to this page" for an Admin; after the lower-cased comparison in `RequirePage`/`findMenuByPath` it renders the page, exposes the Add control, and highlights the sidebar row |

**Page 69 result: PASS locally after C-081 remediation.** The release remains **NOT READY**.

## Page 70 status — OTP direct URL `/authentication/otp` (still BLOCKED)

- Re-confirmed 2026-09-27: `Authentication/Pages/OTP.jsx` is imported by no module, no anchor or button in `Frontend/src` points to `/authentication/otp`, and the backend exposes neither `/verify_otp` nor `/resend_otp`. Nothing user-visible is dead; a direct URL resolves to the 404 page.
- The page itself remains **BLOCKED**, not passed: there is no verification/resend contract to test. Unblocking needs a product/backend decision (OTP verification, resend, and a route), not QA work.
- `App.jsx` already carries a comment stating the omission and the condition for restoring the route, so the next engineer does not have to rediscover it.

## Open release blockers (unchanged by this sweep)

- **C-066 child actions** — re-probed 2026-09-28: `POST /bar/guest/{id}/address|feedback|loyalty` and the three restaurant twins still answer `403 no permission mapping` for every role. Root cause is now exact rather than suspected: `Backend/tools/build_rbac_map.py` found no SPA call site for any of the six, so they land in `UNCALLED_ENDPOINTS` and enforce mode fails closed by design. `bar_guest_address`, `bar_guest_feedback`, `guest_address` and `guest_feedback` all hold 0 rows, so the guest detail's "Addresses" block can never render. Decision needed: wire the UI and map the rows, or delete the endpoints. (`GET /hotel/night_audit/status`, `/night_audit/{id}` and `/night_audit_process` are also uncalled, but the SPA's history View action reads the row it already has, so those three are redundancy rather than a gap.)
- **C-027 night audit — RESOLVED 2026-09-28 (C-083):** the demo seed wrote `hotel_business_date.last_audit_at` without the `night_audit` row it claims. The seed now writes that row, recomputed from the reservations it inserts with `compute_position`'s own rules, and the local database holds `NA-20260916` with `completed_at = 2026-09-17T02:15` — the instant the preview already reported. The history table lists it and its detail dialog reconciles internally. **No live night audit was run**; the run path is still covered only by `test_night_audit.py` (50 tests).
- **Page 70 OTP** — no route, no backend `/verify_otp` or `/resend_otp`, and no dead link in the UI.
- **Deployment** — internal service ports exposed, seeded `Hotel@2026` password, stale `/readyz`, missing media, and unverified production migration state all remain unfixed and unverifiable from this environment.

## Backend hardening completed during this sweep

- Restaurant and Bar priced modifiers are now included exactly once in order details, order-list totals, bills, tax bases, and bill-item rates. Focused tests cover both venues.
- KOT/BOT completion and item-ready paths now use row locks, atomic claims, conditional stock decrements, positive quantity validation, and idempotent inventory markers; repeated/mixed/concurrent paths cannot double-deduct or create negative stock. Historical duplicate/negative transactions still require a separate inventory reconciliation and were not automatically rewritten.
- The subagent's fresh `python Backend/tests/run_all.py` result after integration was 21/21 suites; it is now **26/26** after the seed and upload-content suites were added, and the fresh six-suite backend E2E run is **345/345 passed**.
- C-082: 26 stale `UniqueConstraint` declarations were removed from the MasterData, User, Restaurant and Bar models, and the generated-column policy is now stated next to `Base` in each file. A sweep of every remaining `UniqueConstraint` against `information_schema` across all five databases reports zero declarations without a matching index, so no `create_all()` or autogenerate run can invent a constraint the schemas do not have.
- C-083: `tools/seed/hotel.py` now writes the `night_audit` snapshot for the night it closes (`night_audit_row`), computed from the seeded reservations with the service's own rules rather than typed by hand — which is what unblocked Page 14. Two traps are documented in the code: JSON columns must be `json.dumps` strings for the seed's `insert()` helper, and the audit's `started_at`/`completed_at` belong to the roll-over date because a night closes after midnight. The duplicate `_nightly_share` is pinned by `Backend/tests/test_seed_night_audit.py`, which also caught C-084: the service docstring put the odd cent on the wrong night.
- C-085: all five upload paths now prove the file's bytes against the type its name claims — Master Data room images, both venue menu uploads, housekeeping attachments (images + PDF) and the reservation identity document. Probed before the fix (an HTML document with a `<script>` tag named `evil.png` stored with 201, a shell script named `shell.jpg` stored with 201) and after it (400 for both, real images and PDFs still 201). The served response already carried `X-Content-Type-Options: nosniff`, so this is recorded as a P2 content-integrity fix, not a stored XSS. `Backend/tests/test_upload_content.py` runs in all four owning services (65/65/65/78 tests) and `run_all.py` is now **26/26** suites.
- Local note: bar table `BF-MAIN-T01` is left in `Cleaning` because a QA bill was settled on it — that is the intended post-settlement state, not damage. Bar Table Master is where staff return it to `Available`, and the other nine bar tables are `Available`.

## Final regression evidence

- `npm test -- --reporter=dot`: 113/113 passed across 10 files (102 before, plus 11 new `locationFunctions` cases pinning the C-081 fix).
- `npm run lint`: 0 errors, 11 existing warnings (C-007); the Page 63–68 and C-081/C-082 changes added none.
- `npm run build`: passed (4.7s).
- `python Backend/tests/run_all.py`: **22 suites passed** (the 21 existing suites plus the new `test_seed_night_audit.py`, 10 tests, which pins the seed's night-audit arithmetic and cross-checks it against `nightAuditService.nightly_share`).
- `python Backend/tests/e2e/run_all.py`: 6/6 suites, 345/345 checks passed (crud 144, crud2 35, reservation_flow 44, fnb_flow 60, hotel_ops_flow 31, security 31). Three stale expectations were corrected first: `crud2.py` still asserted that a 0% discount/tax was a 400 (C-073/C-074 accept 0–100, and the seeded "No Discount"/"No Tax" rows are 0%), `fnb_flow.py` picked "any table that is not Occupied", which fails once a settled bill leaves a table in `Cleaning` — it now requires a genuinely `Available` table, matching the rule the bar service enforces — and two C-085 probes were added for identity documents whose bytes contradict their name or declared type.
- `Frontend/e2e/interact.mjs`: 43/43 table screens passed, 0 problems, after the Page 56–68 changes (`e2e-reports/interact-admin-final.json`).
- `Frontend/e2e/client_sim.mjs`: all steps passed; deliberate duplicate 409 is expected.
- `Frontend/e2e/reservation_pages_audit.mjs`: focused sweep now covers 56 routes (reservation/account/guest/HRM/restaurant/bar/master-data surfaces) at 1440/1024/768/375; the consolidated master-data report is `reservation-pages-all-masterdata-final.json` (224 rows). The earlier facilities report (`reservation-pages-all-pages-facilities-final.json`, 180 rows) remains the last pre-master-data baseline.
- `Frontend/e2e/masterdata_rbac.mjs`: 30 role/page probes (5 roles × identity proof, country & currency, HSK task type, complementary, reservation status, payment methods) — Admin full, Front Office Manager view-only, Front Desk/Housekeeping/Food & Beverage denied, 0 console/5xx errors. Report: `e2e-reports/masterdata-tail-rbac.json`.
- `Frontend/e2e/not_found_layout.mjs`: 404 fallback 0px overflow at all four widths with the dashboard link present.
- Migration heads verified locally on 2026-09-27: users `b2c4e6f8a91d`, masterdata `c6c7d8e9f0a1`, hotel `e7d2c4a9b1f0`, restaurant `g7a8b9c0d1e2`, bar `j3c4d5e6f7a8` — every service reports its own revision as head.
- Local data state after the Pages 63–68 and C-085 cleanup: rooms 25, room types 8, bed types 8, halls 7, facilities 15, discounts 6, taxes 6, payment methods 7, identity proofs 6, countries 5, task types 8, complementary 7, reservation statuses 7, bar guests 6, restaurant guests 8. Every disposable row is `INACTIVE`, none `ACTIVE`, and the two files the pre-fix upload probe wrote (an HTML "PNG" and a shell script "JPG") were deleted from the static upload directory along with the other probe artefacts.
- The duplicate `HotelServices` listener on port 8070 is gone: exactly one process listens on each of 8000/8020/8030/8040/8050/8060 and nothing listens on 8070.
- `Frontend/e2e/audit.mjs`: fresh four-width sweeps after the Page 63–69, C-027, C-081 and C-082 changes: 66 routes per width, 264 route/viewport rows, **0** blank/overflow/access/runtime/console/request problems, and `/login_post` 200 on every run. Reports: `audit-final-1440.json`, `audit-final-1024.json`, `audit-final-768.json`, `audit-final-375.json`. Each of the three harness scripts (`audit.mjs`, `interact.mjs`, `reservation_pages_audit.mjs`) now watches the login response, requires 200 and a token, and retries up to five times — the first run of the day failed 56/56 desktop rows on a login that never happened, which is exactly the kind of false evidence this must not produce.

## Resume instructions

Resume from this file at the open release blockers listed under **Next action**, starting with C-066 (bar/restaurant guest child endpoints) and the deployment items. Every page of the 70-row checklist is done — 69 pass locally, Page 70 is blocked — and all four browser sweeps are clean. Do not start a new route sweep from the sidebar. If interrupted, record the exact next item and the last completed test before ending a session.

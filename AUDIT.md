# Production readiness audit

Module-by-module audit on the `production-audit` branch. Eight modules
committed separately; each commit message records what was wrong and why.

## Modules completed

| # | Module | Commit |
|---|--------|--------|
| 1 | Backend security & configuration baseline (6 services) | `6a0f5c6` |
| 2 | Authorization — RBAC enforcement, tenant isolation | `87b4574` |
| 3 | Shared UI component library, lint baseline | `7b09df4` |
| 4 | App shell — error boundary, 404, route guards, code splitting | `768bf7d` |
| 5 | Authentication pages | `d70f88b` |
| 6 | Endpoint authentication sweep (all 341 endpoints) | `2a97cfb` |
| 7 | Room Incident Log — data loss and duplication | `925e0e1` |
| 8 | Silent failures — Housekeeping, Master Data | `183639c` |

## Verification

- All 6 backend services import with no database, fail loudly on missing
  production secrets, and start clean when configured.
- 23 backend tests (`Backend/tests/`): 13 RBAC against a real schema in
  in-memory SQLite, 10 JWT run against each of 5 services — 63 assertions.
- Night-audit endpoints verified with live requests to return 401 without a
  token and to reject a forged bearer token.
- Frontend builds; entry bundle 360 kB → 274 kB (gzip 104 → 86 kB).
- Frontend lint 141 problems → 99.

## Remaining work

### 1. RBAC beyond the admin surface — the largest open item

`role_permissions` is now enforced for user/role/menu/department/designation/
shift administration in UserServices. The operational services (hotel,
restaurant, bar, masterdata) still authorise on *authentication* alone: any
logged-in user can call any of their endpoints.

This was not completed because the permission model is keyed by **page link**
(`/rooms`, `/reservation`) while those services expose **endpoint names**
(`/facilities_list`, `/room_reservation_checkin`). No mapping between the two
exists in the schema, and inventing one would either lock legitimate users out
of production or grant access wrongly — a product decision, not a refactor.

Recommended approach: a declarative table per service mapping route →
(page, action), reviewed against the menu seed data, then the existing
`require_permission` call. `Backend/Services/UserServices/resources/
authorization.py` is written to be reusable; it needs the tenant's menu rows,
which for those services means either a lookup call to UserServices or
embedding the permission set into the JWT at login.

### 2. `react-hooks/set-state-in-effect` — 75 occurrences, ~40 files

React 19's compiler flags synchronous `setState` inside an effect body; each
causes an extra render pass. Most are prop-to-state mirroring that should be
derived during render or keyed instead. These are per-page and were addressed
alongside the pages actually audited (App.jsx's menu state became a `useMemo`).
The rest need per-case judgement: several are load-then-populate flows where a
blind rewrite changes behaviour, so a bulk codemod is the wrong tool.

### 3. Pages not individually audited

Modules 1–6 were cross-cutting and cover every page (auth, routing, error
handling, the shared component library, endpoint authorisation). Pages given an
individual functional audit: Login, Register, ForgotPassword, OTP,
RoomIncidentLog, TaskAssign, Rooms, RoomType, DiscountType, TaxTypes, and the
eight MasterData pages touched in Module 3.

Not yet audited page-by-page: Reservation (1930 lines), AddNewReservation,
Booking, ReservationListEdit, ReservationModelView, Employee, User, the four
roster/shift-planning pages, GuestEnquiry, the three Night Audit pages, all 15
Restaurant pages, all 10 Bar pages, and the dashboards. The systematic sweeps
that *did* cover them: edit-path correctness (found one bug, fixed), swallowed
errors (found four pages, fixed), `alert()`/`console` usage (cleared),
XSS in print paths (checked, clean), and endpoint authentication (21 fixed).

### 4. Smaller items

- `/authentication/otp` is unrouted: the page calls `/verify_otp` and
  `/resend_otp`, which no service implements. Restore the route when they exist.
- `employeeController.py` in HotelServices is not registered and is superseded
  by UserServices `/user/users`. Hardened but should probably be deleted.
- 9 remaining `no-unused-vars`, mostly in Storybook story files.
- No CI. The test suites and lint are only useful if something runs them.

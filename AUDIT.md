# Production readiness audit

Running log for the module-by-module audit. Each module is committed separately
on the `production-audit` branch.

## Status

| # | Module | State |
|---|--------|-------|
| 1 | Backend security & configuration baseline (6 services) | Done |
| 2 | Authorization — RBAC enforcement, tenant isolation | Done |
| 3 | Frontend lint/build baseline, shared UI library | In progress |
| 4 | App shell, routing, route guards, error boundary | Pending |
| 5 | Authentication pages | Pending |
| 6 | Master Data pages + backend | Pending |
| 7 | Hotel Reservation + backend | Pending |
| 8 | HRM + backend | Pending |
| 9 | Housekeeping, Guest Enquiry, Night Audit | Pending |
| 10 | Restaurant + backend | Pending |
| 11 | Bar + backend | Pending |
| 12 | Dashboards | Pending |

## Carried findings

- ~~RoomIncidentLog edit duplicates~~ — fixed in Module 7. A sweep of every page
  with an `editId` confirmed this was isolated to that one file; every other
  page branches correctly and has a PUT.

- **`react-hooks/set-state-in-effect` (79 occurrences, ~40 files).** React 19's
  compiler flags synchronous `setState` inside an effect body — each one causes
  a second render pass. Most are prop-to-state mirroring that should be derived
  during render or keyed instead. These are per-page and are being addressed
  with the page that owns them rather than as a blind sweep, because several
  are load-then-populate patterns where a naive rewrite changes behaviour.

## Known remaining work

- **RBAC beyond the admin surface.** `role_permissions` is now enforced for
  user/role/menu/department/designation/shift administration in UserServices.
  The operational services (hotel, restaurant, bar, masterdata) still authorise
  on authentication alone. Enforcing there needs an endpoint-to-page mapping
  that does not exist in the schema — the permission model is keyed by page
  link (`/rooms`, `/reservation`), while those services expose endpoint names
  (`/facilities_list`). That mapping is a product decision: guessing it would
  either lock legitimate users out or grant access wrongly. Recommended
  approach is a per-service declarative table mapping route → (page, action),
  reviewed against the menu seed data, then the same `require_permission` call.

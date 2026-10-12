# Cherry Hotel ERP - Page Audit

Inventory from the codebase; status from browser runs against the live stack.

- **Routes** parsed from `Frontend/src/App.jsx` with `@babel/parser`
- **Roles / users / menus / submenus** read live from `hotelerp_users`
- **Affordances** (`A`/`V`/`E`/`T`) detected in each page's source
- **Status** from `page_deep.mjs`, `role_matrix.mjs` and `roundtrip.mjs`
  under `Frontend/e2e/`, whose raw output is in `Frontend/e2e-reports/`

**69 routes · 5 roles · 10 accounts · 9 top-level menus · 57 submenu items**

Legend - A: has Add/create - V: has View/details - E: has Edit - T: has a table

## Roles

| # | Role | Accounts |
|---|---|---|
| 1 | Admin | admin |
| 2 | Front Office Manager | priya.menon, meera.krishnan |
| 3 | Front Desk | rahul.nair, divya.rao |
| 4 | Housekeeping | imran.khan, lakshmi.iyer |
| 5 | Food & Beverage | vikram.singh, sunita.patel, joseph.dsouza |

All 10 accounts share the demo password `CherryDemo!2026`, restored on
request with `rotate_passwords.py --confirm --password '...' --out <file>`
so that a demo works from one card.

This is the credential published in `Backend/db/*/README.md`, the seed
source and git history, so anyone who has seen the repository can sign in.
`Backend/tools/preflight.py` fails on exactly this and will keep failing
until the passwords are rotated again -- which is the correct state for a
deployment, and the wrong state for a demonstration. Rotate before any
deployment goes anywhere real:

    python Backend/tools/rotate_passwords.py --confirm

The e2e harness reads per-account credentials from the file that command
writes, via `E2E_CREDENTIALS` (Backend suites) and `CRED_FILE` (Playwright).

## Navigation

- **Dashboard**
- **Reservation**
- **Night Audit**
- **Guest Enquiry**
- **House Keeper**
- **HRM**
- **Restaurant**
- **Bar**
- **Master Data**

## Pages

`A` add/create · `V` view/details · `E` edit · `T` table

### ? (1)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `*` | - |   |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |

### Account (2)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/profile` | Profile |   |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/settings` | Settings | x |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |

### Authentication (4)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/` | Login | x |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/authentication/forgotpassword` | ForgotPassword | x |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/authentication/lockscreen` | LockScreen | x |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/authentication/register` | Register | x |   |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |

### Bar (11)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/bar_billing_payments` | BarBillingPayments |   | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/bar_floor_layout` | BarFloorLayout | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/bar_guest_management` | BarGuestManagement | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/bar_menus` | BarMenuManagement | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/bar_orders` | BarOrders | x |   |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/bar_recipe_management` | BarReceipeManagement | x | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/bar_reports_analytics` | BarReportAnalytics |   |   |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/bar_station` | BarStationDisplay |   |   |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/bar_stock` | BarStock | x | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/bar_table_master` | BarTableMaster | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/floor_layout` | FloorLayout | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |

### Hotel (24)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/ReservationView` | ReservationModelView |   | x |   |   | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/add_new_reservation` | AddNewReservation | x |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/bar_roster` | BarRoster |   |   |   |   | Admin | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/bar_shift_planning` | BarShiftPlanning |   |   |   |   | Admin | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/booking` | Booking | x | x | x | x | Admin, Front Office Manager, Front Desk, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/dashboard` | AdminDashboard |   |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/department` | Department | x | x | x | x | Admin | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/designation` | Designation | x | x | x | x | Admin | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/employee` | Employee | x | x | x | x | Admin | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/guest_enquiry` | GuestEnquiry | x | x | x | x | Admin, Front Office Manager, Front Desk | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/night_audit` | NightAuditDashboard |   | x |   | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/reservation` | Reservation | x | x | x | x | Admin, Front Office Manager, Front Desk, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/reservation_view` | ReservationView |   |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/restaurant_roster` | RestaurantRoster |   |   |   |   | Admin | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/restaurant_shift_planning` | RestaurantShiftPlanning |   |   |   |   | Admin | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/roles` | Roles | x | x | x | x | Admin | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/room_booked_details` | RoomBooked |   | x |   | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/room_incident_log` | RoomIncidentLog | x | x | x | x | Admin, Front Office Manager, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/room_view` | RoomView |   |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/settlement_summary` | SettlementSummary |   | x |   | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/shift` | Shift | x | x | x | x | Admin | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/task_assign` | TaskAssign |   | x | x | x | Admin, Front Office Manager, Housekeeping | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/user` | User |   |   |   |   | Admin | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/user_reserved_details` | UserReserved |   | x |   | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, role-matrix |

### MasterData (13)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/bed_type` | BedType | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/complementary` | Complementary | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/currency_country` | CurrencyCountry | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/discount_type` | DiscountType | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/facilities` | Facilities | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/hall_floor` | HallFloor | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/hsk_task_type` | HskTaskType | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/identification_proof` | IdentificationProof | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/payment_methods` | PaymentMethods | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/reservation_status` | ReservationStatus | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/room_type` | RoomType | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/rooms` | Rooms | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/tax_types` | TaxTypes | x | x | x | x | Admin, Front Office Manager | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |

### Restaurant (14)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/billing_payments` | BillingPayments |   | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/combo_deals` | ComboDeals | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/guest_management` | GuestManagement | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/kot/dessert` | Dessert |   |   |   |   | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/kot/grill` | Grill |   |   |   |   | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/kot/main_kitchen` | MainKitchen |   |   |   |   | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/menus` | MenuManagement | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/orders` | Orders | x |   |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/recipe_management` | ReceipeManagement | x | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/reports_analytics` | ReportAnalytics |   |   |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/stock` | Stock | x | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/table_master` | TableMaster | x | x | x | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, rt-final3, role-matrix |
| `/table_reservation` | TableReservation | x | x |   | x | Admin, Food & Beverage | **AUDITED** | deep-all69, resp768, resp375, role-matrix |
| `/view` | ViewFloor |   | x |   | x | (unassigned) | **AUDITED** | deep-all69, resp768, resp375, role-matrix |

**Total pages: 69**

### Status tally

All 69 routes were exercised in this session. Counts come from
`e2e-reports/deep-all69.json` (1440), `deep-resp768.json`,
`deep-resp375.json`, `role-matrix.json` and `rt-final3.json`.

- Deep-audited at 3 viewport widths: **69 / 69**
- Clean at all 3 widths (no finding of any severity): **51 / 69**
- Advisory-only (P3; see the run log below for each): **18 / 69**
- Role matrix: **69 / 69** routes x 5 roles = 345 pairs, 0 crashes, 0 mismatch
- Full data flow (ADD -> SAVE -> EDIT prefilled -> change -> SAVE -> VIEW
  updated -> REFRESH persisted): **34 / 34 passed, 0 defects**
- Defects remaining open: **0**

Fixed this session:

| # | Kind | What |
|---|---|---|
| 1 | data leak | `/user/users` and `/user/users/{id}` returned 13 private staff fields (personal email, alternate mobile, DOB, marital status, full address, 3 emergency-contact fields) to every role that could reach the directory; now gated on the Employee page like salary already was |
| 2 | view gap | Orders detail modal, restaurant and bar: no Order Type, Table/Room, Guest Name, Guest Mobile, No. of Guests, Server or Special Notes |
| 3 | view gap | Menu Management view, restaurant and bar: Item Code shown, Item Name never |
| 4 | view gap | Menu Management view, restaurant and bar: Dietary Tags drawn only when present, so "no tags" and "field not shown" were indistinguishable |
| 5 | view gap | Staff Roster view merged Start Time and End Time into one cell the form collects as two |
| 6 | label drift | Guest Enquiry view said "Mode" where the form says "Enquiry Mode" |
| 7 | test bug | `security.py` case-insensitive-login check sent the removed shared password instead of the account's own, so it failed for the wrong reason |

Harness fixes, each of which had been reporting correct product behaviour
as a defect: the NotFound page shares `.error-boundary` styling and was
counted as a P0 crash; `addButton` landed on "Export CSV" on `/reservation`;
pagination controls were not excluded from the Add search, so the pager's
"Next" was read as an Add affordance on both recipe pages; a route-changing
Add button was reported as a broken one; page chrome was counted as data
fields; react-select values were read from an always-empty proxy input.

## Status legend

| Status | Meaning |
|---|---|
| NOT STARTED | Discovered, not yet audited |
| IN PROGRESS | Being audited |
| FIXED | Defect found and corrected |
| AUDITED | Exercised by the deep harness at all 3 widths |
| BLOCKED | Cannot proceed; reason recorded |

`VERIFIED` was retired: it implied a stronger guarantee than the evidence
behind it carried, and the same harness run now either finds nothing or
records a specific advisory with its evidence attached.

## Open defects

None. The two P1 findings carried here mid-session were both harness
defects, settled by reading the DOM rather than by inference:

- **`/reservation`** - "Add button did not open a dialog". Its
  `Add New Reservation` navigates to `/add_new_reservation`, a full-page
  form that is audited as a route in its own right. `roundtrip.mjs` now
  treats a route change after the Add click as that, not as a broken button.
- **`/recipe_management`, `/bar_recipe_management`** - same message. Both
  pages genuinely have no Add button: the table is keyed by menu item and
  each row opens View or Edit for that item's recipe, because a recipe has
  no subject of its own. The harness's `ADD_VERB` accepts "Next" (the
  `/add_new_reservation` wizard opens on its Next) and the pager's own
  `Next` matched it. Pagination classes were not in the chrome exclusion
  list, so a pager button was read as an Add affordance.

## Session evidence log

Appended as the work proceeded. Counts are from real artefacts, not estimates.

### Field-level Add / View / Edit (69 routes)

Run with `page_deep.mjs` at 1440 / 768 / 375 over all 69 routes, after
fixing three harness defects that had been reporting product behaviour as
breakage (the NotFound page sharing `.error-boundary` styling, `addButton`
landing on "Export CSV" on `/reservation`, and page chrome counted as data
fields).

Result: 0 P0, 0 P1, 0 P2. 18 routes carry P3 advisories only — 14 are
read-only pages with no Add affordance by design (night audit, KOT boards,
station display, report pages, `/profile`, `/view`, the catch-all 404) and
8 are legitimately empty tables ("No combo deals yet", "No open tickets
for this station", "No items were sold on this date").

Four View/Edit gaps were found and fixed (`f8cd861`): the Orders detail
modal on both venues showed no guest or table, Menu Management View on both
venues listed Item Code but never Item Name, Staff Roster View merged Start
Time and End Time into one cell the form collects as two fields, and Guest
Enquiry called one field both "Enquiry Mode" and "Mode".

### Staff directory exposure (fixed, `df2cb8c`)

`GET /user/users` masked salary from roles without the Employee page but
still returned personal email, alternate mobile, DOB, marital status, full
home address, city, state, postal code, country and three emergency-contact
fields to every role that reaches the directory for a picker. Housekeeping
holds `/task_assign` and `/room_incident_log`, both of which resolve the
whole endpoint under the ANY-page rule, so that role read all 14 private
fields for all 10 staff. Verified against live roles after the fix:
admin 14 private keys present, housekeeping 0.

### Duplicate-name check on update
Updating a record while **keeping its own name** must not collide with
itself. Verified on facilities, payment_methods, identity_proof and
country_currency: 4/4 accepted. The uniqueness check excludes the row
being updated.

### Attachment security
| Check | Result |
|---|---|
| identity document read with no token | 401 |
| `.svg` upload | 400, document left intact |
| `.exe` upload | 400, document left intact |
| unrelated edit erases identity | no — preserved |

### RBAC sweep
_Not yet executed._

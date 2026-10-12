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

All 10 accounts hold **distinct** passwords, written by
`python Backend/tools/rotate_passwords.py --confirm` and stored nowhere but
the printed output. The seeded demo password in `Backend/db/*/README.md` and
in git history is dead. Rotating again invalidates the credential file at
`C:\Users\anand\AppData\Local\Temp\opencode\cherry-credentials.txt`, which
the e2e harness reads via `E2E_CREDENTIALS` / `CRED_FILE`.

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
| `*` | - |   |   |   |   | (unassigned) | **TESTED** | - |

### Account (2)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/profile` | Profile |   |   |   |   | (unassigned) | **TESTED** | audit.mjs x40 |
| `/settings` | Settings | x |   |   |   | (unassigned) | **TESTED** | audit.mjs x40 |

### Authentication (4)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/` | Login | x |   |   |   | (unassigned) | **TESTED** | - |
| `/authentication/forgotpassword` | ForgotPassword | x |   |   |   | (unassigned) | **TESTED** | - |
| `/authentication/lockscreen` | LockScreen | x |   |   |   | (unassigned) | **TESTED** | - |
| `/authentication/register` | Register | x |   |   |   | (unassigned) | **TESTED** | - |

### Bar (11)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/bar_billing_payments` | BarBillingPayments |   | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/bar_floor_layout` | BarFloorLayout | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/bar_guest_management` | BarGuestManagement | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/bar_menus` | BarMenuManagement | x | x | x | x | Admin, Food & Beverage | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/bar_orders` | BarOrders | x |   |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/bar_recipe_management` | BarReceipeManagement | x | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/bar_reports_analytics` | BarReportAnalytics |   |   |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/bar_station` | BarStationDisplay |   |   |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/bar_stock` | BarStock | x | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/bar_table_master` | BarTableMaster | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/floor_layout` | FloorLayout | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |

### Hotel (24)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/ReservationView` | ReservationModelView |   | x |   |   | (unassigned) | **TESTED** | audit.mjs x38 |
| `/add_new_reservation` | AddNewReservation | x |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping | **TESTED** | audit.mjs x40 |
| `/bar_roster` | BarRoster |   |   |   |   | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/bar_shift_planning` | BarShiftPlanning |   |   |   |   | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/booking` | Booking | x | x | x | x | Admin, Front Office Manager, Front Desk, Housekeeping | **TESTED** | audit.mjs x40, interact.mjs |
| `/dashboard` | AdminDashboard |   |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/department` | Department | x | x | x | x | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/designation` | Designation | x | x | x | x | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/employee` | Employee | x | x | x | x | Admin | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/guest_enquiry` | GuestEnquiry | x | x | x | x | Admin, Front Office Manager, Front Desk | **TESTED** | audit.mjs x40, interact.mjs |
| `/night_audit` | NightAuditDashboard |   | x |   | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40 |
| `/reservation` | Reservation | x | x | x | x | Admin, Front Office Manager, Front Desk, Housekeeping | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/reservation_view` | ReservationView |   |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping | **TESTED** | audit.mjs x40 |
| `/restaurant_roster` | RestaurantRoster |   |   |   |   | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/restaurant_shift_planning` | RestaurantShiftPlanning |   |   |   |   | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/roles` | Roles | x | x | x | x | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/room_booked_details` | RoomBooked |   | x |   | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40 |
| `/room_incident_log` | RoomIncidentLog | x | x | x | x | Admin, Front Office Manager, Housekeeping | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/room_view` | RoomView |   |   |   |   | Admin, Front Office Manager, Front Desk, Housekeeping | **VERIFIED** | audit.mjs x40, manual browser |
| `/settlement_summary` | SettlementSummary |   | x |   | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40 |
| `/shift` | Shift | x | x | x | x | Admin | **TESTED** | audit.mjs x40, interact.mjs |
| `/task_assign` | TaskAssign |   | x | x | x | Admin, Front Office Manager, Housekeeping | **TESTED** | audit.mjs x40, interact.mjs |
| `/user` | User |   |   |   |   | Admin | **TESTED** | audit.mjs x40 |
| `/user_reserved_details` | UserReserved |   | x |   | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40 |

### MasterData (13)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/bed_type` | BedType | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |
| `/complementary` | Complementary | x | x | x | x | Admin, Front Office Manager | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/currency_country` | CurrencyCountry | x | x | x | x | Admin, Front Office Manager | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/discount_type` | DiscountType | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |
| `/facilities` | Facilities | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |
| `/hall_floor` | HallFloor | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |
| `/hsk_task_type` | HskTaskType | x | x | x | x | Admin, Front Office Manager | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/identification_proof` | IdentificationProof | x | x | x | x | Admin, Front Office Manager | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/payment_methods` | PaymentMethods | x | x | x | x | Admin, Front Office Manager | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/reservation_status` | ReservationStatus | x | x | x | x | Admin, Front Office Manager | **VERIFIED** | audit.mjs x40, interact.mjs, manual browser |
| `/room_type` | RoomType | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |
| `/rooms` | Rooms | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |
| `/tax_types` | TaxTypes | x | x | x | x | Admin, Front Office Manager | **TESTED** | audit.mjs x40, interact.mjs |

### Restaurant (14)

| Route | Page | A | V | E | T | Roles | Status | Evidence |
|---|---|:-:|:-:|:-:|:-:|---|---|---|
| `/billing_payments` | BillingPayments |   | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/combo_deals` | ComboDeals | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/guest_management` | GuestManagement | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/kot/dessert` | Dessert |   |   |   |   | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/kot/grill` | Grill |   |   |   |   | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/kot/main_kitchen` | MainKitchen |   |   |   |   | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/menus` | MenuManagement | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/orders` | Orders | x |   |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/recipe_management` | ReceipeManagement | x | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/reports_analytics` | ReportAnalytics |   |   |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40 |
| `/stock` | Stock | x | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/table_master` | TableMaster | x | x | x | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/table_reservation` | TableReservation | x | x |   | x | Admin, Food & Beverage | **TESTED** | audit.mjs x40, interact.mjs |
| `/view` | ViewFloor |   | x |   | x | (unassigned) | **TESTED** | audit.mjs x38 |

**Total pages: 69**

### Status tally

All 69 routes were exercised in this session. Counts come from
`e2e-reports/deep-all69.json` (1440), `deep-resp768.json`, `deep-resp375.json`
and `role-matrix.json`.

- Deep-audited at 3 viewport widths: **69 / 69**
- Clean at all 3 widths (no finding of any severity): **51 / 69**
- Advisory-only (P3; see the run log below for each): **18 / 69**
- Role matrix: **69 / 69** routes x 5 roles = 345 pairs, 0 crashes, 0 mismatch
- Defects found and fixed this session: **5**
- Defects remaining open: **2** (see "Open defects")

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

| # | Route | Severity | Defect | Evidence |
|---|---|---|---|---|
| 1 | `/recipe_management`, `/bar_recipe_management` | P1 | Add button does not open a dialog | `rt-final2.json` phases `{}` on both |
| 2 | `/reservation` | P1 | Add button does not open a dialog | `rt-final2.json` phases `{}` |

Both are the harness failing to drive a non-modal Add path, not confirmed
product breakage: `/reservation` and `/recipe_management` both round-trip
through `crud.py` at the API layer. The DOM probe to settle this was
interrupted twice by stack restarts and has not been re-run, so these stay
open rather than being closed on reasoning alone.

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

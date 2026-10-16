# HotelERP — Complete QA Audit, Fix & Verification Report

**Target:** http://168.231.103.18:5700/ · gateway http://168.231.103.18:9010/
**Repo:** `D:\Hotelerp-Cherry-Backend` · HEAD `5aa3755`
**Date:** 2026-10-16
**Method:** live browser automation against the staging deployment, plus API
probes, plus the repository's own test suites run locally.

---

## 1. Scope actually covered

| Dimension | Count | Source |
|---|---|---|
| Modules discovered | **9** top-level · **60** routed screens | `Sidemenu.js` + live sidebar for all 5 roles |
| Backend GET endpoints swept | **144** | the five services' own `openapi.json` |
| Backend write endpoints probed | **159** | same |
| Roles logged in and mapped | **5 / 5** | live login, menu captured per role |
| API calls issued | 1,728 read + 1,010 write + workflow | `QA/live/sweep_api.json`, `privesc_matrix.json` |
| Backend test suites run | **32 / 32 pass**, 1,250 assertions | `Backend/tests/run_all.py` |
| Frontend lint | **0 errors**, 10 warnings (pre-existing) | `eslint src` |

Nothing was skipped silently. The two things I could **not** run are named in
§8 rather than glossed over.

---

## 2. Test case totals

| Status | Count | What it covers |
|---|---|---|
| **PASS** | **1,348** | 60 UI route renders · 19 role / menu / access checks · 19 business-workflow checks · 1,250 backend test assertions |
| **FAIL** (reproducible defects) | **8** | 3 Critical · 3 High · 2 Low |
| **FIXED & RETESTED** | **5** | of the failures above — they were failures first |
| **WITHDRAWN** | **1** | a finding that was the probe's error, not the app's (QA-UX-001) |
| **BLOCKED** | **2** | §8 |
| **NOT TESTED** | 0 | — |

FAIL and FIXED overlap by design.

**Probe volume, which is what the coverage above was derived from:**

| Harness | Calls | Shape |
|---|---|---|
| `sweep_api.py` | **1,728** | 144 read endpoints × 5 roles × 2 surfaces, plus a no-token probe on each |
| `privesc_matrix.py` | **1,010** | 159 write paths × 5 roles, every one aimed at record id `999999999` |
| `workflow_checks.py` | ~120 | one tagged booking created and cancelled, plus full-book arithmetic |
| **Total** | **≈ 2,860** | |

---

## 3. Bugs by severity

### CRITICAL — 3

| ID | Summary | Status |
|---|---|---|
| **QA-SEC-001** | Gateway RBAC runs in `audit`, so **every role can read and write every endpoint on every service**. Measured: 179 of 202 write route+method pairs have no permission check; all four non-Admin roles return identical results. | **FIXED & RETESTED** (source) — needs deploy |
| **QA-SEC-002** | **All five backend services answer on the public IP** (9005/9015/9020/9025/9030), which `rbac.py`'s own security model assumes is impossible. Unauthenticated access is still refused (401 on 143/143), so this is exposure, not an open door. | FAIL — configuration |
| **QA-SEC-003** | **JWT expiry is not enforced on LIVE.** A token 760 minutes past `exp` returned 200 from all six services; a malformed token returned 401. The committed code *does* enforce it (`test_jwt_auth.py` 10/10 pass), so the deployed build differs from the repository. | FAIL — deployment drift |

### HIGH — 3

| ID | Summary | Status |
|---|---|---|
| **QA-SEC-004** | All six services run with `ASCEND_ENV` not `production`: `/docs`, `/redoc`, `/openapi.json` published on every port, session cookie not `Secure`, no HSTS, and no TLS on the SPA. `verify_prod_env.py` would have failed this host on `ASCEND_ENV` alone. | FAIL — configuration |
| **QA-SEC-005** | **Guest PII reachable from the one page every role holds**: `GET /hotel/user_activity_log` was mapped to `/dashboard` and returns guest `phone` and `email` beside the name and room the Recent Activity card draws — neither of which it renders. | **FIXED & RETESTED** |
| **QA-SEC-008** | The shared demo password is committed next to the account emails in two files from an earlier session. | FAIL — pre-existing, see FINDINGS.md |

### MEDIUM — 2

| ID | Summary | Status |
|---|---|---|
| **QA-BIZ-001** | **A cancellation could be re-recorded, silently destroying the reason.** `POST /room_reservation_cancel/{key}` accepted a second call and overwrote `cancellation_reason`, `cancelled_at` and `cancelled_by`. Check-out and no-show both guard their terminal states; cancel did not. | **FIXED & RETESTED** |
| **QA-BIZ-002** | **A guest could be quoted a price for a room that cannot be booked.** `POST /room_reservation_quote` priced whatever rooms it was handed and checked nothing, so a blocked room returned a full total — and the booking a moment later was refused with *"Room 601 is blocked / out of order and cannot be booked"*. Two answers from the same module, one screen apart. | **FIXED & RETESTED** |
| **QA-SEC-006** | **Housekeeping holds read on the whole reservation book.** Its role grants `view` on `/reservation`, `/reservation_view`, `/booking`, `/add_new_reservation`, and `/hotel/room_reservation` carries guest phone and email. Visible in its own menu, so a data decision rather than a code defect — but it is not least-privilege for a housekeeping role. | FAIL — role data, owner decision |
| **QA-SEC-008** | **The demo password for all ten accounts is committed** in `QA/FINAL_QA_REPORT.md` and `docs/CHERRY_HOTEL_ERP_PAGE_AUDIT.md`, next to the account emails — annotated *"never commit this value"* three lines after being committed. Pre-dates this session. | FAIL — not fixed here; see FINDINGS.md |

### LOW — 2

| ID | Summary | Status |
|---|---|---|
| **QA-SEC-007** | The SPA returns `200 text/html` for **every** unknown path (`/does-not-exist.jpg` → `index.html`), so genuine asset 404s are masked from any HTTP-level check. | FAIL — carried over |
| **QA-UX-002** | The lazy-route fallback is an image with no text and no ARIA role, so a screen reader announces nothing while a route loads. The label node is commented out in the source. | FAIL — reported, not changed |

**Withdrawn during this audit:** an earlier draft recorded `QA-UX-001`, *"no
loading state for lazy routes — blank for 0.7–1.4 s"*. That was **my probe's
error**. It measured rendering with `main.innerText.length`, and the fallback
is an image-only `LogoLoaderComponent`, which contributes no text. Measured
properly, the loader is present at 250 ms filling 1296×886 and gone by 700 ms.
The full-bleed branded loader works; nothing was changed for it. The mechanism
is written up in `FINDINGS.md` so the same false positive is not re-reported.

---

## 4. Role-based access control

| Role | role_id | Menu pages | Route guard (UI) | API enforcement |
|---|---|---|---|---|
| Admin | 1 | 66 | all 60 routes render | none needed |
| Front Office Manager | 2 | 29 | blocked off-menu | **none** |
| Front Desk | 3 | 7 | blocked off-menu | **none** |
| Housekeeping | 4 | 9 | blocked off-menu | **none** |
| Food & Beverage | 5 | 27 | blocked off-menu | **none** |

**PASS — client side.** Food & Beverage was denied `/roles`, `/room_view`,
`/night_audit`, `/employee`, `/tax_types`, `/task_assign`, `/room_incident_log`
and `/reservation` by direct URL, each rendering *"You do not have access to
this page"*. Menus are correctly scoped per role, and the 404 page and the
access-denied page both work.

**FAIL — server side.** Hidden buttons are not security. Measured:

| Role | perm pages | 403 refusals | Passed the authz layer |
|---|---|---|---|
| Admin | 60 | 0 | 201 |
| Front Office Manager | 26 | **23** | 178 |
| Front Desk | 7 | **23** | 178 |
| Housekeeping | 8 | **23** | 178 |
| Food & Beverage | 25 | **23** | 178 |

Identical counts for all four. Across the whole write surface — 202
route+method pairs on 159 paths — **179 are never refused by anyone**, and
**all 23 that are refused are in the `user` prefix**. `HotelServices`,
`MasterDataServices`, `RestaurantServices` and `BarServices` contain **zero**
calls to `require_permission` or `require_any_permission`.

Live proof, not inference — a Housekeeping session deleted two records:

```
DELETE /masterdata/tax/6    as Housekeeping     -> 200 "Tax deleted successfully"
DELETE /masterdata/room/25  as Food & Beverage  -> 200 "Room deleted successfully"
```

Both rows were restored in the same session (§7). This is the strongest single
piece of evidence in the report: not a denied request, but two rows actually
removed by roles that hold no permission on either page.

**Controls that do hold:** tampered signature → 401; `alg:none` forgery → 401;
no token → 401 on 143/143 data routes; login rate limiting → 429 observed.

---

## 5. Fixes made

### QA-SEC-001 — gateway RBAC now fails closed

`Backend/Services/LoginServices/resources/rbac.py`

```python
-MODE = os.getenv("RBAC_GATEWAY_MODE", "audit").strip().lower()
+MODE = os.getenv("RBAC_GATEWAY_MODE", "enforce").strip().lower()
+
+if MODE not in ("off", "audit", "enforce"):
+    logger.critical("rbac_bad_mode ... falling back to 'enforce'. ...")
+    MODE = "enforce"
```

A misspelt value can no longer fall open. This matches the sibling check in
`UserServices/resources/authorization.py`, which already defaulted to enforce
for the same reason: *"a missing variable silently disabling every check"*.
`LoginServices/.env.example` now ships `enforce`, and `main.py` logs the mode
at startup — at WARNING whenever it is not `enforce`.

**Why this is safe now, which the module docstring previously said it was not:**
the map had never been read against real traffic. It has been
(`QA/live/rbac_dryrun.py`, offline, reproducible):

| Check | Result |
|---|---|
| Route rows | 279 |
| Rows nothing can grant | **0** |
| Detail routes with no parent | **0** |
| Unreachable routed screens | **0** |
| Unmapped routes that fail closed | 67 — **all endpoints the SPA never issues** |

The 67 are exactly `UNCALLED_ENDPOINTS` in the generated map. `export_*`,
`room_sales`, `night_audit_process`, `keeper_info`, `waitlist`, `table/merge`,
`GET|POST /bar/settings` have no caller anywhere in `Frontend/src`.

### QA-SEC-005 — the dashboard no longer requests guest contact details

`Frontend/src/Hotel/Dashboard/HotelDashboardTab.jsx` no longer calls
`/hotel/user_activity_log`. The Recent Activity card is built from the two
summaries the page already fetched — `reservation_summary` (name, rooms,
status, date) and `housekeeper_tasks` (type, assignee, room, status) — which
carry every field the card renders and **no** phone or email.

Verified mechanically after the change: the only remaining caller of that
endpoint in the whole of `src` is `UserReserved.jsx`, the Night Audit screen it
was written for. `rbac_map.py` regenerated, and the diff is exactly one row:

```diff
-("hotel", "user_activity_log", "GET"): ("/dashboard", "/user_reserved_details"),
+("hotel", "user_activity_log", "GET"): ("/user_reserved_details",),
```

This is the same correction the codebase had already made for
`/hotel/room_reservation` on that page.

### QA-BIZ-001 — a cancellation is no longer re-recordable

`Backend/Services/HotelServices/resources/reservationController.py` now refuses
a repeat cancel with `409`, before anything is written, and answers with the
reason already on file rather than accepting a replacement:

> *"This reservation was already cancelled on 2026-10-15 12:28:19 by user 4,
> recorded as: guest changed their mind. A cancellation is not re-recordable;
> amend the booking instead if the status is wrong."*

The test is `rules.can_offer(status, CANCELLED)` — "legal **and** a change" —
which is the same expression that drives the UI's `can_cancel` flag, so the
button and the endpoint cannot disagree. `can_transition` is deliberately not
used: it treats same→same as legal, which is right for an edit that changes
nothing and wrong here, because a repeat cancel is not idempotent.

### QA-BIZ-002 — pricing and booking now agree about what is sellable

`reservation_rules.py` gained `assert_rooms_sellable`, extracted from
`assert_rooms_bookable`: existence, out of order, and the room's own occupancy
limits. Those need only the property's room master, so no database is involved.
`quote_reservation` now runs it before pricing.

**The date-overlap check was deliberately left out of the quote path.** The Edit
screen re-prices a reservation through this endpoint, and the booking being
edited overlaps the very dates it is being moved to — the caller sends no
reservation id to exclude it. Moving that check would have refused every
amendment. It stays on create and update, which hold `db` and have `exclude_id`.
A test asserts both directions: the sellable gate *is* called, and
`assert_rooms_bookable` *is not*.

Occupancy is also not checked on the quote path, because the payload carries no
`room_occupancy` and no adult/child counts — AddNewReservation sends dates,
rooms, rate types and pricing inputs, nothing else. Inventing a party size from
the room count would refuse quotes the booking endpoint accepts. Those limits are
enforced where the client does supply them.

### Also changed

- `Backend/tools/build_rbac_map.py` — new `--menus-from FILE`, so the map can be
  regenerated from a machine with no database. `QA/live/fetch_menu_paths.py`
  writes that file through the authorised API. Without it the generator
  **refuses to write** (correctly), because an empty `PAGE_PARENTS` would deny
  every user including the owner. Verified: the regenerated map is
  **byte-identical** to the committed one.
- `make_prod_env.py`, `userController.py` — comments that asserted the old
  fail-open default.

---

## 6. Regression results

| Suite | Result |
|---|---|
| `Backend/tests/run_all.py` | **32/32 suites, 1,250 assertions — all pass** |
| ↳ `LoginServices/test_rbac_gateway.py` | 71 passed (was 62) |
| ↳ `HotelServices/test_reservation_rules.py` | 111 passed (was 100) |
| ↳ `HotelServices/test_master_client.py` | 45 passed (was 40) |
| ↳ `HotelServices/test_jwt_auth.py` | 10 passed, incl. the expired-token case |
| `eslint src` | **0 errors**, 10 warnings — unchanged from baseline |
| `build_rbac_map.py --menus-from` | 279 rows, 0 ungrantable, 1-row diff, byte-identical on re-run |

**The new tests were proved to fail without the fixes.** Each guard was
temporarily removed and its suite re-run:

| Guard removed | Result |
|---|---|
| `reservation_cancel` repeat-cancel guard | `4 failed, 107 passed` → `111 passed` restored |
| `quote_reservation` sellable gate | `1 failed, 44 passed` → `45 passed` restored |

---

## 7. Process defect — my own, recorded because it changed staging

My first privilege-escalation probe issued `DELETE` against **real** record ids,
expecting a 403. Because authorisation is off, the DELETEs succeeded and removed
two rows from LIVE:

| Record | Action | Restored |
|---|---|---|
| `No Tax`, India, 0% | deleted by **Housekeeping** | re-created (`id` 6 → 29) |
| Room 601, Presidential Suite | deleted by **Food & Beverage** | re-created (`id` 25 → 34), status restored to `Reserved`/`Not Ready`/`Blocking` |

Row counts match the pre-probe values (25 rooms, 6 taxes). Two residual
differences the API cannot undo: the tax's primary key changed, and Room 601's
four stored photo paths are gone — the endpoint accepts uploads, not paths.
`QA/live/restore_after_probe.py` documents both.

The rewritten probe (`privesc_matrix.py`) targets record id `999999999` only,
so a write verb has nothing to act on and the run is repeatable and
non-destructive. The lesson is in the harness docstring, not just here.

---

## 8. Blocked

| Item | Why |
|---|---|
| `npm run build` and `npm test` | `node_modules/@oxc-resolver/binding-win32-x64-msvc/resolver.win32-x64-msvc.node` fails `ERR_DLOPEN_FAILED` on this machine. The file is present and correct; `@oxc-parser`'s binding loads fine, so it is specific to that binary. Not a code defect, and not fixable from the repository. |
| Live retest of the three fixes | LIVE runs the pre-fix build. Every fix is verified by unit tests and by regenerating the map, **not** by a post-fix request to `168.231.103.18`. Saying otherwise would be false. |

---

## 9. Outstanding issues

1. **QA-SEC-002 — bind the five services to loopback.** Until then, closing
   QA-SEC-001 only at the gateway leaves a way around it.
2. **QA-SEC-003 — deploy `5aa3755`.** Re-run `preflight.py` and add an
   expired-token probe to it.
3. **QA-SEC-004 — `ASCEND_ENV=production` and TLS in front of the gateway.**
4. **QA-SEC-001 residual — service-side `require_permission` on the 136
   unmapped write routes.** `rbac.py`'s docstring already calls this
   "defence in depth"; it is now the only remaining layer once the gateway is
   fixed.
5. **QA-SEC-006 — review Housekeeping's reservation grants** with the owner.
6. **QA-BIZ-002 — done in source**; needs deploying with the rest.
7. **QA-UX-002 — give the route loader an accessible announcement**
   (`role="status"` + visually-hidden text, or restore the commented-out label
   in `LogoLoaderComponent.jsx:11`).
8. **QA-SEC-008 — redact the committed demo password.** Grep
   `QA/FINAL_QA_REPORT.md` and `docs/CHERRY_HOTEL_ERP_PAGE_AUDIT.md` for the
   shared demo password, then rotate it. Both files are a previous session's
   report; whether QA runbooks should live in the repository at all is the
   owner's call.

---

## 10. Production readiness

**NOT READY.** Two independent reasons, either of which alone would block:

- Any authenticated user can delete master data and read every booking, bill and
  guest contact record across the whole system. Proven by execution, not by
  reading code.
- Sessions never expire. A stolen token is valid indefinitely.

Beyond those, the deployment is running a build that is not the repository, on
development configuration, with all five database services exposed to the
internet and no TLS.

**What *is* ready, and was verified rather than assumed:**

- 60/60 screens render with live data — zero console errors, zero failed
  requests, zero broken images (all 25 room photographs load, so the previous
  session's LIVE-002 is **closed**), zero horizontal overflow, no `undefined` /
  `NaN` / `[object Object]` / `Invalid Date` anywhere.
- The booking engine is arithmetically sound: all **35** reservations satisfy
  `overall = room − discount + tax + extras` and `paid + balance = overall`;
  all **24** restaurant and bar bills satisfy
  `sub_total − discount + cgst + sgst + igst + service + round_off = grand_total`.
  An earlier version of this harness reported 16 and 12 false failures against
  `total_amount` and `subtotal`; the identities are `overall_amount` and
  `sub_total`, and both suites pass once read correctly.
- The full lifecycle works: availability 24 → book → 23 → cancel → 24, with the
  reason and timestamp retained and the identity proof stored.
- Rate limiting, idempotent reservation replay, blocked-room refusal,
  terminal-state guards on check-out and no-show, and precise error messages
  (`"reservation_status is required"`, `"Room 601 is blocked / out of order"`)
  are all present and working.

**Bottom line:** the business logic is in good shape and the interface is
clean. The authorisation and session layers are not, and they are small,
well-understood, now-tested changes — they simply have to be deployed, with the
services bound to loopback, before this goes near real guests.

---

## Appendix — reproduction

```bash
# findings and detail
QA/live/FINDINGS.md

# every harness needs a credential; none is stored in this repository
export QA_GATEWAY=http://168.231.103.18:9010
export QA_PASSWORD='<the demo password>'     # or QA_CREDENTIALS=file of email<TAB>password

# 144 read endpoints x 5 roles x 2 surfaces
python QA/live/sweep_api.py

# 159 write routes x 5 roles, against record id 999999999 (safe to re-run)
python QA/live/privesc_matrix.py

# what enforce would do, offline, against captured live traffic
python QA/live/rbac_dryrun.py

# business workflows; creates one tagged booking and cancels it
python QA/live/workflow_checks.py

# code == expired-token check, using the repo's own signing key
python QA/live/jwt_expiry_isolation.py <token>

# regenerate the map without a database
python QA/live/fetch_menu_paths.py > QA/live/menu-paths.txt
python Backend/tools/build_rbac_map.py --menus-from QA/live/menu-paths.txt

# regression
python Backend/tests/run_all.py
cd Frontend && eslint src
```

No credential is written to any file, log or report. The harnesses read it from
`QA_PASSWORD` (`QA/live/qa_common.py`) and refuse with setup instructions when
it is absent, rather than storing it or hitting the API with a blank one. The
password that is already committed by an earlier session is QA-SEC-008.
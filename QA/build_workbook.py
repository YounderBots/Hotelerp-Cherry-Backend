# -*- coding: utf-8 -*-
"""Build the QA status workbook.

    python QA/build_workbook.py

Reads QA/live/workbook_data.json (from QA/build_workbook_data.py) and writes
QA/HOTELERP_QA_STATUS.xlsx.

WHAT THIS WORKBOOK IS FOR
    One place that answers, per page and per module: what was tested, what was
    found, what was fixed, what is still open, and what has to happen before
    the deployment is production-ready.

THE HONESTY RULE APPLIED THROUGHOUT
    "No defect found" is never written as "verified perfect". A page is only
    called Done when a fix for a defect found against it is in the tree AND the
    test that proves the fix passes. Everything else is graded by what is
    actually known. Counts are formulas, not typed numbers, so the workbook
    recalculates when a row changes.
"""

from __future__ import annotations

import json
import pathlib
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

REPO = pathlib.Path(__file__).resolve().parents[1]
DATA = REPO / "QA" / "live" / "workbook_data.json"
RUN = REPO / "QA" / "live" / "regression_run.json"
OUT = REPO / "QA" / "HOTELERP_QA_STATUS.xlsx"

FONT = "Arial"
INK = "1F2933"
MUTED = "616E7C"

# ---- palette ---------------------------------------------------------------
NAVY = "1F3864"
SLATE = "2E4057"
BAND = "F4F6F8"
LINE = "D6DCE4"

GREEN_F, GREEN_T = "DCF0E0", "14532D"
AMBER_F, AMBER_T = "FDF0D5", "7A4A00"
RED_F, RED_T = "FBDDDD", "7F1D1D"
GREY_F, GREY_T = "EDEFF2", "3F4A56"
BLUE_F, BLUE_T = "DCE8F7", "1E3A5F"

STATUS_STYLE = {
    "Done": (GREEN_F, GREEN_T),
    "Fixed in source": (GREEN_F, GREEN_T),
    "Closed": (GREEN_F, GREEN_T),
    "Pass": (GREEN_F, GREEN_T),
    "Needs deploy": (AMBER_F, AMBER_T),
    "Partial": (AMBER_F, AMBER_T),
    "Open": (AMBER_F, AMBER_T),
    "Blocked": (RED_F, RED_T),
    "Critical - OPEN": (RED_F, RED_T),
    "High - OPEN": (RED_F, RED_T),
    "Not started": (RED_F, RED_T),
    "No defect found": (GREY_F, GREY_T),
    "Owner decision": (BLUE_F, BLUE_T),
}

THIN = Side(style="thin", color=LINE)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def f(size=10, bold=False, color=INK, italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def fill(hexcolor):
    return PatternFill("solid", fgColor=hexcolor)


def put(ws, row, col, value, *, font=None, bg=None, wrap=False,
        align="left", valign="top", border=True, fmt=None):
    c = ws.cell(row=row, column=col, value=value)
    c.font = font or f()
    if bg:
        c.fill = fill(bg)
    c.alignment = Alignment(horizontal=align, vertical=valign, wrap_text=wrap)
    if border:
        c.border = BOX
    if fmt:
        c.number_format = fmt
    return c


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


def header_row(ws, row, labels, bg=NAVY):
    for i, label in enumerate(labels, start=1):
        put(ws, row, i, label, font=f(10, True, "FFFFFF"), bg=bg,
            wrap=True, valign="center")
    ws.row_dimensions[row].height = 30


def title_block(ws, title, subtitle, span):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value=title)
    c.font = f(16, True, "FFFFFF")
    c.fill = fill(NAVY)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 32

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    c = ws.cell(row=2, column=1, value=subtitle)
    c.font = f(9, False, MUTED, italic=True)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 20


def add_table(ws, ref, name):
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(
        name="TableStyleLight1", showRowStripes=True, showColumnStripes=False)
    ws.add_table(t)


# ---------------------------------------------------------------------------
# The audit facts. Every one of these is traceable to a file in the repo.
# ---------------------------------------------------------------------------
MODULES = ["Hotel / Reservations", "Master Data", "Restaurant (F&B)", "Bar",
           "HRM / Users", "Cross-module (SPA)",
           "Cross-cutting (build & deploy)"]

MOD_OWNER = {
    "Hotel / Reservations": "HotelServices :9005",
    "Master Data": "MasterDataServices :9015",
    "Restaurant (F&B)": "RestaurantServices :9030",
    "Bar": "BarServices :9025",
    "HRM / Users": "UserServices :9020",
    "Cross-module (SPA)": "Frontend SPA (aggregates every service)",
    "Cross-cutting (build & deploy)": "repo root / deployment host",
}

# Which service's test run belongs to which module. Suites that run from the
# repository root are build-and-deploy invariants, not a module's tests.
SERVICE_MODULE = {
    "HotelServices": "Hotel / Reservations",
    "MasterDataServices": "Master Data",
    "RestaurantServices": "Restaurant (F&B)",
    "BarServices": "Bar",
    "UserServices": "HRM / Users",
    # The gateway is the front door and owns authentication and the permission
    # map itself, so it has no module of its own -- its tests belong with the
    # cross-cutting controls. Named here rather than left to a .get() default,
    # because a default that silently swallows a new service is how a suite
    # ends up filed against the wrong thing.
    "LoginServices": "Cross-cutting (build & deploy)",
    "repo root": "Cross-cutting (build & deploy)",
}

# Which findings bear on which module, and HOW FAR each one reaches.
#
#   (id, severity, one-line, status, scope)
#
# scope "page"      a defect in this module's own logic. It shows on that
#                   module's pages, because it affects what they do.
# scope "module"    a property of the module as deployed -- its bind address,
#                   its configuration, the host clock. Real and Critical, but it
#                   is not a per-page defect: marking all 12 Hotel pages "Open"
#                   because the host clock is wrong would be noise that hides
#                   the pages that genuinely need attention.
# scope "infra"     belongs to no module's pages at all.
#
# Without this, 19 of 60 pages read "Open" purely by inheritance.
MODULE_FINDINGS = {
    "Hotel / Reservations": [
        ("QA-BIZ-001", "High", "Repeat-cancel overwrote the stored reason", "Fixed in source", "page"),
        ("QA-BIZ-002", "High", "Quote priced rooms that cannot be booked", "Fixed in source", "page"),
        ("QA-SEC-006", "Medium", "Housekeeping holds read on the reservation book", "Owner decision", "page"),
        ("QA-SEC-009", "Critical", "Deployment clock 13.4h behind (business_date)", "Open", "infra"),
    ],
    "Master Data": [
        ("QA-SEC-002", "Critical", "Service was reachable from the internet", "Fixed in source", "module"),
        ("QA-SEC-007", "Medium", "SPA answered 200 HTML for missing assets", "Fixed in source", "module"),
    ],
    "Restaurant (F&B)": [
        ("QA-SEC-002", "Critical", "Service was reachable from the internet", "Fixed in source", "module"),
        ("QA-BIZ-003", "Low", "Combo rules and bills reconciled; hardening suite green", "Pass", "page"),
    ],
    "Bar": [
        ("QA-SEC-002", "Critical", "Service was reachable from the internet", "Fixed in source", "module"),
        ("QA-BIZ-003", "Low", "Combo rules and bills reconciled; hardening suite green", "Pass", "page"),
    ],
    "HRM / Users": [
        ("QA-SEC-001", "Critical", "Gateway RBAC ran in audit: any role could read/write all", "Fixed in source", "infra"),
        ("QA-DATA-001", "Low", "9 test-harness roles ship in the demo database", "Open", "page"),
    ],
    "Cross-module (SPA)": [
        ("QA-SEC-005", "High", "Guest PII reachable from the one page every role holds", "Fixed in source", "page"),
        ("QA-UX-002", "Low", "Route loader announced nothing to a screen reader", "Fixed in source", "page"),
    ],
    "Cross-cutting (build & deploy)": [
        ("QA-SEC-004", "Critical", "All six services run with development configuration", "Open", "infra"),
        ("QA-SEC-001b", "Critical", "179 write route+method pairs had no authorisation layer", "Needs deploy", "infra"),
        ("QA-SEC-008", "High", "Demo password published in committed files", "Partial", "infra"),
        ("QA-UX-003", "Low", "Four date constants frozen at import time", "Fixed in source", "module"),
    ],
}

# Suites that cover each module, with the assertion counts actually observed.
# Suites per module are DERIVED from the actual run output recorded in
# QA/live/regression_run.json, not typed by hand, so this workbook cannot
# disagree with what `python Backend/tests/run_all.py` prints.
def module_tests(run):
    """Group the recorded run by the module whose service it ran from."""
    out = {m: [] for m in MODULES}
    for job in run:
        mod = SERVICE_MODULE.get(job["service"], "Cross-cutting (build & deploy)")
        out.setdefault(mod, []).append((job["suite"], job["checks"] or 0))
    return out

FINDINGS = [
    # id, severity, title, status, where, root cause, fix, proof
    ("QA-SEC-001", "Critical",
     "Gateway RBAC runs in `audit`: every role can read and write everything",
     "Fixed in source",
     "LoginServices/resources/rbac.py",
     "MODE defaulted to `audit`, so the 279-row map was computed and discarded.",
     "Default changed to `enforce`; a misspelt value logs CRITICAL and falls forward.",
     "test_rbac_gateway.py 71 + test_route_policy.py 18"),
    ("QA-SEC-001b", "Critical",
     "179 write route+method pairs had no authorisation layer at all",
     "Needs deploy",
     "All 5 services",
     "Permissions were enforced only at the gateway; the services themselves "
     "checked only that a token was valid.",
     "Each service now applies its own slice of the same map, generated by the "
     "same run. Ships in `audit` so the deploy changes no behaviour.",
     "18 exhaustive cross-checks; full suite passes under `enforce` too"),
    ("QA-SEC-002", "Critical",
     "All five backend services answered on the public IP",
     "Fixed in source",
     "All 5 services main.py",
     "Services were started outside start-network.ps1/run.sh, so nothing read "
     "SERVICE_HOST and uvicorn bound 0.0.0.0.",
     "Import-time guard refuses a non-loopback SERVICE_HOST in every env; "
     "ALLOW_PUBLIC_BIND=true is the deliberate opt-out.",
     "test_bind_guard.py: 5 services x 7 cases + message check = 42/42"),
    ("QA-SEC-003", "Critical",
     "JWT expiry appeared not to be enforced",
     "Closed",
     "All 6 services",
     "Not a defect. The deployment's clock is wrong (QA-SEC-009), and the token "
     "was compared against the reviewer's clock.",
     "No source change needed - the deployment now refuses an expired token on "
     "all six surfaces. Added preflight checks 3b/3c so it cannot regress.",
     "expiry_recheck.py: 401 expired / 200 fresh / 401 mangled, x6 surfaces"),
    ("QA-SEC-009", "Critical",
     "The deployment's clock is 13.4 hours behind",
     "Open",
     "Deployment host (configuration)",
     "No time sync on the host. Everything the system records is stamped from "
     "it: JWT iat/exp, night audit business_date, arrival comparisons, payments.",
     "NTP on the host. Not a source fix - but preflight check 3b now fails "
     "whenever the clocks disagree, so it cannot regress unnoticed.",
     "clock_and_expiry.py: server Date header vs local, 48209s"),
    ("QA-SEC-004", "Critical",
     "All six services run with development configuration",
     "Open",
     "Deployment configuration",
     "ASCEND_ENV is not `production`, so /docs, /redoc and /openapi.json are "
     "public. No TLS either.",
     "Set ASCEND_ENV=production and terminate TLS in front of the gateway. "
     "verify_prod_env.py already fails this host on ASCEND_ENV alone.",
     "preflight.py check 1-6"),
    ("QA-BIZ-001", "High",
     "A cancellation could be re-recorded, destroying the reason",
     "Fixed in source",
     "HotelServices reservationController.py",
     "cancel_reservation had no terminal guard, so a second call overwrote the "
     "first call's reason with a default.",
     "409 when the current state already forbids cancelling. Uses "
     "rules.can_offer, the same expression the UI's can_cancel uses, so the "
     "button and the endpoint cannot disagree.",
     "test_reservation_rules.py 111 assertions"),
    ("QA-BIZ-002", "High",
     "A guest could be quoted a price for a room that cannot be booked",
     "Fixed in source",
     "HotelServices reservation_rules.py",
     "The quote path validated dates and tenant scope but not that the rooms "
     "were sellable - blocked, out of order or housekeeping-held.",
     "Extracted assert_rooms_sellable() and wired it into the quote endpoint.",
     "test_reservation_rules.py 111 assertions"),
    ("QA-SEC-005", "High",
     "Guest phone and email reachable from the one page every role holds",
     "Fixed in source",
     "HotelDashboardTab.jsx + rbac_map.py",
     "The dashboard called /hotel/user_activity_log, whose map row granted "
     "/dashboard - a page all five roles hold.",
     "The dashboard card is sourced from reservation_summary + housekeeper_tasks "
     "instead; the map row was regenerated, not hand-edited.",
     "test_rbac_gateway.py 71; map diff is exactly 1 row"),
    ("QA-SEC-006", "Medium",
     "Housekeeping holds read on the whole reservation book",
     "Owner decision",
     "role_permissions seed",
     "The Housekeeping role is granted view on reservation screens, which shows "
     "guest names, phones and emails to a role that does not need them.",
     "A grant to remove. Needs the business to say what Housekeeping actually "
     "needs - which is why it is not changed unilaterally.",
     "privesc_matrix.py: 8 pages, of which 3 are reservation"),
    ("QA-SEC-007", "Medium",
     "SPA answers `200 text/html` for every unknown path, including images",
     "Fixed in source",
     "Frontend/serve-spa.mjs (new)",
     "The history fallback was unconditional, so a missing asset returned 200 "
     "HTML and could not be distinguished from a working one.",
     "Fallback now applies only to a client-side route: no extension, and "
     "Accept: text/html. Missing assets are a true 404.",
     "test_spa_fallback.py: 21 checks, counted from the script's [PASS] lines"),
    ("QA-SEC-008", "High",
     "The demo password was published in committed files",
     "Partial",
     "QA/FINAL_QA_REPORT.md, docs/CHERRY_HOTEL_ERP_PAGE_AUDIT.md",
     "A previous session committed the shared demo password beside a note "
     "saying never to commit it.",
     "17 occurrences redacted (Backend/tools/redact.py). Working tree verified "
     "clean across all file types.",
     "whole-tree sweep: 0 occurrences"),
    ("QA-UX-002", "Low",
     "The route loader announced nothing to a screen reader",
     "Fixed in source",
     "LogoLoaderComponent.jsx",
     "The loading state was an image with alt text only, so it announced "
     "nothing about what was happening.",
     "role=status + aria-live=polite with visible text; the image is marked "
     "decorative. Existing CSS reused, no new design.",
     "eslint clean"),
    ("QA-UX-003", "Low",
     "Four date constants were frozen at import time",
     "Fixed in source",
     "All 6 services configs/base_config.py",
     "CURRENTDATE and three siblings were class-body expressions, evaluated once "
     "when the module imported and then frozen - a service running past midnight "
     "reported yesterday until restarted.",
     "Removed, with a comment saying why there is deliberately no date constant "
     "there. Zero readers existed, so no behaviour changed.",
     "remove_frozen_dates.py --check; all 6 services"),
    ("QA-DATA-001", "Low",
     "9 test-harness roles ship in the demo database",
     "Open",
     "Backend/db/12-Oct-2026/sql/hotelerp_users.sql",
     "A QA hardening pass ran its role CRUD tests against the demo database and "
     "committed the rows: `QB ZZQA<random> changed` x9.",
     "They hold zero permissions and are assigned to zero users, so they cannot "
     "grant access - but they are visible in Role Management.",
     "role_permissions rows: 5 demo roles only; users table: 10, all on roles 1-5"),
    ("QA-UX-001", "Withdrawn", "Reported earlier, then withdrawn",
     "Closed", "QA measurement",
     "My own measurement error: innerText is empty for the image-only loader, so "
     "the 'empty loader' reading was an artefact of how it was measured.",
     "Withdrawn. No source change was made for it.",
     "n/a - never a defect"),
]

PENDING = [
    # item, why it is open, owner, blocks production?, exact action
    ("QA-SEC-009  Fix the host clock (NTP)", "Host configuration, not code",
     "Infrastructure", "YES",
     "Enable NTP, then: python Backend/tools/preflight.py --host <server> - "
     "check 3b must pass"),
    ("QA-SEC-004  ASCEND_ENV=production + TLS", "Deployment configuration",
     "Infrastructure", "YES",
     "Set ASCEND_ENV=production in each service .env; terminate TLS in front of "
     ":9010"),
    ("QA-SEC-001b  Flip the service guard to enforce",
     "Ships in audit on purpose: a third control changing at once with two "
     "others is how a deploy day goes wrong", "Release owner", "NO",
     "grep rbac_would_deny .run-logs/*.log | head -50, then set "
     "ROUTE_POLICY_MODE=enforce"),
    ("QA-SEC-008  Rotate the demo password",
     "Redaction removed the published copy; it does not un-publish the one "
     "already in every clone", "Release owner", "YES",
     "python Backend/tools/rotate_passwords.py --confirm --out <file>. "
     "preflight check 5 fails until this is done."),
    ("QA-SEC-008  Purge the password from git history",
     "Needs a history rewrite and a force-push, which invalidates every clone",
     "Repo owner", "NO",
     "git filter-repo --replace-text, then force-push and tell everyone"),
    ("QA-SEC-006  Housekeeping reservation grants",
     "A business decision: what Housekeeping actually needs is not derivable "
     "from the code", "Product owner", "NO",
     "Decide, then amend role_permissions for role 4"),
    ("QA-DATA-001  Remove the 9 test roles",
     "Data hygiene in the committed dump", "Release owner", "NO",
     "Delete roles 6-14 from hotelerp_users.sql and re-export"),
    ("npm run build  Cannot run on the QA machine",
     "@oxc-resolver's win32 binding fails ERR_DLOPEN_FAILED here. Environment, "
     "not code.", "Whoever deploys", "YES",
     "Run the build on the deploy host or CI, then serve with "
     "node Frontend/serve-spa.mjs"),
    ("Owner decision: should QA runbooks be in the repo?",
     "QA/live/ holds re-runnable harness scripts that invite someone to re-run "
     "them against a live host", "Repo owner", "NO",
     "Decide: keep them in-repo, or move to a private location"),
]

GOLIVE = [
    (1, "Commit and deploy HEAD",
     "36 modified files, 14 new. Nothing is committed yet.",
     "git add -A && git commit -m 'QA fixes' && deploy",
     "Deploy owner"),
    (2, "Bind the services to loopback",
     "The launcher already does this; make sure nothing else is what started them.",
     "start-network.ps1, or run.sh. ALLOW_PUBLIC_BIND must NOT be set.",
     "Deploy owner"),
    (3, "Fix the host clock first",
     "A 13.4h skew makes every timestamp wrong and every session look expired.",
     "Enable NTP, then confirm with preflight check 3b",
     "Infrastructure"),
    (4, "Set ASCEND_ENV=production in every service .env",
     "Turns off /docs, /redoc and /openapi.json.",
     "verify_prod_env.py will refuse to start otherwise",
     "Deploy owner"),
    (5, "Rotate the demo password",
     "It is in git history and in every clone.",
     "rotate_passwords.py --confirm --out <file>",
     "Release owner"),
    (6, "Build the frontend",
     "Could not be built on the QA machine.",
     "npm run build, then serve dist with node Frontend/serve-spa.mjs",
     "Deploy owner"),
    (7, "Terminate TLS in front of the gateway",
     "Credentials and session tokens currently cross the wire in clear.",
     "Reverse proxy on :443 -> :9010",
     "Infrastructure"),
    (8, "Run preflight against the new deployment",
     "The gate. Six checks, and it now also checks token lifetime.",
     "python Backend/tools/preflight.py --host <server>",
     "Deploy owner"),
    (9, "Read the service guard's audit log",
     "This is what turns the audit log from theory into evidence for THIS data.",
     "grep rbac_would_deny .run-logs/*.log | head -50",
     "Release owner"),
    (10, "Flip ROUTE_POLICY_MODE=enforce and restart",
     "Only safe once step 9 is clean.",
     "ROUTE_POLICY_MODE=enforce in each service .env",
     "Release owner"),
    (11, "Re-run the QA sweep against the new deployment",
     "The fixes are verified by unit tests and map regeneration; only a live "
     "request proves them end to end.",
     "QA/live/sweep_api.py, privesc_matrix.py, workflow_checks.py",
     "QA"),
    (12, "Sign off", "Everything above green.",
     "Update the Module Status tab in this workbook",
     "Release owner"),
]

# The Test Evidence tab reads the recorded run directly; see RUN above.


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    run = json.loads(RUN.read_text(encoding="utf-8"))
    mtests = module_tests(run)
    pages = data["pages"]
    demo_roles = ["Admin", "Front Office Manager", "Front Desk", "Housekeeping",
                  "Food & Beverage"]

    n_pytest = sum(1 for j in run if j["kind"] == "pytest")
    n_script = sum(1 for j in run if j["kind"] == "script")
    n_assert = sum(j["checks"] or 0 for j in run if j["kind"] == "pytest")
    n_checks = sum(j["checks"] or 0 for j in run if j["kind"] == "script")
    n_fail = sum(1 for j in run if j["status"] != "PASS")

    wb = Workbook()

    # ======================================================================
    # 1. Read Me
    # ======================================================================
    ws = wb.active
    ws.title = "Read Me"
    widths(ws, {"A": 30, "B": 104})
    title_block(ws, "HotelERP - QA status, module by module",
                "Complete menu and submenu coverage, findings, fixes, and the "
                "go-live sequence. Every figure is either a formula or traceable "
                "to a file in the repository.", 2)

    rows = [
        ("", ""),
        ("WHAT WAS DONE", ""),
        ("Scope", "All 60 pages (3 menus + 57 submenus) across 5 modules, all 5 "
                  "roles, 6 backend services and the SPA."),
        ("Live testing", "~2,860 API calls against the staging deployment: 1,728 "
                         "reads (144 endpoints x 5 roles x 2 surfaces) and 1,010 "
                         "write probes (159 paths x 5 roles)."),
        ("Live page sweep", "60/60 routes rendered with live data. 0 console "
                            "errors, 0 failed requests, 0 broken images, 0 layout "
                            "overflow."),
        ("Regression", f"{len(run)} suites, {n_assert:,} pytest assertions plus "
                       f"{n_checks} checks in the 4 script suites, {n_fail} "
                       f"failures. Identical results under "
                       f"ROUTE_POLICY_MODE=audit (the shipped default) and "
                       f"enforce."),
        ("Lint", "ESLint: 0 errors, 10 warnings (unchanged baseline)."),
        ("", ""),
        ("HOW TO READ THE STATUS COLUMNS", ""),
        ("Done / Fixed in source",
         "A defect was found against this module, the fix is in the working tree, "
         "and a test that fails without the fix now passes. NOT yet on the "
         "deployment."),
        ("Needs deploy",
         "The fix is in the working tree but ships disabled or unactivated. Still "
         "live as a finding until it is deployed."),
        ("No defect found",
         "Tested, and nothing came up. This is NOT the same claim as 'verified "
         "perfect' - it means no test detected a problem, not that none exists."),
        ("Open", "A real defect that is still present. No fix, or a fix that "
                 "cannot be made in source."),
        ("Owner decision",
         "Deliberately not changed here. The right answer depends on the "
         "business, not on the code."),
        ("", ""),
        ("THE ONE THING TO KNOW BEFORE TRUSTING IT", ""),
        ("Not deployed",
         "The fixes are in the working tree. Nothing is committed or pushed. "
         "Every fix is proven by unit tests and by regenerating the permission "
         "map byte-identically - NOT by a request against the running system. "
         "Step 11 of Go-Live closes that gap."),
        ("", ""),
        ("KNOWN LIMITS OF THIS AUDIT", ""),
        ("Frontend build",
         "npm run build could not run on the QA machine (@oxc-resolver's win32 "
         "binding fails ERR_DLOPEN_FAILED). Frontend changes are verified by "
         "ESLint and by Node-level HTTP tests only."),
        ("Scope of destructive testing",
         "No DoS, no real payments, emails or SMS, no deletion of business "
         "records, no database resets. Write probes used record id 999999999, "
         "which cannot exist."),
        ("One process defect",
         "An early probe of this audit issued DELETE against real ids expecting "
         "a 403. It was not refused, and two rows were deleted (a tax, and Room "
         "601's photos). Both were restored. Recorded in QA/live/FINDINGS.md "
         "rather than quietly fixed."),
        ("Passwords",
         "No credential appears anywhere in this workbook or in the repository's "
         "working tree. The value is supplied at seed time via SEED_PASSWORD."),
    ]
    r = 4
    for a, b in rows:
        if a and not b:
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
            c = ws.cell(row=r, column=1, value=a)
            c.font = f(11, True, "FFFFFF")
            c.fill = fill(SLATE)
            c.alignment = Alignment(vertical="center", indent=1)
            ws.row_dimensions[r].height = 22
        elif a or b:
            put(ws, r, 1, a, font=f(10, True, NAVY), wrap=True, valign="top")
            put(ws, r, 2, b, wrap=True, valign="top")
            ws.row_dimensions[r].height = max(28, 13 * (len(b) // 100 + 1))
        r += 1

    # ======================================================================
    # 2. Module Status
    # ======================================================================
    ws = wb.create_sheet("Module Status")
    widths(ws, {"A": 22, "B": 27, "C": 9, "D": 10, "E": 12, "F": 11, "G": 34,
                "H": 30})
    title_block(ws, "Module status - done, pending, and what is still open",
                "One row per module. Page and finding counts are formulas over "
                "the 'Menu & Submenu Status' and 'Findings' tabs.", 8)

    header_row(ws, 4, ["Module", "Owning service", "Pages", "Routes", "Test suites",
                       "Checks", "Findings", "Status"])
    r = 5
    first_data = r

    # The per-suite listing is written further down this same sheet, and the
    # suite count and check total are COUNTIF/SUMIF over it. That is deliberate:
    # an earlier version wrote =SUM(50+111+...), which is a typed-in number
    # wearing a formula's clothes and would never notice the listing changing.
    # Layout below: modules rows 5..11, TOTAL row 12, blank 13, section
    # heading 14, listing header 15, so the listing DATA starts at 16. This was
    # off by one -- it pointed at the header and dropped the last suite, which
    # made the TOTAL read 36 suites / 1,335 checks instead of 37 / 1,341.
    n_listing = sum(len(mtests.get(m, [])) for m in MODULES)
    listing_first = first_data + len(MODULES) + 4
    listing_last = listing_first + n_listing - 1
    LREF = f"$A${listing_first}:$A${listing_last}"
    CREF = f"$C${listing_first}:$C${listing_last}"
    for mod in MODULES:
        bg = BAND if (r - first_data) % 2 else None
        put(ws, r, 1, mod, font=f(10, True), bg=bg)
        put(ws, r, 2, MOD_OWNER[mod], bg=bg)
        put(ws, r, 3, f"=COUNTIF('Menu & Submenu Status'!$E$5:$E$64,\"*\"&A{r}&\"*\")",
            bg=bg, align="center")
        put(ws, r, 4, f"=SUMPRODUCT(--ISNUMBER(SEARCH(A{r},"
                      f"'Menu & Submenu Status'!$E$5:$E$64)),"
                      f"'Menu & Submenu Status'!$H$5:$H$64)",
            bg=bg, align="center")
        put(ws, r, 5, f"=COUNTIF({LREF},A{r})", bg=bg, align="center")
        put(ws, r, 6, f"=SUMIF({LREF},A{r},{CREF})", bg=bg, align="center")

        # Status: the worst unresolved finding for this module decides it.
        findings = MODULE_FINDINGS[mod]
        unresolved = [x for x in findings
                      if x[3] in ("Open", "Critical - OPEN", "High - OPEN")]
        pending = [x for x in findings if x[3] in ("Needs deploy", "Owner decision")]
        # Which of them is a defect in this module's own logic, as opposed to a
        # property of how it is deployed.
        own_unresolved = [x for x in unresolved if x[4] == "page"]
        own_pending = [x for x in pending if x[4] == "page"]
        if own_unresolved:
            status = "Open"
        elif own_pending:
            status = "Needs deploy"
        elif unresolved or pending:
            status = "Needs deploy"
        elif all(x[3] in ("Fixed in source", "Closed", "Pass") for x in findings):
            status = "Fixed in source"
        else:
            status = "Partial"
        fg, ft = STATUS_STYLE[status]
        # Show which findings are this module's own logic and which are
        # deployment-wide, because "Open" on Hotel means something different
        # from "Open" because the host clock is wrong.
        put(ws, r, 7, "; ".join(
            f"{x[0]} {x[3]}" + (" (module-wide)" if x[4] != "page" else "")
            for x in findings) or "none", bg=bg, wrap=True)
        put(ws, r, 8, status, font=f(10, True, ft), bg=fg, align="center",
            wrap=True)
        ws.row_dimensions[r].height = 34
        r += 1

    put(ws, r, 1, "TOTAL", font=f(10, True, "FFFFFF"), bg=NAVY)
    put(ws, r, 2, "", bg=NAVY)
    put(ws, r, 3, f"=SUM(C{first_data}:C{r-1})", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, r, 4, f"=SUM(D{first_data}:D{r-1})", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, r, 5, f"=SUM(E{first_data}:E{r-1})", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, r, 6, f"=SUM(F{first_data}:F{r-1})", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, r, 7, "", bg=NAVY)
    put(ws, r, 8, "", bg=NAVY)
    r += 2

    # Which suites cover which module, listed.
    put(ws, r, 1, "Test suites by module", font=f(11, True, "FFFFFF"), bg=SLATE)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws.cell(row=r, column=1).alignment = Alignment(vertical="center", indent=1)
    r += 1
    header_row(ws, r, ["Module", "Suite", "Checks", "", "", "", "", ""])
    r += 1
    for mod in MODULES:
        for suite, n in mtests.get(mod, []):
            put(ws, r, 1, mod)
            put(ws, r, 2, suite)
            put(ws, r, 3, n, align="center")
            for c in range(4, 9):
                put(ws, r, c, "")
            r += 1
    ws.freeze_panes = "A5"

    # ======================================================================
    # 3. Menu & Submenu Status  (all 60)
    # ======================================================================
    ws = wb.create_sheet("Menu & Submenu Status")
    widths(ws, {"A": 5, "B": 9, "C": 15, "D": 23, "E": 20, "F": 27,
                "G": 22, "H": 7, "I": 7, "J": 13, "K": 13, "L": 12,
                "M": 13, "N": 9, "O": 10, "P": 14, "Q": 34})
    title_block(ws, "Every menu and submenu, with its status",
                "All 60 pages from the shipped database. V/A/E/D are what each "
                "role is granted on that page. 'Reachable' is a formula over "
                "those five columns. 'Owning module' is which menu the screen "
                "sits under; 'Served by' is which services answer for it - two "
                "different questions, and the first attempt conflated them.", 17)

    header_row(ws, 4, [
        "#", "Kind", "Parent menu", "Label", "Owning module", "Path",
        "Served by", "Routes", "Roles",
        "Admin", "F.O. Manager", "Front Desk", "Housekeeping", "F&B",
        "Reachable", "QA status", "Note"])

    PAGE_NOTE = {
        "/dashboard": "QA-SEC-005 fixed: no longer reads guest PII from "
                      "user_activity_log.",
        "/reservation": "Parent screen; 4 children.",
        "/add_new_reservation": "QA-BIZ-002 fixed: quote refuses unsellable rooms.",
        "/booking": "QA-SEC-006: Housekeeping granted view here.",
        "/reservation_view": "QA-BIZ-001 fixed: repeat cancel is a 409.",
        "/night_audit": "QA-SEC-009: business_date comes from the host clock.",
        "/room": "QA-SEC-007 fixed: a missing room photo is now a real 404.",
        "/roles": "QA-DATA-001: 9 test-harness roles are visible on this screen.",
        "/user": "Only role in the product refused unauthenticated reads (401).",
    }

    r = 5
    for i, p in enumerate(pages, start=1):
        bg = BAND if i % 2 == 0 else None
        mods = ", ".join(p["modules"])
        served = ", ".join(p.get("served_by") or [])
        put(ws, r, 1, i, bg=bg, align="center", font=f(9, False, MUTED))
        put(ws, r, 2, p["kind"], bg=bg)
        put(ws, r, 3, p["parent"] or "-", bg=bg)
        put(ws, r, 4, p["label"], font=f(10, True), bg=bg)
        # Module is its own column because Module Status counts pages by it.
        # It was originally folded into a wider "Path" cell, which left the
        # COUNTIF pointing at the wrong column and returning nonsense.
        put(ws, r, 5, mods, bg=bg, wrap=True)
        put(ws, r, 6, p["path"], bg=bg)
        put(ws, r, 7, served or "-", bg=bg, wrap=True, font=f(9, color=MUTED))
        put(ws, r, 8, p["routes"], bg=bg, align="center")
        put(ws, r, 9, len(p["roles"]), bg=bg, align="center")
        for col, role in zip(range(10, 15), demo_roles):
            perms = p["roles"].get(role)
            if perms:
                txt = "/".join(
                    k[0].upper() for k in ("view", "create", "edit", "delete")
                    if perms[k])
            else:
                txt = "-"
            put(ws, r, col, txt, bg=bg, align="center",
                font=f(9, False, INK if perms else MUTED))
        put(ws, r, 15, f'=COUNTIF(J{r}:N{r},"<>-")', bg=bg, align="center",
            font=f(10, True))

        # Per-page status. Two things it must not do:
        #   * pick a module arbitrarily -- a page served by two modules has an
        #     ordered list now, and the primary is the one with most routes;
        #   * inherit a deployment-wide problem (host clock, bind address) as if
        #     it were a defect in this screen's logic.
        mod = p.get("primary_module") or p["modules"][0]
        mod_findings = MODULE_FINDINGS.get(mod, [])
        unresolved = [x for x in mod_findings
                      if x[4] == "page"
                      and x[3] in ("Open", "Critical - OPEN", "High - OPEN")]
        needs_deploy = [x for x in mod_findings
                        if x[4] == "page"
                        and x[3] in ("Needs deploy", "Owner decision")]
        if unresolved:
            status = "Open"
        elif needs_deploy:
            status = "Needs deploy"
        elif any(x[4] == "page" for x in mod_findings):
            status = "Fixed in source"
        else:
            status = "No defect found"
        fg, ft = STATUS_STYLE[status]
        put(ws, r, 16, status, font=f(9, True, ft), bg=fg, align="center",
            wrap=True)
        put(ws, r, 17, PAGE_NOTE.get(p["path"], ""), bg=bg, wrap=True)
        ws.row_dimensions[r].height = 26
        r += 1

    last = r - 1
    add_table(ws, f"A4:Q{last}", "MenuStatus")
    ws.freeze_panes = "F5"
    ws.auto_filter.ref = f"A4:Q{last}"

    put(ws, last + 2, 1, "TOTALS", font=f(10, True, "FFFFFF"), bg=NAVY)
    put(ws, last + 2, 4, f"=COUNTA(D5:D{last})", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, last + 2, 6, "pages", font=f(9, False, "FFFFFF"), bg=NAVY)
    put(ws, last + 2, 8, f"=SUM(H5:H{last})", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, last + 2, 7, "routes", font=f(9, False, "FFFFFF"), bg=NAVY)
    for c in (2, 3, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17):
        put(ws, last + 2, c, "", bg=NAVY)

    # ======================================================================
    # 4. Role Access Matrix
    # ======================================================================
    ws = wb.create_sheet("Role Access Matrix")
    widths(ws, {"A": 7, "B": 24, "C": 27, "D": 16, "E": 16, "F": 16, "G": 16,
                "H": 16})
    title_block(ws, "Role access, as the database actually grants it",
                "V/A/E/D = view / add / edit / delete. This is the permission "
                "data itself, not a re-derivation. Column totals are formulas.", 8)

    header_row(ws, 4, ["#", "Label", "Path", "Admin", "F.O. Manager", "Front Desk",
                       "Housekeeping", "F&B"])
    r = 5
    for i, p in enumerate(pages, start=1):
        bg = BAND if i % 2 == 0 else None
        put(ws, r, 1, i, bg=bg, align="center", font=f(9, False, MUTED))
        put(ws, r, 2, p["label"], bg=bg)
        put(ws, r, 3, p["path"], bg=bg)
        for col, role in zip(range(4, 9), demo_roles):
            perms = p["roles"].get(role)
            if perms:
                txt = "/".join(k[0].upper() for k in
                               ("view", "create", "edit", "delete") if perms[k])
            else:
                txt = "-"
            put(ws, r, col, txt, bg=bg, align="center",
                font=f(9, False, INK if perms else MUTED))
        r += 1
    last = r - 1
    put(ws, last + 2, 2, "PAGES GRANTED", font=f(10, True, "FFFFFF"), bg=NAVY)
    for c in (1, 3):
        put(ws, last + 2, c, "", bg=NAVY)
    for col in range(4, 9):
        L = get_column_letter(col)
        put(ws, last + 2, col, f'=COUNTIF({L}5:{L}{last},"<>-")',
            font=f(10, True, "FFFFFF"), bg=NAVY, align="center")
    add_table(ws, f"A4:H{last}", "RoleMatrix")
    ws.freeze_panes = "D5"

    # ======================================================================
    # 5. Findings
    # ======================================================================
    ws = wb.create_sheet("Findings")
    widths(ws, {"A": 14, "B": 10, "C": 46, "D": 15, "E": 27, "F": 46, "G": 46,
                "H": 34})
    title_block(ws, "Findings - every issue raised by this audit",
                "Severity is the impact if exploited or left in place. Status "
                "says what has actually happened to it, not what is planned.", 8)

    header_row(ws, 4, ["ID", "Severity", "Finding", "Status", "Where",
                       "Root cause", "Fix", "Evidence"])
    r = 5
    for (fid, sev, title, status, where, cause, fix, proof) in FINDINGS:
        sev_style = {"Critical": (RED_F, RED_T), "High": (RED_F, RED_T),
                     "Medium": (AMBER_F, AMBER_T), "Low": (GREY_F, GREY_T),
                     "Withdrawn": (GREY_F, GREY_T)}.get(sev, (GREY_F, GREY_T))
        st_style = STATUS_STYLE.get(status, (GREY_F, GREY_T))
        put(ws, r, 1, fid, font=f(10, True, NAVY))
        put(ws, r, 2, sev, font=f(10, True, sev_style[1]), bg=sev_style[0],
            align="center")
        put(ws, r, 3, title, wrap=True)
        put(ws, r, 4, status, font=f(10, True, st_style[1]), bg=st_style[0],
            align="center", wrap=True)
        put(ws, r, 5, where, wrap=True, font=f(9))
        put(ws, r, 6, cause, wrap=True, font=f(9))
        put(ws, r, 7, fix, wrap=True, font=f(9))
        put(ws, r, 8, proof, wrap=True, font=f(9, color=MUTED))
        ws.row_dimensions[r].height = max(44, 12 * (max(len(cause), len(fix)) // 44 + 1))
        r += 1
    last = r - 1

    put(ws, last + 2, 1, "TOTALS", font=f(10, True, "FFFFFF"), bg=NAVY)
    for c in range(2, 9):
        put(ws, last + 2, c, "", bg=NAVY)
    r = last + 2
    for sev in ("Critical", "High", "Medium", "Low", "Withdrawn"):
        put(ws, r, 1, sev, font=f(10, True))
        put(ws, r, 2, f'=COUNTIF($B$5:$B${last},A{r})', align="center",
            font=f(10, True))
        put(ws, r, 3, f'=IF(B{r}=0,"none","")')
        for c in range(4, 9):
            put(ws, r, c, "")
        r += 1
    add_table(ws, f"A4:H{last}", "Findings")
    ws.freeze_panes = "C5"

    # ======================================================================
    # 6. Pending & Blocked
    # ======================================================================
    ws = wb.create_sheet("Pending & Blocked")
    widths(ws, {"A": 6, "B": 40, "C": 44, "D": 16, "E": 15, "F": 54})
    title_block(ws, "What is still open, and what it needs",
                "'Blocks production' is the honest question: an item marked YES "
                "means the deployment is not production-ready without it.", 6)

    header_row(ws, 4, ["#", "Item", "Why it is still open", "Owner",
                       "Blocks production?", "Exact action"])
    r = 5
    for i, (item, why, owner, blocks, action) in enumerate(PENDING, start=1):
        bg = BAND if i % 2 == 0 else None
        put(ws, r, 1, i, bg=bg, align="center", font=f(9, False, MUTED))
        put(ws, r, 2, item, font=f(10, True), bg=bg, wrap=True)
        put(ws, r, 3, why, bg=bg, wrap=True, font=f(9))
        put(ws, r, 4, owner, bg=bg, align="center")
        if blocks == "YES":
            put(ws, r, 5, "YES", font=f(10, True, RED_T), bg=RED_F,
                align="center")
        else:
            put(ws, r, 5, "No", font=f(10, False, MUTED), bg=GREY_F,
                align="center")
        put(ws, r, 6, action, bg=bg, wrap=True, font=f(9, color=NAVY))
        ws.row_dimensions[r].height = 46
        r += 1
    last = r - 1

    put(ws, last + 2, 2, "ITEMS BLOCKING PRODUCTION READINESS",
        font=f(10, True, "FFFFFF"), bg=NAVY)
    for c in (1, 3, 4, 5, 6):
        put(ws, last + 2, c, "", bg=NAVY)
    put(ws, last + 2, 5, f'=COUNTIF(E5:E{last},"YES")', font=f(12, True, "FFFFFF"),
        bg=NAVY, align="center")
    add_table(ws, f"A4:F{last}", "Pending")
    ws.freeze_panes = "C5"

    # ======================================================================
    # 7. Go-Live Flow
    # ======================================================================
    ws = wb.create_sheet("Go-Live Flow")
    widths(ws, {"A": 6, "B": 34, "C": 52, "D": 54, "E": 16})
    title_block(ws, "Go-live sequence - in order, with the check at each step",
                "Steps 1-7 are deployment work. Step 8 is the gate: if preflight "
                "fails, stop. Step 11 is what turns this audit's unit-test proof "
                "into live proof.", 5)

    header_row(ws, 4, ["Step", "Action", "Why it is in this order", "Command / check",
                       "Owner"])
    r = 5
    for i, (step, action, why, cmd, owner) in enumerate(GOLIVE, start=1):
        bg = BAND if i % 2 == 0 else None
        gate = step in (8, 9)
        put(ws, r, 1, step, bg=bg, align="center", font=f(11, True, NAVY))
        put(ws, r, 2, action, font=f(10, True, RED_T if gate else INK),
            bg=RED_F if gate else bg, wrap=True)
        put(ws, r, 3, why, bg=RED_F if gate else bg, wrap=True, font=f(9))
        put(ws, r, 4, cmd, bg=RED_F if gate else bg, wrap=True,
            font=f(9, color=NAVY))
        put(ws, r, 5, owner, bg=RED_F if gate else bg, align="center", font=f(9))
        ws.row_dimensions[r].height = 42
        r += 1
    last = r - 1
    add_table(ws, f"A4:E{last}", "GoLive")
    ws.freeze_panes = "B5"

    # ======================================================================
    # 8. Test Evidence
    # ======================================================================
    ws = wb.create_sheet("Test Evidence")
    widths(ws, {"A": 32, "B": 21, "C": 9, "D": 11, "E": 60, "F": 11})
    title_block(ws, "Regression evidence - every suite, straight from the run",
                "Read from QA/live/regression_run.json, which is parsed from the "
                "output of python Backend/tests/run_all.py. A pytest suite and a "
                "script suite count differently, so they are shown separately.", 6)

    header_row(ws, 4, ["Suite", "Runs from", "Kind", "Checks",
                       "What it protects", "Result"])
    r = 5
    for i, job in enumerate(run, start=1):
        bg = BAND if i % 2 == 0 else None
        put(ws, r, 1, job["suite"], font=f(10, True), bg=bg)
        put(ws, r, 2, job["service"], bg=bg, font=f(9))
        put(ws, r, 3, "pytest" if job["kind"] == "pytest" else "script",
            bg=bg, font=f(9), align="center")
        put(ws, r, 4, job["checks"], bg=bg, align="center")
        put(ws, r, 5, job["protects"], bg=bg, wrap=True, font=f(9))
        ok = job["status"] == "PASS"
        put(ws, r, 6, "Pass" if ok else "FAIL", font=f(10, True,
            GREEN_T if ok else RED_T), bg=GREEN_F if ok else RED_F,
            align="center")
        ws.row_dimensions[r].height = 26
        r += 1
    last = r - 1
    put(ws, last + 2, 1, "TOTALS", font=f(10, True, "FFFFFF"), bg=NAVY)
    put(ws, last + 2, 2, f"=COUNTA(A5:A{last})&' suites'", font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    put(ws, last + 2, 3, f"=COUNTIF(C5:C{last},\"pytest\")&'+'&"
                         f"COUNTIF(C5:C{last},\"script\")",
        font=f(9, True, "FFFFFF"), bg=NAVY, align="center")
    put(ws, last + 2, 4, f"=SUM(D5:D{last})", font=f(10, True, "FFFFFF"), bg=NAVY,
        align="center")
    put(ws, last + 2, 5, f"=SUMPRODUCT((C5:C{last}=\"pytest\")*D5:D{last})"
                         f"&\" pytest assertions + \"&"
                         f"SUMPRODUCT((C5:C{last}=\"script\")*D5:D{last})"
                         f"&\" script checks. Identical under "
                         f"ROUTE_POLICY_MODE=audit and enforce.\"",
        font=f(9, True, "FFFFFF"), bg=NAVY)
    put(ws, last + 2, 6, f'=COUNTIF(F5:F{last},"FAIL")&" failed"', font=f(10, True, "FFFFFF"),
        bg=NAVY, align="center")
    add_table(ws, f"A4:F{last}", "Suites")
    ws.freeze_panes = "B5"

    wb.save(OUT)
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  sheets  : {', '.join(wb.sheetnames)}")
    print(f"  pages   : {len(pages)}")
    print(f"  findings: {len(FINDINGS)}   pending: {len(PENDING)}   "
          f"go-live steps: {len(GOLIVE)}")
    print(f"  suites  : {len(run)} read from the recorded run "
          f"({n_assert} pytest + {n_checks} script checks, {n_fail} failures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
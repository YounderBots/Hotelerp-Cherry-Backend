#!/usr/bin/env python3
"""Run every backend suite, each in its own process.

Each service is its own top-level package root -- `configs`, `models` and
`resources` are imported absolutely, and six different services all define a
module called `configs`. Collecting them in a single pytest process makes the
first one imported win, so the suites MUST run one subprocess per service, with
cwd set to that service directory. That is what this script does, and it is the
same thing CI runs.

    python Backend/tests/run_all.py
"""
import os
import pathlib
import subprocess
import sys

SERVICES = [
    "LoginServices",
    "UserServices",
    "MasterDataServices",
    "HotelServices",
    "RestaurantServices",
    "BarServices",
]

# The RBAC suite exercises UserServices' authorization tables, which only that
# service defines; the JWT suite is service-agnostic and runs against all six.
RBAC_SERVICE = "UserServices"

# Gateway-side authorisation lives in LoginServices: the route->page map and the
# enforcement that reads it are both there, so the suite has to run from that
# service root to import them.
GATEWAY_SERVICE = "LoginServices"

# Bill payment guards apply to the two services that take money at a till.
BILLING_SERVICES = ["BarServices", "RestaurantServices"]

# Services that accept a file upload: Master Data (room/facility images), both
# venues (menu images) and Hotel (housekeeping attachments, identity documents).
UPLOAD_SERVICES = ["MasterDataServices", "RestaurantServices", "BarServices", "HotelServices"]

# Night Audit lives entirely in HotelServices: the business date, the accrual
# arithmetic and the idempotency guard are all defined there, so the suite has
# to run from that service root to import them.
NIGHT_AUDIT_SERVICE = "HotelServices"

# The preflight suite imports Backend/tools/preflight.py by path and stubs its
# HTTP layer, so it needs no service package at all. It runs from the gateway
# directory because the gateway is what preflight points at.
TOOLS_SERVICE = "LoginServices"

# Country-aware phone/email/name validation (C-086). The rule is one module per
# service -- services cannot import each other -- so the same suite runs from
# each of the four that validate a field, and asserts the copies are identical.
PHONE_VALIDATION_SERVICES = ["BarServices", "RestaurantServices", "UserServices", "HotelServices"]

# The guard that keeps a hand-written phone regex from coming back. It runs from
# one root only: it sweeps the whole repository rather than one service, and it
# carries its own proof that the sweep can still detect a planted pattern.
PHONE_PATTERN_GUARD_SERVICE = "HotelServices"

# The Hotel service reads Master Data and Users over HTTP. Its side of that
# wire -- the client, the records the rules read, the 503 a sibling being down
# turns into, the lock that stayed in its own schema -- runs from HotelServices.
# The other side -- the real /snapshot and PATCH /room/{id}/state routes, served
# over SQLite and fed to that same client -- runs from MasterDataServices, so
# the contract is asserted from both ends in one run.
MASTER_CLIENT_SERVICE = "HotelServices"
SNAPSHOT_CONTRACT_SERVICE = "MasterDataServices"

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVICES_DIR = ROOT / "Backend" / "Services"
TESTS_DIR = ROOT / "Backend" / "tests"

# Suites that are scripts, not pytest modules -- each drives its own
# subprocesses because what it verifies cannot be collected by importing.
#
# The last two are the source-rewriting tools, run WITHOUT --apply. They default
# to reporting, so calling them here is a real assertion that all five non-gateway
# services still carry the loopback bind guard and that none of the six has
# regrown an import-time date constant.
SCRIPT_SUITES = ["test_bind_guard.py", "test_spa_fallback.py"]

SOURCE_INVARIANT_TOOLS = [
    "install_bind_guard.py",
    "remove_frozen_dates.py",
]


def run(service: str, suite: str) -> tuple[str, bool, str]:
    cwd = SERVICES_DIR / service
    env = {**os.environ, "ASCEND_ENV": "dev", "DB_AUTO_CREATE": "false"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS_DIR / suite), "-q"],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    label = f"{service}/{suite}"
    tail = (proc.stdout or proc.stderr).strip().splitlines()
    return label, proc.returncode == 0, tail[-1] if tail else "(no output)"


def run_script(suite: str) -> tuple[str, bool, str]:
    """A suite that is a script rather than a pytest module.

    `test_bind_guard.py` imports each service's `main` in a subprocess with
    different SERVICE_HOST values, because the control it verifies is an
    import-time check -- pytest collects by importing the module under test, so
    it cannot vary the environment per case within one process.
    """
    proc = subprocess.run(
        [sys.executable, str(TESTS_DIR / suite)],
        cwd=str(ROOT), env={**os.environ, "DB_AUTO_CREATE": "false"},
        capture_output=True, text=True,
    )
    tail = (proc.stdout or proc.stderr).strip().splitlines()
    return suite, proc.returncode == 0, tail[-1] if tail else "(no output)"


def run_tool(tool: str) -> tuple[str, bool, str]:
    """Run one of the source-rewriting tools in its reporting mode.

    These tools rewrite files across every service when given --apply. Because
    reporting is the default, running them here is safe to do in CI and doubles
    as the assertion that the invariant they enforce still holds.
    """
    proc = subprocess.run(
        [sys.executable, str(ROOT / "Backend" / "tools" / tool)],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    tail = (proc.stdout or proc.stderr).strip().splitlines()
    return tool, proc.returncode == 0, tail[-1] if tail else "(no output)"


def main() -> int:
    jobs = [
        (RBAC_SERVICE, "test_rbac.py"),
        (GATEWAY_SERVICE, "test_rbac_gateway.py"),
        # The service-side permission guard must reach the same verdict as the
        # gateway for every one of the 279 routes -- exhaustively, not sampled.
        # Runs from the gateway service because it imports both sides to compare.
        (GATEWAY_SERVICE, "test_route_policy.py"),
        (NIGHT_AUDIT_SERVICE, "test_night_audit.py"),
        # Reservation's rules are pure functions in the same service.
        (NIGHT_AUDIT_SERVICE, "test_reservation_rules.py"),
        # The quote engine, which prices from Master Data -- answered here by
        # tests/fake_master.py behind the real HTTP client. It decides every
        # figure on a folio; the suite above covers only the pure helpers.
        (NIGHT_AUDIT_SERVICE, "test_reservation_pricing.py"),
        # Booking-enquiry writes validate dates, numeric boundaries, and the
        # tenant-scoped room-type relationship at the service boundary.
        (NIGHT_AUDIT_SERVICE, "test_booking_validation.py"),
        # The checkout -> housekeeping handover: the Hotel schema in SQLite,
        # Master Data faked, and every room-state write asserted on the wire.
        (NIGHT_AUDIT_SERVICE, "test_reservation_housekeeping.py"),
        # Preflight check 6, which asks a deployment whether the images its
        # database points at are actually on the server.
        (TOOLS_SERVICE, "test_preflight_images.py"),
        # The demo seed's night-audit row has to reconcile with the bookings the
        # same seed writes -- it is the data behind every Night Audit screen, and
        # its arithmetic is a deliberate duplicate of the service's, so the
        # suite cross-checks the two. SQLite only; needs no service package, so it
        # runs from the tools-friendly gateway root like the preflight suite.
        (TOOLS_SERVICE, "test_seed_night_audit.py"),
        # The Hotel service's gateway client and its own-schema lock contract.
        # Cross-service data is reached over HTTP; it must not require grants
        # on another service's schema.
        (MASTER_CLIENT_SERVICE, "test_master_client.py"),
        (SNAPSHOT_CONTRACT_SERVICE, "test_snapshot_contract.py"),
    ]
    # Billing exists only in these two, and both expose the same endpoint, so
    # the money guards run against each.
    jobs += [(svc, "test_bill_payment.py") for svc in BILLING_SERVICES]
    # Upload content validation (C-085): each service proves a file's bytes
    # match the type its name claims. One suite, run from each service root that
    # owns an upload path, because the module layout is per-service.
    jobs += [(svc, "test_upload_content.py") for svc in UPLOAD_SERVICES]
    # The staff-photo path is UserServices' own upload (it writes to
    # templates/static/users and derives the extension from the declared type),
    # so it gets its own suite rather than sharing the extension-based one.
    jobs.append((RBAC_SERVICE, "test_user_photo_upload.py"))
    # Field validation (C-086): the phone matrix, plus email and name rules, run
    # from each service that owns a copy of resources/validation.py.
    jobs += [(svc, "test_phone_validation.py") for svc in PHONE_VALIDATION_SERVICES]
    # The pattern guard (C-086): no hand-written phone regex may reappear, and the
    # check proves it can still fire.
    jobs.append((PHONE_PATTERN_GUARD_SERVICE, "test_phone_pattern_guard.py"))
    # Combo/package request validation is a Restaurant-only business rule.
    jobs.append(("RestaurantServices", "test_combo_rules.py"))
    # F&B pricing and recipe-deduction guards run against both venue schemas.
    jobs += [(svc, "test_fnb_hardening.py") for svc in BILLING_SERVICES]
    # A billed order's lines are frozen, a part-paid bill cannot be cancelled,
    # and wastage only ever removes stock -- in both venues.
    jobs += [(svc, "test_order_bill_integrity.py") for svc in BILLING_SERVICES]
    # Hotel payment/refund amounts must be finite (NaN reached the insert).
    jobs.append(("HotelServices", "test_reservation_payment_guards.py"))
    jobs += [(svc, "test_jwt_auth.py") for svc in SERVICES]

    failed = []
    for service, suite in jobs:
        label, ok, summary = run(service, suite)
        print(f"{'PASS' if ok else 'FAIL'}  {label:<40} {summary}")
        if not ok:
            failed.append(label)

    # Script suites, which need the repository root rather than a service
    # directory and drive their own subprocesses.
    for suite in SCRIPT_SUITES:
        label, ok, summary = run_script(suite)
        print(f"{'PASS' if ok else 'FAIL'}  {label:<40} {summary}")
        if not ok:
            failed.append(label)

    # Invariant checks: the tools that enforce the two source-wide rules, run in
    # reporting mode so they cannot rewrite anything.
    for tool in SOURCE_INVARIANT_TOOLS:
        label, ok, summary = run_tool(tool)
        print(f"{'PASS' if ok else 'FAIL'}  {label:<40} {summary}")
        if not ok:
            failed.append(label)

    print()
    if failed:
        print(f"{len(failed)} suite(s) failed: {', '.join(failed)}")
        return 1
    print(f"All {len(jobs) + len(SCRIPT_SUITES) + len(SOURCE_INVARIANT_TOOLS)} "
          f"suites passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

# Night Audit lives entirely in HotelServices: the business date, the accrual
# arithmetic and the idempotency guard are all defined there, so the suite has
# to run from that service root to import them.
NIGHT_AUDIT_SERVICE = "HotelServices"

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVICES_DIR = ROOT / "Backend" / "Services"
TESTS_DIR = ROOT / "Backend" / "tests"


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


def main() -> int:
    jobs = [
        (RBAC_SERVICE, "test_rbac.py"),
        (GATEWAY_SERVICE, "test_rbac_gateway.py"),
        (NIGHT_AUDIT_SERVICE, "test_night_audit.py"),
        # Reservation's rules are pure functions in the same service.
        (NIGHT_AUDIT_SERVICE, "test_reservation_rules.py"),
    ]
    # Billing exists only in these two, and both expose the same endpoint, so
    # the money guards run against each.
    jobs += [(svc, "test_bill_payment.py") for svc in BILLING_SERVICES]
    jobs += [(svc, "test_jwt_auth.py") for svc in SERVICES]

    failed = []
    for service, suite in jobs:
        label, ok, summary = run(service, suite)
        print(f"{'PASS' if ok else 'FAIL'}  {label:<40} {summary}")
        if not ok:
            failed.append(label)

    print()
    if failed:
        print(f"{len(failed)} suite(s) failed: {', '.join(failed)}")
        return 1
    print(f"All {len(jobs)} suites passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

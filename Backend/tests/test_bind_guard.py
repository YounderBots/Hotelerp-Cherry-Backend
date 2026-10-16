# -*- coding: utf-8 -*-
"""Every non-gateway service must refuse a public bind, at import.

    python Backend/tests/test_bind_guard.py

Run from the repository root. Each service is imported in its own subprocess,
with that service's directory as the working directory, because the guard is an
import-time check on `main.py` -- importing it here is the only honest way to
exercise it, and `configs` must resolve to the right service's package.

The case that matters most is the third: the deployment this guard was written
for was running `ASCEND_ENV=dev`, so a production-only check would have sailed
past it.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SERVICES = REPO / "Backend" / "Services"

# The gateway IS the front door; binding it publicly is the entire point.
UNGUARDED = {"LoginServices"}
GUARDED = ["UserServices", "MasterDataServices", "HotelServices",
           "RestaurantServices", "BarServices"]

PROBE = "import main; print('STARTED')"


def run(service: str, env_overrides: dict) -> tuple[bool, str]:
    child = {**os.environ}
    for key in ("SERVICE_HOST", "ALLOW_PUBLIC_BIND", "ASCEND_ENV"):
        child.pop(key, None)
    child["DB_AUTO_CREATE"] = "false"
    child.update({k: v for k, v in env_overrides.items() if v is not None})
    proc = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=str(SERVICES / service), env=child, capture_output=True, text=True,
    )
    return "STARTED" in proc.stdout, (proc.stderr or proc.stdout)


def main() -> int:
    failures = 0

    # ---- every guarded service refuses a public bind, in every env ----------
    cases = [
        ("SERVICE_HOST=0.0.0.0 ASCEND_ENV=dev", {"SERVICE_HOST": "0.0.0.0", "ASCEND_ENV": "dev"}, False),
        ("SERVICE_HOST=0.0.0.0 ASCEND_ENV=production", {"SERVICE_HOST": "0.0.0.0", "ASCEND_ENV": "production"}, False),
        ("SERVICE_HOST=10.0.0.5 (a LAN address)", {"SERVICE_HOST": "10.0.0.5"}, False),
        ("SERVICE_HOST=[::] (all IPv6)", {"SERVICE_HOST": "[::]"}, False),
        ("SERVICE_HOST=127.0.0.1", {"SERVICE_HOST": "127.0.0.1"}, True),
        ("SERVICE_HOST unset", {"SERVICE_HOST": None}, True),
        ("ALLOW_PUBLIC_BIND=true overrides", {"SERVICE_HOST": "0.0.0.0", "ALLOW_PUBLIC_BIND": "true"}, True),
    ]

    for service in GUARDED:
        for label, env, expect_start in cases:
            started, out = run(service, env)
            ok = started == expect_start
            failures += 0 if ok else 1
            print(f"  [{'PASS' if ok else 'FAIL'}] {service:<20} {label}")
            if not ok:
                for line in out.strip().splitlines()[-4:]:
                    print(f"         | {line}")

    # ---- and the refusal must SAY why, not just fail -------------------------
    for service in GUARDED:
        started, out = run(service, {"SERVICE_HOST": "0.0.0.0"})
        says_why = ("gateway" in out.lower() and "ALLOW_PUBLIC_BIND" in out)
        failures += 0 if says_why else 1
        print(f"  [{'PASS' if says_why else 'FAIL'}] {service:<20} refusal names the gateway and the override")

    # ---- the gateway itself is untouched -------------------------------------
    for service in UNGUARDED:
        started, out = run(service, {"SERVICE_HOST": "0.0.0.0"})
        ok = started
        failures += 0 if ok else 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {service:<20} may bind publicly (it is the front door)")

    print()
    if failures:
        print(f"{failures} case(s) failed")
        return 1
    print(f"bind guard: {len(GUARDED)} services x {len(cases)} cases, plus the "
          f"message check and the gateway exception -- all behave as documented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
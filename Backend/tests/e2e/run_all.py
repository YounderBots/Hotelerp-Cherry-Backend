#!/usr/bin/env python3
"""Run every end-to-end flow against a RUNNING stack.

    ./run.sh                              # start the six services first
    python Backend/tests/e2e/run_all.py

Unlike Backend/tests/run_all.py -- which is offline, in-process and needs no
database -- these drive the real gateway over HTTP, against the real MySQL
schemas, exactly as the SPA does. They are what catches the class of bug a unit
test cannot see: a validation that only exists in the browser, a permission row
the gateway has no mapping for, a column whose vocabulary the seed and the API
disagree about, an error that reaches the client as raw SQL.

WHAT THEY WRITE
    Each suite creates records and removes what it can. A reservation that has
    taken money cannot be deleted (correctly), so a run leaves a small number of
    settled test rows behind. Run against a demo or staging database, never
    against a property's live one.

Exit code 0 when every suite passes, 1 otherwise.
"""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GATEWAY = os.environ.get("E2E_GATEWAY", "http://127.0.0.1:8000")

# security.py runs LAST on purpose: one of its checks is that repeated failed
# logins are rate limited, which exhausts the gateway's per-minute budget for
# this peer. api.login() waits the window out, so ordering is a courtesy rather
# than a requirement -- but it keeps a clean run from pausing for a minute.
SUITES = [
    ("crud.py", "Master Data: create/read/update/delete and validation"),
    ("crud2.py", "Master Data: country, discount, tax, room types"),
    ("reservation_flow.py", "book -> check in -> take payment -> check out"),
    ("fnb_flow.py", "restaurant and bar: order -> ticket -> bill -> payment"),
    ("hotel_ops_flow.py", "housekeeping, incidents, enquiries, night audit"),
    ("security.py", "authentication, tokens, authorisation, rate limiting"),
]


def gateway_is_up() -> bool:
    try:
        with urllib.request.urlopen(f"{GATEWAY}/healthz", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def main() -> int:
    if not gateway_is_up():
        print(f"ERROR: no gateway answering on {GATEWAY}/healthz")
        print("       Start the stack first:  ./run.sh")
        return 1

    results = []
    for name, description in SUITES:
        print(f"\n{'=' * 70}\n{name}  --  {description}\n{'=' * 70}")
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, name)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        tail = (proc.stdout or "").strip().splitlines()
        summary = next((line for line in reversed(tail) if "passed" in line), "(no summary)")
        ok = proc.returncode == 0 and "0 failed" in summary
        if not ok:
            print(proc.stdout)
            if proc.stderr:
                print(proc.stderr)
        else:
            print(f"  {summary.strip()}")
        results.append((name, ok, summary.strip()))

    print(f"\n{'=' * 70}")
    for name, ok, summary in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<26} {summary}")
    failed = [n for n, ok, _ in results if not ok]
    if failed:
        print(f"\n{len(failed)} suite(s) failed: {', '.join(failed)}")
        return 1
    print(f"\nAll {len(results)} end-to-end suites passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

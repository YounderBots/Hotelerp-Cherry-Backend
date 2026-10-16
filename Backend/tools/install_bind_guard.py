# -*- coding: utf-8 -*-
"""Copy the loopback bind guard into the other four non-gateway services.

    python Backend/tools/install_bind_guard.py [--check]

`--check` reports which services have it instead of writing, so this doubles as
the verification that all five stay in step.

WHY A SCRIPT AND NOT FOUR EDITS
    The guard is deliberately identical in all four: it is a security control,
    and four independently-edited copies of a security control is how they drift
    apart. Generated from one source, verified as one source.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVICES_DIR = ROOT / "Backend" / "Services"

# The five services that must NOT be externally reachable. LoginServices is the
# gateway: it is the front door, and binding it publicly is the point.
GUARDED = ["UserServices", "MasterDataServices", "HotelServices",
           "RestaurantServices", "BarServices"]

MARKER = "_LOOPBACK_HOSTS = "


def block(service: str) -> str:
    return f'''
# ---------------------------------------------------------------------------
# Bind address -- the gateway is the only door
# ---------------------------------------------------------------------------
# Every external request is meant to arrive through the login gateway, which is
# where the 279-row permission map is applied. That model has a premise, stated
# in LoginServices/resources/rbac.py:
#
#     "the services themselves bind to 127.0.0.1 and are not routable from
#      outside. Enforcing once at the proxy therefore covers the whole external
#      surface."
#
# On 2026-10-16 that premise was false: all five backend services were answering
# on the deployment's PUBLIC IP, so the permission map could be stepped around by
# addressing a service port directly. It was found while auditing a gateway whose
# authorisation was switched off, which is the worst possible pairing -- and
# neither layer knew.
#
# start-network.ps1 and run.sh already read SERVICE_HOST and pass --host to
# uvicorn, so a run through the launcher is correct. This is the check for every
# OTHER way a process starts -- `uvicorn main:app` typed by hand, a process
# manager, a container -- where nothing reads the .env at all.
#
# It runs at import, which is before uvicorn binds, so a wrong address fails the
# start instead of quietly opening a port. It is NOT limited to production: the
# deployment in question was running ASCEND_ENV=dev, so a production-only check
# would not have caught it.
#
# Deliberately opt-out rather than opt-in, for the same reason the gateway's RBAC
# mode is: ALLOW_PUBLIC_BIND=true is an explicit, greppable decision by somebody
# who knows why. The default has to be the safe one.
#
# Installed identically into all five services by
# Backend/tools/install_bind_guard.py, so they cannot drift apart.
_LOOPBACK_HOSTS = {{"", "127.0.0.1", "::1", "localhost", "loopback"}}


def _assert_private_bind() -> None:
    host = str(os.getenv("SERVICE_HOST", "127.0.0.1")).strip()
    if host.lower() in _LOOPBACK_HOSTS:
        return
    if str(os.getenv("ALLOW_PUBLIC_BIND", "")).strip().lower() in ("1", "true", "yes"):
        print(
            f"[{service.lower()}] WARNING: binding "
            f"{{host}}:{{os.getenv('SERVICE_PORT', '?')}} because "
            f"ALLOW_PUBLIC_BIND is set. This service is meant to be reached only "
            f"through the login gateway; a public bind lets a caller address it "
            f"directly and bypass the gateway's permission map entirely.",
            file=sys.stderr,
        )
        return
    raise RuntimeError(
        f"{service} would bind {{host}}, which is reachable from outside this "
        f"machine. Only the login gateway is meant to be externally reachable: "
        f"the other five services are addressed through it, and the permission "
        f"map that authorises them is applied there. A service on a public "
        f"address can be called directly, skipping that map entirely.\\n"
        f"  Set SERVICE_HOST=127.0.0.1 in "
        f"Backend/Services/{service}/.env, or start it with start-network.ps1 / "
        f"run.sh, which bind loopback by default.\\n"
        f"  If a public bind is genuinely intended, set ALLOW_PUBLIC_BIND=true "
        f"and make sure you have accepted that the gateway is not the only "
        f"thing authorising this service."
    )


_assert_private_bind()
'''


def ensure_imports(text: str) -> str:
    if not re.search(r"^import sys$", text, re.M):
        # Keep the stdlib block alphabetical, which is how it is written today.
        text = re.sub(r"^import os$", "import os\nimport sys", text, count=1, flags=re.M)
    return text


def has_guard(text: str) -> bool:
    return MARKER in text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="actually rewrite the files. Without it the tool only "
                         "reports, so running it can never change source by "
                         "accident -- which is also why the suite can call it as "
                         "a regression check.")
    args = ap.parse_args()

    problems = 0
    for name in GUARDED:
        path = SERVICES_DIR / name / "main.py"
        if not path.is_file():
            print(f"  MISSING  {name}/main.py")
            problems += 1
            continue
        text = path.read_text(encoding="utf-8")
        present = has_guard(text)
        if present:
            # Keep it honest about the service it names in its own message.
            ok = f"{name}" in text.split(MARKER, 1)[1][:4000]
            print(f"  {'ok     ' if ok else 'WRONG  '} {name}")
            problems += 0 if ok else 1
            continue
        if not args.apply:
            print(f"  MISSING {name}")
            problems += 1
            continue

        anchor = f'if _configs.SERVICE_NAME != "{name}":'
        idx = text.find(anchor)
        if idx == -1:
            print(f"  ANCHOR NOT FOUND in {name}/main.py -- install by hand")
            problems += 1
            continue
        # ensure_imports() rewrites the stdlib block near the top, which shifts
        # every offset after it. It has to run BEFORE the insertion point is
        # located, or the guard lands inside whatever statement happens to be
        # there -- which is how the first run split `f"sys.path."` in half.
        text = ensure_imports(text)
        idx = text.find(anchor)
        # Insert before the next top-level import, which is the first line of
        # the block the service's own configuration depends on.
        nxt = text.find("\nfrom ", idx)
        if nxt == -1:
            print(f"  COULD NOT FIND AN INSERTION POINT in {name}/main.py")
            problems += 1
            continue
        text = text[:nxt + 1] + block(name) + text[nxt + 1:]
        path.write_text(text, encoding="utf-8")
        print(f"  installed {name}")

    print()
    if problems:
        print(f"{problems} service(s) do not carry the guard")
        return 1
    print(f"all {len(GUARDED)} non-gateway services carry the loopback bind guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Pre-production check for a deployed HotelERP.

    python Backend/tools/preflight.py                     # check localhost
    python Backend/tools/preflight.py --host 10.0.0.5     # check a server
    python Backend/tools/preflight.py --host x --gateway 9010 \
        --services hotel=9005,user=9020,masterdata=9015,bar=9025,restaurant=9030

Read-only. It logs in and issues GETs; it writes nothing.

WHY THIS EXISTS
    A deployment can pass every unit test, serve every page, answer "ok" on
    /healthz -- and still be wrong in ways only the running environment can
    show. All four checks below are things that were TRUE of a real deployment
    of this system while it looked healthy:

      * the reservation module answered 500 on every request, because
        HotelServices could not read the Master Data schema across databases;
      * the permission system was in audit mode, so every role could reach
        every endpoint and the denials were only being logged;
      * all five internal services were published to the internet, so the
        gateway that does the permission checks could simply be stepped around;
      * the shared demo password was still live.

    None of those is visible from the code. Each is a property of the machine
    the code was deployed onto.

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_SERVICES = {
    "hotel": 8040, "user": 8020, "masterdata": 8030,
    "restaurant": 8050, "bar": 8060,
}
DEFAULT_GATEWAY = 8000

FAILS: list[str] = []
WARNS: list[str] = []


def ok(label, detail=""):
    print(f"  PASS  {label}" + (f"  -- {detail}" if detail else ""))


def bad(label, detail=""):
    print(f"  FAIL  {label}" + (f"  -- {detail}" if detail else ""))
    FAILS.append(label)


def warn(label, detail=""):
    print(f"  WARN  {label}" + (f"  -- {detail}" if detail else ""))
    WARNS.append(label)


def get(url, token=None, timeout=20):
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as exc:                                   # noqa: BLE001
        return 0, str(exc).encode()


def login(host, port, email, password, timeout=25):
    req = urllib.request.Request(
        f"http://{host}:{port}/login_post",
        data=json.dumps({"email": email, "password": password}).encode(),
        method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:200]}
    except Exception as exc:                                   # noqa: BLE001
        return {"_error": 0, "_body": str(exc)[:200]}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--gateway", type=int, default=DEFAULT_GATEWAY)
    ap.add_argument("--services", default="",
                    help="name=port,name=port (default: the local ports)")
    ap.add_argument("--admin-email", default="admin@cherryhotel.com")
    ap.add_argument("--admin-password", default="Hotel@2026")
    ap.add_argument("--low-email", default="rahul.nair@cherryhotel.com",
                    help="a LOW-privilege account, used to prove the "
                         "permission checks actually refuse something")
    ap.add_argument("--low-password", default="Hotel@2026")
    args = ap.parse_args()

    services = dict(DEFAULT_SERVICES)
    if args.services:
        services = {}
        for pair in args.services.split(","):
            name, _, port = pair.partition("=")
            services[name.strip()] = int(port)

    host = args.host
    print(f"HotelERP preflight against {host}\n")

    # -- 1. is anything answering ------------------------------------------
    print("=== 1. the gateway answers ===")
    st, _ = get(f"http://{host}:{args.gateway}/healthz")
    if st == 200:
        ok(f"gateway on :{args.gateway}")
    else:
        bad(f"gateway on :{args.gateway}", f"status {st}")
        print("\nNothing else can be checked without the gateway.")
        return 1

    # -- 2. dependencies each service cannot work without -------------------
    print("\n=== 2. each service's own dependencies ===")
    hotel_port = services.get("hotel")
    if hotel_port:
        st, body = get(f"http://{host}:{hotel_port}/readyz")
        if st == 200:
            ok("hotel service reports ready")
        elif st == 503:
            try:
                detail = json.loads(body.decode())["checks"]["masterdata"]["detail"]
            except Exception:                                  # noqa: BLE001
                detail = body.decode()[:180]
            bad("hotel service is NOT ready", detail)
        elif st == 404:
            warn("hotel /readyz not deployed",
                 "this build predates the readiness probe; upgrade to see "
                 "cross-schema failures at deploy time rather than as 500s")
        else:
            bad("hotel /readyz", f"status {st}")

    # -- 3. are the permission checks actually enforcing --------------------
    print("\n=== 3. the permission checks refuse something ===")
    low = login(host, args.gateway, args.low_email, args.low_password)
    if "_error" in low:
        warn("could not sign in as the low-privilege account",
             f"{low['_error']} {low.get('_body','')}")
    else:
        token = low["access_token"]
        claim_pages = sorted((low.get("menus") or [])
                             and [m.get("path") for m in low["menus"]] or [])
        # An HRM read this account holds no permission for.
        st, _ = get(f"http://{host}:{args.gateway}/user/users", token)
        if st in (401, 403):
            ok("a role without HRM is refused /user/users", f"status {st}")
        elif st == 200:
            bad("RBAC IS NOT ENFORCING",
                f"{args.low_email} holds {claim_pages} yet read /user/users. "
                "Set RBAC_GATEWAY_MODE=enforce on the gateway; the default is "
                "'audit', which only logs what it would have denied.")
        else:
            warn("unexpected status for the RBAC probe", f"status {st}")

        # -- 4. can the gateway be stepped around -------------------------
        print("\n=== 4. the internal services are not reachable directly ===")
        loopback = host in ("127.0.0.1", "localhost", "::1")
        if loopback:
            print("  SKIP  this check is meaningless against loopback --")
            print("        every service is reachable from its own machine by")
            print("        design. Run it from ANOTHER host, pointed at the")
            print("        server's public address, for the answer that matters.")
        else:
            for name, port in sorted(services.items()):
                try:
                    with socket.create_connection((host, port), timeout=5):
                        reachable = True
                except OSError:
                    reachable = False
                if not reachable:
                    ok(f"{name} :{port} is not reachable from outside")
                    continue
                st, _ = get(f"http://{host}:{port}/healthz")
                if st == 0:
                    ok(f"{name} :{port} accepts no HTTP")
                else:
                    bad(f"{name} :{port} IS REACHABLE FROM OUTSIDE",
                        "every permission check lives in the gateway, so a "
                        "caller who can reach this port skips them entirely. "
                        "Bind it to 127.0.0.1 (SERVICE_HOST) or firewall the "
                        "port so only the gateway can reach it.")

    # -- 5. the shipped demo password -------------------------------------
    print("\n=== 5. the seeded demo password ===")
    admin = login(host, args.gateway, args.admin_email, args.admin_password)
    if "_error" in admin:
        ok("the seeded admin password no longer works")
    else:
        bad("THE SEEDED DEMO PASSWORD STILL WORKS",
            f"{args.admin_email} still signs in with the password published in "
            "Backend/db/*/README.md and in the seed source. Change it before "
            "this is reachable by anyone.")

    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) FAILED, {len(WARNS)} warning(s)")
        for f in FAILS:
            print(f"   - {f}")
        print("\nNOT READY FOR PRODUCTION.")
        return 1
    print(f"All checks passed, {len(WARNS)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

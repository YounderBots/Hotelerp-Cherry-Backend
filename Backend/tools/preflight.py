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
    show. All five checks below are things that were TRUE of a real deployment
    of this system while it looked healthy:

      * the reservation module answered 500 on every request, because
        HotelServices could not read the Master Data schema across databases;
      * the permission system was in audit mode, so every role could reach
        every endpoint and the denials were only being logged;
      * all five internal services were published to the internet, so the
        gateway that does the permission checks could simply be stepped around;
      * the shared demo password was still live;
      * every image the database pointed at was missing from the server,
        because restoring the release loaded the SQL but never copied the
        files -- 200s everywhere, and not one picture in the application.

    None of those is visible from the code. Each is a property of the machine
    the code was deployed onto.

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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

# The password every seeded account ships with, published in the seed source
# and in Backend/db/*/README.md. Check 5 exists to assert it no longer works.
SEEDED_PASSWORD = "Hotel@2026"

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
    status, body, _ctype = get_typed(url, token, timeout)
    return status, body


def get_typed(url, token=None, timeout=20):
    """As get(), but also returns the response Content-Type.

    Check 6 needs it: a static mount that has lost its files answers the image
    URL with a JSON 404 body, and "did this return bytes, and were they an
    image?" is the question being asked.
    """
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers.get("Content-Type", "")
    except Exception as exc:                                   # noqa: BLE001
        return 0, str(exc).encode(), ""


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


# Where stored image paths can be read back from, per gateway prefix. One
# cheap list endpoint per module that is known to carry an image column.
IMAGE_SOURCES = {
    "masterdata": ["/room"],
    "user": ["/users"],
    "restaurant": ["/menu"],
    "bar": ["/menu"],
    "hotel": ["/roomincident_log"],
}

# Stored paths look like "/templates/static/upload_image/<uuid>.jpg".
STORED_PATH = re.compile(
    r'"(/templates/static/[^"]+\.(?:jpg|jpeg|png|webp|gif))"', re.I)

# How many distinct files to actually fetch per module. The question is "is the
# static tree populated", not "is every byte present" -- verify_seed.py answers
# the second, against the disk, where it is cheap.
SAMPLE_PER_MODULE = 5


def check_images(host, gateway, token):
    """Do the paths the database serves have files behind them?

    WHY THIS CHECK EXISTS
        Restoring a release is two steps -- load the SQL, then copy
        `Backend/db/<release>/uploads/` into the services' static trees. The
        second is easy to skip, and skipping it is invisible from the API: the
        rows are all there, every endpoint answers 200, and the only symptom is
        that no picture in the application loads.

        That is what happened on the deployment at 168.231.103.18. Checks 1-5
        all passed on the image question because none of them asked it.

        Fix with: python Backend/tools/restore_uploads.py
    """
    print("\n=== 6. the stored images actually serve ===")
    if not token:
        warn("could not check images", "no usable sign-in; pass --low-password")
        return

    checked = failed = 0
    for module, endpoints in sorted(IMAGE_SOURCES.items()):
        paths: list[str] = []
        denied = False
        for ep in endpoints:
            st, body = get(f"http://{host}:{gateway}/{module}{ep}", token)
            if st in (401, 403):
                denied = True
                continue
            if st != 200:
                continue
            for p in STORED_PATH.findall(body.decode("utf-8", "replace")):
                if p not in paths:
                    paths.append(p)

        if not paths:
            if denied:
                # Not a fault: a low-privilege token is SUPPOSED to be refused
                # here, and check 3 is the one that cares about that.
                print(f"  SKIP  {module} -- this account may not read it")
            else:
                print(f"  SKIP  {module} -- no stored image paths found")
            continue

        broken = []
        for p in paths[:SAMPLE_PER_MODULE]:
            st, body, ctype = get_typed(f"http://{host}:{gateway}/{module}{p}", token)
            checked += 1
            if st != 200 or not ctype.lower().startswith("image/"):
                broken.append((p, st))
                failed += 1

        if broken:
            p, st = broken[0]
            bad(f"{module}: stored images do not load",
                f"{len(broken)} of {len(paths[:SAMPLE_PER_MODULE])} sampled "
                f"failed (of {len(paths)} referenced) -- e.g. {p} -> {st}. The "
                "database points at files that are not on the server. Run "
                "`python Backend/tools/restore_uploads.py` on the server, from "
                "the release whose SQL is loaded.")
        else:
            ok(f"{module}: stored images load",
               f"{len(paths[:SAMPLE_PER_MODULE])} of {len(paths)} sampled")

    if checked and not failed:
        ok("every sampled image was served", f"{checked} file(s)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--gateway", type=int, default=DEFAULT_GATEWAY)
    ap.add_argument("--services", default="",
                    help="name=port,name=port (default: the local ports)")
    ap.add_argument("--admin-email", default="admin@cherryhotel.com")
    ap.add_argument("--admin-password", default=SEEDED_PASSWORD,
                    help="only used by check 5, which asserts that the SEEDED "
                         "password no longer works. Leave it alone.")
    ap.add_argument("--low-email",
                    default=os.getenv("PREFLIGHT_LOW_EMAIL", "rahul.nair@cherryhotel.com"),
                    help="a LOW-privilege account, used to prove the "
                         "permission checks actually refuse something")
    # Check 3 is the most important one here, and it needs a working sign-in.
    # After rotate_passwords.py has done its job the seeded password is gone --
    # which is the point -- so this has to be supplied, or the check that asks
    # "is RBAC actually enforcing?" quietly degrades to a warning on exactly the
    # deployments that are ready for production.
    ap.add_argument("--low-password",
                    default=os.getenv("PREFLIGHT_LOW_PASSWORD", SEEDED_PASSWORD),
                    help="password for --low-email. Set it, or export "
                         "PREFLIGHT_LOW_PASSWORD, once the seeded password has "
                         "been rotated.")
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
            # Report every failing check, not just the first: the Master Data
            # and Users schemas are separate grants that fail separately, and
            # naming only one sends the operator back for a second round trip.
            details = []
            try:
                checks = json.loads(body.decode())["checks"]
                details = [f"{name}: {c['detail']}"
                           for name, c in checks.items() if not c.get("ok")]
            except Exception:                                  # noqa: BLE001
                pass
            if not details:
                details = [body.decode()[:180]]
            bad("hotel service is NOT ready", details[0])
            for extra in details[1:]:
                print(f"        {extra}")
        elif st == 404:
            warn("hotel /readyz not deployed",
                 "this build predates the readiness probe; upgrade to see "
                 "cross-schema failures at deploy time rather than as 500s")
        else:
            bad("hotel /readyz", f"status {st}")

    # -- 3. are the permission checks actually enforcing --------------------
    print("\n=== 3. the permission checks refuse something ===")
    # Kept for check 6, which needs any working token to read the stored image
    # paths back out of the API.
    any_token = None
    low = login(host, args.gateway, args.low_email, args.low_password)
    if "_error" in low:
        detail = f"{low['_error']} {low.get('_body','')}"
        if args.low_password == SEEDED_PASSWORD:
            detail += (" -- the seeded password has been rotated (good). Pass "
                       "--low-password, or export PREFLIGHT_LOW_PASSWORD, so "
                       "this check can run.")
        warn("could not sign in as the low-privilege account", detail)
    else:
        token = any_token = low["access_token"]
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
        # A failure, but it does hand check 6 a token that can read every
        # module -- so the images get checked on exactly the deployments that
        # have not been hardened yet.
        any_token = admin["access_token"]
        bad("THE SEEDED DEMO PASSWORD STILL WORKS",
            f"{args.admin_email} still signs in with the password published in "
            "Backend/db/*/README.md and in the seed source. Change it before "
            "this is reachable by anyone.")

    # -- 6. the images the database points at ------------------------------
    check_images(host, args.gateway, any_token)

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

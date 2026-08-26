#!/usr/bin/env python3
"""Pre-flight check on the six production .env files.

Run this on the server after make_prod_env.py and BEFORE starting anything.
It catches the failure modes that are silent at boot but fatal in use -- most
importantly a JWT_SECRET_KEY that differs between the gateway and a service,
which produces a login that appears to succeed while every subsequent request
401s.

    python verify_prod_env.py            # check the real .env files
    python verify_prod_env.py --dir /tmp/envs   # check staged files first

Exit code 0 = safe to start. Non-zero = do not launch.
Secrets are compared by hash; no secret value is ever printed.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

SERVICES = {
    "LoginServices":      ("0.0.0.0",   "8000", "hotelerp_users"),
    "UserServices":       ("127.0.0.1", "8020", "hotelerp_users"),
    "MasterDataServices": ("127.0.0.1", "8030", "hotelerp_masterdata"),
    "HotelServices":      ("127.0.0.1", "8040", "hotelerp_hotel"),
    "RestaurantServices": ("127.0.0.1", "8050", "hotelerp_restaurant"),
    "BarServices":        ("127.0.0.1", "8060", "hotelerp_bar"),
}

SHARED_KEYS = ("JWT_SECRET_KEY", "SESSION_SECRET", "JWT_ISSUER")
DEV_MARKERS = ("dev-only", "changeme", "secret", "test", "password")

errors: list[str] = []
warnings: list[str] = []


def fail(m: str) -> None:
    errors.append(m)


def warn(m: str) -> None:
    warnings.append(m)


def parse(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def digest(v: str) -> str:
    return hashlib.sha256(v.encode()).hexdigest()[:12]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None,
                    help="Directory of staged <Service>.env files")
    args = ap.parse_args()

    base = Path(__file__).resolve().parent
    staged = Path(args.dir).resolve() if args.dir else None

    envs = {}
    for svc in SERVICES:
        p = (staged / f"{svc}.env") if staged else (base / svc / ".env")
        if not p.exists():
            fail(f"{svc}: no .env at {p}")
            continue
        envs[svc] = parse(p)

    if not envs:
        print("No .env files found. Run make_prod_env.py first.", file=sys.stderr)
        return 2

    # --- the shared-secret invariant, the one that fails silently -----------
    print("Shared-secret agreement (must be identical in all six)")
    print("-" * 62)
    for key in SHARED_KEYS:
        seen = {}
        for svc, env in envs.items():
            v = env.get(key, "")
            if not v:
                fail(f"{svc}: {key} is empty -- production startup will refuse")
                continue
            seen.setdefault(digest(v), []).append(svc)
        if len(seen) == 1:
            h = next(iter(seen))
            print(f"  OK        {key:22} all six agree (sha {h})")
        elif len(seen) > 1:
            print(f"  MISMATCH  {key:22} {len(seen)} different values:")
            for h, svcs in seen.items():
                print(f"              sha {h}  {', '.join(svcs)}")
            fail(f"{key} differs between services -- every request will 401")

    # --- per-service correctness -------------------------------------------
    print()
    print("Per-service configuration")
    print("-" * 62)
    for svc, (host, port, db) in SERVICES.items():
        env = envs.get(svc)
        if not env:
            continue
        problems = []

        if env.get("ASCEND_ENV", "").lower() not in ("production", "prod"):
            problems.append(f"ASCEND_ENV={env.get('ASCEND_ENV')!r} (want production)")

        if env.get("SERVICE_PORT") != port:
            problems.append(f"SERVICE_PORT={env.get('SERVICE_PORT')} (want {port})")
        if env.get("SERVICE_HOST") != host:
            problems.append(f"SERVICE_HOST={env.get('SERVICE_HOST')} (want {host})")

        dsn = env.get("DB_URI", "")
        if not dsn:
            problems.append("DB_URI missing -- production config raises at import")
        else:
            if not dsn.rsplit("/", 1)[-1].split("?")[0] == db:
                problems.append(f"DB_URI points at {dsn.rsplit('/',1)[-1]!r} (want {db})")
            hostpart = dsn.split("@")[-1].split("/")[0] if "@" in dsn else ""
            if hostpart.startswith(("127.0.0.1", "localhost")):
                warn(f"{svc}: DB_URI still points at localhost ({hostpart})")

        cors = env.get("CORS_ALLOWED_ORIGINS", "")
        if not cors:
            problems.append("CORS_ALLOWED_ORIGINS empty -- the SPA cannot call the API")
        else:
            origins = [o.strip() for o in cors.split(",") if o.strip()]
            if any(o == "*" for o in origins):
                problems.append("CORS contains '*' -- config strips it, leaving none")
            if any(o.startswith("http://") and "localhost" not in o
                   and "127.0.0.1" not in o for o in origins):
                warn(f"{svc}: plain-http CORS origin; session cookies are "
                     f"https-only in production")
            if any("127.0.0.1" in o or "localhost" in o or "192.168." in o
                   for o in origins):
                warn(f"{svc}: CORS still lists a dev/LAN origin")

        for key in ("JWT_SECRET_KEY", "SESSION_SECRET"):
            v = env.get(key, "")
            if v and len(v) < 32:
                problems.append(f"{key} is only {len(v)} chars (want >= 32)")
            if v and any(m in v.lower() for m in DEV_MARKERS):
                problems.append(f"{key} looks like a development placeholder")

        if problems:
            print(f"  FAIL      {svc}")
            for pr in problems:
                print(f"              - {pr}")
                fail(f"{svc}: {pr}")
        else:
            print(f"  OK        {svc:20} port {port}, db {db}")

    # --- verdict ------------------------------------------------------------
    print()
    print("=" * 62)
    for w in warnings:
        print(f"WARN   {w}")
    if errors:
        print(f"\n{len(errors)} problem(s) -- DO NOT START")
        return 1
    print("\nAll checks passed. Safe to start the services.")
    if warnings:
        print(f"({len(warnings)} warning(s) above -- review before launch.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

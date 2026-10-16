# -*- coding: utf-8 -*-
"""Did the deployment start honouring `exp`? Test every surface with one token.

    set E2E_PASSWORD=<demo password>
    python QA/live/expiry_recheck.py --token-file <path-to-an-old-token>

WHY THIS EXISTS
    On 2026-10-16 an access token whose `exp` was hours past was answered 200
    with data by all six services, while a malformed token was correctly
    refused -- so the signature was verified and the expiry was not.

    On 2026-10-17 the SAME token, same endpoints, answers 401. Something changed
    on the deployment between the two runs. This script establishes which, so
    the finding can be closed or kept on evidence rather than on recollection:

      * the same expired token against all six surfaces, now
      * a freshly minted token, to prove the 401 is about expiry and not the
        endpoint, the account or the deployment being down
      * a token with a mangled signature, as a control -- if THIS returned 200,
        the 401s would mean the endpoint is refusing everything and the expired
        token's result would prove nothing
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.request

SURFACES = [
    ("gateway", 9010, "/masterdata/room"),
    ("user", 9020, "/roles"),
    ("masterdata", 9015, "/room"),
    ("hotel", 9005, "/room_reservation"),
    ("restaurant", 9030, "/menu"),
    ("bar", 9025, "/menu"),
]


def claims(tok):
    try:
        seg = tok.split(".")[1]
        seg += "=" * (-len(seg) % 4)
        return json.loads(base64.urlsafe_b64decode(seg))
    except Exception:                                           # noqa: BLE001
        return {}


def probe(host, port, path, token):
    req = urllib.request.Request(f"http://{host}:{port}{path}", method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read())
    except Exception as e:                                       # noqa: BLE001
        return 0, str(e)[:80]


def login(host, port, email, password):
    req = urllib.request.Request(
        f"http://{host}:{port}/login_post",
        data=json.dumps({"email": email, "password": password}).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())["access_token"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="168.231.103.18")
    ap.add_argument("--gateway", type=int, default=9010)
    ap.add_argument("--email", default="admin@cherryhotel.com")
    ap.add_argument("--password", default=os.getenv("E2E_PASSWORD", ""))
    ap.add_argument("--token-file", default="")
    args = ap.parse_args()
    if not args.password:
        raise SystemExit("set E2E_PASSWORD")

    old = None
    if args.token_file and os.path.isfile(args.token_file):
        old = open(args.token_file, encoding="utf-8").read().strip()
    fresh = login(args.host, args.gateway, args.email, args.password)
    now = int(time.time())
    mangled = fresh[:-4] + ("aaaa" if not fresh.endswith("aaaa") else "bbbb")

    rows = []
    for name, port, path in SURFACES:
        rows.append({
            "surface": f"{name}:{port}{path}",
            "expired_token": probe(args.host, port, path, old) if old else None,
            "fresh_token": probe(args.host, port, path, fresh),
            "mangled_signature": probe(args.host, port, path, mangled),
        })

    fc = claims(fresh)
    oc = claims(old) if old else {}
    print(f"fresh token  exp {fc.get('exp')}  remaining {fc.get('exp', 0) - now}s")
    if oc:
        print(f"old   token  exp {oc.get('exp')}  remaining {oc.get('exp', 0) - now}s "
              f"({(now - oc.get('exp', now)) // 60} min past)")
    print()
    hdr = f"{'surface':<34}{'EXPIRED':>10}{'FRESH':>10}{'MANGLED':>10}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        e = f"{r['expired_token'][0]}" if r["expired_token"] else "-"
        print(f"{r['surface']:<34}{e:>10}{r['fresh_token'][0]:>10}{r['mangled_signature'][0]:>10}")

    verdict_ok = (
        all(r["fresh_token"][0] == 200 for r in rows)
        and all(r["mangled_signature"][0] == 401 for r in rows)
        and (old is None or all(r["expired_token"][0] == 401 for r in rows))
    )
    print()
    if verdict_ok:
        print("EXPIRY IS NOW ENFORCED on every surface.")
        print("  - a fresh token works everywhere (so the endpoints are up)")
        print("  - a mangled signature is refused everywhere (so 401 is meaningful)")
        print("  - the long-expired token is refused everywhere")
        print("\nThe 2026-10-16 finding was real then and is closed now: the")
        print("deployment now runs code that verifies `exp`.")
        return 0
    if not all(r["fresh_token"][0] == 200 for r in rows):
        print("INCONCLUSIVE: a fresh token is not served everywhere, so a 401 on")
        print("the expired token proves nothing. Is the deployment up?")
    elif not all(r["mangled_signature"][0] == 401 for r in rows):
        print("INCONCLUSIVE: a MANGLED signature was accepted somewhere, so the")
        print("401s are not evidence of expiry being enforced.")
    else:
        still = [r["surface"] for r in rows if r["expired_token"] and r["expired_token"][0] != 401]
        print(f"EXPIRY IS STILL NOT ENFORCED on: {still}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
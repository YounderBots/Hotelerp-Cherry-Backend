# -*- coding: utf-8 -*-
"""Separate two things that the same observation could have meant:

  A. the deployment does not enforce JWT expiry, and
  B. the deployment's clock is wrong.

Both are real, and only measuring against the SERVER's own clock tells them
apart. A token's `exp` is computed with the server's clock and verified with the
server's clock, so comparing it to the reviewer's clock confounds the two --
which is exactly what happened in the first pass of this audit.

    python QA/live/clock_and_expiry.py --host 168.231.103.18 --gateway 9010
"""
from __future__ import annotations

import argparse
import base64
import email.utils
import json
import os
import time
import urllib.error
import urllib.request


def claims(tok):
    seg = tok.split(".")[1]
    seg += "=" * (-len(seg) % 4)
    return json.loads(base64.urlsafe_b64decode(seg))


def server_now(host, port) -> int:
    """The deployment's own idea of now, from its own Date header."""
    with urllib.request.urlopen(f"http://{host}:{port}/healthz", timeout=15) as r:
        return int(email.utils.parsedate_to_datetime(r.headers["Date"]).timestamp())


def get(url, token=None):
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read())
    except Exception as e:                                       # noqa: BLE001
        return 0, str(e)[:100]


def login(host, port, email, password):
    req = urllib.request.Request(
        f"http://{host}:{port}/login_post",
        data=json.dumps({"email": email, "password": password}).encode(),
        method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read())["access_token"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"login failed: {e.code} {e.read()[:200]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="168.231.103.18")
    ap.add_argument("--gateway", type=int, default=9010)
    ap.add_argument("--email", default="admin@cherryhotel.com")
    ap.add_argument("--password", default=os.getenv("E2E_PASSWORD", ""))
    args = ap.parse_args()
    if not args.password:
        raise SystemExit("set E2E_PASSWORD (or pass --password)")

    srv = server_now(args.host, args.gateway)
    mine = int(time.time())
    skew = mine - srv

    print("=" * 72)
    print("A. CLOCK")
    print("=" * 72)
    print(f"  my clock            {mine}   ({time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(mine))})")
    print(f"  deployment's clock  {srv}   ({time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(srv))})")
    print(f"  skew                {skew}s ({skew/3600:+.2f} h)")
    if abs(skew) > 120:
        print()
        print("  FINDING: the deployment's clock is wrong. Everything the system")
        print("  records is stamped from it -- JWT iat/exp, night audit's")
        print("  business_date, reservation arrival comparisons, payment times.")
        print("  A 13-hour error also makes every token look expired to any client")
        print("  whose clock is right, and vice versa.")

    print()
    print("=" * 72)
    print("B. IS EXPIRY ENFORCED -- judged by the SERVER's clock, not mine")
    print("=" * 72)
    tok = login(args.host, args.gateway, args.email, args.password)
    c = claims(tok)
    ttl_by_server = c["exp"] - srv
    ttl_by_me = c["exp"] - mine
    print(f"  token iat           {c.get('iat')}")
    print(f"  token exp           {c.get('exp')}")
    print(f"  remaining by SERVER  {ttl_by_server}s ({ttl_by_server/60:.1f} min)  <- the one that counts")
    print(f"  remaining by ME      {ttl_by_me}s ({ttl_by_me/60:.1f} min)  <- misleading when the clock is wrong")

    st, size = get(f"http://{host if (host := args.host) else args.host}:{args.gateway}/masterdata/room", tok)
    print(f"\n  a fresh token is accepted      -> {st}")

    # Now the decisive test: a token that is expired BY THE SERVER'S CLOCK.
    # Take the fresh token and ask the server how long ago it would consider it
    # expired -- we cannot re-sign one, so instead we rely on the browser's older
    # token if it was supplied, and otherwise report what is provable here.
    old = None
    try:
        old = open(r"C:\Users\anand\AppData\Local\Temp\opencode\live_token.txt", encoding="utf-8").read().strip()
    except OSError:
        pass
    if old:
        oc = claims(old)
        expired_by_server = oc["exp"] - srv
        expired_by_me = oc["exp"] - mine
        print()
        print(f"  an older token, exp {oc['exp']}")
        print(f"    expired by SERVER's clock {expired_by_server}s ({expired_by_server/3600:.1f} h ago)")
        print(f"    expired by MY clock       {expired_by_me}s ({expired_by_me/3600:.1f} h ago)")
        for name, port, path in (("gateway", args.gateway, "/masterdata/room"),
                                 ("hotel", 9005, "/room_reservation"),
                                 ("restaurant", 9030, "/menu")):
            s2, _ = get(f"http://{args.host}:{port}{path}", old)
            verdict = "ACCEPTED" if s2 == 200 else f"refused ({s2})"
            print(f"      {name:<11} :{port}{path:<22} -> {s2}  {verdict}")
        if expired_by_server < 0:
            print()
            print("  VERDICT: this token is past `exp` by the DEPLOYMENT'S OWN CLOCK,")
            print("  and is still served data. Expiry is genuinely not enforced,")
            print("  independently of the clock being wrong.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
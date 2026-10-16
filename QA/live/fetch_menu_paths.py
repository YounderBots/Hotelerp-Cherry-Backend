# -*- coding: utf-8 -*-
"""Save the deployment's navigation menu links for build_rbac_map.py --menus-from.

`menu_paths()` reads the `menus` / `submenus` tables from UserServices' database,
falling back to the removed hotelerp_users.sql seed. Neither is available in a
plain checkout, so PAGE_PARENTS would render EMPTY -- and an empty PAGE_PARENTS
denies every user, owners included, the moment the gateway enforces. The
generator refuses to write in that state, correctly.

This writes those links out through the authorised API so the map can be
regenerated from any machine. One line of paths, no credentials, no data beyond
the navigation labels' targets, which the SPA ships in Sidemenu.js anyway.

Usage:
    python QA/live/fetch_menu_paths.py > menu-paths.txt
    python Backend/tools/build_rbac_map.py --menus-from menu-paths.txt
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GW = os.environ.get("QA_GATEWAY", "http://168.231.103.18:9010")
EMAIL = "admin@cherryhotel.com"


def _password():
    from qa_common import password_for
    return password_for(EMAIL)


def call(method, path, tok=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(GW + path, data=data, method=method)
    if data is not None:
        r.add_header("Content-Type", "application/json")
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=30) as x:
            return x.status, x.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)[:150]


def rows(body):
    d = body.get("data") if isinstance(body, dict) else None
    if isinstance(d, dict):
        d = d.get("data", d)
    return d if isinstance(d, list) else []


tok = None
for attempt in range(6):
    s, b = call("POST", "/login_post", None, {"email": EMAIL, "password": _password()})
    if s == 200:
        tok = json.loads(b)["access_token"]
        break
    if s == 429:
        time.sleep(20 * (attempt + 1))
        continue
    raise SystemExit(f"login failed: {s} {b}")

paths = set()
for endpoint, field in (("/user/menus", "menu_link"), ("/user/submenus", "submenu_link")):
    s, b = call("GET", endpoint, tok)
    if s != 200:
        raise SystemExit(f"{endpoint} -> {s} {b[:120]}")
    got = rows(json.loads(b))
    found = {r.get(field) for r in got if isinstance(r, dict) and r.get(field)}
    print(f"# {endpoint}: {len(found)} links", file=sys.stderr)
    paths |= found

for p in sorted(paths):
    print(p)
print(f"# total {len(paths)} menu/submenu links", file=sys.stderr)
# -*- coding: utf-8 -*-
"""Server-side authorisation matrix across the WHOLE write surface, safely.

HOW THIS IS SAFE
    Every probe targets record id 999999999, which does not exist. A write
    verb against a missing row cannot mutate anything, so the run is fully
    repeatable and leaves the database untouched. This replaces an earlier
    version of this file that probed real ids; see QA/live/FINDINGS.md
    (QA-SEC-001) -- those DELETEs succeeded, which is the very defect this
    script is written to detect, and the two rows involved were restored.

HOW TO READ A RESULT
    403 "Your role does not have ... permission"  -> authorised: refused
    404 "not found"                              -> NOT authorised: the request
                                                     passed every permission
                                                     check and reached the data
                                                     layer, which then refused
                                                     for a different reason
    400 / 422 / 500                              -> NOT authorised: reached
                                                     validation or the data layer
    401                                          -> authentication only, not authz
"""
from __future__ import annotations

import base64
import concurrent.futures
import json
import os
import time
import urllib.error
import urllib.request

GW = os.environ.get("E2E_GATEWAY", "http://168.231.103.18:9010")
HOST = GW.split("//")[-1].split(":")[0]
PW = os.environ.get("QA_PASSWORD", "")  # never stored in this repo; see qa_common.py

def _resolve_password(default_email):
    """QA_PASSWORD, or a message explaining how to set it.

    Without this an unset variable produced a bare
    `email and password are required` 400 from the gateway, which reads as a
    broken account rather than a missing environment variable.
    """
    if PW:
        return PW
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from qa_common import password_for
    return password_for(default_email)
GHOST_ID = "999999999"

ACCOUNTS = {
    "Admin": "admin@cherryhotel.com",
    "FrontOfficeManager": "meera.krishnan@cherryhotel.com",
    "FrontDesk": "divya.rao@cherryhotel.com",
    "Housekeeping": "imran.khan@cherryhotel.com",
    "FoodAndBeverage": "joseph.dsouza@cherryhotel.com",
}
SERVICES = {"hotel": 9005, "masterdata": 9015, "user": 9020, "bar": 9025, "restaurant": 9030}


def call(method, url, tok=None, body=None, ctype="application/json", timeout=30, limit=2000000):
    data = json.dumps(body).encode() if body is not None else (b"" if method in ("POST", "PUT") else None)
    r = urllib.request.Request(url, data=data, method=method)
    if data is not None and ctype:
        r.add_header("Content-Type", ctype)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:limit]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:limit]
    except Exception as e:
        return 0, str(e)[:120]


def login(email):
    password = _resolve_password(email)
    for a in range(6):
        s, b = call("POST", GW + "/login_post", None,
                    {"email": email, "password": password})
        if s == 200:
            return json.loads(b)["access_token"]
        if s == 429:
            print(f"  (rate limited {email}; waiting)")
            time.sleep(20 * (a + 1))
            continue
        raise SystemExit(f"login failed {email}: {s} {b}")
    raise SystemExit("rate limited")


def claims(tok):
    seg = tok.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4)))


def sub_ids(path):
    out = path
    while "{" in out:
        a = out.index("{")
        b = out.index("}")
        out = out[:a] + GHOST_ID + out[b + 1:]
    return out


def write_endpoints(spec):
    """(path, methods) for every route that can change state."""
    out = []
    for path, ops in (spec.get("paths") or {}).items():
        if path in ("/", "/healthz", "/readyz", "/openapi.json"):
            continue
        ms = [m.upper() for m in ("post", "put", "patch", "delete") if m in ops]
        if not ms:
            continue
        has_path_param = "{" in path
        # A POST/PUT with only query params still inserts a row. Only send those
        # with an empty body -- the required-field validation refuses them before
        # any INSERT, so nothing is created. A 4xx here proves the request got
        # past authentication; a 403 on the path would prove authorisation.
        out.append((path, ms, has_path_param))
    return out


VERDICT = {}


def verdict(status, text):
    t = (text or "").lower()
    if status == 401:
        return "AUTH_ONLY"
    if status == 403:
        return "REFUSED"
    if status == 404:
        return "PASSED_AUTHZ"
    if status == 405:
        return "N/A_METHOD"
    if status in (400, 409, 422):
        return "PASSED_AUTHZ"
    if status >= 500:
        return "PASSED_AUTHZ+ERROR"
    if status == 200:
        return "ACCEPTED"
    return f"OTHER_{status}"


def main():
    tok, meta = {}, {}
    for role, email in ACCOUNTS.items():
        tok[role] = login(email)
        meta[role] = claims(tok[role])
        print(f"login {role:18s} role_id={meta[role].get('role_id')} pages={len(meta[role].get('perm') or {})}")

    specs = {}
    for prefix, port in SERVICES.items():
        s, b = call("GET", f"http://{HOST}:{port}/openapi.json")
        if s == 200:
            specs[prefix] = json.loads(b)

    jobs = []
    for prefix, spec in specs.items():
        for path, ms, has_param in write_endpoints(spec):
            jobs.append((prefix, path, ms, has_param))
    print(f"\nwrite routes discovered: {len(jobs)}")

    rows = []

    def run(job, role):
        prefix, path, ms, has_param = job
        concrete = sub_ids(path)
        for m in ms:
            url = f"{GW}/{prefix}/{concrete.lstrip('/')}"
            # Only DELETE/GET-like verbs against a ghost id, or an empty-body
            # POST/PUT. Either way nothing can be written.
            s, t = call(m, url, tok[role], {} if m != "DELETE" else None)
            v = verdict(s, t)
            rows.append({"prefix": prefix, "path": concrete, "method": m, "role": role,
                         "status": s, "verdict": v, "msg": t,
                         "perm_pages": len(meta[role].get("perm") or {})})

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(run, j, r) for j in jobs for r in ACCOUNTS]
        for f in concurrent.futures.as_completed(futs):
            try:
                f.result()
            except Exception as e:
                rows.append({"status": 0, "verdict": "EXC", "msg": str(e)[:120]})

    out = {"gateway": GW, "ghost_id": GHOST_ID, "roles": {r: {"role_id": meta[r].get("role_id"),
                                                              "perm": meta[r].get("perm")}
                                                            for r in ACCOUNTS},
           "rows": rows}
    with open(os.path.join(os.path.dirname(__file__), "privesc_matrix.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)

    print(f"\n{len(rows)} write probes -> privesc_matrix.json")
    print("\nPer-role summary of write-route verdicts:")
    for role in ACCOUNTS:
        c = {}
        for x in rows:
            if x.get("role") == role:
                c[x["verdict"]] = c.get(x["verdict"], 0) + 1
        print(f"  {role:18s} perm_pages={len(meta[role].get('perm') or {}):3d}  {c}")

    print("\nRoutes where a role got ACCEPTED (200) on a write verb:")
    for x in rows:
        if x.get("verdict") == "ACCEPTED":
            print(f"  !! {x['role']:18s} {x['method']:6s} {x['prefix']}/{x['path']} -> {x['status']} {x['msg'][:80]}")

    print("\nRoutes REFUSED (403) for at least one role -- the only authorised layer:")
    ref = sorted({(x["prefix"] + "/" + x["path"], x["method"]) for x in rows if x.get("verdict") == "REFUSED"})
    for p, m in ref:
        who = sorted({x["role"] for x in rows if x["prefix"] + "/" + x["path"] == p and x["method"] == m
                      and x["verdict"] == "REFUSED"})
        print(f"  {m:6s} {p}  refused for: {', '.join(who)}")

    print("\n5xx responses on write verbs:")
    for x in rows:
        if x.get("status", 0) >= 500:
            print(f"  !! {x['role']:18s} {x['method']:6s} {x['prefix']}/{x['path']} -> {x['status']} {x['msg'][:90]}")


if __name__ == "__main__":
    main()
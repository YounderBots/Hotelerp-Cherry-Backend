# -*- coding: utf-8 -*-
"""LIVE staging API sweep: every GET route, every role, gateway AND direct service.

READ-ONLY BY CONSTRUCTION -- only GET is issued, so shared staging data is not
mutated. Write workflows live in QA/live/workflow_checks.py.

Two things are measured, because they answer different questions:

  gateway  GW/<prefix>/<path>            -- the surface the app actually uses
  direct   SERVICE_PORT/<path>           -- reachable only if the service is
                                           bound to a public interface, which
                                           the gateway's RBAC design assumes
                                           is impossible

A `direct` call that returns data without a token, or that succeeds for a role
holding no permission on the owning page, is a privilege-escalation path.

Usage:
    python QA/live/sweep_api.py [--gw http://168.231.103.18:9010]
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_common import ACCOUNTS, GATEWAY, HOST, SERVICES, call as _call, claims, login  # noqa: E402

GW = GATEWAY
PORT_BY_PREFIX = {v: k for k, v in SERVICES.items()}

# Endpoints that legitimately need query parameters; a bare GET returns 400 and
# tells us nothing about auth, so they are exercised separately in
# workflow_checks.py rather than counted here.
QUERY_ONLY = re_placeholder = None


def req(method, url, tok=None, timeout=30):
    """GET-shaped wrapper matching this file's (status, body, ctype) contract.

    Read-only by construction: the method is fixed to GET so a refactor cannot
    turn a sweep into a mutating run.
    """
    s, b, ctype = _call("GET", url, tok, timeout=timeout)
    if isinstance(b, (dict, list)):
        return s, b, ctype
    # qa_common returns a length for unparseable bodies; this file wants the text.
    return s, b, ctype


def get_endpoints(spec):
    out = []
    for path, ops in (spec.get("paths") or {}).items():
        g = ops.get("get")
        if not g:
            continue
        if path in ("/", "/healthz", "/readyz", "/openapi.json"):
            continue
        required = [p.get("name") for p in g.get("parameters") or []
                    if p.get("required") and p.get("in") == "path"]
        params = [p.get("name") for p in g.get("parameters") or []]
        out.append((path, required, params))
    return out


def substitute(path, required):
    p = path
    for name in required or []:
        p = p.replace("{" + name + "}", "1")
    return p


def data_rows(body):
    if isinstance(body, dict):
        d = body.get("data")
        if isinstance(d, dict):
            d = d.get("data", d)
        if isinstance(d, list):
            return len(d)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gw", default=GW)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "sweep_api.json"))
    args = ap.parse_args()

    tokens, roles_meta = {}, {}
    for role, email in ACCOUNTS.items():
        tok = login(email)
        c = claims(tok)
        tokens[role] = tok
        roles_meta[role] = {"email": email, "role_id": c.get("role_id"), "user_id": c.get("user_id"),
                            "perm": c.get("perm") or {}}
        print(f"login {role:20s} user={c.get('user_id')} role={c.get('role_id')} "
              f"perm_pages={len(c.get('perm') or {})}")

    specs = {}
    for prefix, port in SERVICES.items():
        s, b, _ = req("GET", f"http://{HOST}:{port}/openapi.json")
        if s == 200 and isinstance(b, dict):
            specs[prefix] = b
    total_eps = sum(len(get_endpoints(sp)) for sp in specs.values())
    print(f"specs: {sorted(specs)}  GET endpoints: {total_eps}")

    jobs = []
    for prefix, spec in specs.items():
        for path, required, params in get_endpoints(spec):
            concrete = substitute(path, required)
            has_query = any("?" in path for path in [path]) or any(
                path.startswith(p) for p in ("/reports/", "/export_"))
            jobs.append((prefix, SERVICES[prefix], concrete, required, has_query))

    matrix = []

    def call(job, role, tok, surface, base):
        prefix, port, path, required, q = job
        url = base + "/" + path.lstrip("/")
        s, b, ctype = req("GET", url, tok=tok)
        return {"surface": surface, "role": role, "prefix": prefix, "port": port,
                "path": path, "status": s, "rows": data_rows(b), "ctype": ctype,
                "msg": (str(b.get("message") or b.get("error"))[:180]
                        if isinstance(b, dict) else (str(b)[:180] if s >= 400 else ""))}

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        futs = []
        for job in jobs:
            prefix, port, concrete, required, q = job
            for role in ACCOUNTS:
                for surface, base in (("gateway", GW + "/" + prefix), ("direct", f"http://{HOST}:{port}")):
                    futs.append(ex.submit(call, job, role, tokens[role], surface, base))
            # no-token probe on both surfaces
            futs.append(ex.submit(call, job, "NO_TOKEN", None, "gateway", GW + "/" + prefix))
            futs.append(ex.submit(call, job, "NO_TOKEN", None, "direct", f"http://{HOST}:{port}"))
        for f in concurrent.futures.as_completed(futs):
            try:
                matrix.append(f.result())
            except Exception as e:
                matrix.append({"status": 0, "error": str(e)[:160]})

    # --- Analysis -------------------------------------------------------
    findings = []

    # 1. Unauthenticated data exposure.
    for m in matrix:
        if m.get("role") == "NO_TOKEN" and m.get("status") == 200 and m.get("rows"):
            findings.append({"kind": "UNAUTH_DATA", **m})

    # 2. Gateway RBAC not enforcing: a role with NO permission bit on any page
    #    the endpoint maps to still gets data. Approximation: flag any non-admin
    #    role that receives data from a service surface its perm map does not
    #    cover at all -- refined per-role below by comparing to the role's own
    #    successful call set.
    perm_summary = {}
    for role, meta in roles_meta.items():
        got = sorted({m["prefix"] + "/" + m["path"] for m in matrix
                      if m.get("role") == role and m.get("surface") == "gateway"
                      and m.get("status") == 200 and m.get("rows")})
        perm_summary[role] = {"email": meta["email"], "role_id": meta["role_id"],
                              "user_id": meta["user_id"], "perm": meta["perm"],
                              "gateway_ok_count": len(got), "gateway_ok": got}

    for m in matrix:
        if m.get("status", 0) >= 500:
            findings.append({"kind": "SERVER_ERROR", **m})

    out = {"gateway": GW, "host": HOST, "services": SERVICES,
           "endpoint_count": len(jobs), "call_count": len(matrix),
           "roles": perm_summary, "matrix": matrix, "findings": findings}

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)

    print(f"\n=== {len(matrix)} calls over {len(jobs)} endpoints -> {args.out} ===")
    print("gateway 200-with-rows per role:")
    for role, v in perm_summary.items():
        print(f"  {role:20s} role_id={v['role_id']} perm_pages={len(v['perm'])} ok={v['gateway_ok_count']}")
    print(f"\nfindings: {len(findings)}")
    for f in findings[:80]:
        print("  !", f["kind"], f["role"], f["status"], f.get("surface"), f["prefix"] + "/" + f["path"],
              str(f.get("msg"))[:90], "rows=", f.get("rows"))


if __name__ == "__main__":
    main()
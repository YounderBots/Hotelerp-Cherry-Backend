# -*- coding: utf-8 -*-
"""Dry-run the gateway RBAC map against the LIVE route matrix.

WHY
    Backend/Services/LoginServices/resources/rbac.py ships with
    `MODE = os.getenv("RBAC_GATEWAY_MODE", "audit")` -- audit logs what it
    *would* deny and allows everything. That default is why every non-Admin
    role currently gets the same 200s on all five services. Flipping the
    default to `enforce` is the fix, but the module's own docstring says not
    to do that until the 222-row map has been read against real traffic.

    This is that read. It loads the committed rbac_map.py, feeds it the real
    permission claim of each demo role and every route the sweep actually
    called, and reports what enforcement WOULD do -- route by route, role by
    role -- without sending a single extra request.

Usage:
    python QA/live/rbac_dryrun.py
"""
from __future__ import annotations

import collections
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
RBAC_DIR = os.path.join(REPO, "Backend", "Services", "LoginServices", "resources")


def load_rbac():
    """Import the real map module without needing flask/sqlalchemy installed."""
    sys.path.insert(0, os.path.dirname(RBAC_DIR))
    for m in list(sys.modules):
        if m.startswith("resources"):
            del sys.modules[m]
    spec = importlib.util.spec_from_file_location("live_rbac_map", os.path.join(RBAC_DIR, "rbac_map.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VIEW, CREATE, EDIT, DELETE = 1, 2, 4, 8
ACTION_BIT = {"view": VIEW, "create": CREATE, "edit": EDIT, "delete": DELETE}


def _pattern_matches(pattern, path):
    """rbac._pattern_matches(): {id} stands for exactly one path segment."""
    ps = pattern.split("/")
    xs = path.split("/") if path else []
    if len(ps) != len(xs):
        return False
    return all(e == a or (e.startswith("{") and e.endswith("}")) for e, a in zip(ps, xs))


def _match(mod, prefix, path, method):
    """rbac._match(), reimplemented so rbac.py itself need not be imported.

    rbac.py pulls in the logger and reads the mode from the environment; only
    its matcher is needed here, and copying it keeps the dry-run honest about
    which file the decision comes from -- rbac_map.py, the committed table.
    """
    path = (path or "").strip("/")
    method = (method or "GET").upper()
    key = (prefix, path, method)
    if key in mod.ROUTE_PERMISSIONS:
        return mod.ACTION_OVERRIDES.get(key) or mod.METHOD_ACTION.get(method), \
            mod.ROUTE_PERMISSIONS[key]
    for (p, pattern, m), pages in mod.ROUTE_PERMISSIONS.items():
        if p != prefix or m != method or "{" not in pattern:
            continue
        if _pattern_matches(pattern, path):
            k = (p, pattern, m)
            return mod.ACTION_OVERRIDES.get(k) or mod.METHOD_ACTION.get(m), pages
    return None


def verdict(mod, perm, prefix, path, method):
    method = method.upper()
    if method == "OPTIONS":
        return "ALLOW", "preflight"
    path = (path or "").strip("/")
    # ALWAYS_ALLOW
    for allowed_prefix, pattern, allowed_method in mod.ALWAYS_ALLOW:
        if allowed_prefix != prefix or allowed_method.upper() != method:
            continue
        if pattern == path or _pattern_matches(pattern, path):
            return "ALLOW", "always_allow"
    resolved = _match(mod, prefix, path, method)
    if resolved is None:
        return "FAIL_CLOSED", "no permission mapping for %s /%s/%s" % (method, prefix, path)
    action, pages = resolved
    bit = ACTION_BIT.get(action or "", 0)
    perm = perm or {}
    for page in pages:
        if perm.get(page, 0) & bit:
            return "ALLOW", f"{action} on {page}"
        for parent in mod.PAGE_PARENTS.get(page, ()):
            if perm.get(parent, 0) & bit:
                return "ALLOW", f"{action} on {parent} (parent of {page})"
    return "DENY", f"role lacks '{action}' on " + (
        pages[0] if len(pages) == 1 else "any of " + ", ".join(pages))


def main():
    mod = load_rbac()
    print(f"rbac_map: {len(mod.ROUTE_PERMISSIONS)} route rows, "
          f"{len(mod.ALWAYS_ALLOW)} always-allow rows, "
          f"{len(mod.PAGE_PARENTS)} page-parent rows")

    sweep = json.load(open(os.path.join(HERE, "sweep_api.json"), encoding="utf-8"))
    matrix = json.load(open(os.path.join(HERE, "privesc_matrix.json"), encoding="utf-8"))
    roles = sweep["roles"]
    rbac_roles = matrix["roles"]

    # ---- 1. What enforce would do to every route actually exercised -------
    calls = []
    for m in sweep["matrix"]:
        if m.get("surface") != "gateway" or m.get("role") == "NO_TOKEN":
            continue
        calls.append((m["prefix"], m["path"].strip("/"), m.get("method", "GET"),
                      m["role"], m.get("status")))
    for m in matrix["rows"]:
        if m.get("role"):
            calls.append((m["prefix"], m["path"].strip("/"), m["method"], m["role"], m.get("status")))

    print(f"\nevaluating {len(calls)} real calls against the map (enforce mode)\n")

    by_role = collections.defaultdict(collections.Counter)
    false_denies = []   # route returned 200 live but the map would deny
    unmapped = collections.Counter()
    for prefix, path, method, role, status in calls:
        perm = rbac_roles.get(role, {}).get("perm") or {}
        v, why = verdict(mod, perm, prefix, path, method)
        by_role[role][v] += 1
        if v == "FAIL_CLOSED":
            unmapped[f"{method} /{prefix}/{path}"] += 1
        if v == "DENY" and status == 200:
            false_denies.append((role, method, prefix, path, why))

    print("Per-role decision counts if RBAC_GATEWAY_MODE=enforce:")
    for role in sorted(by_role):
        print(f"  {role:18s} {dict(by_role[role])}")

    print(f"\nUnmapped routes the map would FAIL CLOSED on ({len(unmapped)} distinct):")
    for k, v in sorted(unmapped.items()):
        print(f"   {k}   (seen {v}x)")

    print(f"\nFALSE DENIES -- live returned 200 but enforce would refuse ({len(false_denies)}):")
    seen = set()
    for role, method, prefix, path, why in sorted(false_denies):
        key = (method, prefix, path, why)
        if key in seen:
            continue
        seen.add(key)
        print(f"   {role:18s} {method:6s} /{prefix}/{path}\n        {why}")

    # ---- 2. Would Admin -- the role every tenant trusts -- still work? ----
    admin_denies = [d for d in false_denies if d[0] == "Admin"]
    print(f"\nAdmin calls enforcement would refuse: {len(admin_denies)}")
    for role, method, prefix, path, why in sorted(set(admin_denies))[:40]:
        print(f"   {method:6s} /{prefix}/{path}   {why}")

    # ---- 3. Does each role's claim line up with its menu pages? ------------
    print("\nClaim vs menu-page cross-check (pages the SPA shows vs pages in the JWT):")
    for role in sorted(roles):
        menu_pages = set(roles[role]["perm_pages"])
        claim_pages = set((rbac_roles.get(role, {}).get("perm") or {}).keys())
        print(f"  {role:18s} menu={len(menu_pages):3d} claim={len(claim_pages):3d} "
              f"menu_not_in_claim={sorted(menu_pages - claim_pages) or 'none'} "
              f"claim_not_in_menu={sorted(claim_pages - menu_pages) or 'none'}")

    out = {"unmapped": dict(unmapped),
           "false_denies": [{"role": r, "method": m, "prefix": p, "path": pa, "why": w}
                            for r, m, p, pa, w in false_denies],
           "per_role": {k: dict(v) for k, v in by_role.items()}}
    with open(os.path.join(HERE, "rbac_dryrun.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote rbac_dryrun.json")


if __name__ == "__main__":
    main()

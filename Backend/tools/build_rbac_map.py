#!/usr/bin/env python3
"""Regenerate the gateway RBAC map from the SPA.

    python Backend/tools/build_rbac_map.py            # rewrite rbac_map.py
    python Backend/tools/build_rbac_map.py --report   # coverage only, no write

WHY DERIVE IT
    The map answers "which page does this endpoint belong to". That question
    already has an answer in the SPA: each route in App.jsx renders one page
    component, and that component calls a specific set of endpoints. Reading it
    out of the code keeps the map honest, and makes it cheap to refresh when
    screens change -- far better than a hand-written list that silently rots.

WHAT IT CANNOT SEE
    Endpoints built dynamically (string concatenation, values from state) are
    invisible to a static read. Those show up as `rbac_unmapped` in audit mode,
    which is the intended way to find them. Run the gateway in audit, exercise
    the app, then add whatever the logs surface.

Run from the repository root.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Frontend" / "src"
OUT = ROOT / "Backend/Services/LoginServices/resources/rbac_map.py"

PREFIXES = ("masterdata", "hotel", "user", "restaurant", "bar")
METHOD = {"get": "GET", "getT": "GET", "post": "POST", "postT": "POST",
          "put": "PUT", "putT": "PUT", "delete": "DELETE", "deleteT": "DELETE"}
ACTION = {"GET": "view", "POST": "create", "PUT": "edit", "DELETE": "delete"}

CALL = re.compile(r'APICall\.(get|getT|post|postT|put|putT|delete|deleteT)\(\s*[`"\']([^`"\']+)')
LAZY = re.compile(r'const\s+(\w+)\s*=\s*lazy\(\s*\(\)\s*=>\s*import\(\s*["\']([^"\']+)["\']')
ROUTE = re.compile(r'<Route\s+path=["\']([^"\']+)["\']\s+element=\{\s*<(?:Page|PageLoader)>\s*<(\w+)\s*/?>')


def collect() -> dict[tuple[str, str, str], list[str]]:
    app = (SRC / "App.jsx").read_text(encoding="utf-8", errors="replace")
    lazy = dict(LAZY.findall(app))

    table: dict[tuple[str, str, str], set[str]] = collections.defaultdict(set)
    for route_path, comp in ROUTE.findall(app):
        rel = lazy.get(comp)
        if not rel:
            continue
        page = (SRC / rel.lstrip("./")).with_suffix(".jsx")
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        for verb, raw in CALL.findall(text):
            ep = re.sub(r"\$\{[^}]*\}", "{id}", raw.split("?")[0].rstrip("/"))
            if not ep.startswith("/"):
                continue
            parts = ep.strip("/").split("/", 1)
            if len(parts) < 2 or parts[0] not in PREFIXES:
                continue
            table[(parts[0], parts[1], METHOD[verb])].add(route_path)
    return {k: sorted(v) for k, v in table.items()}


HEADER = '''"""Route -> page permission map for the gateway (GENERATED, then reviewed).

Every external request reaches the operational services through the gateway
proxy (`/{prefix}/{path}`), so this one table is the whole authorisation
surface for the five operational services.

HOW THIS WAS BUILT
    Derived mechanically from the SPA: for each route in App.jsx, the endpoints
    its page component actually calls. The mapping therefore reflects how the
    app really uses the API rather than a guess. Regenerate with
    Backend/tools/build_rbac_map.py after adding pages or endpoints.

SEMANTICS
    A row maps (service prefix, path pattern, HTTP method) to the pages that
    legitimately call it. Access is granted when the role holds the method's
    action on ANY listed page.

    Method -> action:  GET=view  POST=create  PUT=edit  DELETE=delete

    Most rows list exactly one page. Multi-page rows are overwhelmingly shared
    reference-data reads (room types, tax types, payment methods) that many
    screens need; requiring permission on all of them would deny legitimate
    users, so ANY is the correct rule. Only three WRITE rows are shared, and
    each pair is two views of one feature.

    `{id}` matches exactly one path segment.
"""

from __future__ import annotations

# (prefix, path pattern, method) -> pages that may call it
ROUTE_PERMISSIONS: dict[tuple[str, str, str], tuple[str, ...]] = {
'''

FOOTER = '''}

METHOD_ACTION = {"GET": "view", "POST": "create", "PUT": "edit",
                 "PATCH": "edit", "DELETE": "delete"}
'''


def render(table) -> str:
    lines = [HEADER]
    current = None
    for (prefix, pattern, method) in sorted(table):
        if prefix != current:
            lines.append(f"    # ---- {prefix} ----\n")
            current = prefix
        pages = ", ".join(f'"{p}"' for p in table[(prefix, pattern, method)])
        lines.append(f'    ("{prefix}", "{pattern}", "{method}"): ({pages},),\n')
    lines.append(FOOTER)
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print coverage, write nothing")
    args = ap.parse_args()

    table = collect()
    by_service = collections.Counter(k[0] for k in table)
    ambiguous_writes = {k: v for k, v in table.items() if k[2] != "GET" and len(v) > 1}

    print(f"rows derived            : {len(table)}")
    print(f"by service              : {dict(sorted(by_service.items()))}")
    print(f"ambiguous write rows    : {len(ambiguous_writes)}")
    for k, v in sorted(ambiguous_writes.items()):
        print(f"    {k[2]:6} /{k[0]}/{k[1]} -> {', '.join(v)}")

    if args.report:
        print("\n--report: nothing written")
        return 0

    OUT.write_text(render(table), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

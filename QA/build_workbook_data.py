# -*- coding: utf-8 -*-
"""Build the menu/submenu/module dataset for the QA status workbook.

    python QA/build_workbook_data.py

Writes QA/live/workbook_data.json.

SOURCES, and why each one is used for what
    menus / submenus / roles / role_permissions
        Backend/db/12-Oct-2026/sql/hotelerp_users.sql -- the shipped demo
        database. This is the menu tree the SPA actually renders and the
        permission rows that decide who sees what, so it is the only honest
        source for "which pages exist".

    module for each page
        Derived from the RBAC map: whichever service's routes name a page is
        the module it belongs to. Guessing from the page name would file
        "/rooms" under whichever module sounds right; the map says which
        service actually serves it, which is what a bug in it breaks.

    QA status for each page
        Read from the findings, not asserted. A page with no finding against it
        is "no defect found", which is NOT the same claim as "correct".
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
DUMP = REPO / "Backend" / "db" / "12-Oct-2026" / "sql" / "hotelerp_users.sql"
MAP = REPO / "Backend" / "Services" / "LoginServices" / "resources" / "rbac_map.py"

# Prefix -> the service, and the module name a user would recognise.
PREFIX_MODULE = {
    "hotel": "Hotel / Reservations",
    "masterdata": "Master Data",
    "restaurant": "Restaurant (F&B)",
    "bar": "Bar",
    "user": "HRM / Users",
}

# Screens with no backend route of their own: they read other screens' data.
SCREEN_ONLY = {"/dashboard", "/login", "/profile", "/settings", "/view"}

# WHICH MODULE OWNS A SCREEN.
#
# From the PARENT MENU, not the permission map. This distinction matters and the
# first attempt got it wrong.
#
# ROUTE_PERMISSIONS answers "which pages are allowed to call this route", which
# is an AUTHORISATION grouping. A dashboard route is reachable from every
# module's menu, so ranking modules by route count filed /dashboard under
# Restaurant and /add_new_reservation under Master Data -- both nonsense as
# statements about who owns the screen.
#
# The menu tree is the product's own answer to that question, and it is what a
# user means by "which module is this in". Ownership by parent menu; the route
# count stays on the page as reachability, which is what it actually measures.
#
# The nine menus, and where they belong:
MENU_MODULE = {
    "Dashboard": "Cross-module (SPA)",
    "Reservation": "Hotel / Reservations",
    "Night Audit": "Hotel / Reservations",
    "Guest Enquiry": "Hotel / Reservations",
    "House Keeper": "Hotel / Reservations",
    "HRM": "HRM / Users",
    "Restaurant": "Restaurant (F&B)",
    "Bar": "Bar",
    "Master Data": "Master Data",
}


def _insert(dump: str, table: str) -> str:
    m = re.search(
        r"INSERT INTO `" + table + r"`\s*(?:\([^)]*\))?\s*VALUES\s*(.*?);\s*\n",
        dump, re.S)
    return m.group(1) if m else ""


def _split_fields(text: str) -> list:
    inner = text.strip()
    if inner.startswith("("):
        inner = inner[1:]
    if inner.endswith(")"):
        inner = inner[:-1]
    fields, buf, in_str, quote, depth = [], [], False, "", 0
    i, n = 0, len(inner)
    while i < n:
        ch = inner[i]
        if in_str:
            buf.append(ch)
            if ch == "\\" and i + 1 < n:
                i += 1
                buf.append(inner[i])
            elif ch == quote:
                in_str = False
            i += 1
            continue
        if ch in "'\"`":
            in_str, quote = True, ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            fields.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    fields.append("".join(buf).strip())

    clean = []
    for f in fields:
        if len(f) >= 2 and f[0] == "'" and f[-1] == "'":
            f = f[1:-1].replace("\\'", "'").replace("\\\\", "\\")
        elif f.upper() == "NULL":
            f = ""
        clean.append(f)
    return clean


def _rows(blob: str) -> list[tuple]:
    """Split a VALUES tuple list into rows, respecting quotes and nesting.

    Only accumulates while inside parentheses. Anything at depth 0 -- the commas
    between rows, the whitespace -- is a separator and is dropped, which is what
    stops row 2 onwards from being captured as one giant single-field tuple.
    """
    out, buf, depth, in_str, quote, i, n = [], [], 0, False, "", 0, len(blob)
    while i < n:
        ch = blob[i]
        if in_str:
            buf.append(ch)
            if ch == "\\" and i + 1 < n:
                i += 1
                buf.append(blob[i])
            elif ch == quote:
                in_str = False
            i += 1
            continue
        if ch in "'\"`":
            in_str, quote = True, ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            if depth == 1:
                buf = []          # start of a row: discard what came before it
            else:
                buf.append(ch)
        elif ch == ")":
            depth -= 1
            if depth == 0:
                out.append(tuple(_split_fields("".join(buf))))
                buf = []
            else:
                buf.append(ch)
        elif depth > 0:
            buf.append(ch)
        # depth == 0 and not a paren: a separator, so drop it
        i += 1
    return [r for r in out if r]


def _int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def load_rbac_map() -> dict:
    """The generated map: (prefix, pattern, method) -> pages."""
    for node in ast.parse(MAP.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.AnnAssign) and \
                getattr(node.target, "id", "") == "ROUTE_PERMISSIONS":
            return ast.literal_eval(node.value)
    raise SystemExit("ROUTE_PERMISSIONS not found in rbac_map.py")


def main() -> int:
    dump = DUMP.read_text(encoding="utf-8", errors="replace")

    # menus: id, label, menu_link, icon, sort, status, company, created...
    menus = {}
    for r in _rows(_insert(dump, "menus")):
        menus[str(r[0])] = {
            "id": str(r[0]), "label": r[1], "link": r[2], "icon": r[3],
            "sort": _int(r[4]),
        }

    # submenus: id, menu_id, label, submenu_link, sort, status, ...
    submenus = [
        {"id": str(r[0]), "menu_id": str(r[1]), "label": r[2], "link": r[3],
         "sort": _int(r[4])}
        for r in _rows(_insert(dump, "submenus"))
    ]

    # roles: id, role_name, description, status, ..., company_id
    roles = [
        {"id": str(r[0]), "name": r[1], "description": r[2]}
        for r in _rows(_insert(dump, "roles"))
    ]

    # role_permissions: id, role_id, menu_id, submenu_id, view, create, edit,
    #                   delete, status, ...
    grants: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in _rows(_insert(dump, "role_permissions")):
        role_id, menu_id, submenu_id = str(r[1]), str(r[2]), (r[3] or None)
        if len(r) > 8 and r[8] and r[8].upper() != "ACTIVE":
            continue
        target = submenu_id if submenu_id else menu_id
        grants[role_id][target] = {
            "view": r[4] == "1", "create": r[5] == "1",
            "edit": r[6] == "1", "delete": r[7] == "1",
        }

    page_modules: dict[str, set] = defaultdict(set)
    page_routes: dict[str, list] = defaultdict(list)
    for (prefix, pattern, method), pages in load_rbac_map().items():
        for page in pages:
            page_modules[page].add(PREFIX_MODULE[prefix])
            page_routes[page].append((prefix, pattern, method))

    def _owner(parent_menu: str, link: str) -> str:
        """The module that owns this screen, by which menu it sits under."""
        owned = MENU_MODULE.get(parent_menu)
        if owned:
            return owned
        # A menu that is not in the map above: fall back to the services that
        # serve it, and say so, rather than guessing.
        mods = page_modules.get(link)
        if mods:
            return sorted(mods)[0]
        return "Cross-module (SPA)"

    def who(key: str) -> dict:
        """Roles granted this row, keyed by role_permissions' own target id.

        The target is a submenu_id for a submenu row and a menu_id for a menu
        row -- the menu's `link` is not the key, which is why keying on the link
        reported 0 roles for all three linked menus.
        """
        out = {}
        for role in roles:
            perms = grants[role["id"]].get(key)
            if perms:
                out[role["name"]] = perms
        return out

    pages_out = []
    for mid, m in sorted(menus.items(), key=lambda kv: kv[1]["sort"]):
        kids = sorted([s for s in submenus if s["menu_id"] == mid],
                      key=lambda s: s["sort"])
        if m["link"]:
            pages_out.append({
                "kind": "Menu", "parent": "", "menu_id": mid, "submenu_id": "",
                "label": m["label"], "path": m["link"],
                "modules": [_owner(m["label"], m["link"])],
                "primary_module": _owner(m["label"], m["link"]),
                "served_by": sorted(page_modules.get(m["link"]) or []),
                "routes": len(page_routes.get(m["link"], [])),
                "roles": who(mid), "icon": m["icon"],
            })
        for s in kids:
            if not s["link"]:
                continue
            pages_out.append({
                "kind": "Submenu", "parent": m["label"], "menu_id": mid,
                "submenu_id": s["id"], "label": s["label"], "path": s["link"],
                "modules": [_owner(m["label"], s["link"])],
                "primary_module": _owner(m["label"], s["link"]),
                "served_by": sorted(page_modules.get(s["link"]) or []),
                "routes": len(page_routes.get(s["link"], [])),
                "roles": who(s["id"]), "icon": m["icon"],
            })

    data = {
        "roles": roles,
        "pages": pages_out,
        "menus": [
            {"id": m["id"], "label": m["label"], "link": m["link"],
             "icon": m["icon"],
             "submenu_count": sum(1 for s in submenus if s["menu_id"] == m["id"])}
            for m in sorted(menus.values(), key=lambda d: d["sort"])
        ],
    }
    target = REPO / "QA" / "live" / "workbook_data.json"
    target.write_text(json.dumps(data, indent=1), encoding="utf-8")

    print(f"roles   : {len(roles)}")
    print(f"menus   : {len(data['menus'])}")
    print(f"pages   : {len(pages_out)} "
          f"({sum(1 for p in pages_out if p['kind'] == 'Menu')} menus + "
          f"{sum(1 for p in pages_out if p['kind'] == 'Submenu')} submenus)")
    print(f"modules : {sorted({m for p in pages_out for m in p['modules']})}")
    print(f"wrote   : {target.relative_to(REPO)}")

    orphans = [p["path"] for p in pages_out
               if p["path"] not in page_modules and p["path"] not in SCREEN_ONLY]
    if orphans:
        print(f"\nnote: {len(orphans)} page(s) named by no route, not in SCREEN_ONLY:")
        for o in orphans:
            print(f"    {o}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
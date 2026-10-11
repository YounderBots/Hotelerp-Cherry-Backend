"""Derive the page inventory from the SPA, not from a hand-kept list.

    python Backend/tools/page_inventory.py             # markdown
    python Backend/tools/page_inventory.py --json      # machine-readable

Reads App.jsx for the routes, Sidemenu.js for which of them are reachable from
the navigation, and each page's own source for the affordances it offers
(Add / View / Edit / table). A hand-maintained checklist goes stale the first
time somebody adds a screen; this cannot.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Frontend" / "src"
APP = SRC / "App.jsx"
SIDEMENU = SRC / "Sidemenu.js"

ROUTE_RE = re.compile(r'<Route\s+path="([^"]*)"\s+element=\{\s*<([^>]+)>', re.S)
# <Page><Foo /></Page> / <PageLoader><Bar /></PageLoader> nest one level deeper.
NESTED_RE = re.compile(r"<Page(?:Loader)?>\s*<([A-Za-z0-9_]+)", re.S)
MENU_RE = re.compile(r'label:\s*"([^"]+)"\s*,\s*path:\s*"([^"]+)"')
TOPMENU_RE = re.compile(r'label:\s*"([^"]+)"\s*,\s*path:\s*"([^"]+)"\s*,', re.S)


def routes() -> list[dict]:
    """Each <Route path=... element={...}> with the page component it renders.

    The component is NOT the tag right after `element={` -- that is always the
    wrapper (<Page>, <PageLoader>, <ProtectedRoute>), and reading past it ran
    on into the NEXT route and labelled every page with its neighbour's name.
    Take the text up to the matching close of that element and find the first
    real component in it.
    """
    text = APP.read_text(encoding="utf-8", errors="replace")
    out = []
    for m in ROUTE_RE.finditer(text):
        path, tag = m.group(1), m.group(2).strip()
        tail = _element_body(text, m.end())
        nested = re.search(r"<([A-Za-z][A-Za-z0-9_]*)", tail)
        comp = nested.group(1) if nested else tag
        if comp in {"Page", "PageLoader", "ProtectedRoute", "RedirectIfAuthed", "RequireAuth"}:
            deeper = re.search(r"<([A-Za-z][A-Za-z0-9_]*)", tail[nested.end():]) if nested else None
            comp = deeper.group(1) if deeper else comp
        out.append({"route": path or "*", "component": comp, "element": tag})
    return out


def _element_body(text: str, start: int, limit: int = 400) -> str:
    """The slice of an element={...} expression, stopping at its own closing brace.

    Brace counting is what makes this correct: the body contains JSX with its
    own braces, so a fixed window either truncates a component or runs into the
    next route.
    """
    depth = 1
    i = start
    while i < len(text) and depth > 0 and i - start < limit:
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        i += 1
    return text[start:i]


def menus() -> tuple[dict[str, str], dict[str, str]]:
    text = SIDEMENU.read_text(encoding="utf-8", errors="replace")
    submenu = {p: label for label, p in MENU_RE.findall(text)}
    top = {}
    for m in re.finditer(r'label:\s*"([^"]+)"\s*,\s*path:\s*"([^"]+)"', text):
        top.setdefault(m.group(2), m.group(1))
    return submenu, top


AFFORDANCE = {
    "A": (r"openAddModal|onClick=\{openAdd|actionButton=|hasActionButton|label:\s*\"Add",),
    "V": (r"onView=|setViewData|showViewModal|viewData|viewMode",),
    "E": (r"onEdit=|handleEdit|setEditId|editId",),
    "T": (r"<TableTemplate|TableTemplate\b",),
}


def affordances(component: str) -> dict:
    """Which affordances the page offers, and which file it lives in.

    The file path is what groups a page into a module. Grouping by menu label
    instead put `/floor_layout` (Restaurant) and `/bar_floor_layout` (Bar) in
    the same bucket, because both are labelled "Floor Layout" in the sidebar.
    """
    path = _source_of(component)
    hits = {"file": str(path.relative_to(ROOT)).replace("\\", "/") if path else None}
    text = path.read_text(encoding="utf-8", errors="replace") if path else ""
    for key, pats in AFFORDANCE.items():
        hits[key] = bool(text) and any(re.search(p, text) for p in pats)
    return hits


def _source_of(component: str) -> pathlib.Path | None:
    for path in SRC.rglob("*.jsx"):
        if path.stem == component:
            return path
    for path in SRC.rglob("*.jsx"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(rf"(?:function|const)\s+{re.escape(component)}\b", text):
            return path
    return None


def module_of(file_path: str | None) -> str:
    if not file_path:
        return "Unassigned"
    parts = file_path.split("/")
    # src/<Module>/<Sub>/<Page>.jsx  ->  Module
    for p in parts:
        if p in {"Hotel", "Restaurant", "Bar", "MasterData", "Authentication", "Account"}:
            return p
    return parts[parts.index("src") + 1] if "src" in parts else "Unassigned"


def main() -> int:
    rs = routes()
    submenu, top = menus()
    items = []
    for r in rs:
        aff = affordances(r["component"])
        items.append({
            **r,
            "module": module_of(aff.get("file")),
            "menuLabel": submenu.get(r["route"]) or top.get(r["route"]),
            "affordances": aff,
            "inNavigation": r["route"] in submenu or r["route"] in top,
        })

    if "--json" in sys.argv:
        # Write the file from Python rather than letting the shell redirect it:
        # PowerShell's `>` emits UTF-16 with a BOM, which nothing downstream can
        # parse.
        if "--out" in sys.argv:
            path = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
            path.write_text(json.dumps({"routes": items, "topMenus": top,
                                        "submenus": submenu}, indent=1), encoding="utf-8")
            print(f"wrote {path}")
        else:
            print(json.dumps({"routes": items, "topMenus": top, "submenus": submenu}, indent=1))
        return 0

    nav = [i for i in items if i["inNavigation"] and i["route"] not in ("/", "*")]
    hidden = [i for i in items if not i["inNavigation"] and i["route"] not in ("/", "*")]
    mods = sorted({i["module"] for i in items})
    print(f"# Page inventory -- {len(items)} routes across {len(mods)} modules "
          f"({len(nav)} in the navigation, {len(hidden)} reachable only by URL)\n")
    print("| # | Route | Page | Module | Menu | A | V | E | T |")
    print("|---|---|---|---|---|:-:|:-:|:-:|:-:|")
    for n, i in enumerate(items, 1):
        a = i["affordances"]
        mark = lambda k: "x" if a.get(k) else ""  # noqa: E731
        print(f"| {n} | `{i['route']}` | {i['component']} | {i['module']} | "
              f"{i['menuLabel'] or '-'} | "
              f"{mark('A')} | {mark('V')} | {mark('E')} | {mark('T')} |")
    print(f"\n**Total routes: {len(items)}**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
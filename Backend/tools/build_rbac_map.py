#!/usr/bin/env python3
"""Regenerate the gateway RBAC map from the SPA, and report what it misses.

    python Backend/tools/build_rbac_map.py            # rewrite rbac_map.py
    python Backend/tools/build_rbac_map.py --report   # coverage only, no write

WHY DERIVE IT
    The map answers "which page does this endpoint belong to". That question
    already has an answer in the code: each route in App.jsx renders one page,
    and that page -- with the components it pulls in -- calls a specific set of
    endpoints. Reading it out of the source keeps the map honest and cheap to
    refresh. A hand-written list is a product decision in disguise: get it
    wrong and you lock a front desk out mid-shift.

HOW ENDPOINTS ARE FOUND
    Two passes, in decreasing order of confidence. Both read the page entry
    file AND the local components it imports, transitively -- the tabs, panels
    and modals a page is assembled from issue their own calls, and the first
    version of this tool read only the routed file, so it missed every one of
    them. KitchenDisplay, three dashboard tabs and the whole reservation family
    are child components; none of their endpoints were in the map.

    Comments are stripped first. Doc examples are the reason:
    hooks/useApiResource.js documents itself with APICall.getT("/bar/floor"),
    and 22 routes import it. Left in, that one docstring would have granted
    /bar/floor and /bar/table to all 22 pages.

    pass A  APICall.<verb>("/literal")  ->  (that endpoint, that verb)

    pass B  a call whose argument is not a literal -- APICall.getT(cfg.endpoint)
            -- proves the file issues <verb> dynamically, but not against what.
            The endpoint literals in THAT SAME FILE supply the "what": the two
            report screens keep theirs in a config table, one entry per tab,
            and they are the only dynamic dispatch in the whole SPA.

            Same file, not same page. Widening it to the page reads "this
            screen posts something, and mentions /masterdata/room" as "this
            screen may post rooms", which handed five reservation screens write
            access to the room master and took ambiguous write rows from 3 to
            47. Scoped per file it stays at 3.

WHAT IT STILL CANNOT SEE
    An endpoint assembled by concatenation -- "/bar/guest/" + id + "/feedback"
    -- leaves no literal to match. Those stay out of the map and are listed in
    UNCALLED_ENDPOINTS in the generated file, so the deny is a reviewed
    decision rather than a 403 discovered in production.

    A StaticFiles mount has no decorator, so it is not even in the upstream
    list. CURATED_ROWS below carries the few routes in that position; it is
    merged into the derived table so they survive a regeneration rather than
    being patched into the output by hand.

Run from the repository root.
"""

from __future__ import annotations

import argparse
import ast
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Frontend" / "src"
OUT = ROOT / "Backend/Services/LoginServices/resources/rbac_map.py"

PREFIXES = ("masterdata", "hotel", "user", "restaurant", "bar")

# ---------------------------------------------------------------------------
# CURATED ROWS
# ---------------------------------------------------------------------------
# Routes the two passes below CANNOT see, listed here so they survive every
# regeneration instead of being patched into the output by hand.
#
# The bar for adding one is high: the endpoint has to be genuinely underivable
# (not merely awkward to spell), and the page it is granted to has to be the
# page that actually reaches it. Everything else belongs in the source, where
# spelling the endpoint as a literal is the fix -- see the note in
# TaskAssign.jsx about what an unresolvable call does to this table.
#
#   /hotel/templates/static/room_incidents/{file}
#       HotelServices mounts its uploads directory with StaticFiles, so the
#       gateway proxies it like any other path -- authenticated, which is why
#       stories/AttachmentPreview.jsx fetches it with the session token rather
#       than pointing an <img src> at it. There is no FastAPI decorator behind
#       a StaticFiles mount, so `upstream_routes()` (which reads decorators
#       from the AST) cannot list it, and the URL is assembled from a stored
#       path, so no literal exists to match either. Without this row it is
#       unmapped, and unmapped means denied under RBAC_GATEWAY_MODE=enforce:
#       every incident attachment would 403 in production.
#
#   /masterdata/templates/static/upload_image/{file}
#   /user/templates/static/users/{file}
#   /hotel/templates/static/identity_proofs/{file}
#       The same shape, for the other three upload directories: room photos
#       (Rooms), employee photos (Employee) and a reservation's scanned ID
#       proof. All three are behind StaticFiles mounts, so none is derivable,
#       and all three are now fetched with the session token by ImagePicker /
#       AttachmentPreview. Without these rows every stored photo in the app
#       403s the moment the gateway is switched to enforce.
CURATED_ROWS: dict[tuple[str, str, str], tuple[str, ...]] = {
    ("hotel", "templates/static/room_incidents/{id}", "GET"): ("/room_incident_log",),
    ("masterdata", "templates/static/upload_image/{id}", "GET"): ("/rooms",),
    ("restaurant", "templates/static/upload_image/{id}", "GET"): ("/menus",),
    ("user", "templates/static/users/{id}", "GET"): ("/employee",),
    ("hotel", "templates/static/identity_proofs/{id}", "GET"): (
        "/add_new_reservation",
        "/reservation",
    ),
}

SERVICES = {
    "user": "UserServices",
    "masterdata": "MasterDataServices",
    "hotel": "HotelServices",
    "restaurant": "RestaurantServices",
    "bar": "BarServices",
}
METHOD = {"get": "GET", "getT": "GET", "post": "POST", "postT": "POST",
          "put": "PUT", "putT": "PUT", "delete": "DELETE", "deleteT": "DELETE"}

_VERBS = "|".join(METHOD)
# A call whose first argument is a quoted literal.
CALL_LITERAL = re.compile(r"APICall\.(" + _VERBS + r")\(\s*[`\"']([^`\"']+)")
# Any APICall at all, used to learn which verbs a page issues.
CALL_ANY = re.compile(r"APICall\.(" + _VERBS + r")\(")
# A string that looks like one of our endpoints, wherever it appears.
ENDPOINT_LITERAL = re.compile(
    r"[`\"'](/(?:" + "|".join(PREFIXES) + r")/[^`\"'\s]*)[`\"']")

# navigate("/x") and to="/x" -- how a page hands off to another route.
# `navigate("/x")`, `navigate(`/x?y=z`)` and `to="/x"`. The backtick form
# matters: the idle lock navigates to `/authentication/lockscreen?next=...` as a
# template literal, and without it that route reads as one nothing can reach.
NAVIGATE = re.compile(
    r"""navigate\(\s*["'`](/[A-Za-z0-9_/-]*)["'`?]|to=\{?\s*["'`](/[A-Za-z0-9_/-]*)["'`?]""")
# Menu rows as shipped. Read only to tell which routes a menu can reach; see
# page_parents() for why, and what to do when a deployment's menus differ.
MENU_SEED = ROOT / "hotelerp_users.sql"
MENU_PATH = re.compile(r"'(/[A-Za-z0-9_/-]*)'")
# `path: "/x"` in the frontend's fallback MENU.
SIDEBAR_PATH = re.compile(r'''path:\s*["'](/[A-Za-z0-9_/-]*)["']''')

LAZY = re.compile(
    r"const\s+(\w+)\s*=\s*lazy\(\s*\(\)\s*=>\s*import\(\s*[\"']([^\"']+)[\"']")
# `<Route path element={<Wrapper><Wrapper><Component /></...>}`.
#
# The wrapper list used to be exactly (Page|PageLoader), so the login route --
# whose element is <RedirectIfAuthed><PageLoader><Login /> -- resolved to
# nothing. Login.jsx was therefore never scanned, and the <Link to=
# "/authentication/register"> on it went unseen: the report called a route the
# user can reach from the sign-in page an unreachable one, which is exactly the
# kind of false positive that teaches people to ignore the report.
#
# Any number of capitalised single-tag wrappers are skipped, and the first
# component that is not one of the known guards is taken as the page.
ROUTE_GUARDS = ("Page", "PageLoader", "ProtectedRoute", "RedirectIfAuthed", "RequirePage")
ROUTE = re.compile(
    r"<Route\s+path=[\"']([^\"']+)[\"']\s+element=\{\s*((?:<[A-Z]\w*>\s*)+)<(\w+)\s*/?>")
IMPORT = re.compile(r"(?:from\s*|import\s*\(\s*)[\"'](\.[^\"']+)[\"']")


def strip_comments(text: str) -> str:
    """Remove // and /* */ comments, leaving string contents alone.

    A scanner rather than a regex because "http://x" and `${a}//${b}` both
    contain a // that is not a comment.
    """
    out = []
    i, n = 0, len(text)
    quote = None
    while i < n:
        c = text[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "\"'`":
            quote = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def normalise(raw: str) -> str:
    """`/bar/guest/${id}/feedback?x=1` -> `bar/guest/{id}/feedback`.

    ORDER MATTERS: placeholders collapse BEFORE the query string is cut.

    Cutting at the first "?" used to come first, which corrupted any path whose
    interpolation contained optional chaining. `${encodeURIComponent(r?.token)}`
    was truncated to `${encodeURIComponent(r`, the `${...}` pattern then failed
    to match for want of its closing brace, and the row was emitted under the
    key `room_reservation_payments/${encodeURIComponent(r`. That is worse than
    a crash: the real endpoint silently lost the page that calls it, so under
    `enforce` the request would have been denied to everyone with no failing
    test to show for it.

    A `?` inside `${...}` is JavaScript, not a query string. Collapsing
    placeholders first means only a `?` in the literal part can start one.
    """
    ep = re.sub(r"\$\{[^}]*\}", "{id}", raw)
    ep = ep.split("?")[0].rstrip("/")
    return ep.strip("/")


# ---------------------------------------------------------------------------
# what the services expose
# ---------------------------------------------------------------------------

def upstream_routes() -> list[tuple[str, str, str]]:
    """Every (prefix, path pattern, method) reachable through the gateway.

    All six services mount their router with prefix="", so a decorator path is
    the whole path. Read from the AST rather than by regex so a decorator split
    over several lines still counts.
    """
    found = []
    for prefix, svc in SERVICES.items():
        for path in sorted((ROOT / f"Backend/Services/{svc}/resources").rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for dec in node.decorator_list:
                    if not isinstance(dec, ast.Call):
                        continue
                    fn = dec.func
                    if not (isinstance(fn, ast.Attribute)
                            and isinstance(fn.value, ast.Name)
                            and fn.value.id == "router"):
                        continue
                    verb = fn.attr.upper()
                    if verb not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                        continue
                    if not dec.args or not isinstance(dec.args[0], ast.Constant):
                        continue
                    raw = str(dec.args[0].value).split("?")[0].rstrip("/")
                    found.append(
                        (prefix, re.sub(r"\{[^}]+\}", "{id}", raw).strip("/"), verb))
    return found


# ---------------------------------------------------------------------------
# what the SPA calls
# ---------------------------------------------------------------------------

_text_cache: dict[pathlib.Path, str] = {}


def source(path: pathlib.Path) -> str:
    if path not in _text_cache:
        _text_cache[path] = strip_comments(
            path.read_text(encoding="utf-8", errors="replace"))
    return _text_cache[path]


def resolve_import(importer: pathlib.Path, rel: str):
    base = importer.parent / rel
    for cand in (base, base.with_suffix(".jsx"), base.with_suffix(".js"),
                 base / "index.jsx", base / "index.js"):
        if cand.is_file():
            return cand.resolve()
    return None


def closure(entry: pathlib.Path, cap: int = 60) -> set[pathlib.Path]:
    """The entry file plus every local module it reaches, transitively."""
    seen, stack = {entry}, [entry]
    while stack:
        current = stack.pop()
        if len(seen) > cap:
            break
        for rel in IMPORT.findall(source(current)):
            nxt = resolve_import(current, rel)
            if nxt and nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def route_entries() -> dict[str, pathlib.Path]:
    app = source(SRC / "App.jsx")
    lazy = dict(LAZY.findall(app))
    entries: dict[str, pathlib.Path] = {}
    for route_path, _wrappers, comp in ROUTE.findall(app):
        # A guard used as the innermost element means the route renders only a
        # guard, so there is no page to attribute calls to.
        if comp in ROUTE_GUARDS:
            continue
        rel = lazy.get(comp)
        if not rel:
            continue
        page = (SRC / rel.lstrip("./")).with_suffix(".jsx")
        if page.exists():
            entries[route_path] = page.resolve()
    return entries


def menu_paths() -> set[str]:
    """The route paths the navigation menu points at.

    WHY THIS READS THE DATABASE, NOT JUST THE SEED FILE
        It used to read `hotelerp_users.sql` alone and return an EMPTY SET when
        that file was absent -- and the file was later removed from the repo
        because it carried a published admin password. An empty set is not a
        harmless default here: with no menu paths, `page_parents()` finds no
        parents, PAGE_PARENTS renders empty, and under `enforce` every row
        naming only detail views denies everyone. GET /hotel/room_reservation/
        {id} is exactly such a row, so regenerating without the seed silently
        reintroduced a 403 for every user including the owner -- the precise
        failure PAGE_PARENTS exists to prevent.

        The menus live in the `menus` table, which is the authoritative source
        and is present wherever this tool can usefully run. The seed file stays
        as a fallback for a checkout with no database.
    """
    if MENU_SEED.is_file():
        found = set(MENU_PATH.findall(
            MENU_SEED.read_text(encoding="utf-8", errors="replace")))
        if found:
            return found

    return _menu_paths_from_db()


def _menu_paths_from_db() -> set[str]:
    """Menu and submenu links straight from UserServices' database."""
    env = ROOT / "Backend" / "Services" / "UserServices" / ".env"
    if not env.is_file():
        return set()

    uri = None
    for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("DB_URI="):
            uri = line.split("=", 1)[1].strip()
            break
    if not uri:
        return set()

    try:
        import sqlalchemy as sa
    except ImportError:
        return set()

    try:
        engine = sa.create_engine(uri)
        with engine.connect() as conn:
            paths = {
                r[0] for r in conn.execute(sa.text("SELECT menu_link FROM menus")) if r[0]
            }
            paths |= {
                r[0]
                for r in conn.execute(sa.text("SELECT submenu_link FROM submenus"))
                if r[0]
            }
        return paths
    except Exception:  # noqa: BLE001 -- a tool, not a service; degrade to empty
        return set()


SHELL = "(app shell)"
SIDEBAR = "(sidebar)"


def page_parents(entries: dict[str, pathlib.Path]):
    """Detail routes -> the pages you reach them from. Also the dead routes.

    A permission claim is built from the user's MENUS, so its keys can only
    ever be menu paths. A routed screen with no menu row -- a detail view you
    open by clicking a row, like /ReservationView -- can therefore never appear
    in any claim, and a map row naming only such pages denies everyone.
    GET /hotel/room_reservation/{id} was exactly that: its only two pages were
    /ReservationEdit and /ReservationView, so enforce would have 403'd every
    user, including an owner with the full permission set.

    The fix is the rule the UI already implements: you got to the detail view
    from somewhere, and that somewhere is a menu page. /ReservationView is
    opened from /reservation_view and /dashboard, /view from /floor_layout --
    all three are real menu rows -- so the detail view inherits their
    permission. Derived from the navigate() calls, not assigned by hand.

    Reading the seed couples this to the menus as shipped. That is the point:
    the fallback is only needed for routes no menu can reach, and if a
    deployment reshapes its menus, regenerate and the set changes with it.
    Routes with no menu row and no inbound navigation are returned separately:
    nothing can reach them at all.
    """
    menus = menu_paths()
    inbound: dict[str, set[str]] = collections.defaultdict(set)

    # App.jsx is the shell every route renders inside, so a navigation it makes
    # can happen from any page. The idle lock lives there; without this, the
    # lock screen it navigates to reads as a route nothing can reach.
    for a, b in NAVIGATE.findall(source(SRC / "App.jsx")):
        target = a or b
        if target and target in entries:
            inbound[target].add(SHELL)

    # The sidebar is how a user reaches most pages, and it is data: the server
    # sends the menu, with Sidemenu.js's MENU as the fallback the app ships
    # with. A route named there is reachable by clicking, even when the
    # DEPLOYMENT'S menu table has no row for it yet -- which is the state a
    # newly added page is in until its migration is applied.
    #
    # Grantability still comes from menu_paths() (the database), so a page in
    # that state is correctly still reported under "rows nothing can grant":
    # reachable in the UI, refused by the gateway until the row exists.
    for target in set(SIDEBAR_PATH.findall(source(SRC / "Sidemenu.js"))):
        if target in entries:
            inbound[target].add(SIDEBAR)

    for route, entry in entries.items():
        for f in closure(entry):
            for a, b in NAVIGATE.findall(source(f)):
                target = a or b
                if target and target != route and target in entries:
                    inbound[target].add(route)

    parents, unreachable = {}, []
    for route in sorted(entries):
        if route in menus or not menus:
            continue
        if inbound.get(route):
            # The shell sentinel proves a route is REACHABLE but is not a page,
            # so it must not reach PAGE_PARENTS -- a permission claim is keyed
            # by menu path and could never contain it.
            real = sorted(p for p in inbound[route] if p not in (SHELL, SIDEBAR))
            if real:
                parents[route] = tuple(real)
        else:
            unreachable.append(route)
    return parents, unreachable


def collect():
    """Return (map, uncalled routes, page parents, dead routes, stats)."""
    upstream = upstream_routes()
    entries = route_entries()
    verbs_by_path: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for prefix, path, verb in upstream:
        verbs_by_path[(prefix, path)].add(verb)

    table: dict[tuple[str, str, str], set[str]] = collections.defaultdict(set)
    stats: collections.Counter = collections.Counter()

    for route_path, entry in entries.items():
        for f in closure(entry):
            text = source(f)

            literal_calls: set[tuple[str, str]] = set()   # (endpoint, verb)
            for verb, raw in CALL_LITERAL.findall(text):
                ep = normalise(raw)
                if ep.split("/", 1)[0] in PREFIXES:
                    literal_calls.add((ep, METHOD[verb]))

            # pass A -- the call names its own endpoint
            for ep, verb in literal_calls:
                prefix, _, rest = ep.partition("/")
                if rest:
                    table[(prefix, rest, verb)].add(route_path)
                    stats["pass_a"] += 1

            # pass B -- a dynamically dispatched call in THIS file, paired with
            # the endpoint literals in THIS file. Deliberately not widened to
            # the whole page: a page-wide rule reads "screen posts something,
            # and mentions /masterdata/room" as "screen may post rooms", which
            # handed five reservation screens write access to the room master.
            # A verb is dispatched dynamically when the file issues it more
            # often than it issues it against a literal. Comparing counts, not
            # sets: the bar report screen does both on adjacent lines, so
            # "this verb appears literally somewhere" would cancel it out.
            issued = collections.Counter(METHOD[v] for v in CALL_ANY.findall(text))
            spelled = collections.Counter(
                METHOD[v] for v, _ in CALL_LITERAL.findall(text))
            dynamic = {v for v, n in issued.items() if n > spelled[v]}
            if not dynamic:
                continue
            for raw in ENDPOINT_LITERAL.findall(text):
                ep = normalise(raw)
                prefix, _, rest = ep.partition("/")
                if prefix not in PREFIXES or not rest:
                    continue
                # only verbs the services really define on that path, so a
                # stray literal cannot invent a row for a nonexistent route
                for verb in verbs_by_path.get((prefix, rest), frozenset()) & dynamic:
                    if (ep, verb) not in literal_calls:
                        table[(prefix, rest, verb)].add(route_path)
                        stats["pass_b"] += 1

    for key, pages in CURATED_ROWS.items():
        table[key].update(pages)
        stats["curated"] += 1

    result = {k: tuple(sorted(v)) for k, v in table.items()}
    uncalled = sorted(r for r in set(upstream) if r not in result)
    parents, unreachable = page_parents(entries)
    stats["upstream"] = len(set(upstream))
    stats["rows"] = len(result)
    # A row nothing can grant is the failure this fallback exists to prevent,
    # so count what is still in that state after applying it.
    menus = menu_paths()
    grantable = menus | {r for r in parents if set(parents[r]) & menus}
    stats["ungrantable"] = sum(
        1 for pages in result.values() if menus and not (set(pages) & grantable))
    return result, uncalled, parents, unreachable, stats


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

HEADER = '''"""Route -> page permission map for the gateway (GENERATED -- do not hand-edit).

Every external request reaches the operational services through the gateway
proxy (`/{prefix}/{path}`), so this one table is the whole authorisation
surface for the five operational services.

HOW THIS WAS BUILT
    Derived mechanically from the SPA by Backend/tools/build_rbac_map.py: for
    each route in App.jsx, the endpoints its page -- and every component that
    page imports -- actually calls. The mapping therefore reflects how the app
    really uses the API rather than a guess. Regenerate after adding pages or
    endpoints; the tool also reports what it could not attribute.

SEMANTICS
    A row maps (service prefix, path pattern, HTTP method) to the pages that
    legitimately call it. Access is granted when the role holds the method's
    action on ANY listed page.

    Method -> action:  GET=view  POST=create  PUT=edit  DELETE=delete

    Most rows list exactly one page. Multi-page rows are overwhelmingly shared
    reference-data reads (room types, tax types, payment methods) that many
    screens need; requiring permission on all of them would deny legitimate
    users, so ANY is the correct rule.

    `{id}` matches exactly one path segment.
"""

from __future__ import annotations

# (prefix, path pattern, method) -> pages that may call it
ROUTE_PERMISSIONS: dict[tuple[str, str, str], tuple[str, ...]] = {
'''

FOOTER_HEAD = '''}

METHOD_ACTION = {"GET": "view", "POST": "create", "PUT": "edit",
                 "PATCH": "edit", "DELETE": "delete"}

# Routes whose HTTP verb does not describe what they DO.
#
# METHOD_ACTION above is a good default and a poor rule for action endpoints.
# A POST that changes an existing record -- check a guest in, take a payment,
# cancel a booking -- is an EDIT of that record, not the creation of a new
# one. Mapping it to `create` means a role granted view+edit on Reservation is
# refused every one of them.
#
# That is not hypothetical. The Front Office role in this database holds
# exactly view+edit on /reservation, and under `enforce` it was denied
# check-in, check-out, payment, refund, cancel, no-show AND the pricing quote
# -- the entire front-desk job -- while still being able to edit the booking
# through the form. The permission a receptionist is given did not match the
# permission the buttons required.
#
# A POST that only READS is `view` for the same reason: /room_reservation_quote
# prices a stay and stores nothing, and is a POST purely because the request
# carries a room list and dates that will not fit in a query string.
ACTION_OVERRIDES: dict[tuple[str, str, str], str] = {
    # ---- hotel: reservation lifecycle acts on a booking that already exists
    ("hotel", "room_reservation_checkin/{id}", "POST"): "edit",
    ("hotel", "room_reservation_checkout/{id}", "POST"): "edit",
    ("hotel", "room_reservation_cancel/{id}", "POST"): "edit",
    ("hotel", "room_reservation_no_show/{id}", "POST"): "edit",
    ("hotel", "room_reservation_pay/{id}", "POST"): "edit",
    ("hotel", "room_reservation_refund/{id}", "POST"): "edit",
    # ---- reads that happen to be POSTs
    ("hotel", "room_reservation_quote", "POST"): "view",
}

# Endpoints the services expose that no page was shown to call. Under
# RBAC_GATEWAY_MODE=enforce these are denied, which is the intended
# fail-closed behaviour: an endpoint nobody has classified should not be
# reachable by everyone. They are listed rather than silently absent so the
# deny is a reviewed decision, and so that wiring one into the UI shows up as
# a diff here on the next run of the generator.
UNCALLED_ENDPOINTS: tuple[tuple[str, str, str], ...] = (
'''

FOOTER_TAIL = ")\n"

PARENTS_HEAD = '''
# Detail routes -> the menu pages you reach them from.
#
# A permission claim is keyed by the user's MENU paths, so a routed screen with
# no menu row -- a detail view opened by clicking a row -- can never appear in
# one. A map row naming only such pages would deny everyone, an owner holding
# every permission included. The gateway therefore also accepts the action on a
# page the app navigates here from, which is the rule the UI already follows:
# you arrived from a page you were allowed to open.
PAGE_PARENTS: dict[str, tuple[str, ...]] = {
'''

UNREACHABLE_HEAD = '''}

# Routed screens with no menu row and nothing navigating to them. Nothing can
# open these, so their rows grant nothing; listed so a dead route stays visible
# rather than being mistaken for a permission bug.
UNREACHABLE_ROUTES: tuple[str, ...] = (
'''


def render(table, uncalled, parents, unreachable) -> str:
    lines = [HEADER]
    current = None
    for key in sorted(table):
        prefix, pattern, method = key
        if prefix != current:
            lines.append(f"    # ---- {prefix} ----\n")
            current = prefix
        pages = ", ".join(f'"{p}"' for p in table[key])
        lines.append(f'    ("{prefix}", "{pattern}", "{method}"): ({pages},),\n')
    lines.append(FOOTER_HEAD)
    current = None
    for prefix, pattern, method in uncalled:
        if prefix != current:
            lines.append(f"    # ---- {prefix} ----\n")
            current = prefix
        lines.append(f'    ("{prefix}", "{pattern}", "{method}"),\n')
    lines.append(FOOTER_TAIL)

    lines.append(PARENTS_HEAD)
    for route in sorted(parents):
        pages = ", ".join(f'"{p}"' for p in parents[route])
        lines.append(f'    "{route}": ({pages},),\n')
    lines.append(UNREACHABLE_HEAD)
    for route in sorted(unreachable):
        lines.append(f'    "{route}",\n')
    lines.append(FOOTER_TAIL)
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="print coverage, write nothing")
    args = ap.parse_args()

    table, uncalled, parents, unreachable, stats = collect()
    by_service = collections.Counter(k[0] for k in table)
    ambiguous_writes = {k: v for k, v in table.items()
                        if k[2] != "GET" and len(v) > 1}

    print(f"upstream routes         : {stats['upstream']}")
    print(f"rows derived            : {stats['rows']}   "
          f"(pass A {stats['pass_a']}, pass B {stats['pass_b']}, "
          f"curated {stats['curated']})")
    print(f"uncalled by the SPA     : {len(uncalled)}")
    print(f"detail routes w/ parent : {len(parents)}   {', '.join(sorted(parents))}")
    print(f"unreachable routes      : {len(unreachable)}   {', '.join(unreachable)}")
    print(f"rows nothing can grant  : {stats['ungrantable']}")
    print(f"by service              : {dict(sorted(by_service.items()))}")
    print(f"ambiguous write rows    : {len(ambiguous_writes)}")
    for k, v in sorted(ambiguous_writes.items()):
        print(f"    {k[2]:6} /{k[0]}/{k[1]} -> {', '.join(v)}")

    if args.report:
        print("\nuncalled endpoints (denied under enforce):")
        for prefix, pattern, method in uncalled:
            print(f"    {method:6} /{prefix}/{pattern}")
        print("\n--report: nothing written")
        return 0

    # Writing an empty PAGE_PARENTS is worse than not writing at all: the map
    # keeps working in `audit` and starts 403-ing detail routes for everyone
    # the moment somebody switches to `enforce`. Refuse, and say why.
    if not menu_paths():
        print(
            "\nREFUSING TO WRITE: no navigation menus could be read.\n"
            "  Tried  hotelerp_users.sql  and  UserServices' database.\n"
            "  Without them PAGE_PARENTS renders empty, and under enforce every\n"
            "  route whose only pages are detail views (GET /hotel/"
            "room_reservation/{id}\n"
            "  among them) would deny every user, owners included.\n"
            "  Start the database, or restore the seed, then re-run.",
            file=sys.stderr,
        )
        return 1

    OUT.write_text(render(table, uncalled, parents, unreachable), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

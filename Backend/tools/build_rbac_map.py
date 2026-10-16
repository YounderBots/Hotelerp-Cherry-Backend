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
#   /bar/templates/static/upload_image/{file}
#       The same shape, for the other upload directories: room photos (Rooms
#       and Room View), employee photos (Employee), a reservation's scanned ID
#       proof, and bar menu tiles (Bar Menu Management). All are behind
#       StaticFiles mounts, so none is derivable, and all are fetched with the
#       session token by ImagePicker / AuthedImage / AttachmentPreview. Without
#       these rows every stored photo in the app 403s the moment the gateway is
#       switched to enforce -- which is how the bar menu tiles and the Room
#       View grid were found broken.
# ---------------------------------------------------------------------------
# SELF-SERVICE ENDPOINTS
# ---------------------------------------------------------------------------
# Endpoints the gateway allows for any authenticated caller, checked BEFORE the
# permission map is consulted. Emitted into rbac_map.py as ALWAYS_ALLOW so the
# gateway and this generator cannot drift apart about which they are.
#
# The bar for adding one is that the endpoint must be incapable of reaching
# another user's data no matter how the request is shaped -- not merely
# "everyone happens to need it".
#
#   user/menus, user/submenus, user/role_permissions/{id}
#       What the SPA reads to draw its own navigation. Gating the menu behind a
#       menu permission is circular.
#
#   user/me, user/me/password, user/me/photo
#       The signed-in user's own record, their own password and their own
#       profile photo. None takes a user id: the row comes from the JWT, so
#       there is no colleague to reach and nothing a page permission would be
#       protecting. They are reached from the avatar menu, which has no menu
#       row -- so mapping them the normal way would produce rows nothing can
#       grant, denying every role including an owner holding every permission.
#
#       me/photo exists BECAUSE of that: employee photos are served from a
#       StaticFiles mount whose gateway row belongs to the HRM Employee page,
#       so a user's own avatar on their own Profile page 403'd for every role
#       that cannot read the staff directory.
SELF_SERVICE: dict[tuple[str, str, str], str] = {
    ("user", "role_permissions/{id}", "GET"): "the SPA's own navigation",
    ("user", "menus", "GET"): "the SPA's own navigation",
    ("user", "submenus", "GET"): "the SPA's own navigation",
    ("user", "me", "GET"): "the caller's own record",
    ("user", "me/password", "PUT"): "the caller's own password",
    ("user", "me/photo", "GET"): "the caller's own profile photo",
}

CURATED_ROWS: dict[tuple[str, str, str], tuple[str, ...]] = {
    ("hotel", "templates/static/room_incidents/{id}", "GET"): ("/room_incident_log",),
    ("masterdata", "templates/static/upload_image/{id}", "GET"): ("/room_view", "/rooms",),
    ("restaurant", "templates/static/upload_image/{id}", "GET"): ("/menus",),
    ("bar", "templates/static/upload_image/{id}", "GET"): ("/bar_menus",),
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

# ---------------------------------------------------------------------------
# SERVICE-TO-SERVICE ROUTES
# ---------------------------------------------------------------------------
# Calls one service makes to another THROUGH THE GATEWAY, on the caller's own
# token, so the caller's page permissions decide them exactly as they decide
# the browser's calls. The SPA never issues these, so the passes above cannot
# find them; their pages are DERIVED from the rows of the service that makes
# the call, which is the honest rule: the Hotel service may ask Master Data
# for a snapshot on behalf of anyone who may open a Hotel screen at all, and
# may write a room's operational flags on behalf of anyone who may perform a
# Hotel action that changes them.
#
#   masterdata/snapshot GET
#       Everything a reservation needs to be read or priced (rooms, rate
#       cards, tax, discounts, payment methods, identity proofs, statuses),
#       fetched once per Hotel request. Pages: every page any hotel/* row
#       names -- listing, detail, booking, housekeeping, night audit.
#
#   masterdata/room/{id}/state PUT
#       The room's occupancy, readiness and blocked flags, kept in step by
#       the Hotel service after a booking, check-in, check-out, cancellation,
#       deletion or housekeeping task. Pages: every page a hotel/* WRITE row
#       names. Action `view` (see ACTION_OVERRIDES): a receptionist holding
#       only `create` on the booking screen still causes this write by
#       making a booking, and the write is bounded to three flag columns of
#       the caller's own company -- what the caller's own action would set.
#
#   user/users/{id} GET
#       Is this assignee an active member of staff, when a housekeeping task
#       is created or reassigned. Pages: the same pages the staff LIST is
#       already granted to; the detail reveals nothing the list does not.
#
# Rows are added to the table AFTER the SPA-derived rows exist, because they
# are computed from them.
SERVICE_ROWS = {
    ("masterdata", "snapshot", "GET"):
        lambda table: {p for (pre, _pat, _m), pages in table.items()
                       if pre == "hotel" for p in pages},
    ("masterdata", "room/{id}/state", "PUT"):
        lambda table: {p for (pre, _pat, m), pages in table.items()
                       if pre == "hotel" and m != "GET" for p in pages},
    ("user", "users/{id}", "GET"):
        lambda table: set(table.get(("user", "users", "GET"), ())),
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
# `--menus-from FILE`: one menu/submenu link per line, written by
# QA/live/fetch_menu_paths.py. Read first, so a machine with no database can
# still regenerate the map instead of leaving a stale one in place. Set from
# main(); the default keeps menu_paths() pure.
MENU_FILE = ""
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

        `--menus-from FILE` is the third source, and the one that makes this
        tool runnable off a server: QA/live/fetch_menu_paths.py writes exactly
        those links out through the authorised API, so a map can be regenerated
        in CI, or by a reviewer, without database credentials.
    """
    if MENU_FILE:
        try:
            found = set()
            for line in pathlib.Path(MENU_FILE).read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    found.add(line)
        except OSError as exc:
            print(f"WARNING: --menus-from {MENU_FILE} could not be read ({exc}); "
                  "falling back to the database.", file=sys.stderr)
        else:
            if found:
                return found
            print(f"WARNING: --menus-from {MENU_FILE} held no paths; falling back "
                  "to the database.", file=sys.stderr)

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

    for key, derive in SERVICE_ROWS.items():
        pages = derive(table)
        if not pages:
            raise SystemExit(f"SERVICE_ROWS: nothing to derive {key} from -- "
                             "the rows it depends on are missing")
        table[key].update(pages)
        stats["service"] += 1

    # Self-service endpoints never reach the map: the gateway short-circuits
    # them before consulting it. Leaving them in would put rows in the table
    # that nothing can grant -- their pages have no menu row -- which is a
    # signal reserved for a genuine mapping failure, and one this tool reports
    # on. See SELF_SERVICE for why they are exempt at all.
    for key in SELF_SERVICE:
        table.pop(key, None)

    result = {k: tuple(sorted(v)) for k, v in table.items()}
    uncalled = sorted(
        r for r in set(upstream) if r not in result and r not in SELF_SERVICE)
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
    # ---- service-to-service: the Hotel service writes a room's operational
    # flags on the caller's behalf after a booking, check-out or housekeeping
    # task. Whoever may open the screen that causes it may cause it; requiring
    # `edit` would refuse a receptionist who holds only `create` on the
    # booking screen the moment they book a room. See SERVICE_ROWS in
    # Backend/tools/build_rbac_map.py.
    ("masterdata", "room/{id}/state", "PUT"): "view",
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

SELF_SERVICE_HEAD = '''
# Endpoints allowed for any authenticated caller, checked BEFORE this map is
# consulted -- so they deliberately have no row above.
#
# Each one is incapable of reaching another user's data however the request is
# shaped. `menus`/`submenus`/`role_permissions/{id}` are what the SPA reads to
# draw its own navigation, and gating the menu behind a menu permission is
# circular. `me` and `me/password` take no user id at all: the row comes from
# the JWT, so there is no colleague to reach.
#
# They are reached from the avatar menu, which has no menu row, so mapping them
# the ordinary way would produce rows nothing can grant -- denying every role,
# an owner holding every permission included.
ALWAYS_ALLOW: set[tuple[str, str, str]] = {
'''

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

    lines.append(SELF_SERVICE_HEAD)
    for key in sorted(SELF_SERVICE):
        prefix, pattern, method = key
        lines.append(
            f'    ("{prefix}", "{pattern}", "{method}"),'
            f'  # {SELF_SERVICE[key]}\n')
    lines.append(FOOTER_TAIL.replace(")", "}"))
    return "".join(lines)


# Which service directory owns which gateway prefix. The per-service policy
# files are written into these, so the gateway map and the services' own copies
# come out of one run of this generator and cannot drift apart.
SERVICE_DIRS = {
    "masterdata": "MasterDataServices",
    "hotel": "HotelServices",
    "user": "UserServices",
    "restaurant": "RestaurantServices",
    "bar": "BarServices",
}

# The tables below are hand-written policy, not derived data, so this generator
# does not invent them -- it reads them back out of the file it generated and
# hands each service the slice that concerns it.
#
# AST rather than `import resources.rbac_map`, deliberately: importing would
# make the generator depend on the gateway service's package resolving, and the
# whole point of the generator is that it runs without the services running.
HAND_WRITTEN_TABLES = ("METHOD_ACTION", "ACTION_OVERRIDES", "ALWAYS_ALLOW")


def _literal_tables(path: pathlib.Path, wanted: tuple) -> dict:
    """Read module-level assignments out of a Python file, by AST.

    Handles both `X = {...}` and the annotated `X: dict[...] = {...}` that the
    generated map uses for most of its tables -- an AnnAssign is a different AST
    node, and missing that is why ACTION_OVERRIDES and ALWAYS_ALLOW silently
    came back empty on the first attempt.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        elif isinstance(node, ast.AnnAssign):
            target = node.target
        else:
            continue
        if isinstance(target, ast.Name) and target.id in wanted:
            found[target.id] = ast.literal_eval(node.value)
    return found


def load_hand_written_tables(path: pathlib.Path) -> dict:
    # AST rather than `import resources.rbac_map`, deliberately: importing would
    # make the generator depend on the gateway service's package resolving, and
    # the whole point of the generator is that it runs without the services
    # running.
    found = _literal_tables(path, HAND_WRITTEN_TABLES)
    missing = [t for t in HAND_WRITTEN_TABLES if t not in found]
    if missing:
        raise SystemExit(
            f"cannot read {missing} out of {path}. They are hand-written policy "
            f"that lives in the generated file, so they have to already be there."
        )
    return found


POLICY_BODY = '''def _pattern_matches(pattern: str, path: str) -> bool:
    """Whether a slash-delimited pattern matches a concrete path.

    ``{id}`` stands for exactly one segment, so it cannot swallow a slash.
    """
    pattern_segs = pattern.split("/")
    path_segs = path.split("/") if path else []
    if len(pattern_segs) != len(path_segs):
        return False
    return all(
        expected == actual or (expected.startswith("{") and expected.endswith("}"))
        for expected, actual in zip(pattern_segs, path_segs)
    )


def _action_for(pattern: str, method: str) -> Optional[str]:
    """The permission a route needs -- its override, else its verb's default.

    Keyed by the resolved pattern, so a literal row and the parameterised row
    that matched it resolve identically.
    """
    return ACTION_OVERRIDES.get((pattern, method)) or METHOD_ACTION.get(method)


def _is_always_allowed(path: str, method: str) -> bool:
    for pattern, allowed_method in ALWAYS_ALLOW:
        if allowed_method != method:
            continue
        if pattern == path or _pattern_matches(pattern, path):
            return True
    return False


def _match(path: str, method: str):
    """Resolve a request against this service's map. (action, pages) or None."""
    path = (path or "").strip("/")
    method = (method or "GET").upper()

    key = (path, method)
    if key in ROUTE_PERMISSIONS:
        return _action_for(path, method), ROUTE_PERMISSIONS[key]

    # Fall back to parameterised rows.
    for (pattern, m), pages in ROUTE_PERMISSIONS.items():
        if m != method or "{" not in pattern:
            continue
        if _pattern_matches(pattern, path):
            return _action_for(pattern, method), pages
    return None


def check(perm: Optional[dict], path: str, method: str,
          *, user_id=None, role_id=None) -> Optional[str]:
    """None to allow, or a reason to deny. Same contract as the gateway's."""
    if MODE == "off":
        return None

    method = (method or "GET").upper()
    if method == "OPTIONS":
        return None

    path = (path or "").strip("/")
    if _is_always_allowed(path, method):
        return None

    resolved = _match(path, method)
    if resolved is None:
        # Unmapped. Fail closed under enforce: a route nobody classified is
        # exactly the one that should not be reachable by everyone by default.
        reason = f"no permission mapping for {method} /{SERVICE_NAME}/{path}"
        logger.error("rbac_unmapped svc=%s path=%s method=%s user=%s role=%s",
                     SERVICE_NAME, path, method, user_id, role_id)
        return None if MODE == "audit" else reason

    action, pages = resolved
    bit = ACTION_BIT.get(action or "", 0)
    perm = perm or {}

    for page in pages:
        if perm.get(page, 0) & bit:
            return None
        for parent in PAGE_PARENTS.get(page, ()):
            if perm.get(parent, 0) & bit:
                return None

    reason = (
        f"role lacks '{action}' on "
        + (pages[0] if len(pages) == 1 else "any of " + ", ".join(pages))
    )
    logger.warning("rbac_would_deny svc=%s path=%s method=%s user=%s role=%s: %s",
                   SERVICE_NAME, path, method, user_id, role_id, reason)
    return None if MODE == "audit" else reason


def _caller(request):
    """(perm, user_id, role_id) from the request's own token.

    Unverified on purpose: this layer is not the thing authenticating anybody.
    It runs AFTER nothing -- it is first -- so it cannot be the authority, and a
    forged token that got this far would still be rejected by the route's own
    `verify_authentication`. What it needs is the `perm` claim, and reading it
    is enough: a caller who forges a permissive claim still has to get past the
    route, which verifies the same token properly. Verification happens once, in
    the route, where it already did.
    """
    header = request.headers.get("authorization") or ""
    if not header.lower().startswith("bearer "):
        return None, None, None
    token = header.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(
            token,
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM],
            issuer=BaseConfig.JWT_ISSUER,
        )
    except JWTError:
        # Not a token this service can read. The route will reject it properly;
        # there is nothing to decide here.
        return None, None, None
    claim = payload.get("perm")
    return (claim if isinstance(claim, dict) else {}), payload.get("user_id"), \\
        payload.get("role_id")


class RoutePermissionMiddleware(BaseHTTPMiddleware):
    """Applies this service's slice of the gateway's permission map."""

    async def dispatch(self, request, call_next):
        method = (request.method or "GET").upper()
        path = request.url.path.rstrip("/") or "/"

        if MODE == "off" or method == "OPTIONS" or path in EXEMPT_PATHS:
            return await call_next(request)

        perm, user_id, role_id = _caller(request)
        if perm is None:
            # No usable token: let the route's own authentication answer, so the
            # caller gets a 401 about authentication rather than a 403 about
            # permission for a token they never proved.
            return await call_next(request)

        reason = check(perm, path, method, user_id=user_id, role_id=role_id)
        if reason is None:
            return await call_next(request)

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": f"Your role does not have permission for this "
                              f"action ({reason})."},
        )
'''


POLICY_HEADER = '''"""GENERATED FILE -- DO NOT EDIT.

Emitted by ``Backend/tools/build_rbac_map.py`` alongside the gateway's
``rbac_map.py``, from the same run and the same data. To change an
endpoint-to-page mapping, change the generator or the SPA and re-run it; a hand
edit here is silently overwritten on the next run and, until then, makes this
service disagree with the gateway about who may call what.

WHAT THIS IS
    A second, independent copy of the gateway's authorisation decision, living
    in the service that actually holds the data.

WHY IT IS WORTH HAVING
    The gateway is the primary control, and it is a good one -- it is the only
    place that holds the whole permission model, so deciding once there covers
    the entire external surface. Its model has a premise, though: *the services
    are not reachable except through it*. That premise held in the repository
    but not in the deployment this was written for, where all five services
    answered on the public IP and the gateway could be stepped around entirely.

    A check at the far end does not depend on that premise. It holds even if a
    service is exposed, if the gateway is misconfigured, if a proxy is added
    later that forwards straight to a service port. That is defence in depth,
    and defence in depth is the point: the two layers must fail independently.

HOW IT STAYS CORRECT
    Same rows, same decision function, same ``perm`` claim as the gateway, so
    the two layers cannot answer differently for the same request. ``audit`` is
    the default for exactly that reason -- the first deployment of a third
    enforcement layer should not also be the deployment that changes behaviour.

MODE (``ROUTE_POLICY_MODE``)
    ``audit``     log what would be denied, allow the request. Default.
    ``enforce``   refuse with 403.
    ``off``       no checks.

    Opt-OUT, like the gateway's own mode and like the bind guard, so a missing
    variable cannot silently disable the control.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import status
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from configs.base_config import BaseConfig

logger = logging.getLogger(__name__)

MODE = os.getenv("ROUTE_POLICY_MODE", "audit").strip().lower()
if MODE not in ("off", "audit", "enforce"):
    # A typo must not read as "off" or "audit" by accident. Fall forward to the
    # safe end and be loud about it.
    logger.critical(
        "ROUTE_POLICY_MODE=%r is not one of off/audit/enforce; treating it as "
        "'enforce'. Valid values are off, audit, enforce.", MODE)
    MODE = "enforce"

# Routes that exist on the service itself rather than in the permission model.
# An unauthenticated request is passed through untouched so the route's own
# `verify_authentication` produces its proper 401 -- a middleware that answered
# first would turn "no token" into "forbidden", which is both wrong and a worse
# error message.
EXEMPT_PATHS = frozenset({
    "/", "/healthz", "/readyz", "/docs", "/docs/oauth2-redirect",
    "/redoc", "/openapi.json",
})


'''


def render_service_policy(prefix: str, service: str, table: dict, hand: dict) -> str:
    """One service's slice of the map, plus the decision logic that reads it."""
    rows = sorted(k for k in table if k[0] == prefix)

    out = [POLICY_HEADER]
    out.append(f'SERVICE_NAME = "{prefix}"\n\n')

    out.append(
        "# Bit layout of the JWT `perm` claim. These travel inside a signed token,\n"
        "# so they are a wire format shared with the gateway and with\n"
        "# resources/utils.py -- not a value either side may change alone.\n"
        "VIEW, CREATE, EDIT, DELETE = 1, 2, 4, 8\n"
        'ACTION_BIT = {"view": VIEW, "create": CREATE, "edit": EDIT, "delete": DELETE}\n\n'
    )

    out.append(f"METHOD_ACTION = {hand['METHOD_ACTION']!r}\n\n")

    out.append(
        "# Routes whose HTTP verb does not describe what they DO: a POST that\n"
        "# changes an existing record is an EDIT of it, not the creation of a new\n"
        "# one. See the gateway's rbac.py for why this table exists.\n"
        "ACTION_OVERRIDES = {\n"
    )
    overrides = sorted(
        (k for k in hand["ACTION_OVERRIDES"] if k[0] == prefix),
        key=lambda k: (k[1], k[2]),
    )
    for _, pattern, method in overrides:
        out.append(f'    ("{pattern}", "{method}"): '
                   f"{hand['ACTION_OVERRIDES'][(prefix, pattern, method)]!r},\n")
    out.append("}\n\n")

    out.append(
        "# Exempt from checking. These are read by the SPA with the session token\n"
        "# but are not permissioned screens (uploads, role_permissions/{id}), and\n"
        "# an exact key alone would not exempt `role_permissions/7`.\n"
        "ALWAYS_ALLOW = {\n"
    )
    for _, pattern, method in sorted(
        (k for k in hand["ALWAYS_ALLOW"] if k[0] == prefix),
        key=lambda k: (k[1], k[2]),
    ):
        out.append(f'    ("{pattern}", "{method}"),\n')
    out.append("}\n\n")

    out.append(
        "# (path pattern, method) -> the pages whose permission authorises it.\n"
        "# An endpoint in UNCALLED_ENDPOINTS is deliberately absent: the SPA never\n"
        "# calls it, so it has no page to grant, and it is refused under enforce\n"
        "# for the same reason it is refused at the gateway.\n"
        "ROUTE_PERMISSIONS = {\n"
    )
    for _, pattern, method in rows:
        pages = ", ".join(f'"{p}"' for p in table[(prefix, pattern, method)])
        out.append(f'    ("{pattern}", "{method}"): ({pages},),\n')
    out.append("}\n\n")

    out.append(
        "# A detail view has no menu row, so it can never be a key in `perm`.\n"
        "# Naming the screen it is opened from is how the app already behaves.\n"
        "# Not service-scoped: these are page links, shared by every service.\n"
        "PAGE_PARENTS = {\n"
    )
    for route, parents in sorted(_page_parents().items()):
        values = ", ".join(f'"{p}"' for p in parents)
        out.append(f'    "{route}": ({values},),\n')
    out.append("}\n\n")

    out.append(POLICY_BODY)
    return "".join(out)


def _page_parents() -> dict:
    """Read PAGE_PARENTS back out of the generated gateway map."""
    parents = _literal_tables(OUT, ("PAGE_PARENTS",))
    if "PAGE_PARENTS" not in parents:
        raise SystemExit(f"cannot read PAGE_PARENTS out of {OUT}")
    return parents["PAGE_PARENTS"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="print coverage, write nothing")
    ap.add_argument("--menus-from", default="",
                    help="file of menu/submenu links, one per line; used "
                         "instead of the database when present "
                         "(see QA/live/fetch_menu_paths.py)")
    args = ap.parse_args()

    global MENU_FILE
    MENU_FILE = args.menus_from
    if MENU_FILE:
        print(f"menu paths    : {MENU_FILE}")

    table, uncalled, parents, unreachable, stats = collect()
    by_service = collections.Counter(k[0] for k in table)
    ambiguous_writes = {k: v for k, v in table.items()
                        if k[2] != "GET" and len(v) > 1}

    print(f"upstream routes         : {stats['upstream']}")
    print(f"rows derived            : {stats['rows']}   "
          f"(pass A {stats['pass_a']}, pass B {stats['pass_b']}, "
          f"curated {stats['curated']}, service-to-service {stats['service']})")
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

    # Each service gets its own slice of the same data, written from the same run
    # so the two layers cannot disagree. The hand-written policy tables are read
    # back out of the gateway map just written, which is why this happens after.
    hand = load_hand_written_tables(OUT)
    print("\nper-service policy (the second, independent authorisation layer):")
    for prefix, service in sorted(SERVICE_DIRS.items()):
        rows = sum(1 for k in table if k[0] == prefix)
        target = (ROOT / "Backend" / "Services" / service
                  / "resources" / "route_policy.py")
        target.write_text(render_service_policy(prefix, service, table, hand),
                          encoding="utf-8")
        exempt = sum(1 for k in hand["ALWAYS_ALLOW"] if k[0] == prefix)
        print(f"    {service:<22} {rows:>4} route(s), {exempt} exempt -> "
              f"{target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

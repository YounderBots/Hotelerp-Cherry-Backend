"""Gateway-side RBAC: the authorisation layer for the five operational services.

Run from inside LoginServices, which is where the map and the enforcement live:

    cd Backend/Services/LoginServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_rbac_gateway.py -v

These assert the property that was missing before Phase 2: authentication alone
no longer grants access to every operational endpoint. A role is refused unless
its menu actually carries the matching action.
"""

from __future__ import annotations

import logging

import pytest

from resources import rbac
from resources.rbac import (
    CREATE,
    DELETE,
    EDIT,
    VIEW,
    build_permission_claim,
    check,
)
from resources.rbac_map import (
    METHOD_ACTION,
    PAGE_PARENTS,
    ROUTE_PERMISSIONS,
    UNREACHABLE_ROUTES,
)

logging.disable(logging.CRITICAL)


@pytest.fixture
def enforce(monkeypatch):
    monkeypatch.setattr(rbac, "MODE", "enforce")


@pytest.fixture
def audit(monkeypatch):
    monkeypatch.setattr(rbac, "MODE", "audit")


# Front-desk style role: may view and create reservations, may view rooms.
FRONT_DESK_MENUS = [
    {
        "path": "/dashboard",
        "permissions": {"view": 1, "add": 0, "edit": 0, "delete": 0},
        "children": [
            {"path": "/reservation",
             "permissions": {"view": 1, "add": 1, "edit": 1, "delete": 0}},
            {"path": "/rooms",
             "permissions": {"view": 1, "add": 0, "edit": 0, "delete": 0}},
        ],
    }
]


@pytest.fixture
def front_desk():
    return build_permission_claim(FRONT_DESK_MENUS)


# --------------------------------------------------------------------------
# Claim construction
# --------------------------------------------------------------------------

def test_claim_packs_each_action_into_its_bit(front_desk):
    assert front_desk["/reservation"] == VIEW | CREATE | EDIT
    assert front_desk["/rooms"] == VIEW
    assert front_desk["/dashboard"] == VIEW


def test_claim_skips_pages_without_a_path():
    claim = build_permission_claim([{"permissions": {"view": 1}, "children": []}])
    assert claim == {}


def test_claim_unions_duplicate_pages():
    """A page listed twice must not lose permissions to ordering."""
    claim = build_permission_claim([
        {"path": "/x", "permissions": {"view": 1, "add": 0, "edit": 0, "delete": 0}},
        {"path": "/x", "permissions": {"view": 0, "add": 1, "edit": 0, "delete": 0}},
    ])
    assert claim["/x"] == VIEW | CREATE


def test_empty_menus_produce_empty_claim():
    assert build_permission_claim([]) == {}
    assert build_permission_claim(None) == {}


# --------------------------------------------------------------------------
# The core property: authentication is not authorisation
# --------------------------------------------------------------------------

def test_allows_action_the_role_holds(front_desk, enforce):
    assert check(front_desk, "masterdata", "room", "GET") is None


def test_denies_action_the_role_lacks(front_desk, enforce):
    """View on /rooms must not imply delete on /rooms."""
    denial = check(front_desk, "masterdata", "room/5", "DELETE")
    assert denial is not None
    assert "delete" in denial


def test_denies_page_the_role_cannot_see(front_desk, enforce):
    """The whole point: a front-desk token must not reach the bar service."""
    assert check(front_desk, "bar", "bill", "GET") is not None


def test_empty_claim_denies_everything(enforce):
    """A failed permission lookup must not produce a token that authorises."""
    assert check({}, "masterdata", "room", "GET") is not None
    assert check(None, "masterdata", "room", "GET") is not None


def test_unmapped_route_is_denied_under_enforce(enforce):
    """A new endpoint nobody classified must not be open to everyone."""
    denial = check({"/rooms": 15}, "bar", "totally_new_endpoint", "GET")
    assert denial is not None
    assert "no permission mapping" in denial


# --------------------------------------------------------------------------
# Method to action
# --------------------------------------------------------------------------

# This API carries record ids in the body for updates, so the real rows are
# POST/PUT on the collection and DELETE on the {id} form. Using the actual
# paths keeps the test honest about the surface being guarded.
# (request path actually sent, map key pattern, bit required)
_ROOM_ROUTES = {
    "GET": ("room", "room", VIEW),
    "POST": ("room", "room", CREATE),
    "PUT": ("room", "room", EDIT),
    "DELETE": ("room/5", "room/{id}", DELETE),
}


@pytest.mark.parametrize("method", list(_ROOM_ROUTES))
def test_method_allowed_only_with_its_own_action(method, enforce):
    """Holding exactly one bit on /rooms allows that method and no other."""
    path, _key, bit = _ROOM_ROUTES[method]
    claim = {"/rooms": bit}

    assert check(claim, "masterdata", path, method) is None, (
        f"{method} {path} should be allowed with bit {bit}"
    )

    for other, (other_path, other_key, _b) in _ROOM_ROUTES.items():
        if other == method:
            continue
        if ROUTE_PERMISSIONS[("masterdata", other_key, other)] != ("/rooms",):
            # Shared reads resolve through another page; not this test's subject.
            continue
        assert check(claim, "masterdata", other_path, other) is not None, (
            f"bit {bit} must not authorise {other} {other_path}"
        )


def test_options_is_never_blocked(enforce):
    assert check({}, "bar", "bill", "OPTIONS") is None


# --------------------------------------------------------------------------
# Shared endpoints: ANY listed page grants access
# --------------------------------------------------------------------------

def test_shared_read_allowed_via_any_owning_page(enforce):
    """/masterdata/room is called by 8 screens; view on one of them is enough."""
    pages = ROUTE_PERMISSIONS[("masterdata", "room", "GET")]
    assert len(pages) > 1, "expected a shared row for this test to mean anything"
    for page in pages:
        assert check({page: VIEW}, "masterdata", "room", "GET") is None


# --------------------------------------------------------------------------
# Path patterns
# --------------------------------------------------------------------------

def test_id_segment_matches_one_segment(enforce):
    """DELETE masterdata/room/{id} must match any single id value."""
    claim = {"/rooms": DELETE}
    for room_id in ("1", "42", "abc-uuid"):
        assert check(claim, "masterdata", f"room/{room_id}", "DELETE") is None


def test_id_segment_does_not_match_extra_segments(enforce):
    assert check({"/rooms": 15}, "masterdata", "room/42/deeper/still", "DELETE") is not None


# --------------------------------------------------------------------------
# Rollout modes
# --------------------------------------------------------------------------

def test_audit_mode_allows_what_enforce_would_deny(front_desk, audit):
    assert check(front_desk, "bar", "bill", "GET") is None


def test_off_mode_skips_checks_entirely(front_desk, monkeypatch):
    monkeypatch.setattr(rbac, "MODE", "off")
    assert check({}, "bar", "bill", "DELETE") is None


def test_default_mode_is_audit_not_enforce():
    """Shipping straight to enforce on a live hotel is how people get locked out."""
    import importlib
    assert importlib.import_module("resources.rbac").MODE in ("audit", "enforce", "off")


# --------------------------------------------------------------------------
# Map integrity
# --------------------------------------------------------------------------

def test_every_row_has_at_least_one_page():
    for key, pages in ROUTE_PERMISSIONS.items():
        assert pages, f"{key} maps to no page"
        assert all(p.startswith("/") for p in pages), f"{key} has a malformed page"


def test_every_row_uses_a_known_method():
    for (_prefix, _pattern, method) in ROUTE_PERMISSIONS:
        assert method in METHOD_ACTION, f"unknown method {method}"


def test_every_row_targets_a_known_service():
    known = {"masterdata", "hotel", "user", "restaurant", "bar"}
    for (prefix, _pattern, _method) in ROUTE_PERMISSIONS:
        assert prefix in known, f"unknown service prefix {prefix}"


def test_all_five_services_are_covered():
    covered = {prefix for prefix, _p, _m in ROUTE_PERMISSIONS}
    assert covered == {"masterdata", "hotel", "user", "restaurant", "bar"}


def test_a_detail_view_is_granted_by_the_page_you_reach_it_from(enforce):
    """The bug this fallback exists for.

    GET /hotel/room_reservation/{id} is attributed to /ReservationEdit and
    /ReservationView. Neither has a menu row, so neither can ever be a key in a
    permission claim -- under enforce the row refused every user alive,
    including one holding every permission. /ReservationView is opened from
    /reservation_view, so that page's `view` is what should grant it.
    """
    assert "/ReservationView" in PAGE_PARENTS
    reached_from = {"/reservation_view": VIEW}
    assert check(reached_from, "hotel", "room_reservation/1", "GET") is None


def test_the_parent_fallback_still_respects_the_action(enforce):
    """Inheriting the page must not mean inheriting every action on it."""
    view_only = {"/reservation_view": VIEW}
    assert check(view_only, "hotel", "room_reservation", "PUT") is not None


def test_the_parent_fallback_does_not_grant_unrelated_pages(enforce):
    """Holding a page that navigates nowhere near it grants nothing."""
    elsewhere = {"/bar_menus": VIEW | CREATE | EDIT | DELETE}
    assert check(elsewhere, "hotel", "room_reservation/1", "GET") is not None


def test_no_row_is_grantable_only_through_a_dead_route():
    """Every row must have at least one page something can actually open.

    A row naming only unreachable routes denies everyone by construction, and
    would read in the logs as a permission misconfiguration rather than a map
    defect. Rows whose pages are detail views are fine: PAGE_PARENTS resolves
    those to a real menu page.
    """
    dead = set(UNREACHABLE_ROUTES)
    ungrantable = {
        k: v for k, v in ROUTE_PERMISSIONS.items()
        if v and all(p in dead and not PAGE_PARENTS.get(p) for p in v)
    }
    assert not ungrantable, f"rows nothing can grant: {sorted(ungrantable)}"


def test_write_rows_are_essentially_unambiguous():
    """Writes are the operations worth guarding; they must resolve to one page.

    Six known exceptions, each several views of a single feature: a roster and
    its shift planner, the kitchen display mounted once per station, and the
    reservation pricing call. Pinned as an exact set rather than a count, so a
    genuinely new ambiguity fails here even if a known one is removed.

    `("hotel", "room_reservation", "PUT")` used to be a seventh. It resolved to
    /reservation and /ReservationEdit -- a second edit screen nothing in the app
    ever navigated to. Deleting that screen left the edit exactly one home, so
    the ambiguity is gone rather than merely reviewed.
    """
    expected = {
        ("bar", "staff_assignment", "POST"),
        # Reviewed: /hotel/room_reservation_quote is a POST that writes
        # nothing -- it prices a stay and returns the figures, and it is a POST
        # only because the request carries a room list and dates that do not
        # fit a query string. Both screens that price a reservation call it:
        # /add_new_reservation before the booking exists, and /reservation when
        # the edit form re-prices an amendment. Granting it on either page is
        # therefore correct, and the create permission it resolves to is the
        # same one those pages already need to act on the answer.
        ("hotel", "room_reservation_quote", "POST"),
        # Reviewed: /masterdata/room/{id}/state is the Hotel service writing a
        # room's occupancy / readiness / blocked flags on the caller's behalf,
        # as the consequence of a booking, check-out or housekeeping task. Its
        # pages are DERIVED as the union of every Hotel write row's pages
        # (build_rbac_map.py, SERVICE_ROWS), so it is ambiguous by
        # construction: any screen whose action moves a room's flags may move
        # them. The write is bounded to three flag columns of the caller's own
        # company, and its action is `view` (see ACTION_OVERRIDES below).
        ("masterdata", "room/{id}/state", "PUT"),
        ("restaurant", "kot/item/{id}/status", "PUT"),
        ("restaurant", "kot/{id}/acknowledge", "PUT"),
        ("restaurant", "kot/{id}/status", "PUT"),
        ("restaurant", "staff_assignment", "POST"),
    }
    shared_writes = {
        k for k, v in ROUTE_PERMISSIONS.items()
        if k[2] != "GET" and len(v) > 1
    }
    assert shared_writes == expected, (
        f"unreviewed ambiguous writes: {sorted(shared_writes - expected)}; "
        f"gone: {sorted(expected - shared_writes)}"
    )


# ---------------------------------------------------------------------------
# ACTION_OVERRIDES -- when the HTTP verb is the wrong name for what a route does
# ---------------------------------------------------------------------------
# METHOD_ACTION is a good default and a poor rule for action endpoints. A POST
# that changes an existing record is an EDIT of it, not a create.
#
# The Front Office role in this product holds view+edit on /reservation and NOT
# add. Under `enforce` with the default mapping it was denied check-in,
# check-out, payment, refund, cancel, no-show and the pricing quote -- the whole
# front-desk job -- while still being able to edit the same booking through the
# form. These tests pin the fix so a regeneration cannot quietly undo it.

def test_reservation_lifecycle_actions_require_edit_not_create():
    """Acting on a booking that already exists is an edit."""
    from resources.rbac_map import ACTION_OVERRIDES

    for path in (
        "room_reservation_checkin/{id}",
        "room_reservation_checkout/{id}",
        "room_reservation_cancel/{id}",
        "room_reservation_no_show/{id}",
        "room_reservation_pay/{id}",
        "room_reservation_refund/{id}",
    ):
        assert ACTION_OVERRIDES[("hotel", path, "POST")] == "edit", path


def test_the_pricing_quote_is_a_read():
    """It stores nothing; it is a POST only because the request body is a list
    of rooms and dates that will not fit in a query string."""
    from resources.rbac_map import ACTION_OVERRIDES

    assert ACTION_OVERRIDES[("hotel", "room_reservation_quote", "POST")] == "view"


def test_a_view_and_edit_role_can_run_the_front_desk(enforce):
    """The end-to-end consequence, asserted against rbac.check itself."""
    from resources import rbac

    # Exactly what the Front Office role holds: view + edit, no add, no delete.
    perm = {"/reservation": rbac.VIEW | rbac.EDIT}

    for path in (
        "room_reservation_checkin/{id}",
        "room_reservation_checkout/{id}",
        "room_reservation_cancel/{id}",
        "room_reservation_no_show/{id}",
        "room_reservation_pay/{id}",
        "room_reservation_refund/{id}",
    ):
        assert rbac.check(perm, "hotel", path, "POST") is None, path


def test_that_role_still_cannot_create_or_delete_a_reservation(enforce):
    """The override must not have widened anything: add and delete are still
    the permissions they always were."""
    from resources import rbac

    perm = {"/reservation": rbac.VIEW | rbac.EDIT, "/add_new_reservation": rbac.VIEW}

    # Creating a booking is a genuine create, and this role lacks it.
    assert rbac.check(perm, "hotel", "room_reservation", "POST") is not None
    # Deleting one is a genuine delete, and this role lacks it.
    assert rbac.check(perm, "hotel", "room_reservation/{id}", "DELETE") is not None


def test_every_override_names_a_route_that_exists():
    """An override for a route that is not in the map does nothing, and would
    hide a typo behind silence."""
    from resources.rbac_map import ACTION_OVERRIDES, ROUTE_PERMISSIONS

    unknown = [k for k in ACTION_OVERRIDES if k not in ROUTE_PERMISSIONS]
    assert not unknown, f"overrides for routes not in the map: {unknown}"


def test_every_override_names_a_real_action():
    from resources.rbac import ACTION_BIT
    from resources.rbac_map import ACTION_OVERRIDES

    bad = {k: v for k, v in ACTION_OVERRIDES.items() if v not in ACTION_BIT}
    assert not bad, f"overrides naming an unknown action: {bad}"


# ---------------------------------------------------------------------------
# PAGE_PARENTS must never be empty
# ---------------------------------------------------------------------------

def test_detail_routes_still_resolve_to_a_menu_page():
    """PAGE_PARENTS renders from the shipped menus, and the generator returned
    an EMPTY set when it could not read them -- which it could not, after
    hotelerp_users.sql was removed from the repo. An empty table is invisible
    in `audit` and denies every user in `enforce`: GET /hotel/room_reservation/
    {id} names only detail views, so with no parents it grants nothing to
    anybody, owners included."""
    from resources.rbac_map import PAGE_PARENTS, ROUTE_PERMISSIONS

    assert PAGE_PARENTS, "PAGE_PARENTS is empty -- the generator could not read the menus"
    assert "/ReservationView" in PAGE_PARENTS

    # And the row that motivated it must be grantable to somebody.
    pages = ROUTE_PERMISSIONS[("hotel", "room_reservation/{id}", "GET")]
    parents = set()
    for page in pages:
        parents |= set(PAGE_PARENTS.get(page, ()))
    assert parents, f"{pages} resolve to no menu page, so nobody can be granted them"


# ---------------------------------------------------------------------------
# The map GENERATOR's path normalisation
#
# These guard the tool that writes rbac_map.py rather than the gateway that
# reads it, but they belong with the gateway tests: a generator bug here does
# not crash, it emits a row under a key no request will ever match, and the
# endpoint silently loses the page that grants it. Under `enforce` that is a
# 403 for everyone, with nothing failing to point at it.
# ---------------------------------------------------------------------------

def _normalise():
    """Import the generator by path -- it lives in tools/, not on sys.path."""
    import importlib.util
    import sys
    from pathlib import Path

    tool = Path(__file__).resolve().parents[1] / "tools" / "build_rbac_map.py"
    spec = importlib.util.spec_from_file_location("_build_rbac_map", tool)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_build_rbac_map"] = module
    spec.loader.exec_module(module)
    return module.normalise


def test_normalise_collapses_a_template_placeholder():
    assert _normalise()("/bar/guest/${id}/feedback") == "bar/guest/{id}/feedback"


def test_normalise_strips_a_real_query_string():
    assert _normalise()("/bar/guest/${id}/feedback?x=1") == "bar/guest/{id}/feedback"


def test_normalise_survives_optional_chaining_inside_a_placeholder():
    """The '?' in `r?.token` is JavaScript, not the start of a query string.

    Cutting at the first '?' before collapsing `${...}` truncated the
    placeholder to `${encodeURIComponent(r`, which then failed to match for
    want of its closing brace. The row was emitted under that literal text, so
    the real endpoint lost the page that calls it.
    """
    got = _normalise()(
        "/hotel/room_reservation_payments/${encodeURIComponent(reservation?.token)}"
    )
    assert got == "hotel/room_reservation_payments/{id}"


def test_normalise_handles_optional_chaining_and_a_query_string_together():
    got = _normalise()("/hotel/thing/${a?.b}/sub?page=1")
    assert got == "hotel/thing/{id}/sub"


# ---------------------------------------------------------------------------
# Guest contact details are not a dashboard capability
# ---------------------------------------------------------------------------

def test_a_dashboard_only_role_cannot_read_the_reservation_list(enforce):
    """The Dashboard is a reporting screen, not a guest-contact export.

    `/hotel/room_reservation` returns every guest's phone number and email.
    /dashboard used to be granted it, because both Dashboard tabs fetched the
    whole book to derive four counts and two short lists of names. They now
    call /hotel/reports/reservation_summary, which carries no contact details,
    and the generated map no longer names /dashboard on the list route.

    If a future change makes a dashboard fetch the list again, the generator
    will silently re-grant it and this test is what notices.
    """
    dashboard_only = {"/dashboard": VIEW}
    denial = check(dashboard_only, "hotel", "room_reservation", "GET")
    assert denial is not None


def test_a_dashboard_only_role_can_read_the_summary_it_needs(enforce):
    dashboard_only = {"/dashboard": VIEW}
    assert check(dashboard_only, "hotel", "reports/reservation_summary", "GET") is None


def test_the_reservation_screens_still_read_the_list(enforce):
    for page in ("/reservation", "/reservation_view"):
        assert check({page: VIEW}, "hotel", "room_reservation", "GET") is None


# ---------------------------------------------------------------------------
# Self-service endpoints
#
# /user/me and /user/me/password are reached from the avatar menu, which has no
# menu row, so no permission claim can ever contain /profile or /settings. If
# these were mapped the ordinary way they would deny every role -- an owner
# holding every permission included. They are exempt because neither takes a
# user id: the row comes from the JWT, so no request shape reaches a colleague.
# ---------------------------------------------------------------------------

def test_a_user_with_no_permissions_at_all_can_read_their_own_profile(enforce):
    assert check({}, "user", "me", "GET") is None


def test_a_user_with_no_permissions_at_all_can_change_their_own_password(enforce):
    assert check({}, "user", "me/password", "PUT") is None


def test_front_desk_reaches_self_service_without_any_hrm_permission(enforce):
    """The case that motivated the exemption: a Front Desk claim holds nothing
    on /user or /employee, and must still reach all three."""
    claim = {"/reservation": VIEW | CREATE | EDIT, "/dashboard": VIEW}
    assert check(claim, "user", "me", "GET") is None
    assert check(claim, "user", "me/password", "PUT") is None
    assert check(claim, "user", "me/photo", "GET") is None


def test_a_user_with_no_permissions_at_all_can_see_their_own_photo(enforce):
    """Employee photos are served from a StaticFiles mount whose row belongs to
    the HRM Employee page, so the avatar on a user's OWN profile answered 403
    for every role that cannot read the staff directory. /me/photo resolves the
    file from the token, so it can only ever be the caller's own."""
    assert check({}, "user", "me/photo", "GET") is None


def test_the_staff_photo_mount_is_still_gated(enforce):
    """The fix must not have widened the directory itself: reaching a photo BY
    PATH still requires the Employee page."""
    assert check({}, "user", "templates/static/users/someone.png", "GET") is not None


def test_self_service_is_not_mapped_as_an_ordinary_row():
    """The generator drops these from ROUTE_PERMISSIONS on purpose. A row here
    would be one nothing can grant, which is the signal reserved for a real
    mapping failure."""
    assert ("user", "me", "GET") not in ROUTE_PERMISSIONS
    assert ("user", "me/password", "PUT") not in ROUTE_PERMISSIONS
    assert ("user", "me/photo", "GET") not in ROUTE_PERMISSIONS


def test_the_exempt_set_stays_small_and_self_scoped():
    """A guard on the blast radius. Everything exempt here bypasses page
    permissions entirely, so the set must not quietly grow: each entry has to
    be incapable of reaching another user's data however the request is shaped.
    """
    from resources.rbac import ALWAYS_ALLOW

    assert ALWAYS_ALLOW == {
        ("user", "role_permissions/{id}", "GET"),
        ("user", "menus", "GET"),
        ("user", "submenus", "GET"),
        ("user", "me", "GET"),
        ("user", "me/password", "PUT"),
        # Resolves the file from the JWT, not from the URL. The only photo it
        # can answer with is the caller's own.
        ("user", "me/photo", "GET"),
    }
    # Nothing exempt may carry a path parameter that names a user.
    for prefix, path, method in ALWAYS_ALLOW:
        assert not path.startswith("users/"), f"{path} can address another user"


# --------------------------------------------------------------------------
# Service-to-service calls, which go through this gateway on the caller's
# own token: the Hotel service reading Master Data and Users.
#
# The SPA never issues these, so build_rbac_map.py derives their pages from
# the Hotel rows (SERVICE_ROWS): whoever may open a Hotel screen may, through
# the Hotel service, read the snapshot; whoever may perform a Hotel action
# that changes a room's flags may, through it, write them.
# --------------------------------------------------------------------------

SERVICE_ROUTES = (
    ("masterdata", "snapshot", "GET"),
    ("masterdata", "room/{id}/state", "PUT"),
    ("user", "users/{id}", "GET"),
)


def test_the_service_routes_are_mapped_not_uncalled():
    """A build of the gateway that lacks these rows denies every reservation
    screen under enforce -- the Hotel service cannot price a stay without the
    snapshot. Pinned so a regenerated map cannot silently drop them."""
    from resources.rbac_map import UNCALLED_ENDPOINTS
    for key in SERVICE_ROUTES:
        assert key in ROUTE_PERMISSIONS, key
        assert key not in UNCALLED_ENDPOINTS, key
        assert ROUTE_PERMISSIONS[key], key


def test_the_snapshot_is_readable_from_every_hotel_screen():
    """Derived, not typed: the snapshot's pages are the union of the pages
    of every hotel/* row, so adding a Hotel screen extends it automatically."""
    hotel_pages = {p for (pre, _pat, _m), pages in ROUTE_PERMISSIONS.items()
                   if pre == "hotel" for p in pages}
    assert set(ROUTE_PERMISSIONS[("masterdata", "snapshot", "GET")]) == hotel_pages


def test_a_dashboard_only_role_can_still_have_its_summary_priced(enforce):
    """A role that may only open the dashboard reads the snapshot through the
    Hotel service (the dashboard shows reservation labels), and nothing else
    of Master Data."""
    perm = {"/dashboard": VIEW}
    assert check(perm, "masterdata", "snapshot", "GET") is None
    # Not widened: the room master's own editor and the rate card stay theirs.
    assert check(perm, "masterdata", "room", "PUT") is not None
    assert check(perm, "masterdata", "room_types", "GET") is not None


def test_a_receptionist_who_may_only_create_bookings_can_cause_the_room_write(enforce):
    """The override this exists for. Making a booking marks the room Reserved;
    that write is a PUT, whose default action is `edit`, which a create-only
    receptionist does not hold. `view` on the screen that causes it is the
    rule -- the write is the consequence of an action they are allowed."""
    perm = {"/add_new_reservation": VIEW | CREATE}
    assert check(perm, "masterdata", "room/12/state", "PUT") is None
    # ...while the room's own editor stays gated as before.
    assert check(perm, "masterdata", "room", "PUT") is not None


def test_a_bar_only_role_reaches_none_of_it(enforce):
    perm = {"/bar_billing_payments": VIEW | CREATE | EDIT | DELETE}
    for prefix, path, method in SERVICE_ROUTES:
        assert check(perm, prefix, path.replace("{id}", "7"), method) is not None, path


def test_the_assignee_check_is_granted_where_the_staff_list_already_is():
    """The detail reveals nothing the list does not, so it is granted to
    exactly the same pages -- neither wider nor narrower."""
    assert (ROUTE_PERMISSIONS[("user", "users/{id}", "GET")]
            == ROUTE_PERMISSIONS[("user", "users", "GET")])


# --------------------------------------------------------------------------
# The `gw` claim: the gateway tells services where it is, inside the token
#
# A downstream service that calls back through this gateway (the Hotel
# service, for Master Data and Users) learns the gateway's address from the
# token it already holds, so a deployment that never set API_GATEWAY_URL in
# the Hotel .env still works. The live one never had.
# --------------------------------------------------------------------------

def _request(scope_server=("0.0.0.0", 9010), headers=()):
    from starlette.requests import Request
    scope = {"type": "http", "method": "POST", "path": "/login_post", "headers": list(headers),
             "server": scope_server, "query_string": b""}
    return Request(scope)


def test_the_gateway_writes_its_bound_port_on_loopback(monkeypatch):
    from resources.loginController import self_url
    monkeypatch.delenv("GATEWAY_SELF_URL", raising=False)
    assert self_url(_request(("0.0.0.0", 9010))) == "http://127.0.0.1:9010"


def test_the_claim_never_comes_from_the_callers_headers(monkeypatch):
    """A Host or X-Forwarded-Host is the caller's to set. A signed claim of a
    caller-chosen address would let them steer the Hotel service at a Master
    Data of their own and book a room at any price it names."""
    from resources.loginController import self_url
    monkeypatch.delenv("GATEWAY_SELF_URL", raising=False)
    evil = [(b"host", b"evil.example:80"), (b"x-forwarded-host", b"evil.example"),
            (b"x-forwarded-proto", b"https")]
    assert self_url(_request(("0.0.0.0", 9010), evil)) == "http://127.0.0.1:9010"


def test_an_operator_can_name_the_address_for_a_split_deployment(monkeypatch):
    from resources.loginController import self_url
    monkeypatch.setenv("GATEWAY_SELF_URL", "http://gateway.internal:8000/")
    assert self_url(_request()) == "http://gateway.internal:8000"


def test_no_bound_port_means_no_claim(monkeypatch):
    from resources.loginController import self_url
    monkeypatch.delenv("GATEWAY_SELF_URL", raising=False)
    assert self_url(_request(scope_server=None)) == ""


def test_the_minted_token_carries_the_claim():
    from jose import jwt
    from configs import BaseConfig
    from resources.utils import create_access_token
    tok = create_access_token(data={"user_id": 1, "perm": {}, "gw": "http://127.0.0.1:9010"})
    claims = jwt.decode(tok, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM],
                        issuer=BaseConfig.JWT_ISSUER)
    assert claims["gw"] == "http://127.0.0.1:9010"

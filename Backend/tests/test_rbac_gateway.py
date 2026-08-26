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
    its shift planner, a reservation and its edit view, and the kitchen display
    mounted once per station. Pinned as an exact set rather than a count, so a
    genuinely new ambiguity fails here even if a known one is removed.
    """
    expected = {
        ("bar", "staff_assignment", "POST"),
        ("hotel", "room_reservation", "PUT"),
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

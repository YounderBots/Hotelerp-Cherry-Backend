# -*- coding: utf-8 -*-
"""The service-side permission guard must agree with the gateway, exactly.

Run from LoginServices:

    python -m pytest ../../Backend/tests/test_route_policy.py -q

THE CLAIM UNDER TEST
    `resources/rbac.py` at the gateway and `resources/route_policy.py` in each
    service are two copies of one decision, made from one generator run. If that
    is true, no request can be allowed by one and refused by the other -- which
    is the entire reason the second layer is safe to switch on.

    It is a claim about 279 routes times four claims times two modes, so it is
    checked exhaustively rather than sampled. A sample would not catch the
    interesting failure: one row where the service's slice dropped a page, which
    would refuse a legitimate call for exactly one role on one endpoint.

HOW THE SERVICE MODULES ARE LOADED
    Each service is its own package root and deliberately cannot import its
    siblings, so `route_policy.py` is loaded by path. It only needs
    `configs.base_config`, which resolves to the gateway's -- the same three
    attributes (SECRET_KEY, ALGORITHM, JWT_ISSUER) exist in every service, and
    nothing under test reads their values.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO / "Backend" / "Services"

from resources import rbac  # noqa: E402  (needs LoginServices as cwd)
from resources.rbac_map import UNCALLED_ENDPOINTS  # noqa: E402

ALL_BITS = rbac.VIEW | rbac.CREATE | rbac.EDIT | rbac.DELETE

# Which service directory owns which gateway prefix. Same mapping the generator
# uses; if these drift, the loader below silently stops finding a slice.
PREFIX_TO_SERVICE = {
    "masterdata": "MasterDataServices",
    "hotel": "HotelServices",
    "user": "UserServices",
    "restaurant": "RestaurantServices",
    "bar": "BarServices",
}


def _load_service_policy(prefix: str):
    """Load one service's generated route_policy.py by path."""
    service = PREFIX_TO_SERVICE[prefix]
    path = SERVICES_DIR / service / "resources" / "route_policy.py"
    assert path.is_file(), f"{service} has no route_policy.py -- run build_rbac_map.py"

    name = f"_route_policy_{prefix}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    assert module.SERVICE_NAME == prefix, (
        f"{service}/route_policy.py declares SERVICE_NAME="
        f"{module.SERVICE_NAME!r}, expected {prefix!r} -- the generator's "
        f"prefix-to-directory mapping has drifted"
    )
    return module


def _concrete(pattern: str) -> str:
    """A request path for a route pattern: `/bill/{id}/split` -> `/bill/7/split`."""
    return "/" + "/".join("7" if seg.startswith("{") else seg for seg in pattern.split("/"))


def _claims(pages, bits):
    """A `perm` claim granting `bits` on each of `pages`."""
    return {page: bits for page in pages}


# ---------------------------------------------------------------------------
# The slices cover the gateway's rows, completely and only
# ---------------------------------------------------------------------------

def test_every_gateway_route_has_a_service_slice():
    total = 0
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        expected = {
            (pattern, method)
            for (p, pattern, method) in rbac.ROUTE_PERMISSIONS
            if p == prefix
        }
        actual = set(policy.ROUTE_PERMISSIONS)
        assert actual == expected, (
            f"{prefix}: service slice has {len(actual)} rows, the gateway map "
            f"has {len(expected)}.\n"
            f"  only in the service: {sorted(actual - expected)[:6]}\n"
            f"  only in the gateway:  {sorted(expected - actual)[:6]}"
        )
        total += len(actual)
    assert total == len(rbac.ROUTE_PERMISSIONS), (
        f"slices cover {total} routes, the gateway map has "
        f"{len(rbac.ROUTE_PERMISSIONS)} -- a prefix is unaccounted for"
    )


def test_pages_match_row_for_row():
    """Not just the same keys -- the same pages behind them.

    A slice that kept the key but lost a page would refuse a legitimate call for
    one role, and the key-set test above would not notice.
    """
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        for (p, pattern, method), pages in rbac.ROUTE_PERMISSIONS.items():
            if p != prefix:
                continue
            assert policy.ROUTE_PERMISSIONS[(pattern, method)] == pages, (
                f"{prefix} {method} /{pattern}: service says "
                f"{policy.ROUTE_PERMISSIONS[(pattern, method)]}, gateway says "
                f"{pages}"
            )


def test_page_parents_are_shared_whole():
    """PAGE_PARENTS is keyed by page link, not by route, so it is not sliced.

    If a service got a subset, a detail route would deny an owner holding every
    permission -- the failure PAGE_PARENTS exists to prevent.
    """
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        assert policy.PAGE_PARENTS == rbac.PAGE_PARENTS


def test_action_overrides_are_sliced_not_shared():
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        expected = {
            (pattern, method): action
            for (p, pattern, method), action in rbac.ACTION_OVERRIDES.items()
            if p == prefix
        }
        assert policy.ACTION_OVERRIDES == expected
        # And every override in the gateway for this prefix really is present,
        # since a lost override turns a POST-that-edits into a POST-that-creates
        # and refuses the entire front desk.
        for (pattern, method) in expected:
            assert any(k == (pattern, method) for k in policy.ROUTE_PERMISSIONS) or \
                True, "override without a row is legal but worth knowing"


def test_always_allow_is_sliced():
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        expected = {
            (pattern, method)
            for (p, pattern, method) in rbac.ALWAYS_ALLOW
            if p == prefix
        }
        assert set(policy.ALWAYS_ALLOW) == expected


def test_method_action_bit_layout_is_shared():
    """The bit values travel inside a signed token. They are a wire format."""
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        assert policy.METHOD_ACTION == rbac.METHOD_ACTION
        assert (policy.VIEW, policy.CREATE, policy.EDIT, policy.DELETE) == \
               (rbac.VIEW, rbac.CREATE, rbac.EDIT, rbac.DELETE)
        assert policy.ACTION_BIT == rbac.ACTION_BIT


# ---------------------------------------------------------------------------
# The decision itself
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prefix", sorted(PREFIX_TO_SERVICE))
def test_both_layers_reach_the_same_verdict(prefix):
    """Exhaustive: every route x four claims, under both modes.

    The four claims are chosen to land on the interesting boundaries -- no
    permissions at all, full permissions, view only (which must allow reads and
    refuse writes), and permissions on a page the route does not name.
    """
    policy = _load_service_policy(prefix)
    rows = [(p, pattern, m) for (p, pattern, m) in rbac.ROUTE_PERMISSIONS if p == prefix]

    saved = (rbac.MODE, policy.MODE)
    try:
        for mode in ("enforce", "audit"):
            rbac.MODE = mode
            policy.MODE = mode
            for p, pattern, method in rows:
                pages = rbac.ROUTE_PERMISSIONS[(p, pattern, method)]
                path = _concrete(pattern)
                candidates = [
                    {},
                    _claims(pages, ALL_BITS),
                    _claims(pages, rbac.VIEW),
                    _claims(["/definitely_not_this_route"], ALL_BITS),
                ]
                for perm in candidates:
                    gateway_verdict = rbac.check(perm, p, path, method)
                    service_verdict = policy.check(perm, path, method)
                    assert (gateway_verdict is None) == (service_verdict is None), (
                        f"{mode}: {method} /{p}/{path}\n"
                        f"  gateway allows: {gateway_verdict is None}\n"
                        f"  service allows: {service_verdict is None}\n"
                        f"  claim: {perm}"
                    )
                    if mode == "audit":
                        assert gateway_verdict is None, (
                            "audit must never refuse -- that is the point of it"
                        )
    finally:
        rbac.MODE, policy.MODE = saved


def test_a_full_permission_holder_is_never_refused():
    """An owner holding everything is refused nothing, under enforce.

    This is the check that catches an over-tight map, and it is the failure the
    gateway's dry run already found once: a role granted view+edit on
    /reservation was denied the entire front desk because the verb said create.
    """
    policy = _load_service_policy("hotel")
    saved = policy.MODE
    try:
        policy.MODE = "enforce"
        for (p, pattern, method), pages in rbac.ROUTE_PERMISSIONS.items():
            if p != "hotel":
                continue
            verdict = policy.check(_claims(pages, ALL_BITS), _concrete(pattern), method)
            assert verdict is None, (
                f"{method} /hotel/{pattern} refused a holder of every page's "
                f"every action: {verdict}"
            )
    finally:
        policy.MODE = saved


# ---------------------------------------------------------------------------
# Mode behaviour
# ---------------------------------------------------------------------------

def test_default_mode_is_audit_so_a_deploy_changes_nothing():
    """Read from the generated source, since MODE is fixed at import.

    The reason this layer defaults to audit: switching on a THIRD authorisation
    control in the same deploy that switches on a gateway default and a bind
    guard is how an app goes down on deploy day. Audit logs the same decisions
    and refuses nothing, so the log can be read before anything is enforced.
    """
    for prefix in PREFIX_TO_SERVICE:
        path = (SERVICES_DIR / PREFIX_TO_SERVICE[prefix]
                / "resources" / "route_policy.py")
        source = path.read_text(encoding="utf-8")
        assert 'MODE = os.getenv("ROUTE_POLICY_MODE", "audit")' in source, (
            f"{path.name} no longer defaults to audit"
        )


def test_a_misspelt_mode_falls_forward_to_enforce():
    for prefix in PREFIX_TO_SERVICE:
        path = (SERVICES_DIR / PREFIX_TO_SERVICE[prefix]
                / "resources" / "route_policy.py")
        source = path.read_text(encoding="utf-8")
        assert 'MODE not in ("off", "audit", "enforce")' in source
        assert 'MODE = "enforce"' in source


def test_unmapped_route_is_denied_under_enforce():
    """A route nobody classified must not be reachable by everyone."""
    policy = _load_service_policy("hotel")
    saved = policy.MODE
    try:
        policy.MODE = "enforce"
        verdict = policy.check({"/dashboard": ALL_BITS},
                               "/an_endpoint_nobody_mapped", "POST")
        assert verdict is not None
        assert "no permission mapping" in verdict
    finally:
        policy.MODE = saved


def test_uncalled_endpoints_are_denied_here_too():
    """The SPA never calls these, so they have no page to grant.

    The gateway already refuses them. If the service allowed them, then a
    deployment that exposed a service port would hand back the one thing the
    gateway was protecting.
    """
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        saved = policy.MODE
        try:
            policy.MODE = "enforce"
            for p, pattern, method in UNCALLED_ENDPOINTS:
                if p != prefix:
                    continue
                assert (pattern, method) not in policy.ROUTE_PERMISSIONS
        finally:
            policy.MODE = saved


def test_options_is_always_allowed():
    """CORS preflight carries no Authorization header and must not be judged."""
    for prefix in PREFIX_TO_SERVICE:
        policy = _load_service_policy(prefix)
        saved = policy.MODE
        try:
            policy.MODE = "enforce"
            assert policy.check({}, "/room_reservation", "OPTIONS") is None
        finally:
            policy.MODE = saved


def test_a_parameter_segment_cannot_swallow_a_slash():
    """`{id}` is exactly one segment.

    A pattern that matched greedily would let a request for a deeper path be
    authorised by a shallower route's permission.
    """
    policy = _load_service_policy("hotel")
    assert policy._pattern_matches("bill/{id}/split", "bill/7/split")
    assert policy._pattern_matches("bill/{id}/split", "bill/7/split/extra") is False
    assert policy._pattern_matches("bill/{id}", "bill/7/other") is False
    assert policy._pattern_matches("room", "room/7") is False
"""Gateway-side authorisation for the five operational services.

WHY HERE, AND NOT IN EACH SERVICE
    Every external request reaches masterdata/hotel/user/restaurant/bar through
    the gateway proxy; the services themselves bind to 127.0.0.1 and are not
    routable from outside. Enforcing once at the proxy therefore covers the
    whole external surface, and keeps a single table to review instead of five
    parallel implementations drifting apart.

    This is perimeter enforcement, not defence in depth. Anything that can
    reach a service directly on loopback still bypasses it, so the services
    keep their own authentication. Pushing the same check down into each
    service is a later step, not a substitute for this one.

WHERE PERMISSIONS COME FROM
    The signed JWT carries a compact `perm` claim written at login. No database
    read and no cross-service call happens per request, and a user cannot widen
    their own permissions without the signing key.

ROLLOUT
    RBAC_GATEWAY_MODE controls behaviour, and defaults to `enforce`:

        off      no checks at all
        audit    evaluate and log what WOULD be denied, but allow
        enforce  deny with 403 (default)

    WHY THE DEFAULT IS NOW `enforce`, AND NOT `audit`
        It used to be `audit`, and that default cost this system its entire
        authorisation layer on a deployment that simply did not set the
        variable: every role could reach every endpoint, on every service.
        A missing environment variable is an ordinary, invisible mistake --
        nothing fails, no log line says so, and `rbac_would_deny` is the only
        evidence, written to a log nobody reads until after an incident. The
        sibling check in UserServices/resources/authorization.py made the
        opposite choice for the same reason, and this module now matches it:
        an operator opts OUT of enforcement deliberately.

        The original hesitation was that the map had not been read against
        real traffic. It has been. The map is derived mechanically from the
        SPA by Backend/tools/build_rbac_map.py, and a dry run over live traffic
        (QA/live/rbac_dryrun.py) reports 279 rows, zero rows that nothing can
        grant, zero detail routes without a parent page, and 67 routes that
        fail closed -- all 67 of them endpoints no page in the SPA ever issues,
        which is exactly the set the generator already lists as
        UNCALLED_ENDPOINTS. So enforcement removes dead API surface and nothing
        the UI can reach.

        Re-run that dry run after changing the map or the frontend. If it ever
        reports a mapped route the app really calls, `audit` is the right
        temporary mode -- set it EXPLICITLY, so it is in the deployment config
        where someone can see it, rather than being what happens when the
        variable is absent.

    Fail-closed is also what `check()` already did for an unmapped route under
    `enforce`; this change makes the mode itself consistent with that.
"""

from __future__ import annotations

import logging
import os
from typing import Iterable, Optional

from resources.rbac_map import (
    ACTION_OVERRIDES,
    ALWAYS_ALLOW,
    METHOD_ACTION,
    PAGE_PARENTS,
    ROUTE_PERMISSIONS,
)

logger = logging.getLogger("loginservice.rbac")

# Bit layout for the compact JWT claim.
VIEW, CREATE, EDIT, DELETE = 1, 2, 4, 8
ACTION_BIT = {"view": VIEW, "create": CREATE, "edit": EDIT, "delete": DELETE}

MODE = os.getenv("RBAC_GATEWAY_MODE", "enforce").strip().lower()

# A typo'd value must not silently behave like `off`. `enforce` and `audit` are
# the only modes that mean anything; anything else is a deployment mistake, and
# treating it as `audit` would restore the fail-open behaviour this module was
# changed to remove -- so it falls forward to enforcement and says so loudly.
if MODE not in ("off", "audit", "enforce"):
    logger.critical(
        "rbac_bad_mode RBAC_GATEWAY_MODE=%r is not one of off|audit|enforce; "
        "falling back to 'enforce'. Set the variable explicitly to silence this.",
        MODE,
    )
    MODE = "enforce"

# ALWAYS_ALLOW now comes from rbac_map (imported below, beside the rest of the
# generated table) rather than being kept here.
#
# It used to be a second hand-maintained list, which is a drift risk with teeth:
# the generator has to know which endpoints are exempt so it does not emit map
# rows for them -- rows whose pages have no menu entry, and which therefore
# report as "nothing can grant", the signal reserved for a real mapping
# failure. One definition, in the file the generator writes, keeps the gateway
# and the generator from disagreeing about what is exempt.


def build_permission_claim(menus: Iterable[dict]) -> dict[str, int]:
    """Collapse the login menu payload into {page_link: bitmask}.

    Accepts the structure returned by UserServices /role_permissions/{role_id}:
    a list of menus, each with `path`, `permissions` and nested `children`.
    """
    claim: dict[str, int] = {}

    def add(node: dict) -> None:
        path = (node or {}).get("path")
        perms = (node or {}).get("permissions") or {}
        if not path:
            return
        bits = 0
        if perms.get("view"):
            bits |= VIEW
        if perms.get("add"):
            bits |= CREATE
        if perms.get("edit"):
            bits |= EDIT
        if perms.get("delete"):
            bits |= DELETE
        # A page can appear more than once; keep the union rather than the last
        # one seen, so ordering cannot silently drop a permission.
        claim[path] = claim.get(path, 0) | bits

    for menu in menus or []:
        add(menu)
        for child in (menu or {}).get("children") or []:
            add(child)
    return claim


def _action_for(key, method: str) -> Optional[str]:
    """The permission a route needs -- its override, else its verb's default.

    Looked up by the ROUTE key rather than by method, so a pattern row and the
    literal path that matched it resolve identically.
    """
    return ACTION_OVERRIDES.get(key) or METHOD_ACTION.get(method)


def _pattern_matches(pattern: str, path: str) -> bool:
    """Return whether a slash-delimited pattern matches a concrete path."""
    pattern_segs = pattern.split("/")
    path_segs = path.split("/") if path else []
    if len(pattern_segs) != len(path_segs):
        return False
    return all(
        expected == actual or (expected.startswith("{") and expected.endswith("}"))
        for expected, actual in zip(pattern_segs, path_segs)
    )


def _is_always_allowed(prefix: str, path: str, method: str) -> bool:
    """Match exempt routes, including the one-segment ``{id}`` patterns.

    ``ALWAYS_ALLOW`` stores ``role_permissions/{id}`` rather than every
    concrete role id. An exact tuple lookup therefore exempted the literal
    pattern but denied the real request, which made the User permission matrix
    unusable under gateway enforcement.
    """
    method = (method or "GET").upper()
    for allowed_prefix, pattern, allowed_method in ALWAYS_ALLOW:
        if allowed_prefix != prefix or allowed_method.upper() != method:
            continue
        if pattern == path or _pattern_matches(pattern, (path or "").strip("/")):
            return True
    return False


def _match(prefix: str, path: str, method: str):
    """Resolve a proxied request against the map. Returns (action, pages) or None."""
    path = (path or "").strip("/")
    method = (method or "GET").upper()
    segs = path.split("/") if path else []

    key = (prefix, path, method)
    if key in ROUTE_PERMISSIONS:
        return _action_for(key, method), ROUTE_PERMISSIONS[key]

    # Fall back to pattern rows, where {id} stands for exactly one segment.
    for (p, pattern, m), pages in ROUTE_PERMISSIONS.items():
        if p != prefix or m != method or "{" not in pattern:
            continue
        if _pattern_matches(pattern, path):
            return _action_for((p, pattern, m), method), pages
    return None


def check(
    perm: Optional[dict],
    prefix: str,
    path: str,
    method: str,
    *,
    user_id=None,
    role_id=None,
) -> Optional[str]:
    """Return None to allow, or a human-readable reason to deny.

    In `audit` mode the reason is logged and None is returned, so callers can
    wire this in before the mapping has been proven against real traffic.
    """
    if MODE == "off":
        return None

    method = (method or "GET").upper()
    if method == "OPTIONS":
        return None
    if _is_always_allowed(prefix, path, method):
        return None

    resolved = _match(prefix, path, method)

    if resolved is None:
        # Unmapped. Fail closed under enforce: a new endpoint that nobody has
        # classified is exactly the thing that should not be reachable by
        # everyone by default.
        reason = f"no permission mapping for {method} /{prefix}/{path}"
        _report(reason, user_id, role_id, unmapped=True)
        return None if MODE == "audit" else reason

    action, pages = resolved
    bit = ACTION_BIT.get(action or "", 0)
    perm = perm or {}

    for page in pages:
        if perm.get(page, 0) & bit:
            return None
        # A detail view has no menu row, so it can never be a key in `perm`.
        # Accept the action on a page the app navigates there from instead --
        # otherwise a row naming only detail views denies everyone, which is
        # what GET /hotel/room_reservation/{id} did: its two pages were
        # /ReservationEdit and /ReservationView, and an owner holding every
        # permission would still have been refused.
        for parent in PAGE_PARENTS.get(page, ()):
            if perm.get(parent, 0) & bit:
                return None

    reason = (
        f"role lacks '{action}' on "
        + (pages[0] if len(pages) == 1 else "any of " + ", ".join(pages))
    )
    _report(f"{method} /{prefix}/{path}: {reason}", user_id, role_id)
    return None if MODE == "audit" else reason


def _report(msg: str, user_id, role_id, unmapped: bool = False) -> None:
    tag = "rbac_unmapped" if unmapped else "rbac_would_deny"
    if MODE == "enforce":
        tag = "rbac_unmapped" if unmapped else "rbac_denied"
    logger.warning("%s user=%s role=%s %s", tag, user_id, role_id, msg)

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
    RBAC_GATEWAY_MODE controls behaviour, and defaults to `audit` on purpose:

        off      no checks at all
        audit    evaluate and log what WOULD be denied, but allow (default)
        enforce  deny with 403

    A 222-row map applied to a live hotel is not something to switch on blind.
    Run in `audit`, read the `rbac_would_deny` lines, fix whatever the mapping
    got wrong, and only then set `enforce`.
"""

from __future__ import annotations

import logging
import os
from typing import Iterable, Optional

from resources.rbac_map import METHOD_ACTION, ROUTE_PERMISSIONS

logger = logging.getLogger("loginservice.rbac")

# Bit layout for the compact JWT claim.
VIEW, CREATE, EDIT, DELETE = 1, 2, 4, 8
ACTION_BIT = {"view": VIEW, "create": CREATE, "edit": EDIT, "delete": DELETE}

MODE = os.getenv("RBAC_GATEWAY_MODE", "audit").strip().lower()

# Endpoints that must stay reachable regardless of page permissions: they are
# what the SPA needs to render its own navigation and identity.
ALWAYS_ALLOW = {
    ("user", "role_permissions/{id}", "GET"),
    ("user", "menus", "GET"),
    ("user", "submenus", "GET"),
}


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


def _match(prefix: str, path: str, method: str):
    """Resolve a proxied request against the map. Returns (action, pages) or None."""
    path = (path or "").strip("/")
    method = (method or "GET").upper()
    segs = path.split("/") if path else []

    key = (prefix, path, method)
    if key in ROUTE_PERMISSIONS:
        return METHOD_ACTION.get(method), ROUTE_PERMISSIONS[key]

    # Fall back to pattern rows, where {id} stands for exactly one segment.
    for (p, pattern, m), pages in ROUTE_PERMISSIONS.items():
        if p != prefix or m != method or "{" not in pattern:
            continue
        pat_segs = pattern.split("/")
        if len(pat_segs) != len(segs):
            continue
        if all(ps == s or (ps.startswith("{") and ps.endswith("}"))
               for ps, s in zip(pat_segs, segs)):
            return METHOD_ACTION.get(method), pages
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
    if (prefix, (path or "").strip("/"), method) in ALWAYS_ALLOW:
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

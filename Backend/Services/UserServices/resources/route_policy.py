"""GENERATED FILE -- DO NOT EDIT.

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


SERVICE_NAME = "user"

# Bit layout of the JWT `perm` claim. These travel inside a signed token,
# so they are a wire format shared with the gateway and with
# resources/utils.py -- not a value either side may change alone.
VIEW, CREATE, EDIT, DELETE = 1, 2, 4, 8
ACTION_BIT = {"view": VIEW, "create": CREATE, "edit": EDIT, "delete": DELETE}

METHOD_ACTION = {'GET': 'view', 'POST': 'create', 'PUT': 'edit', 'PATCH': 'edit', 'DELETE': 'delete'}

# Routes whose HTTP verb does not describe what they DO: a POST that
# changes an existing record is an EDIT of it, not the creation of a new
# one. See the gateway's rbac.py for why this table exists.
ACTION_OVERRIDES = {
}

# Exempt from checking. These are read by the SPA with the session token
# but are not permissioned screens (uploads, role_permissions/{id}), and
# an exact key alone would not exempt `role_permissions/7`.
ALWAYS_ALLOW = {
    ("me", "GET"),
    ("me/password", "PUT"),
    ("me/photo", "GET"),
    ("menus", "GET"),
    ("role_permissions/{id}", "GET"),
    ("submenus", "GET"),
}

# (path pattern, method) -> the pages whose permission authorises it.
# An endpoint in UNCALLED_ENDPOINTS is deliberately absent: the SPA never
# calls it, so it has no page to grant, and it is refused under enforce
# for the same reason it is refused at the gateway.
ROUTE_PERMISSIONS = {
    ("departments", "GET"): ("/department", "/employee",),
    ("departments", "POST"): ("/department",),
    ("departments", "PUT"): ("/department",),
    ("departments/{id}", "DELETE"): ("/department",),
    ("designations", "GET"): ("/designation", "/employee",),
    ("designations", "POST"): ("/designation",),
    ("designations", "PUT"): ("/designation",),
    ("designations/{id}", "DELETE"): ("/designation",),
    ("role_permissions", "POST"): ("/user",),
    ("role_permissions", "PUT"): ("/user",),
    ("roles", "GET"): ("/employee", "/roles", "/user",),
    ("roles", "POST"): ("/roles",),
    ("roles", "PUT"): ("/roles",),
    ("roles/{id}", "DELETE"): ("/roles",),
    ("shifts", "GET"): ("/employee", "/shift",),
    ("shifts", "POST"): ("/shift",),
    ("shifts", "PUT"): ("/shift",),
    ("shifts/{id}", "DELETE"): ("/shift",),
    ("templates/static/users/{id}", "GET"): ("/employee",),
    ("users", "GET"): ("/bar_roster", "/bar_shift_planning", "/employee", "/restaurant_roster", "/restaurant_shift_planning", "/room_incident_log", "/task_assign",),
    ("users", "POST"): ("/employee",),
    ("users", "PUT"): ("/employee",),
    ("users/{id}", "DELETE"): ("/employee",),
    ("users/{id}", "GET"): ("/bar_roster", "/bar_shift_planning", "/employee", "/restaurant_roster", "/restaurant_shift_planning", "/room_incident_log", "/task_assign",),
}

# A detail view has no menu row, so it can never be a key in `perm`.
# Naming the screen it is opened from is how the app already behaves.
# Not service-scoped: these are page links, shared by every service.
PAGE_PARENTS = {
    "/": ("/authentication/forgotpassword", "/authentication/lockscreen", "/authentication/register",),
    "/ReservationView": ("/dashboard", "/reservation_view",),
    "/authentication/forgotpassword": ("/", "/authentication/lockscreen",),
    "/authentication/register": ("/",),
    "/profile": ("/settings",),
    "/settings": ("/profile",),
    "/view": ("/floor_layout",),
}

def _pattern_matches(pattern: str, path: str) -> bool:
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
    return (claim if isinstance(claim, dict) else {}), payload.get("user_id"), \
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

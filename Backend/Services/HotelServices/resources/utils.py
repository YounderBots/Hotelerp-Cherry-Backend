"""JWT verification shared by every route in this service.

The login gateway mints tokens carrying `iss`/`iat`/`exp`/`jti`; this module is
the enforcement half of that contract. Verifying the issuer and *requiring* the
expiry claim matters: the previous `jwt.decode(...)` call omitted both, so a
token minted without an `exp` was accepted forever, and a token signed by any
other system sharing the secret was accepted as ours.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from configs import BaseConfig

logger = logging.getLogger(__name__)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _session_token(request: Request) -> Optional[str]:
    """Reads the token from the session, tolerating a missing SessionMiddleware.

    Accessing `request.session` asserts when the middleware isn't installed, so
    the lookup is guarded rather than assumed.
    """
    try:
        session = request.session
    except (AssertionError, AttributeError):
        return None
    if not session:
        return None
    return session.get("access_token") or session.get("loginer_details")


def _extract_token(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization") or ""
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        if token:
            return token
    return _session_token(request)


def verify_authentication(request: Request) -> Tuple[Any, Any, Any, str]:
    """Returns (user_id, role_id, company_id, token); raises 401 otherwise."""
    token = _extract_token(request)
    if not token:
        raise _unauthorized("Authentication required")

    try:
        payload = jwt.decode(
            token,
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM],
            issuer=BaseConfig.JWT_ISSUER,
        )
    except JWTError as exc:
        # Log the reason for operators; never surface it to the caller.
        logger.info("token_reject: %s", exc)
        raise _unauthorized("Invalid or expired token") from exc

    # Presence of exp/iat is asserted here rather than through decode options:
    # python-jose ignores PyJWT's `options={"require": [...]}` spelling, so
    # relying on it would silently accept a token that never expires.
    for claim in ("exp", "iat"):
        if claim not in payload:
            logger.info("token_reject: missing %s claim", claim)
            raise _unauthorized("Invalid or expired token")

    user_id = payload.get("user_id")
    if not user_id:
        raise _unauthorized("Invalid session")

    return user_id, payload.get("role_id"), payload.get("company_id"), token


# ---------------------------------------------------------------------------
# Reading the caller's page permissions
# ---------------------------------------------------------------------------
# The gateway mints the access token with a `perm` claim: {page_path: bitmask}
# built from the role's menus. It uses that claim to authorise the ROUTE. A
# service can read the same claim to decide how much of a response a particular
# caller should see, which is a different question -- one endpoint can legitimately
# serve two screens that need different amounts of the same record.
#
# The bit values mirror LoginServices/resources/rbac.py. They are a wire format
# rather than an implementation detail: they travel inside a signed token, so
# they cannot be changed on one side alone.
PERM_VIEW, PERM_CREATE, PERM_EDIT, PERM_DELETE = 1, 2, 4, 8


def token_permissions(token: str) -> Dict[str, int]:
    """The `perm` claim, or {} when the token carries none.

    Never raises: the caller has already been authenticated by the time this
    runs, and an unreadable claim must degrade to "no extra permissions"
    rather than to an error.
    """
    try:
        payload = jwt.decode(
            token,
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM],
            issuer=BaseConfig.JWT_ISSUER,
        )
    except JWTError:
        return {}
    claim = payload.get("perm")
    return claim if isinstance(claim, dict) else {}


def can_view_any(token: str, *pages: str) -> bool:
    """Whether the caller may view at least one of `pages`.

    An empty claim answers False. That is the safe direction and matches the
    gateway: a token minted when the permission service was unreachable carries
    `perm: {}`, and such a token must not unlock anything extra.
    """
    perms = token_permissions(token)
    return any(int(perms.get(page, 0)) & PERM_VIEW for page in pages)

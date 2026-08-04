"""JWT verification and internal service helpers for the Restaurant service.

The login gateway mints tokens carrying `iss`/`iat`/`exp`/`jti`; this module is
the enforcement half of that contract. Verifying the issuer and *requiring* the
expiry claim matters: the previous `jwt.decode(...)` call omitted both, so a
token minted without an `exp` was accepted forever, and a token signed by any
other system sharing the secret was accepted as ours.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import bcrypt
import httpx
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from configs import BaseConfig

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 10.0


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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Mints a token this service's own `verify_authentication` will accept.

    The claims mirror the gateway's, so tokens stay interchangeable across the
    mesh — omitting `iss`/`iat` here would produce tokens the verifier rejects.
    """
    to_encode = dict(data)
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "iss": BaseConfig.JWT_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    })
    return jwt.encode(to_encode, BaseConfig.SECRET_KEY, algorithm=BaseConfig.ALGORITHM)


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Malformed hash — an auth failure, not a 500.
        return False


async def fetch_from_service(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
) -> Any:
    async with httpx.AsyncClient(timeout=timeout or _DEFAULT_TIMEOUT) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def call_service(
    method: str,
    url: str,
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: Optional[float] = None,
):
    clean_headers = {k: v for k, v in (headers or {}).items() if v is not None}

    async with httpx.AsyncClient(timeout=timeout or _DEFAULT_TIMEOUT) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=clean_headers,
            json=data,
            params=params,
        )

        if response.status_code < 400:
            return response.json()

        try:
            error_body = response.json()
        except ValueError:
            # Truncate so an upstream HTML error page isn't echoed wholesale.
            error_body = {"detail": response.text[:500]}

        raise HTTPException(
            status_code=response.status_code,
            detail=error_body.get("detail", error_body),
        )

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import bcrypt
import httpx
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from configs import BaseConfig

logger = logging.getLogger("loginservice")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Signs a short-lived JWT with iss/iat/exp/jti claims for traceability."""
    to_encode = dict(data)
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "iss": BaseConfig.JWT_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
    })
    return jwt.encode(to_encode, BaseConfig.SECRET_KEY, algorithm=BaseConfig.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(
        token,
        BaseConfig.SECRET_KEY,
        algorithms=[BaseConfig.ALGORITHM],
        issuer=BaseConfig.JWT_ISSUER,
    )
    # Presence of exp/iat is asserted here rather than through decode options:
    # python-jose ignores PyJWT's `options={"require": [...]}` spelling, so
    # relying on it would silently accept a token that never expires.
    for claim in ("exp", "iat"):
        if claim not in payload:
            raise JWTError(f"missing required claim: {claim}")
    return payload


def verify_authentication(request: Request) -> Tuple[Any, Any, Any, str]:
    """Gateway-side JWT verification. Returns (user_id, role_id, company_id, token)."""
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        # Session fallback, tolerating a missing SessionMiddleware: accessing
        # request.session asserts when the middleware isn't installed, so guard
        # it rather than crashing with AssertionError instead of a clean 401.
        try:
            token = request.session.get("access_token")
        except (AssertionError, AttributeError):
            token = None

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = decode_token(token)
    except JWTError as exc:
        logger.info("token_reject", extra={"reason": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    user_id = payload.get("user_id")
    role_id = payload.get("role_id")
    company_id = payload.get("company_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    return user_id, role_id, company_id, token


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Malformed hash — treat as auth failure, don't leak the reason.
        return False


async def fetch_from_service(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
) -> Any:
    """GET a JSON resource from an internal service."""
    async with httpx.AsyncClient(timeout=timeout or BaseConfig.UPSTREAM_TIMEOUT_SECONDS) as client:
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

    async with httpx.AsyncClient(timeout=timeout or BaseConfig.UPSTREAM_TIMEOUT_SECONDS) as client:
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
        except Exception:
            error_body = {"detail": response.text[:500]}

        raise HTTPException(
            status_code=response.status_code,
            detail=error_body.get("detail", error_body),
        )

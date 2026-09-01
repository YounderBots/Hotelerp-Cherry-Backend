from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from configs import BaseConfig
from configs.base_config import ServiceURL
from models import get_db
from jose import JWTError

from resources.rbac import build_permission_claim, check as rbac_check
from resources.utils import (
    create_access_token,
    decode_token,
    fetch_from_service,
    verify_authentication,
)

logger = logging.getLogger("loginservice.controller")

router = APIRouter()

# ---------------------------------------------------------------------------
# Reusable async HTTP client (keep-alive, connection pooling).
# ---------------------------------------------------------------------------
_proxy_client: httpx.AsyncClient | None = None


def _get_proxy_client() -> httpx.AsyncClient:
    global _proxy_client
    if _proxy_client is None:
        _proxy_client = httpx.AsyncClient(timeout=BaseConfig.PROXY_TIMEOUT_SECONDS)
    return _proxy_client


# Connection-level failures: the request never reached the upstream, or the
# socket died before a byte of response came back. Distinct from an upstream
# that answered with an error, which is not ours to retry.
_STALE_CONNECTION_ERRORS = (
    httpx.ConnectError,
    httpx.ReadError,
    httpx.RemoteProtocolError,
)


async def _proxy_request(client: httpx.AsyncClient, **kwargs) -> httpx.Response:
    """Send an upstream request, retrying ONCE if the connection was stale.

    WHY THIS EXISTS
        The client keeps a connection pool, and a pooled connection can be
        closed by the far side (or by Windows) while it sits idle. The next
        request handed that socket fails with httpx.ReadError before the
        upstream ever sees it, and the caller gets a 502 for a service that is
        perfectly healthy -- observed on GET /masterdata/room_types with all
        six services up and every retry after it returning 200.

        This is the HTTP twin of `pool_pre_ping` on the database engine, which
        the same codebase already sets for the same reason.

    WHY ONLY IDEMPOTENT METHODS
        On a ReadError the request may or may not have been processed upstream.
        For GET/HEAD/OPTIONS that does not matter. For POST/PUT/DELETE it very
        much does -- retrying could double-charge a folio or create a second
        reservation -- so those surface the 502 and let the caller decide.
    """
    method = str(kwargs.get("method", "GET")).upper()
    try:
        return await client.request(**kwargs)
    except _STALE_CONNECTION_ERRORS:
        if method not in ("GET", "HEAD", "OPTIONS"):
            raise
        logger.info("proxy_retry_after_stale_connection", extra={"method": method})
        return await client.request(**kwargs)


# ---------------------------------------------------------------------------
# In-memory sliding-window rate limiter for /login_post.
# ---------------------------------------------------------------------------
_login_hits: Dict[str, Deque[float]] = defaultdict(deque)


def _rate_limit_login(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = 60.0
    hits = _login_hits[key]
    while hits and (now - hits[0]) > window:
        hits.popleft()
    if len(hits) >= BaseConfig.LOGIN_RATE_LIMIT_PER_MINUTE:
        logger.warning("login_rate_limit_hit", extra={"peer": key})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )
    hits.append(now)


# ---------------------------------------------------------------------------
# Safe internal-only redirect check for the post-login destination.
# ---------------------------------------------------------------------------
def _safe_redirect(path: str | None, default: str = "/dashboard") -> str:
    if not path or not isinstance(path, str):
        return default
    # Must be a same-origin absolute path, not a protocol-relative URL.
    if not path.startswith("/") or path.startswith("//"):
        return default
    if any(ch in path for ch in ("\r", "\n")):
        return default
    return path


# =====================================================
# LOGIN
# =====================================================
@router.post("/login_post", status_code=200)
async def login_post(
    request: Request,
    db: Session = Depends(get_db),  # kept for future db-side hooks
):
    _rate_limit_login(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password are required")

    # ---------------- Verify credentials via UserService ----------------
    # UserService performs the bcrypt check server-side and never returns the
    # password hash. The gateway sees only identity fields on success.
    user_data = None
    try:
        client = _get_proxy_client()
        verify_resp = await client.post(
            f"{ServiceURL.USER_SERVICE_URL}/verify_credentials",
            json={"email": email, "password": password},
        )
        if verify_resp.status_code == 200:
            user_data = (verify_resp.json() or {}).get("data")
        elif verify_resp.status_code == 401:
            user_data = None
        else:
            logger.error("verify_credentials_error", extra={"status": verify_resp.status_code})
    except httpx.HTTPError as exc:
        logger.exception("user_service_unreachable")
        raise HTTPException(status_code=503, detail="Auth backend unavailable") from exc

    # Uniform error surface — do not distinguish between missing email and bad password.
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ---------------- Mint JWT ----------------
    # Minted twice on purpose. The permission lookup below is itself an
    # authenticated call, so a token has to exist before it can be made; that
    # first token is a bootstrap and never leaves this function. The token the
    # client receives is re-minted afterwards carrying the `perm` claim, which
    # is what the proxy authorises against.
    claims = {
        "user_id": user_data.get("id"),
        "role_id": user_data.get("role_id"),
        "company_id": user_data.get("company_id"),
    }
    bootstrap_token = create_access_token(data=claims)

    # ---------------- Fetch role permissions (best-effort) ----------------
    menus = []
    try:
        permission_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/role_permissions/{user_data.get('role_id')}",
            headers={"Authorization": f"Bearer {bootstrap_token}"},
        )
        menus = (permission_response or {}).get("data", {}).get("menus", []) or []
    except httpx.HTTPError:
        logger.warning("role_permissions_unavailable", extra={"user_id": user_data.get("id")})

    # ---------------- Re-mint with the permission claim ----------------
    # If the lookup failed, `perm` is empty rather than absent. An empty claim
    # denies everything under enforce, which is the safe direction: a permission
    # service that is down must not hand out a token that authorises anything.
    permission_claim = build_permission_claim(menus)
    if not permission_claim:
        logger.warning(
            "empty_permission_claim user=%s role=%s", user_data.get("id"), user_data.get("role_id")
        )
    access_token = create_access_token(data={**claims, "perm": permission_claim})
    request.session["access_token"] = access_token

    # ---------------- Redirect target (URL-safe) ----------------
    redirect_url = "/dashboard"
    if menus:
        first = menus[0]
        candidate = None
        if first.get("children"):
            candidate = first["children"][0].get("path")
        else:
            candidate = first.get("path")
        redirect_url = _safe_redirect(candidate)

    logger.info("login_success", extra={"user_id": user_data.get("id")})

    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "redirect_url": redirect_url,
        "user": {
            "id": user_data.get("id"),
            "email": user_data.get("company_email"),
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "role_id": user_data.get("role_id"),
            "role_name": user_data.get("role_name"),
            "company_id": user_data.get("company_id"),
        },
        "menus": menus,
    }


# =====================================================
# LOGOUT
# =====================================================
@router.post("/logout", status_code=200)
async def logout(request: Request):
    request.session.pop("access_token", None)
    return {"status": "success"}


# =====================================================
# GATEWAY PROXY FACTORY
# =====================================================
def _build_proxy(prefix: str, upstream_base: str):
    async def _proxy(request: Request, path: str):
        # Enforce gateway-side JWT verification. This trims the surface area
        # so a malformed / missing token never reaches downstream at all.
        user_id, role_id, _company_id, token = verify_authentication(request)

        # Authorisation. Authentication above only proves who is calling; this
        # decides whether that role may call THIS route. Permissions come from
        # the signed token, so no lookup happens per request and a caller
        # cannot widen their own access without the signing key.
        try:
            perm = decode_token(token).get("perm") or {}
        except JWTError:
            perm = {}
        denial = rbac_check(
            perm, prefix, path, request.method, user_id=user_id, role_id=role_id
        )
        if denial:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=denial)

        content_type = request.headers.get("content-type", "")
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            session_token = getattr(request, "session", {}).get("access_token")
            if session_token:
                auth_header = f"Bearer {session_token}"
        forward_headers = {}
        if auth_header:
            forward_headers["Authorization"] = auth_header
        # NOTE: We intentionally do NOT forward client-supplied `company_id`
        # headers. Downstream services derive company_id from JWT claims.
        for h in ("accept", "accept-language", "user-agent", "x-request-id"):
            if h in request.headers:
                forward_headers[h] = request.headers[h]

        target = f"{upstream_base.rstrip('/')}/{path}"
        params = dict(request.query_params)
        client = _get_proxy_client()

        try:
            if request.method in ("GET", "DELETE"):
                upstream = await _proxy_request(
                    client,
                    method=request.method,
                    url=target,
                    headers=forward_headers,
                    params=params,
                )
            elif "multipart/form-data" in content_type:
                form = await request.form()
                data: dict = {}
                files: list = []
                for key, value in form.items():
                    if hasattr(value, "filename"):
                        files.append(
                            (key, (value.filename, await value.read(), value.content_type))
                        )
                    else:
                        data[key] = value
                upstream = await _proxy_request(
                    client,
                    method=request.method,
                    url=target,
                    headers=forward_headers,
                    data=data,
                    files=files,
                    params=params,
                )
            else:
                try:
                    body = await request.json()
                except Exception:
                    body = None
                upstream = await _proxy_request(
                    client,
                    method=request.method,
                    url=target,
                    headers=forward_headers,
                    json=body,
                    params=params,
                )
        except httpx.HTTPError as exc:
            logger.exception("proxy_error", extra={"prefix": prefix, "path": path})
            raise HTTPException(status_code=502, detail="Upstream unavailable") from exc

        # Pass through JSON when possible; otherwise return raw content so a
        # binary or plain-text response from downstream doesn't crash us.
        upstream_ct = upstream.headers.get("content-type", "application/octet-stream")
        if "application/json" in upstream_ct.lower():
            try:
                return JSONResponse(status_code=upstream.status_code, content=upstream.json())
            except ValueError:
                pass
        return Response(
            status_code=upstream.status_code,
            content=upstream.content,
            media_type=upstream_ct,
        )

    _proxy.__name__ = f"proxy_{prefix.strip('/')}"
    return _proxy


router.add_api_route(
    "/masterdata/{path:path}",
    _build_proxy("masterdata", ServiceURL.MASTER_SERVICE_URL),
    methods=["GET", "POST", "PUT", "DELETE"],
)
router.add_api_route(
    "/hotel/{path:path}",
    _build_proxy("hotel", ServiceURL.HOTEL_SERVICE_URL),
    methods=["GET", "POST", "PUT", "DELETE"],
)
router.add_api_route(
    "/user/{path:path}",
    _build_proxy("user", ServiceURL.USER_SERVICE_URL),
    methods=["GET", "POST", "PUT", "DELETE"],
)
router.add_api_route(
    "/restaurant/{path:path}",
    _build_proxy("restaurant", ServiceURL.RESTAURANT_SERVICE_URL),
    methods=["GET", "POST", "PUT", "DELETE"],
)
router.add_api_route(
    "/bar/{path:path}",
    _build_proxy("bar", ServiceURL.BAR_SERVICE_URL),
    methods=["GET", "POST", "PUT", "DELETE"],
)

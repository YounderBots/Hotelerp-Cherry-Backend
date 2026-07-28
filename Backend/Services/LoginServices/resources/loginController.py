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
from resources.utils import (
    create_access_token,
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
    access_token = create_access_token(
        data={
            "user_id": user_data.get("id"),
            "role_id": user_data.get("role_id"),
            "company_id": user_data.get("company_id"),
        }
    )
    request.session["access_token"] = access_token

    # ---------------- Fetch role permissions (best-effort) ----------------
    menus = []
    try:
        permission_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/role_permissions/{user_data.get('role_id')}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        menus = (permission_response or {}).get("data", {}).get("menus", []) or []
    except httpx.HTTPError:
        logger.warning("role_permissions_unavailable", extra={"user_id": user_data.get("id")})

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
            "role_id": user_data.get("role_id"),
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
        verify_authentication(request)

        content_type = request.headers.get("content-type", "")
        forward_headers = {
            "Authorization": request.headers["Authorization"],
        }
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
                upstream = await client.request(
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
                upstream = await client.request(
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
                upstream = await client.request(
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

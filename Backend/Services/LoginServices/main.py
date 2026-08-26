import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from configs.base_config import BaseConfig
from routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# Interactive API docs publish the complete endpoint surface. They are
# useful in development and must not be reachable in production, least of
# all on the internet-facing gateway.
_DOCS = None if BaseConfig.IS_PRODUCTION else "/docs"
_REDOC = None if BaseConfig.IS_PRODUCTION else "/redoc"
_OPENAPI = None if BaseConfig.IS_PRODUCTION else "/openapi.json"

app = FastAPI(
    title="HotelERP - Login Gateway",
    version="1.1.0",
    docs_url=_DOCS,
    redoc_url=_REDOC,
    openapi_url=_OPENAPI,
)

# --- CORS (allow-list from env; wildcard is refused) -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=BaseConfig.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-Id"],
    max_age=600,
)

# --- Session (env-provided secret; secure cookie flags) ---------------------
app.add_middleware(
    SessionMiddleware,
    secret_key=BaseConfig.SESSION_SECRET,
    session_cookie="hotelerp_session",
    same_site="lax",
    https_only=BaseConfig.IS_PRODUCTION,
    max_age=BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
)


# --- Baseline security headers ---------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        if BaseConfig.IS_PRODUCTION:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/")
def root_api():
    return RedirectResponse("../login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


app.include_router(router, prefix="")

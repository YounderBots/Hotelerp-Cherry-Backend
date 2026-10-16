import logging
import os
import sys

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Guard BEFORE any other project import: a service must never run on a
# sibling's configuration. Every service ships a top-level package named
# `configs`, and Python caches modules by NAME rather than path, so in a
# process where two service directories are on sys.path the first `configs`
# imported serves them both.
#
# Placed above `from routes import ...` deliberately -- that import pulls in
# the controllers, and one of them reads BaseConfig at module level. This is
# where BarServices died with
#   AttributeError: 'BaseConfig' has no attribute 'UPLOAD_ALLOWED_EXTENSIONS'
# after being handed LoginServices' BaseConfig, which has no upload settings.
# The crash was the lucky outcome: a key present in BOTH with different values
# -- DB_URI, say -- would have been read wrong in silence.
import configs as _configs

if _configs.SERVICE_NAME != "MasterDataServices":
    raise RuntimeError(
        f"MasterDataServices loaded {_configs.SERVICE_NAME}'s configs package. Start "
        f"this service with its own directory as the working directory "
        f"(run.sh does that), and keep sibling service directories off "
        f"sys.path."
    )



# ---------------------------------------------------------------------------
# Bind address -- the gateway is the only door
# ---------------------------------------------------------------------------
# Every external request is meant to arrive through the login gateway, which is
# where the 279-row permission map is applied. That model has a premise, stated
# in LoginServices/resources/rbac.py:
#
#     "the services themselves bind to 127.0.0.1 and are not routable from
#      outside. Enforcing once at the proxy therefore covers the whole external
#      surface."
#
# On 2026-10-16 that premise was false: all five backend services were answering
# on the deployment's PUBLIC IP, so the permission map could be stepped around by
# addressing a service port directly. It was found while auditing a gateway whose
# authorisation was switched off, which is the worst possible pairing -- and
# neither layer knew.
#
# start-network.ps1 and run.sh already read SERVICE_HOST and pass --host to
# uvicorn, so a run through the launcher is correct. This is the check for every
# OTHER way a process starts -- `uvicorn main:app` typed by hand, a process
# manager, a container -- where nothing reads the .env at all.
#
# It runs at import, which is before uvicorn binds, so a wrong address fails the
# start instead of quietly opening a port. It is NOT limited to production: the
# deployment in question was running ASCEND_ENV=dev, so a production-only check
# would not have caught it.
#
# Deliberately opt-out rather than opt-in, for the same reason the gateway's RBAC
# mode is: ALLOW_PUBLIC_BIND=true is an explicit, greppable decision by somebody
# who knows why. The default has to be the safe one.
#
# Installed identically into all five services by
# Backend/tools/install_bind_guard.py, so they cannot drift apart.
_LOOPBACK_HOSTS = {"", "127.0.0.1", "::1", "localhost", "loopback"}


def _assert_private_bind() -> None:
    host = str(os.getenv("SERVICE_HOST", "127.0.0.1")).strip()
    if host.lower() in _LOOPBACK_HOSTS:
        return
    if str(os.getenv("ALLOW_PUBLIC_BIND", "")).strip().lower() in ("1", "true", "yes"):
        print(
            f"[masterdataservices] WARNING: binding "
            f"{host}:{os.getenv('SERVICE_PORT', '?')} because "
            f"ALLOW_PUBLIC_BIND is set. This service is meant to be reached only "
            f"through the login gateway; a public bind lets a caller address it "
            f"directly and bypass the gateway's permission map entirely.",
            file=sys.stderr,
        )
        return
    raise RuntimeError(
        f"MasterDataServices would bind {host}, which is reachable from outside this "
        f"machine. Only the login gateway is meant to be externally reachable: "
        f"the other five services are addressed through it, and the permission "
        f"map that authorises them is applied there. A service on a public "
        f"address can be called directly, skipping that map entirely.\n"
        f"  Set SERVICE_HOST=127.0.0.1 in "
        f"Backend/Services/MasterDataServices/.env, or start it with start-network.ps1 / "
        f"run.sh, which bind loopback by default.\n"
        f"  If a public bind is genuinely intended, set ALLOW_PUBLIC_BIND=true "
        f"and make sure you have accepted that the gateway is not the only "
        f"thing authorising this service."
    )


_assert_private_bind()
from configs.base_config import BaseConfig
from resources.route_policy import RoutePermissionMiddleware
from routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("masterdataservice")

# Interactive API docs publish the complete endpoint surface. They are
# useful in development and must not be reachable in production, least of
# all on the internet-facing gateway.
_DOCS = None if BaseConfig.IS_PRODUCTION else "/docs"
_REDOC = None if BaseConfig.IS_PRODUCTION else "/redoc"
_OPENAPI = None if BaseConfig.IS_PRODUCTION else "/openapi.json"

app = FastAPI(
    title="HotelERP - Master Data Service",
    version="1.1.0",
    docs_url=_DOCS,
    redoc_url=_REDOC,
    openapi_url=_OPENAPI,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=BaseConfig.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-Id"],
    max_age=600,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=BaseConfig.SESSION_SECRET,
    session_cookie="hotelerp_master_session",
    same_site="lax",
    https_only=BaseConfig.IS_PRODUCTION,
    max_age=BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
)


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


# The gateway's permission map, applied again here -- the second,
# independent authorisation layer. `audit` by default, so this changes
# no behaviour on deploy and logs what it would have refused; set
# ROUTE_POLICY_MODE=enforce after the log has been read.
app.add_middleware(RoutePermissionMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Static uploads live under templates/static.
#
# The mount used to be guarded by `if os.path.isdir(...)`, evaluated once at
# import. The directory is created by the upload handler, so a service that
# started before the first upload had no mount for the rest of its life and
# answered 404 for every stored file until someone restarted it -- which is
# exactly what a long-running production process does. Creating the directory
# here and mounting unconditionally removes the ordering dependency: the mount
# always exists, and an empty directory simply serves nothing.
os.makedirs("templates/static", exist_ok=True)
app.mount("/templates/static", StaticFiles(directory="templates/static"), name="static")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", extra={"path": str(request.url.path)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def root_api():
    return RedirectResponse("../login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness probe. Returns 503 while the database is unreachable."""
    from sqlalchemy import text
    from models import get_db

    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        return {"status": "ready", "checks": {"database": {"ok": True, "detail": "connected"}}}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "degraded": ["database"],
                "checks": {"database": {"ok": False, "detail": str(exc)}},
            },
        )


app.include_router(router, prefix="")

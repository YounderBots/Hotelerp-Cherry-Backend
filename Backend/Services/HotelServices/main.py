import logging
import os

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

if _configs.SERVICE_NAME != "HotelServices":
    raise RuntimeError(
        f"HotelServices loaded {_configs.SERVICE_NAME}'s configs package. Start "
        f"this service with its own directory as the working directory "
        f"(run.sh does that), and keep sibling service directories off "
        f"sys.path."
    )


from configs.base_config import BaseConfig
from routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("hotelservice")

# Interactive API docs publish the complete endpoint surface. They are
# useful in development and must not be reachable in production, least of
# all on the internet-facing gateway.
_DOCS = None if BaseConfig.IS_PRODUCTION else "/docs"
_REDOC = None if BaseConfig.IS_PRODUCTION else "/redoc"
_OPENAPI = None if BaseConfig.IS_PRODUCTION else "/openapi.json"

app = FastAPI(
    title="HotelERP - Hotel Service",
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
    session_cookie="hotelerp_hotel_session",
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
    # The controllers catch their own exceptions and go through the same
    # helper; this is the net under everything else. It answers what the
    # helper answers: a sibling service being down is a 503 that names it,
    # anything else is a plain 500 with the cause in the log.
    from resources.utils import server_error

    err = server_error(logger, exc, "unhandled_exception")
    return JSONResponse(status_code=err.status_code, content={"detail": err.detail})


@app.get("/")
def root_api():
    return RedirectResponse("../login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


def _dependency_checks() -> dict:
    """Every dependency this service cannot do its job without.

    Two sibling services, reported separately because they fail separately
    and break different screens: without Master Data the whole reservation
    module is down, while without Users only assigning a housekeeping task
    is. Both are reached over HTTP on the caller's behalf; this service's
    own database account never leaves its own schema, so there is no
    cross-schema privilege left to probe.
    """
    from resources.master_client import probe

    md_ok, md_detail = probe(
        "Master Data", BaseConfig.MASTER_SERVICE_URL, "MASTER_SERVICE_URL",
        "Every reservation screen answers 503 until it is.",
    )
    users_ok, users_detail = probe(
        "Users", BaseConfig.USER_SERVICE_URL, "USER_SERVICE_URL",
        "Assigning a housekeeping task cannot check its assignee until it is.",
    )
    return {
        "masterdata": {"ok": md_ok, "detail": md_detail},
        "users": {"ok": users_ok, "detail": users_detail},
    }


# Liveness. Stays 200 whenever the process is serving, so a dependency being
# down does not send a supervisor into a restart loop over something restarting
# cannot fix.
#
# It no longer answers a flat "ok" though. It used to, unconditionally, which
# is how a deployment whose reservation module was answering 500 on every
# request looked perfectly healthy: the list, the detail and the availability
# check were down, and the only thing that said so was a 500 the operator had
# to go looking for.
@app.get("/healthz")
def healthz():
    checks = _dependency_checks()
    degraded = [name for name, c in checks.items() if not c["ok"]]
    if degraded:
        logger.error("healthz_degraded failing=%s detail=%s",
                     degraded, checks[degraded[0]]["detail"])
    return {
        "status": "degraded" if degraded else "ok",
        "degraded": degraded,
        "checks": checks,
    }


# Readiness. 503 while a required dependency is unreachable, so a probe that
# gates traffic can actually tell the difference -- which /healthz deliberately
# will not, being a liveness check.
@app.get("/readyz")
def readyz():
    checks = _dependency_checks()
    degraded = [name for name, c in checks.items() if not c["ok"]]
    body = {"status": "degraded" if degraded else "ready",
            "degraded": degraded, "checks": checks}
    return JSONResponse(status_code=503 if degraded else 200, content=body)


@app.on_event("startup")
def _check_dependencies_on_boot():
    """Say it once, loudly, at boot rather than 500 per request afterwards.

    This service reads Master Data and Users over HTTP. A deployment whose
    MASTER_SERVICE_URL or USER_SERVICE_URL points nowhere used to start
    cleanly and break only the reservation module, one 500 at a time; now the
    boot log names the URL that does not answer.
    """
    for name, c in _dependency_checks().items():
        if c["ok"]:
            logger.info("dependency_ok name=%s detail=%s", name, c["detail"])
        else:
            # The detail names the consequence itself -- which screens go down
            # differs per check, so stating one fixed sentence here would be
            # wrong for the other.
            logger.critical("DEPENDENCY UNAVAILABLE name=%s -- %s",
                            name, c["detail"])


app.include_router(router, prefix="")

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

if _configs.SERVICE_NAME != "MasterDataServices":
    raise RuntimeError(
        f"MasterDataServices loaded {_configs.SERVICE_NAME}'s configs package. Start "
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


app.include_router(router, prefix="")

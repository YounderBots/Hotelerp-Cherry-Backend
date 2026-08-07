import os

from datetime import datetime
import datetime as dt


class BaseConfig(object):
    _ENV = os.getenv("ASCEND_ENV", "dev").lower()
    _IS_PROD = _ENV in ("prod", "production")
    SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        None if _IS_PROD else "dev-only-do-not-use-in-prod",
    )
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY must be set in production")
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))

    # Must match the `iss` claim the login gateway mints, otherwise every
    # token this service receives is rejected.
    JWT_ISSUER = os.getenv("JWT_ISSUER", "hotelerp-login")

    IS_PRODUCTION = _IS_PROD
    ENVIRONMENT = _ENV

    SESSION_SECRET = os.getenv(
        "SESSION_SECRET",
        None if _IS_PROD else "dev-only-session-secret",
    )
    if not SESSION_SECRET:
        raise RuntimeError("SESSION_SECRET must be set in production")

    _raw_origins = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    CORS_ALLOWED_ORIGINS = [
        o.strip() for o in _raw_origins.split(",") if o.strip() and o.strip() != "*"
    ]


# ------- Common Using Names -------#
class CommonWords():
    STATUS = 'ACTIVE'
    UNSTATUS = 'INACTIVE'
    CURRENTDATE = dt.datetime.today().strftime('%Y-%m-%d')
    Today_DateFormated = dt.datetime.today().strftime('%d %b %Y')
    CURRENTTIME = dt.datetime.today().strftime('%H:%M')
    CURRENTDATETIME = dt.datetime.today()


class ServiceURL:
    # Base URLs come from .env so cross-service calls follow the same host/port
    # configuration as everything else; loopback defaults keep local dev working.
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8020")
    MASTER_SERVICE_URL = os.getenv("MASTER_SERVICE_URL", "http://127.0.0.1:8030")
    HOTEL_SERVICE_URL = os.getenv("HOTEL_SERVICE_URL", "http://127.0.0.1:8040")
    RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://127.0.0.1:8050")
    BAR_SERVICE_URL = os.getenv("BAR_SERVICE_URL", "http://127.0.0.1:8060")

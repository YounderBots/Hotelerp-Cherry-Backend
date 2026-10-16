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

    UPLOAD_MAX_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", str(5 * 1024 * 1024)))
    UPLOAD_ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# ------- Common Using Names -------#
class CommonWords():
        # DELIBERATELY NO DATE CONSTANT HERE.
        #
        # There used to be four on this class -- CURRENTDATE, Today_DateFormated,
        # CURRENTTIME, CURRENTDATETIME -- all written as `dt.datetime.today()...` in
        # the class body. A class-body expression is evaluated once, when this module
        # is imported, and then frozen for the life of the process: a service running
        # across midnight reported yesterday's date until it was restarted.
        #
        # Nothing read them, so nothing ever broke, which is precisely why they were
        # dangerous -- the failure mode was invisible until the one night the service
        # was not restarted. In a system with a `business_date` and a night audit
        # that closes on it, a date helper that silently stops being the date is not
        # worth keeping around.
        #
        # If you want the date, ask for it where you use it:
        #
        #     import datetime as dt
        #     today = dt.date.today()          # or dt.datetime.now()
        #
        # A value captured at import is the bug, whichever name it is filed under.
    STATUS = 'ACTIVE'
    UNSTATUS = 'INACTIVE'

class ServiceURL:
    # Base URLs come from .env so cross-service calls follow the same host/port
    # configuration as everything else; loopback defaults keep local dev working.
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8020")
    MASTER_SERVICE_URL = os.getenv("MASTER_SERVICE_URL", "http://127.0.0.1:8030")
    HOTEL_SERVICE_URL = os.getenv("HOTEL_SERVICE_URL", "http://127.0.0.1:8040")
    RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://127.0.0.1:8050")
    BAR_SERVICE_URL = os.getenv("BAR_SERVICE_URL", "http://127.0.0.1:8060")

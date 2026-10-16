import datetime as dt
import os

class BaseConfig:
    # Secrets are ALWAYS resolved from the environment. A dev-only fallback is
    # allowed via SECRET_KEY / SESSION_SECRET, but production deploys must set
    # them explicitly or startup will fail (see `_require_env`).
    ENVIRONMENT = os.getenv("ASCEND_ENV", "dev")
    IS_PRODUCTION = ENVIRONMENT.lower() in ("prod", "production")

    SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        None if IS_PRODUCTION else "dev-only-do-not-use-in-prod",
    )
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY must be set in production")

    SESSION_SECRET = os.getenv(
        "SESSION_SECRET",
        None if IS_PRODUCTION else "dev-only-session-secret",
    )
    if not SESSION_SECRET:
        raise RuntimeError("SESSION_SECRET must be set in production")

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))

    JWT_ISSUER = os.getenv("JWT_ISSUER", "hotelerp-login")

    # CORS allow-list. Comma-separated origins; wildcard forbidden.
    _raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip() and o.strip() != "*"]

    # Login brute-force guard
    LOGIN_RATE_LIMIT_PER_MINUTE = int(os.getenv("LOGIN_RATE_LIMIT_PER_MINUTE", "10"))
    LOGIN_RATE_LIMIT_BURST = int(os.getenv("LOGIN_RATE_LIMIT_BURST", "3"))

    # Proxy timeouts
    PROXY_TIMEOUT_SECONDS = float(os.getenv("PROXY_TIMEOUT_SECONDS", "30"))
    UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "10"))

class CommonWords:
    STATUS = "ACTIVE"
    UNSTATUS = "INACTIVE"
    AVAILABLE = "Available"
    RESERVED = "RESERVED"
    Room_Status = "Available"
    Room_Condition = "UnBlocking"
    WORK_STATUS = "Not Assigne"
    HouseKeeper_RoleID = "5"
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
    Reser_Type_Reservation = "Reservation"
    Reser_Type_GroupReservation = "Group Reservation"
    LOGINER_URL = "../login"
    Checkout_List = "../checkout_list"
    Confirmed = "Confirmed"
    Arrived = "Arrived"
    Departures = "Departures"
    Cancelled = "Cancelled"

class ServiceURL:
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8020")
    MASTER_SERVICE_URL = os.getenv("MASTER_SERVICE_URL", "http://127.0.0.1:8030")
    HOTEL_SERVICE_URL = os.getenv("HOTEL_SERVICE_URL", "http://127.0.0.1:8040")
    RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://127.0.0.1:8050")
    BAR_SERVICE_URL = os.getenv("BAR_SERVICE_URL", "http://127.0.0.1:8060")

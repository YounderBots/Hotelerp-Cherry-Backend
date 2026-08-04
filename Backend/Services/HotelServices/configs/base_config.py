import os

from datetime import datetime
import datetime  as dt


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

    IS_PRODUCTION = _IS_PROD
    ENVIRONMENT = _ENV

    # Must match the `iss` claim the login gateway mints, otherwise every
    # token this service receives is rejected.
    JWT_ISSUER = os.getenv("JWT_ISSUER", "hotelerp-login")

    SESSION_SECRET = os.getenv(
        "SESSION_SECRET",
        None if _IS_PROD else "dev-only-session-secret",
    )
    if not SESSION_SECRET:
        raise RuntimeError("SESSION_SECRET must be set in production")

    # CORS allow-list. Comma-separated origins; wildcard is stripped because
    # `allow_credentials=True` with `*` is both invalid and unsafe.
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
    AVAILABLE = 'Available'
    RESERVED = 'RESERVED'
    Room_Status = "Available"
    Room_Condition = "UnBlocking"
    WORK_STATUS = 'Not Assigne'
    HouseKeeper_RoleID = "5"
    CURRENTDATE = dt.datetime.today().strftime('%Y-%m-%d')
    Today_DateFormated = dt.datetime.today().strftime('%d %b %Y')
    Reser_Type_Reservation = "Reservation"
    Reser_Type_GroupReservation = "Group Reservation"
    CURRENTTIME = dt.datetime.today().strftime('%H:%M')
    CURRENTDATETIME = dt.datetime.today()
    LOGINER_URL = '../login'
    Checkout_List = '../checkout_list'
    Confirmed = "Confirmed"
    Arrived = "Arrived"
    Departures = "Departures"
    Cancelled = "Cancelled"
  
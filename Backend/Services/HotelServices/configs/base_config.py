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
  
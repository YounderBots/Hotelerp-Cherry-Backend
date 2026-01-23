import os

from datetime import datetime
import datetime  as dt


class BaseConfig(object):
    SECRET_KEY = '691a03c2f0a7a449a00a394ca9deca08a3c4602f0995d8376bc60884c184c991'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440
    REFRESH_TOKEN_EXPIRE_MINUTES = 45
    
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

class ServiceURL:

    # ================= USER / AUTH =================
    USER_SERVICE_URL = "http://127.0.0.1:8020"

    # ================= MASTER DATA =================
    MASTER_SERVICE_URL = "http://127.0.0.1:8003"

    # ================= HOTEL =================
    HOTEL_SERVICE_URL = "http://127.0.0.1:8004"

    # ================= RESTAURANT =================
    RESTAURANT_SERVICE_URL = "http://127.0.0.1:8005"

    # ================= BAR =================
    BAR_SERVICE_URL = "http://127.0.0.1:8006"
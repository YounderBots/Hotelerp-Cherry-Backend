import os

from configs.base_config import BaseConfig
class Configuration(BaseConfig):
    DEBUG = True
    # Derived from the shared DB_URL_BASE in .env (single source for host+creds);
    # an explicit DB_URI still wins, then a localhost dev fallback.
    DB_URI = os.getenv("DB_URI") or (
        f"{os.getenv('DB_URL_BASE')}/hotelerp_restaurant"
        if os.getenv("DB_URL_BASE")
        else "mysql+pymysql://root@localhost/hotelerp_restaurant"
    )
  
   
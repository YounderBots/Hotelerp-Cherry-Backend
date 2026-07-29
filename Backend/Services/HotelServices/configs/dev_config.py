import os

from configs.base_config import BaseConfig
class Configuration(BaseConfig):
    DEBUG = True
    DB_URI = os.getenv(
        "DB_URI",
        "mysql+pymysql://root@localhost/hotelerp_hotel",
    )
  
   
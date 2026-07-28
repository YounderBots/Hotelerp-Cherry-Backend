import os

from configs.base_config import BaseConfig


class Configuration(BaseConfig):
    DEBUG = True
    DB_URI = os.getenv(
        "DB_URI",
        # Local developer fallback only. Production must set DB_URI explicitly.
        "mysql+pymysql://root@localhost/hotelerp_users",
    )

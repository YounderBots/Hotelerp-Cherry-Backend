import os

from configs.base_config import BaseConfig


class Configuration(BaseConfig):
    DEBUG = True
    DB_URI = os.getenv(
        "DB_URI",
        # Local developer fallback only. Production must set DB_URI explicitly.
        "mysql+pymysql://hotelerp_app:CHANGE_ME@localhost/hotelerp_users",
    )

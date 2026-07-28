import os

from configs.base_config import BaseConfig


class Configuration(BaseConfig):
    DEBUG = True
    DB_URI = os.getenv(
        "DB_URI",
        "mysql+pymysql://hotelerp_app:CHANGE_ME@localhost/hotelerp_users",
    )

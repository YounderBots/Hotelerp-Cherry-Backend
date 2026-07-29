from configs.base_config import BaseConfig

class Configuration(BaseConfig):
    DEBUG = True
    DB_URI = 'mysql+pymysql://root@localhost/hotelerp_restaurant'

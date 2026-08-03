import os

from configs.base_config import BaseConfig


class Configuration(BaseConfig):
    """Production settings. Every secret is env-driven; nothing is defaulted.

    Startup fails loudly here rather than silently connecting a production
    service to a developer database.
    """

    DEBUG = False

    DB_URI = os.getenv("DB_URI")
    if not DB_URI:
        raise RuntimeError(
            "DB_URI must be set in production "
            "(expected a DSN for the users database)"
        )

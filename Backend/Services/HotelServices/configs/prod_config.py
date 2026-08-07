import os

from configs.base_config import BaseConfig


class Configuration(BaseConfig):
    """Production settings. Every secret is env-driven; nothing is defaulted.

    Startup fails loudly here rather than silently connecting a production
    service to a developer database.
    """

    DEBUG = False

    # Prefer an explicit DB_URI; otherwise derive from the shared DB_URL_BASE.
    DB_URI = os.getenv("DB_URI") or (
        f"{os.getenv('DB_URL_BASE')}/hotelerp_hotel" if os.getenv("DB_URL_BASE") else None
    )
    if not DB_URI:
        raise RuntimeError(
            "DB_URI must be set in production "
            "(expected a DSN for the hotel database)"
        )

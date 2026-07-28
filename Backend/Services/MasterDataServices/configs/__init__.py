import os

from .base_config import BaseConfig

env = os.getenv("ASCEND_ENV", "dev").lower()

if env == "local":
    from .local_config import Configuration  # noqa: F401
elif env in ("prod", "production"):
    from .prod_config import Configuration  # type: ignore  # noqa: F401
else:
    from .dev_config import Configuration  # noqa: F401

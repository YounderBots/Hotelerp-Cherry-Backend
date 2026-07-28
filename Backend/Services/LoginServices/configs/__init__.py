import os

from .base_config import BaseConfig

env = os.getenv("ASCEND_ENV", "dev").lower()

if env == "local":
    from .local_config import Configuration
elif env in ("prod", "production"):
    # Production config must exist; import lazily so a missing file is loud.
    from .prod_config import Configuration  # type: ignore  # noqa: F401
else:
    from .dev_config import Configuration  # noqa: F401

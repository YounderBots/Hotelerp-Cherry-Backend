import os
from pathlib import Path

from dotenv import load_dotenv

# Each service is self-contained: it loads ONLY its own .env (which sits next to
# main.py in the service directory). Variables already present in the environment
# are NOT overridden, so an explicit override at launch still wins.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .base_config import BaseConfig  # noqa: E402,F401

env = os.getenv("ASCEND_ENV", "dev").lower()

if env == "local":
    from .local_config import Configuration  # noqa: F401
elif env in ("prod", "production"):
    from .prod_config import Configuration  # noqa: F401
else:
    from .dev_config import Configuration  # noqa: F401

# ---------------------------------------------------------------------------
# Which service this configs package belongs to.
#
# Every service ships a package with this same name, and Python caches modules
# by NAME rather than by path: in a process where two service directories are
# on sys.path, the first `configs` imported serves them both. main.py asserts
# against this so a service handed a sibling's configuration fails at startup
# saying so, rather than reading the wrong DB_URI in silence.
# ---------------------------------------------------------------------------
SERVICE_NAME = Path(__file__).resolve().parents[1].name

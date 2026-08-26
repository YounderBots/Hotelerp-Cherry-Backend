"""Shared Alembic environment, run once per database.

Each service is its own top-level package root -- `configs`, `models` and
`resources` are imported absolutely, and all six services define a module named
`configs`. They therefore cannot be imported into one process, which rules out
Alembic's multi-database template. Instead this single env.py is run once per
database with cwd set to the owning service directory, exactly like the test
suites in Backend/tests/run_all.py.

`migrate.py` sets that cwd and passes the owning service in as `-x service=...`.
Do not invoke alembic directly against this file.
"""
from __future__ import annotations

import os
import pathlib
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

service = context.get_x_argument(as_dictionary=True).get("service")
if not service:
    raise SystemExit(
        "env.py must be invoked through Backend/migrations/migrate.py, which "
        "supplies -x service=<OwningService> and the matching cwd."
    )

# cwd is the owning service directory; put it first so `configs` / `models`
# resolve to THAT service and not to whichever one is earliest on sys.path.
sys.path.insert(0, str(pathlib.Path.cwd()))

# Never let a migration run trigger create_all -- that is the very behaviour
# Alembic is here to replace.
os.environ.setdefault("DB_AUTO_CREATE", "false")

from configs import Configuration  # noqa: E402
import models.models as service_models  # noqa: E402

target_metadata = service_models.Base.metadata

# The URL comes from the service's own .env (loaded by configs/__init__.py), so
# there is one source of truth for it and no credential lands in alembic.ini.
config.set_main_option("sqlalchemy.url", Configuration.DB_URI.replace("%", "%%"))


def include_object(obj, name, type_, reflected, compare_to):
    """Keep Alembic's own bookkeeping table out of autogenerate."""
    if type_ == "table" and name == "alembic_version":
        return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

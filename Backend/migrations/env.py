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
    # The `active_*` generated columns -- and the `uq_*` unique indexes over
    # them -- exist ONLY in the database. The models deliberately do not
    # declare them: see the C-082 note at the top of each service's
    # models/models.py. Autogenerating a revision while they are visible would
    # emit DROP COLUMN / DROP INDEX operations that destroy the very
    # invariants the schema is enforcing (active names are unique per company,
    # soft-deleted history may repeat). Nothing may ever drop them, so they are
    # not part of the comparison at all.
    if reflected and compare_to is None:
        if type_ == "column" and name.startswith("active_"):
            return False
        if type_ == "index" and "active_" in name:
            return False
    return True


def _now_like(text) -> bool:
    """Is this rendered server default some spelling of "the current time"?

    The rendered forms are strings: the hand-built schemas store
    `DEFAULT now()` (or `CURRENT_TIMESTAMP`) as text, the models render
    `func.now()` as `CURRENT_TIMESTAMP`. All of them are the same rule.
    """
    if text is None:
        return False
    return "now()" in text.lower() or "current_timestamp" in text.lower()


def compare_server_default(migration_context, inspected_column, metadata_column,
                           rendered_inspected_default, metadata_default,
                           rendered_metadata_default):
    """Do NOT report a difference between two spellings of now().

    With `compare_server_default=True`, Alembic reported 120 phantom
    `modify_default` operations across the five databases -- every
    `created_at` in every schema -- because the database spells the default
    `now()` and the model spells it `func.now()`. That noise is what hid the
    one real drift (a column type and two index mismatches) inside a wall of
    120 false positives, and it meant `migrate.py check` could never pass.

    Returning False means "these are the same"; returning None defers to
    Alembic's own dialect comparison, so a genuinely different default is
    still reported.
    """
    if (_now_like(rendered_inspected_default)
            and _now_like(rendered_metadata_default)):
        return False
    return None


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=compare_server_default,
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
            compare_server_default=compare_server_default,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""remove the legacy global roles.role_name unique index

Revision ID: a1f6d8c2b44e
Revises: 9e4b7c1d3a22
Create Date: 2026-09-25

The hand-built users schema has a global unique index on ``role_name``.  It
blocks recreating a role after its soft delete, even though the intended
invariant is uniqueness among active names within a company.  The active-name
index added by the preceding revision is the replacement.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1f6d8c2b44e"
down_revision: Union[str, None] = "9e4b7c1d3a22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE roles DROP INDEX ix_roles_role_name")


def downgrade() -> None:
    op.execute("ALTER TABLE roles ADD UNIQUE INDEX ix_roles_role_name (role_name)")

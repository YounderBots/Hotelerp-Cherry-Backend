"""enforce one active role name per company

Revision ID: 9e4b7c1d3a22
Revises: 8d3a4b6c2e11
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "9e4b7c1d3a22"
down_revision: Union[str, None] = "8d3a4b6c2e11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE roles "
        "ADD COLUMN active_role_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN role_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_roles_active_company_name",
        "roles",
        ["company_id", "active_role_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_roles_active_company_name", table_name="roles")
    op.drop_column("roles", "active_role_name")

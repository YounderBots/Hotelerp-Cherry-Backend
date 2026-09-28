"""enforce one active designation name per company

Revision ID: 8d3a4b6c2e11
Revises: 7c2f1a9d4e10
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "8d3a4b6c2e11"
down_revision: Union[str, None] = "7c2f1a9d4e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE designation "
        "ADD COLUMN active_designation_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN Designation_Name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_designation_active_company_name",
        "designation",
        ["company_id", "active_designation_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_designation_active_company_name", table_name="designation")
    op.drop_column("designation", "active_designation_name")

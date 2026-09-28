"""enforce case-insensitive active hall/floor names per company

Revision ID: b6f7a8b9c0d1
Revises: b5e6f7a8b9c0
Create Date: 2026-09-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b6f7a8b9c0d1"
down_revision: Union[str, None] = "b5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE table_hall_names "
        "ADD COLUMN active_hall_name VARCHAR(255) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(hall_name) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_table_hall_active_name",
        "table_hall_names",
        ["company_id", "active_hall_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_table_hall_active_name", table_name="table_hall_names")
    op.drop_column("table_hall_names", "active_hall_name")

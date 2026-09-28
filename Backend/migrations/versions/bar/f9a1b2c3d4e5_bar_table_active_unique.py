"""enforce active bar table number and name uniqueness per floor

Revision ID: f9a1b2c3d4e5
Revises: e8f0a1b2c3d4
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f9a1b2c3d4e5"
down_revision: Union[str, None] = "e8f0a1b2c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bar_table "
        "ADD COLUMN active_table_number INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN table_number ELSE NULL END) STORED"
    )
    op.execute(
        "ALTER TABLE bar_table "
        "ADD COLUMN active_table_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN table_name ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_table_active_number", "bar_table", ["company_id", "floor_id", "active_table_number"], unique=True)
    op.create_index("uq_bar_table_active_name", "bar_table", ["company_id", "floor_id", "active_table_name"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_bar_table_active_name", table_name="bar_table")
    op.drop_index("uq_bar_table_active_number", table_name="bar_table")
    op.drop_column("bar_table", "active_table_name")
    op.drop_column("bar_table", "active_table_number")

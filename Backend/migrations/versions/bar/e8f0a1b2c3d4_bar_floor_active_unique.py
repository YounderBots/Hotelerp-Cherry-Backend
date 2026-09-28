"""enforce active bar floor number and name uniqueness

Revision ID: e8f0a1b2c3d4
Revises: d7e9f0a1b2c3
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "e8f0a1b2c3d4"
down_revision: Union[str, None] = "d7e9f0a1b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bar_floor "
        "ADD COLUMN active_floor_number INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN floor_number ELSE NULL END) STORED"
    )
    op.execute(
        "ALTER TABLE bar_floor "
        "ADD COLUMN active_floor_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN floor_name ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_floor_active_number", "bar_floor", ["company_id", "active_floor_number"], unique=True)
    op.create_index("uq_bar_floor_active_name", "bar_floor", ["company_id", "active_floor_name"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_bar_floor_active_name", table_name="bar_floor")
    op.drop_index("uq_bar_floor_active_number", table_name="bar_floor")
    op.drop_column("bar_floor", "active_floor_name")
    op.drop_column("bar_floor", "active_floor_number")

"""enforce active restaurant table number/name uniqueness per floor

Revision ID: e9a2b3c4d5e6
Revises: d8f1a2b3c4d5
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "e9a2b3c4d5e6"
down_revision: Union[str, None] = "d8f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE restaurant_table "
        "ADD COLUMN active_table_number INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN table_number ELSE NULL END) STORED"
    )
    op.execute(
        "ALTER TABLE restaurant_table "
        "ADD COLUMN active_table_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN table_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_table_active_number",
        "restaurant_table",
        ["company_id", "branch_id", "floor_id", "active_table_number"],
        unique=True,
    )
    op.create_index(
        "uq_restaurant_table_active_name",
        "restaurant_table",
        ["company_id", "branch_id", "floor_id", "active_table_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_table_active_name", table_name="restaurant_table")
    op.drop_index("uq_restaurant_table_active_number", table_name="restaurant_table")
    op.drop_column("restaurant_table", "active_table_name")
    op.drop_column("restaurant_table", "active_table_number")

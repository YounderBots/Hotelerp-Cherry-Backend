"""enforce active restaurant floor number/name uniqueness per company branch

Revision ID: d8f1a2b3c4d5
Revises: c6d8e9f0a1b2
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "d8f1a2b3c4d5"
down_revision: Union[str, None] = "c6d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE restaurant_floor "
        "ADD COLUMN active_floor_number INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN floor_number ELSE NULL END) STORED"
    )
    op.execute(
        "ALTER TABLE restaurant_floor "
        "ADD COLUMN active_floor_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN floor_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_floor_active_number",
        "restaurant_floor",
        ["company_id", "branch_id", "active_floor_number"],
        unique=True,
    )
    op.create_index(
        "uq_restaurant_floor_active_name",
        "restaurant_floor",
        ["company_id", "branch_id", "active_floor_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_floor_active_name", table_name="restaurant_floor")
    op.drop_index("uq_restaurant_floor_active_number", table_name="restaurant_floor")
    op.drop_column("restaurant_floor", "active_floor_name")
    op.drop_column("restaurant_floor", "active_floor_number")

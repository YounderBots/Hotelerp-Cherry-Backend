"""enforce active restaurant inventory item name uniqueness

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE inventory_item "
        "ADD COLUMN active_item_name VARCHAR(150) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN item_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_inventory_active_name",
        "inventory_item",
        ["company_id", "branch_id", "active_item_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_inventory_active_name", table_name="inventory_item")
    op.drop_column("inventory_item", "active_item_name")

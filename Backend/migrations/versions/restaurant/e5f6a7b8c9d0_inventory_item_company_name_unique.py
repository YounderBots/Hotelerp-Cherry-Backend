"""scope active inventory item names to the company, not a legacy branch id

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("uq_restaurant_inventory_active_name", table_name="inventory_item")
    op.create_index(
        "uq_restaurant_inventory_active_name",
        "inventory_item",
        ["company_id", "active_item_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_inventory_active_name", table_name="inventory_item")
    op.create_index(
        "uq_restaurant_inventory_active_name",
        "inventory_item",
        ["company_id", "branch_id", "active_item_name"],
        unique=True,
    )

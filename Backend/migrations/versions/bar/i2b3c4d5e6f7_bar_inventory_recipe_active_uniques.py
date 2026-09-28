"""enforce active bar inventory names and recipe line uniqueness

Revision ID: i2b3c4d5e6f7
Revises: h1a2b3c4d5e6
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "i2b3c4d5e6f7"
down_revision: Union[str, None] = "h1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bar_inventory_item "
        "ADD COLUMN active_item_name VARCHAR(150) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN item_name ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_inventory_active_name", "bar_inventory_item", ["company_id", "active_item_name"], unique=True)
    op.drop_index("uq_bar_recipe_line", table_name="bar_recipe")
    op.execute(
        "ALTER TABLE bar_recipe "
        "ADD COLUMN active_inventory_item_id INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN inventory_item_id ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_recipe_active_line", "bar_recipe", ["menu_id", "active_inventory_item_id"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_bar_recipe_active_line", table_name="bar_recipe")
    op.drop_column("bar_recipe", "active_inventory_item_id")
    op.create_index("uq_bar_recipe_line", "bar_recipe", ["menu_id", "inventory_item_id"], unique=True)
    op.drop_index("uq_bar_inventory_active_name", table_name="bar_inventory_item")
    op.drop_column("bar_inventory_item", "active_item_name")

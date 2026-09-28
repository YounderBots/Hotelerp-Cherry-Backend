"""allow recipe replacement while keeping active lines unique

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("uq_menu_recipe_line", table_name="menu_recipe")
    op.execute(
        "ALTER TABLE menu_recipe "
        "ADD COLUMN active_inventory_item_id INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN inventory_item_id ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_menu_recipe_active_line",
        "menu_recipe",
        ["menu_id", "active_inventory_item_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_menu_recipe_active_line", table_name="menu_recipe")
    op.drop_column("menu_recipe", "active_inventory_item_id")
    op.create_index(
        "uq_menu_recipe_line",
        "menu_recipe",
        ["menu_id", "inventory_item_id"],
        unique=True,
    )

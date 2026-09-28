"""enforce active menu, variant, and modifier name uniqueness

Revision ID: a1b2c3d4e5f6
Revises: f0b1c2d3e4f5
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f0b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE restaurant_menu "
        "ADD COLUMN active_menu_name VARCHAR(150) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN item_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_menu_active_name",
        "restaurant_menu",
        ["company_id", "branch_id", "category_id", "active_menu_name"],
        unique=True,
    )

    op.drop_index("uq_menu_variant_name", table_name="menu_variant")
    op.execute(
        "ALTER TABLE menu_variant "
        "ADD COLUMN active_variant_name VARCHAR(50) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN variant_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_menu_variant_active_name",
        "menu_variant",
        ["menu_id", "active_variant_name"],
        unique=True,
    )

    op.execute(
        "ALTER TABLE menu_modifier "
        "ADD COLUMN active_modifier_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN modifier_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_menu_modifier_active_name",
        "menu_modifier",
        ["menu_id", "active_modifier_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_menu_modifier_active_name", table_name="menu_modifier")
    op.drop_column("menu_modifier", "active_modifier_name")
    op.drop_index("uq_menu_variant_active_name", table_name="menu_variant")
    op.drop_column("menu_variant", "active_variant_name")
    op.create_index("uq_menu_variant_name", "menu_variant", ["menu_id", "variant_name"], unique=True)
    op.drop_index("uq_restaurant_menu_active_name", table_name="restaurant_menu")
    op.drop_column("restaurant_menu", "active_menu_name")

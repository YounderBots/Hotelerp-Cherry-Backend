"""enforce active bar menu, variant, and modifier name uniqueness

Revision ID: h1a2b3c4d5e6
Revises: g0b1c2d3e4f5
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "h1a2b3c4d5e6"
down_revision: Union[str, None] = "g0b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bar_menu_item "
        "ADD COLUMN active_item_name VARCHAR(150) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN item_name ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_menu_active_name", "bar_menu_item", ["company_id", "category_id", "active_item_name"], unique=True)
    op.drop_index("uq_bar_menu_variant_name", table_name="bar_menu_variant")
    op.execute(
        "ALTER TABLE bar_menu_variant "
        "ADD COLUMN active_variant_name VARCHAR(50) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN variant_name ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_variant_active_name", "bar_menu_variant", ["menu_id", "active_variant_name"], unique=True)
    op.execute(
        "ALTER TABLE bar_menu_modifier "
        "ADD COLUMN active_modifier_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN modifier_name ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_modifier_active_name", "bar_menu_modifier", ["menu_id", "active_modifier_name"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_bar_modifier_active_name", table_name="bar_menu_modifier")
    op.drop_column("bar_menu_modifier", "active_modifier_name")
    op.drop_index("uq_bar_variant_active_name", table_name="bar_menu_variant")
    op.drop_column("bar_menu_variant", "active_variant_name")
    op.create_index("uq_bar_menu_variant_name", "bar_menu_variant", ["menu_id", "variant_name"], unique=True)
    op.drop_index("uq_bar_menu_active_name", table_name="bar_menu_item")
    op.drop_column("bar_menu_item", "active_item_name")

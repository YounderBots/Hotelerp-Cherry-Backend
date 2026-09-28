"""enforce active restaurant combo name uniqueness

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE combo_deal "
        "ADD COLUMN active_combo_name VARCHAR(150) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' AND is_active = 1 "
        "THEN combo_name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_combo_active_name",
        "combo_deal",
        ["company_id", "branch_id", "active_combo_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_combo_active_name", table_name="combo_deal")
    op.drop_column("combo_deal", "active_combo_name")

"""enforce one active order per bar table

Revision ID: g0b1c2d3e4f5
Revises: f9a1b2c3d4e5
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "g0b1c2d3e4f5"
down_revision: Union[str, None] = "f9a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bar_order "
        "ADD COLUMN active_table_id INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "AND order_status NOT IN ('Completed', 'Cancelled') "
        "THEN table_id ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_bar_order_active_table",
        "bar_order",
        ["company_id", "active_table_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_bar_order_active_table", table_name="bar_order")
    op.drop_column("bar_order", "active_table_id")

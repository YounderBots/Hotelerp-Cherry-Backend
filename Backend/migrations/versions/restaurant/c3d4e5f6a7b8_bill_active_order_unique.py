"""enforce one non-cancelled bill per restaurant order

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE restaurant_bill "
        "ADD COLUMN active_order_id INT "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' AND bill_status <> 'Cancelled' "
        "THEN order_id ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_bill_active_order",
        "restaurant_bill",
        ["company_id", "branch_id", "active_order_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_bill_active_order", table_name="restaurant_bill")
    op.drop_column("restaurant_bill", "active_order_id")

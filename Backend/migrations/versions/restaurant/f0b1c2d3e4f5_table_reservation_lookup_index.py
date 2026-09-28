"""index active table reservations for overlap checks

Revision ID: f0b1c2d3e4f5
Revises: e9a2b3c4d5e6
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f0b1c2d3e4f5"
down_revision: Union[str, None] = "e9a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_restaurant_reservation_table_date_status",
        "restaurant_table_reservation",
        ["company_id", "table_id", "reservation_date", "status", "start_time"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_restaurant_reservation_table_date_status",
        table_name="restaurant_table_reservation",
    )

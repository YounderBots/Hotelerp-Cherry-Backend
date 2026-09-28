"""scope active bar guest mobile uniqueness to the company

Revision ID: j3c4d5e6f7a8
Revises: i2b3c4d5e6f7
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "j3c4d5e6f7a8"
down_revision: Union[str, None] = "i2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("uq_bar_guest_mobile", table_name="bar_guest")
    op.execute(
        "ALTER TABLE bar_guest "
        "ADD COLUMN active_mobile VARCHAR(20) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN mobile ELSE NULL END) STORED"
    )
    op.create_index("uq_bar_guest_active_mobile", "bar_guest", ["company_id", "active_mobile"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_bar_guest_active_mobile", table_name="bar_guest")
    op.drop_column("bar_guest", "active_mobile")
    op.create_index("uq_bar_guest_mobile", "bar_guest", ["company_id", "branch_id", "mobile"], unique=True)

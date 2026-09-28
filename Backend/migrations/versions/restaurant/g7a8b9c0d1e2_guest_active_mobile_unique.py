"""scope active guest mobile uniqueness to the company and permit soft-delete recreation

Revision ID: g7a8b9c0d1e2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "g7a8b9c0d1e2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("uq_guest_mobile", table_name="guest")
    op.execute(
        "ALTER TABLE guest "
        "ADD COLUMN active_mobile VARCHAR(20) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN mobile ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_guest_active_mobile",
        "guest",
        ["company_id", "active_mobile"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_restaurant_guest_active_mobile", table_name="guest")
    op.drop_column("guest", "active_mobile")
    op.create_index("uq_guest_mobile", "guest", ["company_id", "branch_id", "mobile"], unique=True)

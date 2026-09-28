"""enforce one active shift name per company

Revision ID: b2c4e6f8a91d
Revises: a1f6d8c2b44e
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2c4e6f8a91d"
down_revision: Union[str, None] = "a1f6d8c2b44e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE shift "
        "ADD COLUMN active_shift_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN Shift_Name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_shift_active_company_name",
        "shift",
        ["company_id", "active_shift_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_shift_active_company_name", table_name="shift")
    op.drop_column("shift", "active_shift_name")

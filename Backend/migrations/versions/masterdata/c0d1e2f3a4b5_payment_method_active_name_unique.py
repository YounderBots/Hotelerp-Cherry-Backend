"""enforce active payment method names per company

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-09-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "c0d1e2f3a4b5"
down_revision: Union[str, None] = "b9c0d1e2f3a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE payment_methods "
        "ADD COLUMN active_payment_method VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(payment_method) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_payment_method_active_name",
        "payment_methods",
        ["company_id", "active_payment_method"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_payment_method_active_name", table_name="payment_methods")
    op.drop_column("payment_methods", "active_payment_method")

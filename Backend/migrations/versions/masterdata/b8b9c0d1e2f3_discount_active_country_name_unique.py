"""enforce active discount names per country and company

Revision ID: b8b9c0d1e2f3
Revises: b7a8b9c0d1e2
Create Date: 2026-09-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b8b9c0d1e2f3"
down_revision: Union[str, None] = "b7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE discount_data "
        "ADD COLUMN active_discount_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Discount_Name) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_discount_active_country_name",
        "discount_data",
        ["company_id", "Country_ID", "active_discount_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_discount_active_country_name", table_name="discount_data")
    op.drop_column("discount_data", "active_discount_name")

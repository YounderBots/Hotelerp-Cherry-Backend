"""enforce active tax names per country and company

Revision ID: b9c0d1e2f3a4
Revises: b8b9c0d1e2f3
Create Date: 2026-09-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b9c0d1e2f3a4"
down_revision: Union[str, None] = "b8b9c0d1e2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE tax_type "
        "ADD COLUMN active_tax_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Tax_Name) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_tax_active_country_name",
        "tax_type",
        ["company_id", "Country_ID", "active_tax_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_tax_active_country_name", table_name="tax_type")
    op.drop_column("tax_type", "active_tax_name")

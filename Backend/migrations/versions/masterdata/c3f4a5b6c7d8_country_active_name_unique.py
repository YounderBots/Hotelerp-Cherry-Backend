"""enforce active country names per company

Revision ID: c3f4a5b6c7d8
Revises: c2e3f4a5b6c7
Create Date: 2026-09-27
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "c3f4a5b6c7d8"
down_revision: Union[str, None] = "c2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {c["name"] for c in inspect(op.get_bind()).get_columns("countries_currency")}
    if "active_country_name" not in columns:
        op.execute(
            "ALTER TABLE countries_currency "
            "ADD COLUMN active_country_name VARCHAR(100) "
            "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Country_Name) ELSE NULL END) STORED"
        )
    indexes = {i["name"] for i in inspect(op.get_bind()).get_indexes("countries_currency")}
    if "uq_country_active_name" not in indexes:
        op.create_index(
            "uq_country_active_name",
            "countries_currency",
            ["company_id", "active_country_name"],
            unique=True,
        )


def downgrade() -> None:
    op.drop_index("uq_country_active_name", table_name="countries_currency")
    op.drop_column("countries_currency", "active_country_name")

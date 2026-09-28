"""enforce case-insensitive active facility names per company

Revision ID: b3c4d5e6f7a8
Revises: a1c4e7f20b91
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, None] = "a1c4e7f20b91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE facility "
        "ADD COLUMN active_facility_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Facility_Name) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_facility_active_name",
        "facility",
        ["company_id", "active_facility_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_facility_active_name", table_name="facility")
    op.drop_column("facility", "active_facility_name")

"""enforce case-insensitive active bed type names per company

Revision ID: b5e6f7a8b9c0
Revises: b4d5e6f7a8b9
Create Date: 2026-09-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b5e6f7a8b9c0"
down_revision: Union[str, None] = "b4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bed_type "
        "ADD COLUMN active_type_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Type_Name) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_bed_type_active_name",
        "bed_type",
        ["company_id", "active_type_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_bed_type_active_name", table_name="bed_type")
    op.drop_column("bed_type", "active_type_name")

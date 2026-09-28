"""enforce case-insensitive active room type names per company

Revision ID: b4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b4d5e6f7a8b9"
down_revision: Union[str, None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE room_type "
        "ADD COLUMN active_type_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Type_Name) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_room_type_active_name",
        "room_type",
        ["company_id", "active_type_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_room_type_active_name", table_name="room_type")
    op.drop_column("room_type", "active_type_name")

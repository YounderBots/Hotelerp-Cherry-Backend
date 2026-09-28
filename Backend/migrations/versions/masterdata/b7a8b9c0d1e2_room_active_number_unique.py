"""enforce active room numbers per company

Revision ID: b7a8b9c0d1e2
Revises: b6f7a8b9c0d1
Create Date: 2026-09-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b7a8b9c0d1e2"
down_revision: Union[str, None] = "b6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE room "
        "ADD COLUMN active_room_no VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN Room_No ELSE NULL END) STORED"
    )
    op.create_index("uq_room_active_no", "room", ["company_id", "active_room_no"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_room_active_no", table_name="room")
    op.drop_column("room", "active_room_no")

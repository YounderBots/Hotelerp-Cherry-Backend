"""enforce active complementary names per company

Revision ID: c5b6c7d8e9f0
Revises: c4a5b6c7d8e9
Create Date: 2026-09-27
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "c5b6c7d8e9f0"
down_revision: Union[str, None] = "c4a5b6c7d8e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {c["name"] for c in inspect(op.get_bind()).get_columns("room_complementry")}
    if "active_complementry_name" not in columns:
        op.execute(
            "ALTER TABLE room_complementry "
            "ADD COLUMN active_complementry_name VARCHAR(255) "
            "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Complementry_Name) ELSE NULL END) STORED"
        )
    indexes = {i["name"] for i in inspect(op.get_bind()).get_indexes("room_complementry")}
    if "uq_complementary_active_name" not in indexes:
        op.create_index("uq_complementary_active_name", "room_complementry", ["company_id", "active_complementry_name"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_complementary_active_name", table_name="room_complementry")
    op.drop_column("room_complementry", "active_complementry_name")

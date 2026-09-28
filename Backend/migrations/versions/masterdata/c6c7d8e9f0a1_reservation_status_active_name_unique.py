"""enforce active reservation status names per company

Revision ID: c6c7d8e9f0a1
Revises: c5b6c7d8e9f0
Create Date: 2026-09-27
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "c6c7d8e9f0a1"
down_revision: Union[str, None] = "c5b6c7d8e9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {c["name"] for c in inspect(op.get_bind()).get_columns("reservation_status")}
    if "active_reservation_status" not in columns:
        op.execute(
            "ALTER TABLE reservation_status "
            "ADD COLUMN active_reservation_status VARCHAR(100) "
            "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Reservation_Status) ELSE NULL END) STORED"
        )
    indexes = {i["name"] for i in inspect(op.get_bind()).get_indexes("reservation_status")}
    if "uq_reservation_status_active_name" not in indexes:
        op.create_index(
            "uq_reservation_status_active_name",
            "reservation_status",
            ["company_id", "active_reservation_status"],
            unique=True,
        )


def downgrade() -> None:
    op.drop_index("uq_reservation_status_active_name", table_name="reservation_status")
    op.drop_column("reservation_status", "active_reservation_status")

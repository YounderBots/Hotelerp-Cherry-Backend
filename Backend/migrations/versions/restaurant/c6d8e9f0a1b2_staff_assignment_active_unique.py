"""one active restaurant assignment per employee and date

Revision ID: c6d8e9f0a1b2
Revises: 5b9e1d7a4c30
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "c6d8e9f0a1b2"
down_revision: Union[str, None] = "5b9e1d7a4c30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE restaurant_staff_assignment "
        "ADD COLUMN active_employee_date VARCHAR(40) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN CONCAT(CAST(employee_id AS CHAR), ':', "
        "DATE_FORMAT(shift_date, '%Y-%m-%d')) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_restaurant_staff_active_employee_date",
        "restaurant_staff_assignment",
        ["company_id", "active_employee_date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_restaurant_staff_active_employee_date",
        table_name="restaurant_staff_assignment",
    )
    op.drop_column("restaurant_staff_assignment", "active_employee_date")

"""one active bar assignment per employee and date

Revision ID: d7e9f0a1b2c3
Revises: 7f2a8c6d1e45
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "d7e9f0a1b2c3"
down_revision: Union[str, None] = "7f2a8c6d1e45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bar_staff_assignment "
        "ADD COLUMN active_employee_date VARCHAR(40) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN CONCAT(CAST(employee_id AS CHAR), ':', "
        "DATE_FORMAT(shift_date, '%Y-%m-%d')) ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_bar_staff_active_employee_date",
        "bar_staff_assignment",
        ["company_id", "active_employee_date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_bar_staff_active_employee_date", table_name="bar_staff_assignment")
    op.drop_column("bar_staff_assignment", "active_employee_date")

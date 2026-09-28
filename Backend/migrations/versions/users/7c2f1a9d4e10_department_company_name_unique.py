"""enforce one active department name per company

Revision ID: 7c2f1a9d4e10
Revises: 198e9660fd95
Create Date: 2026-09-25

The application already performs a case-insensitive duplicate check before a
department insert, but two concurrent requests can both pass that check when the
legacy hand-built schema has no unique index.  A plain unique constraint on
``(company_id, Department_Name)`` would also reject a legitimate recreation
after a soft delete, because inactive history is retained.  This generated
column/index therefore constrains active rows only.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "7c2f1a9d4e10"
down_revision: Union[str, None] = "198e9660fd95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # MySQL has no partial unique index.  A generated nullable key gives the
    # same active-row guarantee while leaving inactive history reusable.
    op.execute(
        "ALTER TABLE department "
        "ADD COLUMN active_department_name VARCHAR(100) "
        "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' "
        "THEN Department_Name ELSE NULL END) STORED"
    )
    op.create_index(
        "uq_department_active_company_name",
        "department",
        ["company_id", "active_department_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_department_active_company_name", table_name="department")
    op.drop_column("department", "active_department_name")

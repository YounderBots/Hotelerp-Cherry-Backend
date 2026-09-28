"""enforce active housekeeping task type names per company

Revision ID: c4a5b6c7d8e9
Revises: c3f4a5b6c7d8
Create Date: 2026-09-27
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "c4a5b6c7d8e9"
down_revision: Union[str, None] = "c3f4a5b6c7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {c["name"] for c in inspect(op.get_bind()).get_columns("task_type")}
    if "active_type_name" not in columns:
        op.execute(
            "ALTER TABLE task_type "
            "ADD COLUMN active_type_name VARCHAR(100) "
            "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Type_Name) ELSE NULL END) STORED"
        )
    indexes = {i["name"] for i in inspect(op.get_bind()).get_indexes("task_type")}
    if "uq_task_type_active_name" not in indexes:
        op.create_index("uq_task_type_active_name", "task_type", ["company_id", "active_type_name"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_task_type_active_name", table_name="task_type")
    op.drop_column("task_type", "active_type_name")

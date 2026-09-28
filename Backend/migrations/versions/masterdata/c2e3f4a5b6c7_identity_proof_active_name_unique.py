"""enforce active identity proof names per company

Revision ID: c2e3f4a5b6c7
Revises: c0d1e2f3a4b5
Create Date: 2026-09-27
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "c2e3f4a5b6c7"
down_revision: Union[str, None] = "c0d1e2f3a4b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {c["name"] for c in inspect(op.get_bind()).get_columns("identity_proof")}
    if "active_proof_name" not in columns:
        op.execute(
            "ALTER TABLE identity_proof "
            "ADD COLUMN active_proof_name VARCHAR(100) "
            "GENERATED ALWAYS AS (CASE WHEN status = 'ACTIVE' THEN LOWER(Proof_Name) ELSE NULL END) STORED"
        )
    indexes = {i["name"] for i in inspect(op.get_bind()).get_indexes("identity_proof")}
    if "uq_identity_proof_active_name" not in indexes:
        op.create_index(
            "uq_identity_proof_active_name",
            "identity_proof",
            ["company_id", "active_proof_name"],
            unique=True,
        )


def downgrade() -> None:
    op.drop_index("uq_identity_proof_active_name", table_name="identity_proof")
    op.drop_column("identity_proof", "active_proof_name")

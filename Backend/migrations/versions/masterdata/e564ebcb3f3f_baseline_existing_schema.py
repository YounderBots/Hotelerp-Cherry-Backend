"""baseline existing schema

Revision ID: e564ebcb3f3f
Revises: 
Create Date: 2026-08-26 07:02:07.306816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e564ebcb3f3f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

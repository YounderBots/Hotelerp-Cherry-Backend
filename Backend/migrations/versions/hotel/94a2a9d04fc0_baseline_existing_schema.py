"""baseline existing schema

Revision ID: 94a2a9d04fc0
Revises: 
Create Date: 2026-08-26 07:02:07.734049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '94a2a9d04fc0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""baseline existing schema

Revision ID: 3e3d820c4703
Revises: 
Create Date: 2026-08-26 07:02:08.171934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3e3d820c4703'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

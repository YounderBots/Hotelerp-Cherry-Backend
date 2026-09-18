"""room_lock -- the double-booking mutex, in this service's own schema

One table, one column, no data:

    room_lock(room_id INT PRIMARY KEY)

WHY
    A booking has to check that a room is free and then insert, and between
    those two statements a second booker can run the same check and reach the
    same answer. `reservation_rules.lock_rooms` makes them take turns with a
    row lock (`SELECT ... FOR UPDATE`) taken before the check.

    That lock used to be on Master Data's `room` row, across schemas. It was
    the last reason the Hotel service's MySQL account needed a privilege in a
    schema it does not own -- every read had already moved to HTTP -- and a
    missing GRANT for it took every reservation screen on the live server
    down for three days. A mutex need not be the contended thing, only a row
    every contender agrees to lock first. This is that row.

WHY NO DATA IS COPIED
    Rows are created on first use (`INSERT IGNORE` in `lock_rooms`), so a
    room that has never been booked simply has no row yet. Nothing reads this
    table; nothing joins it. Dropping it loses nothing but the ability to
    take the lock, and `lock_rooms` would then fail loudly rather than
    silently double-book.

Revision ID: e7d2c4a9b1f0
Revises: d38f6b0c2e54
Create Date: 2026-09-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7d2c4a9b1f0"
down_revision: Union[str, None] = "d38f6b0c2e54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "room_lock",
        # The room's id in Master Data -- supplied by the caller, never
        # generated here, so no AUTO_INCREMENT.
        sa.Column("room_id", sa.Integer(), primary_key=True, nullable=False,
                  autoincrement=False),
    )


def downgrade() -> None:
    op.drop_table("room_lock")

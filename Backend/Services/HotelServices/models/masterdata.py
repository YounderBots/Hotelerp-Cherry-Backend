"""Read-only views onto the Master Data schema.

WHY THIS FILE EXISTS
    Reservation is the one module that cannot be correct without Master Data.
    A booking has to know that room 20 exists, that it is a Deluxe, that a
    Deluxe costs 11,000 a night, that tax type 3 is 12% and that "Confirmed" is
    a real status. Until now the Reservation API took every one of those facts
    from the request body, which is why a client could book a nonexistent room
    for a negative number of nights at a total of 1.

    `room`, `room_type`, `tax_type`, `discount_data`, `payment_methods`,
    `identity_proof` and `reservation_status` live in the MasterData service's
    own schema, on the same MySQL server as this service's. These mappings let
    the reservation transaction read them in the *same* session as the write,
    which matters: the availability check and the insert that depends on it
    have to be one atomic unit, and an HTTP call to another service cannot be.

WHY READ-ONLY
    MasterDataServices owns these tables. Nothing here ever writes them, and
    every mapping is deliberately partial -- only the columns Reservation
    needs. Treat them as a view: if a column is missing, add it here, never
    write through these classes.

    The exception is `room`'s three state flags, which this service does have
    to keep in step: `Room_Booking_status` (occupancy, recomputed by
    `sync_room_booking_status`), `Room_Working_status` (dirty at checkout) and
    `Room_Status` (blocked by a housekeeping task). Those are statements
    *about* occupancy and housekeeping, which is exactly what this module owns.

    It is also why the deployment needs UPDATE on `room` and not only SELECT:
    the lifecycle writes those columns, and `lock_rooms()` takes
    `SELECT ... FOR UPDATE` on the same rows, which MySQL refuses without
    UPDATE as well. See Backend/tools/grant_cross_schema.py.

SCHEMA RESOLUTION
    The schema name is derived from this service's own DB URI rather than
    hardcoded: both databases are deployed as `<prefix>_hotel` and
    `<prefix>_masterdata` on one server (see Backend/Services/make_prod_env.py),
    so `hotelerp_hotel` implies `hotelerp_masterdata`. `MASTERDATA_DB_SCHEMA`
    overrides it for a deployment that names them differently.
"""

from __future__ import annotations

import logging
import os
import re

from sqlalchemy import Column, DateTime, Float, Integer, String, text
from sqlalchemy.orm import declarative_base

from configs import Configuration

logger = logging.getLogger(__name__)

MasterBase = declarative_base()


def _resolve_schema() -> str:
    """Name of the Master Data schema on this service's database server."""
    explicit = os.getenv("MASTERDATA_DB_SCHEMA")
    if explicit:
        return explicit.strip()

    # `mysql+pymysql://user:pw@host:3306/hotelerp_hotel?charset=utf8` -> hotelerp_hotel
    uri = str(getattr(Configuration, "DB_URI", "") or "")
    own = uri.rsplit("/", 1)[-1].split("?", 1)[0].strip()

    if own.endswith("_hotel"):
        return own[: -len("_hotel")] + "_masterdata"

    # Unrecognised naming: fall back to the documented default rather than
    # guessing, and say so once at import so a mis-deploy is visible in the log
    # instead of surfacing later as "room not found" on every booking.
    logger.warning(
        "masterdata_schema_fallback own_schema=%r using=hotelerp_masterdata "
        "(set MASTERDATA_DB_SCHEMA to override)",
        own,
    )
    return "hotelerp_masterdata"


def _resolve_users_schema() -> str:
    """Name of the Users schema on this service's database server.

    Same derivation as the Master Data schema above, and the same reason: the
    databases are deployed as `<prefix>_hotel`, `<prefix>_masterdata` and
    `<prefix>_users` on one server. `USERS_DB_SCHEMA` overrides it.
    """
    explicit = os.getenv("USERS_DB_SCHEMA")
    if explicit:
        return explicit.strip()

    uri = str(getattr(Configuration, "DB_URI", "") or "")
    own = uri.rsplit("/", 1)[-1].split("?", 1)[0].strip()

    if own.endswith("_hotel"):
        return own[: -len("_hotel")] + "_users"

    logger.warning(
        "users_schema_fallback own_schema=%r using=hotelerp_users "
        "(set USERS_DB_SCHEMA to override)",
        own,
    )
    return "hotelerp_users"


MASTERDATA_SCHEMA = _resolve_schema()
USERS_SCHEMA = _resolve_users_schema()


class MasterRoom(MasterBase):
    """`room` — the physical rooms that can be sold."""

    __tablename__ = "room"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    Room_No = Column(String(100), nullable=False, index=True)
    Room_Name = Column(String(100), nullable=False)
    # Stored as a string in the master schema even though it holds an integer id.
    Room_Type_ID = Column(String(100), nullable=False, index=True)
    Bed_Type_ID = Column(String(100), nullable=False)
    Max_Adult_Occupy = Column(String(100), nullable=False)
    Max_Child_Occupy = Column(String(100), nullable=False)
    # Current occupancy flag: Available | Reserved | Occupied. This is a
    # *today* state, never a statement about a future date -- see
    # `sync_room_booking_status`.
    Room_Booking_status = Column(String(100), nullable=False, index=True)
    # Housekeeping readiness: Ready | Not Ready | Not Assigne.
    Room_Working_status = Column(String(100), nullable=False, index=True)
    # Blocking | UnBlocking — a blocked room is out of order and unsellable.
    Room_Status = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)
    updated_at = Column(DateTime)
    updated_by = Column(String(100))


class MasterRoomType(MasterBase):
    """`room_type` — the rate card. Every price in a quote starts here."""

    __tablename__ = "room_type"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    Type_Name = Column(String(100), nullable=False, index=True)
    Room_Cost = Column(Float, nullable=False)
    Bed_Cost = Column(Float, nullable=False)

    Daily_Rate = Column(Float)
    Weekly_Rate = Column(Float)
    Bed_Only_Rate = Column(Float)
    Bed_And_Breakfast_Rate = Column(Float)
    Half_Board_Rate = Column(Float)
    Full_Board_Rate = Column(Float)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


class MasterTaxType(MasterBase):
    """`tax_type` — percentages are stored as strings in the master schema."""

    __tablename__ = "tax_type"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    Tax_Name = Column(String(100), nullable=False, index=True)
    Tax_Percentage = Column(String(100), nullable=False)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


class MasterDiscount(MasterBase):
    """`discount_data` — percentages are stored as strings in the master schema."""

    __tablename__ = "discount_data"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    Discount_Name = Column(String(100), nullable=False, index=True)
    Discount_Percentage = Column(String(100), nullable=False)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


class MasterPaymentMethod(MasterBase):
    __tablename__ = "payment_methods"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    payment_method = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


class MasterIdentityProof(MasterBase):
    __tablename__ = "identity_proof"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    Proof_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


class MasterReservationStatus(MasterBase):
    """`reservation_status` — the ONLY source of the status vocabulary.

    The controller reads this rather than hardcoding labels. The reason is the
    bug it replaces: check-in required the literal status "Booked", which has
    never been a row in this table, so no reservation in the system could ever
    be checked in.
    """

    __tablename__ = "reservation_status"
    __table_args__ = {"schema": MASTERDATA_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    Reservation_Status = Column(String(100), nullable=False, index=True)
    Color = Column(String(100), nullable=False)

    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


class StaffUser(MasterBase):
    """`users` — only enough to confirm a person exists and name them.

    Housekeeping assigns a task to a member of staff, and that assignment was
    never checked: `employee_id` only had to be non-empty, so a task could be
    raised against a user id that is not a user. Deliberately partial, and
    deliberately without the password or salary columns -- nothing here needs
    them, and a read-only view onto another service's table should carry the
    least it can.
    """

    __tablename__ = "users"
    __table_args__ = {"schema": USERS_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    First_Name = Column(String(100))
    Last_Name = Column(String(100))
    status = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)


# ---------------------------------------------------------------------------
# Deployment probe
# ---------------------------------------------------------------------------
FIX = ("Run `python Backend/tools/grant_cross_schema.py` on the server to see "
       "exactly which privilege is missing, and `--confirm` to grant it. "
       "Restart this service afterwards: MySQL applies a database-level grant "
       "at a connection's next USE, and the pool holds connections opened "
       "before it.")

# What a MySQL privilege refusal looks like, and the one thing in it worth
# reading -- the account the server matched the connection to, host included:
#
#   (1142, "SELECT command denied to user 'cherryhotel'@'localhost' for table 'room'")
#   (1044, "Access denied for user 'cherryhotel'@'localhost' to database 'hotelerp_masterdata'")
#
# That account, and no other, is the one a GRANT has to name. The username in
# the DSN with a guessed host is how 'cherryhotel'@'%' got created on the
# deployment at 168.231.103.18: a second, empty account, "Query OK", and every
# 500 exactly where it was.
_DENIED_ACCOUNT = re.compile(r"denied (?:to|for) user '([^']+)'@'([^']+)'")


def grants(account: str, which=("read", "write", "users")) -> list:
    """The cross-schema GRANTs this deployment needs, aimed at `account`.

    Keyed so a probe can name only the ones it proved missing. This is the
    same set Backend/tools/grant_cross_schema.py applies; the test suite
    holds the two together so neither can drift.
    """
    stmts = {
        "read":  f"GRANT SELECT ON `{MASTERDATA_SCHEMA}`.* TO {account};",
        "write": f"GRANT UPDATE ON `{MASTERDATA_SCHEMA}`.`room` TO {account};",
        "users": f"GRANT SELECT ON `{USERS_SCHEMA}`.`users` TO {account};",
    }
    return [stmts[k] for k in which]


def denied_account(reason: str):
    """`'cherryhotel'@'localhost'` out of a refusal, or None if it is not one."""
    m = _DENIED_ACCOUNT.search(reason or "")
    return "'{}'@'{}'".format(*m.groups()) if m else None


def fix_for(reason: str, which=("read", "write", "users")) -> str:
    """The remedy, worded for whoever is reading the log.

    When MySQL named the account it refused, the remedy IS the SQL: the exact
    statements, aimed at the exact account, with nothing left to look up or
    guess. Everything else on the log line is a symptom; this is the only part
    anyone acts on, so it is written to be pasted into `mysql -u root -p` as
    it stands. Without an account in the message there is nothing exact to
    say, and the tool that asks MySQL for it is the answer.
    """
    account = denied_account(reason)
    if not account:
        return FIX
    return (
        "FIX, as a MySQL account that may GRANT (root): "
        + " ".join(grants(account, which))
        + " -- then RESTART this service: a pooled connection does not see a "
        "database-level grant until it reconnects. "
        "(`python Backend/tools/grant_cross_schema.py --confirm` runs the "
        "same statements and proves them on a fresh connection.)"
    )


def privilege_refusal(exc):
    """If `exc` is MySQL refusing this service a privilege, the fix; else None.

    For the 500 handler. A stack trace ends in "1142 ... denied ... for table
    'room'" and the operator then has to read it backwards to the account,
    the schema and the grant. This puts the whole remedy on one line, next to
    the failure, in the journal they are already reading -- and prescribes
    all three grants, because the request that failed only ever names the
    first privilege it was refused.
    """
    reason = str(getattr(exc, "orig", exc))
    if denied_account(reason) is None:
        return None
    return fix_for(reason)


def _is_mysql(db) -> bool:
    try:
        return db.get_bind().dialect.name == "mysql"
    except Exception:                                          # noqa: BLE001
        return False


def probe(db) -> tuple[bool, str]:
    """Can this service read the Master Data schema -- and write room state?

    WHY THIS EXISTS
        These mappings are cross-schema: HotelServices reads Master Data's
        tables directly, on its own connection, so that an availability check
        and the booking that depends on it commit in ONE transaction. A read
        over HTTP could not hold the row locks that make double-booking
        impossible.

        The price is a deployment coupling that nothing enforced and nothing
        documented: every schema must live on the SAME MySQL server, and the
        user in this service's DB_URI must hold privileges in a schema it does
        not own.

        Break either half and the service still starts, housekeeping and the
        night audit still work -- and every reservation screen answers 500.
        That is exactly how it reached production: the reservation list, the
        reservation detail and the availability check were the only three
        endpoints down, and the deployment looked healthy.

    WHY IT CHECKS THE WRITE TOO
        The failure in the log only ever names SELECT, so SELECT is what gets
        granted -- and the list comes back while every attempt to *book* still
        fails, because the reservation lifecycle writes `Room_Booking_status`
        back and `lock_rooms()` takes `SELECT ... FOR UPDATE`, which MySQL
        will not run without UPDATE on top of SELECT. A probe that checks only
        the read half declares that deployment ready.

        EXPLAIN runs the privilege check and nothing else -- MySQL requires
        the same privileges to EXPLAIN a statement as to execute it -- so this
        stays a read-only probe, takes no row lock, and is safe to call per
        request. `id = 0` matches no row in any case.

    Returns (ok, detail). Cheap enough for a readiness probe: one indexed
    read and one plan, no scan.
    """
    try:
        db.query(MasterRoom.id).limit(1).all()
    except Exception as exc:                                   # noqa: BLE001
        reason = str(getattr(exc, "orig", exc))[:200]
        return False, (
            f"cannot read schema {MASTERDATA_SCHEMA!r}: {reason}. "
            "Every schema must be on the same MySQL server as this service's, "
            "and this service's DB user needs SELECT on it. Set "
            "MASTERDATA_DB_SCHEMA if the schema is not named "
            # Prescribe UPDATE on room alongside SELECT: the write probe below
            # never ran, and granting SELECT alone is the trap this file
            # documents at the top.
            f"<own-prefix>_masterdata. {fix_for(reason, ('read', 'write'))}"
        )

    if not _is_mysql(db):
        # SQLite under test, where the schema is an ATTACHed database and
        # every privilege is implicit. Nothing to assert.
        return True, f"{MASTERDATA_SCHEMA} readable"

    try:
        db.execute(text(
            f"EXPLAIN UPDATE `{MASTERDATA_SCHEMA}`.`room` "
            "SET `Room_Booking_status` = `Room_Booking_status` WHERE `id` = 0"
        ))
    except Exception as exc:                                   # noqa: BLE001
        reason = str(getattr(exc, "orig", exc))[:200]
        if "denied" not in reason.lower():
            # Not a privilege problem -- an ancient MySQL that cannot EXPLAIN
            # an UPDATE, say. The read works, which is the half that matters
            # for serving; do not fail readiness over an inconclusive check.
            logger.warning("masterdata_write_probe_inconclusive detail=%s", reason)
            return True, f"{MASTERDATA_SCHEMA} readable (write check inconclusive)"
        return False, (
            f"can read {MASTERDATA_SCHEMA!r} but cannot write "
            f"{MASTERDATA_SCHEMA}.room: {reason}. Reservations will list but "
            "no booking, check-in, check-out or room block will succeed: this "
            "service keeps the room's occupancy and housekeeping flags in step "
            "and takes SELECT ... FOR UPDATE on those rows, which MySQL "
            f"refuses without UPDATE as well as SELECT. {fix_for(reason, ('write',))}"
        )

    return True, f"{MASTERDATA_SCHEMA} readable and room state writable"


def probe_users(db) -> tuple[bool, str]:
    """Can this service read the Users schema?

    Same coupling, smaller blast radius: housekeeping validates that a task's
    assignee is a real member of staff against `users`.`users`. Without the
    grant, assigning a task 500s while every other screen in the service works
    -- so it gets its own check rather than being folded into the one above,
    which would report "reservations are down" for a housekeeping problem.
    """
    try:
        db.query(StaffUser.id).limit(1).all()
        return True, f"{USERS_SCHEMA} readable"
    except Exception as exc:                                   # noqa: BLE001
        reason = str(getattr(exc, "orig", exc))[:200]
        return False, (
            f"cannot read {USERS_SCHEMA}.users: {reason}. Assigning a "
            "housekeeping task checks its assignee against that table and will "
            f"answer 500 until this is fixed. {fix_for(reason, ('users',))}"
        )

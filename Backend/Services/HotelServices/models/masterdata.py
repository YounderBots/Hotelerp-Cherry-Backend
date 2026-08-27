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

    The one exception is `Room.Room_Booking_status`, which the reservation
    lifecycle does have to keep in step (see `sync_room_booking_status` in the
    controller). That is a status flag *about* occupancy, and occupancy is
    exactly what this module owns.

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

from sqlalchemy import Column, DateTime, Float, Integer, String
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


MASTERDATA_SCHEMA = _resolve_schema()


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

from configs import BaseConfig
import os
from sqlalchemy import Boolean, Column, String, DateTime, LargeBinary, func
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time, Date, DateTime, BLOB, JSON, Float, Numeric
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from models import engine
import bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

# NO TABLE-LEVEL UniqueConstraint ON THESE MASTER-DATA TABLES, ON PURPOSE (C-082)
#
# These models used to declare `UniqueConstraint("company_id", <name>)` for
# facility, room type, bed type, hall/floor, room number, discount, tax, payment
# method, identity proof, country, task type, complementary, reservation status,
# department and designation. No such index exists in any applied schema, so the
# declaration described an invariant the database never enforced -- and a
# `Base.metadata.create_all()` or an Alembic autogenerate would have tried to add
# it, producing a schema no environment has.
#
# It was also the wrong invariant. Master data is soft-deleted, so a hard unique
# on (company_id, name) refuses to recreate a name whose previous row was
# deleted, which is a legitimate operation. The invariant that is actually
# enforced -- active names are unique per company, soft-deleted history may
# repeat -- is created by migrations as a generated column plus a unique index
# (`uq_facility_active_name`, `uq_room_type_active_name`, ... ). Add new
# uniqueness the same way: a generated column that is NULL for soft-deleted
# rows, a unique index over it, and no `__table_args__` here.

#Facility
class Facility(Base):
    __tablename__ = "facility"

    id = Column(Integer, primary_key=True, index=True)
    Facility_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Room Type
class Room_Type(Base):
    __tablename__ = "room_type"

    id = Column(Integer, primary_key=True, index=True)
    Type_Name = Column(String(100), nullable=False, index=True)
    Room_Cost = Column(Numeric(12, 2, asdecimal=False), nullable=False, index=True)
    Bed_Cost = Column(Numeric(12, 2, asdecimal=False), nullable=False, index=True)
    Complementry = Column(String(100), nullable=False, index=True)  # Room Complementry table id store

    # Rate Types
    Daily_Rate = Column(Numeric(12, 2, asdecimal=False), nullable=True, index=True)
    Weekly_Rate = Column(Numeric(12, 2, asdecimal=False), nullable=True, index=True)
    Bed_Only_Rate = Column(Numeric(12, 2, asdecimal=False), nullable=True, index=True)
    Bed_And_Breakfast_Rate = Column(Numeric(12, 2, asdecimal=False), nullable=True, index=True)
    Half_Board_Rate = Column(Numeric(12, 2, asdecimal=False), nullable=True, index=True)
    Full_Board_Rate = Column(Numeric(12, 2, asdecimal=False), nullable=True, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Bed Type
class Bed_Type(Base):
    __tablename__ = "bed_type"

    id = Column(Integer, primary_key=True, index=True)
    Type_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Hall and Floor Details
class TableHallNames(Base):
    __tablename__ = "table_hall_names"

    id = Column(Integer, primary_key=True, index=True)
    hall_name = Column(String(255), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Room
class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    Room_No = Column(String(100), nullable=False, index=True)
    Room_Name = Column(String(100), nullable=False, index=True)
    Room_Type_ID = Column(String(100), nullable=False, index=True)
    Bed_Type_ID = Column(String(100), nullable=False, index=True)
    Room_Telephone = Column(String(100), nullable=False, index=True)
    Room_Image_1 = Column(String(255), nullable=False)
    Room_Image_2 = Column(String(255), nullable=False)
    Room_Image_3 = Column(String(255), nullable=False)
    Room_Image_4 = Column(String(255), nullable=False)
    Max_Adult_Occupy = Column(String(100), nullable=False, index=True)
    Max_Child_Occupy = Column(String(100), nullable=False, index=True)
    Room_Booking_status = Column(String(100), nullable=False, index=True)
    Room_Working_status = Column(String(100), nullable=False, index=True)
    Room_Status = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Discount
class Discount_Data(Base):
    __tablename__ = "discount_data"

    id = Column(Integer, primary_key=True, index=True)
    Country_ID = Column(String(100), nullable=False, index=True)
    Discount_Name = Column(String(100), nullable=False, index=True)
    Discount_Percentage = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Tax Type
class Tax_type(Base):
    __tablename__ = "tax_type"

    id = Column(Integer, primary_key=True, index=True)
    Country_ID = Column(String(100), nullable=False, index=True)
    Tax_Name = Column(String(100), nullable=False, index=True)
    Tax_Percentage = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Payment Method
class Payment_Methods(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    payment_method = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Identity Proof
class Identity_Proofs(Base):
    __tablename__ = "identity_proof"

    id = Column(Integer, primary_key=True, index=True)
    Proof_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


# Country Currency
class Country_Currency(Base):
    __tablename__ = "countries_currency"

    id = Column(Integer, primary_key=True, index=True)
    Country_Name = Column(String(100), nullable=False, index=True)
    Currency_Name = Column(String(100), nullable=False, index=True)
    Symbol = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#House Keeping Task Type
class Task_Type(Base):
    __tablename__ = "task_type"

    id = Column(Integer, primary_key=True, index=True)
    Type_Name = Column(String(100), nullable=False, index=True)
    Color = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#------------------->Complementry
#Room Complementry
class Room_Complementry(Base):
    __tablename__ = "room_complementry"

    id = Column(Integer, primary_key=True, index=True)
    Complementry_Name = Column(String(255), nullable=False, index=True)
    Description = Column(String(255), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Reservation Status
class Reservation_Status(Base):
    __tablename__ = "reservation_status"

    id = Column(Integer, primary_key=True, index=True)
    Reservation_Status = Column(String(100), nullable=False, index=True)
    Color = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)

#Department
class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, index=True)
    Department_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)

#Designation
class Designation(Base):
    __tablename__ = "designation"

    id = Column(Integer, primary_key=True, index=True)
    Designation_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)

# ---------------------------------------------------------------------------
# Schema creation is opt-in.
#
# This used to run unconditionally at import, which meant (a) the service could
# not start at all if the database was briefly unreachable, and (b) production
# schema was implicitly created from the ORM models, racing between replicas and
# silently diverging from the managed .sql schema. `create_all` only ever adds
# missing tables — it never alters an existing one — so the drift stayed hidden.
#
# Dev keeps the convenience; production must apply migrations explicitly.
# ---------------------------------------------------------------------------
def init_schema() -> None:
    """Creates any missing tables. Call explicitly; never on import."""
    Base.metadata.create_all(bind=engine)


if os.getenv(
    "DB_AUTO_CREATE",
    "false" if getattr(BaseConfig, "IS_PRODUCTION", False) else "true",
).lower() in ("1", "true", "yes"):
    init_schema()


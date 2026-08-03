from configs import BaseConfig
import os
from sqlalchemy import Boolean, Column, String, DateTime, LargeBinary, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time, Date, DateTime, BLOB, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from models import engine
import bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

#Facility
class Facility(Base):
    __tablename__ = "facility"
    __table_args__ = (
        UniqueConstraint("company_id", "Facility_Name", name="uq_facility_facility_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Type_Name", name="uq_room_type_type_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    Type_Name = Column(String(100), nullable=False, index=True)
    Room_Cost = Column(Float, nullable=False, index=True)
    Bed_Cost = Column(Float, nullable=False, index=True)
    Complementry = Column(String(100), nullable=False, index=True)  # Room Complementry table id store

    # Rate Types
    Daily_Rate = Column(Float, nullable=True, index=True)
    Weekly_Rate = Column(Float, nullable=True, index=True)
    Bed_Only_Rate = Column(Float, nullable=True, index=True)
    Bed_And_Breakfast_Rate = Column(Float, nullable=True, index=True)
    Half_Board_Rate = Column(Float, nullable=True, index=True)
    Full_Board_Rate = Column(Float, nullable=True, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)


#Bed Type
class Bed_Type(Base):
    __tablename__ = "bed_type"
    __table_args__ = (
        UniqueConstraint("company_id", "Type_Name", name="uq_bed_type_type_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "hall_name", name="uq_tablehallnames_hall_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Room_No", name="uq_room_room_no"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Country_ID", "Discount_Name", name="uq_discount_data_country_id_discount_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Country_ID", "Tax_Name", name="uq_tax_type_country_id_tax_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "payment_method", name="uq_payment_methods_payment_method"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Proof_Name", name="uq_identity_proofs_proof_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Country_Name", name="uq_country_currency_country_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Type_Name", name="uq_task_type_type_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Complementry_Name", name="uq_room_complementry_complementry_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Reservation_Status", name="uq_reservation_status_reservation_status"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Department_Name", name="uq_department_department_name"),
    )

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
    __table_args__ = (
        UniqueConstraint("company_id", "Designation_Name", name="uq_designation_designation_name"),
    )

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


from sqlalchemy import Boolean, Column,String, DateTime, LargeBinary ,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time,Date,DateTime,BLOB, JSON,Float
from sqlalchemy.orm import relationship
from datetime import datetime
from models import engine
import bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
   
# =====================================================
# ROOM RESERVATION
# Room Reservation | Group Reservation | Check-in/out
# =====================================================
class RoomReservation(Base):
    __tablename__ = "room_reservation"

    id = Column(Integer, primary_key=True, index=True)

    room_reservation_id = Column(String(255), unique=True, nullable=False, index=True)

    # ---------------- Guest Details ----------------
    salutation = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True)

    # ---------------- Stay Details ----------------
    arrival_date = Column(Date, nullable=False, index=True)
    departure_date = Column(Date, nullable=False, index=True)
    no_of_nights = Column(Integer, nullable=False)

    room_type = Column(JSON, nullable=True)
    rate_type = Column(JSON, nullable=True)
    room_no = Column(JSON, nullable=True)

    no_of_rooms = Column(Integer, nullable=True)
    no_of_adults = Column(Integer, nullable=True)
    no_of_children = Column(Integer, nullable=True)

    # ---------------- Payment Details ----------------
    payment_mode = Column(String(100), nullable=True)

    extra_bed_count = Column(Integer, nullable=True)
    extra_bed_cost = Column(Float, nullable=True)

    total_amount = Column(Float, nullable=True)
    tax_percentage = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)

    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)

    extra_charges = Column(Float, nullable=True)

    overall_amount = Column(Float, nullable=True)
    paid_amount = Column(Float, nullable=True)
    balance_amount = Column(Float, nullable=True)
    extra_amount = Column(Float, nullable=True)

    # ---------------- Reservation Info ----------------
    booking_status = Column(String(50), nullable=True, index=True)
    reservation_type = Column(String(50), nullable=False, index=True)

    room_complementary = Column(String(100), nullable=True)
    common_complementary = Column(String(100), nullable=True)

    identity_type = Column(String(100), nullable=True)
    proof_document = Column(String(255), nullable=True)

    confirmation_code = Column(String(100), nullable=True, index=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)

    status = Column(String(50), nullable=False, index=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)


class RoomDetails(Base):
    __tablename__ = "room_details"

    id = Column(Integer, primary_key=True, index=True)

    reservation_id = Column(String(255), nullable=False, index=True)

    # ---------------- Room Info ----------------
    room_category = Column(String(255), nullable=False)
    available_rooms = Column(Integer, nullable=False)

    total_adults = Column(Integer, nullable=False)
    total_children = Column(Integer, nullable=False)

    arrival_date = Column(Date, nullable=False, index=True)
    departure_date = Column(Date, nullable=False, index=True)

    booking_status = Column(String(50), nullable=True, index=True)

    reservation_type = Column(String(50), nullable=False, index=True)  # Reservation | Group_Reservation | Checkin

    # ---------------- Extra Charges ----------------
    extra_bed_count = Column(Integer, nullable=True)
    extra_bed_cost = Column(Float, nullable=True)

    total_amount = Column(Float, nullable=True)

    room_complementary = Column(String(10), nullable=True)  # Yes / No

    # ---------------- System Fields ----------------
    token = Column(String(36),unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(String(50), nullable=False, index=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

#Reservation Amount Paid History
class ReservationAmountPaidHistory(Base):
    __tablename__ = "reservation_amount_paid_history"

    id = Column(Integer, primary_key=True, index=True)

    reservation_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    paid_date = Column(Date, nullable=False, index=True)

    payment_method = Column(String(100), nullable=False, index=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(String(50), nullable=False, index=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

 
# =====================================================
# CUSTOMER ROOM RESERVED COMPLEMENTARY HISTORY
# =====================================================
class RoomComplementaryHistory(Base):
    __tablename__ = "room_complementary_history"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Reservation Reference ----------------
    reservation_id = Column(String(255), nullable=False, index=True)
    room_complementary_id = Column(String(255), nullable=False, index=True)

    # ---------------- Complementary Details ----------------
    complementary_name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# CUSTOMER RESERVED COMMON COMPLEMENTARY HISTORY
# =====================================================
class CommonComplementaryHistory(Base):
    __tablename__ = "common_complementary_history"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Reservation Reference ----------------
    reservation_id = Column(String(255), nullable=False, index=True)
    common_complementary_id = Column(String(255), nullable=False, index=True)

    # ---------------- Complementary Details ----------------
    complementary_name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# ROOM BOOKING
# =====================================================
class RoomBooking(Base):
    __tablename__ = "room_booking"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Booking Reference ----------------
    room_booking_id = Column(String(255), unique=True, nullable=False, index=True)

    # ---------------- Guest Details ----------------
    salutation = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True)

    # ---------------- Stay Details ----------------
    arrival_date = Column(Date, nullable=False, index=True)
    departure_date = Column(Date, nullable=False, index=True)
    no_of_nights = Column(Integer, nullable=False)

    room_type = Column(JSON, nullable=True)

    no_of_rooms = Column(Integer, nullable=True)
    no_of_adults = Column(Integer, nullable=True)
    no_of_children = Column(Integer, nullable=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# HOUSE KEEPING
# Housekeeper Task Management
# =====================================================
class HousekeeperTask(Base):
    __tablename__ = "housekeeper_task"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String(100), nullable=False, index=True)  # stores users.id
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    schedule_date = Column(Date, nullable=False, index=True)
    schedule_time = Column(Time, nullable=False)
    room_no = Column(Integer, nullable=False, index=True) # room id
    task_type = Column(String(100), nullable=False, index=True) # task type id
    assign_staff = Column(String(100), nullable=False, index=True) # users.id
    task_status = Column(String(50), nullable=False, index=True)  # Pending | In-Progress | Completed
    room_status = Column(String(50), nullable=False, index=True)  # Blocking | Unblocking
    lost_found = Column(String(255), nullable=True)
    special_instructions = Column(String(255), nullable=True) 

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=False, index=True)


# =====================================================
# HOUSE KEEPING
# Housekeeper Room Incident
# =====================================================
class HousekeeperRoomIncident(Base):
    __tablename__ = "hsk_room_incident"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Room & Incident Details ----------------
    room_no = Column(Integer, nullable=True, index=True)
    incident_date = Column(Date, nullable=True, index=True)
    incident_time = Column(Time, nullable=True)

    incident_description = Column(String(255), nullable=True)

    # ---------------- Staff & Severity ----------------
    involved_staff = Column(String(255), nullable=True, index=True)
    severity = Column(String(50), nullable=True, index=True)
    witnesses = Column(String(255), nullable=True)

    # ---------------- Action & Reporting ----------------
    actions_taken = Column(String(255), nullable=True)
    reported_by = Column(String(100), nullable=True, index=True)
    report_date = Column(Date, nullable=True, index=True)

    # ---------------- Attachments ----------------
    attachment_file = Column(String(255), nullable=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# LAUNDRY MANAGEMENT
# Laundry Items Master
# =====================================================
class LaundryItems(Base):
    __tablename__ = "laundry_items"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Item Details ----------------
    item_name = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# LAUNDRY MANAGEMENT
# Laundry Transactions
# =====================================================
class LaundryManagement(Base):
    __tablename__ = "laundry_management"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Guest / Room Details ----------------
    room_id = Column(String(100), nullable=True, index=True)
    guest_name = Column(String(100), nullable=True)
    mobile = Column(String(20), nullable=False, index=True)

    # ---------------- Laundry Details ----------------
    laundry_date = Column(Date, nullable=False, index=True)

    items = Column(JSON, nullable=False)              # [{item_id, item_name}]
    item_counts = Column(JSON, nullable=False)        # {item_id: qty}
    item_prices = Column(JSON, nullable=False)        # {item_id: price}

    total_items = Column(Integer, nullable=False)
    net_price = Column(Float, nullable=False)

    laundry_status = Column(String(50), nullable=False, index=True)   # Pending | In-Process | Completed | Delivered

    special_instructions = Column(String(255), nullable=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# CUSTOMER DATA
# Guest / Stay / Billing Snapshot
# =====================================================
class CustomerData(Base):
    __tablename__ = "customer_data"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Customer Identity ----------------
    customer_id = Column(String(100), nullable=True, index=True)
    photo = Column(String(255), nullable=True)

    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)

    email = Column(String(100), nullable=False, index=True)
    mobile = Column(String(20), nullable=False, index=True)

    date_of_birth = Column(Date, nullable=False)

    gender = Column(String(20), nullable=False, index=True)
    marital_status = Column(String(20), nullable=False, index=True)
    vip_status = Column(String(20), nullable=False, index=True)

    # ---------------- Address Details ----------------
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    postal_code = Column(String(20), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)

    # ---------------- Guest Details ----------------
    number_of_guests = Column(Integer, nullable=False)
    number_of_adults = Column(Integer, nullable=False)
    adult_names = Column(JSON, nullable=False)

    number_of_children = Column(Integer, nullable=False)
    children_names = Column(JSON, nullable=False)

    # ---------------- Identification ----------------
    identification_type_id = Column(String(100), nullable=False, index=True)
    identification_proof = Column(String(255), nullable=False)

    # ---------------- Stay Details ----------------
    reservation_id = Column(String(100), nullable=True, index=True)

    check_in_date = Column(Date, nullable=True, index=True)
    check_in_time = Column(Time, nullable=True)

    check_out_date = Column(Date, nullable=True, index=True)
    check_out_time = Column(Time, nullable=True)

    room_ids = Column(JSON, nullable=True)
    room_type_ids = Column(JSON, nullable=True)
    bed_type_ids = Column(JSON, nullable=True)

    # ---------------- Purpose & Emergency ----------------
    purpose_of_visit = Column(String(255), nullable=True)

    emergency_name = Column(String(100), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    emergency_relationship = Column(String(50), nullable=True)

    # ---------------- Consent ----------------
    consent_for_data_use = Column(String(10), nullable=True)              # Yes / No
    acknowledgment_of_hotel_policies = Column(String(10), nullable=True) # Yes / No

    # ---------------- Special Services ----------------
    special_services_info = Column(JSON, nullable=True)

    # ---------------- Billing Snapshot ----------------
    total_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)

    laundry_amount = Column(Float, nullable=True)
    bar_amount = Column(Float, nullable=True)
    cafe_amount = Column(Float, nullable=True)
    restaurant_amount = Column(Float, nullable=True)
    special_services_amount = Column(Float, nullable=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)
 
# =====================================================
# MASTER DATA
# Language
# =====================================================
class Language(Base):
    __tablename__ = "language"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Language Details ----------------
    language_name = Column(String(100), nullable=False, index=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# MASTER DATA
# Quantity
# =====================================================
class Quantity(Base):
    __tablename__ = "quantity"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Quantity Details ----------------
    name = Column(String(100), nullable=False, index=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# INQUIRY MANAGEMENT
# Guest Inquiry Tracking
# =====================================================
class Inquiry(Base):
    __tablename__ = "inquiry"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Inquiry Details ----------------
    inquiry_mode = Column(String(50), nullable=False, index=True)      # Online | Offline
    guest_name = Column(String(255), nullable=False, index=True)

    response = Column(String(255), nullable=True)
    follow_up = Column(String(255), nullable=True)

    incidents = Column(String(255), nullable=True)

    inquiry_status = Column(String(50), nullable=False, index=True)    # In Progress | Completed

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# MASTER DATA
# Theme Configuration
# =====================================================
class Themes(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Theme Colors ----------------
    primary_color = Column(String(50), nullable=False, index=True)
    button_color = Column(String(50), nullable=False, index=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True) 
    
Base.metadata.create_all(bind=engine)

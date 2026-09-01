from configs import BaseConfig
import os
from sqlalchemy import Boolean, Column,String, DateTime, LargeBinary ,func
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time,Date,DateTime,BLOB, JSON,Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from models import engine
import bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()
   
# =====================================================
# ROOM RESERVATION
# =====================================================
class RoomReservation(Base):
    __tablename__ = "room_reservation"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Reference ----------------
    room_reservation_id = Column(String(255), unique=True, nullable=False, index=True)

    # ---------------- Guest Details ----------------
    salutation = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    email = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=False, index=True)

    # ---------------- Stay Details ----------------
    arrival_date = Column(Date, nullable=False, index=True)
    departure_date = Column(Date, nullable=False, index=True)

    no_of_nights = Column(Integer, nullable=False)
    no_of_rooms = Column(Integer, nullable=True)

    reservation_status = Column(String(100), nullable=True, index=True)

    # ---------------- Identity ----------------
    identity_type_id = Column(Integer, nullable=True, index=True)  # identity_proofs.id
    proof_document = Column(String(255), nullable=True)

    # ---------------- Room Details ----------------
    room_ids = Column(JSON, nullable=True)       # [room_id]
    room_type_ids = Column(JSON, nullable=True)  # [room_type_id]
    room_no = Column(JSON, nullable=True)        # [room_no]

    rate_type = Column(JSON, nullable=True)      # ["daily", "weekly"]

    no_of_adults = Column(Integer, nullable=True)
    no_of_children = Column(Integer, nullable=True)

    room_complementary = Column(String(100), nullable=True)
    common_complementary = Column(String(100), nullable=True)

    # ---------------- Tax & Discount ----------------
    tax_type_id = Column(Integer, nullable=True, index=True)        # tax_types.id
    discount_type_id = Column(Integer, nullable=True, index=True)   # discount_types.id

    room_amount = Column(Float, default=0)
    extra_charges = Column(Float, default=0)

    tax_percentage = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)

    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)

    overall_amount = Column(Float, nullable=True)

    # ---------------- Payment ----------------
    payment_method_id = Column(Integer, nullable=True, index=True)  # payment_methods.id

    paying_amount = Column(Float, nullable=True)
    paid_amount = Column(Float, default=0)

    balance_amount = Column(Float, nullable=True)
    extra_amount = Column(Float, default=0)

    extra_bed_count = Column(Integer, default=0)
    extra_bed_cost = Column(Float, default=0)

    total_amount = Column(Float, nullable=True)

    # ---------------- Reservation Info ----------------
    booking_status_id = Column(Integer, nullable=True, index=True)  # reservation_status.id
    reservation_type = Column(String(50), nullable=False, index=True)

    confirmation_code = Column(String(100), nullable=True, index=True)

    # ---------------- Cancellation ----------------
    # Why a booking was cancelled, when, and by whom.
    #
    # The status alone said a reservation had been cancelled and nothing about
    # why, so a released room, a guest who changed their mind, an overbooking
    # the desk resolved and a duplicate somebody tidied up were all the same
    # record. That is the one question anyone asks about a cancellation
    # afterwards, and it was the one thing not kept.
    #
    # All three are nullable: every reservation that already exists was
    # cancelled -- or not -- before these columns did, and back-filling a
    # reason nobody recorded would be inventing history.
    cancellation_reason = Column(String(500), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(String(100), nullable=True)

    # ---------------- System ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

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

    # employee_id and assign_staff both hold the assigned user's id, and
    # first/last name are that user's name denormalised onto the row (the
    # dashboard and night-audit screens read the name from here rather than
    # joining across to UserServices). One staff picker fills all four.
    employee_id = Column(String(100), nullable=False, index=True)  # stores users.id
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    schedule_time = Column(Time, nullable=False)
    schedule_date = Column(Date, nullable=False)
    room_no = Column(Integer, nullable=False, index=True)  # master room id (room.id)
    # The task_type NAME from the masterdata task_type table, not its id --
    # that is what every existing row holds and what the dashboard renders.
    task_type = Column(String(100), nullable=False, index=True)
    # `assign_staff` was declared twice: once above as a Date and again here as
    # the String the column really is. SQLAlchemy kept the second, so the Date
    # was dead weight that only made the model lie about the schema.
    assign_staff = Column(String(100), nullable=False, index=True)  # users.id
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
    

# =====================================================
# NIGHT AUDIT
# Hotel business date (one row per company)
# =====================================================
class HotelBusinessDate(Base):
    """The hotel's own operating date, which is NOT the calendar date.

    A hotel day runs from one night audit to the next, so between midnight and
    the audit the property is still transacting on *yesterday's* date. Every
    Night Audit figure is scoped to this value rather than `date.today()`, and
    the audit is the only thing that moves it forward.

    Deriving the date from the server clock -- which is what the module used to
    do everywhere -- means the books roll over at midnight whether or not the
    day was ever closed, so a night that was never audited is silently skipped
    and can never be audited afterwards.
    """

    __tablename__ = "hotel_business_date"
    __table_args__ = (
        # One business date per property. The upsert path relies on this to
        # make a concurrent first-time initialisation fail rather than create
        # a second, divergent date for the same company.
        UniqueConstraint("company_id", name="uq_business_date_company"),
    )

    id = Column(Integer, primary_key=True, index=True)

    business_date = Column(Date, nullable=False, index=True)

    # Set by the audit that last advanced the date; null until the first run.
    last_audit_at = Column(DateTime, nullable=True)
    last_audit_by = Column(String(100), nullable=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)


# =====================================================
# NIGHT AUDIT
# One immutable record per audited business date
# =====================================================
class NightAudit(Base):
    """The record of one night's audit, and the module's idempotency guard.

    WHY THE UNIQUE CONSTRAINT IS THE DESIGN
        Everything else about running an audit twice -- a double-clicked
        button, a retried request, a second browser tab, two operators at two
        terminals -- is a race that application code cannot close on its own.
        `uq_night_audit_company_date` closes it in the database: the second
        writer for a given business date fails on the constraint, so the day's
        figures can only ever be recorded once and the date can only advance
        once.

    WHY THE TOTALS ARE STORED RATHER THAN RECOMPUTED
        A night audit is a statement of the property's position at a point in
        time. Recomputing it later from live reservation rows would produce a
        different answer every time somebody edits an old booking, which is the
        opposite of what an audit trail is for. These columns are a snapshot
        and are never rewritten after the run completes.
    """

    __tablename__ = "night_audit"
    __table_args__ = (
        UniqueConstraint("company_id", "business_date", name="uq_night_audit_company_date"),
    )

    id = Column(Integer, primary_key=True, index=True)

    night_audit_id = Column(String(100), unique=True, nullable=False, index=True)

    # ---------------- Dates ----------------
    # The night that was audited, and the date the property moved to.
    business_date = Column(Date, nullable=False, index=True)
    next_business_date = Column(Date, nullable=True)

    # ---------------- Run State ----------------
    # Running | Completed | Failed  -- see AUDIT_STATUSES in the controller.
    audit_status = Column(String(20), nullable=False, index=True, default="Running")

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    run_by = Column(String(100), nullable=True)
    error_message = Column(String(500), nullable=True)

    # ---------------- Occupancy ----------------
    # rooms_occupied is derived from reservations, which this service owns.
    # rooms_total comes from the room master in another service and is fetched
    # best-effort, so it -- and anything derived from it -- may be null.
    rooms_total = Column(Integer, nullable=True)
    rooms_occupied = Column(Integer, nullable=True)
    occupancy_percent = Column(Float, nullable=True)
    room_nights = Column(Integer, nullable=True)

    # ---------------- Guest Movement ----------------
    arrivals_expected = Column(Integer, nullable=True)
    arrivals_completed = Column(Integer, nullable=True)
    departures_expected = Column(Integer, nullable=True)
    departures_completed = Column(Integer, nullable=True)
    in_house = Column(Integer, nullable=True)
    stayovers = Column(Integer, nullable=True)

    no_shows_marked = Column(Integer, nullable=True)
    # Reservation ids this run moved to No-Show, so the change is attributable
    # and reversible by hand if an operator marked a late arrival in error.
    no_show_reservation_ids = Column(JSON, nullable=True)

    # ---------------- Revenue (accrued for this night only) ----------------
    room_revenue = Column(Float, nullable=True)
    extra_charges = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    gross_revenue = Column(Float, nullable=True)

    # ---------------- Settlement (cash movement on this date) ----------------
    payments_collected = Column(Float, nullable=True)
    # [{payment_method, amount}] -- by method name as recorded on the payment.
    payment_breakdown = Column(JSON, nullable=True)
    outstanding_balance = Column(Float, nullable=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
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


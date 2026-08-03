from sqlalchemy.orm import declarative_base
from configs import BaseConfig
import os
import uuid
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    func,
)
from models import engine

Base = declarative_base()

# Standard record lifecycle flag, reused via `status_enum` on every table.
STATUS_VALUES = ("ACTIVE", "INACTIVE")


# =====================================================
# RESTAURANT MANAGEMENT
# Floor Master
# =====================================================
class RestaurantFloor(Base):
    __tablename__ = "restaurant_floor"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "floor_code", name="uq_floor_code"),)

    id = Column(Integer, primary_key=True, index=True)

    floor_code = Column(String(100), nullable=False, index=True)
    floor_name = Column(String(100), nullable=False, index=True)
    floor_number = Column(Integer, nullable=False, index=True)

    floor_type = Column(SAEnum("Restaurant", "Banquet", "Outdoor", name="floor_type_enum"), nullable=False, index=True)

    description = Column(String(255), nullable=True)

    total_tables = Column(Integer, nullable=True)
    total_capacity = Column(Integer, nullable=True)

    layout_json = Column(JSON, nullable=True)  # table positions for visual floor layout

    color_code = Column(String(20), nullable=True)
    is_open = Column(Boolean, nullable=False, default=True)

    status = Column(SAEnum(*STATUS_VALUES, name="floor_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Table Master
# =====================================================
class RestaurantTable(Base):
    __tablename__ = "restaurant_table"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "table_code", name="uq_table_code"),)

    id = Column(Integer, primary_key=True, index=True)

    table_code = Column(String(100), nullable=False, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    table_number = Column(Integer, nullable=False, index=True)

    floor_id = Column(Integer, ForeignKey("restaurant_floor.id"), nullable=False, index=True)
    floor_code = Column(String(100), nullable=False, index=True)

    table_type = Column(SAEnum("Standard", "VIP", "Private", name="table_type_enum"), nullable=False, index=True)
    seating_capacity = Column(Integer, nullable=False)

    section = Column(SAEnum("Restaurant", "Outdoor", "Banquet", name="table_section_enum"), nullable=True, index=True)

    # No FK: would form a circular dependency with RestaurantOrder.table_id.
    # Type fixed from the previous String(100) mismatch to a real Integer id.
    current_order_id = Column(Integer, nullable=True, index=True)  # restaurant_order.id
    server_id = Column(String(100), nullable=True, index=True)
    server_name = Column(String(100), nullable=True)

    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    shape = Column(String(50), nullable=True)  # Circle | Square | Rectangle
    color_code = Column(String(20), nullable=True)

    table_status = Column(
        SAEnum("Available", "Occupied", "Reserved", "Cleaning", "Blocked", name="table_status_enum"),
        nullable=False,
        index=True,
    )
    is_mergeable = Column(Boolean, nullable=False, default=False)

    status = Column(SAEnum(*STATUS_VALUES, name="table_status_lifecycle_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Order Management
# =====================================================
class RestaurantOrder(Base):
    __tablename__ = "restaurant_order"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "order_number", name="uq_order_number"),)

    id = Column(Integer, primary_key=True, index=True)

    order_number = Column(String(100), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    order_time = Column(Time, nullable=False)

    order_type = Column(SAEnum("Dine-In", "Takeaway", "Delivery", "Room Service", name="order_type_enum"), nullable=False, index=True)

    table_id = Column(Integer, ForeignKey("restaurant_table.id"), nullable=True, index=True)
    table_code = Column(String(100), nullable=True, index=True)
    room_no = Column(String(50), nullable=True, index=True)  # for room service

    floor_id = Column(Integer, ForeignKey("restaurant_floor.id"), nullable=True, index=True)
    floor_code = Column(String(100), nullable=True, index=True)

    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=True, index=True)
    guest_name = Column(String(100), nullable=True)
    guest_mobile = Column(String(20), nullable=True, index=True)

    no_of_guests = Column(Integer, nullable=True)

    server_id = Column(String(100), nullable=True, index=True)
    server_name = Column(String(100), nullable=True)

    order_status = Column(
        SAEnum("New", "In Progress", "Ready", "Served", "Completed", "Cancelled", name="order_status_enum"),
        nullable=False,
        index=True,
    )
    payment_status = Column(SAEnum("Pending", "Partial", "Paid", name="order_payment_status_enum"), nullable=False, index=True)

    sub_total = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    service_charge = Column(Float, default=0)

    discount_type = Column(SAEnum("Percentage", "Flat", name="order_discount_type_enum"), nullable=True)
    discount_value = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    grand_total = Column(Float, default=0)

    special_notes = Column(String(255), nullable=True)
    estimated_prep_time = Column(Integer, nullable=True)  # in minutes

    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(SAEnum(*STATUS_VALUES, name="order_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Table Reservation
# =====================================================
class RestaurantTableReservation(Base):
    __tablename__ = "restaurant_table_reservation"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "reservation_code", name="uq_reservation_code"),)

    id = Column(Integer, primary_key=True, index=True)

    reservation_code = Column(String(100), nullable=False, index=True)
    reservation_date = Column(Date, nullable=False, index=True)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)

    table_id = Column(Integer, ForeignKey("restaurant_table.id"), nullable=False, index=True)
    table_code = Column(String(100), nullable=False, index=True)

    floor_id = Column(Integer, ForeignKey("restaurant_floor.id"), nullable=False, index=True)
    floor_code = Column(String(100), nullable=False, index=True)

    guest_name = Column(String(100), nullable=False, index=True)
    guest_mobile = Column(String(20), nullable=False, index=True)
    guest_email = Column(String(100), nullable=True)

    no_of_guests = Column(Integer, nullable=False)

    reservation_type = Column(
        SAEnum("Walk-In", "Phone", "Online", "Hotel Guest", name="reservation_type_enum"), nullable=False, index=True
    )

    occasion = Column(String(100), nullable=True)
    special_requests = Column(String(255), nullable=True)

    reservation_status = Column(
        SAEnum("Reserved", "Checked-In", "Cancelled", "No-Show", "Completed", name="reservation_status_enum"),
        nullable=False,
        index=True,
    )

    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)

    order_id = Column(Integer, ForeignKey("restaurant_order.id"), nullable=True, index=True)
    order_number = Column(String(100), nullable=True, index=True)

    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(SAEnum(*STATUS_VALUES, name="reservation_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Waitlist
# =====================================================
class RestaurantWaitlist(Base):
    __tablename__ = "restaurant_waitlist"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "waitlist_code", name="uq_waitlist_code"),)

    id = Column(Integer, primary_key=True, index=True)

    waitlist_code = Column(String(100), nullable=False, index=True)

    guest_name = Column(String(100), nullable=False, index=True)
    guest_mobile = Column(String(20), nullable=False, index=True)
    party_size = Column(Integer, nullable=False)

    floor_id = Column(Integer, ForeignKey("restaurant_floor.id"), nullable=True, index=True)
    section = Column(String(100), nullable=True, index=True)

    wait_start_time = Column(DateTime, server_default=func.now())
    estimated_wait_minutes = Column(Integer, nullable=True)

    waitlist_status = Column(
        SAEnum("Waiting", "Notified", "Seated", "Cancelled", name="waitlist_status_enum"), nullable=False, index=True
    )

    notified_at = Column(DateTime, nullable=True)
    seated_at = Column(DateTime, nullable=True)

    table_id = Column(Integer, ForeignKey("restaurant_table.id"), nullable=True, index=True)  # filled once seated

    status = Column(SAEnum(*STATUS_VALUES, name="waitlist_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Table Merge (event log) + Merge Details (member tables)
# =====================================================
class RestaurantTableMerge(Base):
    __tablename__ = "restaurant_table_merge"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "merge_code", name="uq_merge_code"),)

    id = Column(Integer, primary_key=True, index=True)

    merge_code = Column(String(100), nullable=False, index=True)
    merged_table_name = Column(String(150), nullable=False)

    merged_by = Column(String(100), nullable=False)
    merge_datetime = Column(DateTime, server_default=func.now())
    unmerged_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)  # True while merged, False once split back apart

    status = Column(SAEnum(*STATUS_VALUES, name="table_merge_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class RestaurantTableMergeDetail(Base):
    __tablename__ = "restaurant_table_merge_detail"

    id = Column(Integer, primary_key=True, index=True)

    merge_id = Column(Integer, ForeignKey("restaurant_table_merge.id"), nullable=False, index=True)
    table_id = Column(Integer, ForeignKey("restaurant_table.id"), nullable=False, index=True)

    status = Column(SAEnum(*STATUS_VALUES, name="table_merge_detail_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Kitchen Station Master (must precede Menu* below — referenced by FK)
# =====================================================
class Kitchen(Base):
    __tablename__ = "kitchen"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "kitchen_code", name="uq_kitchen_code"),)

    id = Column(Integer, primary_key=True, index=True)

    kitchen_code = Column(String(100), nullable=False, index=True)
    kitchen_name = Column(String(100), nullable=False, index=True)
    kitchen_type = Column(SAEnum("Main", "Grill", "Dessert", name="kitchen_type_enum"), nullable=False, index=True)

    printer_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    status = Column(SAEnum(*STATUS_VALUES, name="kitchen_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Menu Category
# =====================================================
class MenuCategory(Base):
    __tablename__ = "menu_category"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "category_code", name="uq_category_code"),)

    id = Column(Integer, primary_key=True, index=True)

    category_code = Column(String(100), nullable=False, index=True)
    category_name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=False, index=True)

    display_order = Column(Integer, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="menu_category_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Menu Sub Category
# =====================================================
class MenuSubCategory(Base):
    __tablename__ = "menu_sub_category"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "sub_category_code", name="uq_sub_category_code"),)

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(Integer, ForeignKey("menu_category.id"), nullable=False, index=True)
    category_code = Column(String(100), nullable=False, index=True)

    sub_category_code = Column(String(100), nullable=False, index=True)
    sub_category_name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    display_order = Column(Integer, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="menu_sub_category_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Menu Item Master
# =====================================================
class RestaurantMenu(Base):
    __tablename__ = "restaurant_menu"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "item_code", name="uq_item_code"),)

    id = Column(Integer, primary_key=True, index=True)

    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    category_id = Column(Integer, ForeignKey("menu_category.id"), nullable=False, index=True)
    sub_category_id = Column(Integer, ForeignKey("menu_sub_category.id"), nullable=True, index=True)

    price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)

    tax_percentage = Column(Float, nullable=True)
    service_charge_applicable = Column(Boolean, nullable=False, default=False)

    preparation_time = Column(Integer, nullable=True)

    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=False, index=True)

    availability_status = Column(SAEnum("Available", "Out of Stock", name="menu_availability_status_enum"), nullable=False, index=True)

    is_veg = Column(Boolean, nullable=False, default=True)
    dietary_tags = Column(JSON, nullable=True)

    has_variants = Column(Boolean, nullable=False, default=False)

    item_image = Column(String(255), nullable=True)

    happy_hour_eligible = Column(Boolean, nullable=False, default=False)

    status = Column(SAEnum(*STATUS_VALUES, name="menu_item_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Menu Item Variant
# =====================================================
class MenuVariant(Base):
    __tablename__ = "menu_variant"
    __table_args__ = (UniqueConstraint("menu_id", "variant_name", name="uq_menu_variant_name"),)

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)

    variant_name = Column(String(50), nullable=False, index=True)  # Small | Medium | Large | Half | Full
    price = Column(Float, nullable=False)

    status = Column(SAEnum(*STATUS_VALUES, name="menu_variant_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Menu Modifier
# =====================================================
class MenuModifier(Base):
    __tablename__ = "menu_modifier"

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)

    modifier_name = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=True)

    modifier_type = Column(SAEnum("Add-on", "Remove", name="modifier_type_enum"), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="menu_modifier_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Combo / Package Deals
# =====================================================
class ComboDeal(Base):
    __tablename__ = "combo_deal"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "combo_code", name="uq_combo_code"),)

    id = Column(Integer, primary_key=True, index=True)

    combo_code = Column(String(100), nullable=False, index=True)
    combo_name = Column(String(150), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    combo_price = Column(Float, nullable=False)

    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    status = Column(SAEnum(*STATUS_VALUES, name="combo_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class ComboItem(Base):
    __tablename__ = "combo_item"
    __table_args__ = (UniqueConstraint("combo_id", "menu_id", name="uq_combo_item"),)

    id = Column(Integer, primary_key=True, index=True)

    combo_id = Column(Integer, ForeignKey("combo_deal.id"), nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)

    status = Column(SAEnum(*STATUS_VALUES, name="combo_item_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Order Items + Modifier Selections
# =====================================================
class RestaurantOrderItem(Base):
    __tablename__ = "restaurant_order_item"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("restaurant_order.id"), nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)

    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=False, index=True)

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    item_status = Column(SAEnum("Pending", "Preparing", "Ready", "Served", "Cancelled", name="order_item_status_enum"), nullable=False, index=True)

    special_instructions = Column(String(255), nullable=True)
    variant_id = Column(Integer, ForeignKey("menu_variant.id"), nullable=True)
    variant_name = Column(String(50), nullable=True)  # snapshot at order time

    status = Column(SAEnum(*STATUS_VALUES, name="order_item_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class RestaurantOrderItemModifier(Base):
    """Records which MenuModifier(s) were selected on a given order item — previously unstructured."""

    __tablename__ = "restaurant_order_item_modifier"

    id = Column(Integer, primary_key=True, index=True)

    order_item_id = Column(Integer, ForeignKey("restaurant_order_item.id"), nullable=False, index=True)
    modifier_id = Column(Integer, ForeignKey("menu_modifier.id"), nullable=False, index=True)

    modifier_name = Column(String(100), nullable=False)  # snapshot
    price = Column(Float, nullable=True)  # snapshot

    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Kitchen Order Ticket (KOT)
# =====================================================
class KitchenOrderTicket(Base):
    __tablename__ = "kitchen_order_ticket"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "kot_number", name="uq_kot_number"),)

    id = Column(Integer, primary_key=True, index=True)

    kot_number = Column(String(100), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("restaurant_order.id"), nullable=False, index=True)

    parent_kot_id = Column(Integer, ForeignKey("kitchen_order_ticket.id"), nullable=True, index=True)

    kot_type = Column(
        SAEnum("Original", "Supplementary", "Modification", "Cancellation", name="kot_type_enum"),
        nullable=False,
        default="Original",
        index=True,
    )

    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=False, index=True)

    kot_status = Column(
        SAEnum("New", "Acknowledged", "In Progress", "Completed", "Cancelled", name="kot_status_enum"), nullable=False, index=True
    )

    priority = Column(SAEnum("Normal", "High", "ASAP", name="kot_priority_enum"), nullable=True)

    print_count = Column(Integer, default=0)
    printed_by = Column(String(100), nullable=True)

    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    completed_by = Column(String(100), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    remarks = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="kot_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class KitchenOrderItem(Base):
    __tablename__ = "kitchen_order_item"

    id = Column(Integer, primary_key=True, index=True)

    kot_id = Column(Integer, ForeignKey("kitchen_order_ticket.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("restaurant_order_item.id"), nullable=False, index=True)

    preparation_status = Column(SAEnum("Pending", "Preparing", "Ready", "Cancelled", name="kot_item_prep_status_enum"), nullable=False, index=True)

    prep_start_time = Column(DateTime, nullable=True)
    prep_end_time = Column(DateTime, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="kot_item_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# KOT Modifications (add / remove / change against an already-fired KOT)
# =====================================================
class KitchenOrderModification(Base):
    __tablename__ = "kitchen_order_modification"

    id = Column(Integer, primary_key=True, index=True)

    kot_id = Column(Integer, ForeignKey("kitchen_order_ticket.id"), nullable=False, index=True)
    original_kot_item_id = Column(Integer, ForeignKey("kitchen_order_item.id"), nullable=True, index=True)

    modification_type = Column(SAEnum("Add", "Remove", "Change", name="kot_modification_type_enum"), nullable=False, index=True)
    modification_details = Column(String(255), nullable=True)

    modified_by = Column(String(100), nullable=False)
    modification_datetime = Column(DateTime, server_default=func.now())

    status = Column(SAEnum(*STATUS_VALUES, name="kot_modification_status_enum"), nullable=False, index=True, default="ACTIVE")

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Billing
# =====================================================
class RestaurantBill(Base):
    __tablename__ = "restaurant_bill"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "bill_number", name="uq_bill_number"),)

    id = Column(Integer, primary_key=True, index=True)

    bill_number = Column(String(100), nullable=False, index=True)
    bill_date = Column(Date, nullable=False, index=True)
    bill_time = Column(Time, nullable=False)

    order_id = Column(Integer, ForeignKey("restaurant_order.id"), nullable=False, index=True)
    order_number = Column(String(100), nullable=False, index=True)

    table_id = Column(Integer, ForeignKey("restaurant_table.id"), nullable=True, index=True)
    table_code = Column(String(100), nullable=True, index=True)
    room_no = Column(String(50), nullable=True, index=True)

    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=True, index=True)
    guest_name = Column(String(100), nullable=True)
    guest_mobile = Column(String(20), nullable=True, index=True)

    sub_total = Column(Float, default=0)

    cgst_percentage = Column(Float, nullable=True)
    cgst_amount = Column(Float, default=0)

    sgst_percentage = Column(Float, nullable=True)
    sgst_amount = Column(Float, default=0)

    igst_percentage = Column(Float, nullable=True)
    igst_amount = Column(Float, default=0)

    service_charge_percentage = Column(Float, nullable=True)
    service_charge_amount = Column(Float, default=0)

    discount_type = Column(SAEnum("Percentage", "Flat", name="bill_discount_type_enum"), nullable=True)
    discount_value = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    round_off = Column(Float, default=0)

    grand_total = Column(Float, nullable=False)

    bill_status = Column(SAEnum("Open", "Paid", "Cancelled", name="bill_status_enum"), nullable=False, index=True)
    payment_status = Column(SAEnum("Pending", "Partial", "Paid", name="bill_payment_status_enum"), nullable=False, index=True)

    remarks = Column(String(255), nullable=True)

    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(SAEnum(*STATUS_VALUES, name="bill_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class RestaurantBillItem(Base):
    __tablename__ = "restaurant_bill_item"

    id = Column(Integer, primary_key=True, index=True)

    bill_id = Column(Integer, ForeignKey("restaurant_bill.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("restaurant_order_item.id"), nullable=False, index=True)

    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)

    quantity = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    tax_amount = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bill_item_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Payment Method Master
# =====================================================
class PaymentMethod(Base):
    __tablename__ = "payment_method"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "method_name", name="uq_payment_method_name"),)

    id = Column(Integer, primary_key=True, index=True)

    method_name = Column(String(50), nullable=False, index=True)  # Cash | Card | UPI | Wallet | Room Posting (admin-extensible)

    status = Column(SAEnum(*STATUS_VALUES, name="payment_method_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class RestaurantBillPayment(Base):
    __tablename__ = "restaurant_bill_payment"

    id = Column(Integer, primary_key=True, index=True)

    bill_id = Column(Integer, ForeignKey("restaurant_bill.id"), nullable=False, index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_method.id"), nullable=False, index=True)

    paid_amount = Column(Float, nullable=False)
    payment_reference = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_time = Column(Time, nullable=False)

    payment_status = Column(SAEnum("Success", "Failed", "Refunded", name="bill_payment_txn_status_enum"), nullable=False, index=True)

    remarks = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bill_payment_status_lifecycle_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# RESTAURANT MANAGEMENT
# Bill Split (event log) + Split Details (resulting child bills)
# =====================================================
class RestaurantBillSplit(Base):
    __tablename__ = "restaurant_bill_split"

    id = Column(Integer, primary_key=True, index=True)

    original_bill_id = Column(Integer, ForeignKey("restaurant_bill.id"), nullable=False, index=True)

    split_type = Column(SAEnum("By Person", "By Item", "By Amount", name="bill_split_type_enum"), nullable=False)

    split_count = Column(Integer, nullable=False)
    split_datetime = Column(DateTime, server_default=func.now())

    status = Column(SAEnum(*STATUS_VALUES, name="bill_split_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class RestaurantBillSplitDetail(Base):
    __tablename__ = "restaurant_bill_split_detail"

    id = Column(Integer, primary_key=True, index=True)

    split_id = Column(Integer, ForeignKey("restaurant_bill_split.id"), nullable=False, index=True)
    child_bill_id = Column(Integer, ForeignKey("restaurant_bill.id"), nullable=False, index=True)
    split_number = Column(Integer, nullable=False)
    split_amount = Column(Float, nullable=False)

    status = Column(SAEnum(*STATUS_VALUES, name="bill_split_detail_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# INVENTORY MANAGEMENT
# Inventory Item Master
# =====================================================
class InventoryItem(Base):
    __tablename__ = "inventory_item"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "item_code", name="uq_inventory_item_code"),)

    id = Column(Integer, primary_key=True, index=True)

    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)

    category = Column(String(100), nullable=True, index=True)
    unit = Column(SAEnum("Kg", "Gram", "Litre", "ml", "Nos", name="inventory_unit_enum"), nullable=False, index=True)

    min_stock_level = Column(Float, default=0)

    is_perishable = Column(Boolean, nullable=False, default=False)

    status = Column(SAEnum(*STATUS_VALUES, name="inventory_item_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class InventoryStock(Base):
    __tablename__ = "inventory_stock"
    __table_args__ = (
        UniqueConstraint("inventory_item_id", "kitchen_id", "company_id", "branch_id", name="uq_inventory_stock_location"),
    )

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, ForeignKey("inventory_item.id"), nullable=False, index=True)
    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=True, index=True)  # Null = Main Store

    available_quantity = Column(Float, nullable=False)

    last_updated_date = Column(Date, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="inventory_stock_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class InventoryStockTransaction(Base):
    __tablename__ = "inventory_stock_transaction"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, ForeignKey("inventory_item.id"), nullable=False, index=True)
    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=True, index=True)

    transaction_type = Column(SAEnum("IN", "OUT", "ADJUSTMENT", "WASTE", name="stock_transaction_type_enum"), nullable=False, index=True)

    quantity = Column(Float, nullable=False)

    reference_type = Column(SAEnum("Purchase", "KOT", "Manual", "Transfer", name="stock_reference_type_enum"), nullable=True)
    reference_id = Column(String(100), nullable=True)  # polymorphic pointer, resolved via reference_type

    remarks = Column(String(255), nullable=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class MenuRecipe(Base):
    __tablename__ = "menu_recipe"
    __table_args__ = (UniqueConstraint("menu_id", "inventory_item_id", name="uq_menu_recipe_line"),)

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_item.id"), nullable=False, index=True)

    quantity_required = Column(Float, nullable=False)
    unit = Column(SAEnum("Kg", "Gram", "Litre", "ml", "Nos", name="recipe_unit_enum"), nullable=False)

    status = Column(SAEnum(*STATUS_VALUES, name="menu_recipe_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class InventoryPurchase(Base):
    __tablename__ = "inventory_purchase"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, ForeignKey("inventory_item.id"), nullable=False, index=True)

    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # app layer validates == quantity * unit_price

    purchase_date = Column(Date, nullable=False, index=True)
    supplier_name = Column(String(150), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="inventory_purchase_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# GUEST MANAGEMENT
# =====================================================
class Guest(Base):
    __tablename__ = "guest"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "mobile", name="uq_guest_mobile"),)

    id = Column(Integer, primary_key=True, index=True)

    guest_code = Column(String(100), unique=True, nullable=False, index=True)

    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=True, index=True)

    mobile = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True, index=True)

    guest_type = Column(SAEnum("Walk-In", "Regular", "VIP", "Hotel Guest", name="guest_type_enum"), nullable=False, index=True)

    food_preferences = Column(JSON, nullable=True)  # Veg | Non-Veg | Jain | Allergies
    special_notes = Column(String(255), nullable=True)

    loyalty_points = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="guest_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class GuestAddress(Base):
    __tablename__ = "guest_address"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=False, index=True)

    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)
    postal_code = Column(String(20), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="guest_address_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class GuestVisitHistory(Base):
    __tablename__ = "guest_visit_history"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=False, index=True)

    visit_date = Column(Date, nullable=False, index=True)

    order_id = Column(Integer, ForeignKey("restaurant_order.id"), nullable=True, index=True)
    bill_id = Column(Integer, ForeignKey("restaurant_bill.id"), nullable=True, index=True)

    visit_type = Column(
        SAEnum("Dine-In", "Takeaway", "Delivery", "Room Service", name="guest_visit_type_enum"), nullable=False, index=True
    )

    total_amount = Column(Float, nullable=True)

    rating = Column(Integer, nullable=True)
    feedback = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="guest_visit_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class GuestFeedback(Base):
    __tablename__ = "guest_feedback"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_guest_feedback_rating"),)

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("restaurant_order.id"), nullable=True, index=True)

    rating = Column(Integer, nullable=False)
    comments = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="guest_feedback_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# REPORTS & ANALYTICS
# =====================================================
class DailySalesReport(Base):
    __tablename__ = "daily_sales_report"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "report_date", name="uq_daily_sales_report_date"),)

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    total_orders = Column(Integer, default=0)
    total_bills = Column(Integer, default=0)

    total_sales = Column(Float, default=0)
    total_tax = Column(Float, default=0)
    total_discount = Column(Float, default=0)
    total_service_charge = Column(Float, default=0)
    # Payment-method breakdown lives in PaymentModeReport (FK'd to PaymentMethod)
    # instead of being hardcoded here as fixed cash/card/upi/room-posting columns.

    status = Column(SAEnum(*STATUS_VALUES, name="daily_sales_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class ItemSalesReport(Base):
    __tablename__ = "item_sales_report"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "report_date", "menu_id", name="uq_item_sales_report_line"),)

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    menu_id = Column(Integer, ForeignKey("restaurant_menu.id"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)

    category_id = Column(Integer, ForeignKey("menu_category.id"), nullable=True, index=True)
    quantity_sold = Column(Integer, default=0)

    total_amount = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="item_sales_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class CategorySalesReport(Base):
    __tablename__ = "category_sales_report"
    __table_args__ = (
        UniqueConstraint("company_id", "branch_id", "report_date", "category_id", name="uq_category_sales_report_line"),
    )

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    category_id = Column(Integer, ForeignKey("menu_category.id"), nullable=False, index=True)
    category_name = Column(String(100), nullable=False)

    total_quantity = Column(Integer, default=0)
    total_sales = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="category_sales_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class StaffPerformanceReport(Base):
    __tablename__ = "staff_performance_report"
    __table_args__ = (
        UniqueConstraint("company_id", "branch_id", "report_date", "employee_id", name="uq_staff_performance_report_line"),
    )

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    employee_id = Column(Integer, nullable=False, index=True)  # UserServices employee id, cross-service by id only
    role = Column(SAEnum("Waiter", "Chef", "Cashier", "Manager", name="staff_report_role_enum"), nullable=False, index=True)

    total_orders = Column(Integer, default=0)
    total_sales = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="staff_performance_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class KitchenPerformanceReport(Base):
    __tablename__ = "kitchen_performance_report"
    __table_args__ = (
        UniqueConstraint("company_id", "branch_id", "report_date", "kitchen_id", name="uq_kitchen_performance_report_line"),
    )

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    kitchen_id = Column(Integer, ForeignKey("kitchen.id"), nullable=False, index=True)

    total_kots = Column(Integer, default=0)
    avg_preparation_time = Column(Float, nullable=True)
    completed_kots = Column(Integer, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="kitchen_performance_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class PaymentModeReport(Base):
    __tablename__ = "payment_mode_report"
    __table_args__ = (
        UniqueConstraint("company_id", "branch_id", "report_date", "payment_method_id", name="uq_payment_mode_report_line"),
    )

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    payment_method_id = Column(Integer, ForeignKey("payment_method.id"), nullable=False, index=True)  # was free-text before

    total_amount = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="payment_mode_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# STAFF MANAGEMENT
# Restaurant Staff Assignment (shift/section/table for an existing employee)
# =====================================================
class RestaurantStaffAssignment(Base):
    __tablename__ = "restaurant_staff_assignment"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, nullable=False, index=True)  # UserServices employee id (not duplicated here)
    employee_name = Column(String(150), nullable=True)

    role = Column(SAEnum("Waiter", "Chef", "Cashier", "Manager", name="staff_role_enum"), nullable=False, index=True)

    shift_date = Column(Date, nullable=False, index=True)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=True)

    section = Column(String(100), nullable=True, index=True)
    floor_id = Column(Integer, ForeignKey("restaurant_floor.id"), nullable=True, index=True)

    sales_target = Column(Float, nullable=True)
    actual_sales = Column(Float, default=0)

    clock_in_at = Column(DateTime, nullable=True)
    clock_out_at = Column(DateTime, nullable=True)

    opening_cash_float = Column(Float, nullable=True)
    closing_cash_amount = Column(Float, nullable=True)

    shift_status = Column(
        SAEnum("Scheduled", "On Shift", "On Break", "Closed", name="staff_shift_status_enum"),
        nullable=False,
        index=True,
        default="Scheduled",
    )

    status = Column(SAEnum(*STATUS_VALUES, name="staff_assignment_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# SETTINGS & CONFIGURATION
# Key/value business settings (operating hours, tax, printers, numbering formats...)
# =====================================================
class RestaurantSettings(Base):
    __tablename__ = "restaurant_settings"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "setting_key", name="uq_setting_key"),)

    id = Column(Integer, primary_key=True, index=True)

    setting_key = Column(String(100), nullable=False, index=True)
    setting_value = Column(String(255), nullable=True)

    setting_group = Column(
        SAEnum(
            "OperatingHours", "Tax", "ServiceCharge", "Printer", "Numbering", "Discount", "Language", name="settings_group_enum"
        ),
        nullable=True,
        index=True,
    )

    description = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="settings_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


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


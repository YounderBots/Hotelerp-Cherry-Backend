from configs import BaseConfig
import os
import uuid
from sqlalchemy.ext.declarative import declarative_base
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

STATUS_VALUES = ("ACTIVE", "INACTIVE")


# =====================================================
# BAR MANAGEMENT
# Floor / Table (POS seating)
# =====================================================
class BarFloor(Base):
    __tablename__ = "bar_floor"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "floor_code", name="uq_bar_floor_code"),)

    id = Column(Integer, primary_key=True, index=True)

    floor_code = Column(String(100), nullable=False, index=True)
    floor_name = Column(String(100), nullable=False, index=True)
    floor_number = Column(Integer, nullable=False, index=True)

    description = Column(String(255), nullable=True)
    total_tables = Column(Integer, nullable=True)
    total_capacity = Column(Integer, nullable=True)
    layout_json = Column(JSON, nullable=True)

    color_code = Column(String(20), nullable=True)
    is_open = Column(Boolean, nullable=False, default=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_floor_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarTable(Base):
    __tablename__ = "bar_table"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "table_code", name="uq_bar_table_code"),)

    id = Column(Integer, primary_key=True, index=True)

    table_code = Column(String(100), nullable=False, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    table_number = Column(Integer, nullable=False, index=True)

    floor_id = Column(Integer, ForeignKey("bar_floor.id"), nullable=False, index=True)
    floor_code = Column(String(100), nullable=False, index=True)

    table_type = Column(SAEnum("Counter", "Table", "Booth", "VIP Lounge", name="bar_table_type_enum"), nullable=False, index=True)
    seating_capacity = Column(Integer, nullable=False)

    current_order_id = Column(Integer, nullable=True, index=True)  # bar_order.id — no FK: circular with BarOrder.table_id
    server_id = Column(String(100), nullable=True, index=True)
    server_name = Column(String(100), nullable=True)

    table_status = Column(
        SAEnum("Available", "Occupied", "Reserved", "Cleaning", "Blocked", name="bar_table_status_enum"),
        nullable=False,
        index=True,
    )

    status = Column(SAEnum(*STATUS_VALUES, name="bar_table_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Bar Station Master (bar counters KOTs/BOTs route to)
# =====================================================
class BarStation(Base):
    __tablename__ = "bar_station"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "station_code", name="uq_bar_station_code"),)

    id = Column(Integer, primary_key=True, index=True)

    station_code = Column(String(100), nullable=False, index=True)
    station_name = Column(String(100), nullable=False, index=True)

    printer_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_station_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Menu (drinks) Category / Sub Category
# =====================================================
class BarMenuCategory(Base):
    __tablename__ = "bar_menu_category"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "category_code", name="uq_bar_category_code"),)

    id = Column(Integer, primary_key=True, index=True)

    category_code = Column(String(100), nullable=False, index=True)
    category_name = Column(String(100), nullable=False, index=True)  # Beer | Wine | Spirits | Cocktails | Mocktails | Bar Snacks
    description = Column(String(255), nullable=True)

    station_id = Column(Integer, ForeignKey("bar_station.id"), nullable=False, index=True)

    display_order = Column(Integer, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_menu_category_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarMenuSubCategory(Base):
    __tablename__ = "bar_menu_sub_category"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "sub_category_code", name="uq_bar_sub_category_code"),)

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(Integer, ForeignKey("bar_menu_category.id"), nullable=False, index=True)
    category_code = Column(String(100), nullable=False, index=True)

    sub_category_code = Column(String(100), nullable=False, index=True)
    sub_category_name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    display_order = Column(Integer, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_menu_sub_category_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Menu Item (drink) Master
# =====================================================
class BarMenuItem(Base):
    __tablename__ = "bar_menu_item"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "item_code", name="uq_bar_item_code"),)

    id = Column(Integer, primary_key=True, index=True)

    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    category_id = Column(Integer, ForeignKey("bar_menu_category.id"), nullable=False, index=True)
    sub_category_id = Column(Integer, ForeignKey("bar_menu_sub_category.id"), nullable=True, index=True)

    price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)

    tax_percentage = Column(Float, nullable=True)
    service_charge_applicable = Column(Boolean, nullable=False, default=False)

    preparation_time = Column(Integer, nullable=True)

    station_id = Column(Integer, ForeignKey("bar_station.id"), nullable=False, index=True)

    availability_status = Column(SAEnum("Available", "Out of Stock", name="bar_menu_availability_status_enum"), nullable=False, index=True)

    dietary_tags = Column(JSON, nullable=True)

    has_variants = Column(Boolean, nullable=False, default=False)

    item_image = Column(String(255), nullable=True)

    happy_hour_eligible = Column(Boolean, nullable=False, default=False)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_menu_item_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarMenuVariant(Base):
    """Peg sizes (30ml / 60ml / 90ml), bottle vs glass, etc."""

    __tablename__ = "bar_menu_variant"
    __table_args__ = (UniqueConstraint("menu_id", "variant_name", name="uq_bar_menu_variant_name"),)

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, ForeignKey("bar_menu_item.id"), nullable=False, index=True)

    variant_name = Column(String(50), nullable=False, index=True)  # 30ml | 60ml | 90ml | Glass | Bottle
    price = Column(Float, nullable=False)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_menu_variant_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarMenuModifier(Base):
    __tablename__ = "bar_menu_modifier"

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, ForeignKey("bar_menu_item.id"), nullable=False, index=True)

    modifier_name = Column(String(100), nullable=False, index=True)  # e.g. "On the Rocks", "Extra Shot"
    price = Column(Float, nullable=True)

    modifier_type = Column(SAEnum("Add-on", "Remove", name="bar_modifier_type_enum"), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_menu_modifier_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Orders / Order Items + Modifier Selections
# =====================================================
class BarOrder(Base):
    __tablename__ = "bar_order"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "order_number", name="uq_bar_order_number"),)

    id = Column(Integer, primary_key=True, index=True)

    order_number = Column(String(100), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    order_time = Column(Time, nullable=False)

    order_type = Column(SAEnum("At Table", "At Counter", "Takeaway", name="bar_order_type_enum"), nullable=False, index=True)

    table_id = Column(Integer, ForeignKey("bar_table.id"), nullable=True, index=True)
    table_code = Column(String(100), nullable=True, index=True)

    floor_id = Column(Integer, ForeignKey("bar_floor.id"), nullable=True, index=True)
    floor_code = Column(String(100), nullable=True, index=True)

    guest_id = Column(Integer, ForeignKey("bar_guest.id"), nullable=True, index=True)
    guest_name = Column(String(100), nullable=True)
    guest_mobile = Column(String(20), nullable=True, index=True)

    no_of_guests = Column(Integer, nullable=True)

    server_id = Column(String(100), nullable=True, index=True)
    server_name = Column(String(100), nullable=True)

    order_status = Column(
        SAEnum("New", "In Progress", "Ready", "Served", "Completed", "Cancelled", name="bar_order_status_enum"),
        nullable=False,
        index=True,
    )
    payment_status = Column(SAEnum("Pending", "Partial", "Paid", name="bar_order_payment_status_enum"), nullable=False, index=True)

    sub_total = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    service_charge = Column(Float, default=0)

    discount_type = Column(SAEnum("Percentage", "Flat", name="bar_order_discount_type_enum"), nullable=True)
    discount_value = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    grand_total = Column(Float, default=0)

    special_notes = Column(String(255), nullable=True)

    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(SAEnum(*STATUS_VALUES, name="bar_order_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarOrderItem(Base):
    __tablename__ = "bar_order_item"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("bar_order.id"), nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("bar_menu_item.id"), nullable=False, index=True)

    station_id = Column(Integer, ForeignKey("bar_station.id"), nullable=False, index=True)

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    item_status = Column(SAEnum("Pending", "Preparing", "Ready", "Served", "Cancelled", name="bar_order_item_status_enum"), nullable=False, index=True)

    special_instructions = Column(String(255), nullable=True)
    variant_id = Column(Integer, ForeignKey("bar_menu_variant.id"), nullable=True)
    variant_name = Column(String(50), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_order_item_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarOrderItemModifier(Base):
    __tablename__ = "bar_order_item_modifier"

    id = Column(Integer, primary_key=True, index=True)

    order_item_id = Column(Integer, ForeignKey("bar_order_item.id"), nullable=False, index=True)
    modifier_id = Column(Integer, ForeignKey("bar_menu_modifier.id"), nullable=False, index=True)

    modifier_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Bar Order Ticket (BOT)
# =====================================================
class BarOrderTicket(Base):
    __tablename__ = "bar_order_ticket"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "bot_number", name="uq_bot_number"),)

    id = Column(Integer, primary_key=True, index=True)

    bot_number = Column(String(100), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("bar_order.id"), nullable=False, index=True)

    parent_bot_id = Column(Integer, ForeignKey("bar_order_ticket.id"), nullable=True, index=True)

    bot_type = Column(
        SAEnum("Original", "Supplementary", "Modification", "Cancellation", name="bot_type_enum"),
        nullable=False,
        default="Original",
        index=True,
    )

    station_id = Column(Integer, ForeignKey("bar_station.id"), nullable=False, index=True)

    bot_status = Column(
        SAEnum("New", "Acknowledged", "In Progress", "Completed", "Cancelled", name="bot_status_enum"), nullable=False, index=True
    )

    priority = Column(SAEnum("Normal", "High", "ASAP", name="bot_priority_enum"), nullable=True)

    print_count = Column(Integer, default=0)
    printed_by = Column(String(100), nullable=True)

    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    completed_by = Column(String(100), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    remarks = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bot_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarOrderTicketItem(Base):
    __tablename__ = "bar_order_ticket_item"

    id = Column(Integer, primary_key=True, index=True)

    bot_id = Column(Integer, ForeignKey("bar_order_ticket.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("bar_order_item.id"), nullable=False, index=True)

    preparation_status = Column(SAEnum("Pending", "Preparing", "Ready", "Cancelled", name="bot_item_prep_status_enum"), nullable=False, index=True)

    prep_start_time = Column(DateTime, nullable=True)
    prep_end_time = Column(DateTime, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bot_item_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Billing
# =====================================================
class BarBill(Base):
    __tablename__ = "bar_bill"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "bill_number", name="uq_bar_bill_number"),)

    id = Column(Integer, primary_key=True, index=True)

    bill_number = Column(String(100), nullable=False, index=True)
    bill_date = Column(Date, nullable=False, index=True)
    bill_time = Column(Time, nullable=False)

    order_id = Column(Integer, ForeignKey("bar_order.id"), nullable=False, index=True)
    order_number = Column(String(100), nullable=False, index=True)

    table_id = Column(Integer, ForeignKey("bar_table.id"), nullable=True, index=True)
    table_code = Column(String(100), nullable=True, index=True)

    guest_id = Column(Integer, ForeignKey("bar_guest.id"), nullable=True, index=True)
    guest_name = Column(String(100), nullable=True)
    guest_mobile = Column(String(20), nullable=True, index=True)

    sub_total = Column(Float, default=0)

    cgst_percentage = Column(Float, nullable=True)
    cgst_amount = Column(Float, default=0)

    sgst_percentage = Column(Float, nullable=True)
    sgst_amount = Column(Float, default=0)

    service_charge_percentage = Column(Float, nullable=True)
    service_charge_amount = Column(Float, default=0)

    discount_type = Column(SAEnum("Percentage", "Flat", name="bar_bill_discount_type_enum"), nullable=True)
    discount_value = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    round_off = Column(Float, default=0)

    grand_total = Column(Float, nullable=False)

    bill_status = Column(SAEnum("Open", "Paid", "Cancelled", name="bar_bill_status_enum"), nullable=False, index=True)
    payment_status = Column(SAEnum("Pending", "Partial", "Paid", name="bar_bill_payment_status_enum"), nullable=False, index=True)

    remarks = Column(String(255), nullable=True)

    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(SAEnum(*STATUS_VALUES, name="bar_bill_lifecycle_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarBillItem(Base):
    __tablename__ = "bar_bill_item"

    id = Column(Integer, primary_key=True, index=True)

    bill_id = Column(Integer, ForeignKey("bar_bill.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("bar_order_item.id"), nullable=False, index=True)

    menu_id = Column(Integer, ForeignKey("bar_menu_item.id"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)

    quantity = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    tax_amount = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_bill_item_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarPaymentMethod(Base):
    __tablename__ = "bar_payment_method"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "method_name", name="uq_bar_payment_method_name"),)

    id = Column(Integer, primary_key=True, index=True)

    method_name = Column(String(50), nullable=False, index=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_payment_method_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarBillPayment(Base):
    __tablename__ = "bar_bill_payment"

    id = Column(Integer, primary_key=True, index=True)

    bill_id = Column(Integer, ForeignKey("bar_bill.id"), nullable=False, index=True)
    payment_method_id = Column(Integer, ForeignKey("bar_payment_method.id"), nullable=False, index=True)

    paid_amount = Column(Float, nullable=False)
    payment_reference = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_time = Column(Time, nullable=False)

    payment_status = Column(SAEnum("Success", "Failed", "Refunded", name="bar_bill_payment_txn_status_enum"), nullable=False, index=True)

    remarks = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_bill_payment_status_lifecycle_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarBillSplit(Base):
    __tablename__ = "bar_bill_split"

    id = Column(Integer, primary_key=True, index=True)

    original_bill_id = Column(Integer, ForeignKey("bar_bill.id"), nullable=False, index=True)

    split_type = Column(SAEnum("By Person", "By Item", "By Amount", name="bar_bill_split_type_enum"), nullable=False)

    split_count = Column(Integer, nullable=False)
    split_datetime = Column(DateTime, server_default=func.now())

    status = Column(SAEnum(*STATUS_VALUES, name="bar_bill_split_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarBillSplitDetail(Base):
    __tablename__ = "bar_bill_split_detail"

    id = Column(Integer, primary_key=True, index=True)

    split_id = Column(Integer, ForeignKey("bar_bill_split.id"), nullable=False, index=True)
    child_bill_id = Column(Integer, ForeignKey("bar_bill.id"), nullable=False, index=True)
    split_number = Column(Integer, nullable=False)
    split_amount = Column(Float, nullable=False)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_bill_split_detail_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Inventory (liquor / bar stock)
# =====================================================
class BarInventoryItem(Base):
    __tablename__ = "bar_inventory_item"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "item_code", name="uq_bar_inventory_item_code"),)

    id = Column(Integer, primary_key=True, index=True)

    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)

    category = Column(String(100), nullable=True, index=True)  # Spirits | Wine | Beer | Mixers | Garnish
    unit = Column(SAEnum("Bottle", "Litre", "ml", "Can", "Nos", name="bar_inventory_unit_enum"), nullable=False, index=True)

    min_stock_level = Column(Float, default=0)

    is_perishable = Column(Boolean, nullable=False, default=False)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_inventory_item_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarInventoryStock(Base):
    __tablename__ = "bar_inventory_stock"
    __table_args__ = (
        UniqueConstraint("inventory_item_id", "station_id", "company_id", "branch_id", name="uq_bar_inventory_stock_location"),
    )

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, ForeignKey("bar_inventory_item.id"), nullable=False, index=True)
    station_id = Column(Integer, ForeignKey("bar_station.id"), nullable=True, index=True)  # Null = Main Store

    available_quantity = Column(Float, nullable=False)

    last_updated_date = Column(Date, nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_inventory_stock_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarInventoryStockTransaction(Base):
    __tablename__ = "bar_inventory_stock_transaction"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, ForeignKey("bar_inventory_item.id"), nullable=False, index=True)
    station_id = Column(Integer, ForeignKey("bar_station.id"), nullable=True, index=True)

    transaction_type = Column(SAEnum("IN", "OUT", "ADJUSTMENT", "WASTE", name="bar_stock_transaction_type_enum"), nullable=False, index=True)

    quantity = Column(Float, nullable=False)

    reference_type = Column(SAEnum("Purchase", "BOT", "Manual", "Transfer", name="bar_stock_reference_type_enum"), nullable=True)
    reference_id = Column(String(100), nullable=True)

    remarks = Column(String(255), nullable=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarRecipe(Base):
    __tablename__ = "bar_recipe"
    __table_args__ = (UniqueConstraint("menu_id", "inventory_item_id", name="uq_bar_recipe_line"),)

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, ForeignKey("bar_menu_item.id"), nullable=False, index=True)
    inventory_item_id = Column(Integer, ForeignKey("bar_inventory_item.id"), nullable=False, index=True)

    quantity_required = Column(Float, nullable=False)
    unit = Column(SAEnum("Bottle", "Litre", "ml", "Can", "Nos", name="bar_recipe_unit_enum"), nullable=False)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_recipe_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarInventoryPurchase(Base):
    __tablename__ = "bar_inventory_purchase"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, ForeignKey("bar_inventory_item.id"), nullable=False, index=True)

    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    purchase_date = Column(Date, nullable=False, index=True)
    supplier_name = Column(String(150), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_inventory_purchase_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Guest / CRM (local to this service — mirrors the existing
# Hotel/Restaurant precedent of each keeping its own guest table)
# =====================================================
class BarGuest(Base):
    __tablename__ = "bar_guest"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "mobile", name="uq_bar_guest_mobile"),)

    id = Column(Integer, primary_key=True, index=True)

    guest_code = Column(String(100), unique=True, nullable=False, index=True)

    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=True, index=True)

    mobile = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True, index=True)

    guest_type = Column(SAEnum("Walk-In", "Regular", "VIP", "Hotel Guest", name="bar_guest_type_enum"), nullable=False, index=True)

    special_notes = Column(String(255), nullable=True)

    loyalty_points = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_guest_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarGuestAddress(Base):
    __tablename__ = "bar_guest_address"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, ForeignKey("bar_guest.id"), nullable=False, index=True)

    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)
    postal_code = Column(String(20), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_guest_address_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarGuestVisitHistory(Base):
    __tablename__ = "bar_guest_visit_history"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, ForeignKey("bar_guest.id"), nullable=False, index=True)

    visit_date = Column(Date, nullable=False, index=True)

    order_id = Column(Integer, ForeignKey("bar_order.id"), nullable=True, index=True)
    bill_id = Column(Integer, ForeignKey("bar_bill.id"), nullable=True, index=True)

    visit_type = Column(SAEnum("At Table", "At Counter", "Takeaway", name="bar_guest_visit_type_enum"), nullable=False, index=True)

    total_amount = Column(Float, nullable=True)

    rating = Column(Integer, nullable=True)
    feedback = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_guest_visit_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarGuestFeedback(Base):
    __tablename__ = "bar_guest_feedback"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_bar_guest_feedback_rating"),)

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, ForeignKey("bar_guest.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("bar_order.id"), nullable=True, index=True)

    rating = Column(Integer, nullable=False)
    comments = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_guest_feedback_status_enum"), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# BAR MANAGEMENT
# Staff Assignment (shift/section/table for an existing UserServices employee)
# =====================================================
class BarStaffAssignment(Base):
    __tablename__ = "bar_staff_assignment"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, nullable=False, index=True)  # UserServices employee id (cross-service by id only)
    employee_name = Column(String(150), nullable=True)

    role = Column(SAEnum("Bartender", "Cashier", "Manager", name="bar_staff_role_enum"), nullable=False, index=True)

    shift_date = Column(Date, nullable=False, index=True)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=True)

    floor_id = Column(Integer, ForeignKey("bar_floor.id"), nullable=True, index=True)

    sales_target = Column(Float, nullable=True)
    actual_sales = Column(Float, default=0)

    clock_in_at = Column(DateTime, nullable=True)
    clock_out_at = Column(DateTime, nullable=True)

    opening_cash_float = Column(Float, nullable=True)
    closing_cash_amount = Column(Float, nullable=True)

    shift_status = Column(
        SAEnum("Scheduled", "On Shift", "On Break", "Closed", name="bar_staff_shift_status_enum"),
        nullable=False,
        index=True,
        default="Scheduled",
    )

    status = Column(SAEnum(*STATUS_VALUES, name="bar_staff_assignment_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# REPORTS & ANALYTICS
# =====================================================
class BarDailySalesReport(Base):
    __tablename__ = "bar_daily_sales_report"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "report_date", name="uq_bar_daily_sales_report_date"),)

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    total_orders = Column(Integer, default=0)
    total_bills = Column(Integer, default=0)

    total_sales = Column(Float, default=0)
    total_tax = Column(Float, default=0)
    total_discount = Column(Float, default=0)
    total_service_charge = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_daily_sales_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarItemSalesReport(Base):
    __tablename__ = "bar_item_sales_report"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "report_date", "menu_id", name="uq_bar_item_sales_report_line"),)

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    menu_id = Column(Integer, ForeignKey("bar_menu_item.id"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)

    category_id = Column(Integer, ForeignKey("bar_menu_category.id"), nullable=True, index=True)
    quantity_sold = Column(Integer, default=0)

    total_amount = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_item_sales_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarPaymentModeReport(Base):
    __tablename__ = "bar_payment_mode_report"
    __table_args__ = (
        UniqueConstraint("company_id", "branch_id", "report_date", "payment_method_id", name="uq_bar_payment_mode_report_line"),
    )

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    payment_method_id = Column(Integer, ForeignKey("bar_payment_method.id"), nullable=False, index=True)

    total_amount = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_payment_mode_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


class BarStaffPerformanceReport(Base):
    __tablename__ = "bar_staff_performance_report"
    __table_args__ = (
        UniqueConstraint("company_id", "branch_id", "report_date", "employee_id", name="uq_bar_staff_performance_report_line"),
    )

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    employee_id = Column(Integer, nullable=False, index=True)
    role = Column(SAEnum("Bartender", "Cashier", "Manager", name="bar_staff_report_role_enum"), nullable=False, index=True)

    total_orders = Column(Integer, default=0)
    total_sales = Column(Float, default=0)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_staff_performance_report_status_enum"), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)
    branch_id = Column(String(100), nullable=False, index=True, default="MAIN")


# =====================================================
# SETTINGS & CONFIGURATION
# =====================================================
class BarSettings(Base):
    __tablename__ = "bar_settings"
    __table_args__ = (UniqueConstraint("company_id", "branch_id", "setting_key", name="uq_bar_setting_key"),)

    id = Column(Integer, primary_key=True, index=True)

    setting_key = Column(String(100), nullable=False, index=True)
    setting_value = Column(String(255), nullable=True)

    setting_group = Column(
        SAEnum("OperatingHours", "Tax", "ServiceCharge", "Printer", "Numbering", "Discount", "Language", name="bar_settings_group_enum"),
        nullable=True,
        index=True,
    )

    description = Column(String(255), nullable=True)

    status = Column(SAEnum(*STATUS_VALUES, name="bar_settings_status_enum"), nullable=False, index=True, default="ACTIVE")
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


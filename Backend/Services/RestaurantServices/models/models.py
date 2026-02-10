import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import JSON, Column, Date, Integer, String, DateTime, Float, Time, func
from models import engine

Base = declarative_base()

# =====================================================
# RESTAURANT MANAGEMENT
# Floor Master
# =====================================================
class RestaurantFloor(Base):
    __tablename__ = "restaurant_floor"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Floor Reference ----------------
    floor_code = Column(String(100), unique=True, nullable=False, index=True)
    floor_name = Column(String(100), nullable=False, index=True)
    floor_number = Column(Integer, nullable=False, index=True)

    # ---------------- Floor Details ----------------
    floor_type = Column(String(50), nullable=False, index=True)  
    # Restaurant | Bar | Banquet | Outdoor

    description = Column(String(255), nullable=True)

    # ---------------- Capacity & Layout ----------------
    total_tables = Column(Integer, nullable=True)
    total_capacity = Column(Integer, nullable=True)

    layout_json = Column(JSON, nullable=True)  
    # Stores table positions for visual floor layout

    # ---------------- UI & Operational Status ----------------
    color_code = Column(String(20), nullable=True)     # UI color
    is_open = Column(String(10), nullable=False, index=True)  
    # Yes | No

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Table Master
# =====================================================
class RestaurantTable(Base):
    __tablename__ = "restaurant_table"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Table Reference ----------------
    table_code = Column(String(100), unique=True, nullable=False, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    table_number = Column(Integer, nullable=False, index=True)

    # ---------------- Floor Mapping ----------------
    floor_id = Column(Integer, nullable=False, index=True)       # restaurant_floor.id
    floor_code = Column(String(100), nullable=False, index=True)

    # ---------------- Table Details ----------------
    table_type = Column(String(50), nullable=False, index=True)
    # Standard | VIP | Private | Bar Counter

    seating_capacity = Column(Integer, nullable=False)

    section = Column(String(100), nullable=True, index=True)
    # Restaurant | Bar | Outdoor | Banquet

    # ---------------- Order & Service ----------------
    current_order_id = Column(String(100), nullable=True, index=True)
    server_id = Column(String(100), nullable=True, index=True)
    server_name = Column(String(100), nullable=True)

    # ---------------- Layout & UI ----------------
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    shape = Column(String(50), nullable=True)        # Circle | Square | Rectangle
    color_code = Column(String(20), nullable=True)

    # ---------------- Table Status ----------------
    table_status = Column(String(50), nullable=False, index=True)
    # Available | Occupied | Reserved | Cleaning | Blocked

    is_mergeable = Column(String(10), nullable=False, default="No")  
    # Yes | No

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Order Management
# =====================================================
class RestaurantOrder(Base):
    __tablename__ = "restaurant_order"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Order Reference ----------------
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    order_time = Column(Time, nullable=False)

    # ---------------- Order Type ----------------
    order_type = Column(String(50), nullable=False, index=True)
    # Dine-In | Takeaway | Delivery | Room Service

    # ---------------- Table / Room Mapping ----------------
    table_id = Column(Integer, nullable=True, index=True)     # restaurant_table.id
    table_code = Column(String(100), nullable=True, index=True)
    room_no = Column(String(50), nullable=True, index=True)   # for room service

    floor_id = Column(Integer, nullable=True, index=True)
    floor_code = Column(String(100), nullable=True, index=True)

    # ---------------- Guest Details ----------------
    guest_name = Column(String(100), nullable=True)
    guest_mobile = Column(String(20), nullable=True, index=True)

    no_of_guests = Column(Integer, nullable=True)

    # ---------------- Staff ----------------
    server_id = Column(String(100), nullable=True, index=True)
    server_name = Column(String(100), nullable=True)

    # ---------------- Order Status ----------------
    order_status = Column(String(50), nullable=False, index=True)
    # New | In Progress | Ready | Served | Completed | Cancelled

    payment_status = Column(String(50), nullable=False, index=True)
    # Pending | Partial | Paid

    # ---------------- Amount Summary ----------------
    sub_total = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    service_charge = Column(Float, default=0)

    discount_type = Column(String(50), nullable=True)
    discount_value = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    grand_total = Column(Float, default=0)

    # ---------------- Special Instructions ----------------
    special_notes = Column(String(255), nullable=True)

    estimated_prep_time = Column(Integer, nullable=True)   # in minutes

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Table Reservation
# =====================================================
class RestaurantTableReservation(Base):
    __tablename__ = "restaurant_table_reservation"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Reservation Reference ----------------
    reservation_code = Column(String(100), unique=True, nullable=False, index=True)
    reservation_date = Column(Date, nullable=False, index=True)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)

    # ---------------- Table & Floor Mapping ----------------
    table_id = Column(Integer, nullable=False, index=True)       # restaurant_table.id
    table_code = Column(String(100), nullable=False, index=True)

    floor_id = Column(Integer, nullable=False, index=True)
    floor_code = Column(String(100), nullable=False, index=True)

    # ---------------- Guest Details ----------------
    guest_name = Column(String(100), nullable=False, index=True)
    guest_mobile = Column(String(20), nullable=False, index=True)
    guest_email = Column(String(100), nullable=True)

    no_of_guests = Column(Integer, nullable=False)

    # ---------------- Reservation Details ----------------
    reservation_type = Column(String(50), nullable=False, index=True)
    # Walk-In | Phone | Online | Hotel Guest

    occasion = Column(String(100), nullable=True)
    special_requests = Column(String(255), nullable=True)

    # ---------------- Status Handling ----------------
    reservation_status = Column(String(50), nullable=False, index=True)
    # Reserved | Checked-In | Cancelled | No-Show | Completed

    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)

    # ---------------- Order Mapping ----------------
    order_id = Column(Integer, nullable=True, index=True)       # restaurant_order.id
    order_number = Column(String(100), nullable=True, index=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Menu Category
# =====================================================
class MenuCategory(Base):
    __tablename__ = "menu_category"

    id = Column(Integer, primary_key=True, index=True)

    category_code = Column(String(100), unique=True, nullable=False, index=True)
    category_name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    kitchen_section = Column(String(100), nullable=False, index=True)
    # Main Kitchen | Grill | Dessert | Bar

    display_order = Column(Integer, nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Menu Sub Category
# =====================================================
class MenuSubCategory(Base):
    __tablename__ = "menu_sub_category"

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(Integer, nullable=False, index=True)   # menu_category.id
    category_code = Column(String(100), nullable=False, index=True)

    sub_category_code = Column(String(100), unique=True, nullable=False, index=True)
    sub_category_name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    display_order = Column(Integer, nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Menu Item Master
# =====================================================
class RestaurantMenu(Base):
    __tablename__ = "restaurant_menu"

    id = Column(Integer, primary_key=True, index=True)

    item_code = Column(String(100), unique=True, nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    category_id = Column(Integer, nullable=False, index=True)
    sub_category_id = Column(Integer, nullable=True, index=True)

    price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)

    tax_percentage = Column(Float, nullable=True)

    service_charge_applicable = Column(String(10), nullable=False, default="No")
    # Yes | No

    preparation_time = Column(Integer, nullable=True)

    kitchen_section = Column(String(100), nullable=False, index=True)

    availability_status = Column(String(50), nullable=False, index=True)
    # Available | Out of Stock

    is_veg = Column(String(10), nullable=False, default="Yes")
    dietary_tags = Column(JSON, nullable=True)

    has_variants = Column(String(10), nullable=False, default="No")

    item_image = Column(String(255), nullable=True)

    happy_hour_eligible = Column(String(10), nullable=False, default="No")

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Menu Item Variant
# =====================================================
class MenuVariant(Base):
    __tablename__ = "menu_variant"

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, nullable=False, index=True)   # restaurant_menu.id

    variant_name = Column(String(50), nullable=False, index=True)
    # Small | Medium | Large | Half | Full

    price = Column(Float, nullable=False)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Menu Modifier
# =====================================================
class MenuModifier(Base):
    __tablename__ = "menu_modifier"

    id = Column(Integer, primary_key=True, index=True)

    modifier_name = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Menu Recipe Mapping
# =====================================================
class MenuRecipe(Base):
    __tablename__ = "menu_recipe"

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, nullable=False, index=True)

    ingredients = Column(JSON, nullable=False)
    # [{ingredient_id, quantity, unit}]

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

class Kitchen(Base):
    __tablename__ = "kitchen"

    id = Column(Integer, primary_key=True, index=True)

    kitchen_code = Column(String(100), unique=True, nullable=False, index=True)
    kitchen_name = Column(String(100), nullable=False, index=True)
    kitchen_type = Column(String(50), nullable=False, index=True)
    # Main | Grill | Tandoor | Bar

    printer_name = Column(String(100), nullable=True)
    is_active = Column(String(10), nullable=False, default="Yes")

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

class RestaurantOrderItem(Base):
    __tablename__ = "restaurant_order_item"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False, index=True)
    menu_id = Column(Integer, nullable=False, index=True)

    kitchen_id = Column(Integer, nullable=False, index=True)

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    item_status = Column(String(50), nullable=False, index=True)
    # Pending | Preparing | Ready | Served

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

class KitchenOrderTicket(Base):
    __tablename__ = "kitchen_order_ticket"

    id = Column(Integer, primary_key=True, index=True)

    kot_number = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(Integer, nullable=False, index=True)

    kitchen_id = Column(Integer, nullable=False, index=True)

    kot_status = Column(String(50), nullable=False, index=True)
    # New | In Progress | Completed

    priority = Column(String(20), nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=False, index=True)

class KitchenOrderItem(Base):
    __tablename__ = "kitchen_order_item"

    id = Column(Integer, primary_key=True, index=True)

    kot_id = Column(Integer, nullable=False, index=True)
    order_item_id = Column(Integer, nullable=False, index=True)

    preparation_status = Column(String(50), nullable=False, index=True)
    # Pending | Preparing | Ready

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())

# =====================================================
# RESTAURANT MANAGEMENT
# Billing
# =====================================================
class RestaurantBill(Base):
    __tablename__ = "restaurant_bill"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Bill Reference ----------------
    bill_number = Column(String(100), unique=True, nullable=False, index=True)
    bill_date = Column(Date, nullable=False, index=True)
    bill_time = Column(Time, nullable=False)

    # ---------------- Order Mapping ----------------
    order_id = Column(Integer, nullable=False, index=True)
    order_number = Column(String(100), nullable=False, index=True)

    table_id = Column(Integer, nullable=True, index=True)
    table_code = Column(String(100), nullable=True, index=True)
    room_no = Column(String(50), nullable=True, index=True)

    # ---------------- Guest Details ----------------
    guest_name = Column(String(100), nullable=True)
    guest_mobile = Column(String(20), nullable=True, index=True)

    # ---------------- Amount Summary ----------------
    sub_total = Column(Float, default=0)

    cgst_percentage = Column(Float, nullable=True)
    cgst_amount = Column(Float, default=0)

    sgst_percentage = Column(Float, nullable=True)
    sgst_amount = Column(Float, default=0)

    igst_percentage = Column(Float, nullable=True)
    igst_amount = Column(Float, default=0)

    service_charge_percentage = Column(Float, nullable=True)
    service_charge_amount = Column(Float, default=0)

    discount_type = Column(String(50), nullable=True)
    discount_value = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    round_off = Column(Float, default=0)

    grand_total = Column(Float, nullable=False)

    # ---------------- Bill Status ----------------
    bill_status = Column(String(50), nullable=False, index=True)
    # Open | Paid | Cancelled

    payment_status = Column(String(50), nullable=False, index=True)
    # Pending | Partial | Paid

    remarks = Column(String(255), nullable=True)

    # ---------------- System Fields ----------------
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Bill Items
# =====================================================
class RestaurantBillItem(Base):
    __tablename__ = "restaurant_bill_item"

    id = Column(Integer, primary_key=True, index=True)

    bill_id = Column(Integer, nullable=False, index=True)
    order_item_id = Column(Integer, nullable=False, index=True)

    menu_id = Column(Integer, nullable=False, index=True)
    item_name = Column(String(150), nullable=False)

    quantity = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    tax_amount = Column(Float, default=0)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())

# =====================================================
# RESTAURANT MANAGEMENT
# Payment Method Master
# =====================================================
class PaymentMethod(Base):
    __tablename__ = "payment_method"

    id = Column(Integer, primary_key=True, index=True)

    method_name = Column(String(50), nullable=False, index=True)
    # Cash | Card | UPI | Wallet | Room Posting

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# RESTAURANT MANAGEMENT
# Bill Payments
# =====================================================
class RestaurantBillPayment(Base):
    __tablename__ = "restaurant_bill_payment"

    id = Column(Integer, primary_key=True, index=True)

    bill_id = Column(Integer, nullable=False, index=True)
    payment_method_id = Column(Integer, nullable=False, index=True)

    paid_amount = Column(Float, nullable=False)
    payment_reference = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_time = Column(Time, nullable=False)

    payment_status = Column(String(50), nullable=False, index=True)
    # Success | Failed | Refunded

    remarks = Column(String(255), nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# INVENTORY MANAGEMENT
# Inventory Item Master
# =====================================================
class InventoryItem(Base):
    __tablename__ = "inventory_item"

    id = Column(Integer, primary_key=True, index=True)

    item_code = Column(String(100), unique=True, nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)

    category = Column(String(100), nullable=True, index=True)
    unit = Column(String(50), nullable=False, index=True)
    # Kg | Gram | Litre | ml | Nos

    min_stock_level = Column(Float, default=0)

    is_perishable = Column(String(10), nullable=False, default="No")
    # Yes | No

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# INVENTORY MANAGEMENT
# Inventory Stock
# =====================================================
class InventoryStock(Base):
    __tablename__ = "inventory_stock"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, nullable=False, index=True)
    kitchen_id = Column(Integer, nullable=True, index=True)
    # Null = Main Store

    available_quantity = Column(Float, nullable=False)

    last_updated_date = Column(Date, nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# INVENTORY MANAGEMENT
# Inventory Stock Transactions
# =====================================================
class InventoryStockTransaction(Base):
    __tablename__ = "inventory_stock_transaction"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, nullable=False, index=True)
    kitchen_id = Column(Integer, nullable=True, index=True)

    transaction_type = Column(String(50), nullable=False, index=True)
    # IN | OUT | ADJUSTMENT | WASTE

    quantity = Column(Float, nullable=False)

    reference_type = Column(String(50), nullable=True)
    # Purchase | KOT | Manual | Transfer

    reference_id = Column(String(100), nullable=True)

    remarks = Column(String(255), nullable=True)

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# INVENTORY MANAGEMENT
# Menu Recipe
# =====================================================
class MenuRecipe(Base):
    __tablename__ = "menu_recipe"

    id = Column(Integer, primary_key=True, index=True)

    menu_id = Column(Integer, nullable=False, index=True)
    inventory_item_id = Column(Integer, nullable=False, index=True)

    quantity_required = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# INVENTORY MANAGEMENT
# Inventory Purchase
# =====================================================
class InventoryPurchase(Base):
    __tablename__ = "inventory_purchase"

    id = Column(Integer, primary_key=True, index=True)

    inventory_item_id = Column(Integer, nullable=False, index=True)

    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    purchase_date = Column(Date, nullable=False, index=True)
    supplier_name = Column(String(150), nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# GUEST MANAGEMENT
# Guest Master
# =====================================================
class Guest(Base):
    __tablename__ = "guest"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Guest Identity ----------------
    guest_code = Column(String(100), unique=True, nullable=False, index=True)

    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=True, index=True)

    mobile = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True, index=True)

    # ---------------- Guest Type ----------------
    guest_type = Column(String(50), nullable=False, index=True)
    # Walk-In | Regular | VIP | Hotel Guest

    # ---------------- Preferences ----------------
    food_preferences = Column(JSON, nullable=True)
    # Veg | Non-Veg | Jain | Allergies

    special_notes = Column(String(255), nullable=True)

    # ---------------- Loyalty ----------------
    loyalty_points = Column(Float, default=0)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# GUEST MANAGEMENT
# Guest Address
# =====================================================
class GuestAddress(Base):
    __tablename__ = "guest_address"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, nullable=False, index=True)

    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)
    postal_code = Column(String(20), nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# GUEST MANAGEMENT
# Guest Visit History
# =====================================================
class GuestVisitHistory(Base):
    __tablename__ = "guest_visit_history"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, nullable=False, index=True)

    visit_date = Column(Date, nullable=False, index=True)

    order_id = Column(Integer, nullable=True, index=True)
    bill_id = Column(Integer, nullable=True, index=True)

    visit_type = Column(String(50), nullable=False, index=True)
    # Dine-In | Takeaway | Delivery | Room Service

    total_amount = Column(Float, nullable=True)

    rating = Column(Integer, nullable=True)
    feedback = Column(String(255), nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# GUEST MANAGEMENT
# Guest Feedback
# =====================================================
class GuestFeedback(Base):
    __tablename__ = "guest_feedback"

    id = Column(Integer, primary_key=True, index=True)

    guest_id = Column(Integer, nullable=False, index=True)
    order_id = Column(Integer, nullable=True, index=True)

    rating = Column(Integer, nullable=False)
    comments = Column(String(255), nullable=True)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# REPORTS & ANALYTICS
# Daily Sales Summary
# =====================================================
class DailySalesReport(Base):
    __tablename__ = "daily_sales_report"

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    total_orders = Column(Integer, default=0)
    total_bills = Column(Integer, default=0)

    total_sales = Column(Float, default=0)
    total_tax = Column(Float, default=0)
    total_discount = Column(Float, default=0)
    total_service_charge = Column(Float, default=0)

    cash_amount = Column(Float, default=0)
    card_amount = Column(Float, default=0)
    upi_amount = Column(Float, default=0)
    room_posting_amount = Column(Float, default=0)

    status = Column(String(50), nullable=False, index=True, default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# REPORTS & ANALYTICS
# Item Wise Sales
# =====================================================
class ItemSalesReport(Base):
    __tablename__ = "item_sales_report"

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    menu_id = Column(Integer, nullable=False, index=True)
    item_name = Column(String(150), nullable=False)

    category_id = Column(Integer, nullable=True, index=True)
    quantity_sold = Column(Integer, default=0)

    total_amount = Column(Float, default=0)

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# REPORTS & ANALYTICS
# Category Wise Sales
# =====================================================
class CategorySalesReport(Base):
    __tablename__ = "category_sales_report"

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    category_id = Column(Integer, nullable=False, index=True)
    category_name = Column(String(100), nullable=False)

    total_quantity = Column(Integer, default=0)
    total_sales = Column(Float, default=0)

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# REPORTS & ANALYTICS
# Staff Performance
# =====================================================
class StaffPerformanceReport(Base):
    __tablename__ = "staff_performance_report"

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    employee_id = Column(Integer, nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)
    # Waiter | Cashier | Manager

    total_orders = Column(Integer, default=0)
    total_sales = Column(Float, default=0)

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# REPORTS & ANALYTICS
# Kitchen Performance
# =====================================================
class KitchenPerformanceReport(Base):
    __tablename__ = "kitchen_performance_report"

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    kitchen_id = Column(Integer, nullable=False, index=True)

    total_kots = Column(Integer, default=0)
    avg_preparation_time = Column(Float, nullable=True)
    completed_kots = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# REPORTS & ANALYTICS
# Payment Mode Report
# =====================================================
class PaymentModeReport(Base):
    __tablename__ = "payment_mode_report"

    id = Column(Integer, primary_key=True, index=True)

    report_date = Column(Date, nullable=False, index=True)

    payment_method = Column(String(50), nullable=False, index=True)
    # Cash | Card | UPI | Room Posting

    total_amount = Column(Float, default=0)

    created_at = Column(DateTime, server_default=func.now())
    company_id = Column(String(100), nullable=False, index=True)


Base.metadata.create_all(bind=engine)

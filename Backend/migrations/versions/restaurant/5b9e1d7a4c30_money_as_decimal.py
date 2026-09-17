"""money as exact DECIMAL rather than FLOAT

WHAT THIS CHANGES
    Every FLOAT column in `hotelerp_restaurant` becomes DECIMAL. 56 columns, no data
    dropped and no value re-derived -- MySQL converts each float to its decimal
    form on the way.

WHY
    Money was stored as single-precision FLOAT. 20009.85 is not representable
    in binary floating point, so the column actually held 20009.849609375, and
    `mysqldump` writes a FLOAT at about six significant digits -- so the
    release dump said `20009.8` and a restore came back five paise light.
    Two of `verify_seed.py`'s 34 invariants failed after any restore, and the
    deployment at 168.231.103.18 was restored from exactly such a dump.

    DECIMAL stores the digits, dumps as exact text, and compares exactly. The
    conversion also repairs the stored values: 20009.849609375 rounds to the
    20009.85 that was meant all along.

    Percentages, quantities, floor-plan coordinates and preparation times are
    included so that nothing in this schema can drift on a round trip. They
    keep a scale that suits them rather than money's two places.

WHY THE MODELS SAY `asdecimal=False`
    The column is exact; the value SQLAlchemy hands Python is still a float.
    Returning `Decimal` would be more correct in principle and would raise
    TypeError wherever a DB value meets a plain float from a request body --
    hundreds of sites, and a far larger change than the defect being fixed.
    Storage and transport are what were broken, and this fixes those.

OPERATIONALLY
    `ALTER TABLE ... MODIFY` rewrites the table on MySQL 8; this is not an
    INSTANT change. On a live property, run it in a maintenance window. It is
    also the reason this revision touches nothing but these column types.

Revision ID: 5b9e1d7a4c30
Revises: 3e3d820c4703
Create Date: 2026-09-17 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5b9e1d7a4c30"
down_revision: Union[str, None] = "3e3d820c4703"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, column, precision, scale, nullable)
COLUMNS = [
    ("category_sales_report", "total_sales", 12, 2, True),
    ("combo_deal", "combo_price", 12, 2, False),
    ("daily_sales_report", "total_sales", 12, 2, True),
    ("daily_sales_report", "total_tax", 12, 2, True),
    ("daily_sales_report", "total_discount", 12, 2, True),
    ("daily_sales_report", "total_service_charge", 12, 2, True),
    ("guest", "loyalty_points", 12, 2, True),
    ("guest_visit_history", "total_amount", 12, 2, True),
    ("inventory_item", "min_stock_level", 12, 3, True),
    ("inventory_purchase", "quantity", 12, 3, False),
    ("inventory_purchase", "unit_price", 12, 2, False),
    ("inventory_purchase", "total_amount", 12, 2, False),
    ("inventory_stock", "available_quantity", 12, 3, False),
    ("inventory_stock_transaction", "quantity", 12, 3, False),
    ("item_sales_report", "total_amount", 12, 2, True),
    ("kitchen_performance_report", "avg_preparation_time", 8, 2, True),
    ("menu_modifier", "price", 12, 2, True),
    ("menu_recipe", "quantity_required", 12, 3, False),
    ("menu_variant", "price", 12, 2, False),
    ("payment_mode_report", "total_amount", 12, 2, True),
    ("restaurant_bill", "sub_total", 12, 2, True),
    ("restaurant_bill", "cgst_percentage", 6, 3, True),
    ("restaurant_bill", "cgst_amount", 12, 2, True),
    ("restaurant_bill", "sgst_percentage", 6, 3, True),
    ("restaurant_bill", "sgst_amount", 12, 2, True),
    ("restaurant_bill", "igst_percentage", 6, 3, True),
    ("restaurant_bill", "igst_amount", 12, 2, True),
    ("restaurant_bill", "service_charge_percentage", 6, 3, True),
    ("restaurant_bill", "service_charge_amount", 12, 2, True),
    ("restaurant_bill", "discount_value", 12, 2, True),
    ("restaurant_bill", "discount_amount", 12, 2, True),
    ("restaurant_bill", "round_off", 12, 2, True),
    ("restaurant_bill", "grand_total", 12, 2, False),
    ("restaurant_bill_item", "rate", 12, 2, False),
    ("restaurant_bill_item", "amount", 12, 2, False),
    ("restaurant_bill_item", "tax_amount", 12, 2, True),
    ("restaurant_bill_payment", "paid_amount", 12, 2, False),
    ("restaurant_bill_split_detail", "split_amount", 12, 2, False),
    ("restaurant_menu", "price", 12, 2, False),
    ("restaurant_menu", "cost_price", 12, 2, True),
    ("restaurant_menu", "tax_percentage", 6, 3, True),
    ("restaurant_order", "sub_total", 12, 2, True),
    ("restaurant_order", "tax_amount", 12, 2, True),
    ("restaurant_order", "service_charge", 12, 2, True),
    ("restaurant_order", "discount_value", 12, 2, True),
    ("restaurant_order", "discount_amount", 12, 2, True),
    ("restaurant_order", "grand_total", 12, 2, True),
    ("restaurant_order_item", "price", 12, 2, False),
    ("restaurant_order_item_modifier", "price", 12, 2, True),
    ("restaurant_staff_assignment", "sales_target", 12, 2, True),
    ("restaurant_staff_assignment", "actual_sales", 12, 2, True),
    ("restaurant_staff_assignment", "opening_cash_float", 12, 2, True),
    ("restaurant_staff_assignment", "closing_cash_amount", 12, 2, True),
    ("restaurant_table", "position_x", 10, 2, True),
    ("restaurant_table", "position_y", 10, 2, True),
    ("staff_performance_report", "total_sales", 12, 2, True),
]


def upgrade() -> None:
    for table, column, precision, scale, nullable in COLUMNS:
        op.alter_column(
            table, column,
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=precision, scale=scale),
            existing_nullable=nullable,
        )


def downgrade() -> None:
    """Back to FLOAT, which is lossy -- the paise beyond six digits go again."""
    for table, column, precision, scale, nullable in COLUMNS:
        op.alter_column(
            table, column,
            existing_type=sa.Numeric(precision=precision, scale=scale),
            type_=sa.Float(),
            existing_nullable=nullable,
        )

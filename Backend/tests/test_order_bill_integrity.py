"""An order and the bill raised against it must not drift apart.

Run from inside RestaurantServices or BarServices (run_all.py does both):

    cd Backend/Services/RestaurantServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_order_bill_integrity.py -q

SQLite, the real models and controllers. Seed helpers come from
test_fnb_hardening.py so both suites build the same menu.

WHY THIS EXISTS
A bill copies the order's lines when it is generated and never reads the order
again. Three paths let the two disagree, each reachable from the UI:

- Items could be added to a Served order after it was billed. They went to the
  kitchen and were never charged: the guest paid the old total and that payment
  closed the order.
- A part-paid bill could be cancelled. There is no refund path, so the payment
  sat on a Cancelled bill that every report excludes, and the order could then
  be billed again for the full amount.
- "Wastage" with "Add" raised the stock level and wrote a positive WASTE row.
"""

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

import models.models as models
from test_fnb_hardening import (
    IS_BAR,
    TENANT,
    USER,
    add_item,
    billingController,
    inventoryController,
    make_order,
    orderController,
    seed_menu_and_inventory,
)

if IS_BAR:
    Bill, Method, OrderItem = models.BarBill, models.BarPaymentMethod, models.BarOrderItem
    Stock, Txn = models.BarInventoryStock, models.BarInventoryStockTransaction
    LOCATION_FIELD = "station_id"
else:
    Bill, Method, OrderItem = models.RestaurantBill, models.PaymentMethod, models.RestaurantOrderItem
    Stock, Txn = models.InventoryStock, models.InventoryStockTransaction
    LOCATION_FIELD = "kitchen_id"

METHOD_ID = 1


@pytest.fixture()
def db():
    engine = sa.create_engine("sqlite://")
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    session.add(Method(id=METHOD_ID, method_name="Cash", status="ACTIVE",
                       created_by=USER, company_id=TENANT))
    session.commit()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def stub_auth(monkeypatch):
    for module in (orderController, billingController, inventoryController):
        monkeypatch.setattr(module, "_auth", lambda request: (USER, "role", TENANT))


@pytest.fixture()
def seeded(db):
    return seed_menu_and_inventory(db)


def generate(db, order):
    payload = billingController.BillGenerateIn()
    return billingController.generate_bill(order.id, payload, None, db)["data"]


def pay(db, bill_id, amount):
    payload = billingController.PaymentIn(payment_method_id=METHOD_ID, paid_amount=amount)
    return billingController.record_payment(bill_id, payload, None, db)


def cancel_bill(db, bill_id, reason="Guest changed order"):
    payload = billingController.BillCancelIn(reason=reason)
    return billingController.cancel_bill(bill_id, payload, None, db)


def add_more(db, order, seeded, quantity=1):
    payload = orderController.OrderItemsIn(
        items=[orderController.OrderItemIn(menu_id=seeded["menu"].id, quantity=quantity)]
    )
    return orderController.add_order_items(order.id, payload, None, db)


def remove_item(db, item_id):
    return orderController.cancel_order_item(item_id, None, db)


def set_order_status(db, order, target):
    payload = orderController.OrderStatusIn(order_status=target)
    return orderController.update_order_status(order.id, payload, None, db)


def adjust(db, seeded, quantity, transaction_type):
    payload = inventoryController.StockAdjustIn(
        inventory_item_id=seeded["ingredient"].id,
        quantity=quantity,
        transaction_type=transaction_type,
        **{LOCATION_FIELD: seeded["location"]},
    )
    return inventoryController.adjust_stock(payload, None, db)


def stock_level(db, seeded):
    db.expire_all()
    row = db.query(Stock).filter(Stock.inventory_item_id == seeded["ingredient"].id).one()
    return float(row.available_quantity)


# --------------------------------------------------------------------------
# Cancelling a bill
# --------------------------------------------------------------------------

def test_a_part_paid_bill_cannot_be_cancelled(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    bill = generate(db, order)
    pay(db, bill["id"], 100)

    with pytest.raises(HTTPException) as exc:
        cancel_bill(db, bill["id"])
    assert exc.value.status_code == 400
    assert "payments against it" in exc.value.detail

    db.expire_all()
    row = db.get(Bill, bill["id"])
    assert row.bill_status != "Cancelled"
    assert row.payment_status == "Partial"


def test_a_part_paid_bill_still_blocks_a_second_bill(db, seeded):
    """The point of the guard: no full-price bill on top of money taken."""
    order = make_order(db)
    add_item(db, order, seeded)
    bill = generate(db, order)
    pay(db, bill["id"], 100)
    with pytest.raises(HTTPException):
        cancel_bill(db, bill["id"])
    with pytest.raises(HTTPException) as exc:
        generate(db, order)
    assert "already exists" in exc.value.detail


def test_an_unpaid_bill_cancels_once(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    bill = generate(db, order)

    cancel_bill(db, bill["id"], reason="Wrong table")
    with pytest.raises(HTTPException) as exc:
        cancel_bill(db, bill["id"], reason="Second reason")
    assert exc.value.status_code == 409

    db.expire_all()
    assert db.get(Bill, bill["id"]).remarks == "Cancelled: Wrong table"


def test_a_cancel_needs_a_reason(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    bill = generate(db, order)
    with pytest.raises(HTTPException) as exc:
        cancel_bill(db, bill["id"], reason="   ")
    assert exc.value.status_code == 400


# --------------------------------------------------------------------------
# Changing a billed order
# --------------------------------------------------------------------------

def test_items_cannot_be_added_to_a_billed_order(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    bill = generate(db, order)

    with pytest.raises(HTTPException) as exc:
        add_more(db, order, seeded)
    assert exc.value.status_code == 409
    assert bill["bill_number"] in exc.value.detail

    db.expire_all()
    active = db.query(OrderItem).filter(OrderItem.order_id == order.id,
                                        OrderItem.status == "ACTIVE").count()
    assert active == 1


def test_a_billed_line_cannot_be_removed(db, seeded):
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    generate(db, order)

    with pytest.raises(HTTPException) as exc:
        remove_item(db, item_id)
    assert exc.value.status_code == 409


def test_a_billed_order_cannot_be_cancelled(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    generate(db, order)

    with pytest.raises(HTTPException) as exc:
        set_order_status(db, order, "Cancelled")
    assert exc.value.status_code == 409
    db.expire_all()
    assert db.get(type(order), order.id).order_status == "In Progress"


def test_cancelling_the_bill_unfreezes_the_order(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    bill = generate(db, order)
    cancel_bill(db, bill["id"])

    add_more(db, order, seeded)
    rebilled = generate(db, order)
    # Two lines now: QUANTITY x (base + modifier) from add_item, plus one base.
    assert rebilled["grand_total"] > bill["grand_total"]


def test_get_order_names_the_standing_bill(db, seeded):
    order = make_order(db)
    add_item(db, order, seeded)
    assert orderController.get_order(order.id, None, db)["data"]["active_bill_number"] is None

    bill = generate(db, order)
    data = orderController.get_order(order.id, None, db)["data"]
    assert data["active_bill_number"] == bill["bill_number"]

    cancel_bill(db, bill["id"])
    assert orderController.get_order(order.id, None, db)["data"]["active_bill_number"] is None


# --------------------------------------------------------------------------
# Removing a line before billing
# --------------------------------------------------------------------------

def test_a_pending_line_can_be_removed(db, seeded):
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    remove_item(db, item_id)
    db.expire_all()
    assert db.get(OrderItem, item_id).item_status == "Cancelled"


def test_a_line_already_in_the_kitchen_cannot_be_removed(db, seeded):
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    db.get(OrderItem, item_id).item_status = "Preparing"
    db.commit()

    with pytest.raises(HTTPException) as exc:
        remove_item(db, item_id)
    assert exc.value.status_code == 409
    assert "Preparing" in exc.value.detail


def test_a_line_on_a_closed_order_cannot_be_removed(db, seeded):
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    order.order_status = "Completed"
    db.commit()

    with pytest.raises(HTTPException) as exc:
        remove_item(db, item_id)
    assert exc.value.status_code == 400


# --------------------------------------------------------------------------
# Wastage
# --------------------------------------------------------------------------

def test_wastage_cannot_add_stock(db, seeded):
    before = stock_level(db, seeded)
    with pytest.raises(HTTPException) as exc:
        adjust(db, seeded, 5, "WASTE")
    assert exc.value.status_code == 400
    assert stock_level(db, seeded) == before
    assert db.query(Txn).filter(Txn.transaction_type == "WASTE").count() == 0


def test_wastage_removes_stock(db, seeded):
    before = stock_level(db, seeded)
    adjust(db, seeded, -5, "WASTE")
    assert stock_level(db, seeded) == before - 5


def test_an_adjustment_still_goes_both_ways(db, seeded):
    before = stock_level(db, seeded)
    adjust(db, seeded, 3, "ADJUSTMENT")
    adjust(db, seeded, -1, "ADJUSTMENT")
    assert stock_level(db, seeded) == before + 2


def test_an_unknown_location_is_refused(db, seeded):
    payload = inventoryController.StockAdjustIn(
        inventory_item_id=seeded["ingredient"].id,
        quantity=1,
        **{LOCATION_FIELD: 999999},
    )
    with pytest.raises(HTTPException) as exc:
        inventoryController.adjust_stock(payload, None, db)
    assert exc.value.status_code == 400

"""Restaurant and Bar F&B hardening tests.

Run this suite from the owning service directory, in the same way as the
existing service-specific suites:

    cd Backend/Services/RestaurantServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest \
        ../../tests/test_fnb_hardening.py -q

The suite uses SQLite and the real service models/controllers.  It covers the
two money/inventory boundaries that browser QA could not exercise reliably:
priced modifiers must be present once in the server's price breakdown, and a
KOT/BOT Ready or Completed request must be safe to retry without consuming a
second recipe.
"""

from datetime import date, time
import math

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker

import models.models as models

if hasattr(models, "RestaurantBill"):
    from resources import billingController, inventoryController, kitchenController, orderController

    IS_BAR = False
    ITEM_STATUS_TYPE = kitchenController.KotItemStatusIn
    TICKET_STATUS_TYPE = kitchenController.KotStatusIn
    ITEM_STATUS_HANDLER = kitchenController.update_kot_item_status
    TICKET_STATUS_HANDLER = kitchenController.update_kot_status
elif hasattr(models, "BarBill"):
    from resources import billingController, inventoryController, orderController, ticketController

    IS_BAR = True
    kitchenController = ticketController  # the two services use the same shape
    ITEM_STATUS_TYPE = ticketController.BotItemStatusIn
    TICKET_STATUS_TYPE = ticketController.BotStatusIn
    ITEM_STATUS_HANDLER = ticketController.update_bot_item_status
    TICKET_STATUS_HANDLER = ticketController.update_bot_status
else:  # pragma: no cover - protects against running from the wrong directory
    raise RuntimeError("run this from RestaurantServices or BarServices")


TENANT = "tenant-fnb"
USER = "waiter-1"
BASE_PRICE = 100.0
MODIFIER_PRICE = 25.0
QUANTITY = 3
RECIPE_QUANTITY = 2.0
START_STOCK = 20.0


@pytest.fixture()
def db():
    engine = sa.create_engine("sqlite://")
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def stub_auth(monkeypatch):
    """The tests exercise pricing and inventory, not bearer-token verification."""
    monkeypatch.setattr(orderController, "_auth", lambda request: (USER, "role", TENANT))
    monkeypatch.setattr(billingController, "_auth", lambda request: (USER, "role", TENANT))
    monkeypatch.setattr(kitchenController, "_auth", lambda request: (USER, "role", TENANT))


def seed_menu_and_inventory(db):
    """Create one menu item, one priced modifier, and one recipe ingredient."""
    if IS_BAR:
        station = models.BarStation(
            station_code="BST-TEST",
            station_name="Test Bar",
            is_active=True,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(station)
        db.flush()
        category = models.BarMenuCategory(
            category_code="BCAT-TEST",
            category_name="Test Drinks",
            station_id=station.id,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(category)
        db.flush()
        menu = models.BarMenuItem(
            item_code="BAR-TEST-1",
            item_name="Test Drink",
            category_id=category.id,
            price=BASE_PRICE,
            service_charge_applicable=False,
            station_id=station.id,
            availability_status="Available",
            has_variants=False,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        modifier_model = models.BarMenuModifier
        inventory_item_model = models.BarInventoryItem
        stock_model = models.BarInventoryStock
        recipe_model = models.BarRecipe
        stock_location = {"station_id": station.id}
        recipe_unit = "ml"
        item_unit = "ml"
        location_field = "station_id"
    else:
        kitchen = models.Kitchen(
            kitchen_code="KTC-TEST",
            kitchen_name="Test Kitchen",
            kitchen_type="Main",
            is_active=True,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(kitchen)
        db.flush()
        category = models.MenuCategory(
            category_code="CAT-TEST",
            category_name="Test Food",
            kitchen_id=kitchen.id,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(category)
        db.flush()
        menu = models.RestaurantMenu(
            item_code="RES-TEST-1",
            item_name="Test Dish",
            category_id=category.id,
            price=BASE_PRICE,
            service_charge_applicable=False,
            kitchen_id=kitchen.id,
            availability_status="Available",
            is_veg=True,
            has_variants=False,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        modifier_model = models.MenuModifier
        inventory_item_model = models.InventoryItem
        stock_model = models.InventoryStock
        recipe_model = models.MenuRecipe
        stock_location = {"kitchen_id": kitchen.id}
        recipe_unit = "Kg"
        item_unit = "Kg"
        location_field = "kitchen_id"

    db.add(menu)
    db.flush()
    modifier = modifier_model(
        menu_id=menu.id,
        modifier_name="Extra",
        price=MODIFIER_PRICE,
        modifier_type="Add-on",
        status="ACTIVE",
        created_by=USER,
        company_id=TENANT,
    )
    ingredient = inventory_item_model(
        item_code="INV-TEST-1",
        item_name="Test Ingredient",
        unit=item_unit,
        min_stock_level=0,
        is_perishable=False,
        status="ACTIVE",
        created_by=USER,
        company_id=TENANT,
    )
    db.add_all([modifier, ingredient])
    db.flush()
    stock = stock_model(
        inventory_item_id=ingredient.id,
        available_quantity=START_STOCK,
        last_updated_date=date.today(),
        status="ACTIVE",
        company_id=TENANT,
        **stock_location,
    )
    recipe = recipe_model(
        menu_id=menu.id,
        inventory_item_id=ingredient.id,
        quantity_required=RECIPE_QUANTITY,
        unit=recipe_unit,
        status="ACTIVE",
        created_by=USER,
        company_id=TENANT,
    )
    db.add_all([stock, recipe])
    db.commit()
    return {
        "menu": menu,
        "modifier": modifier,
        "ingredient": ingredient,
        "stock": stock,
        "recipe": recipe,
        "location": stock_location[location_field],
    }


def make_order(db):
    if IS_BAR:
        order = models.BarOrder(
            order_number="BORD-TEST-1",
            order_date=date.today(),
            order_time=time(12, 0),
            order_type="At Counter",
            order_status="In Progress",
            payment_status="Pending",
            sub_total=0,
            tax_amount=0,
            service_charge=0,
            discount_amount=0,
            grand_total=0,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
    else:
        order = models.RestaurantOrder(
            order_number="ORD-TEST-1",
            order_date=date.today(),
            order_time=time(12, 0),
            order_type="Takeaway",
            order_status="In Progress",
            payment_status="Pending",
            sub_total=0,
            tax_amount=0,
            service_charge=0,
            discount_amount=0,
            grand_total=0,
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def add_item(db, order, seeded):
    payload = orderController.OrderItemsIn(
        items=[
            orderController.OrderItemIn(
                menu_id=seeded["menu"].id,
                modifier_ids=[seeded["modifier"].id],
                quantity=QUANTITY,
            )
        ]
    )
    result = orderController.add_order_items(order.id, payload, None, db)
    return result["data"][0]


def make_ticket(db, order, item_id, seeded, number):
    if IS_BAR:
        ticket = models.BarOrderTicket(
            bot_number=number,
            order_id=order.id,
            bot_type="Original",
            station_id=seeded["location"],
            bot_status="New",
            priority="Normal",
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(ticket)
        db.flush()
        ticket_item = models.BarOrderTicketItem(
            bot_id=ticket.id,
            order_item_id=item_id,
            preparation_status="Pending",
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
    else:
        ticket = models.KitchenOrderTicket(
            kot_number=number,
            order_id=order.id,
            kot_type="Original",
            kitchen_id=seeded["location"],
            kot_status="New",
            priority="Normal",
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(ticket)
        db.flush()
        ticket_item = models.KitchenOrderItem(
            kot_id=ticket.id,
            order_item_id=item_id,
            preparation_status="Pending",
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
    db.add(ticket_item)
    db.commit()
    db.refresh(ticket)
    db.refresh(ticket_item)
    return ticket, ticket_item


def make_ticket_for_items(db, order, item_ids, seeded, number):
    """Create one ticket with multiple order lines for idempotency coverage."""
    if IS_BAR:
        ticket = models.BarOrderTicket(
            bot_number=number,
            order_id=order.id,
            bot_type="Original",
            station_id=seeded["location"],
            bot_status="New",
            priority="Normal",
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(ticket)
        db.flush()
        ticket_items = [
            models.BarOrderTicketItem(
                bot_id=ticket.id,
                order_item_id=item_id,
                preparation_status="Pending",
                status="ACTIVE",
                created_by=USER,
                company_id=TENANT,
            )
            for item_id in item_ids
        ]
    else:
        ticket = models.KitchenOrderTicket(
            kot_number=number,
            order_id=order.id,
            kot_type="Original",
            kitchen_id=seeded["location"],
            kot_status="New",
            priority="Normal",
            status="ACTIVE",
            created_by=USER,
            company_id=TENANT,
        )
        db.add(ticket)
        db.flush()
        ticket_items = [
            models.KitchenOrderItem(
                kot_id=ticket.id,
                order_item_id=item_id,
                preparation_status="Pending",
                status="ACTIVE",
                created_by=USER,
                company_id=TENANT,
            )
            for item_id in item_ids
        ]
    db.add_all(ticket_items)
    db.commit()
    for item in ticket_items:
        db.refresh(item)
    db.refresh(ticket)
    return ticket, ticket_items


def stock_quantity(db, seeded):
    stock_model = models.BarInventoryStock if IS_BAR else models.InventoryStock
    return db.get(stock_model, seeded["stock"].id).available_quantity


def transaction_count(db, seeded):
    if IS_BAR:
        return (
            db.query(models.BarInventoryStockTransaction)
            .filter(
                models.BarInventoryStockTransaction.inventory_item_id == seeded["ingredient"].id,
                models.BarInventoryStockTransaction.transaction_type == "OUT",
            )
            .count()
        )
    return (
        db.query(models.InventoryStockTransaction)
        .filter(
            models.InventoryStockTransaction.inventory_item_id == seeded["ingredient"].id,
            models.InventoryStockTransaction.transaction_type == "OUT",
        )
        .count()
    )


def test_priced_modifier_is_included_once_in_order_and_bill(db):
    seeded = seed_menu_and_inventory(db)
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    # Simulate a row written by the old calculator: the modifier snapshot is
    # present, but the stored order total is only the base price.
    order.sub_total = BASE_PRICE * QUANTITY
    order.grand_total = BASE_PRICE * QUANTITY
    db.commit()

    detail = orderController.get_order(order.id, None, db)["data"]
    item = detail["items"][0]
    expected_subtotal = (BASE_PRICE + MODIFIER_PRICE) * QUANTITY
    assert detail["sub_total"] == expected_subtotal
    assert detail["modifier_total"] == MODIFIER_PRICE * QUANTITY
    assert detail["grand_total"] == expected_subtotal
    assert item["modifier_ids"] == [seeded["modifier"].id]
    assert item["modifiers"][0]["price"] == MODIFIER_PRICE
    assert item["modifier_total"] == MODIFIER_PRICE
    assert item["unit_price"] == BASE_PRICE + MODIFIER_PRICE
    assert item["total_price"] == expected_subtotal
    assert item["line_total"] == expected_subtotal
    if IS_BAR:
        listed = orderController.list_orders(
            None,
            order_status_filter=None,
            order_type=None,
            table_id=None,
            order_date=None,
            db=db,
        )["data"][0]
    else:
        listed = orderController.list_orders(
            None,
            order_status_filter=None,
            order_type=None,
            table_id=None,
            floor_id=None,
            order_date=None,
            db=db,
        )["data"][0]
    assert listed["sub_total"] == expected_subtotal
    assert listed["grand_total"] == expected_subtotal

    result = billingController.generate_bill(
        order.id,
        billingController.BillGenerateIn(),
        None,
        db,
    )
    bill_model = models.BarBill if IS_BAR else models.RestaurantBill
    bill = db.get(bill_model, result["data"]["id"])
    assert bill.sub_total == expected_subtotal
    assert bill.grand_total == expected_subtotal
    bill_item = db.query(
        models.BarBillItem if IS_BAR else models.RestaurantBillItem
    ).filter_by(bill_id=bill.id, order_item_id=item_id).one()
    assert bill_item.rate == BASE_PRICE + MODIFIER_PRICE
    assert bill_item.amount == expected_subtotal

    bill_detail = billingController.get_bill(bill.id, None, db)["data"]
    assert bill_detail["items"][0].modifier_total == MODIFIER_PRICE
    assert bill_detail["items"][0].modifiers[0]["modifier_id"] == seeded["modifier"].id


def test_completing_a_ticket_and_retrying_deducts_recipe_once(db):
    seeded = seed_menu_and_inventory(db)
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    ticket, ticket_item = make_ticket(db, order, item_id, seeded, "TICKET-1")

    item_payload = ITEM_STATUS_TYPE(preparation_status="Ready")
    first = ITEM_STATUS_HANDLER(ticket_item.id, item_payload, None, db)
    second = ITEM_STATUS_HANDLER(ticket_item.id, item_payload, None, db)
    assert first["status"] == second["status"] == "success"
    assert stock_quantity(db, seeded) == pytest.approx(START_STOCK - RECIPE_QUANTITY * QUANTITY)
    assert transaction_count(db, seeded) == 1

    # A whole-ticket completion after the item action must not consume a
    # second recipe, and a repeated whole-ticket request is also a no-op.
    if IS_BAR:
        status_payload = TICKET_STATUS_TYPE(bot_status="Completed")
    else:
        status_payload = TICKET_STATUS_TYPE(kot_status="Completed")
    TICKET_STATUS_HANDLER(ticket.id, status_payload, None, db)
    TICKET_STATUS_HANDLER(ticket.id, status_payload, None, db)
    assert stock_quantity(db, seeded) == pytest.approx(START_STOCK - RECIPE_QUANTITY * QUANTITY)
    assert transaction_count(db, seeded) == 1


def test_duplicate_ticket_for_same_order_item_is_idempotent(db):
    seeded = seed_menu_and_inventory(db)
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    _first_ticket, first_item = make_ticket(db, order, item_id, seeded, "TICKET-1")
    _second_ticket, second_item = make_ticket(db, order, item_id, seeded, "TICKET-2")

    ITEM_STATUS_HANDLER(
        first_item.id, ITEM_STATUS_TYPE(preparation_status="Ready"), None, db
    )
    ITEM_STATUS_HANDLER(
        second_item.id, ITEM_STATUS_TYPE(preparation_status="Ready"), None, db
    )
    assert stock_quantity(db, seeded) == pytest.approx(START_STOCK - RECIPE_QUANTITY * QUANTITY)
    assert transaction_count(db, seeded) == 1


def test_two_lines_on_one_ticket_each_deduct_once(db):
    seeded = seed_menu_and_inventory(db)
    order = make_order(db)
    first_item = add_item(db, order, seeded)
    second_item = add_item(db, order, seeded)
    ticket, _ = make_ticket_for_items(
        db, order, [first_item, second_item], seeded, "TICKET-MULTI"
    )

    if IS_BAR:
        status_payload = TICKET_STATUS_TYPE(bot_status="Completed")
    else:
        status_payload = TICKET_STATUS_TYPE(kot_status="Completed")
    TICKET_STATUS_HANDLER(ticket.id, status_payload, None, db)
    assert stock_quantity(db, seeded) == pytest.approx(
        START_STOCK - (RECIPE_QUANTITY * QUANTITY * 2)
    )
    assert transaction_count(db, seeded) == 2


def test_insufficient_stock_is_refused_without_creating_negative_stock(db):
    seeded = seed_menu_and_inventory(db)
    order = make_order(db)
    item_id = add_item(db, order, seeded)
    ticket, ticket_item = make_ticket(db, order, item_id, seeded, "TICKET-LOW")

    stock_model = models.BarInventoryStock if IS_BAR else models.InventoryStock
    stock = db.get(stock_model, seeded["stock"].id)
    stock.available_quantity = 1
    db.commit()

    with pytest.raises(HTTPException) as exc:
        ITEM_STATUS_HANDLER(
            ticket_item.id,
            ITEM_STATUS_TYPE(preparation_status="Ready"),
            None,
            db,
        )
    assert exc.value.status_code == 409
    assert "Insufficient stock" in exc.value.detail
    assert stock_quantity(db, seeded) == pytest.approx(1)
    assert transaction_count(db, seeded) == 0
    db.refresh(ticket_item)
    assert ticket_item.preparation_status == "Pending"


def test_positive_quantity_validation_rejects_zero_and_nonfinite_recipes(db):
    recipe_type = inventoryController.RecipeIngredientIn
    order_type = orderController.OrderItemIn
    for value in (0, -1):
        with pytest.raises(ValidationError):
            recipe_type(inventory_item_id=1, quantity_required=value, unit="Kg" if not IS_BAR else "ml")
        with pytest.raises(ValidationError):
            order_type(menu_id=1, quantity=value)
    with pytest.raises(ValidationError):
        recipe_type(inventory_item_id=1, quantity_required=math.nan, unit="Kg" if not IS_BAR else "ml")

    seeded = seed_menu_and_inventory(db)
    with pytest.raises(inventoryController.InventoryDeductionError):
        inventoryController.deduct_stock_for_menu_item(
            db,
            TENANT,
            seeded["menu"].id,
            seeded["location"],
            0,
            "BAD-QUANTITY",
            USER,
        )
    assert stock_quantity(db, seeded) == pytest.approx(START_STOCK)
    assert transaction_count(db, seeded) == 0

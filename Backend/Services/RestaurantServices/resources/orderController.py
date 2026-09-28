import logging
import math
import uuid
from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from models import get_db, models
from resources.utils import verify_authentication
from resources.validation import normalize_phone
from configs.base_config import CommonWords

logger = logging.getLogger(__name__)

router = APIRouter()

def _server_error(exc: Exception) -> HTTPException:
    """Log the detail, return a generic message.

    `detail=str(e)` leaked Python exception text -- driver errors and whole SQL
    statements -- to the browser on every unexpected failure, which is both a
    poor error message and an information disclosure.
    """
    logger.exception("unhandled_exception")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
    )


STATUS = CommonWords.STATUS
UNSTATUS = CommonWords.UNSTATUS


def gen_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


# The column's own vocabulary, copied from the SAEnum declarations in
# models.py. Anything outside these sets used to travel all the way to MySQL
# and come back as "Data truncated for column ..." -- a 500 for what is a bad
# request, with the failing SQL attached.
ORDER_TYPES = ("Dine-In", "Takeaway", "Delivery", "Room Service")
ORDER_STATUSES = ("New", "In Progress", "Ready", "Served", "Completed", "Cancelled")


def _assert_in(value, allowed, field):
    if value not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field} must be one of: {', '.join(allowed)}",
        )


# =====================================================
# SCHEMAS
# =====================================================
class OrderIn(BaseModel):
    order_type: str  # Dine-In | Takeaway | Delivery | Room Service
    table_id: Optional[int] = None
    room_no: Optional[str] = None
    guest_name: Optional[str] = None
    guest_mobile: Optional[str] = None
    # ISO-3166-1 alpha-2 country the number was typed in; a national number with
    # no country code is ambiguous and is not guessed. See
    # resources/validation.py.
    phone_region: Optional[str] = None
    no_of_guests: Optional[int] = None
    server_id: Optional[str] = None
    server_name: Optional[str] = None
    special_notes: Optional[str] = None


class OrderItemIn(BaseModel):
    menu_id: int
    variant_id: Optional[int] = None
    modifier_ids: Optional[List[int]] = None
    quantity: int
    special_instructions: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("quantity must be at least 1")
        return value


class OrderItemsIn(BaseModel):
    items: List[OrderItemIn]


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    item_status: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 1:
            raise ValueError("quantity must be at least 1")
        return value


class OrderConfirmIn(BaseModel):
    priority: Optional[str] = "Normal"  # Normal | High | ASAP


class OrderStatusIn(BaseModel):
    order_status: str


# =====================================================
# HELPERS
# =====================================================
def _resolve_price_and_kitchen(db: Session, company_id: str, created_by: str, item: OrderItemIn):
    menu = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == item.menu_id, models.RestaurantMenu.company_id == company_id)
        .first()
    )
    if not menu:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"menu_id {item.menu_id} does not exist")
    if menu.availability_status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{menu.item_name} is not available")

    price = menu.price
    variant = None
    if item.variant_id:
        variant = (
            db.query(models.MenuVariant)
            .filter(models.MenuVariant.id == item.variant_id, models.MenuVariant.menu_id == item.menu_id)
            .first()
        )
        if not variant:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="variant_id does not match menu_id")
        price = variant.price

    kitchen = db.query(models.Kitchen).filter(models.Kitchen.id == menu.kitchen_id, models.Kitchen.company_id == company_id).first()
    if not kitchen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{menu.item_name} has no valid kitchen station configured")
    return menu, price, kitchen, variant


def _finite_number(value, field: str) -> float:
    """Return a database numeric as a finite float for authoritative arithmetic."""
    if value is None:
        return 0.0
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _money(value) -> float:
    return round(_finite_number(value, "amount"), 2)


def _modifier_rows_by_item(db: Session, items: List[models.RestaurantOrderItem]):
    """Load the persisted modifier snapshots once for a set of order lines.

    The order item's ``price`` is the menu/variant price.  Modifier prices live
    on the child rows, so pricing has to read those rows explicitly rather than
    trusting a client-provided total (or adding them to ``price`` and risking a
    second addition in billing).
    """
    item_ids = [item.id for item in items if item.id is not None]
    rows_by_item: Dict[int, List[models.RestaurantOrderItemModifier]] = {
        item.id: [] for item in items if item.id is not None
    }
    if not item_ids:
        return rows_by_item
    rows = (
        db.query(models.RestaurantOrderItemModifier)
        .filter(models.RestaurantOrderItemModifier.order_item_id.in_(item_ids))
        .order_by(models.RestaurantOrderItemModifier.id.asc())
        .all()
    )
    for row in rows:
        rows_by_item.setdefault(row.order_item_id, []).append(row)
    return rows_by_item


def pricing_for_items(db: Session, items: List[models.RestaurantOrderItem]):
    """Return the one server-side price breakdown used by orders and bills."""
    rows_by_item = _modifier_rows_by_item(db, items)
    pricing = {}
    for item in items:
        quantity = _finite_number(item.quantity, "quantity")
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        base_rate = _finite_number(item.price, "price")
        modifiers = rows_by_item.get(item.id, [])
        modifier_total = _money(
            sum(_finite_number(modifier.price, "modifier price") for modifier in modifiers)
        )
        effective_rate = _money(base_rate + modifier_total)
        base_total = _money(base_rate * quantity)
        # Derive the final amount from the same rounded effective rate used by
        # the bill.  This keeps rate * quantity and the authoritative line
        # amount add up even when a fractional unit price is configured.
        line_total = _money(effective_rate * quantity)
        pricing[item.id] = {
            "modifiers": modifiers,
            "modifier_total": modifier_total,
            "base_rate": _money(base_rate),
            "base_total": base_total,
            "effective_rate": effective_rate,
            "line_total": line_total,
        }
    return pricing


def _modifier_total_for_items(items: List[models.RestaurantOrderItem], pricing: dict):
    return _money(
        sum(
            pricing[item.id]["modifier_total"] * _finite_number(item.quantity, "quantity")
            for item in items
        )
    )


def _totals_for_pricing(order: models.RestaurantOrder, pricing: dict):
    sub_total = _money(sum(row["line_total"] for row in pricing.values()))
    grand_total = _money(
        sub_total
        + _finite_number(order.tax_amount, "tax_amount")
        + _finite_number(order.service_charge, "service_charge")
        - _finite_number(order.discount_amount, "discount_amount")
    )
    return sub_total, grand_total


def calculate_order_totals(db: Session, order: models.RestaurantOrder):
    """Calculate an order from persisted base prices and modifier snapshots."""
    items = (
        db.query(models.RestaurantOrderItem)
        .filter(models.RestaurantOrderItem.order_id == order.id, models.RestaurantOrderItem.status == STATUS)
        .all()
    )
    pricing = pricing_for_items(db, items)
    return _totals_for_pricing(order, pricing)


def _recalculate_totals(db: Session, order: models.RestaurantOrder):
    sub_total, grand_total = calculate_order_totals(db, order)
    order.sub_total = sub_total
    order.grand_total = grand_total
    return sub_total, grand_total


def _modifier_data(modifier: models.RestaurantOrderItemModifier):
    return {
        "id": modifier.id,
        "order_item_id": modifier.order_item_id,
        "modifier_id": modifier.modifier_id,
        "modifier_name": modifier.modifier_name,
        "price": _finite_number(modifier.price, "modifier price"),
    }


def _order_item_data(item: models.RestaurantOrderItem, item_name: Optional[str], item_pricing: dict):
    modifiers = item_pricing["modifiers"]
    return {
        **item.__dict__,
        # ``price`` is the persisted menu/variant base.  The explicit
        # unit/effective fields below are the amount that includes modifiers.
        "item_name": item_name,
        "modifier_ids": [modifier.modifier_id for modifier in modifiers],
        "modifier_names": [modifier.modifier_name for modifier in modifiers],
        "modifiers": [_modifier_data(modifier) for modifier in modifiers],
        "modifier_total": item_pricing["modifier_total"],
        "base_total": item_pricing["base_total"],
        "base_rate": item_pricing["base_rate"],
        "base_unit_price": item_pricing["base_rate"],
        "unit_price": item_pricing["effective_rate"],
        "effective_rate": item_pricing["effective_rate"],
        "effective_unit_price": item_pricing["effective_rate"],
        "line_total": item_pricing["line_total"],
        "total_price": item_pricing["line_total"],
    }


# =====================================================
# ORDERS
# =====================================================
@router.post("/order", status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)

    _assert_in(payload.order_type, ORDER_TYPES, "order_type")

    if payload.order_type == "Dine-In" and not payload.table_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id is required for Dine-In orders")
    if payload.order_type == "Room Service" and not payload.room_no:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="room_no is required for Room Service orders")

    table = None
    if payload.table_id:
        table = (
            db.query(models.RestaurantTable)
            .filter(models.RestaurantTable.id == payload.table_id, models.RestaurantTable.company_id == company_id)
            .with_for_update()
            .first()
        )
        if not table:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id does not exist")
        if table.table_status == "Occupied" and table.current_order_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table already has an active order")

    guest = None
    if payload.guest_mobile:
        # Canonicalised before the lookup, so an order typed as "+91 98765 43210"
        # finds the guest stored as +919876543210. Previously the raw string was
        # compared, so the same guest produced a different order depending on the
        # spacing the person used (C-086).
        guest_mobile = normalize_phone(payload.guest_mobile, field="guest_mobile",
                                       default_region=payload.phone_region)
        guest = (
            db.query(models.Guest)
            .filter(models.Guest.mobile == guest_mobile, models.Guest.company_id == company_id, models.Guest.status == STATUS)
            .first()
        )
    else:
        guest_mobile = None

    try:
        now = datetime.now()
        # `phone_region` is request-scoped so the number could be read; the row
        # stores the canonical E.164 value instead.
        order_values = payload.dict(exclude={"phone_region"})
        if guest_mobile:
            order_values["guest_mobile"] = guest_mobile
        order = models.RestaurantOrder(
            order_number=gen_code("ORD"),
            order_date=now.date(),
            order_time=now.time(),
            order_status="New",
            payment_status="Pending",
            table_code=table.table_code if table else None,
            floor_id=table.floor_id if table else None,
            floor_code=table.floor_code if table else None,
            guest_id=guest.id if guest else None,
            created_by=user_id,
            company_id=company_id,
            **order_values,
        )
        db.add(order)
        db.flush()

        if table:
            table.table_status = "Occupied"
            table.current_order_id = order.id
            table.updated_by = user_id

        db.commit()
        db.refresh(order)
        return {"status": "success", "data": {"id": order.id, "order_number": order.order_number, "token": order.token}}
    except HTTPException:
        raise
    except OperationalError as e:
        db.rollback()
        # A concurrent create for the same table can deadlock if both callers
        # read the available row before either writes the order/table pair.
        # The row lock above serializes the normal path; translate a residual
        # lock timeout/deadlock to a deterministic client conflict rather than
        # leaking a 500.
        mysql_code = e.orig.args[0] if getattr(e, "orig", None) and e.orig.args else None
        if mysql_code in (1205, 1213):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table already has an active order")
        raise _server_error(e)
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/order", status_code=status.HTTP_200_OK)
def list_orders(
    request: Request,
    order_status_filter: Optional[str] = Query(None, alias="order_status"),
    order_type: Optional[str] = Query(None),
    table_id: Optional[int] = Query(None),
    floor_id: Optional[int] = Query(None),
    order_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.RestaurantOrder).filter(
        models.RestaurantOrder.company_id == company_id, models.RestaurantOrder.status == STATUS
    )
    # Orders for one floor. The floor detail screen had no way to ask for this,
    # so it fetched EVERY order in the company on each visit and filtered them
    # in the browser against that floor's table ids -- a full table scan over
    # the wire that grows with the order history.
    if floor_id is not None:
        floor_table_ids = [
            t.id
            for t in db.query(models.RestaurantTable.id)
            .filter(
                models.RestaurantTable.floor_id == floor_id,
                models.RestaurantTable.company_id == company_id,
            )
            .all()
        ]
        if not floor_table_ids:
            return {"status": "success", "count": 0, "data": []}
        q = q.filter(models.RestaurantOrder.table_id.in_(floor_table_ids))
    if order_status_filter:
        q = q.filter(models.RestaurantOrder.order_status == order_status_filter)
    if order_type:
        q = q.filter(models.RestaurantOrder.order_type == order_type)
    if table_id is not None:
        q = q.filter(models.RestaurantOrder.table_id == table_id)
    if order_date is not None:
        q = q.filter(models.RestaurantOrder.order_date == order_date)
    rows = q.order_by(models.RestaurantOrder.id.desc()).all()

    # Where the order is being served. The orders screen was resolving table_id
    # against a separately-fetched table list, so a slow or failed second
    # request left the column showing "-" for every dine-in order.
    table_ids = {r.table_id for r in rows if r.table_id}
    tables = (
        db.query(models.RestaurantTable).filter(models.RestaurantTable.id.in_(table_ids)).all()
        if table_ids
        else []
    )
    table_by_id = {t.id: t for t in tables}

    data = []
    for r in rows:
        table = table_by_id.get(r.table_id)
        sub_total, grand_total = calculate_order_totals(db, r)
        data.append(
            {
                **r.__dict__,
                "sub_total": sub_total,
                "grand_total": grand_total,
                "table_name": table.table_name if table else None,
                "table_code": table.table_code if table else None,
                # One label for the "where" column, whichever kind of order it
                # is: a table for dine-in, a room number for room service, and
                # the order type itself for takeaway and delivery, which have
                # neither.
                "service_location": (
                    r.room_no
                    if r.order_type == "Room Service"
                    else (f"{table.table_name} ({table.table_code})" if table else r.order_type)
                ),
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/order/{order_id}", status_code=status.HTTP_200_OK)
def get_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = (
        db.query(models.RestaurantOrder)
        .filter(models.RestaurantOrder.id == order_id, models.RestaurantOrder.company_id == company_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    items = (
        db.query(models.RestaurantOrderItem)
        .filter(models.RestaurantOrderItem.order_id == order_id, models.RestaurantOrderItem.status == STATUS)
        .all()
    )

    # The line item stores menu_id but snapshots only the variant name and the
    # price, so the order screen was resolving the dish name against a
    # separately-fetched menu list and printing "#42" whenever that missed.
    menu_ids = {i.menu_id for i in items if i.menu_id}
    menus = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id.in_(menu_ids), models.RestaurantMenu.company_id == company_id)
        .all()
        if menu_ids
        else []
    )
    menu_name_by_id = {m.id: m.item_name for m in menus}
    item_pricing = pricing_for_items(db, items)
    sub_total, grand_total = _totals_for_pricing(order, item_pricing)
    modifier_total = _modifier_total_for_items(items, item_pricing)
    item_data = [
        _order_item_data(i, menu_name_by_id.get(i.menu_id), item_pricing[i.id]) for i in items
    ]
    # Return the same values used by the calculator, even for an order created
    # before modifier pricing was fixed and still carrying an old stored total.
    return {
        "status": "success",
        "data": {
            **order.__dict__,
            "sub_total": sub_total,
            "modifier_total": modifier_total,
            "grand_total": grand_total,
            "items": item_data,
        },
    }


@router.post("/order/{order_id}/items", status_code=status.HTTP_201_CREATED)
def add_order_items(order_id: int, payload: OrderItemsIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = (
        db.query(models.RestaurantOrder)
        .filter(models.RestaurantOrder.id == order_id, models.RestaurantOrder.company_id == company_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.order_status in ("Completed", "Cancelled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot add items to a {order.order_status} order")

    try:
        created = []
        for item in payload.items:
            if item.quantity < 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity must be at least 1")
            menu, price, kitchen, variant = _resolve_price_and_kitchen(db, company_id, user_id, item)
            row = models.RestaurantOrderItem(
                order_id=order.id,
                menu_id=menu.id,
                kitchen_id=kitchen.id,
                quantity=item.quantity,
                price=price,
                item_status="Pending",
                special_instructions=item.special_instructions,
                variant_id=item.variant_id,
                variant_name=variant.variant_name if variant else None,
                created_by=user_id,
                company_id=company_id,
            )
            db.add(row)
            db.flush()
            created.append(row)

            for modifier_id in (item.modifier_ids or []):
                modifier = (
                    db.query(models.MenuModifier)
                    .filter(models.MenuModifier.id == modifier_id, models.MenuModifier.menu_id == menu.id)
                    .first()
                )
                if not modifier:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"modifier_id {modifier_id} does not match menu_id")
                db.add(models.RestaurantOrderItemModifier(
                    order_item_id=row.id,
                    modifier_id=modifier.id,
                    modifier_name=modifier.modifier_name,
                    price=modifier.price,
                    company_id=company_id,
                ))

        db.flush()
        _recalculate_totals(db, order)
        db.commit()
        return {"status": "success", "count": len(created), "data": [c.id for c in created]}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.put("/order/item/{order_item_id}", status_code=status.HTTP_200_OK)
def update_order_item(order_item_id: int, payload: OrderItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.RestaurantOrderItem)
        .filter(models.RestaurantOrderItem.id == order_item_id, models.RestaurantOrderItem.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_by = user_id
    db.flush()
    order = db.query(models.RestaurantOrder).filter(models.RestaurantOrder.id == item.order_id).first()
    if order:
        _recalculate_totals(db, order)
    db.commit()
    return {"status": "success", "message": "Order item updated"}


@router.delete("/order/item/{order_item_id}", status_code=status.HTTP_200_OK)
def cancel_order_item(order_item_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.RestaurantOrderItem)
        .filter(models.RestaurantOrderItem.id == order_item_id, models.RestaurantOrderItem.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    item.status = UNSTATUS
    item.item_status = "Cancelled"
    item.updated_by = user_id
    db.flush()
    order = db.query(models.RestaurantOrder).filter(models.RestaurantOrder.id == item.order_id).first()
    if order:
        _recalculate_totals(db, order)
    db.commit()
    return {"status": "success", "message": "Order item cancelled"}


# =====================================================
# ORDER CONFIRM -> GENERATE KOTs (split by kitchen)
# =====================================================
@router.post("/order/{order_id}/confirm", status_code=status.HTTP_201_CREATED)
def confirm_order(order_id: int, payload: OrderConfirmIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = (
        db.query(models.RestaurantOrder)
        .filter(models.RestaurantOrder.id == order_id, models.RestaurantOrder.company_id == company_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    items = (
        db.query(models.RestaurantOrderItem)
        .filter(
            models.RestaurantOrderItem.order_id == order_id,
            models.RestaurantOrderItem.status == STATUS,
            models.RestaurantOrderItem.item_status == "Pending",
        )
        .all()
    )
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending items to send to the kitchen")

    is_supplementary = order.order_status in ("In Progress", "Ready", "Served")
    kot_type = "Supplementary" if is_supplementary else "Original"

    try:
        by_kitchen = {}
        for it in items:
            by_kitchen.setdefault(it.kitchen_id, []).append(it)

        created_kots = []
        for kitchen_id, kitchen_items in by_kitchen.items():
            parent_kot_id = None
            if is_supplementary:
                original = (
                    db.query(models.KitchenOrderTicket)
                    .filter(models.KitchenOrderTicket.order_id == order_id, models.KitchenOrderTicket.kitchen_id == kitchen_id)
                    .order_by(models.KitchenOrderTicket.id.asc())
                    .first()
                )
                parent_kot_id = original.id if original else None

            kot = models.KitchenOrderTicket(
                kot_number=gen_code("KOT"),
                order_id=order_id,
                parent_kot_id=parent_kot_id,
                kot_type=kot_type,
                kitchen_id=kitchen_id,
                kot_status="New",
                priority=payload.priority,
                created_by=user_id,
                company_id=company_id,
            )
            db.add(kot)
            db.flush()

            for it in kitchen_items:
                db.add(models.KitchenOrderItem(
                    kot_id=kot.id, order_item_id=it.id, preparation_status="Pending", created_by=user_id, company_id=company_id
                ))
                it.item_status = "Preparing"

            created_kots.append({"id": kot.id, "kot_number": kot.kot_number, "kitchen_id": kitchen_id})

        order.order_status = "In Progress"
        order.updated_by = user_id
        db.commit()
        return {"status": "success", "data": {"kots": created_kots}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.put("/order/{order_id}/status", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, payload: OrderStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = (
        db.query(models.RestaurantOrder)
        .filter(models.RestaurantOrder.id == order_id, models.RestaurantOrder.company_id == company_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    _assert_in(payload.order_status, ORDER_STATUSES, "order_status")

    order.order_status = payload.order_status
    order.updated_by = user_id

    if payload.order_status in ("Completed", "Cancelled") and order.table_code:
        table = (
            db.query(models.RestaurantTable)
            .filter(models.RestaurantTable.table_code == order.table_code, models.RestaurantTable.company_id == company_id)
            .first()
        )
        if table:
            table.table_status = "Cleaning" if payload.order_status == "Completed" else "Available"
            table.current_order_id = None
            table.updated_by = user_id

    db.commit()
    return {"status": "success", "message": "Order status updated"}

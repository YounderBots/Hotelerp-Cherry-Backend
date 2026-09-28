import logging
import math
import re
import uuid
from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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
ORDER_TYPES = ("At Table", "At Counter", "Takeaway")
ORDER_STATUSES = ("New", "In Progress", "Ready", "Served", "Completed", "Cancelled")


def _assert_in(value, allowed, field):
    if value not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field} must be one of: {', '.join(allowed)}",
        )


ORDER_TRANSITIONS = {
    "New": {"In Progress", "Cancelled"},
    "In Progress": {"Ready", "Served", "Cancelled"},
    "Ready": {"Served", "Cancelled"},
    "Served": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


def _validate_order_values(*, order_type, table_id, guest_mobile=None, no_of_guests=None,
                           guest_name=None, phone_region=None):
    if order_type not in ORDER_TYPES:
        raise HTTPException(status_code=400, detail="order_type is invalid")
    if order_type == "At Table" and not table_id:
        raise HTTPException(status_code=400, detail="table_id is required for At Table orders")
    if order_type != "At Table" and table_id:
        raise HTTPException(status_code=400, detail="table_id is only valid for At Table orders")
    if guest_name is not None and len(str(guest_name).strip()) > 100:
        raise HTTPException(status_code=400, detail="guest_name must not exceed 100 characters")
    # Country-aware, stored as E.164. This was `re.fullmatch(r"\d{10}", ...)`,
    # which refused every guest outside the home country and every number typed
    # in international format (C-086). The order is matched against a guest by
    # this same value, so it has to be canonical to find the right guest.
    guest_mobile = normalize_phone(guest_mobile, field="guest_mobile",
                                   default_region=phone_region)
    if no_of_guests is not None and int(no_of_guests) < 1:
        raise HTTPException(status_code=400, detail="no_of_guests must be at least one")
    return guest_mobile


# =====================================================
# SCHEMAS
# =====================================================
class OrderIn(BaseModel):
    order_type: str  # At Table | At Counter | Takeaway
    table_id: Optional[int] = None
    guest_name: Optional[str] = None
    guest_mobile: Optional[str] = None
    # ISO-3166-1 alpha-2 country the mobile was typed in. A national number
    # with no country code is ambiguous and the API will not guess one; see
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
    priority: Optional[str] = "Normal"


class OrderStatusIn(BaseModel):
    order_status: str


# =====================================================
# HELPERS
# =====================================================
def _resolve_price_and_station(db: Session, company_id: str, item: OrderItemIn):
    menu = db.query(models.BarMenuItem).filter(
        models.BarMenuItem.id == item.menu_id,
        models.BarMenuItem.company_id == company_id,
        models.BarMenuItem.status == STATUS,
    ).first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"menu_id {item.menu_id} does not exist")
    if menu.availability_status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{menu.item_name} is not available")

    price = menu.price
    variant = None
    if item.variant_id:
        variant = (
            db.query(models.BarMenuVariant)
            .filter(
                models.BarMenuVariant.id == item.variant_id,
                models.BarMenuVariant.menu_id == item.menu_id,
                models.BarMenuVariant.company_id == company_id,
                models.BarMenuVariant.status == STATUS,
            )
            .first()
        )
        if not variant:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="variant_id does not match menu_id")
        price = variant.price

    station = db.query(models.BarStation).filter(
        models.BarStation.id == menu.station_id,
        models.BarStation.company_id == company_id,
        models.BarStation.status == STATUS,
        models.BarStation.is_active == True,
    ).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{menu.item_name} has no valid bar station configured")
    return menu, price, station, variant


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


def _modifier_rows_by_item(db: Session, items: List[models.BarOrderItem]):
    """Load persisted modifier snapshots once for a set of order lines."""
    item_ids = [item.id for item in items if item.id is not None]
    rows_by_item: Dict[int, List[models.BarOrderItemModifier]] = {
        item.id: [] for item in items if item.id is not None
    }
    if not item_ids:
        return rows_by_item
    rows = (
        db.query(models.BarOrderItemModifier)
        .filter(models.BarOrderItemModifier.order_item_id.in_(item_ids))
        .order_by(models.BarOrderItemModifier.id.asc())
        .all()
    )
    for row in rows:
        rows_by_item.setdefault(row.order_item_id, []).append(row)
    return rows_by_item


def pricing_for_items(db: Session, items: List[models.BarOrderItem]):
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


def _modifier_total_for_items(items: List[models.BarOrderItem], pricing: dict):
    return _money(
        sum(
            pricing[item.id]["modifier_total"] * _finite_number(item.quantity, "quantity")
            for item in items
        )
    )


def _totals_for_pricing(order: models.BarOrder, pricing: dict):
    sub_total = _money(sum(row["line_total"] for row in pricing.values()))
    grand_total = _money(
        sub_total
        + _finite_number(order.tax_amount, "tax_amount")
        + _finite_number(order.service_charge, "service_charge")
        - _finite_number(order.discount_amount, "discount_amount")
    )
    return sub_total, grand_total


def calculate_order_totals(db: Session, order: models.BarOrder):
    """Calculate an order from persisted base prices and modifier snapshots."""
    items = (
        db.query(models.BarOrderItem)
        .filter(models.BarOrderItem.order_id == order.id, models.BarOrderItem.status == STATUS)
        .all()
    )
    pricing = pricing_for_items(db, items)
    return _totals_for_pricing(order, pricing)


def _recalculate_totals(db: Session, order: models.BarOrder):
    sub_total, grand_total = calculate_order_totals(db, order)
    order.sub_total = sub_total
    order.grand_total = grand_total
    return sub_total, grand_total


def _modifier_data(modifier: models.BarOrderItemModifier):
    return {
        "id": modifier.id,
        "order_item_id": modifier.order_item_id,
        "modifier_id": modifier.modifier_id,
        "modifier_name": modifier.modifier_name,
        "price": _finite_number(modifier.price, "modifier price"),
    }


def _order_item_data(item: models.BarOrderItem, item_name: Optional[str], item_pricing: dict):
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

    guest_mobile = _validate_order_values(
        order_type=payload.order_type,
        table_id=payload.table_id,
        guest_mobile=payload.guest_mobile,
        no_of_guests=payload.no_of_guests,
        guest_name=payload.guest_name,
        phone_region=payload.phone_region,
    )

    table = None
    if payload.table_id:
        table = (
            db.query(models.BarTable)
            .filter(
                models.BarTable.id == payload.table_id,
                models.BarTable.company_id == company_id,
                models.BarTable.status == STATUS,
            )
            .with_for_update()
            .first()
        )
        if not table:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id does not exist")
        if table.table_status != "Available" or table.current_order_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table is not available")

    guest = None
    if guest_mobile:
        # Matched on the canonical E.164 form, so an order typed as
        # "+91 98765 43210" finds the guest stored as +919876543210.
        guest = (
            db.query(models.BarGuest)
            .filter(models.BarGuest.mobile == guest_mobile, models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
            .first()
        )

    try:
        now = datetime.now()
        # `phone_region` exists so the number could be read; it is not a column.
        order_values = payload.dict(exclude={"phone_region"})
        if guest_mobile:
            order_values["guest_mobile"] = guest_mobile
        order = models.BarOrder(
            order_number=gen_code("BORD"),
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
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Table already has an active order")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/order", status_code=status.HTTP_200_OK)
def list_orders(
    request: Request,
    order_status_filter: Optional[str] = Query(None, alias="order_status"),
    order_type: Optional[str] = Query(None),
    table_id: Optional[int] = Query(None),
    order_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarOrder).filter(models.BarOrder.company_id == company_id, models.BarOrder.status == STATUS)
    if order_status_filter:
        q = q.filter(models.BarOrder.order_status == order_status_filter)
    if order_type:
        q = q.filter(models.BarOrder.order_type == order_type)
    if table_id is not None:
        q = q.filter(models.BarOrder.table_id == table_id)
    if order_date is not None:
        q = q.filter(models.BarOrder.order_date == order_date)
    rows = q.order_by(models.BarOrder.id.desc()).all()

    # Where the order is being served. The orders screen was resolving table_id
    # against a separately-fetched table list, so a slow or failed second
    # request left the column showing "-" for every at-table order.
    table_ids = {r.table_id for r in rows if r.table_id}
    tables = (
        db.query(models.BarTable)
        .filter(
            models.BarTable.id.in_(table_ids),
            models.BarTable.company_id == company_id,
            models.BarTable.status == STATUS,
        )
        .all()
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
                # One label for the "where" column: the table when there is
                # one, and the order type itself for counter and takeaway
                # orders, which have none.
                "service_location": (
                    f"{table.table_name} ({table.table_code})" if table else r.order_type
                ),
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/order/{order_id}", status_code=status.HTTP_200_OK)
def get_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = db.query(models.BarOrder).filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    items = db.query(models.BarOrderItem).filter(models.BarOrderItem.order_id == order_id, models.BarOrderItem.status == STATUS).all()

    # The line item stores menu_id but snapshots only the variant name and the
    # price, so the order screen was resolving the drink name against a
    # separately-fetched menu list and printing "#42" whenever that missed.
    menu_ids = {i.menu_id for i in items if i.menu_id}
    menus = (
        db.query(models.BarMenuItem)
        .filter(models.BarMenuItem.id.in_(menu_ids), models.BarMenuItem.company_id == company_id)
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
        db.query(models.BarOrder)
        .filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id, models.BarOrder.status == STATUS)
        .with_for_update()
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if not payload.items:
        raise HTTPException(status_code=400, detail="At least one order item is required")
    if order.order_status in ("Completed", "Cancelled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot add items to a {order.order_status} order")

    try:
        created = []
        for item in payload.items:
            if item.quantity < 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity must be at least 1")
            menu, price, station, variant = _resolve_price_and_station(db, company_id, item)
            row = models.BarOrderItem(
                order_id=order.id,
                menu_id=menu.id,
                station_id=station.id,
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

            modifier_ids = item.modifier_ids or []
            if len(set(modifier_ids)) != len(modifier_ids):
                raise HTTPException(status_code=400, detail="A modifier can only be selected once")
            for modifier_id in modifier_ids:
                modifier = db.query(models.BarMenuModifier).filter(
                    models.BarMenuModifier.id == modifier_id,
                    models.BarMenuModifier.menu_id == menu.id,
                    models.BarMenuModifier.company_id == company_id,
                    models.BarMenuModifier.status == STATUS,
                ).first()
                if not modifier:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"modifier_id {modifier_id} does not match menu_id")
                db.add(models.BarOrderItemModifier(
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
        db.query(models.BarOrderItem)
        .filter(
            models.BarOrderItem.id == order_item_id,
            models.BarOrderItem.company_id == company_id,
            models.BarOrderItem.status == STATUS,
        )
        .with_for_update()
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    order = db.query(models.BarOrder).filter(models.BarOrder.id == item.order_id, models.BarOrder.company_id == company_id).first()
    if not order or order.order_status in ("Completed", "Cancelled"):
        raise HTTPException(status_code=400, detail="Cannot update an item on a terminal order")
    updates = payload.dict(exclude_unset=True)
    if updates.get("quantity") is not None and int(updates["quantity"]) < 1:
        raise HTTPException(status_code=400, detail="quantity must be at least 1")
    if updates.get("item_status") is not None and updates["item_status"] not in {"Pending", "Preparing", "Ready", "Served", "Cancelled"}:
        raise HTTPException(status_code=400, detail="item_status is invalid")
    for field, value in updates.items():
        setattr(item, field, value)
    item.updated_by = user_id
    db.flush()
    order = db.query(models.BarOrder).filter(models.BarOrder.id == item.order_id).first()
    if order:
        _recalculate_totals(db, order)
    db.commit()
    return {"status": "success", "message": "Order item updated"}


@router.delete("/order/item/{order_item_id}", status_code=status.HTTP_200_OK)
def cancel_order_item(order_item_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.BarOrderItem)
        .filter(
            models.BarOrderItem.id == order_item_id,
            models.BarOrderItem.company_id == company_id,
            models.BarOrderItem.status == STATUS,
        )
        .with_for_update()
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    order = db.query(models.BarOrder).filter(models.BarOrder.id == item.order_id, models.BarOrder.company_id == company_id).first()
    if not order or order.order_status in ("Completed", "Cancelled"):
        raise HTTPException(status_code=400, detail="Cannot remove an item from a terminal order")
    item.status = UNSTATUS
    item.item_status = "Cancelled"
    item.updated_by = user_id
    db.flush()
    order = db.query(models.BarOrder).filter(models.BarOrder.id == item.order_id).first()
    if order:
        _recalculate_totals(db, order)
    db.commit()
    return {"status": "success", "message": "Order item cancelled"}


# =====================================================
# ORDER CONFIRM -> GENERATE BOTs (split by station)
# =====================================================
@router.post("/order/{order_id}/confirm", status_code=status.HTTP_201_CREATED)
def confirm_order(order_id: int, payload: OrderConfirmIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = (
        db.query(models.BarOrder)
        .filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id, models.BarOrder.status == STATUS)
        .with_for_update()
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.order_status in ("Completed", "Cancelled"):
        raise HTTPException(status_code=400, detail=f"Cannot confirm a {order.order_status} order")

    items = (
        db.query(models.BarOrderItem)
        .filter(
            models.BarOrderItem.order_id == order_id,
            models.BarOrderItem.company_id == company_id,
            models.BarOrderItem.status == STATUS,
            models.BarOrderItem.item_status == "Pending",
        )
        .with_for_update()
        .all()
    )
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending items to send to the bar")

    is_supplementary = order.order_status in ("In Progress", "Ready", "Served")
    bot_type = "Supplementary" if is_supplementary else "Original"

    try:
        by_station = {}
        for it in items:
            by_station.setdefault(it.station_id, []).append(it)

        created_bots = []
        for station_id, station_items in by_station.items():
            parent_bot_id = None
            if is_supplementary:
                original = (
                    db.query(models.BarOrderTicket)
                    .filter(models.BarOrderTicket.order_id == order_id, models.BarOrderTicket.station_id == station_id)
                    .order_by(models.BarOrderTicket.id.asc())
                    .first()
                )
                parent_bot_id = original.id if original else None

            bot = models.BarOrderTicket(
                bot_number=gen_code("BOT"),
                order_id=order_id,
                parent_bot_id=parent_bot_id,
                bot_type=bot_type,
                station_id=station_id,
                bot_status="New",
                priority=payload.priority,
                created_by=user_id,
                company_id=company_id,
            )
            db.add(bot)
            db.flush()

            for it in station_items:
                db.add(models.BarOrderTicketItem(
                    bot_id=bot.id, order_item_id=it.id, preparation_status="Pending", created_by=user_id, company_id=company_id
                ))
                it.item_status = "Preparing"

            created_bots.append({"id": bot.id, "bot_number": bot.bot_number, "station_id": station_id})

        order.order_status = "In Progress"
        order.updated_by = user_id
        db.commit()
        return {"status": "success", "data": {"bots": created_bots}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.put("/order/{order_id}/status", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, payload: OrderStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = (
        db.query(models.BarOrder)
        .filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id, models.BarOrder.status == STATUS)
        .with_for_update()
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    _assert_in(payload.order_status, ORDER_STATUSES, "order_status")
    if payload.order_status != order.order_status and payload.order_status not in ORDER_TRANSITIONS.get(order.order_status, set()):
        raise HTTPException(status_code=400, detail=f"Cannot transition order from {order.order_status} to {payload.order_status}")

    order.order_status = payload.order_status
    order.updated_by = user_id

    if payload.order_status in ("Completed", "Cancelled") and order.table_id:
        table = db.query(models.BarTable).filter(
            models.BarTable.id == order.table_id,
            models.BarTable.company_id == company_id,
            models.BarTable.status == STATUS,
        ).with_for_update().first()
        if table:
            table.table_status = "Cleaning" if payload.order_status == "Completed" else "Available"
            table.current_order_id = None
            table.updated_by = user_id

    tickets = (
        db.query(models.BarOrderTicket)
        .filter(
            models.BarOrderTicket.order_id == order.id,
            models.BarOrderTicket.company_id == company_id,
            models.BarOrderTicket.status == STATUS,
        )
        .with_for_update()
        .all()
    )
    if payload.order_status == "Completed" and any(
        ticket.bot_status not in ("Completed", "Cancelled") for ticket in tickets
    ):
        raise HTTPException(status_code=409, detail="Complete or cancel all station tickets first")
    if payload.order_status == "Cancelled":
        for ticket in tickets:
            if ticket.bot_status not in ("Completed", "Cancelled"):
                ticket.bot_status = "Cancelled"
                ticket.updated_by = user_id
                ticket_items = (
                    db.query(models.BarOrderTicketItem)
                    .filter(
                        models.BarOrderTicketItem.bot_id == ticket.id,
                        models.BarOrderTicketItem.company_id == company_id,
                    )
                    .with_for_update()
                    .all()
                )
                for item in ticket_items:
                    if item.preparation_status != "Ready":
                        item.preparation_status = "Cancelled"

    db.commit()
    return {"status": "success", "message": "Order status updated"}

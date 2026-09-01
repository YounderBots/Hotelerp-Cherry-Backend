import uuid
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import get_db, models
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

STATUS = CommonWords.STATUS
UNSTATUS = CommonWords.UNSTATUS


def gen_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


# =====================================================
# SCHEMAS
# =====================================================
class OrderIn(BaseModel):
    order_type: str  # At Table | At Counter | Takeaway
    table_id: Optional[int] = None
    guest_name: Optional[str] = None
    guest_mobile: Optional[str] = None
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


class OrderItemsIn(BaseModel):
    items: List[OrderItemIn]


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    item_status: Optional[str] = None


class OrderConfirmIn(BaseModel):
    priority: Optional[str] = "Normal"


class OrderStatusIn(BaseModel):
    order_status: str


# =====================================================
# HELPERS
# =====================================================
def _resolve_price_and_station(db: Session, company_id: str, item: OrderItemIn):
    menu = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == item.menu_id, models.BarMenuItem.company_id == company_id).first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"menu_id {item.menu_id} does not exist")
    if menu.availability_status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{menu.item_name} is not available")

    price = menu.price
    variant = None
    if item.variant_id:
        variant = (
            db.query(models.BarMenuVariant)
            .filter(models.BarMenuVariant.id == item.variant_id, models.BarMenuVariant.menu_id == item.menu_id)
            .first()
        )
        if not variant:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="variant_id does not match menu_id")
        price = variant.price

    station = db.query(models.BarStation).filter(models.BarStation.id == menu.station_id, models.BarStation.company_id == company_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{menu.item_name} has no valid bar station configured")
    return menu, price, station, variant


def _recalculate_totals(db: Session, order: models.BarOrder):
    items = db.query(models.BarOrderItem).filter(models.BarOrderItem.order_id == order.id, models.BarOrderItem.status == STATUS).all()
    sub_total = sum((i.price or 0) * (i.quantity or 0) for i in items)
    order.sub_total = sub_total
    order.grand_total = sub_total + (order.tax_amount or 0) + (order.service_charge or 0) - (order.discount_amount or 0)


# =====================================================
# ORDERS
# =====================================================
@router.post("/order", status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)

    if payload.order_type == "At Table" and not payload.table_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id is required for At Table orders")

    table = None
    if payload.table_id:
        table = db.query(models.BarTable).filter(models.BarTable.id == payload.table_id, models.BarTable.company_id == company_id).first()
        if not table:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id does not exist")
        if table.table_status == "Occupied" and table.current_order_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table already has an active order")

    guest = None
    if payload.guest_mobile:
        guest = (
            db.query(models.BarGuest)
            .filter(models.BarGuest.mobile == payload.guest_mobile, models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
            .first()
        )

    try:
        now = datetime.now()
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
            **payload.dict(),
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
        db.query(models.BarTable).filter(models.BarTable.id.in_(table_ids)).all()
        if table_ids
        else []
    )
    table_by_id = {t.id: t for t in tables}

    data = []
    for r in rows:
        table = table_by_id.get(r.table_id)
        data.append(
            {
                **r.__dict__,
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
        db.query(models.BarMenuItem).filter(models.BarMenuItem.id.in_(menu_ids)).all()
        if menu_ids
        else []
    )
    menu_name_by_id = {m.id: m.item_name for m in menus}
    item_data = [{**i.__dict__, "item_name": menu_name_by_id.get(i.menu_id)} for i in items]
    return {"status": "success", "data": {**order.__dict__, "items": item_data}}


@router.post("/order/{order_id}/items", status_code=status.HTTP_201_CREATED)
def add_order_items(order_id: int, payload: OrderItemsIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = db.query(models.BarOrder).filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
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

            for modifier_id in (item.modifier_ids or []):
                modifier = db.query(models.BarMenuModifier).filter(models.BarMenuModifier.id == modifier_id, models.BarMenuModifier.menu_id == menu.id).first()
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/order/item/{order_item_id}", status_code=status.HTTP_200_OK)
def update_order_item(order_item_id: int, payload: OrderItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = db.query(models.BarOrderItem).filter(models.BarOrderItem.id == order_item_id, models.BarOrderItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    for field, value in payload.dict(exclude_unset=True).items():
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
    item = db.query(models.BarOrderItem).filter(models.BarOrderItem.id == order_item_id, models.BarOrderItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
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
    order = db.query(models.BarOrder).filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    items = (
        db.query(models.BarOrderItem)
        .filter(models.BarOrderItem.order_id == order_id, models.BarOrderItem.status == STATUS, models.BarOrderItem.item_status == "Pending")
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/order/{order_id}/status", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, payload: OrderStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = db.query(models.BarOrder).filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.order_status = payload.order_status
    order.updated_by = user_id

    if payload.order_status in ("Completed", "Cancelled") and order.table_code:
        table = db.query(models.BarTable).filter(models.BarTable.table_code == order.table_code, models.BarTable.company_id == company_id).first()
        if table:
            table.table_status = "Cleaning" if payload.order_status == "Completed" else "Available"
            table.current_order_id = None
            table.updated_by = user_id

    db.commit()
    return {"status": "success", "message": "Order status updated"}

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_committed_value

from models import get_db, models
from resources.utils import verify_authentication
from resources.inventoryController import (
    InsufficientStockError,
    InventoryDeductionError,
    deduct_stock_for_menu_item,
)
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

BOT_STATUSES = ("New", "Acknowledged", "In Progress", "Completed", "Cancelled")
BOT_ITEM_STATUSES = ("Pending", "Preparing", "Ready", "Cancelled")
BOT_TRANSITIONS = {
    "New": {"Acknowledged", "In Progress", "Completed", "Cancelled"},
    "Acknowledged": {"In Progress", "Completed", "Cancelled"},
    "In Progress": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


def _assert_status(value: str, allowed, field: str) -> None:
    if value not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field} must be one of: {', '.join(allowed)}",
        )


def _locked_bot(db: Session, bot_id: int, company_id: str):
    return (
        db.query(models.BarOrderTicket)
        .filter(models.BarOrderTicket.id == bot_id, models.BarOrderTicket.company_id == company_id)
        .populate_existing()
        .with_for_update()
        .first()
    )


def _claim_bot_item(db: Session, bot_item_id: int, ready_at: datetime) -> int:
    """Atomically claim one non-terminal item for its one inventory deduction."""
    return (
        db.query(models.BarOrderTicketItem)
        .filter(
            models.BarOrderTicketItem.id == bot_item_id,
            models.BarOrderTicketItem.preparation_status.notin_(["Ready", "Cancelled"]),
        )
        .update(
            {
                models.BarOrderTicketItem.preparation_status: "Ready",
                models.BarOrderTicketItem.prep_end_time: ready_at,
            },
            synchronize_session=False,
        )
    )


def _claim_order_item(db: Session, order_item_id: int) -> int:
    """Claim the order line as the cross-ticket idempotency marker."""
    return (
        db.query(models.BarOrderItem)
        .filter(
            models.BarOrderItem.id == order_item_id,
            models.BarOrderItem.status == STATUS,
            models.BarOrderItem.item_status.in_(["Pending", "Preparing"]),
        )
        .update({models.BarOrderItem.item_status: "Ready"}, synchronize_session=False)
    )


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
class StationIn(BaseModel):
    station_name: str
    printer_name: Optional[str] = None


class BotStatusIn(BaseModel):
    bot_status: str  # In Progress | Completed | Cancelled


class BotItemStatusIn(BaseModel):
    preparation_status: str  # Preparing | Ready


# =====================================================
# BAR STATIONS
# =====================================================
@router.post("/station", status_code=status.HTTP_201_CREATED)
def create_station(payload: StationIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    station = models.BarStation(station_code=gen_code("BST"), is_active=True, created_by=user_id, company_id=company_id, **payload.dict())
    db.add(station)
    db.commit()
    db.refresh(station)
    return {"status": "success", "data": {"id": station.id, "station_code": station.station_code}}


@router.get("/station", status_code=status.HTTP_200_OK)
def list_stations(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = db.query(models.BarStation).filter(models.BarStation.company_id == company_id, models.BarStation.status == STATUS).all()
    return {"status": "success", "count": len(rows), "data": rows}


# =====================================================
# BOT LIST / DETAIL
# =====================================================
def _bot_with_items(db: Session, bot: models.BarOrderTicket):
    bot_items = (
        db.query(models.BarOrderTicketItem)
        .filter(
            models.BarOrderTicketItem.bot_id == bot.id,
            models.BarOrderTicketItem.company_id == bot.company_id,
        )
        .all()
    )
    order_item_ids = [bi.order_item_id for bi in bot_items]
    order_items = (
        db.query(models.BarOrderItem)
        .filter(
            models.BarOrderItem.id.in_(order_item_ids),
            models.BarOrderItem.company_id == bot.company_id,
        )
        .all()
        if order_item_ids
        else []
    )
    order_items_by_id = {oi.id: oi for oi in order_items}
    menu_ids = [oi.menu_id for oi in order_items]
    menus = (
        db.query(models.BarMenuItem)
        .filter(
            models.BarMenuItem.id.in_(menu_ids),
            models.BarMenuItem.company_id == bot.company_id,
        )
        .all()
        if menu_ids
        else []
    )
    menu_by_id = {m.id: m for m in menus}

    modifiers = (
        db.query(models.BarOrderItemModifier)
        .filter(
            models.BarOrderItemModifier.order_item_id.in_(order_item_ids),
            models.BarOrderItemModifier.company_id == bot.company_id,
        )
        .all()
        if order_item_ids
        else []
    )
    modifiers_by_item = {}
    for m in modifiers:
        modifiers_by_item.setdefault(m.order_item_id, []).append(m.modifier_name)

    items = []
    for bi in bot_items:
        oi = order_items_by_id.get(bi.order_item_id)
        menu = menu_by_id.get(oi.menu_id) if oi else None
        items.append(
            {
                "bot_item_id": bi.id,
                "order_item_id": bi.order_item_id,
                "item_name": menu.item_name if menu else None,
                "quantity": oi.quantity if oi else None,
                "preparation_status": bi.preparation_status,
                "prep_start_time": bi.prep_start_time,
                "prep_end_time": bi.prep_end_time,
                "special_instructions": oi.special_instructions if oi else None,
                "variant_name": oi.variant_name if oi else None,
                "modifiers": modifiers_by_item.get(bi.order_item_id, []),
            }
        )

    order = db.query(models.BarOrder).filter(
        models.BarOrder.id == bot.order_id,
        models.BarOrder.company_id == bot.company_id,
    ).first()
    return {
        **bot.__dict__,
        # The station display was showing the raw bar_order.id in a column
        # headed "Order ID". order_number is the code printed on the ticket.
        "order_number": order.order_number if order else None,
        "table_code": order.table_code if order else None,
        "no_of_guests": order.no_of_guests if order else None,
        "items": items,
    }


@router.get("/bot", status_code=status.HTTP_200_OK)
def list_bots(
    request: Request,
    station_id: Optional[int] = Query(None),
    bot_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarOrderTicket).filter(models.BarOrderTicket.company_id == company_id, models.BarOrderTicket.status == STATUS)
    if station_id is not None:
        q = q.filter(models.BarOrderTicket.station_id == station_id)
    if bot_status:
        q = q.filter(models.BarOrderTicket.bot_status == bot_status)
    else:
        q = q.filter(models.BarOrderTicket.bot_status.notin_(["Completed", "Cancelled"]))
    bots = q.order_by(models.BarOrderTicket.id.asc()).all()
    return {"status": "success", "count": len(bots), "data": [_bot_with_items(db, b) for b in bots]}


@router.get("/bot/{bot_id}", status_code=status.HTTP_200_OK)
def get_bot(bot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = db.query(models.BarOrderTicket).filter(
        models.BarOrderTicket.id == bot_id,
        models.BarOrderTicket.company_id == company_id,
        models.BarOrderTicket.status == STATUS,
    ).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")
    return {"status": "success", "data": _bot_with_items(db, bot)}


# =====================================================
# BOT LIFECYCLE
# =====================================================
@router.put("/bot/{bot_id}/acknowledge", status_code=status.HTTP_200_OK)
def acknowledge_bot(bot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = _locked_bot(db, bot_id, company_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")
    if bot.bot_status not in ("New", "Acknowledged"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A {bot.bot_status} BOT cannot be acknowledged",
        )
    bot.bot_status = "Acknowledged"
    bot.acknowledged_by = user_id
    bot.acknowledged_at = bot.acknowledged_at or datetime.now()
    bot.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "BOT acknowledged"}


@router.put("/bot/{bot_id}/status", status_code=status.HTTP_200_OK)
def update_bot_status(bot_id: int, payload: BotStatusIn, request: Request, db: Session = Depends(get_db)):
    """Complete a BOT once; retries are successful no-ops."""
    user_id, role_id, company_id = _auth(request)
    _assert_status(payload.bot_status, BOT_STATUSES, "bot_status")
    bot = _locked_bot(db, bot_id, company_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")

    if payload.bot_status != bot.bot_status and payload.bot_status not in BOT_TRANSITIONS.get(bot.bot_status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A {bot.bot_status} BOT cannot be changed to {payload.bot_status}",
        )
    if payload.bot_status == bot.bot_status:
        db.commit()
        return {"status": "success", "message": f"BOT already {payload.bot_status}", "low_stock_alerts": []}
    try:
        linked_order = (
            db.query(models.BarOrder)
            .filter(
                models.BarOrder.id == bot.order_id,
                models.BarOrder.company_id == company_id,
                models.BarOrder.status == STATUS,
            )
            .with_for_update()
            .first()
        )
        if not linked_order:
            raise HTTPException(status_code=400, detail="Linked order is not active")
        if payload.bot_status == "Completed" and linked_order.order_status in ("Completed", "Cancelled"):
            raise HTTPException(status_code=400, detail=f"A {linked_order.order_status} order cannot complete a BOT")
        low_stock_alerts = []
        if payload.bot_status == "Completed":
            bot_items = (
                db.query(models.BarOrderTicketItem)
                .filter(models.BarOrderTicketItem.bot_id == bot_id)
                .order_by(models.BarOrderTicketItem.id.asc())
                .populate_existing()
                .with_for_update()
                .all()
            )
            order_item_ids = [bi.order_item_id for bi in bot_items]
            order_items = (
                db.query(models.BarOrderItem)
                .filter(models.BarOrderItem.id.in_(order_item_ids))
                .order_by(models.BarOrderItem.id.asc())
                .populate_existing()
                .with_for_update()
                .all()
                if order_item_ids
                else []
            )
            order_item_by_id = {item.id: item for item in order_items}
            for bi in bot_items:
                order_item = order_item_by_id.get(bi.order_item_id)
                if not order_item or order_item.status != STATUS:
                    continue
                ready_at = datetime.now()
                if _claim_bot_item(db, bi.id, ready_at) != 1:
                    continue
                if _claim_order_item(db, order_item.id) != 1:
                    # Another ticket already completed this order line.  The
                    # BOT still becomes ready, but it must not consume stock a
                    # second time.
                    db.refresh(order_item)
                    set_committed_value(
                        bi,
                        "preparation_status",
                        "Cancelled" if order_item.status != STATUS or order_item.item_status == "Cancelled" else "Ready",
                    )
                    set_committed_value(bi, "prep_end_time", ready_at)
                    continue
                set_committed_value(order_item, "item_status", "Ready")
                low_stock_alerts.extend(
                    deduct_stock_for_menu_item(
                        db,
                        company_id,
                        order_item.menu_id,
                        bot.station_id,
                        order_item.quantity,
                        bot.bot_number,
                        user_id,
                        source_order_item_id=order_item.id,
                    )
                )
                set_committed_value(bi, "preparation_status", "Ready")
                set_committed_value(bi, "prep_end_time", ready_at)

            bot.bot_status = "Completed"
            bot.completed_by = user_id
            bot.completed_at = bot.completed_at or datetime.now()
        elif payload.bot_status == "Cancelled":
            bot_items = (
                db.query(models.BarOrderTicketItem)
                .filter(models.BarOrderTicketItem.bot_id == bot_id)
                .order_by(models.BarOrderTicketItem.id.asc())
                .populate_existing()
                .with_for_update()
                .all()
            )
            for bi in bot_items:
                if bi.preparation_status != "Ready":
                    bi.preparation_status = "Cancelled"
            bot.bot_status = "Cancelled"
        else:
            bot.bot_status = payload.bot_status

        bot.updated_by = user_id
        db.commit()
        return {"status": "success", "message": f"BOT marked {payload.bot_status}", "low_stock_alerts": low_stock_alerts}
    except HTTPException:
        db.rollback()
        raise
    except InsufficientStockError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InventoryDeductionError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.put("/bot/item/{bot_item_id}/status", status_code=status.HTTP_200_OK)
def update_bot_item_status(bot_item_id: int, payload: BotItemStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    _assert_status(payload.preparation_status, BOT_ITEM_STATUSES, "preparation_status")

    bi = (
        db.query(models.BarOrderTicketItem)
        .filter(models.BarOrderTicketItem.id == bot_item_id, models.BarOrderTicketItem.company_id == company_id)
        .first()
    )
    if not bi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT item not found")
    bot = _locked_bot(db, bi.bot_id, company_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT item not found")
    bi = (
        db.query(models.BarOrderTicketItem)
        .filter(
            models.BarOrderTicketItem.id == bot_item_id,
            models.BarOrderTicketItem.bot_id == bot.id,
            models.BarOrderTicketItem.company_id == company_id,
        )
        .populate_existing()
        .with_for_update()
        .first()
    )
    if not bi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT item not found")

    if bot.bot_status == "Completed" and payload.preparation_status != "Ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A Completed BOT item cannot be changed")
    if payload.preparation_status == "Ready" and bi.preparation_status == "Ready":
        db.rollback()
        return {"status": "success", "message": "BOT item already Ready", "low_stock_alerts": []}
    if bi.preparation_status == "Ready" and payload.preparation_status != "Ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A Ready BOT item cannot be changed")
    if bi.preparation_status == "Cancelled" and payload.preparation_status == "Ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A Cancelled BOT item cannot become Ready")
    if bot.bot_status == "Cancelled" and payload.preparation_status == "Ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A Cancelled BOT cannot become Ready")

    try:
        low_stock_alerts = []
        if payload.preparation_status == "Preparing":
            bi.preparation_status = "Preparing"
            bi.prep_start_time = bi.prep_start_time or datetime.now()
        elif payload.preparation_status == "Cancelled":
            bi.preparation_status = "Cancelled"
        else:
            ready_at = datetime.now()
            if _claim_bot_item(db, bi.id, ready_at) != 1:
                db.refresh(bi)
                if bi.preparation_status == "Ready":
                    db.commit()
                    return {"status": "success", "message": "BOT item already Ready", "low_stock_alerts": []}
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="BOT item changed concurrently")

            order_item = (
                db.query(models.BarOrderItem)
                .filter(
                    models.BarOrderItem.id == bi.order_item_id,
                    models.BarOrderItem.company_id == company_id,
                )
                .populate_existing()
                .with_for_update()
                .first()
            )
            if not order_item or order_item.status != STATUS:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order item is not active")
            linked_order = db.query(models.BarOrder).filter(
                models.BarOrder.id == order_item.order_id,
                models.BarOrder.company_id == company_id,
                models.BarOrder.status == STATUS,
            ).with_for_update().first()
            if not linked_order or linked_order.order_status in ("Completed", "Cancelled"):
                raise HTTPException(status_code=400, detail="Linked order is not active")
            if _claim_order_item(db, order_item.id) != 1:
                db.refresh(order_item)
                if order_item.status == STATUS and order_item.item_status in ("Ready", "Served"):
                    set_committed_value(bi, "preparation_status", "Ready")
                    set_committed_value(bi, "prep_end_time", ready_at)
                    db.commit()
                    return {"status": "success", "message": "Order item already Ready", "low_stock_alerts": []}
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order item changed concurrently")
            set_committed_value(order_item, "item_status", "Ready")
            low_stock_alerts = deduct_stock_for_menu_item(
                db,
                company_id,
                order_item.menu_id,
                bot.station_id,
                order_item.quantity,
                bot.bot_number,
                user_id,
                source_order_item_id=order_item.id,
            )
            set_committed_value(bi, "preparation_status", "Ready")
            set_committed_value(bi, "prep_end_time", ready_at)

        db.commit()
        return {"status": "success", "message": "BOT item updated", "low_stock_alerts": low_stock_alerts}
    except HTTPException:
        db.rollback()
        raise
    except InsufficientStockError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InventoryDeductionError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.post("/bot/{bot_id}/print", status_code=status.HTTP_200_OK)
def print_bot(bot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = db.query(models.BarOrderTicket).filter(
        models.BarOrderTicket.id == bot_id,
        models.BarOrderTicket.company_id == company_id,
        models.BarOrderTicket.status == STATUS,
    ).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")
    bot.print_count = (bot.print_count or 0) + 1
    bot.printed_by = user_id
    db.commit()
    return {"status": "success", "print_count": bot.print_count}

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import get_db, models
from resources.utils import verify_authentication
from resources.inventoryController import deduct_stock_for_menu_item
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
    bot_items = db.query(models.BarOrderTicketItem).filter(models.BarOrderTicketItem.bot_id == bot.id).all()
    order_item_ids = [bi.order_item_id for bi in bot_items]
    order_items = (
        db.query(models.BarOrderItem).filter(models.BarOrderItem.id.in_(order_item_ids)).all() if order_item_ids else []
    )
    order_items_by_id = {oi.id: oi for oi in order_items}
    menu_ids = [oi.menu_id for oi in order_items]
    menus = db.query(models.BarMenuItem).filter(models.BarMenuItem.id.in_(menu_ids)).all() if menu_ids else []
    menu_by_id = {m.id: m for m in menus}

    modifiers = (
        db.query(models.BarOrderItemModifier).filter(models.BarOrderItemModifier.order_item_id.in_(order_item_ids)).all()
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

    order = db.query(models.BarOrder).filter(models.BarOrder.id == bot.order_id).first()
    return {
        **bot.__dict__,
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
        q = q.filter(models.BarOrderTicket.bot_status != "Completed")
    bots = q.order_by(models.BarOrderTicket.id.asc()).all()
    return {"status": "success", "count": len(bots), "data": [_bot_with_items(db, b) for b in bots]}


@router.get("/bot/{bot_id}", status_code=status.HTTP_200_OK)
def get_bot(bot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = db.query(models.BarOrderTicket).filter(models.BarOrderTicket.id == bot_id, models.BarOrderTicket.company_id == company_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")
    return {"status": "success", "data": _bot_with_items(db, bot)}


# =====================================================
# BOT LIFECYCLE
# =====================================================
@router.put("/bot/{bot_id}/acknowledge", status_code=status.HTTP_200_OK)
def acknowledge_bot(bot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = db.query(models.BarOrderTicket).filter(models.BarOrderTicket.id == bot_id, models.BarOrderTicket.company_id == company_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")
    bot.bot_status = "Acknowledged"
    bot.acknowledged_by = user_id
    bot.acknowledged_at = datetime.now()
    bot.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "BOT acknowledged"}


@router.put("/bot/{bot_id}/status", status_code=status.HTTP_200_OK)
def update_bot_status(bot_id: int, payload: BotStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = db.query(models.BarOrderTicket).filter(models.BarOrderTicket.id == bot_id, models.BarOrderTicket.company_id == company_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")

    try:
        bot.bot_status = payload.bot_status
        bot.updated_by = user_id
        if payload.bot_status == "Completed":
            bot.completed_by = user_id
            bot.completed_at = datetime.now()

        bot_items = db.query(models.BarOrderTicketItem).filter(models.BarOrderTicketItem.bot_id == bot_id).all()
        low_stock_alerts = []
        for bi in bot_items:
            if payload.bot_status == "Completed":
                bi.preparation_status = "Ready"
                bi.prep_end_time = datetime.now()
                order_item = db.query(models.BarOrderItem).filter(models.BarOrderItem.id == bi.order_item_id).first()
                if order_item:
                    order_item.item_status = "Ready"
                    alerts = deduct_stock_for_menu_item(db, company_id, order_item.menu_id, bot.station_id, order_item.quantity, bot.bot_number, user_id)
                    low_stock_alerts.extend(alerts)
            elif payload.bot_status == "Cancelled":
                bi.preparation_status = "Cancelled"

        db.commit()
        return {"status": "success", "message": f"BOT marked {payload.bot_status}", "low_stock_alerts": low_stock_alerts}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/bot/item/{bot_item_id}/status", status_code=status.HTTP_200_OK)
def update_bot_item_status(bot_item_id: int, payload: BotItemStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bi = db.query(models.BarOrderTicketItem).filter(models.BarOrderTicketItem.id == bot_item_id).first()
    if not bi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT item not found")
    bot = db.query(models.BarOrderTicket).filter(models.BarOrderTicket.id == bi.bot_id, models.BarOrderTicket.company_id == company_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT item not found")

    low_stock_alerts = []
    bi.preparation_status = payload.preparation_status
    if payload.preparation_status == "Preparing" and not bi.prep_start_time:
        bi.prep_start_time = datetime.now()
    if payload.preparation_status == "Ready":
        bi.prep_end_time = datetime.now()
        order_item = db.query(models.BarOrderItem).filter(models.BarOrderItem.id == bi.order_item_id).first()
        if order_item:
            order_item.item_status = "Ready"
            low_stock_alerts = deduct_stock_for_menu_item(db, company_id, order_item.menu_id, bot.station_id, order_item.quantity, bot.bot_number, user_id)

    db.commit()
    return {"status": "success", "message": "BOT item updated", "low_stock_alerts": low_stock_alerts}


@router.post("/bot/{bot_id}/print", status_code=status.HTTP_200_OK)
def print_bot(bot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bot = db.query(models.BarOrderTicket).filter(models.BarOrderTicket.id == bot_id, models.BarOrderTicket.company_id == company_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOT not found")
    bot.print_count = (bot.print_count or 0) + 1
    bot.printed_by = user_id
    db.commit()
    return {"status": "success", "print_count": bot.print_count}

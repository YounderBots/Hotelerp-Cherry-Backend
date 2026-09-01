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
class KitchenIn(BaseModel):
    kitchen_name: str
    kitchen_type: str  # Main | Grill | Dessert
    printer_name: Optional[str] = None


class KotStatusIn(BaseModel):
    kot_status: str  # In Progress | Completed | Cancelled


class KotItemStatusIn(BaseModel):
    preparation_status: str  # Preparing | Ready


# =====================================================
# KITCHENS
# =====================================================
@router.post("/kitchen", status_code=status.HTTP_201_CREATED)
def create_kitchen(payload: KitchenIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    kitchen = models.Kitchen(
        kitchen_code=gen_code("KTC"), is_active=True, created_by=user_id, company_id=company_id, **payload.dict()
    )
    db.add(kitchen)
    db.commit()
    db.refresh(kitchen)
    return {"status": "success", "data": {"id": kitchen.id, "kitchen_code": kitchen.kitchen_code}}


@router.get("/kitchen", status_code=status.HTTP_200_OK)
def list_kitchens(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.Kitchen)
        .filter(models.Kitchen.company_id == company_id, models.Kitchen.status == STATUS)
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


# =====================================================
# KOT LIST / DETAIL
# =====================================================
def _kot_with_items(db: Session, kot: models.KitchenOrderTicket):
    kot_items = db.query(models.KitchenOrderItem).filter(models.KitchenOrderItem.kot_id == kot.id).all()
    order_item_ids = [ki.order_item_id for ki in kot_items]
    order_items = (
        db.query(models.RestaurantOrderItem).filter(models.RestaurantOrderItem.id.in_(order_item_ids)).all()
        if order_item_ids
        else []
    )
    order_items_by_id = {oi.id: oi for oi in order_items}
    menu_ids = [oi.menu_id for oi in order_items]
    menus = db.query(models.RestaurantMenu).filter(models.RestaurantMenu.id.in_(menu_ids)).all() if menu_ids else []
    menu_by_id = {m.id: m for m in menus}

    modifiers = (
        db.query(models.RestaurantOrderItemModifier).filter(models.RestaurantOrderItemModifier.order_item_id.in_(order_item_ids)).all()
        if order_item_ids
        else []
    )
    modifiers_by_item = {}
    for m in modifiers:
        modifiers_by_item.setdefault(m.order_item_id, []).append(m.modifier_name)

    items = []
    for ki in kot_items:
        oi = order_items_by_id.get(ki.order_item_id)
        menu = menu_by_id.get(oi.menu_id) if oi else None
        items.append(
            {
                "kot_item_id": ki.id,
                "order_item_id": ki.order_item_id,
                "item_name": menu.item_name if menu else None,
                "quantity": oi.quantity if oi else None,
                "preparation_status": ki.preparation_status,
                "prep_start_time": ki.prep_start_time,
                "prep_end_time": ki.prep_end_time,
                "special_instructions": oi.special_instructions if oi else None,
                "variant_name": oi.variant_name if oi else None,
                "modifiers": modifiers_by_item.get(ki.order_item_id, []),
            }
        )

    order = db.query(models.RestaurantOrder).filter(models.RestaurantOrder.id == kot.order_id).first()
    return {
        **kot.__dict__,
        # The kitchen display was showing the raw restaurant_order.id in a
        # column headed "Order ID". order_number is the code printed on the
        # ticket and the one the floor calls out.
        "order_number": order.order_number if order else None,
        "table_code": order.table_code if order else None,
        "room_no": order.room_no if order else None,
        "no_of_guests": order.no_of_guests if order else None,
        "items": items,
    }


@router.get("/kot", status_code=status.HTTP_200_OK)
def list_kots(
    request: Request,
    kitchen_id: Optional[int] = Query(None),
    kot_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.KitchenOrderTicket).filter(
        models.KitchenOrderTicket.company_id == company_id, models.KitchenOrderTicket.status == STATUS
    )
    if kitchen_id is not None:
        q = q.filter(models.KitchenOrderTicket.kitchen_id == kitchen_id)
    if kot_status:
        q = q.filter(models.KitchenOrderTicket.kot_status == kot_status)
    else:
        q = q.filter(models.KitchenOrderTicket.kot_status != "Completed")
    kots = q.order_by(models.KitchenOrderTicket.id.asc()).all()
    return {"status": "success", "count": len(kots), "data": [_kot_with_items(db, k) for k in kots]}


@router.get("/kot/{kot_id}", status_code=status.HTTP_200_OK)
def get_kot(kot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    kot = (
        db.query(models.KitchenOrderTicket)
        .filter(models.KitchenOrderTicket.id == kot_id, models.KitchenOrderTicket.company_id == company_id)
        .first()
    )
    if not kot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KOT not found")
    return {"status": "success", "data": _kot_with_items(db, kot)}


# =====================================================
# KOT LIFECYCLE
# =====================================================
@router.put("/kot/{kot_id}/acknowledge", status_code=status.HTTP_200_OK)
def acknowledge_kot(kot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    kot = (
        db.query(models.KitchenOrderTicket)
        .filter(models.KitchenOrderTicket.id == kot_id, models.KitchenOrderTicket.company_id == company_id)
        .first()
    )
    if not kot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KOT not found")
    kot.kot_status = "Acknowledged"
    kot.acknowledged_by = user_id
    kot.acknowledged_at = datetime.now()
    kot.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "KOT acknowledged"}


@router.put("/kot/{kot_id}/status", status_code=status.HTTP_200_OK)
def update_kot_status(kot_id: int, payload: KotStatusIn, request: Request, db: Session = Depends(get_db)):
    """Marks the whole ticket (and every item on it) Ready/Completed/Cancelled — this is what the
    kitchen-display "Mark Ready" action calls."""
    user_id, role_id, company_id = _auth(request)
    kot = (
        db.query(models.KitchenOrderTicket)
        .filter(models.KitchenOrderTicket.id == kot_id, models.KitchenOrderTicket.company_id == company_id)
        .first()
    )
    if not kot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KOT not found")

    try:
        kot.kot_status = payload.kot_status
        kot.updated_by = user_id
        if payload.kot_status == "Completed":
            kot.completed_by = user_id
            kot.completed_at = datetime.now()

        kot_items = db.query(models.KitchenOrderItem).filter(models.KitchenOrderItem.kot_id == kot_id).all()
        low_stock_alerts = []
        for ki in kot_items:
            if payload.kot_status == "Completed":
                ki.preparation_status = "Ready"
                ki.prep_end_time = datetime.now()
                order_item = db.query(models.RestaurantOrderItem).filter(models.RestaurantOrderItem.id == ki.order_item_id).first()
                if order_item:
                    order_item.item_status = "Ready"
                    alerts = deduct_stock_for_menu_item(
                        db, company_id, order_item.menu_id, kot.kitchen_id, order_item.quantity, kot.kot_number, user_id
                    )
                    low_stock_alerts.extend(alerts)
            elif payload.kot_status == "Cancelled":
                ki.preparation_status = "Cancelled"

        db.commit()
        return {"status": "success", "message": f"KOT marked {payload.kot_status}", "low_stock_alerts": low_stock_alerts}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/kot/item/{kot_item_id}/status", status_code=status.HTTP_200_OK)
def update_kot_item_status(kot_item_id: int, payload: KotItemStatusIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    ki = db.query(models.KitchenOrderItem).filter(models.KitchenOrderItem.id == kot_item_id).first()
    if not ki:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KOT item not found")
    kot = db.query(models.KitchenOrderTicket).filter(models.KitchenOrderTicket.id == ki.kot_id, models.KitchenOrderTicket.company_id == company_id).first()
    if not kot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KOT item not found")

    low_stock_alerts = []
    ki.preparation_status = payload.preparation_status
    if payload.preparation_status == "Preparing" and not ki.prep_start_time:
        ki.prep_start_time = datetime.now()
    if payload.preparation_status == "Ready":
        ki.prep_end_time = datetime.now()
        order_item = db.query(models.RestaurantOrderItem).filter(models.RestaurantOrderItem.id == ki.order_item_id).first()
        if order_item:
            order_item.item_status = "Ready"
            low_stock_alerts = deduct_stock_for_menu_item(
                db, company_id, order_item.menu_id, kot.kitchen_id, order_item.quantity, kot.kot_number, user_id
            )

    db.commit()
    return {"status": "success", "message": "KOT item updated", "low_stock_alerts": low_stock_alerts}


@router.post("/kot/{kot_id}/print", status_code=status.HTTP_200_OK)
def print_kot(kot_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    kot = (
        db.query(models.KitchenOrderTicket)
        .filter(models.KitchenOrderTicket.id == kot_id, models.KitchenOrderTicket.company_id == company_id)
        .first()
    )
    if not kot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KOT not found")
    kot.print_count = (kot.print_count or 0) + 1
    kot.printed_by = user_id
    db.commit()
    return {"status": "success", "print_count": kot.print_count}

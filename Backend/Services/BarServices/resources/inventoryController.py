import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import func
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


def _get_or_create_stock_row(db: Session, inventory_item_id: int, station_id: Optional[int], company_id: str) -> models.BarInventoryStock:
    row = (
        db.query(models.BarInventoryStock)
        .filter(
            models.BarInventoryStock.inventory_item_id == inventory_item_id,
            models.BarInventoryStock.station_id == station_id,
            models.BarInventoryStock.company_id == company_id,
        )
        .first()
    )
    if not row:
        row = models.BarInventoryStock(
            inventory_item_id=inventory_item_id,
            station_id=station_id,
            available_quantity=0,
            last_updated_date=date.today(),
            company_id=company_id,
        )
        db.add(row)
        db.flush()
    return row


def deduct_stock_for_menu_item(db: Session, company_id: str, menu_id: int, station_id: Optional[int], quantity: int, reference_id: str, created_by: str) -> List[str]:
    """Auto-deducts recipe ingredients when a BOT item is completed. Returns a list of
    item names that dropped below their minimum stock level (for a low-stock alert)."""
    recipe_rows = db.query(models.BarRecipe).filter(models.BarRecipe.menu_id == menu_id, models.BarRecipe.status == STATUS).all()
    low_stock_alerts = []
    for r in recipe_rows:
        stock = _get_or_create_stock_row(db, r.inventory_item_id, station_id, company_id)
        needed = r.quantity_required * quantity
        stock.available_quantity = (stock.available_quantity or 0) - needed
        stock.last_updated_date = date.today()

        db.add(
            models.BarInventoryStockTransaction(
                inventory_item_id=r.inventory_item_id,
                station_id=station_id,
                transaction_type="OUT",
                quantity=needed,
                reference_type="BOT",
                reference_id=reference_id,
                created_by=created_by,
                company_id=company_id,
            )
        )

        item = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id == r.inventory_item_id).first()
        if item and stock.available_quantity < (item.min_stock_level or 0):
            low_stock_alerts.append(item.item_name)
    return low_stock_alerts


# =====================================================
# SCHEMAS
# =====================================================
class InventoryItemIn(BaseModel):
    item_name: str
    category: Optional[str] = None
    unit: str
    min_stock_level: float = 0
    is_perishable: bool = False


class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    min_stock_level: Optional[float] = None
    is_perishable: Optional[bool] = None


class StockAdjustIn(BaseModel):
    inventory_item_id: int
    station_id: Optional[int] = None
    quantity: float
    transaction_type: str = "ADJUSTMENT"
    remarks: Optional[str] = None


class PurchaseIn(BaseModel):
    inventory_item_id: int
    quantity: float
    unit_price: float
    supplier_name: Optional[str] = None
    station_id: Optional[int] = None


class RecipeIngredientIn(BaseModel):
    inventory_item_id: int
    quantity_required: float
    unit: str


class RecipeIn(BaseModel):
    ingredients: List[RecipeIngredientIn]


# =====================================================
# INVENTORY ITEMS
# =====================================================
@router.post("/inventory_item", status_code=status.HTTP_201_CREATED)
def create_inventory_item(payload: InventoryItemIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = models.BarInventoryItem(item_code=gen_code("BINV"), created_by=user_id, company_id=company_id, **payload.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"status": "success", "data": {"id": item.id, "item_code": item.item_code}}


@router.get("/inventory_item", status_code=status.HTTP_200_OK)
def list_inventory_items(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.BarInventoryItem)
        .filter(models.BarInventoryItem.company_id == company_id, models.BarInventoryItem.status == STATUS)
        .order_by(models.BarInventoryItem.item_name.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/inventory_item/{item_id}", status_code=status.HTTP_200_OK)
def update_inventory_item(item_id: int, payload: InventoryItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id == item_id, models.BarInventoryItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Inventory item updated"}


# =====================================================
# STOCK
# =====================================================
@router.get("/inventory_stock", status_code=status.HTTP_200_OK)
def list_stock(request: Request, station_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarInventoryStock).filter(models.BarInventoryStock.company_id == company_id, models.BarInventoryStock.status == STATUS)
    if station_id is not None:
        q = q.filter(models.BarInventoryStock.station_id == station_id)
    stock_rows = q.all()

    item_ids = [s.inventory_item_id for s in stock_rows]
    items = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id.in_(item_ids)).all() if item_ids else []
    item_by_id = {i.id: i for i in items}

    data = []
    for s in stock_rows:
        item = item_by_id.get(s.inventory_item_id)
        data.append(
            {
                **s.__dict__,
                "item_name": item.item_name if item else None,
                "unit": item.unit if item else None,
                "min_stock_level": item.min_stock_level if item else None,
                "below_minimum": bool(item and s.available_quantity < (item.min_stock_level or 0)),
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/inventory_item/{item_id}/transactions", status_code=status.HTTP_200_OK)
def list_item_transactions(item_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.BarInventoryStockTransaction)
        .filter(models.BarInventoryStockTransaction.inventory_item_id == item_id, models.BarInventoryStockTransaction.company_id == company_id)
        .order_by(models.BarInventoryStockTransaction.created_at.desc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.get("/inventory_stock/low_stock", status_code=status.HTTP_200_OK)
def low_stock(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    stock_rows = db.query(models.BarInventoryStock).filter(models.BarInventoryStock.company_id == company_id, models.BarInventoryStock.status == STATUS).all()
    item_ids = [s.inventory_item_id for s in stock_rows]
    items = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id.in_(item_ids)).all() if item_ids else []
    item_by_id = {i.id: i for i in items}

    alerts = []
    for s in stock_rows:
        item = item_by_id.get(s.inventory_item_id)
        if item and s.available_quantity < (item.min_stock_level or 0):
            alerts.append({"inventory_item_id": item.id, "item_name": item.item_name, "available_quantity": s.available_quantity, "min_stock_level": item.min_stock_level, "station_id": s.station_id})
    return {"status": "success", "count": len(alerts), "data": alerts}


@router.post("/inventory_stock/adjust", status_code=status.HTTP_200_OK)
def adjust_stock(payload: StockAdjustIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id == payload.inventory_item_id, models.BarInventoryItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inventory_item_id does not exist")

    try:
        stock = _get_or_create_stock_row(db, payload.inventory_item_id, payload.station_id, company_id)
        stock.available_quantity = (stock.available_quantity or 0) + payload.quantity
        stock.last_updated_date = date.today()

        db.add(
            models.BarInventoryStockTransaction(
                inventory_item_id=payload.inventory_item_id,
                station_id=payload.station_id,
                transaction_type=payload.transaction_type,
                quantity=payload.quantity,
                reference_type="Manual",
                remarks=payload.remarks,
                created_by=user_id,
                company_id=company_id,
            )
        )
        db.commit()
        return {"status": "success", "data": {"available_quantity": stock.available_quantity}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/inventory_purchase", status_code=status.HTTP_201_CREATED)
def record_purchase(payload: PurchaseIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id == payload.inventory_item_id, models.BarInventoryItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inventory_item_id does not exist")

    try:
        purchase = models.BarInventoryPurchase(
            inventory_item_id=payload.inventory_item_id,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            total_amount=round(payload.quantity * payload.unit_price, 2),
            purchase_date=date.today(),
            supplier_name=payload.supplier_name,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(purchase)

        stock = _get_or_create_stock_row(db, payload.inventory_item_id, payload.station_id, company_id)
        stock.available_quantity = (stock.available_quantity or 0) + payload.quantity
        stock.last_updated_date = date.today()

        db.add(
            models.BarInventoryStockTransaction(
                inventory_item_id=payload.inventory_item_id,
                station_id=payload.station_id,
                transaction_type="IN",
                quantity=payload.quantity,
                reference_type="Purchase",
                created_by=user_id,
                company_id=company_id,
            )
        )
        db.commit()
        db.refresh(purchase)
        return {"status": "success", "data": {"id": purchase.id, "total_amount": purchase.total_amount}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =====================================================
# RECIPES (per menu item)
# =====================================================
@router.post("/menu/{menu_id}/recipe", status_code=status.HTTP_201_CREATED)
def set_recipe(menu_id: int, payload: RecipeIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    menu = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id).first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    try:
        db.query(models.BarRecipe).filter(models.BarRecipe.menu_id == menu_id).update({"status": UNSTATUS})
        for ing in payload.ingredients:
            db.add(models.BarRecipe(menu_id=menu_id, created_by=user_id, company_id=company_id, **ing.dict()))
        db.commit()
        return {"status": "success", "message": "Recipe saved"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/menu/{menu_id}/recipe", status_code=status.HTTP_200_OK)
def get_recipe(menu_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = db.query(models.BarRecipe).filter(models.BarRecipe.menu_id == menu_id, models.BarRecipe.status == STATUS).all()
    item_ids = [r.inventory_item_id for r in rows]
    items = db.query(models.BarInventoryItem).filter(models.BarInventoryItem.id.in_(item_ids)).all() if item_ids else []
    item_by_id = {i.id: i for i in items}
    data = [{**r.__dict__, "item_name": item_by_id.get(r.inventory_item_id).item_name if item_by_id.get(r.inventory_item_id) else None} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/menu_recipe_counts", status_code=status.HTTP_200_OK)
def get_menu_recipe_counts(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.BarRecipe.menu_id, func.count(models.BarRecipe.id))
        .filter(models.BarRecipe.company_id == company_id, models.BarRecipe.status == STATUS)
        .group_by(models.BarRecipe.menu_id)
        .all()
    )
    return {"status": "success", "data": {str(menu_id): count for menu_id, count in rows}}

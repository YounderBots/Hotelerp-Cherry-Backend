import logging
import math
import uuid
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import set_committed_value

from models import get_db, models
from resources.utils import verify_authentication
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


def _get_or_create_stock_row(db: Session, inventory_item_id: int, kitchen_id: Optional[int], company_id: str) -> models.InventoryStock:
    row = (
        db.query(models.InventoryStock)
        .filter(
            models.InventoryStock.inventory_item_id == inventory_item_id,
            models.InventoryStock.kitchen_id == kitchen_id,
            models.InventoryStock.company_id == company_id,
        )
        .with_for_update()
        .first()
    )
    if not row:
        row = models.InventoryStock(
            inventory_item_id=inventory_item_id,
            kitchen_id=kitchen_id,
            available_quantity=0,
            last_updated_date=date.today(),
            company_id=company_id,
        )
        db.add(row)
        db.flush()
    return row


class InventoryDeductionError(ValueError):
    """A recipe deduction request cannot be applied safely."""


class InsufficientStockError(InventoryDeductionError):
    """Applying a deduction would make an ingredient unavailable or negative."""


def _positive_quantity(value, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InventoryDeductionError(f"{field} must be a positive number") from exc
    if not math.isfinite(number) or number <= 0:
        raise InventoryDeductionError(f"{field} must be greater than zero")
    return number


def _nonnegative_quantity(value, field: str) -> float:
    try:
        number = float(value or 0)
    except (TypeError, ValueError) as exc:
        raise InventoryDeductionError(f"{field} must be a non-negative number") from exc
    if not math.isfinite(number) or number < 0:
        raise InventoryDeductionError(f"{field} must be zero or greater")
    return number


def _deduction_marker(_reference_id: str, source_order_item_id: Optional[int]) -> Optional[str]:
    if source_order_item_id is None:
        return None
    # The order line, rather than the ticket number, is the durable source
    # identity.  A retry may arrive through a supplementary ticket.  The
    # existing transaction schema has remarks but no separate idempotency key,
    # so the stable marker lives there while reference_id remains the audit
    # pointer to the KOT.
    return f"Recipe deduction for order item {source_order_item_id}"


def _has_existing_deduction(
    db: Session,
    company_id: str,
    kitchen_id: Optional[int],
    inventory_item_id: int,
    reference_id: str,
    source_order_item_id: Optional[int],
) -> bool:
    """Check the transaction ledger while its stock rows are locked.

    The marker includes the order line as well as the ticket.  A ticket number
    alone is not an idempotency key: one ticket may contain two separate lines
    for the same menu, and each line needs its own recipe deduction.
    """
    query = db.query(models.InventoryStockTransaction).filter(
        models.InventoryStockTransaction.company_id == company_id,
        models.InventoryStockTransaction.inventory_item_id == inventory_item_id,
        models.InventoryStockTransaction.kitchen_id == kitchen_id,
        models.InventoryStockTransaction.transaction_type == "OUT",
        models.InventoryStockTransaction.reference_type == "KOT",
    )
    if source_order_item_id is None:
        query = query.filter(models.InventoryStockTransaction.reference_id == reference_id)
    else:
        query = query.filter(
            models.InventoryStockTransaction.remarks == _deduction_marker(reference_id, source_order_item_id)
        )
    return query.with_for_update().first() is not None


def deduct_stock_for_menu_item(
    db: Session,
    company_id: str,
    menu_id: int,
    kitchen_id: Optional[int],
    quantity: int,
    reference_id: str,
    created_by: str,
    source_order_item_id: Optional[int] = None,
) -> List[str]:
    """Deduct a recipe exactly once, atomically, and never below zero.

    All stock rows are locked and checked before any row is changed.  The
    conditional UPDATE is retained as a second line of defence for databases
    or sessions where the ORM lock is not sufficient.  A missing stock row is
    treated as unavailable rather than silently creating a zero row.
    """
    quantity = _positive_quantity(quantity, "quantity")
    recipe_rows = (
        db.query(models.MenuRecipe)
        .filter(
            models.MenuRecipe.company_id == company_id,
            models.MenuRecipe.menu_id == menu_id,
            models.MenuRecipe.status == STATUS,
        )
        .order_by(models.MenuRecipe.inventory_item_id.asc())
        .all()
    )

    requirements = []
    for recipe in recipe_rows:
        recipe_quantity = _positive_quantity(recipe.quantity_required, "recipe quantity_required")
        needed = round(recipe_quantity * quantity, 3)
        if needed <= 0:
            raise InventoryDeductionError("recipe quantity_required must be greater than zero")

        stock = (
            db.query(models.InventoryStock)
            .filter(
                models.InventoryStock.company_id == company_id,
                models.InventoryStock.inventory_item_id == recipe.inventory_item_id,
                models.InventoryStock.kitchen_id == kitchen_id,
            )
            .populate_existing()
            .with_for_update()
            .first()
        )
        if stock is None:
            raise InsufficientStockError(
                f"Insufficient stock: no stock record exists for inventory item {recipe.inventory_item_id}"
            )

        if _has_existing_deduction(
            db,
            company_id,
            kitchen_id,
            recipe.inventory_item_id,
            reference_id,
            source_order_item_id,
        ):
            continue

        available = _nonnegative_quantity(stock.available_quantity, "available_quantity")
        if available < needed:
            raise InsufficientStockError(
                f"Insufficient stock for inventory item {recipe.inventory_item_id}: "
                f"needed {needed:g}, available {available:g}"
            )
        requirements.append((recipe, stock, needed, available))

    low_stock_alerts = []
    for recipe, stock, needed, available in requirements:
        updated = (
            db.query(models.InventoryStock)
            .filter(
                models.InventoryStock.id == stock.id,
                models.InventoryStock.available_quantity >= needed,
            )
            .update(
                {
                    models.InventoryStock.available_quantity: models.InventoryStock.available_quantity - needed,
                    models.InventoryStock.last_updated_date: date.today(),
                },
                synchronize_session=False,
            )
        )
        if updated != 1:
            raise InsufficientStockError(
                f"Insufficient stock for inventory item {recipe.inventory_item_id}"
            )
        set_committed_value(stock, "available_quantity", available - needed)

        db.add(
            models.InventoryStockTransaction(
                inventory_item_id=recipe.inventory_item_id,
                kitchen_id=kitchen_id,
                transaction_type="OUT",
                quantity=needed,
                reference_type="KOT",
                reference_id=reference_id,
                remarks=_deduction_marker(reference_id, source_order_item_id),
                created_by=created_by,
                company_id=company_id,
            )
        )

        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == recipe.inventory_item_id).first()
        if item and stock.available_quantity < _nonnegative_quantity(item.min_stock_level, "min_stock_level"):
            if item.item_name not in low_stock_alerts:
                low_stock_alerts.append(item.item_name)
    db.flush()
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
    kitchen_id: Optional[int] = None
    quantity: float  # positive = add, negative = remove
    transaction_type: str = "ADJUSTMENT"  # ADJUSTMENT | WASTE
    remarks: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def adjustment_quantity_must_be_nonzero(cls, value: float) -> float:
        if not math.isfinite(value) or value == 0:
            raise ValueError("quantity must be greater than zero or less than zero")
        return value


class PurchaseIn(BaseModel):
    inventory_item_id: int
    quantity: float
    unit_price: float
    supplier_name: Optional[str] = None
    kitchen_id: Optional[int] = None

    @field_validator("quantity")
    @classmethod
    def purchase_quantity_must_be_positive(cls, value: float) -> float:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("quantity must be greater than zero")
        return value


class RecipeIngredientIn(BaseModel):
    inventory_item_id: int
    quantity_required: float
    unit: str

    @field_validator("quantity_required")
    @classmethod
    def quantity_required_must_be_positive(cls, value: float) -> float:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("quantity_required must be greater than zero")
        return value

    @field_validator("unit")
    @classmethod
    def recipe_unit_must_be_supported(cls, value: str) -> str:
        if value not in {"Kg", "Gram", "Litre", "ml", "Nos"}:
            raise ValueError("recipe unit is invalid")
        return value


class RecipeIn(BaseModel):
    ingredients: List[RecipeIngredientIn]


INVENTORY_UNITS = ("Kg", "Gram", "Litre", "ml", "Nos")
STOCK_TRANSACTION_TYPES = ("ADJUSTMENT", "WASTE")


def _validate_inventory_item(*, item_name, unit, min_stock_level):
    if item_name is not None:
        item_name = str(item_name).strip()
        if not item_name:
            raise HTTPException(status_code=400, detail="item_name is required")
        if len(item_name) > 150:
            raise HTTPException(status_code=400, detail="item_name must not exceed 150 characters")
    if unit is not None and unit not in INVENTORY_UNITS:
        raise HTTPException(status_code=400, detail="unit is invalid")
    if min_stock_level is not None and float(min_stock_level) < 0:
        raise HTTPException(status_code=400, detail="min_stock_level must be zero or greater")
    return item_name


# =====================================================
# INVENTORY ITEMS
# =====================================================
@router.post("/inventory_item", status_code=status.HTTP_201_CREATED)
def create_inventory_item(payload: InventoryItemIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item_name = _validate_inventory_item(
        item_name=payload.item_name,
        unit=payload.unit,
        min_stock_level=payload.min_stock_level,
    )
    duplicate = db.query(models.InventoryItem).filter(
        models.InventoryItem.company_id == company_id,
        models.InventoryItem.status == STATUS,
        func.lower(models.InventoryItem.item_name) == item_name.lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active inventory item with this name already exists")
    values = payload.dict()
    values["item_name"] = item_name
    item = models.InventoryItem(item_code=gen_code("INV"), created_by=user_id, company_id=company_id, **values)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active inventory item with this name already exists")
    db.refresh(item)
    return {"status": "success", "data": {"id": item.id, "item_code": item.item_code}}


@router.get("/inventory_item", status_code=status.HTTP_200_OK)
def list_inventory_items(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.company_id == company_id, models.InventoryItem.status == STATUS)
        .order_by(models.InventoryItem.item_name.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/inventory_item/{item_id}", status_code=status.HTTP_200_OK)
def update_inventory_item(item_id: int, payload: InventoryItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.id == item_id, models.InventoryItem.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = _validate_inventory_item(
        item_name=updates.get("item_name", item.item_name),
        unit=updates.get("unit", item.unit),
        min_stock_level=updates.get("min_stock_level", item.min_stock_level),
    )
    duplicate = db.query(models.InventoryItem).filter(
        models.InventoryItem.company_id == company_id,
        models.InventoryItem.status == STATUS,
        models.InventoryItem.id != item.id,
        func.lower(models.InventoryItem.item_name) == candidate_name.lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active inventory item with this name already exists")
    for field, value in updates.items():
        setattr(item, field, value)
    if "item_name" in updates:
        item.item_name = candidate_name
    item.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active inventory item with this name already exists")
    return {"status": "success", "message": "Inventory item updated"}


# =====================================================
# STOCK
# =====================================================
@router.get("/inventory_stock", status_code=status.HTTP_200_OK)
def list_stock(request: Request, kitchen_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.InventoryStock).filter(models.InventoryStock.company_id == company_id, models.InventoryStock.status == STATUS)
    if kitchen_id is not None:
        q = q.filter(models.InventoryStock.kitchen_id == kitchen_id)
    stock_rows = q.all()

    item_ids = [s.inventory_item_id for s in stock_rows]
    items = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id.in_(item_ids),
            models.InventoryItem.company_id == company_id,
            models.InventoryItem.status == STATUS,
        )
        .all()
        if item_ids
        else []
    )
    item_by_id = {i.id: i for i in items}

    # Resolve the storage location's NAME alongside its id. kitchen_id is a raw
    # foreign key, and the stock screen was rendering it as "Kitchen #3" -- a
    # database row number shown to a storekeeper, who knows the place by its
    # name. The item join above already sets the precedent.
    kitchen_ids = {s.kitchen_id for s in stock_rows if s.kitchen_id}
    kitchens = (
        db.query(models.Kitchen)
        .filter(
            models.Kitchen.id.in_(kitchen_ids),
            models.Kitchen.company_id == company_id,
            models.Kitchen.status == STATUS,
        )
        .all()
        if kitchen_ids
        else []
    )
    kitchen_name_by_id = {k.id: k.kitchen_name for k in kitchens}

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
                # "Main Store" is what a null kitchen_id means: stock held
                # centrally rather than at a station.
                "kitchen_name": kitchen_name_by_id.get(s.kitchen_id) or "Main Store",
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/inventory_item/{item_id}/transactions", status_code=status.HTTP_200_OK)
def list_item_transactions(item_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.InventoryStockTransaction)
        .filter(models.InventoryStockTransaction.inventory_item_id == item_id, models.InventoryStockTransaction.company_id == company_id)
        .order_by(models.InventoryStockTransaction.created_at.desc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.get("/inventory_stock/low_stock", status_code=status.HTTP_200_OK)
def low_stock(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    stock_rows = db.query(models.InventoryStock).filter(models.InventoryStock.company_id == company_id, models.InventoryStock.status == STATUS).all()
    item_ids = [s.inventory_item_id for s in stock_rows]
    items = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id.in_(item_ids),
            models.InventoryItem.company_id == company_id,
            models.InventoryItem.status == STATUS,
        )
        .all()
        if item_ids
        else []
    )
    item_by_id = {i.id: i for i in items}

    alerts = []
    for s in stock_rows:
        item = item_by_id.get(s.inventory_item_id)
        if item and s.available_quantity < (item.min_stock_level or 0):
            alerts.append({"inventory_item_id": item.id, "item_name": item.item_name, "available_quantity": s.available_quantity, "min_stock_level": item.min_stock_level, "kitchen_id": s.kitchen_id})
    return {"status": "success", "count": len(alerts), "data": alerts}


@router.post("/inventory_stock/adjust", status_code=status.HTTP_200_OK)
def adjust_stock(payload: StockAdjustIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.id == payload.inventory_item_id, models.InventoryItem.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inventory_item_id does not exist")
    if payload.transaction_type not in STOCK_TRANSACTION_TYPES:
        raise HTTPException(status_code=400, detail="transaction_type is invalid")

    try:
        stock = _get_or_create_stock_row(db, payload.inventory_item_id, payload.kitchen_id, company_id)
        new_quantity = (stock.available_quantity or 0) + payload.quantity
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Stock cannot be reduced below zero")
        stock.available_quantity = new_quantity
        stock.last_updated_date = date.today()

        db.add(
            models.InventoryStockTransaction(
                inventory_item_id=payload.inventory_item_id,
                kitchen_id=payload.kitchen_id,
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
        raise _server_error(e)


@router.post("/inventory_purchase", status_code=status.HTTP_201_CREATED)
def record_purchase(payload: PurchaseIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.id == payload.inventory_item_id, models.InventoryItem.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inventory_item_id does not exist")

    try:
        purchase = models.InventoryPurchase(
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

        stock = _get_or_create_stock_row(db, payload.inventory_item_id, payload.kitchen_id, company_id)
        stock.available_quantity = (stock.available_quantity or 0) + payload.quantity
        stock.last_updated_date = date.today()

        db.add(
            models.InventoryStockTransaction(
                inventory_item_id=payload.inventory_item_id,
                kitchen_id=payload.kitchen_id,
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
        raise _server_error(e)


# =====================================================
# RECIPES (per menu item)
# =====================================================
@router.post("/menu/{menu_id}/recipe", status_code=status.HTTP_201_CREATED)
def set_recipe(menu_id: int, payload: RecipeIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    menu = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == menu_id, models.RestaurantMenu.company_id == company_id)
        .with_for_update()
        .first()
    )
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    if not payload.ingredients:
        raise HTTPException(status_code=400, detail="At least one recipe ingredient is required")

    ingredient_ids = [ing.inventory_item_id for ing in payload.ingredients]
    if len(set(ingredient_ids)) != len(ingredient_ids):
        raise HTTPException(status_code=400, detail="Each ingredient can only appear once in a recipe")
    items = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id.in_(ingredient_ids),
            models.InventoryItem.company_id == company_id,
            models.InventoryItem.status == STATUS,
        )
        .all()
    )
    item_by_id = {item.id: item for item in items}
    if len(item_by_id) != len(ingredient_ids):
        raise HTTPException(status_code=400, detail="One or more recipe ingredients are unavailable")
    for ing in payload.ingredients:
        item = item_by_id[ing.inventory_item_id]
        if ing.unit != item.unit:
            raise HTTPException(status_code=400, detail=f"unit for ingredient {item.item_name} must be {item.unit}")

    try:
        db.query(models.MenuRecipe).filter(
            models.MenuRecipe.menu_id == menu_id,
            models.MenuRecipe.company_id == company_id,
        ).update({"status": UNSTATUS})
        for ing in payload.ingredients:
            db.add(models.MenuRecipe(menu_id=menu_id, created_by=user_id, company_id=company_id, **ing.dict()))
        db.commit()
        return {"status": "success", "message": "Recipe saved"}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Recipe could not be saved because it conflicts with an active recipe")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/menu/{menu_id}/recipe", status_code=status.HTTP_200_OK)
def get_recipe(menu_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = db.query(models.MenuRecipe).filter(
        models.MenuRecipe.menu_id == menu_id,
        models.MenuRecipe.company_id == company_id,
        models.MenuRecipe.status == STATUS,
    ).all()
    item_ids = [r.inventory_item_id for r in rows]
    items = (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.id.in_(item_ids),
            models.InventoryItem.company_id == company_id,
            models.InventoryItem.status == STATUS,
        )
        .all()
        if item_ids
        else []
    )
    item_by_id = {i.id: i for i in items}
    data = [{**r.__dict__, "item_name": item_by_id.get(r.inventory_item_id).item_name if item_by_id.get(r.inventory_item_id) else None} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/menu_recipe_counts", status_code=status.HTTP_200_OK)
def get_menu_recipe_counts(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.MenuRecipe.menu_id, func.count(models.MenuRecipe.id))
        .filter(models.MenuRecipe.company_id == company_id, models.MenuRecipe.status == STATUS)
        .group_by(models.MenuRecipe.menu_id)
        .all()
    )
    return {"status": "success", "data": {str(menu_id): count for menu_id, count in rows}}

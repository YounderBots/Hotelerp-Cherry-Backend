import uuid
from datetime import datetime
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
class CategoryIn(BaseModel):
    category_name: str
    description: Optional[str] = None
    kitchen_section: str
    display_order: Optional[int] = None


class SubCategoryIn(BaseModel):
    category_id: int
    sub_category_name: str
    description: Optional[str] = None
    display_order: Optional[int] = None


class VariantIn(BaseModel):
    variant_name: str
    price: float


class ModifierIn(BaseModel):
    modifier_name: str
    price: Optional[float] = None
    modifier_type: Optional[str] = None


class MenuItemIn(BaseModel):
    item_name: str
    description: Optional[str] = None
    category_id: int
    sub_category_id: Optional[int] = None
    price: float
    cost_price: Optional[float] = None
    tax_percentage: Optional[float] = None
    service_charge_applicable: str = "No"
    preparation_time: Optional[int] = None
    kitchen_section: str
    availability_status: str = "Available"
    is_veg: str = "Yes"
    dietary_tags: Optional[List[str]] = None
    item_image: Optional[str] = None
    happy_hour_eligible: str = "No"
    variants: Optional[List[VariantIn]] = None
    modifiers: Optional[List[ModifierIn]] = None


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    tax_percentage: Optional[float] = None
    service_charge_applicable: Optional[str] = None
    preparation_time: Optional[int] = None
    kitchen_section: Optional[str] = None
    availability_status: Optional[str] = None
    is_veg: Optional[str] = None
    dietary_tags: Optional[List[str]] = None
    item_image: Optional[str] = None
    happy_hour_eligible: Optional[str] = None


class ComboItemIn(BaseModel):
    menu_id: int
    quantity: int = 1


class ComboIn(BaseModel):
    combo_name: str
    description: Optional[str] = None
    combo_price: float
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    items: List[ComboItemIn]


# =====================================================
# CATEGORIES
# =====================================================
@router.post("/menu_category", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    category = models.MenuCategory(
        category_code=gen_code("CAT"), created_by=user_id, company_id=company_id, **payload.dict()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"status": "success", "data": {"id": category.id, "category_code": category.category_code}}


@router.get("/menu_category", status_code=status.HTTP_200_OK)
def list_categories(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.MenuCategory)
        .filter(models.MenuCategory.company_id == company_id, models.MenuCategory.status == STATUS)
        .order_by(models.MenuCategory.display_order.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.post("/menu_sub_category", status_code=status.HTTP_201_CREATED)
def create_sub_category(payload: SubCategoryIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    category = (
        db.query(models.MenuCategory)
        .filter(models.MenuCategory.id == payload.category_id, models.MenuCategory.company_id == company_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id does not exist")
    sub = models.MenuSubCategory(
        sub_category_code=gen_code("SUBCAT"),
        category_code=category.category_code,
        created_by=user_id,
        company_id=company_id,
        **payload.dict(),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"status": "success", "data": {"id": sub.id, "sub_category_code": sub.sub_category_code}}


@router.get("/menu_sub_category", status_code=status.HTTP_200_OK)
def list_sub_categories(request: Request, category_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.MenuSubCategory).filter(
        models.MenuSubCategory.company_id == company_id, models.MenuSubCategory.status == STATUS
    )
    if category_id is not None:
        q = q.filter(models.MenuSubCategory.category_id == category_id)
    rows = q.order_by(models.MenuSubCategory.display_order.asc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


# =====================================================
# MENU ITEMS
# =====================================================
@router.post("/menu", status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        data = payload.dict(exclude={"variants", "modifiers"})
        item = models.RestaurantMenu(
            item_code=gen_code("ITM"),
            has_variants="Yes" if payload.variants else "No",
            created_by=user_id,
            company_id=company_id,
            **data,
        )
        db.add(item)
        db.flush()

        for v in (payload.variants or []):
            db.add(models.MenuVariant(menu_id=item.id, created_by=user_id, company_id=company_id, **v.dict()))
        for m in (payload.modifiers or []):
            db.add(models.MenuModifier(menu_id=item.id, created_by=user_id, company_id=company_id, **m.dict()))

        db.commit()
        db.refresh(item)
        return {"status": "success", "data": {"id": item.id, "item_code": item.item_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/menu", status_code=status.HTTP_200_OK)
def list_menu_items(
    request: Request,
    category_id: Optional[int] = Query(None),
    kitchen_section: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.RestaurantMenu).filter(
        models.RestaurantMenu.company_id == company_id, models.RestaurantMenu.status == STATUS
    )
    if category_id is not None:
        q = q.filter(models.RestaurantMenu.category_id == category_id)
    if kitchen_section:
        q = q.filter(models.RestaurantMenu.kitchen_section == kitchen_section)
    items = q.order_by(models.RestaurantMenu.item_name.asc()).all()

    item_ids = [i.id for i in items]
    variants = (
        db.query(models.MenuVariant).filter(models.MenuVariant.menu_id.in_(item_ids), models.MenuVariant.status == STATUS).all()
        if item_ids
        else []
    )
    variants_by_item = {}
    for v in variants:
        variants_by_item.setdefault(v.menu_id, []).append(v)

    data = []
    for i in items:
        data.append({**i.__dict__, "variants": variants_by_item.get(i.id, [])})
    return {"status": "success", "count": len(data), "data": data}


@router.get("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def get_menu_item(menu_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == menu_id, models.RestaurantMenu.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    variants = db.query(models.MenuVariant).filter(models.MenuVariant.menu_id == menu_id, models.MenuVariant.status == STATUS).all()
    modifiers = db.query(models.MenuModifier).filter(models.MenuModifier.menu_id == menu_id, models.MenuModifier.status == STATUS).all()
    recipe = db.query(models.MenuRecipe).filter(models.MenuRecipe.menu_id == menu_id, models.MenuRecipe.status == STATUS).all()
    return {"status": "success", "data": {**item.__dict__, "variants": variants, "modifiers": modifiers, "recipe": recipe}}


@router.put("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def update_menu_item(menu_id: int, payload: MenuItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == menu_id, models.RestaurantMenu.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Menu item updated"}


@router.delete("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def deactivate_menu_item(menu_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == menu_id, models.RestaurantMenu.company_id == company_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    item.status = UNSTATUS
    item.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Menu item deactivated"}


# =====================================================
# COMBO / PACKAGE DEALS
# =====================================================
@router.post("/combo", status_code=status.HTTP_201_CREATED)
def create_combo(payload: ComboIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        combo = models.ComboDeal(
            combo_code=gen_code("CMB"),
            combo_name=payload.combo_name,
            description=payload.description,
            combo_price=payload.combo_price,
            valid_from=payload.valid_from,
            valid_to=payload.valid_to,
            is_active="Yes",
            created_by=user_id,
            company_id=company_id,
        )
        db.add(combo)
        db.flush()
        for it in payload.items:
            db.add(models.ComboItem(combo_id=combo.id, menu_id=it.menu_id, quantity=it.quantity))
        db.commit()
        db.refresh(combo)
        return {"status": "success", "data": {"id": combo.id, "combo_code": combo.combo_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/combo", status_code=status.HTTP_200_OK)
def list_combos(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    combos = (
        db.query(models.ComboDeal)
        .filter(models.ComboDeal.company_id == company_id, models.ComboDeal.status == STATUS, models.ComboDeal.is_active == "Yes")
        .all()
    )
    combo_ids = [c.id for c in combos]
    items = db.query(models.ComboItem).filter(models.ComboItem.combo_id.in_(combo_ids)).all() if combo_ids else []
    items_by_combo = {}
    for it in items:
        items_by_combo.setdefault(it.combo_id, []).append(it)
    data = [{**c.__dict__, "items": items_by_combo.get(c.id, [])} for c in combos]
    return {"status": "success", "count": len(data), "data": data}

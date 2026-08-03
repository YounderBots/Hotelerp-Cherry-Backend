import uuid
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
    station_id: int
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


class VariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    price: Optional[float] = None


class ModifierUpdate(BaseModel):
    modifier_name: Optional[str] = None
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
    service_charge_applicable: bool = False
    preparation_time: Optional[int] = None
    station_id: int
    availability_status: str = "Available"
    dietary_tags: Optional[List[str]] = None
    item_image: Optional[str] = None
    happy_hour_eligible: bool = False
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
    service_charge_applicable: Optional[bool] = None
    preparation_time: Optional[int] = None
    station_id: Optional[int] = None
    availability_status: Optional[str] = None
    dietary_tags: Optional[List[str]] = None
    item_image: Optional[str] = None
    happy_hour_eligible: Optional[bool] = None


# =====================================================
# CATEGORIES
# =====================================================
@router.post("/menu_category", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    category = models.BarMenuCategory(category_code=gen_code("BCAT"), created_by=user_id, company_id=company_id, **payload.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"status": "success", "data": {"id": category.id, "category_code": category.category_code}}


@router.get("/menu_category", status_code=status.HTTP_200_OK)
def list_categories(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.BarMenuCategory)
        .filter(models.BarMenuCategory.company_id == company_id, models.BarMenuCategory.status == STATUS)
        .order_by(models.BarMenuCategory.display_order.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.post("/menu_sub_category", status_code=status.HTTP_201_CREATED)
def create_sub_category(payload: SubCategoryIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    category = (
        db.query(models.BarMenuCategory)
        .filter(models.BarMenuCategory.id == payload.category_id, models.BarMenuCategory.company_id == company_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id does not exist")
    sub = models.BarMenuSubCategory(
        sub_category_code=gen_code("BSUBCAT"),
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
    q = db.query(models.BarMenuSubCategory).filter(
        models.BarMenuSubCategory.company_id == company_id, models.BarMenuSubCategory.status == STATUS
    )
    if category_id is not None:
        q = q.filter(models.BarMenuSubCategory.category_id == category_id)
    rows = q.order_by(models.BarMenuSubCategory.display_order.asc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


# =====================================================
# MENU ITEMS
# =====================================================
@router.post("/menu", status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        data = payload.dict(exclude={"variants", "modifiers"})
        item = models.BarMenuItem(
            item_code=gen_code("BITM"),
            has_variants=bool(payload.variants),
            created_by=user_id,
            company_id=company_id,
            **data,
        )
        db.add(item)
        db.flush()

        for v in (payload.variants or []):
            db.add(models.BarMenuVariant(menu_id=item.id, created_by=user_id, company_id=company_id, **v.dict()))
        for m in (payload.modifiers or []):
            db.add(models.BarMenuModifier(menu_id=item.id, created_by=user_id, company_id=company_id, **m.dict()))

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
    station_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarMenuItem).filter(models.BarMenuItem.company_id == company_id, models.BarMenuItem.status == STATUS)
    if category_id is not None:
        q = q.filter(models.BarMenuItem.category_id == category_id)
    if station_id is not None:
        q = q.filter(models.BarMenuItem.station_id == station_id)
    items = q.order_by(models.BarMenuItem.item_name.asc()).all()

    item_ids = [i.id for i in items]
    variants = (
        db.query(models.BarMenuVariant).filter(models.BarMenuVariant.menu_id.in_(item_ids), models.BarMenuVariant.status == STATUS).all()
        if item_ids
        else []
    )
    variants_by_item = {}
    for v in variants:
        variants_by_item.setdefault(v.menu_id, []).append(v)

    data = [{**i.__dict__, "variants": variants_by_item.get(i.id, [])} for i in items]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def get_menu_item(menu_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    variants = db.query(models.BarMenuVariant).filter(models.BarMenuVariant.menu_id == menu_id, models.BarMenuVariant.status == STATUS).all()
    modifiers = db.query(models.BarMenuModifier).filter(models.BarMenuModifier.menu_id == menu_id, models.BarMenuModifier.status == STATUS).all()
    recipe = db.query(models.BarRecipe).filter(models.BarRecipe.menu_id == menu_id, models.BarRecipe.status == STATUS).all()
    return {"status": "success", "data": {**item.__dict__, "variants": variants, "modifiers": modifiers, "recipe": recipe}}


@router.put("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def update_menu_item(menu_id: int, payload: MenuItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id).first()
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
    item = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    item.status = UNSTATUS
    item.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Menu item deactivated"}


# =====================================================
# VARIANTS
# =====================================================
@router.post("/menu/{menu_id}/variant", status_code=status.HTTP_201_CREATED)
def create_menu_variant(menu_id: int, payload: VariantIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    menu = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id).first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    variant = models.BarMenuVariant(menu_id=menu_id, created_by=user_id, company_id=company_id, **payload.dict())
    db.add(variant)
    menu.has_variants = True
    db.commit()
    db.refresh(variant)
    return {"status": "success", "data": {"id": variant.id}}


@router.put("/variant/{variant_id}", status_code=status.HTTP_200_OK)
def update_menu_variant(variant_id: int, payload: VariantUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    variant = db.query(models.BarMenuVariant).filter(models.BarMenuVariant.id == variant_id, models.BarMenuVariant.company_id == company_id).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(variant, field, value)
    variant.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Variant updated"}


@router.delete("/variant/{variant_id}", status_code=status.HTTP_200_OK)
def deactivate_menu_variant(variant_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    variant = db.query(models.BarMenuVariant).filter(models.BarMenuVariant.id == variant_id, models.BarMenuVariant.company_id == company_id).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    variant.status = UNSTATUS
    variant.updated_by = user_id
    remaining = (
        db.query(models.BarMenuVariant)
        .filter(models.BarMenuVariant.menu_id == variant.menu_id, models.BarMenuVariant.status == STATUS, models.BarMenuVariant.id != variant_id)
        .count()
    )
    if remaining == 0:
        menu = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == variant.menu_id).first()
        if menu:
            menu.has_variants = False
    db.commit()
    return {"status": "success", "message": "Variant deactivated"}


# =====================================================
# MODIFIERS
# =====================================================
@router.post("/menu/{menu_id}/modifier", status_code=status.HTTP_201_CREATED)
def create_menu_modifier(menu_id: int, payload: ModifierIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    menu = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id).first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    modifier = models.BarMenuModifier(menu_id=menu_id, created_by=user_id, company_id=company_id, **payload.dict())
    db.add(modifier)
    db.commit()
    db.refresh(modifier)
    return {"status": "success", "data": {"id": modifier.id}}


@router.put("/modifier/{modifier_id}", status_code=status.HTTP_200_OK)
def update_menu_modifier(modifier_id: int, payload: ModifierUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    modifier = db.query(models.BarMenuModifier).filter(models.BarMenuModifier.id == modifier_id, models.BarMenuModifier.company_id == company_id).first()
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(modifier, field, value)
    modifier.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Modifier updated"}


@router.delete("/modifier/{modifier_id}", status_code=status.HTTP_200_OK)
def deactivate_menu_modifier(modifier_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    modifier = db.query(models.BarMenuModifier).filter(models.BarMenuModifier.id == modifier_id, models.BarMenuModifier.company_id == company_id).first()
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found")
    modifier.status = UNSTATUS
    modifier.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Modifier deactivated"}

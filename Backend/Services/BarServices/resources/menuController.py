import logging
import math
import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import get_db, models
from resources.utils import verify_authentication
from configs.base_config import BaseConfig, CommonWords

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

# Menu photo uploads. The bar screen had no upload endpoint at all, so it asked
# the user to paste a hosted image URL while the identical restaurant screen
# offered a file picker -- the same job done two different ways, and one of them
# depending on an image the property has to host somewhere else.
UPLOAD_PATH = "./templates/static/upload_image"
os.makedirs(UPLOAD_PATH, exist_ok=True)
ALLOWED_UPLOAD_EXTS = BaseConfig.UPLOAD_ALLOWED_EXTENSIONS
UPLOAD_MAX_BYTES = BaseConfig.UPLOAD_MAX_BYTES


def _sniff_family(data: bytes) -> str:
    """The file family implied by the first bytes of `data`.

    An extension is a claim the client makes; these bytes are what the server
    actually received. Only the header is read, which is all that is needed to
    tell an accepted family apart from a text file or a script wearing an
    image's name.
    """
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"%PDF-"):
        return "pdf"
    return ""


_UPLOAD_EXT_FAMILY = {
    "jpg": "jpeg", "jpeg": "jpeg",
    "png": "png",
    "gif": "gif",
    "webp": "webp",
    "pdf": "pdf",
}


def _sanitize_upload(upload: UploadFile) -> tuple[str, bytes]:
    """Validate and read an incoming UploadFile. Mirrors RestaurantServices.

    Also proves the bytes are an image of the type the name claims, so a `.png`
    name is no longer enough to store a text file or a script (C-085).
    """
    if not upload or not upload.filename:
        raise HTTPException(status_code=400, detail="File is required")
    ext = os.path.splitext(upload.filename)[1].lstrip(".").lower()
    if not ext or ext not in ALLOWED_UPLOAD_EXTS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    data = upload.file.read(UPLOAD_MAX_BYTES + 1)
    if len(data) > UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds size limit")
    expected = _UPLOAD_EXT_FAMILY.get(ext)
    if expected and _sniff_family(data) != expected:
        raise HTTPException(
            status_code=400,
            detail=f"File content is not a valid {expected.upper()} image",
        )
    return ext, data


def _write_upload(data: bytes, ext: str) -> str:
    """Persist bytes under UPLOAD_PATH; return the site-relative path.

    Relative, not absolute: this service binds to 127.0.0.1, so a URL built
    from its own address resolves to the VIEWER'S machine. The client fetches
    the path through the gateway with the session token -- see
    Frontend/src/hooks/useAuthedMedia.js.
    """
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(UPLOAD_PATH, safe_name), "wb") as fh:
        fh.write(data)
    return f"/templates/static/upload_image/{safe_name}"


def gen_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


@router.post("/upload_image", status_code=status.HTTP_201_CREATED)
def upload_menu_image(request: Request, image: UploadFile = File(...)):
    _auth(request)
    ext, data = _sanitize_upload(image)
    return {"status": "success", "data": {"url": _write_upload(data, ext)}}


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


MENU_AVAILABILITY = ("Available", "Out of Stock")
MODIFIER_TYPES = ("Add-on", "Remove")


def _validate_menu_values(*, item_name, description, price, cost_price, tax_percentage, preparation_time, availability_status, dietary_tags=None):
    if item_name is not None:
        item_name = str(item_name).strip()
        if not item_name or len(item_name) > 150:
            raise HTTPException(status_code=400, detail="item_name must be 1-150 characters")
    if description is not None and len(str(description).strip()) > 255:
        raise HTTPException(status_code=400, detail="description must not exceed 255 characters")
    if price is not None and float(price) <= 0:
        raise HTTPException(status_code=400, detail="price must be greater than zero")
    if cost_price is not None and float(cost_price) < 0:
        raise HTTPException(status_code=400, detail="cost_price must be zero or greater")
    if tax_percentage is not None and not (0 <= float(tax_percentage) <= 100):
        raise HTTPException(status_code=400, detail="tax_percentage must be between 0 and 100")
    if preparation_time is not None and int(preparation_time) < 0:
        raise HTTPException(status_code=400, detail="preparation_time must be zero or greater")
    if availability_status is not None and availability_status not in MENU_AVAILABILITY:
        raise HTTPException(status_code=400, detail="availability_status is invalid")
    if dietary_tags is not None and (not isinstance(dietary_tags, list) or any(len(str(x).strip()) > 50 for x in dietary_tags)):
        raise HTTPException(status_code=400, detail="dietary_tags are invalid")
    return item_name


def _validate_variant(variant):
    name = str(variant.variant_name).strip()
    if not name or len(name) > 50:
        raise HTTPException(status_code=400, detail="variant_name must be 1-50 characters")
    if float(variant.price) <= 0:
        raise HTTPException(status_code=400, detail="variant price must be greater than zero")
    return name


def _validate_modifier(modifier):
    name = str(modifier.modifier_name).strip()
    if not name or len(name) > 100:
        raise HTTPException(status_code=400, detail="modifier_name must be 1-100 characters")
    if modifier.price is not None and float(modifier.price) < 0:
        raise HTTPException(status_code=400, detail="modifier price must be zero or greater")
    if modifier.modifier_type is not None and modifier.modifier_type not in MODIFIER_TYPES:
        raise HTTPException(status_code=400, detail="modifier_type is invalid")
    return name


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
    item_name = _validate_menu_values(
        item_name=payload.item_name,
        description=payload.description,
        price=payload.price,
        cost_price=payload.cost_price,
        tax_percentage=payload.tax_percentage,
        preparation_time=payload.preparation_time,
        availability_status=payload.availability_status,
        dietary_tags=payload.dietary_tags,
    )
    category = db.query(models.BarMenuCategory).filter(
        models.BarMenuCategory.id == payload.category_id,
        models.BarMenuCategory.company_id == company_id,
        models.BarMenuCategory.status == STATUS,
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="category_id does not exist")
    station = db.query(models.BarStation).filter(
        models.BarStation.id == payload.station_id,
        models.BarStation.company_id == company_id,
        models.BarStation.status == STATUS,
        models.BarStation.is_active == True,
    ).first()
    if not station:
        raise HTTPException(status_code=400, detail="station_id does not exist")
    if payload.sub_category_id is not None:
        sub = db.query(models.BarMenuSubCategory).filter(
            models.BarMenuSubCategory.id == payload.sub_category_id,
            models.BarMenuSubCategory.category_id == payload.category_id,
            models.BarMenuSubCategory.company_id == company_id,
            models.BarMenuSubCategory.status == STATUS,
        ).first()
        if not sub:
            raise HTTPException(status_code=400, detail="sub_category_id does not belong to category")
    duplicate = db.query(models.BarMenuItem).filter(
        models.BarMenuItem.company_id == company_id,
        models.BarMenuItem.category_id == payload.category_id,
        models.BarMenuItem.status == STATUS,
        models.BarMenuItem.item_name == item_name,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists")
    variant_names = [_validate_variant(v) for v in (payload.variants or [])]
    if len(set(variant_names)) != len(variant_names):
        raise HTTPException(status_code=400, detail="Variant names must be unique within a menu item")
    modifier_names = [_validate_modifier(m) for m in (payload.modifiers or [])]
    if len(set(modifier_names)) != len(modifier_names):
        raise HTTPException(status_code=400, detail="Modifier names must be unique within a menu item")
    try:
        data = payload.dict(exclude={"variants", "modifiers"})
        data["item_name"] = item_name
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
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


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
        db.query(models.BarMenuVariant)
        .filter(
            models.BarMenuVariant.menu_id.in_(item_ids),
            models.BarMenuVariant.company_id == company_id,
            models.BarMenuVariant.status == STATUS,
        )
        .all()
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
    item = db.query(models.BarMenuItem).filter(
        models.BarMenuItem.id == menu_id,
        models.BarMenuItem.company_id == company_id,
        models.BarMenuItem.status == STATUS,
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    variants = db.query(models.BarMenuVariant).filter(
        models.BarMenuVariant.menu_id == menu_id,
        models.BarMenuVariant.company_id == company_id,
        models.BarMenuVariant.status == STATUS,
    ).all()
    modifiers = db.query(models.BarMenuModifier).filter(
        models.BarMenuModifier.menu_id == menu_id,
        models.BarMenuModifier.company_id == company_id,
        models.BarMenuModifier.status == STATUS,
    ).all()
    recipe = db.query(models.BarRecipe).filter(
        models.BarRecipe.menu_id == menu_id,
        models.BarRecipe.company_id == company_id,
        models.BarRecipe.status == STATUS,
    ).all()
    return {"status": "success", "data": {**item.__dict__, "variants": variants, "modifiers": modifiers, "recipe": recipe}}


@router.put("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def update_menu_item(menu_id: int, payload: MenuItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.BarMenuItem)
        .filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id, models.BarMenuItem.status == STATUS)
        .with_for_update()
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = _validate_menu_values(
        item_name=updates.get("item_name", item.item_name),
        description=updates.get("description", item.description),
        price=updates.get("price", item.price),
        cost_price=updates.get("cost_price", item.cost_price),
        tax_percentage=updates.get("tax_percentage", item.tax_percentage),
        preparation_time=updates.get("preparation_time", item.preparation_time),
        availability_status=updates.get("availability_status", item.availability_status),
        dietary_tags=updates.get("dietary_tags", item.dietary_tags),
    )
    category_id = updates.get("category_id", item.category_id)
    station_id = updates.get("station_id", item.station_id)
    if not db.query(models.BarMenuCategory).filter(models.BarMenuCategory.id == category_id, models.BarMenuCategory.company_id == company_id, models.BarMenuCategory.status == STATUS).first():
        raise HTTPException(status_code=400, detail="category_id does not exist")
    if not db.query(models.BarStation).filter(models.BarStation.id == station_id, models.BarStation.company_id == company_id, models.BarStation.status == STATUS, models.BarStation.is_active == True).first():
        raise HTTPException(status_code=400, detail="station_id does not exist")
    if updates.get("sub_category_id", item.sub_category_id) is not None:
        sub_id = updates.get("sub_category_id", item.sub_category_id)
        if not db.query(models.BarMenuSubCategory).filter(models.BarMenuSubCategory.id == sub_id, models.BarMenuSubCategory.category_id == category_id, models.BarMenuSubCategory.company_id == company_id, models.BarMenuSubCategory.status == STATUS).first():
            raise HTTPException(status_code=400, detail="sub_category_id does not belong to category")
    duplicate = db.query(models.BarMenuItem).filter(
        models.BarMenuItem.company_id == company_id,
        models.BarMenuItem.category_id == category_id,
        models.BarMenuItem.status == STATUS,
        models.BarMenuItem.id != item.id,
        models.BarMenuItem.item_name == candidate_name,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists")
    for field, value in updates.items():
        setattr(item, field, value)
    if "item_name" in updates:
        item.item_name = candidate_name
    item.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists")
    return {"status": "success", "message": "Menu item updated"}


@router.delete("/menu/{menu_id}", status_code=status.HTTP_200_OK)
def deactivate_menu_item(menu_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    item = (
        db.query(models.BarMenuItem)
        .filter(models.BarMenuItem.id == menu_id, models.BarMenuItem.company_id == company_id, models.BarMenuItem.status == STATUS)
        .with_for_update()
        .first()
    )
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
    menu = db.query(models.BarMenuItem).filter(
        models.BarMenuItem.id == menu_id,
        models.BarMenuItem.company_id == company_id,
        models.BarMenuItem.status == STATUS,
    ).with_for_update().first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    name = _validate_variant(payload)
    if db.query(models.BarMenuVariant).filter(
        models.BarMenuVariant.menu_id == menu_id,
        models.BarMenuVariant.status == STATUS,
        models.BarMenuVariant.variant_name == name,
    ).first():
        raise HTTPException(status_code=409, detail="Variant name already exists")
    values = payload.dict()
    values["variant_name"] = name
    variant = models.BarMenuVariant(menu_id=menu_id, created_by=user_id, company_id=company_id, **values)
    db.add(variant)
    menu.has_variants = True
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Variant name already exists")
    db.refresh(variant)
    return {"status": "success", "data": {"id": variant.id}}


@router.put("/variant/{variant_id}", status_code=status.HTTP_200_OK)
def update_menu_variant(variant_id: int, payload: VariantUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    variant = db.query(models.BarMenuVariant).filter(
        models.BarMenuVariant.id == variant_id,
        models.BarMenuVariant.company_id == company_id,
        models.BarMenuVariant.status == STATUS,
    ).with_for_update().first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    updates = payload.dict(exclude_unset=True)
    candidate = type("VariantCandidate", (), {"variant_name": updates.get("variant_name", variant.variant_name), "price": updates.get("price", variant.price)})()
    name = _validate_variant(candidate)
    if db.query(models.BarMenuVariant).filter(
        models.BarMenuVariant.menu_id == variant.menu_id,
        models.BarMenuVariant.status == STATUS,
        models.BarMenuVariant.id != variant.id,
        models.BarMenuVariant.variant_name == name,
    ).first():
        raise HTTPException(status_code=409, detail="Variant name already exists")
    for field, value in updates.items():
        setattr(variant, field, value)
    variant.variant_name = name
    variant.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Variant name already exists")
    return {"status": "success", "message": "Variant updated"}


@router.delete("/variant/{variant_id}", status_code=status.HTTP_200_OK)
def deactivate_menu_variant(variant_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    variant = db.query(models.BarMenuVariant).filter(
        models.BarMenuVariant.id == variant_id,
        models.BarMenuVariant.company_id == company_id,
        models.BarMenuVariant.status == STATUS,
    ).with_for_update().first()
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
    menu = db.query(models.BarMenuItem).filter(
        models.BarMenuItem.id == menu_id,
        models.BarMenuItem.company_id == company_id,
        models.BarMenuItem.status == STATUS,
    ).with_for_update().first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    name = _validate_modifier(payload)
    if db.query(models.BarMenuModifier).filter(
        models.BarMenuModifier.menu_id == menu_id,
        models.BarMenuModifier.status == STATUS,
        models.BarMenuModifier.modifier_name == name,
    ).first():
        raise HTTPException(status_code=409, detail="Modifier already exists")
    values = payload.dict()
    values["modifier_name"] = name
    modifier = models.BarMenuModifier(menu_id=menu_id, created_by=user_id, company_id=company_id, **values)
    db.add(modifier)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Modifier already exists")
    db.refresh(modifier)
    return {"status": "success", "data": {"id": modifier.id}}


@router.put("/modifier/{modifier_id}", status_code=status.HTTP_200_OK)
def update_menu_modifier(modifier_id: int, payload: ModifierUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    modifier = db.query(models.BarMenuModifier).filter(
        models.BarMenuModifier.id == modifier_id,
        models.BarMenuModifier.company_id == company_id,
        models.BarMenuModifier.status == STATUS,
    ).with_for_update().first()
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found")
    updates = payload.dict(exclude_unset=True)
    candidate = type("ModifierCandidate", (), {
        "modifier_name": updates.get("modifier_name", modifier.modifier_name),
        "price": updates.get("price", modifier.price),
        "modifier_type": updates.get("modifier_type", modifier.modifier_type),
    })()
    name = _validate_modifier(candidate)
    if db.query(models.BarMenuModifier).filter(
        models.BarMenuModifier.menu_id == modifier.menu_id,
        models.BarMenuModifier.status == STATUS,
        models.BarMenuModifier.id != modifier.id,
        models.BarMenuModifier.modifier_name == name,
    ).first():
        raise HTTPException(status_code=409, detail="Modifier already exists")
    for field, value in updates.items():
        setattr(modifier, field, value)
    modifier.modifier_name = name
    modifier.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Modifier already exists")
    return {"status": "success", "message": "Modifier updated"}


@router.delete("/modifier/{modifier_id}", status_code=status.HTTP_200_OK)
def deactivate_menu_modifier(modifier_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    modifier = db.query(models.BarMenuModifier).filter(
        models.BarMenuModifier.id == modifier_id,
        models.BarMenuModifier.company_id == company_id,
        models.BarMenuModifier.status == STATUS,
    ).with_for_update().first()
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found")
    modifier.status = UNSTATUS
    modifier.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Modifier deactivated"}

import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy import func, or_
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


# `jpg` and `jpeg` are one family, so either extension is accepted for a JPEG
# header and neither is accepted for anything else.
_UPLOAD_EXT_FAMILY = {
    "jpg": "jpeg", "jpeg": "jpeg",
    "png": "png",
    "gif": "gif",
    "webp": "webp",
    "pdf": "pdf",
}


def _sanitize_upload(upload: UploadFile) -> tuple[str, bytes]:
    """Validate and read an incoming UploadFile.

    Returns ``(safe_extension, raw_bytes)``. Raises HTTPException on any
    violation (bad extension, content that is not that type of file, oversized
    payload, unreadable filename).

    The extension check alone stored whatever it was given, so a `.png` name
    was enough to persist a text file or a script on the menu (C-085).
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
    """Persist bytes under UPLOAD_PATH using a random filename; return its path.

    This used to return an ABSOLUTE url built from RESTAURANT_SERVICE_URL, on
    the reasoning that the gateway has no route for /templates/static and a
    plain <img> tag cannot send an Authorization header. Both halves were
    wrong in practice:

      * RestaurantServices binds to 127.0.0.1 (see its .env; only the gateway
        is meant to be reachable from outside), so the URL that got written
        into the database — http://127.0.0.1:8050/... — resolves to the
        VIEWER'S own machine. Every menu photo was therefore broken for every
        user except someone browsing on the server itself.
      * The gateway proxies `/restaurant/{path:path}` to this service, and
        /templates/static IS one of those paths. The client fetches it with the
        session token and renders it from an object URL — see
        Frontend/src/hooks/useAuthedMedia.js, which is how room photos,
        employee photos and incident attachments already work.

    So the stored value is now the site-relative path, matching what
    MasterDataServices stores, and the client resolves it through the gateway.
    Rows written before this change still hold an absolute URL; the frontend
    passes those through untouched rather than rewriting stored data.
    """
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(UPLOAD_PATH, safe_name)
    with open(dest, "wb") as fh:
        fh.write(data)
    return f"/templates/static/upload_image/{safe_name}"


def gen_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


@router.post("/upload_image", status_code=status.HTTP_201_CREATED)
def upload_menu_image(request: Request, image: UploadFile = File(...)):
    _auth(request)
    ext, data = _sanitize_upload(image)
    url = _write_upload(data, ext)
    return {"status": "success", "data": {"url": url}}


MENU_AVAILABILITY = ("Available", "Out of Stock")
MODIFIER_TYPES = ("Add-on", "Remove")


def _validate_menu_values(
    *,
    item_name,
    description,
    price,
    cost_price,
    tax_percentage,
    preparation_time,
    availability_status,
    is_veg=None,
    dietary_tags=None,
):
    if item_name is not None:
        item_name = str(item_name).strip()
        if not item_name:
            raise HTTPException(status_code=400, detail="item_name is required")
        if len(item_name) > 150:
            raise HTTPException(status_code=400, detail="item_name must not exceed 150 characters")
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
    if dietary_tags is not None:
        if not isinstance(dietary_tags, list) or any(len(str(tag).strip()) > 50 for tag in dietary_tags):
            raise HTTPException(status_code=400, detail="dietary_tags are invalid")
    return item_name


def _validate_variant_value(variant):
    name = str(variant.variant_name).strip()
    if not name or len(name) > 50:
        raise HTTPException(status_code=400, detail="variant_name must be 1-50 characters")
    if float(variant.price) <= 0:
        raise HTTPException(status_code=400, detail="variant price must be greater than zero")


def _validate_modifier_value(modifier):
    name = str(modifier.modifier_name).strip()
    if not name or len(name) > 100:
        raise HTTPException(status_code=400, detail="modifier_name must be 1-100 characters")
    if modifier.price is not None and float(modifier.price) < 0:
        raise HTTPException(status_code=400, detail="modifier price must be zero or greater")
    if modifier.modifier_type is not None and modifier.modifier_type not in MODIFIER_TYPES:
        raise HTTPException(status_code=400, detail="modifier_type is invalid")


# =====================================================
# SCHEMAS
# =====================================================
class CategoryIn(BaseModel):
    category_name: str
    description: Optional[str] = None
    kitchen_id: int
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
    kitchen_id: int
    availability_status: str = "Available"
    is_veg: bool = True
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
    kitchen_id: Optional[int] = None
    availability_status: Optional[str] = None
    is_veg: Optional[bool] = None
    dietary_tags: Optional[List[str]] = None
    item_image: Optional[str] = None
    happy_hour_eligible: Optional[bool] = None


class ComboItemIn(BaseModel):
    menu_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("quantity must be at least 1")
        return value


class ComboIn(BaseModel):
    combo_name: str
    description: Optional[str] = None
    combo_price: float
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    items: List[ComboItemIn]

    @field_validator("combo_price")
    @classmethod
    def price_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("combo_price must be greater than zero")
        return value

    @model_validator(mode="after")
    def dates_must_be_ordered(self):
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must be on or after valid_from")
        return self


class ComboUpdate(BaseModel):
    combo_name: Optional[str] = None
    description: Optional[str] = None
    combo_price: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    items: Optional[List[ComboItemIn]] = None

    @field_validator("combo_price")
    @classmethod
    def price_must_be_positive(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value <= 0:
            raise ValueError("combo_price must be greater than zero")
        return value

    @model_validator(mode="after")
    def supplied_dates_must_be_ordered(self):
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must be on or after valid_from")
        return self


def _validate_combo_fields(*, combo_name, description, combo_price, valid_from=None, valid_to=None):
    if combo_name is not None:
        combo_name = str(combo_name).strip()
        if not combo_name:
            raise HTTPException(status_code=400, detail="combo_name is required")
        if len(combo_name) > 150:
            raise HTTPException(status_code=400, detail="combo_name must not exceed 150 characters")
    if description is not None and len(str(description).strip()) > 255:
        raise HTTPException(status_code=400, detail="description must not exceed 255 characters")
    if combo_price is not None and float(combo_price) <= 0:
        raise HTTPException(status_code=400, detail="combo_price must be greater than zero")
    if valid_from is not None and valid_to is not None and valid_to < valid_from:
        raise HTTPException(status_code=400, detail="valid_to must be on or after valid_from")
    return combo_name


def _validate_combo_items(db: Session, company_id: str, items: List[ComboItemIn]) -> None:
    """Reject malformed/stale combo lines before the database raises a raw 500."""
    menu_ids = [item.menu_id for item in items]
    if len(menu_ids) != len(set(menu_ids)):
        raise HTTPException(status_code=400, detail="A menu item can appear only once in a combo")
    if not menu_ids:
        raise HTTPException(status_code=400, detail="A combo must contain at least one menu item")
    found = (
        db.query(models.RestaurantMenu.id)
        .filter(
            models.RestaurantMenu.company_id == company_id,
            models.RestaurantMenu.status == STATUS,
            models.RestaurantMenu.id.in_(menu_ids),
        )
        .all()
    )
    if len(found) != len(set(menu_ids)):
        raise HTTPException(status_code=400, detail="One or more menu items are unavailable")


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
        item_name = _validate_menu_values(
            item_name=payload.item_name,
            description=payload.description,
            price=payload.price,
            cost_price=payload.cost_price,
            tax_percentage=payload.tax_percentage,
            preparation_time=payload.preparation_time,
            availability_status=payload.availability_status,
            is_veg=payload.is_veg,
            dietary_tags=payload.dietary_tags,
        )
        category = db.query(models.MenuCategory).filter(
            models.MenuCategory.id == payload.category_id,
            models.MenuCategory.company_id == company_id,
            models.MenuCategory.status == STATUS,
        ).first()
        if not category:
            raise HTTPException(status_code=400, detail="category_id does not exist")
        kitchen = db.query(models.Kitchen).filter(
            models.Kitchen.id == payload.kitchen_id,
            models.Kitchen.company_id == company_id,
            models.Kitchen.status == STATUS,
        ).first()
        if not kitchen:
            raise HTTPException(status_code=400, detail="kitchen_id does not exist")
        if payload.sub_category_id is not None:
            sub = db.query(models.MenuSubCategory).filter(
                models.MenuSubCategory.id == payload.sub_category_id,
                models.MenuSubCategory.category_id == payload.category_id,
                models.MenuSubCategory.company_id == company_id,
                models.MenuSubCategory.status == STATUS,
            ).first()
            if not sub:
                raise HTTPException(status_code=400, detail="sub_category_id does not belong to category")
        duplicate = db.query(models.RestaurantMenu).filter(
            models.RestaurantMenu.company_id == company_id,
            models.RestaurantMenu.branch_id == "MAIN",
            models.RestaurantMenu.category_id == payload.category_id,
            models.RestaurantMenu.status == STATUS,
            func.lower(models.RestaurantMenu.item_name) == item_name.lower(),
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="An active menu item with this name already exists in the category")
        for variant in payload.variants or []:
            _validate_variant_value(variant)
        for modifier in payload.modifiers or []:
            _validate_modifier_value(modifier)
        data = payload.dict(exclude={"variants", "modifiers"})
        data["item_name"] = item_name
        item = models.RestaurantMenu(
            item_code=gen_code("ITM"),
            has_variants=bool(payload.variants),
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

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="An active menu item with this name already exists in the category")
        db.refresh(item)
        return {"status": "success", "data": {"id": item.id, "item_code": item.item_code}}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists in the category")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/menu", status_code=status.HTTP_200_OK)
def list_menu_items(
    request: Request,
    category_id: Optional[int] = Query(None),
    kitchen_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.RestaurantMenu).filter(
        models.RestaurantMenu.company_id == company_id, models.RestaurantMenu.status == STATUS
    )
    if category_id is not None:
        q = q.filter(models.RestaurantMenu.category_id == category_id)
    if kitchen_id is not None:
        q = q.filter(models.RestaurantMenu.kitchen_id == kitchen_id)
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
    updates = payload.dict(exclude_unset=True)
    candidate_name = _validate_menu_values(
        item_name=updates.get("item_name", item.item_name),
        description=updates.get("description", item.description),
        price=updates.get("price", item.price),
        cost_price=updates.get("cost_price", item.cost_price),
        tax_percentage=updates.get("tax_percentage", item.tax_percentage),
        preparation_time=updates.get("preparation_time", item.preparation_time),
        availability_status=updates.get("availability_status", item.availability_status),
        is_veg=updates.get("is_veg", item.is_veg),
        dietary_tags=updates.get("dietary_tags", item.dietary_tags),
    )
    candidate_category = updates.get("category_id", item.category_id)
    candidate_kitchen = updates.get("kitchen_id", item.kitchen_id)
    category = db.query(models.MenuCategory).filter(
        models.MenuCategory.id == candidate_category,
        models.MenuCategory.company_id == company_id,
        models.MenuCategory.status == STATUS,
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="category_id does not exist")
    kitchen = db.query(models.Kitchen).filter(
        models.Kitchen.id == candidate_kitchen,
        models.Kitchen.company_id == company_id,
        models.Kitchen.status == STATUS,
    ).first()
    if not kitchen:
        raise HTTPException(status_code=400, detail="kitchen_id does not exist")
    candidate_sub = updates.get("sub_category_id", item.sub_category_id)
    if candidate_sub is not None:
        sub = db.query(models.MenuSubCategory).filter(
            models.MenuSubCategory.id == candidate_sub,
            models.MenuSubCategory.category_id == candidate_category,
            models.MenuSubCategory.company_id == company_id,
            models.MenuSubCategory.status == STATUS,
        ).first()
        if not sub:
            raise HTTPException(status_code=400, detail="sub_category_id does not belong to category")
    duplicate = db.query(models.RestaurantMenu).filter(
        models.RestaurantMenu.company_id == company_id,
        models.RestaurantMenu.branch_id == item.branch_id,
        models.RestaurantMenu.category_id == candidate_category,
        models.RestaurantMenu.status == STATUS,
        models.RestaurantMenu.id != item.id,
        func.lower(models.RestaurantMenu.item_name) == candidate_name.lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists in the category")
    for field, value in updates.items():
        setattr(item, field, value)
    if "item_name" in updates:
        item.item_name = candidate_name
    item.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active menu item with this name already exists in the category")
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
# VARIANTS
# =====================================================
@router.post("/menu/{menu_id}/variant", status_code=status.HTTP_201_CREATED)
def create_menu_variant(menu_id: int, payload: VariantIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    menu = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == menu_id, models.RestaurantMenu.company_id == company_id)
        .first()
    )
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    _validate_variant_value(payload)
    duplicate = db.query(models.MenuVariant).filter(
        models.MenuVariant.menu_id == menu_id,
        models.MenuVariant.status == STATUS,
        func.lower(models.MenuVariant.variant_name) == payload.variant_name.strip().lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Variant name already exists")
    variant = models.MenuVariant(menu_id=menu_id, created_by=user_id, company_id=company_id, **payload.dict())
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
    variant = (
        db.query(models.MenuVariant)
        .filter(models.MenuVariant.id == variant_id, models.MenuVariant.company_id == company_id)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = updates.get("variant_name", variant.variant_name).strip()
    candidate_price = updates.get("price", variant.price)
    if not candidate_name or len(candidate_name) > 50 or float(candidate_price) <= 0:
        raise HTTPException(status_code=400, detail="Variant name/price is invalid")
    duplicate = db.query(models.MenuVariant).filter(
        models.MenuVariant.menu_id == variant.menu_id,
        models.MenuVariant.status == STATUS,
        models.MenuVariant.id != variant.id,
        func.lower(models.MenuVariant.variant_name) == candidate_name.lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Variant name already exists")
    for field, value in updates.items():
        setattr(variant, field, value)
    variant.variant_name = candidate_name
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
    variant = (
        db.query(models.MenuVariant)
        .filter(models.MenuVariant.id == variant_id, models.MenuVariant.company_id == company_id)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    variant.status = UNSTATUS
    variant.updated_by = user_id
    remaining = (
        db.query(models.MenuVariant)
        .filter(models.MenuVariant.menu_id == variant.menu_id, models.MenuVariant.status == STATUS, models.MenuVariant.id != variant_id)
        .count()
    )
    if remaining == 0:
        menu = db.query(models.RestaurantMenu).filter(models.RestaurantMenu.id == variant.menu_id).first()
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
    menu = (
        db.query(models.RestaurantMenu)
        .filter(models.RestaurantMenu.id == menu_id, models.RestaurantMenu.company_id == company_id)
        .first()
    )
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    _validate_modifier_value(payload)
    duplicate = db.query(models.MenuModifier).filter(
        models.MenuModifier.menu_id == menu_id,
        models.MenuModifier.status == STATUS,
        func.lower(models.MenuModifier.modifier_name) == payload.modifier_name.strip().lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Modifier already exists")
    modifier = models.MenuModifier(menu_id=menu_id, created_by=user_id, company_id=company_id, **payload.dict())
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
    modifier = (
        db.query(models.MenuModifier)
        .filter(models.MenuModifier.id == modifier_id, models.MenuModifier.company_id == company_id)
        .first()
    )
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = updates.get("modifier_name", modifier.modifier_name).strip()
    candidate_price = updates.get("price", modifier.price)
    candidate_type = updates.get("modifier_type", modifier.modifier_type)
    if not candidate_name or len(candidate_name) > 100 or (candidate_price is not None and float(candidate_price) < 0) or (candidate_type is not None and candidate_type not in MODIFIER_TYPES):
        raise HTTPException(status_code=400, detail="Modifier fields are invalid")
    duplicate = db.query(models.MenuModifier).filter(
        models.MenuModifier.menu_id == modifier.menu_id,
        models.MenuModifier.status == STATUS,
        models.MenuModifier.id != modifier.id,
        func.lower(models.MenuModifier.modifier_name) == candidate_name.lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Modifier already exists")
    for field, value in updates.items():
        setattr(modifier, field, value)
    modifier.modifier_name = candidate_name
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
    modifier = (
        db.query(models.MenuModifier)
        .filter(models.MenuModifier.id == modifier_id, models.MenuModifier.company_id == company_id)
        .first()
    )
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modifier not found")
    modifier.status = UNSTATUS
    modifier.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Modifier deactivated"}


# =====================================================
# COMBO / PACKAGE DEALS
# =====================================================
@router.post("/combo", status_code=status.HTTP_201_CREATED)
def create_combo(payload: ComboIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    _validate_combo_fields(
        combo_name=payload.combo_name,
        description=payload.description,
        combo_price=payload.combo_price,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
    )
    _validate_combo_items(db, company_id, payload.items)
    duplicate = db.query(models.ComboDeal).filter(
        models.ComboDeal.company_id == company_id,
        models.ComboDeal.branch_id == "MAIN",
        models.ComboDeal.status == STATUS,
        models.ComboDeal.is_active == True,
        func.lower(models.ComboDeal.combo_name) == payload.combo_name.strip().lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active combo with this name already exists")
    try:
        combo = models.ComboDeal(
            combo_code=gen_code("CMB"),
            combo_name=payload.combo_name.strip(),
            description=payload.description,
            combo_price=payload.combo_price,
            valid_from=payload.valid_from,
            valid_to=payload.valid_to,
            is_active=True,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(combo)
        db.flush()
        for it in payload.items:
            db.add(models.ComboItem(combo_id=combo.id, menu_id=it.menu_id, quantity=it.quantity, created_by=user_id, company_id=company_id))
        db.commit()
        db.refresh(combo)
        return {"status": "success", "data": {"id": combo.id, "combo_code": combo.combo_code}}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active combo with this name already exists")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/combo", status_code=status.HTTP_200_OK)
def list_combos(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    combos = (
        db.query(models.ComboDeal)
        .filter(models.ComboDeal.company_id == company_id, models.ComboDeal.status == STATUS, models.ComboDeal.is_active == True)
        .all()
    )
    combo_ids = [c.id for c in combos]
    items = db.query(models.ComboItem).filter(models.ComboItem.combo_id.in_(combo_ids)).all() if combo_ids else []
    items_by_combo = {}
    for it in items:
        items_by_combo.setdefault(it.combo_id, []).append(it)
    data = [{**c.__dict__, "items": items_by_combo.get(c.id, [])} for c in combos]
    return {"status": "success", "count": len(data), "data": data}


@router.put("/combo/{combo_id}", status_code=status.HTTP_200_OK)
def update_combo(combo_id: int, payload: ComboUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    combo = (
        db.query(models.ComboDeal)
        .filter(models.ComboDeal.id == combo_id, models.ComboDeal.company_id == company_id)
        .with_for_update()
        .first()
    )
    if not combo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combo not found")
    fields = payload.dict(exclude_unset=True, exclude={"items"})
    effective_from = fields.get("valid_from", combo.valid_from)
    effective_to = fields.get("valid_to", combo.valid_to)
    candidate_name = _validate_combo_fields(
        combo_name=fields.get("combo_name", combo.combo_name),
        description=fields.get("description", combo.description),
        combo_price=fields.get("combo_price", combo.combo_price),
        valid_from=effective_from,
        valid_to=effective_to,
    )
    duplicate = db.query(models.ComboDeal).filter(
        models.ComboDeal.company_id == company_id,
        models.ComboDeal.branch_id == combo.branch_id,
        models.ComboDeal.status == STATUS,
        models.ComboDeal.is_active == True,
        models.ComboDeal.id != combo.id,
        func.lower(models.ComboDeal.combo_name) == candidate_name.lower(),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active combo with this name already exists")
    if payload.items is not None:
        _validate_combo_items(db, company_id, payload.items)
    try:
        for field, value in fields.items():
            setattr(combo, field, value)
        if "combo_name" in fields:
            combo.combo_name = candidate_name
        combo.updated_by = user_id
        if payload.items is not None:
            db.query(models.ComboItem).filter(models.ComboItem.combo_id == combo_id).delete()
            for it in payload.items:
                db.add(models.ComboItem(combo_id=combo.id, menu_id=it.menu_id, quantity=it.quantity, created_by=user_id, company_id=company_id))
        db.commit()
        return {"status": "success", "message": "Combo updated"}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active combo with this name already exists")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.delete("/combo/{combo_id}", status_code=status.HTTP_200_OK)
def deactivate_combo(combo_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    combo = (
        db.query(models.ComboDeal)
        .filter(models.ComboDeal.id == combo_id, models.ComboDeal.company_id == company_id)
        .first()
    )
    if not combo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combo not found")
    combo.status = UNSTATUS
    combo.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Combo deactivated"}

import math
import re
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import get_db, models
from resources.utils import verify_authentication
from resources.validation import (
    EMAIL_MESSAGE,
    clean_name,
    normalize_phone,
    validate_email,
)
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


GUEST_TYPES = ("Walk-In", "Regular", "VIP", "Hotel Guest")


def _validate_guest_values(*, first_name, last_name, mobile, email, guest_type,
                           special_notes=None, phone_region=None):
    if first_name is not None:
        first_name = str(first_name).strip()
        if not first_name or len(first_name) > 100:
            raise HTTPException(status_code=400, detail="first_name must be 1-100 characters")
    if last_name is not None and len(str(last_name).strip()) > 100:
        raise HTTPException(status_code=400, detail="last_name must not exceed 100 characters")
    # Country-aware, and stored as E.164. This used to be
    # `re.fullmatch(r"\d{10}", ...)`, which rejected every guest from outside
    # the property's home country and stored the same number three ways
    # depending on who typed it (C-086).
    mobile = normalize_phone(mobile, field="mobile", default_region=phone_region,
                             allow_mobile_only=True)
    if email is not None and str(email).strip() and not validate_email(email):
        raise HTTPException(status_code=400, detail=EMAIL_MESSAGE)
    if guest_type is not None and guest_type not in GUEST_TYPES:
        raise HTTPException(status_code=400, detail="guest_type is invalid")
    if special_notes is not None and len(str(special_notes).strip()) > 255:
        raise HTTPException(status_code=400, detail="special_notes must not exceed 255 characters")
    return first_name, mobile


# =====================================================
# SCHEMAS
# =====================================================
class GuestIn(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    mobile: str
    # The country the mobile was typed in, as an ISO-3166-1 alpha-2 code. Sent
    # by the client because a number with no country code is ambiguous and the
    # API refuses to guess one -- see resources/validation.py. Optional only so
    # an international number (+...) still works without it.
    phone_region: Optional[str] = None
    email: Optional[str] = None
    guest_type: str = "Walk-In"
    special_notes: Optional[str] = None


class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    phone_region: Optional[str] = None
    email: Optional[str] = None
    guest_type: Optional[str] = None
    special_notes: Optional[str] = None


class AddressIn(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class FeedbackIn(BaseModel):
    order_id: Optional[int] = None
    rating: int
    comments: Optional[str] = None


class LoyaltyAdjustIn(BaseModel):
    points: float
    reason: Optional[str] = None


# =====================================================
# GUESTS
# =====================================================
@router.post("/guest", status_code=status.HTTP_201_CREATED)
def create_guest(payload: GuestIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    first_name, mobile = _validate_guest_values(
        first_name=payload.first_name,
        last_name=payload.last_name,
        mobile=payload.mobile,
        email=payload.email,
        guest_type=payload.guest_type,
        special_notes=payload.special_notes,
        phone_region=payload.phone_region,
    )
    existing = db.query(models.BarGuest).filter(
        models.BarGuest.mobile == mobile,
        models.BarGuest.company_id == company_id,
        models.BarGuest.status == STATUS,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="A guest with this mobile number already exists")
    # `phone_region` travels with the request and is not a column: it exists so
    # a national number can be read, and is dropped before the row is built.
    values = payload.dict(exclude={"phone_region"})
    values.update({"first_name": first_name, "mobile": mobile})
    guest = models.BarGuest(guest_code=gen_code("BGST"), created_by=user_id, company_id=company_id, **values)
    db.add(guest)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A guest with this mobile number already exists")
    db.refresh(guest)
    return {"status": "success", "data": {"id": guest.id, "guest_code": guest.guest_code}}


@router.get("/guest", status_code=status.HTTP_200_OK)
def list_guests(request: Request, mobile: Optional[str] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarGuest).filter(models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
    if mobile:
        q = q.filter(models.BarGuest.mobile == mobile)
    rows = q.order_by(models.BarGuest.first_name.asc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


@router.get("/guest/{guest_id}", status_code=status.HTTP_200_OK)
def get_guest(guest_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.BarGuest).filter(
        models.BarGuest.id == guest_id,
        models.BarGuest.company_id == company_id,
        models.BarGuest.status == STATUS,
    ).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    addresses = db.query(models.BarGuestAddress).filter(
        models.BarGuestAddress.guest_id == guest_id,
        models.BarGuestAddress.company_id == company_id,
        models.BarGuestAddress.status == STATUS,
    ).all()
    history = db.query(models.BarGuestVisitHistory).filter(
        models.BarGuestVisitHistory.guest_id == guest_id,
        models.BarGuestVisitHistory.company_id == company_id,
    ).order_by(models.BarGuestVisitHistory.visit_date.desc()).all()
    return {"status": "success", "data": {**guest.__dict__, "addresses": addresses, "visit_history": history}}


@router.put("/guest/{guest_id}", status_code=status.HTTP_200_OK)
def update_guest(guest_id: int, payload: GuestUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = (
        db.query(models.BarGuest)
        .filter(models.BarGuest.id == guest_id, models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
        .with_for_update()
        .first()
    )
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    # `phone_region` is request-scoped, not a column: excluded from the values
    # that are written back to the row.
    updates = payload.dict(exclude_unset=True, exclude={"phone_region"})
    # Rows written before country-aware validation hold a bare national number.
    # Re-validating one that the caller did not touch would refuse the edit --
    # changing a guest's name would fail because of a number they never edited.
    # So an unchanged mobile is left exactly as it is, and the row is only
    # normalised when the number itself is being changed.
    if "mobile" not in updates or str(updates.get("mobile")).strip() == str(guest.mobile).strip():
        mobile = guest.mobile
        first_name = clean_name(updates.get("first_name", guest.first_name), field="first_name") or guest.first_name
    else:
        first_name, mobile = _validate_guest_values(
            first_name=updates.get("first_name", guest.first_name),
            last_name=updates.get("last_name", guest.last_name),
            mobile=updates.get("mobile"),
            email=updates.get("email", guest.email),
            guest_type=updates.get("guest_type", guest.guest_type),
            special_notes=updates.get("special_notes", guest.special_notes),
            phone_region=payload.phone_region,
        )
    duplicate = db.query(models.BarGuest).filter(
        models.BarGuest.id != guest.id,
        models.BarGuest.mobile == mobile,
        models.BarGuest.company_id == company_id,
        models.BarGuest.status == STATUS,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="A guest with this mobile number already exists")
    for field, value in updates.items():
        setattr(guest, field, value)
    guest.first_name = first_name
    guest.mobile = mobile
    guest.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A guest with this mobile number already exists")
    return {"status": "success", "message": "Guest updated"}


@router.delete("/guest/{guest_id}", status_code=status.HTTP_200_OK)
def deactivate_guest(guest_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = (
        db.query(models.BarGuest)
        .filter(models.BarGuest.id == guest_id, models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
        .with_for_update()
        .first()
    )
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    guest.status = UNSTATUS
    guest.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Guest deactivated"}


@router.post("/guest/{guest_id}/address", status_code=status.HTTP_201_CREATED)
def add_guest_address(guest_id: int, payload: AddressIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.BarGuest).filter(
        models.BarGuest.id == guest_id,
        models.BarGuest.company_id == company_id,
        models.BarGuest.status == STATUS,
    ).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    values = payload.dict()
    for field, limit in (("address", 255), ("city", 100), ("state", 100), ("country", 100), ("postal_code", 20)):
        if values.get(field) is not None and len(str(values[field]).strip()) > limit:
            raise HTTPException(status_code=400, detail=f"{field} is too long")
    addr = models.BarGuestAddress(guest_id=guest_id, company_id=company_id, **values)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return {"status": "success", "data": {"id": addr.id}}


@router.post("/guest/{guest_id}/feedback", status_code=status.HTTP_201_CREATED)
def add_feedback(guest_id: int, payload: FeedbackIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.BarGuest).filter(
        models.BarGuest.id == guest_id,
        models.BarGuest.company_id == company_id,
        models.BarGuest.status == STATUS,
    ).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    if payload.comments is not None and len(str(payload.comments).strip()) > 255:
        raise HTTPException(status_code=400, detail="comments must not exceed 255 characters")
    if payload.order_id is not None and not db.query(models.BarOrder).filter(
        models.BarOrder.id == payload.order_id,
        models.BarOrder.company_id == company_id,
        models.BarOrder.status == STATUS,
    ).first():
        raise HTTPException(status_code=400, detail="order_id does not exist")
    if not (1 <= payload.rating <= 5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rating must be between 1 and 5")
    fb = models.BarGuestFeedback(guest_id=guest_id, company_id=company_id, **payload.dict())
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"status": "success", "data": {"id": fb.id}}


@router.post("/guest/{guest_id}/loyalty", status_code=status.HTTP_200_OK)
def adjust_loyalty(guest_id: int, payload: LoyaltyAdjustIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = (
        db.query(models.BarGuest)
        .filter(models.BarGuest.id == guest_id, models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
        .with_for_update()
        .first()
    )
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    if not math.isfinite(payload.points) or payload.points == 0:
        raise HTTPException(status_code=400, detail="points must be a finite non-zero number")
    new_balance = (guest.loyalty_points or 0) + payload.points
    if new_balance < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest does not have enough points to redeem")
    guest.loyalty_points = new_balance
    guest.updated_by = user_id
    db.commit()
    return {"status": "success", "data": {"loyalty_points": guest.loyalty_points}}

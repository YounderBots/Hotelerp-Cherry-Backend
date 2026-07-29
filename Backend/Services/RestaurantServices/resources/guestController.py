import uuid
from datetime import date
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
class GuestIn(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    mobile: str
    email: Optional[str] = None
    guest_type: str = "Walk-In"
    food_preferences: Optional[List[str]] = None
    special_notes: Optional[str] = None


class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    guest_type: Optional[str] = None
    food_preferences: Optional[List[str]] = None
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
    points: float  # positive = earn, negative = redeem
    reason: Optional[str] = None


# =====================================================
# GUESTS
# =====================================================
@router.post("/guest", status_code=status.HTTP_201_CREATED)
def create_guest(payload: GuestIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    existing = (
        db.query(models.Guest)
        .filter(models.Guest.mobile == payload.mobile, models.Guest.company_id == company_id, models.Guest.status == STATUS)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A guest with this mobile number already exists")
    guest = models.Guest(guest_code=gen_code("GST"), created_by=user_id, company_id=company_id, **payload.dict())
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return {"status": "success", "data": {"id": guest.id, "guest_code": guest.guest_code}}


@router.get("/guest", status_code=status.HTTP_200_OK)
def list_guests(request: Request, mobile: Optional[str] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.Guest).filter(models.Guest.company_id == company_id, models.Guest.status == STATUS)
    if mobile:
        q = q.filter(models.Guest.mobile == mobile)
    rows = q.order_by(models.Guest.first_name.asc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


@router.get("/guest/{guest_id}", status_code=status.HTTP_200_OK)
def get_guest(guest_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id, models.Guest.company_id == company_id).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    addresses = db.query(models.GuestAddress).filter(models.GuestAddress.guest_id == guest_id, models.GuestAddress.status == STATUS).all()
    history = db.query(models.GuestVisitHistory).filter(models.GuestVisitHistory.guest_id == guest_id).order_by(models.GuestVisitHistory.visit_date.desc()).all()
    return {"status": "success", "data": {**guest.__dict__, "addresses": addresses, "visit_history": history}}


@router.put("/guest/{guest_id}", status_code=status.HTTP_200_OK)
def update_guest(guest_id: int, payload: GuestUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id, models.Guest.company_id == company_id).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(guest, field, value)
    guest.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Guest updated"}


@router.delete("/guest/{guest_id}", status_code=status.HTTP_200_OK)
def deactivate_guest(guest_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id, models.Guest.company_id == company_id).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    guest.status = UNSTATUS
    guest.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Guest deactivated"}


@router.post("/guest/{guest_id}/address", status_code=status.HTTP_201_CREATED)
def add_guest_address(guest_id: int, payload: AddressIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id, models.Guest.company_id == company_id).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    addr = models.GuestAddress(guest_id=guest_id, company_id=company_id, **payload.dict())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return {"status": "success", "data": {"id": addr.id}}


@router.post("/guest/{guest_id}/feedback", status_code=status.HTTP_201_CREATED)
def add_feedback(guest_id: int, payload: FeedbackIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id, models.Guest.company_id == company_id).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    if not (1 <= payload.rating <= 5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rating must be between 1 and 5")
    fb = models.GuestFeedback(guest_id=guest_id, company_id=company_id, **payload.dict())
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"status": "success", "data": {"id": fb.id}}


@router.post("/guest/{guest_id}/loyalty", status_code=status.HTTP_200_OK)
def adjust_loyalty(guest_id: int, payload: LoyaltyAdjustIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id, models.Guest.company_id == company_id).first()
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    new_balance = (guest.loyalty_points or 0) + payload.points
    if new_balance < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest does not have enough points to redeem")
    guest.loyalty_points = new_balance
    guest.updated_by = user_id
    db.commit()
    return {"status": "success", "data": {"loyalty_points": guest.loyalty_points}}

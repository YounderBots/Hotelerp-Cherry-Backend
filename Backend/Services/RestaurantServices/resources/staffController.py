from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import get_db, models
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

STATUS = CommonWords.STATUS
UNSTATUS = CommonWords.UNSTATUS


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


# =====================================================
# SCHEMAS
# =====================================================
class ShiftIn(BaseModel):
    employee_id: int
    employee_name: Optional[str] = None
    role: str  # Waiter | Bartender | Chef | Cashier | Manager
    shift_date: date
    shift_start: time
    shift_end: Optional[time] = None
    section: Optional[str] = None
    floor_id: Optional[int] = None
    sales_target: Optional[float] = None


class ShiftUpdate(BaseModel):
    role: Optional[str] = None
    shift_start: Optional[time] = None
    shift_end: Optional[time] = None
    section: Optional[str] = None
    floor_id: Optional[int] = None
    sales_target: Optional[float] = None


class ClockInIn(BaseModel):
    opening_cash_float: Optional[float] = None


class ClockOutIn(BaseModel):
    closing_cash_amount: Optional[float] = None


# =====================================================
# STAFF SHIFT ASSIGNMENTS
# =====================================================
@router.post("/staff_assignment", status_code=status.HTTP_201_CREATED)
def create_shift(payload: ShiftIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    shift = models.RestaurantStaffAssignment(
        shift_status="Scheduled",
        actual_sales=0,
        created_by=user_id,
        company_id=company_id,
        **payload.dict(),
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return {"status": "success", "data": {"id": shift.id}}


@router.get("/staff_assignment", status_code=status.HTTP_200_OK)
def list_shifts(
    request: Request,
    shift_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.RestaurantStaffAssignment).filter(
        models.RestaurantStaffAssignment.company_id == company_id, models.RestaurantStaffAssignment.status == STATUS
    )
    if shift_date is not None:
        q = q.filter(models.RestaurantStaffAssignment.shift_date == shift_date)
    if employee_id is not None:
        q = q.filter(models.RestaurantStaffAssignment.employee_id == employee_id)
    rows = q.order_by(models.RestaurantStaffAssignment.shift_date.desc(), models.RestaurantStaffAssignment.shift_start.asc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/staff_assignment/{shift_id}", status_code=status.HTTP_200_OK)
def update_shift(shift_id: int, payload: ShiftUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    shift = (
        db.query(models.RestaurantStaffAssignment)
        .filter(models.RestaurantStaffAssignment.id == shift_id, models.RestaurantStaffAssignment.company_id == company_id)
        .first()
    )
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(shift, field, value)
    shift.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Shift updated"}


@router.delete("/staff_assignment/{shift_id}", status_code=status.HTTP_200_OK)
def cancel_shift(shift_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    shift = (
        db.query(models.RestaurantStaffAssignment)
        .filter(models.RestaurantStaffAssignment.id == shift_id, models.RestaurantStaffAssignment.company_id == company_id)
        .first()
    )
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    shift.status = UNSTATUS
    shift.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Shift cancelled"}


@router.post("/staff_assignment/{shift_id}/clock_in", status_code=status.HTTP_200_OK)
def clock_in(shift_id: int, payload: ClockInIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    shift = (
        db.query(models.RestaurantStaffAssignment)
        .filter(models.RestaurantStaffAssignment.id == shift_id, models.RestaurantStaffAssignment.company_id == company_id)
        .first()
    )
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    if shift.clock_in_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already clocked in")
    shift.clock_in_at = datetime.now()
    shift.opening_cash_float = payload.opening_cash_float
    shift.shift_status = "On Shift"
    shift.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Clocked in", "data": {"clock_in_at": shift.clock_in_at}}


@router.post("/staff_assignment/{shift_id}/clock_out", status_code=status.HTTP_200_OK)
def clock_out(shift_id: int, payload: ClockOutIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    shift = (
        db.query(models.RestaurantStaffAssignment)
        .filter(models.RestaurantStaffAssignment.id == shift_id, models.RestaurantStaffAssignment.company_id == company_id)
        .first()
    )
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    if not shift.clock_in_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot clock out before clocking in")
    if shift.clock_out_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already clocked out")

    shift.clock_out_at = datetime.now()
    shift.closing_cash_amount = payload.closing_cash_amount
    shift.shift_status = "Closed"
    shift.updated_by = user_id

    variance = None
    if payload.closing_cash_amount is not None and shift.opening_cash_float is not None:
        expected = (shift.opening_cash_float or 0) + (shift.actual_sales or 0)
        variance = round(payload.closing_cash_amount - expected, 2)

    db.commit()
    return {"status": "success", "message": "Clocked out", "data": {"clock_out_at": shift.clock_out_at, "cash_variance": variance}}

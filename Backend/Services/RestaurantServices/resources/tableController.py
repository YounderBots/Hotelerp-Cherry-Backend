import logging
import uuid
from datetime import date, datetime, time, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import get_db, models
from resources.utils import verify_authentication
from resources.validation import EMAIL_MESSAGE, normalize_phone, validate_email
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
FLOOR_TYPES = ("Restaurant", "Banquet", "Outdoor")
TABLE_TYPES = ("Standard", "VIP", "Private")
TABLE_SECTIONS = ("Restaurant", "Outdoor", "Banquet")
TABLE_STATUSES = ("Available", "Occupied", "Reserved", "Cleaning", "Blocked")
RESERVATION_SOURCES = ("Walk-In", "Phone", "Online", "Hotel Guest")
RESERVATION_STATUSES = ("Reserved", "Checked-In", "Completed", "Cancelled", "No-Show")


def gen_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# =====================================================
# SCHEMAS
# =====================================================
class FloorIn(BaseModel):
    floor_name: str
    floor_number: int
    floor_type: str
    description: Optional[str] = None
    total_tables: Optional[int] = None
    total_capacity: Optional[int] = None
    layout_json: Optional[dict] = None
    color_code: Optional[str] = None
    is_open: bool = True


class FloorUpdate(BaseModel):
    floor_name: Optional[str] = None
    floor_number: Optional[int] = None
    floor_type: Optional[str] = None
    description: Optional[str] = None
    total_tables: Optional[int] = None
    total_capacity: Optional[int] = None
    layout_json: Optional[dict] = None
    color_code: Optional[str] = None
    is_open: Optional[bool] = None


class TableIn(BaseModel):
    table_name: str
    table_number: int
    floor_id: int
    table_type: str
    seating_capacity: int
    section: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    shape: Optional[str] = None
    color_code: Optional[str] = None
    table_status: str = "Available"
    is_mergeable: bool = False


class TableUpdate(BaseModel):
    table_name: Optional[str] = None
    table_number: Optional[int] = None
    floor_id: Optional[int] = None
    table_type: Optional[str] = None
    seating_capacity: Optional[int] = None
    section: Optional[str] = None
    server_id: Optional[str] = None
    server_name: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    shape: Optional[str] = None
    color_code: Optional[str] = None
    table_status: Optional[str] = None
    is_mergeable: Optional[bool] = None
    current_order_id: Optional[int] = None


class TableMergeIn(BaseModel):
    table_ids: List[int]
    merged_table_name: str


class ReservationIn(BaseModel):
    reservation_date: date
    start_time: time
    end_time: Optional[time] = None
    table_id: int
    guest_name: str
    guest_mobile: str
    # ISO-3166-1 alpha-2 country the number was typed in; see
    # resources/validation.py for why it cannot be guessed.
    phone_region: Optional[str] = None
    guest_email: Optional[str] = None
    no_of_guests: int
    reservation_type: str = "Phone"
    occasion: Optional[str] = None
    special_requests: Optional[str] = None


class ReservationUpdate(BaseModel):
    reservation_status: Optional[str] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    order_id: Optional[int] = None
    order_number: Optional[str] = None


class WaitlistIn(BaseModel):
    guest_name: str
    guest_mobile: str
    # ISO-3166-1 alpha-2 country the number was typed in; see
    # resources/validation.py for why it cannot be guessed.
    phone_region: Optional[str] = None
    party_size: int
    floor_id: Optional[int] = None
    section: Optional[str] = None
    estimated_wait_minutes: Optional[int] = None


class WaitlistUpdate(BaseModel):
    waitlist_status: Optional[str] = None
    table_id: Optional[int] = None


# Mirrors `waitlist_status_enum` in models.py.
WAITLIST_STATUSES = ("Waiting", "Notified", "Seated", "Cancelled")


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


def _validate_floor_values(
    *,
    floor_name,
    floor_number,
    floor_type,
    total_tables,
    total_capacity,
):
    if floor_name is not None:
        floor_name = str(floor_name).strip()
        if not floor_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_name is required")
        if len(floor_name) > 100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_name must not exceed 100 characters")
    if floor_number is not None and int(floor_number) <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_number must be positive")
    if floor_type is not None and floor_type not in FLOOR_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_type must be Restaurant, Banquet or Outdoor")
    for label, value in (("total_tables", total_tables), ("total_capacity", total_capacity)):
        if value is not None and int(value) < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} must be zero or greater")
    return floor_name


def _validate_table_values(
    *,
    table_name,
    table_number,
    floor_id,
    seating_capacity,
    table_type,
    section,
    table_status,
):
    if table_name is not None:
        table_name = str(table_name).strip()
        if not table_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_name is required")
        if len(table_name) > 100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_name must not exceed 100 characters")
    for label, value in (("table_number", table_number), ("floor_id", floor_id), ("seating_capacity", seating_capacity)):
        if value is not None and int(value) <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} must be positive")
    if table_type is not None and table_type not in TABLE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_type must be Standard, VIP or Private")
    if section is not None and section not in TABLE_SECTIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="section must be Restaurant, Outdoor or Banquet")
    if table_status is not None and table_status not in TABLE_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_status is invalid")
    return table_name


def _validate_reservation_values(payload):
    if payload.no_of_guests is None or int(payload.no_of_guests) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no_of_guests must be at least 1")
    if payload.reservation_type not in RESERVATION_SOURCES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reservation_type is invalid")
    if payload.end_time is not None and payload.end_time <= payload.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be after start_time")
    for key, label in (("guest_name", "guest_name"), ("guest_mobile", "guest_mobile"), ("guest_email", "guest_email"), ("occasion", "occasion"), ("special_requests", "special_requests")):
        value = getattr(payload, key, None)
        if value is not None and len(str(value).strip()) > 255:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} must not exceed 255 characters")
    # A booking is made by telephone as often as online, so the number is checked
    # for real rather than only for length: it must be a number in a real
    # numbering plan, and the region decides how a national one is read (C-086).
    normalize_phone(getattr(payload, "guest_mobile", None), field="guest_mobile",
                    default_region=getattr(payload, "phone_region", None))
    # Same for the address a confirmation is sent to.
    guest_email = getattr(payload, "guest_email", None)
    if guest_email and str(guest_email).strip() and not validate_email(guest_email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_MESSAGE)
    return True


# =====================================================
# FLOOR MANAGEMENT
# =====================================================
@router.post("/floor", status_code=status.HTTP_201_CREATED)
def create_floor(payload: FloorIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        floor_name = _validate_floor_values(
            floor_name=payload.floor_name,
            floor_number=payload.floor_number,
            floor_type=payload.floor_type,
            total_tables=payload.total_tables,
            total_capacity=payload.total_capacity,
        )
        duplicate = (
            db.query(models.RestaurantFloor)
            .filter(
                models.RestaurantFloor.company_id == company_id,
                models.RestaurantFloor.status == STATUS,
                models.RestaurantFloor.branch_id == "MAIN",
                or_(
                    models.RestaurantFloor.floor_number == payload.floor_number,
                    func.lower(models.RestaurantFloor.floor_name) == floor_name.lower(),
                ),
            )
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Floor number or name already exists")
        values = payload.dict()
        values["floor_name"] = floor_name
        floor = models.RestaurantFloor(
            floor_code=gen_code("FLR"),
            **values,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(floor)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Floor number or name already exists")
        db.refresh(floor)
        return {"status": "success", "data": {"id": floor.id, "floor_code": floor.floor_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/floor", status_code=status.HTTP_200_OK)
def list_floors(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.RestaurantFloor)
        .filter(models.RestaurantFloor.company_id == company_id, models.RestaurantFloor.status == STATUS)
        .order_by(models.RestaurantFloor.floor_number.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/floor/{floor_id}", status_code=status.HTTP_200_OK)
def update_floor(floor_id: int, payload: FloorUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    floor = (
        db.query(models.RestaurantFloor)
        .filter(models.RestaurantFloor.id == floor_id, models.RestaurantFloor.company_id == company_id)
        .first()
    )
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = updates.get("floor_name", floor.floor_name)
    candidate_number = updates.get("floor_number", floor.floor_number)
    candidate_type = updates.get("floor_type", floor.floor_type)
    candidate_tables = updates.get("total_tables", floor.total_tables)
    candidate_capacity = updates.get("total_capacity", floor.total_capacity)
    candidate_name = _validate_floor_values(
        floor_name=candidate_name,
        floor_number=candidate_number,
        floor_type=candidate_type,
        total_tables=candidate_tables,
        total_capacity=candidate_capacity,
    )
    duplicate = (
        db.query(models.RestaurantFloor)
        .filter(
            models.RestaurantFloor.company_id == company_id,
            models.RestaurantFloor.status == STATUS,
            models.RestaurantFloor.branch_id == floor.branch_id,
            models.RestaurantFloor.id != floor.id,
            or_(
                models.RestaurantFloor.floor_number == candidate_number,
                func.lower(models.RestaurantFloor.floor_name) == candidate_name.lower(),
            ),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Floor number or name already exists")
    for field, value in updates.items():
        setattr(floor, field, value)
    if "floor_name" in updates:
        floor.floor_name = candidate_name
    floor.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Floor number or name already exists")
    return {"status": "success", "message": "Floor updated"}


@router.delete("/floor/{floor_id}", status_code=status.HTTP_200_OK)
def deactivate_floor(floor_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    floor = (
        db.query(models.RestaurantFloor)
        .filter(models.RestaurantFloor.id == floor_id, models.RestaurantFloor.company_id == company_id)
        .first()
    )
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    floor.status = UNSTATUS
    floor.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Floor deactivated"}


# =====================================================
# TABLE MANAGEMENT
# =====================================================
@router.post("/table", status_code=status.HTTP_201_CREATED)
def create_table(payload: TableIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        floor = (
            db.query(models.RestaurantFloor)
            .filter(models.RestaurantFloor.id == payload.floor_id, models.RestaurantFloor.company_id == company_id)
            .first()
        )
        if not floor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_id does not exist")
        table_name = _validate_table_values(
            table_name=payload.table_name,
            table_number=payload.table_number,
            floor_id=payload.floor_id,
            seating_capacity=payload.seating_capacity,
            table_type=payload.table_type,
            section=payload.section,
            table_status=payload.table_status,
        )
        duplicate = (
            db.query(models.RestaurantTable)
            .filter(
                models.RestaurantTable.company_id == company_id,
                models.RestaurantTable.branch_id == "MAIN",
                models.RestaurantTable.floor_id == payload.floor_id,
                models.RestaurantTable.status == STATUS,
                or_(
                    models.RestaurantTable.table_number == payload.table_number,
                    func.lower(models.RestaurantTable.table_name) == table_name.lower(),
                ),
            )
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table number or name already exists on this floor")
        values = payload.dict()
        values["table_name"] = table_name
        table = models.RestaurantTable(
            table_code=gen_code("TBL"),
            floor_code=floor.floor_code,
            created_by=user_id,
            company_id=company_id,
            **values,
        )
        db.add(table)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table number or name already exists on this floor")
        db.refresh(table)
        return {"status": "success", "data": {"id": table.id, "table_code": table.table_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/table", status_code=status.HTTP_200_OK)
def list_tables(
    request: Request,
    floor_id: Optional[int] = Query(None),
    table_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.RestaurantTable).filter(
        models.RestaurantTable.company_id == company_id, models.RestaurantTable.status == STATUS
    )
    if floor_id is not None:
        q = q.filter(models.RestaurantTable.floor_id == floor_id)
    if table_status:
        q = q.filter(models.RestaurantTable.table_status == table_status)
    rows = q.order_by(models.RestaurantTable.table_number.asc()).all()

    # Resolve the two foreign keys the table screen shows to a human. It was
    # rendering the floor by joining in the browser (which meant an unloaded
    # floor list showed the raw id) and the current order as the raw
    # restaurant_order.id -- a row number no waiter can act on. order_number is
    # the code printed on the KOT.
    floor_ids = {r.floor_id for r in rows if r.floor_id}
    floors = (
        db.query(models.RestaurantFloor).filter(models.RestaurantFloor.id.in_(floor_ids)).all()
        if floor_ids
        else []
    )
    floor_name_by_id = {f.id: f.floor_name for f in floors}

    order_ids = {r.current_order_id for r in rows if r.current_order_id}
    orders = (
        db.query(models.RestaurantOrder).filter(models.RestaurantOrder.id.in_(order_ids)).all()
        if order_ids
        else []
    )
    order_number_by_id = {o.id: o.order_number for o in orders}

    data = [
        {
            **r.__dict__,
            "floor_name": floor_name_by_id.get(r.floor_id),
            "current_order_number": order_number_by_id.get(r.current_order_id),
        }
        for r in rows
    ]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/table/{table_id}", status_code=status.HTTP_200_OK)
def get_table(table_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    table = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.id == table_id, models.RestaurantTable.company_id == company_id)
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return {"status": "success", "data": table}


@router.put("/table/{table_id}", status_code=status.HTTP_200_OK)
def update_table(table_id: int, payload: TableUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    table = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.id == table_id, models.RestaurantTable.company_id == company_id)
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = updates.get("table_name", table.table_name)
    candidate_number = updates.get("table_number", table.table_number)
    candidate_floor = updates.get("floor_id", table.floor_id)
    candidate_capacity = updates.get("seating_capacity", table.seating_capacity)
    candidate_type = updates.get("table_type", table.table_type)
    candidate_section = updates.get("section", table.section)
    candidate_status = updates.get("table_status", table.table_status)
    candidate_name = _validate_table_values(
        table_name=candidate_name,
        table_number=candidate_number,
        floor_id=candidate_floor,
        seating_capacity=candidate_capacity,
        table_type=candidate_type,
        section=candidate_section,
        table_status=candidate_status,
    )
    duplicate = (
        db.query(models.RestaurantTable)
        .filter(
            models.RestaurantTable.company_id == company_id,
            models.RestaurantTable.branch_id == table.branch_id,
            models.RestaurantTable.floor_id == candidate_floor,
            models.RestaurantTable.status == STATUS,
            models.RestaurantTable.id != table.id,
            or_(
                models.RestaurantTable.table_number == candidate_number,
                func.lower(models.RestaurantTable.table_name) == candidate_name.lower(),
            ),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table number or name already exists on this floor")
    for field, value in updates.items():
        setattr(table, field, value)
    if "table_name" in updates:
        table.table_name = candidate_name
    table.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table number or name already exists on this floor")
    return {"status": "success", "message": "Table updated"}


@router.delete("/table/{table_id}", status_code=status.HTTP_200_OK)
def deactivate_table(table_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    table = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.id == table_id, models.RestaurantTable.company_id == company_id)
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    table.status = UNSTATUS
    table.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Table deactivated"}


# =====================================================
# TABLE MERGE / UNMERGE
# =====================================================
@router.post("/table/merge", status_code=status.HTTP_201_CREATED)
def merge_tables(payload: TableMergeIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    if len(payload.table_ids) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select at least two tables to merge")

    tables = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.id.in_(payload.table_ids), models.RestaurantTable.company_id == company_id)
        .all()
    )
    if len(tables) != len(payload.table_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more tables were not found")
    for t in tables:
        if not t.is_mergeable:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Table {t.table_name} is not mergeable")
        if t.table_status == "Occupied":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Table {t.table_name} is currently occupied")

    try:
        merge = models.RestaurantTableMerge(
            merge_code=gen_code("MRG"),
            merged_table_name=payload.merged_table_name,
            merged_by=user_id,
            is_active=True,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(merge)
        db.flush()

        for t in tables:
            db.add(models.RestaurantTableMergeDetail(merge_id=merge.id, table_id=t.id, created_by=user_id, company_id=company_id))
            t.table_status = "Occupied"
            t.updated_by = user_id

        db.commit()
        db.refresh(merge)
        return {"status": "success", "data": {"id": merge.id, "merge_code": merge.merge_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.post("/table/unmerge/{merge_id}", status_code=status.HTTP_200_OK)
def unmerge_tables(merge_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    merge = (
        db.query(models.RestaurantTableMerge)
        .filter(models.RestaurantTableMerge.id == merge_id, models.RestaurantTableMerge.company_id == company_id)
        .first()
    )
    if not merge or not merge.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active merge not found")

    details = db.query(models.RestaurantTableMergeDetail).filter(models.RestaurantTableMergeDetail.merge_id == merge_id).all()
    table_ids = [d.table_id for d in details]
    tables = db.query(models.RestaurantTable).filter(models.RestaurantTable.id.in_(table_ids)).all()
    for t in tables:
        t.table_status = "Cleaning"
        t.updated_by = user_id

    merge.is_active = False
    merge.unmerged_at = datetime.now()
    merge.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Tables unmerged"}


# =====================================================
# TABLE RESERVATIONS
# =====================================================
@router.post("/table_reservation", status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    _validate_reservation_values(payload)
    table = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.id == payload.table_id, models.RestaurantTable.company_id == company_id)
        .with_for_update()
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id does not exist")
    if table.table_status in ("Occupied", "Reserved"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table is already reserved or occupied")
    existing = (
        db.query(models.RestaurantTableReservation)
        .filter(
            models.RestaurantTableReservation.table_id == payload.table_id,
            models.RestaurantTableReservation.reservation_date == payload.reservation_date,
            models.RestaurantTableReservation.status == STATUS,
            models.RestaurantTableReservation.reservation_status.in_(["Reserved", "Checked-In"]),
        )
        .all()
    )
    for row in existing:
        row_end = row.end_time or time(23, 59, 59)
        new_end = payload.end_time or time(23, 59, 59)
        if payload.start_time < row_end and new_end > row.start_time:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table is already reserved for that time")
    try:
        reservation = models.RestaurantTableReservation(
            reservation_code=gen_code("RSV"),
            table_code=table.table_code,
            floor_id=table.floor_id,
            floor_code=table.floor_code,
            reservation_status="Reserved",
            created_by=user_id,
            company_id=company_id,
            **payload.dict(),
        )
        db.add(reservation)
        table.table_status = "Reserved"
        table.updated_by = user_id
        db.commit()
        db.refresh(reservation)
        return {"status": "success", "data": {"id": reservation.id, "reservation_code": reservation.reservation_code}}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table reservation conflicts with an existing booking")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/table_reservation", status_code=status.HTTP_200_OK)
def list_reservations(
    request: Request,
    reservation_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.RestaurantTableReservation).filter(
        models.RestaurantTableReservation.company_id == company_id,
        models.RestaurantTableReservation.status == STATUS,
    )
    if reservation_date is not None:
        q = q.filter(models.RestaurantTableReservation.reservation_date == reservation_date)
    rows = q.order_by(models.RestaurantTableReservation.start_time.asc()).all()

    # The table's name, so the screen does not have to join it against a
    # separately-fetched table list and fall back to printing the raw id.
    table_ids = {r.table_id for r in rows if r.table_id}
    tables = (
        db.query(models.RestaurantTable).filter(models.RestaurantTable.id.in_(table_ids)).all()
        if table_ids
        else []
    )
    table_by_id = {t.id: t for t in tables}

    data = []
    for r in rows:
        table = table_by_id.get(r.table_id)
        data.append(
            {
                **r.__dict__,
                "table_name": table.table_name if table else None,
                "table_code": table.table_code if table else None,
                "table_label": (
                    f"{table.table_name} ({table.table_code})" if table else None
                ),
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/table_reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def get_reservation(reservation_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    reservation = (
        db.query(models.RestaurantTableReservation)
        .filter(models.RestaurantTableReservation.id == reservation_id, models.RestaurantTableReservation.company_id == company_id)
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return {"status": "success", "data": reservation}


@router.put("/table_reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def update_reservation(reservation_id: int, payload: ReservationUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    reservation = (
        db.query(models.RestaurantTableReservation)
        .filter(models.RestaurantTableReservation.id == reservation_id, models.RestaurantTableReservation.company_id == company_id)
        .with_for_update()
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    if payload.reservation_status is not None and payload.reservation_status not in RESERVATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reservation_status is invalid")
    if reservation.reservation_status in ("Completed", "Cancelled", "No-Show") and payload.reservation_status not in (None, reservation.reservation_status):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Terminal reservation cannot transition again")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(reservation, field, value)
    reservation.updated_by = user_id

    if payload.reservation_status in ("Cancelled", "No-Show", "Completed"):
        table = (
            db.query(models.RestaurantTable)
            .filter(models.RestaurantTable.id == reservation.table_id, models.RestaurantTable.company_id == company_id)
            .with_for_update()
            .first()
        )
        if table and table.table_status in ("Reserved", "Occupied"):
            table.table_status = "Available"
            table.updated_by = user_id
    elif payload.reservation_status == "Checked-In":
        table = (
            db.query(models.RestaurantTable)
            .filter(models.RestaurantTable.id == reservation.table_id, models.RestaurantTable.company_id == company_id)
            .with_for_update()
            .first()
        )
        if table:
            if table.table_status not in ("Reserved", "Occupied"):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table is no longer available for check-in")
            table.table_status = "Occupied"
            table.updated_by = user_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reservation conflicts with an existing booking")
    return {"status": "success", "message": "Reservation updated"}


# =====================================================
# WAITLIST
# =====================================================
@router.post("/waitlist", status_code=status.HTTP_201_CREATED)
def add_to_waitlist(payload: WaitlistIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        entry = models.RestaurantWaitlist(
            waitlist_code=gen_code("WL"),
            waitlist_status="Waiting",
            created_by=user_id,
            company_id=company_id,
            **payload.dict(),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return {"status": "success", "data": {"id": entry.id, "waitlist_code": entry.waitlist_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/waitlist", status_code=status.HTTP_200_OK)
def list_waitlist(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.RestaurantWaitlist)
        .filter(
            models.RestaurantWaitlist.company_id == company_id,
            models.RestaurantWaitlist.status == STATUS,
            models.RestaurantWaitlist.waitlist_status.in_(["Waiting", "Notified"]),
        )
        .order_by(models.RestaurantWaitlist.wait_start_time.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/waitlist/{waitlist_id}", status_code=status.HTTP_200_OK)
def update_waitlist(waitlist_id: int, payload: WaitlistUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    entry = (
        db.query(models.RestaurantWaitlist)
        .filter(models.RestaurantWaitlist.id == waitlist_id, models.RestaurantWaitlist.company_id == company_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waitlist entry not found")

    if payload.waitlist_status == "Notified":
        entry.notified_at = datetime.now()
    elif payload.waitlist_status == "Seated":
        entry.seated_at = datetime.now()
        if payload.table_id:
            # Scoped to this tenant. Unscoped, a caller could seat their party
            # on another property's table id and flip it to Occupied -- a write
            # into a different company's floor plan, from an id they can guess.
            table = (
                db.query(models.RestaurantTable)
                .filter(
                    models.RestaurantTable.id == payload.table_id,
                    models.RestaurantTable.company_id == company_id,
                )
                .first()
            )
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Table not found",
                )
            if table.table_status == "Occupied":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="That table is already occupied",
                )
            table.table_status = "Occupied"
            table.updated_by = user_id
            entry.table_id = table.id

    for field, value in payload.dict(exclude_unset=True).items():
        if field == "table_id":
            # Written above, only against a table that exists in this tenant.
            continue
        if field == "waitlist_status" and value is not None:
            # The column is an ENUM; an unknown value reaches MySQL and comes
            # back as "Data truncated for column" -- a 500 for a bad request.
            if value not in WAITLIST_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"waitlist_status must be one of: {', '.join(WAITLIST_STATUSES)}",
                )
        setattr(entry, field, value)
    entry.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Waitlist entry updated"}

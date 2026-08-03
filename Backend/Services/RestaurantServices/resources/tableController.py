import uuid
from datetime import date, datetime, time
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
    party_size: int
    floor_id: Optional[int] = None
    section: Optional[str] = None
    estimated_wait_minutes: Optional[int] = None


class WaitlistUpdate(BaseModel):
    waitlist_status: Optional[str] = None
    table_id: Optional[int] = None


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


# =====================================================
# FLOOR MANAGEMENT
# =====================================================
@router.post("/floor", status_code=status.HTTP_201_CREATED)
def create_floor(payload: FloorIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    try:
        floor = models.RestaurantFloor(
            floor_code=gen_code("FLR"),
            **payload.dict(),
            created_by=user_id,
            company_id=company_id,
        )
        db.add(floor)
        db.commit()
        db.refresh(floor)
        return {"status": "success", "data": {"id": floor.id, "floor_code": floor.floor_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(floor, field, value)
    floor.updated_by = user_id
    db.commit()
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
        table = models.RestaurantTable(
            table_code=gen_code("TBL"),
            floor_code=floor.floor_code,
            created_by=user_id,
            company_id=company_id,
            **payload.dict(),
        )
        db.add(table)
        db.commit()
        db.refresh(table)
        return {"status": "success", "data": {"id": table.id, "table_code": table.table_code}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    return {"status": "success", "count": len(rows), "data": rows}


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
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(table, field, value)
    table.updated_by = user_id
    db.commit()
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    table = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.id == payload.table_id, models.RestaurantTable.company_id == company_id)
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id does not exist")
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    return {"status": "success", "count": len(rows), "data": rows}


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
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(reservation, field, value)
    reservation.updated_by = user_id

    if payload.reservation_status in ("Cancelled", "No-Show", "Completed"):
        table = db.query(models.RestaurantTable).filter(models.RestaurantTable.id == reservation.table_id).first()
        if table and table.table_status == "Reserved":
            table.table_status = "Available"
            table.updated_by = user_id
    elif payload.reservation_status == "Checked-In":
        table = db.query(models.RestaurantTable).filter(models.RestaurantTable.id == reservation.table_id).first()
        if table:
            table.table_status = "Occupied"
            table.updated_by = user_id

    db.commit()
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
            table = db.query(models.RestaurantTable).filter(models.RestaurantTable.id == payload.table_id).first()
            if table:
                table.table_status = "Occupied"
                table.updated_by = user_id

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(entry, field, value)
    entry.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Waitlist entry updated"}

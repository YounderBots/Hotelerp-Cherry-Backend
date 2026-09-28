import logging
import math
import re
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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


def _validate_floor_values(*, floor_name, floor_number, description=None, total_tables=None, total_capacity=None, color_code=None):
    if floor_name is not None:
        floor_name = str(floor_name).strip()
        if not floor_name or len(floor_name) > 100:
            raise HTTPException(status_code=400, detail="floor_name must be 1-100 characters")
    if floor_number is not None and int(floor_number) < 0:
        raise HTTPException(status_code=400, detail="floor_number must be zero or greater")
    if description is not None and len(str(description).strip()) > 255:
        raise HTTPException(status_code=400, detail="description must not exceed 255 characters")
    for field, value in (("total_tables", total_tables), ("total_capacity", total_capacity)):
        if value is not None and (not math.isfinite(float(value)) or float(value) < 0):
            raise HTTPException(status_code=400, detail=f"{field} must be zero or greater")
    if color_code is not None and not re.fullmatch(r"^#[0-9A-Fa-f]{6}$", str(color_code)):
        raise HTTPException(status_code=400, detail="color_code must be a six-digit hex color")
    return floor_name


TABLE_TYPES = ("Counter", "Table", "Booth", "VIP Lounge")
TABLE_STATUSES = ("Available", "Occupied", "Reserved", "Cleaning", "Blocked")


def _validate_table_values(*, table_name, table_number, seating_capacity, table_type=None, table_status=None, server_name=None):
    if table_name is not None:
        table_name = str(table_name).strip()
        if not table_name or len(table_name) > 100:
            raise HTTPException(status_code=400, detail="table_name must be 1-100 characters")
    if table_number is not None and int(table_number) < 1:
        raise HTTPException(status_code=400, detail="table_number must be at least one")
    if seating_capacity is not None and int(seating_capacity) < 1:
        raise HTTPException(status_code=400, detail="seating_capacity must be at least one")
    if table_type is not None and table_type not in TABLE_TYPES:
        raise HTTPException(status_code=400, detail="table_type is invalid")
    if table_status is not None and table_status not in TABLE_STATUSES:
        raise HTTPException(status_code=400, detail="table_status is invalid")
    if server_name is not None and len(str(server_name).strip()) > 100:
        raise HTTPException(status_code=400, detail="server_name must not exceed 100 characters")
    return table_name


# =====================================================
# SCHEMAS
# =====================================================
class FloorIn(BaseModel):
    floor_name: str
    floor_number: int
    description: Optional[str] = None
    total_tables: Optional[int] = None
    total_capacity: Optional[int] = None
    layout_json: Optional[dict] = None
    color_code: Optional[str] = None
    is_open: bool = True


class FloorUpdate(BaseModel):
    floor_name: Optional[str] = None
    floor_number: Optional[int] = None
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
    table_status: str = "Available"


class TableUpdate(BaseModel):
    table_name: Optional[str] = None
    table_number: Optional[int] = None
    floor_id: Optional[int] = None
    table_type: Optional[str] = None
    seating_capacity: Optional[int] = None
    server_id: Optional[str] = None
    server_name: Optional[str] = None
    table_status: Optional[str] = None
    current_order_id: Optional[int] = None


# =====================================================
# FLOOR MANAGEMENT
# =====================================================
@router.post("/floor", status_code=status.HTTP_201_CREATED)
def create_floor(payload: FloorIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    floor_name = _validate_floor_values(
        floor_name=payload.floor_name,
        floor_number=payload.floor_number,
        description=payload.description,
        total_tables=payload.total_tables,
        total_capacity=payload.total_capacity,
        color_code=payload.color_code,
    )
    duplicate = db.query(models.BarFloor).filter(
        models.BarFloor.company_id == company_id,
        models.BarFloor.status == STATUS,
        (models.BarFloor.floor_number == payload.floor_number) | (models.BarFloor.floor_name == floor_name),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active floor with this number or name already exists")
    try:
        values = payload.dict()
        values["floor_name"] = floor_name
        floor = models.BarFloor(
            floor_code=gen_code("BFLR"),
            **values,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(floor)
        db.commit()
        db.refresh(floor)
        return {"status": "success", "data": {"id": floor.id, "floor_code": floor.floor_code}}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active floor with this number or name already exists")
    except Exception as e:
        db.rollback()
        raise _server_error(e)


@router.get("/floor", status_code=status.HTTP_200_OK)
def list_floors(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = (
        db.query(models.BarFloor)
        .filter(models.BarFloor.company_id == company_id, models.BarFloor.status == STATUS)
        .order_by(models.BarFloor.floor_number.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/floor/{floor_id}", status_code=status.HTTP_200_OK)
def update_floor(floor_id: int, payload: FloorUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    floor = (
        db.query(models.BarFloor)
        .filter(models.BarFloor.id == floor_id, models.BarFloor.company_id == company_id, models.BarFloor.status == STATUS)
        .with_for_update()
        .first()
    )
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = _validate_floor_values(
        floor_name=updates.get("floor_name", floor.floor_name),
        floor_number=updates.get("floor_number", floor.floor_number),
        description=updates.get("description", floor.description),
        total_tables=updates.get("total_tables", floor.total_tables),
        total_capacity=updates.get("total_capacity", floor.total_capacity),
        color_code=updates.get("color_code", floor.color_code),
    )
    candidate_number = updates.get("floor_number", floor.floor_number)
    duplicate = db.query(models.BarFloor).filter(
        models.BarFloor.company_id == company_id,
        models.BarFloor.status == STATUS,
        models.BarFloor.id != floor.id,
        (models.BarFloor.floor_number == candidate_number) | (models.BarFloor.floor_name == candidate_name),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active floor with this number or name already exists")
    for field, value in updates.items():
        setattr(floor, field, value)
    if "floor_name" in updates:
        floor.floor_name = candidate_name
    floor.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active floor with this number or name already exists")
    return {"status": "success", "message": "Floor updated"}


@router.delete("/floor/{floor_id}", status_code=status.HTTP_200_OK)
def deactivate_floor(floor_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    floor = (
        db.query(models.BarFloor)
        .filter(models.BarFloor.id == floor_id, models.BarFloor.company_id == company_id, models.BarFloor.status == STATUS)
        .with_for_update()
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
    table_name = _validate_table_values(
        table_name=payload.table_name,
        table_number=payload.table_number,
        seating_capacity=payload.seating_capacity,
        table_type=payload.table_type,
        table_status=payload.table_status,
    )
    try:
        floor = (
            db.query(models.BarFloor)
            .filter(models.BarFloor.id == payload.floor_id, models.BarFloor.company_id == company_id, models.BarFloor.status == STATUS)
            .first()
        )
        if not floor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_id does not exist")
        duplicate = db.query(models.BarTable).filter(
            models.BarTable.company_id == company_id,
            models.BarTable.floor_id == payload.floor_id,
            models.BarTable.status == STATUS,
            (models.BarTable.table_number == payload.table_number) | (models.BarTable.table_name == table_name),
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="An active table with this number or name already exists on the floor")
        values = payload.dict()
        values["table_name"] = table_name
        table = models.BarTable(
            table_code=gen_code("BTBL"),
            floor_code=floor.floor_code,
            created_by=user_id,
            company_id=company_id,
            **values,
        )
        db.add(table)
        db.commit()
        db.refresh(table)
        return {"status": "success", "data": {"id": table.id, "table_code": table.table_code}}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active table with this number or name already exists on the floor")
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
    q = db.query(models.BarTable).filter(models.BarTable.company_id == company_id, models.BarTable.status == STATUS)
    if floor_id is not None:
        q = q.filter(models.BarTable.floor_id == floor_id)
    if table_status:
        q = q.filter(models.BarTable.table_status == table_status)
    rows = q.order_by(models.BarTable.table_number.asc()).all()

    # Resolve the two foreign keys the table screen shows to a human. The floor
    # was being joined in the browser (so an unloaded floor list showed the raw
    # id) and the current order was the raw bar_order.id -- a row number no
    # bartender can act on. order_number is the code printed on the BOT.
    floor_ids = {r.floor_id for r in rows if r.floor_id}
    floors = (
        db.query(models.BarFloor)
        .filter(
            models.BarFloor.id.in_(floor_ids),
            models.BarFloor.company_id == company_id,
            models.BarFloor.status == STATUS,
        )
        .all()
        if floor_ids
        else []
    )
    floor_name_by_id = {f.id: f.floor_name for f in floors}

    order_ids = {r.current_order_id for r in rows if r.current_order_id}
    orders = (
        db.query(models.BarOrder)
        .filter(
            models.BarOrder.id.in_(order_ids),
            models.BarOrder.company_id == company_id,
        )
        .all()
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
    table = db.query(models.BarTable).filter(models.BarTable.id == table_id, models.BarTable.company_id == company_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return {"status": "success", "data": table}


@router.put("/table/{table_id}", status_code=status.HTTP_200_OK)
def update_table(table_id: int, payload: TableUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    table = (
        db.query(models.BarTable)
        .filter(models.BarTable.id == table_id, models.BarTable.company_id == company_id, models.BarTable.status == STATUS)
        .with_for_update()
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    updates = payload.dict(exclude_unset=True)
    candidate_name = _validate_table_values(
        table_name=updates.get("table_name", table.table_name),
        table_number=updates.get("table_number", table.table_number),
        seating_capacity=updates.get("seating_capacity", table.seating_capacity),
        table_type=updates.get("table_type", table.table_type),
        table_status=updates.get("table_status", table.table_status),
        server_name=updates.get("server_name", table.server_name),
    )
    candidate_floor = updates.get("floor_id", table.floor_id)
    floor = db.query(models.BarFloor).filter(
        models.BarFloor.id == candidate_floor,
        models.BarFloor.company_id == company_id,
        models.BarFloor.status == STATUS,
    ).first()
    if not floor:
        raise HTTPException(status_code=400, detail="floor_id does not exist")
    duplicate = db.query(models.BarTable).filter(
        models.BarTable.company_id == company_id,
        models.BarTable.floor_id == candidate_floor,
        models.BarTable.status == STATUS,
        models.BarTable.id != table.id,
        (models.BarTable.table_number == updates.get("table_number", table.table_number))
        | (models.BarTable.table_name == candidate_name),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="An active table with this number or name already exists on the floor")
    for field, value in updates.items():
        setattr(table, field, value)
    if "table_name" in updates:
        table.table_name = candidate_name
    if "floor_id" in updates:
        table.floor_code = floor.floor_code
    table.updated_by = user_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active table with this number or name already exists on the floor")
    return {"status": "success", "message": "Table updated"}


@router.delete("/table/{table_id}", status_code=status.HTTP_200_OK)
def deactivate_table(table_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    table = (
        db.query(models.BarTable)
        .filter(models.BarTable.id == table_id, models.BarTable.company_id == company_id, models.BarTable.status == STATUS)
        .with_for_update()
        .first()
    )
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    table.status = UNSTATUS
    table.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Table deactivated"}

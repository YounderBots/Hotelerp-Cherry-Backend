import uuid
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
    try:
        floor = models.BarFloor(
            floor_code=gen_code("BFLR"),
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
        db.query(models.BarFloor)
        .filter(models.BarFloor.company_id == company_id, models.BarFloor.status == STATUS)
        .order_by(models.BarFloor.floor_number.asc())
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/floor/{floor_id}", status_code=status.HTTP_200_OK)
def update_floor(floor_id: int, payload: FloorUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    floor = db.query(models.BarFloor).filter(models.BarFloor.id == floor_id, models.BarFloor.company_id == company_id).first()
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
    floor = db.query(models.BarFloor).filter(models.BarFloor.id == floor_id, models.BarFloor.company_id == company_id).first()
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
        floor = db.query(models.BarFloor).filter(models.BarFloor.id == payload.floor_id, models.BarFloor.company_id == company_id).first()
        if not floor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floor_id does not exist")
        table = models.BarTable(
            table_code=gen_code("BTBL"),
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
        db.query(models.BarFloor).filter(models.BarFloor.id.in_(floor_ids)).all()
        if floor_ids
        else []
    )
    floor_name_by_id = {f.id: f.floor_name for f in floors}

    order_ids = {r.current_order_id for r in rows if r.current_order_id}
    orders = (
        db.query(models.BarOrder).filter(models.BarOrder.id.in_(order_ids)).all()
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
    table = db.query(models.BarTable).filter(models.BarTable.id == table_id, models.BarTable.company_id == company_id).first()
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
    table = db.query(models.BarTable).filter(models.BarTable.id == table_id, models.BarTable.company_id == company_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    table.status = UNSTATUS
    table.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Table deactivated"}

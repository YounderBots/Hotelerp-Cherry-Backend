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


class SettingIn(BaseModel):
    setting_key: str
    setting_value: Optional[str] = None
    setting_group: Optional[str] = None
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    setting_value: Optional[str] = None
    setting_group: Optional[str] = None
    description: Optional[str] = None


@router.post("/settings", status_code=status.HTTP_201_CREATED)
def create_setting(payload: SettingIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    existing = db.query(models.BarSettings).filter(models.BarSettings.setting_key == payload.setting_key, models.BarSettings.company_id == company_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="setting_key already exists; use PUT to update it")
    row = models.BarSettings(created_by=user_id, company_id=company_id, **payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "success", "data": {"id": row.id, "setting_key": row.setting_key}}


@router.get("/settings", status_code=status.HTTP_200_OK)
def list_settings(request: Request, setting_group: Optional[str] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarSettings).filter(models.BarSettings.company_id == company_id, models.BarSettings.status == STATUS)
    if setting_group:
        q = q.filter(models.BarSettings.setting_group == setting_group)
    rows = q.order_by(models.BarSettings.setting_group.asc(), models.BarSettings.setting_key.asc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


@router.put("/settings/{setting_key}", status_code=status.HTTP_200_OK)
def update_setting(setting_key: str, payload: SettingUpdate, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    row = db.query(models.BarSettings).filter(models.BarSettings.setting_key == setting_key, models.BarSettings.company_id == company_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Setting updated"}

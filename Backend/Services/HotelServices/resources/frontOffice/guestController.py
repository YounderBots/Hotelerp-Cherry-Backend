# =============================== Inquiry APIs ==============================

from fastapi import APIRouter, Depends, Request, status, Form
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from jose import jwt, JWTError

from models import get_db, models
from configs.base_config import BaseConfig, CommonWords

router = APIRouter()


# =====================================================
# GET ALL INQUIRIES
# =====================================================
@router.get("/inquiry", status_code=status.HTTP_200_OK)
def get_inquiries(
    request: Request,
    db: Session = Depends(get_db)
):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        if not created_by or not company_id:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        inquiries = db.query(models.Inquiry).filter(
            models.Inquiry.company_id == company_id,
            models.Inquiry.status == CommonWords.STATUS
        ).order_by(models.Inquiry.id.desc()).all()

        return {
            "status": "success",
            "data": inquiries
        }

    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# =====================================================
# CREATE INQUIRY
# =====================================================
@router.post("/inquiry", status_code=status.HTTP_201_CREATED)
def create_inquiry(
    request: Request,
    inquiry_mode: str = Form(...),
    guest_name: Optional[str] = Form(None),
    response: Optional[str] = Form(None),
    followup: Optional[str] = Form(None),
    incidents: Optional[str] = Form(None),
    inquiry_status: str = Form(...),
    db: Session = Depends(get_db)
):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        if not created_by or not company_id:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        new_inquiry = models.Inquiry(
            inquiry_mode=inquiry_mode,
            guest_name=guest_name or "",
            response=response or "",
            followup=followup or "",
            incidents=incidents or "",
            inquiry_status=inquiry_status,
            status=CommonWords.STATUS,
            created_by=created_by,
            updated_by="",
            company_id=company_id
        )

        db.add(new_inquiry)
        db.commit()
        db.refresh(new_inquiry)

        return {
            "status": "success",
            "message": "Inquiry created successfully"
        }

    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# =====================================================
# GET INQUIRY BY ID
# =====================================================
@router.get("/inquiry/{inquiry_id}", status_code=status.HTTP_200_OK)
def get_inquiry_by_id(
    request: Request,
    inquiry_id: int,
    db: Session = Depends(get_db)
):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        company_id = payload.get("company_id")

        inquiry = db.query(models.Inquiry).filter(
            models.Inquiry.id == inquiry_id,
            models.Inquiry.company_id == company_id,
            models.Inquiry.status == CommonWords.STATUS
        ).first()

        if not inquiry:
            return JSONResponse(
                content={"status": "error", "message": "Inquiry not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        return {
            "status": "success",
            "data": inquiry
        }

    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# =====================================================
# UPDATE INQUIRY
# =====================================================
@router.put("/inquiry", status_code=status.HTTP_200_OK)
def update_inquiry(
    request: Request,
    edit_id: int = Form(...),
    edit_inquiry_mode: str = Form(...),
    edit_guest_name: str = Form(...),
    edit_response: Optional[str] = Form(None),
    edit_followup: Optional[str] = Form(None),
    edit_incidents: Optional[str] = Form(None),
    edit_inquiry_status: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        updated = db.query(models.Inquiry).filter(
            models.Inquiry.id == edit_id,
            models.Inquiry.company_id == company_id,
            models.Inquiry.status == CommonWords.STATUS
        ).update({
            "inquiry_mode": edit_inquiry_mode,
            "guest_name": edit_guest_name,
            "response": edit_response or "",
            "followup": edit_followup or "",
            "incidents": edit_incidents or "",
            "inquiry_status": edit_inquiry_status,
            "updated_by": created_by
        })

        if not updated:
            return JSONResponse(
                content={"status": "error", "message": "Inquiry not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        db.commit()

        return {
            "status": "success",
            "message": "Inquiry updated successfully"
        }

    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# =====================================================
# DELETE INQUIRY (SOFT DELETE)
# =====================================================
@router.delete("/inquiry/{inquiry_id}", status_code=status.HTTP_200_OK)
def delete_inquiry(
    request: Request,
    inquiry_id: int,
    db: Session = Depends(get_db)
):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        company_id = payload.get("company_id")

        deleted = db.query(models.Inquiry).filter(
            models.Inquiry.id == inquiry_id,
            models.Inquiry.company_id == company_id
        ).update({
            "status": CommonWords.UNSTATUS
        })

        if not deleted:
            return JSONResponse(
                content={"status": "error", "message": "Inquiry not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        db.commit()

        return {
            "status": "success",
            "message": "Inquiry deleted successfully"
        }

    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

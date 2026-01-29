# =============================== Inquiry APIs ==============================

from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from jose import jwt, JWTError
from resources.utils import verify_authentication
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
# CREATE GUEST INQUIRY
# =====================================================
@router.post("/inquiry", status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (RAW JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        inquiry_mode = payload.get("inquiry_mode", "").strip()
        inquiry_status = payload.get("inquiry_status", "").strip()
        guest_name = payload.get("guest_name", "").strip()
        response = payload.get("response", "").strip()
        followup = payload.get("followup", "").strip()
        incidents = payload.get("incidents", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not inquiry_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inquiry_mode is required"
            )

        if not inquiry_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inquiry_status is required"
            )

        # -------------------------------------------------
        # CREATE INQUIRY
        # -------------------------------------------------
        inquiry = models.Inquiry(
            inquiry_mode=inquiry_mode,
            guest_name=guest_name,
            response=response,
            followup=followup,
            incidents=incidents,
            inquiry_status=inquiry_status,
            status=CommonWords.STATUS,
            created_by=user_id,
            updated_by=None,
            company_id=company_id
        )

        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Guest inquiry created successfully",
            "data": {
                "id": inquiry.id,
                "inquiry_mode": inquiry.inquiry_mode,
                "guest_name": inquiry.guest_name,
                "inquiry_status": inquiry.inquiry_status,
                "company_id": inquiry.company_id,
                "created_by": inquiry.created_by,
                "created_at": inquiry.created_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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

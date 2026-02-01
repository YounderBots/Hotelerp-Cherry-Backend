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
        # FETCH INQUIRIES
        # -------------------------------------------------
        inquiries = (
            db.query(models.Inquiry)
            .filter(
                models.Inquiry.company_id == company_id,
                models.Inquiry.status == CommonWords.STATUS
            )
            .order_by(models.Inquiry.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE DATA
        # -------------------------------------------------
        data = [
            {
                "id": inquiry.id,
                "inquiry_mode": inquiry.inquiry_mode,
                "guest_name": inquiry.guest_name,
                "response": inquiry.response,
                "follow_up": inquiry.follow_up,
                "incidents": inquiry.incidents,
                "inquiry_status": inquiry.inquiry_status,
                "created_by": inquiry.created_by,
                "created_at": inquiry.created_at,
                "updated_at": inquiry.updated_at,
                "company_id": inquiry.company_id
            }
            for inquiry in inquiries
        ]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }

    except HTTPException:
        # ✅ Expected errors
        raise

    except Exception as e:
        # ❌ Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        inquiry_mode = payload.get("inquiry_mode", "").strip()
        guest_name = payload.get("guest_name", "").strip()
        inquiry_status = payload.get("inquiry_status", "").strip()

        response = payload.get("response", "").strip() or None
        follow_up = payload.get("follow_up", "").strip() or None
        incidents = payload.get("incidents", "").strip() or None

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not inquiry_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inquiry_mode is required"
            )

        if not guest_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="guest_name is required"
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
            follow_up=follow_up,
            incidents=incidents,
            inquiry_status=inquiry_status,
            status=CommonWords.STATUS,
            created_by=user_id,
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
        # VALIDATION
        # -------------------------------------------------
        if inquiry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid inquiry_id"
            )

        # -------------------------------------------------
        # FETCH INQUIRY
        # -------------------------------------------------
        inquiry = (
            db.query(models.Inquiry)
            .filter(
                models.Inquiry.id == inquiry_id,
                models.Inquiry.company_id == company_id,
                models.Inquiry.status == CommonWords.STATUS
            )
            .first()
        )

        if not inquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inquiry not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": inquiry.id,
                "inquiry_mode": inquiry.inquiry_mode,
                "guest_name": inquiry.guest_name,
                "response": inquiry.response,
                "follow_up": inquiry.follow_up,
                "incidents": inquiry.incidents,
                "inquiry_status": inquiry.inquiry_status,
                "created_by": inquiry.created_by,
                "created_at": inquiry.created_at,
                "updated_at": inquiry.updated_at,
                "company_id": inquiry.company_id
            }
        }

    except HTTPException:
        # ✅ Expected errors
        raise

    except Exception as e:
        # ❌ Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE INQUIRY
# =====================================================
@router.put("/inquiry", status_code=status.HTTP_200_OK)
async def update_inquiry(
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
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        inquiry_id = payload.get("id")
        inquiry_mode = payload.get("inquiry_mode", "").strip()
        guest_name = payload.get("guest_name", "").strip()
        inquiry_status = payload.get("inquiry_status", "").strip()

        response = payload.get("response", "").strip() or None
        follow_up = payload.get("follow_up", "").strip() or None
        incidents = payload.get("incidents", "").strip() or None

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not inquiry_id or not isinstance(inquiry_id, int) or inquiry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid inquiry id is required"
            )

        if not inquiry_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inquiry_mode is required"
            )

        if not guest_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="guest_name is required"
            )

        if not inquiry_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inquiry_status is required"
            )

        # -------------------------------------------------
        # FETCH INQUIRY
        # -------------------------------------------------
        inquiry = (
            db.query(models.Inquiry)
            .filter(
                models.Inquiry.id == inquiry_id,
                models.Inquiry.company_id == company_id,
                models.Inquiry.status == CommonWords.STATUS
            )
            .first()
        )

        if not inquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inquiry not found"
            )

        # -------------------------------------------------
        # UPDATE INQUIRY
        # -------------------------------------------------
        inquiry.inquiry_mode = inquiry_mode
        inquiry.guest_name = guest_name
        inquiry.response = response
        inquiry.follow_up = follow_up
        inquiry.incidents = incidents
        inquiry.inquiry_status = inquiry_status
        inquiry.updated_by = user_id

        db.commit()
        db.refresh(inquiry)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Inquiry updated successfully",
            "data": {
                "id": inquiry.id,
                "inquiry_mode": inquiry.inquiry_mode,
                "guest_name": inquiry.guest_name,
                "inquiry_status": inquiry.inquiry_status,
                "updated_at": inquiry.updated_at
            }
        }

    except HTTPException:
        # ✅ Expected errors
        raise

    except Exception as e:
        # ❌ Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE INQUIRY (SOFT DELETE)
# =====================================================
@router.delete("/inquiry/{inquiry_id}", status_code=status.HTTP_200_OK)
def delete_inquiry(
    request: Request,
    inquiry_id: int,
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
        # VALIDATION
        # -------------------------------------------------
        if inquiry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid inquiry_id"
            )

        # -------------------------------------------------
        # FETCH INQUIRY
        # -------------------------------------------------
        inquiry = (
            db.query(models.Inquiry)
            .filter(
                models.Inquiry.id == inquiry_id,
                models.Inquiry.company_id == company_id,
                models.Inquiry.status == CommonWords.STATUS
            )
            .first()
        )

        if not inquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inquiry not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        inquiry.status = CommonWords.UNSTATUS
        inquiry.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Inquiry deleted successfully"
        }

    except HTTPException:
        # ✅ Expected errors
        raise

    except Exception as e:
        # ❌ Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
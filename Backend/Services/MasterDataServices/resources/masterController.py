from enum import verify
from fastapi import APIRouter, Depends, Form, status, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from httpx import request
from sqlalchemy.orm import Session 
from sqlalchemy import func
from typing import Optional
import os
import uuid
import shutil

from resources.utils import verify_authentication
from models import models
from models import get_db
from configs.base_config import CommonWords

UPLOAD_PATH = "./templates/static/upload_image"
os.makedirs(UPLOAD_PATH, exist_ok=True)

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from fastapi import Header

from models import models, get_db
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from models import models, get_db
from configs.base_config import CommonWords
from resources.utils import verify_authentication

router = APIRouter()

# =====================================================
# GET ALL FACILITIES
# =====================================================
@router.get("/facilities", status_code=status.HTTP_200_OK)
def get_facilities(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # SAFETY CHECK (AUTH SHOULD GUARANTEE THIS)
        # -------------------------------------------------
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH FACILITIES
        # -------------------------------------------------
        facilities = (
            db.query(models.Facility)
            .filter(
                models.Facility.company_id == company_id,
                models.Facility.status == CommonWords.STATUS
            )
            .order_by(models.Facility.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE DATA
        # -------------------------------------------------
        data = [
            {
                "id": facility.id,
                "facility_name": facility.Facility_Name,
                "company_id": facility.company_id,
                "created_by": facility.created_by,
                "created_at": facility.created_at,
                "updated_at": facility.updated_at,
            }
            for facility in facilities
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
        # ✅ Keep expected HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE FACILITY
# =====================================================
@router.post("/facilities", status_code=status.HTTP_201_CREATED)
async def create_facility(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

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

        facility_name = payload.get("facility_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not facility_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="facility_name is required"
            )

        if len(facility_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="facility_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Facility)
            .filter(
                func.lower(models.Facility.Facility_Name) == facility_name.lower(),
                models.Facility.company_id == company_id,
                models.Facility.status == CommonWords.STATUS,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Facility already exists"
            )

        # -------------------------------------------------
        # CREATE FACILITY
        # -------------------------------------------------
        facility = models.Facility(
            Facility_Name=facility_name,
            company_id=company_id,
            created_by=user_id,
            status=CommonWords.STATUS,
        )

        db.add(facility)
        db.commit()
        db.refresh(facility)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Facility created successfully",
            "data": {
                "id": facility.id,
                "facility_name": facility.Facility_Name,
                "company_id": facility.company_id,
                "created_by": facility.created_by,
                "created_at": facility.created_at,
            },
        }

    except HTTPException:
        # Keep intended HTTP errors
        raise

    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
# =====================================================
# GET FACILITY BY ID
# =====================================================
@router.get("/facilities/{facility_id}", status_code=status.HTTP_200_OK)
def get_facility_by_id(
    request: Request,
    facility_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if facility_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid facility_id"
            )

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH FACILITY
        # -------------------------------------------------
        facility = (
            db.query(models.Facility)
            .filter(
                models.Facility.id == facility_id,
                models.Facility.company_id == company_id,
                models.Facility.status == CommonWords.STATUS,
            )
            .first()
        )

        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": facility.id,
                "facility_name": facility.Facility_Name,
                "company_id": facility.company_id,
                "created_by": facility.created_by,
                "created_at": facility.created_at,
                "updated_at": facility.updated_at,
            }
        }

    except HTTPException:
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# UPDATE FACILITY
# =====================================================
@router.put("/facilities", status_code=status.HTTP_200_OK)
async def update_facility(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        facility_id = payload.get("id")
        facility_name = payload.get("facility_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not facility_id or not isinstance(facility_id, int) or facility_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid facility id is required"
            )

        if not facility_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="facility_name is required"
            )

        if len(facility_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="facility_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE NAME CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Facility)
            .filter(
                models.Facility.id != facility_id,
                func.lower(models.Facility.Facility_Name) == facility_name.lower(),
                models.Facility.company_id == company_id,
                models.Facility.status == CommonWords.STATUS,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Facility name already exists"
            )

        # -------------------------------------------------
        # FETCH FACILITY
        # -------------------------------------------------
        facility = (
            db.query(models.Facility)
            .filter(
                models.Facility.id == facility_id,
                models.Facility.company_id == company_id,
                models.Facility.status == CommonWords.STATUS,
            )
            .first()
        )

        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )

        # -------------------------------------------------
        # UPDATE FACILITY
        # -------------------------------------------------
        facility.Facility_Name = facility_name
        facility.updated_by = user_id if hasattr(facility, "updated_by") else None

        db.commit()
        db.refresh(facility)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Facility updated successfully",
            "data": {
                "id": facility.id,
                "facility_name": facility.Facility_Name,
                "company_id": facility.company_id,
                "updated_at": facility.updated_at,
            },
        }

    except HTTPException:
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# =====================================================
# DELETE FACILITY (SOFT DELETE)
# =====================================================
@router.delete("/facilities/{facility_id}", status_code=status.HTTP_200_OK)
def delete_facility(
    request: Request,
    facility_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if facility_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid facility_id"
            )

        # -------------------------------------------------
        # FETCH FACILITY
        # -------------------------------------------------
        facility = (
            db.query(models.Facility)
            .filter(
                models.Facility.id == facility_id,
                models.Facility.company_id == company_id,
                models.Facility.status == CommonWords.STATUS,
            )
            .first()
        )

        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        facility.status = CommonWords.UNSTATUS
        facility.updated_by = user_id if hasattr(facility, "updated_by") else None

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Facility deleted successfully"
        }

    except HTTPException:
        # ✅ Keep expected HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL ROOM TYPES
# =====================================================
@router.get("/room_types", status_code=status.HTTP_200_OK)
def get_room_types(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH ROOM TYPES
        # -------------------------------------------------
        room_types = (
            db.query(models.Room_Type)
            .filter(
                models.Room_Type.company_id == company_id,
                models.Room_Type.status == CommonWords.STATUS
            )
            .order_by(models.Room_Type.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": room_type.id,
                "room_type_name": room_type.Type_Name,
                "company_id": room_type.company_id,
                "created_by": room_type.created_by,
                "created_at": room_type.created_at,
                "updated_at": room_type.updated_at,
            }
            for room_type in room_types
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
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# CREATE ROOM TYPE
# =====================================================
@router.post("/room_types", status_code=status.HTTP_201_CREATED)
async def create_room_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        type_name = payload.get("type_name", "").strip()
        room_cost = payload.get("room_cost")
        bed_cost = payload.get("bed_cost")
        complementry = payload.get("complementry")

        daily_rate = payload.get("daily_rate")
        weekly_rate = payload.get("weekly_rate")
        bed_only_rate = payload.get("bed_only_rate")
        bed_breakfast_rate = payload.get("bed_breakfast_rate")
        half_board_rate = payload.get("half_board_rate")
        full_board_rate = payload.get("full_board_rate")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not type_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="type_name is required"
            )

        if len(type_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="type_name must not exceed 100 characters"
            )

        if room_cost is None or bed_cost is None or complementry is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_cost, bed_cost and complementry are required"
            )

        if room_cost < 0 or bed_cost < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_cost and bed_cost must be non-negative"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Room_Type)
            .filter(
                func.lower(models.Room_Type.Type_Name) == type_name.lower(),
                models.Room_Type.company_id == company_id,
                models.Room_Type.status == CommonWords.STATUS,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room type already exists"
            )

        # -------------------------------------------------
        # CREATE ROOM TYPE
        # -------------------------------------------------
        room_type = models.Room_Type(
            Type_Name=type_name,
            Room_Cost=room_cost,
            Bed_Cost=bed_cost,
            Complementry=complementry,
            Daily_Rate=daily_rate,
            Weekly_Rate=weekly_rate,
            Bed_Only_Rate=bed_only_rate,
            Bed_And_Breakfast_Rate=bed_breakfast_rate,
            Half_Board_Rate=half_board_rate,
            Full_Board_Rate=full_board_rate,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(room_type)
        db.commit()
        db.refresh(room_type)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room type created successfully",
            "data": {
                "id": room_type.id,
                "type_name": room_type.Type_Name,
                "room_cost": room_type.Room_Cost,
                "bed_cost": room_type.Bed_Cost,
                "complementry": room_type.Complementry,
                "company_id": room_type.company_id,
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
# GET ROOM TYPE BY ID
# =====================================================
@router.get("/room_types/{room_type_id}", status_code=status.HTTP_200_OK)
def get_room_type_by_id(
    request: Request,
    room_type_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if room_type_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid room_type_id"
            )

        # -------------------------------------------------
        # FETCH ROOM TYPE
        # -------------------------------------------------
        room_type = (
            db.query(models.Room_Type)
            .filter(
                models.Room_Type.id == room_type_id,
                models.Room_Type.company_id == company_id,
                models.Room_Type.status == CommonWords.STATUS,
            )
            .first()
        )

        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": room_type.id,
                "type_name": room_type.Type_Name,
                "room_cost": room_type.Room_Cost,
                "bed_cost": room_type.Bed_Cost,
                "complementry": room_type.Complementry,
                "daily_rate": room_type.Daily_Rate,
                "weekly_rate": room_type.Weekly_Rate,
                "bed_only_rate": room_type.Bed_Only_Rate,
                "bed_breakfast_rate": room_type.Bed_And_Breakfast_Rate,
                "half_board_rate": room_type.Half_Board_Rate,
                "full_board_rate": room_type.Full_Board_Rate,
                "company_id": room_type.company_id,
                "created_by": room_type.created_by,
                "created_at": room_type.created_at,
                "updated_at": room_type.updated_at,
            }
        }

    except HTTPException:
        # ✅ Keep correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE ROOM TYPE
# =====================================================
@router.put("/room_types", status_code=status.HTTP_200_OK)
async def update_room_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        room_type_id = payload.get("id")
        type_name = payload.get("type_name", "").strip()
        room_cost = payload.get("room_cost")
        bed_cost = payload.get("bed_cost")
        complementry = payload.get("complementry")

        daily_rate = payload.get("daily_rate")
        weekly_rate = payload.get("weekly_rate")
        bed_only_rate = payload.get("bed_only_rate")
        bed_breakfast_rate = payload.get("bed_breakfast_rate")
        half_board_rate = payload.get("half_board_rate")
        full_board_rate = payload.get("full_board_rate")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not room_type_id or not isinstance(room_type_id, int) or room_type_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid room type id is required"
            )

        if not type_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="type_name is required"
            )

        if len(type_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="type_name must not exceed 100 characters"
            )

        if room_cost is None or bed_cost is None or complementry is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_cost, bed_cost and complementry are required"
            )

        if room_cost < 0 or bed_cost < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_cost and bed_cost must be non-negative"
            )

        # -------------------------------------------------
        # DUPLICATE NAME CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Room_Type)
            .filter(
                models.Room_Type.id != room_type_id,
                func.lower(models.Room_Type.Type_Name) == type_name.lower(),
                models.Room_Type.company_id == company_id,
                models.Room_Type.status == CommonWords.STATUS,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room type name already exists"
            )

        # -------------------------------------------------
        # FETCH ROOM TYPE
        # -------------------------------------------------
        room_type = (
            db.query(models.Room_Type)
            .filter(
                models.Room_Type.id == room_type_id,
                models.Room_Type.company_id == company_id,
                models.Room_Type.status == CommonWords.STATUS,
            )
            .first()
        )

        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found"
            )

        # -------------------------------------------------
        # UPDATE ROOM TYPE
        # -------------------------------------------------
        room_type.Type_Name = type_name
        room_type.Room_Cost = room_cost
        room_type.Bed_Cost = bed_cost
        room_type.Complementry = complementry
        room_type.Daily_Rate = daily_rate
        room_type.Weekly_Rate = weekly_rate
        room_type.Bed_Only_Rate = bed_only_rate
        room_type.Bed_And_Breakfast_Rate = bed_breakfast_rate
        room_type.Half_Board_Rate = half_board_rate
        room_type.Full_Board_Rate = full_board_rate
        room_type.updated_by = user_id if hasattr(room_type, "updated_by") else None

        db.commit()
        db.refresh(room_type)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room type updated successfully",
            "data": {
                "id": room_type.id,
                "type_name": room_type.Type_Name,
                "room_cost": room_type.Room_Cost,
                "bed_cost": room_type.Bed_Cost,
                "complementry": room_type.Complementry,
                "company_id": room_type.company_id,
                "updated_at": room_type.updated_at,
            }
        }

    except HTTPException:
        # ✅ Preserve intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE ROOM TYPE (SOFT DELETE)
# =====================================================
@router.delete("/room_types/{room_type_id}", status_code=status.HTTP_200_OK)
def delete_room_type(
    request: Request,
    room_type_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if room_type_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid room_type_id"
            )

        # -------------------------------------------------
        # FETCH ROOM TYPE
        # -------------------------------------------------
        room_type = (
            db.query(models.Room_Type)
            .filter(
                models.Room_Type.id == room_type_id,
                models.Room_Type.company_id == company_id,
                models.Room_Type.status == CommonWords.STATUS,
            )
            .first()
        )

        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        room_type.status = CommonWords.UNSTATUS
        room_type.updated_by = user_id if hasattr(room_type, "updated_by") else None

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room type deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL BED TYPES
# =====================================================
@router.get("/bed_types", status_code=status.HTTP_200_OK)
def get_bed_types(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH BED TYPES
        # -------------------------------------------------
        bed_types = (
            db.query(models.Bed_Type)
            .filter(
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .order_by(models.Bed_Type.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": bed.id,
                "bed_type_name": bed.Type_Name,
                "company_id": bed.company_id,
                "created_by": bed.created_by,
                "created_at": bed.created_at,
                "updated_at": bed.updated_at,
            }
            for bed in bed_types
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
        # ✅ Keep correct HTTP errors
        raise

    except Exception as e:
        # ❌ Only unexpected errors become 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE BED TYPE
# =====================================================
@router.post("/bed_type", status_code=status.HTTP_201_CREATED)
async def create_bed_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        bed_type_name = payload.get("bed_type", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not bed_type_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bed_type is required"
            )

        if len(bed_type_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bed_type must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Bed_Type)
            .filter(
                func.lower(models.Bed_Type.Type_Name) == bed_type_name.lower(),
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bed type already exists"
            )

        # -------------------------------------------------
        # CREATE BED TYPE
        # -------------------------------------------------
        bed_type = models.Bed_Type(
            Type_Name=bed_type_name,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(bed_type)
        db.commit()
        db.refresh(bed_type)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Bed type created successfully",
            "data": {
                "id": bed_type.id,
                "bed_type": bed_type.Type_Name,
                "company_id": bed_type.company_id,
                "created_by": bed_type.created_by,
                "created_at": bed_type.created_at,
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
# GET BED TYPE BY ID
# =====================================================
@router.get("/bed_type/{bed_type_id}", status_code=status.HTTP_200_OK)
def get_bed_type_by_id(
    request: Request,
    bed_type_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if bed_type_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bed_type_id"
            )

        # -------------------------------------------------
        # FETCH BED TYPE
        # -------------------------------------------------
        bed_type = (
            db.query(models.Bed_Type)
            .filter(
                models.Bed_Type.id == bed_type_id,
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .first()
        )

        if not bed_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed type not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": bed_type.id,
                "bed_type": bed_type.Type_Name,
                "company_id": bed_type.company_id,
                "created_by": bed_type.created_by,
                "created_at": bed_type.created_at,
                "updated_at": bed_type.updated_at
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
# UPDATE BED TYPE
# =====================================================
@router.put("/bed_type", status_code=status.HTTP_200_OK)
async def update_bed_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        bed_type_id = payload.get("id")
        bed_type_name = payload.get("bed_type", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not bed_type_id or not isinstance(bed_type_id, int) or bed_type_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid bed type id is required"
            )

        if not bed_type_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bed_type is required"
            )

        if len(bed_type_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bed_type must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Bed_Type)
            .filter(
                models.Bed_Type.id != bed_type_id,
                func.lower(models.Bed_Type.Type_Name) == bed_type_name.lower(),
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bed type name already exists"
            )

        # -------------------------------------------------
        # FETCH BED TYPE
        # -------------------------------------------------
        bed_type = (
            db.query(models.Bed_Type)
            .filter(
                models.Bed_Type.id == bed_type_id,
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .first()
        )

        if not bed_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed type not found"
            )

        # -------------------------------------------------
        # UPDATE BED TYPE
        # -------------------------------------------------
        bed_type.Type_Name = bed_type_name
        bed_type.updated_by = user_id if hasattr(bed_type, "updated_by") else None

        db.commit()
        db.refresh(bed_type)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Bed type updated successfully",
            "data": {
                "id": bed_type.id,
                "bed_type": bed_type.Type_Name,
                "company_id": bed_type.company_id,
                "updated_at": bed_type.updated_at
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
# DELETE BED TYPE (SOFT DELETE)
# =====================================================
@router.delete("/bed_type/{bed_type_id}", status_code=status.HTTP_200_OK)
def delete_bed_type(
    request: Request,
    bed_type_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if bed_type_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bed_type_id"
            )

        # -------------------------------------------------
        # FETCH BED TYPE
        # -------------------------------------------------
        bed_type = (
            db.query(models.Bed_Type)
            .filter(
                models.Bed_Type.id == bed_type_id,
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .first()
        )

        if not bed_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed type not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        bed_type.status = CommonWords.UNSTATUS
        bed_type.updated_by = user_id if hasattr(bed_type, "updated_by") else None

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Bed type deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL HALL / FLOOR
# =====================================================
@router.get("/hall_floor", status_code=status.HTTP_200_OK)
def get_hall_floors(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH HALL / FLOOR DATA
        # -------------------------------------------------
        halls = (
            db.query(models.TableHallNames)
            .filter(
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .order_by(models.TableHallNames.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": hall.id,
                "hall_name": hall.hall_name,
                "company_id": hall.company_id,
                "created_by": hall.created_by,
                "created_at": hall.created_at,
                "updated_at": hall.updated_at
            }
            for hall in halls
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
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE HALL / FLOOR
# =====================================================
@router.post("/hall_floor", status_code=status.HTTP_201_CREATED)
async def create_hall_floor(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        hall_name = payload.get("hall_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not hall_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hall_name is required"
            )

        if len(hall_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hall_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.TableHallNames)
            .filter(
                func.lower(models.TableHallNames.hall_name) == hall_name.lower(),
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hall / Floor already exists"
            )

        # -------------------------------------------------
        # CREATE HALL / FLOOR
        # -------------------------------------------------
        hall = models.TableHallNames(
            hall_name=hall_name,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(hall)
        db.commit()
        db.refresh(hall)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Hall / Floor created successfully",
            "data": {
                "id": hall.id,
                "hall_name": hall.hall_name,
                "company_id": hall.company_id,
                "created_by": hall.created_by,
                "created_at": hall.created_at
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
# GET HALL / FLOOR BY ID
# =====================================================
@router.get("/hall_floor/{hall_id}", status_code=status.HTTP_200_OK)
def get_hall_floor_by_id(
    request: Request,
    hall_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if hall_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid hall_id"
            )

        # -------------------------------------------------
        # FETCH HALL / FLOOR
        # -------------------------------------------------
        hall = (
            db.query(models.TableHallNames)
            .filter(
                models.TableHallNames.id == hall_id,
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .first()
        )

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall / Floor not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": hall.id,
                "hall_name": hall.hall_name,
                "company_id": hall.company_id,
                "created_by": hall.created_by,
                "created_at": hall.created_at,
                "updated_at": hall.updated_at
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
# UPDATE HALL / FLOOR
# =====================================================
@router.put("/hall_floor", status_code=status.HTTP_200_OK)
async def update_hall_floor(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
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

        hall_id = payload.get("id")
        hall_name = payload.get("hall_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not hall_id or not isinstance(hall_id, int) or hall_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid hall id is required"
            )

        if not hall_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hall_name is required"
            )

        if len(hall_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hall_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE NAME CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.TableHallNames)
            .filter(
                models.TableHallNames.id != hall_id,
                func.lower(models.TableHallNames.hall_name) == hall_name.lower(),
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hall / Floor name already exists"
            )

        # -------------------------------------------------
        # FETCH HALL / FLOOR
        # -------------------------------------------------
        hall = (
            db.query(models.TableHallNames)
            .filter(
                models.TableHallNames.id == hall_id,
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .first()
        )

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall / Floor not found"
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------
        hall.hall_name = hall_name
        hall.updated_by = user_id if hasattr(hall, "updated_by") else None

        db.commit()
        db.refresh(hall)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Hall / Floor updated successfully",
            "data": {
                "id": hall.id,
                "hall_name": hall.hall_name,
                "company_id": hall.company_id,
                "updated_at": hall.updated_at
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
# DELETE HALL / FLOOR (SOFT DELETE)
# =====================================================
@router.delete("/hall_floor/{hall_id}", status_code=status.HTTP_200_OK)
def delete_hall_floor(
    request: Request,
    hall_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if hall_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid hall_id"
            )

        # -------------------------------------------------
        # FETCH HALL / FLOOR
        # -------------------------------------------------
        hall = (
            db.query(models.TableHallNames)
            .filter(
                models.TableHallNames.id == hall_id,
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .first()
        )

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall / Floor not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        hall.status = CommonWords.UNSTATUS
        hall.updated_by = user_id if hasattr(hall, "updated_by") else None

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Hall / Floor deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL ROOMS
# =====================================================
@router.get("/room", status_code=status.HTTP_200_OK)
def get_rooms(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH ROOMS
        # -------------------------------------------------
        rooms = (
            db.query(models.Room)
            .filter(
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .order_by(models.Room.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE (NO RAW ORM)
        # -------------------------------------------------
        data = [
            {
                "id": room.id,
                "room_no": room.Room_No,
                "room_name": room.Room_Name,
                "room_type_id": room.Room_Type_ID,
                "bed_type_id": room.Bed_Type_ID,
                "room_telephone": room.Room_Telephone,
                "max_adult": room.Max_Adult_Occupy,
                "max_child": room.Max_Child_Occupy,
                "booking_status": room.Room_Booking_status,
                "working_status": room.Room_Working_status,
                "room_status": room.Room_Status,
                "images": {
                    "image_1": room.Room_Image_1,
                    "image_2": room.Room_Image_2,
                    "image_3": room.Room_Image_3,
                    "image_4": room.Room_Image_4,
                },
                "company_id": room.company_id,
                "created_by": room.created_by,
                "created_at": room.created_at,
                "updated_at": room.updated_at,
            }
            for room in rooms
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
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE ROOM
# =====================================================
@router.post("/room", status_code=status.HTTP_201_CREATED)
async def create_room(
    request: Request,

    # -------- FORM FIELDS --------
    room_no: str = Form(...),
    room_name: str = Form(...),
    room_type_id: int = Form(...),
    bed_type_id: int = Form(...),
    tele_no: str = Form(None),
    max_adult: int = Form(...),
    max_child: int = Form(...),

    # -------- IMAGES (OPTIONAL) --------
    image_1: UploadFile = File(None),
    image_2: UploadFile = File(None),
    image_3: UploadFile = File(None),
    image_4: UploadFile = File(None),

    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION (JWT ONLY)
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not room_no or not room_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_no and room_name are required"
            )

        if max_adult < 0 or max_child < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_adult and max_child must be non-negative"
            )

        # -------------------------------------------------
        # DUPLICATE ROOM CHECK
        # -------------------------------------------------
        exists = (
            db.query(models.Room)
            .filter(
                models.Room.Room_No == room_no,
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

        # -------------------------------------------------
        # IMAGE SAVE HELPER
        # -------------------------------------------------
        def save_image(file: UploadFile | None):
            if not file:
                return None
            ext = file.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            filepath = os.path.join(UPLOAD_PATH, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return filename

        img1 = save_image(image_1)
        img2 = save_image(image_2)
        img3 = save_image(image_3)
        img4 = save_image(image_4)

        # -------------------------------------------------
        # CREATE ROOM
        # -------------------------------------------------
        room = models.Room(
            Room_No=room_no,
            Room_Name=room_name,
            Room_Type_ID=room_type_id,
            Bed_Type_ID=bed_type_id,
            Room_Telephone=tele_no,
            Max_Adult_Occupy=max_adult,
            Max_Child_Occupy=max_child,

            Room_Booking_status=CommonWords.AVAILABLE,
            Room_Working_status=CommonWords.WORK_STATUS,
            Room_Status=CommonWords.Room_Condition,

            Room_Image_1=img1,
            Room_Image_2=img2,
            Room_Image_3=img3,
            Room_Image_4=img4,

            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(room)
        db.commit()
        db.refresh(room)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room created successfully",
            "data": {
                "id": room.id,
                "room_no": room.Room_No,
                "room_name": room.Room_Name,
                "room_type_id": room.Room_Type_ID,
                "bed_type_id": room.Bed_Type_ID,
                "company_id": room.company_id,
                "created_at": room.created_at
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
# GET ROOM BY ID
# =====================================================
@router.get("/room/{room_id}", status_code=status.HTTP_200_OK)
def get_room_by_id(
    request: Request,
    room_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if room_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid room_id"
            )

        # -------------------------------------------------
        # FETCH ROOM
        # -------------------------------------------------
        room = (
            db.query(models.Room)
            .filter(
                models.Room.id == room_id,
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .first()
        )

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": room.id,
                "room_no": room.Room_No,
                "room_name": room.Room_Name,
                "room_type_id": room.Room_Type_ID,
                "bed_type_id": room.Bed_Type_ID,
                "room_telephone": room.Room_Telephone,
                "max_adult": room.Max_Adult_Occupy,
                "max_child": room.Max_Child_Occupy,
                "booking_status": room.Room_Booking_status,
                "working_status": room.Room_Working_status,
                "room_status": room.Room_Status,
                "images": {
                    "image_1": room.Room_Image_1,
                    "image_2": room.Room_Image_2,
                    "image_3": room.Room_Image_3,
                    "image_4": room.Room_Image_4,
                },
                "company_id": room.company_id,
                "created_by": room.created_by,
                "created_at": room.created_at,
                "updated_at": room.updated_at,
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
# UPDATE ROOM
# =====================================================
@router.put("/room", status_code=status.HTTP_200_OK)
async def update_room(
    request: Request,

    # -------- FORM FIELDS --------
    room_id: int = Form(...),
    room_no: str = Form(...),
    room_name: str = Form(...),
    room_type_id: int = Form(...),
    bed_type_id: int = Form(...),
    tele_no: str = Form(None),
    max_adult: int = Form(...),
    max_child: int = Form(...),
    room_condition: str = Form(...),

    # -------- OPTIONAL IMAGES --------
    image_1: Optional[UploadFile] = File(None),
    image_2: Optional[UploadFile] = File(None),
    image_3: Optional[UploadFile] = File(None),
    image_4: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if room_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid room_id"
            )

        if max_adult < 0 or max_child < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_adult and max_child must be non-negative"
            )

        # -------------------------------------------------
        # DUPLICATE ROOM NO CHECK
        # -------------------------------------------------
        duplicate = (
            db.query(models.Room)
            .filter(
                models.Room.id != room_id,
                models.Room.Room_No == room_no,
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

        # -------------------------------------------------
        # FETCH ROOM
        # -------------------------------------------------
        room = (
            db.query(models.Room)
            .filter(
                models.Room.id == room_id,
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .first()
        )

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        # -------------------------------------------------
        # IMAGE SAVE / REPLACE HELPER
        # -------------------------------------------------
        def save_or_replace_image(file: UploadFile, old_name: str | None):
            ext = file.filename.split(".")[-1]
            filename = (
                f"{uuid.uuid4()}.{ext}"
                if not old_name
                else f"{old_name.split('.')[0]}.{ext}"
            )
            filepath = os.path.join(UPLOAD_PATH, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return filename

        if image_1:
            room.Room_Image_1 = save_or_replace_image(image_1, room.Room_Image_1)
        if image_2:
            room.Room_Image_2 = save_or_replace_image(image_2, room.Room_Image_2)
        if image_3:
            room.Room_Image_3 = save_or_replace_image(image_3, room.Room_Image_3)
        if image_4:
            room.Room_Image_4 = save_or_replace_image(image_4, room.Room_Image_4)

        # -------------------------------------------------
        # UPDATE ROOM DATA
        # -------------------------------------------------
        room.Room_No = room_no
        room.Room_Name = room_name
        room.Room_Type_ID = room_type_id
        room.Bed_Type_ID = bed_type_id
        room.Room_Telephone = tele_no
        room.Max_Adult_Occupy = max_adult
        room.Max_Child_Occupy = max_child
        room.Room_Status = room_condition
        room.updated_by = user_id

        db.commit()
        db.refresh(room)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room updated successfully",
            "data": {
                "id": room.id,
                "room_no": room.Room_No,
                "room_name": room.Room_Name,
                "room_type_id": room.Room_Type_ID,
                "bed_type_id": room.Bed_Type_ID,
                "room_status": room.Room_Status,
                "updated_at": room.updated_at
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
# DELETE ROOM (SOFT DELETE)
# =====================================================
@router.delete("/room/{room_id}", status_code=status.HTTP_200_OK)
def delete_room(
    request: Request,
    room_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if room_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid room_id"
            )

        # -------------------------------------------------
        # FETCH ROOM
        # -------------------------------------------------
        room = (
            db.query(models.Room)
            .filter(
                models.Room.id == room_id,
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .first()
        )

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        room.status = CommonWords.UNSTATUS
        room.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL DISCOUNTS
# =====================================================
@router.get("/discount", status_code=status.HTTP_200_OK)
def get_discounts(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH DISCOUNTS
        # -------------------------------------------------
        discounts = (
            db.query(models.Discount_Data)
            .filter(
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .order_by(models.Discount_Data.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE (MODEL SAFE)
        # -------------------------------------------------
        data = [
            {
                "id": discount.id,
                "country_id": discount.Country_ID,
                "discount_name": discount.Discount_Name,
                "discount_percentage": discount.Discount_Percentage,
                "company_id": discount.company_id,
                "created_by": discount.created_by,
                "created_at": discount.created_at,
                "updated_at": discount.updated_at
            }
            for discount in discounts
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
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE DISCOUNT
# =====================================================
@router.post("/discount", status_code=status.HTTP_201_CREATED)
async def create_discount(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY
        # -------------------------------------------------
        payload = await request.json()

        country_id = payload.get("country_id")
        discount_name = payload.get("discount_name")
        discount_percentage = payload.get("discount_percentage")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not country_id or not discount_name or discount_percentage is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_id, discount_name and discount_percentage are required"
            )

        try:
            discount_percentage = float(discount_percentage)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_percentage must be a number"
            )

        if not (0 < discount_percentage <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_percentage must be between 1 and 100"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        exists = (
            db.query(models.Discount_Data)
            .filter(
                func.lower(models.Discount_Data.Country_ID) == country_id.lower(),
                func.lower(models.Discount_Data.Discount_Name) == discount_name.lower(),
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Discount already exists for this country"
            )

        # -------------------------------------------------
        # CREATE DISCOUNT
        # -------------------------------------------------
        discount = models.Discount_Data(
            Country_ID=country_id,
            Discount_Name=discount_name,
            Discount_Percentage=str(discount_percentage),
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(discount)
        db.commit()
        db.refresh(discount)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Discount created successfully",
            "data": {
                "id": discount.id,
                "country_id": discount.Country_ID,
                "discount_name": discount.Discount_Name,
                "discount_percentage": discount.Discount_Percentage,
                "company_id": discount.company_id,
                "created_by": discount.created_by,
                "created_at": discount.created_at
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
# GET DISCOUNT BY ID
# =====================================================
@router.get("/discount/{discount_id}", status_code=status.HTTP_200_OK)
def get_discount_by_id(
    request: Request,
    discount_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if discount_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid discount_id"
            )

        # -------------------------------------------------
        # FETCH DISCOUNT
        # -------------------------------------------------
        discount = (
            db.query(models.Discount_Data)
            .filter(
                models.Discount_Data.id == discount_id,
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .first()
        )

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": discount.id,
                "country_id": discount.Country_ID,
                "discount_name": discount.Discount_Name,
                "discount_percentage": discount.Discount_Percentage,
                "company_id": discount.company_id,
                "created_by": discount.created_by,
                "created_at": discount.created_at,
                "updated_at": discount.updated_at
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
# UPDATE DISCOUNT
# =====================================================
@router.put("/discount", status_code=status.HTTP_200_OK)
async def update_discount(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE PARSE)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        discount_id = payload.get("id")
        country_id = payload.get("country_id")
        discount_name = payload.get("discount_name")
        discount_percentage = payload.get("discount_percentage")

        # -------------------------------------------------
        # VALIDATION (MANDATORY)
        # -------------------------------------------------
        if not isinstance(discount_id, int) or discount_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid discount id is required"
            )

        if not isinstance(country_id, str) or not country_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_id is required"
            )

        if not isinstance(discount_name, str) or not discount_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_name is required"
            )

        if discount_percentage is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_percentage is required"
            )

        try:
            discount_percentage = float(discount_percentage)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_percentage must be a number"
            )

        if not (0 < discount_percentage <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_percentage must be between 1 and 100"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        duplicate = (
            db.query(models.Discount_Data)
            .filter(
                models.Discount_Data.id != discount_id,
                func.lower(models.Discount_Data.Country_ID) == country_id.lower(),
                func.lower(models.Discount_Data.Discount_Name) == discount_name.lower(),
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Discount already exists for this country"
            )

        # -------------------------------------------------
        # FETCH DISCOUNT
        # -------------------------------------------------
        discount = (
            db.query(models.Discount_Data)
            .filter(
                models.Discount_Data.id == discount_id,
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .first()
        )

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------
        discount.Country_ID = country_id.strip()
        discount.Discount_Name = discount_name.strip()
        discount.Discount_Percentage = str(discount_percentage)
        discount.updated_by = user_id

        db.commit()
        db.refresh(discount)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Discount updated successfully",
            "data": {
                "id": discount.id,
                "country_id": discount.Country_ID,
                "discount_name": discount.Discount_Name,
                "discount_percentage": discount.Discount_Percentage,
                "company_id": discount.company_id,
                "updated_by": discount.updated_by,
                "updated_at": discount.updated_at
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
# DELETE DISCOUNT (SOFT DELETE)
# =====================================================
@router.delete("/discount/{discount_id}", status_code=status.HTTP_200_OK)
def delete_discount(
    request: Request,
    discount_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(discount_id, int) or discount_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid discount id is required"
            )

        # -------------------------------------------------
        # FETCH DISCOUNT
        # -------------------------------------------------
        discount = (
            db.query(models.Discount_Data)
            .filter(
                models.Discount_Data.id == discount_id,
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .first()
        )

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        discount.status = CommonWords.UNSTATUS
        discount.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Discount deleted successfully",
            "data": {
                "id": discount.id,
                "discount_name": discount.Discount_Name,
                "company_id": discount.company_id
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
# GET ALL TAX TYPES
# =====================================================
@router.get("/tax", status_code=status.HTTP_200_OK)
def get_taxes(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH TAX TYPES + COUNTRY
        # -------------------------------------------------
        taxes = (
            db.query(
                models.Tax_type,
                models.Country_Courrency.Country_Name
            )
            .join(
                models.Country_Courrency,
                models.Country_Courrency.id
                == models.Tax_type.Country_ID
            )
            .filter(
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .order_by(models.Tax_type.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": tax.id,
                "country_id": tax.Country_ID,
                "country_name": country_name,
                "tax_name": tax.Tax_Name,
                "tax_percentage": tax.Tax_Percentage,
                "company_id": tax.company_id,
                "created_by": tax.created_by,
                "created_at": tax.created_at,
                "updated_at": tax.updated_at
            }
            for tax, country_name in taxes
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
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE TAX
# =====================================================
@router.post("/tax", status_code=status.HTTP_201_CREATED)
async def create_tax(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        country_id = payload.get("country_id")
        tax_name = payload.get("tax_name")
        tax_percentage = payload.get("tax_percentage")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(country_id, int) or country_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid country_id is required"
            )

        if not tax_name or not tax_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_name is required"
            )

        if tax_percentage is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_percentage is required"
            )

        try:
            tax_percentage = float(tax_percentage)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_percentage must be a number"
            )

        if not (0 < tax_percentage <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_percentage must be between 1 and 100"
            )

        # -------------------------------------------------
        # FETCH COUNTRY (MANDATORY)
        # -------------------------------------------------
        country = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.id == country_id,
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found or inactive"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (COUNTRY + TAX NAME)
        # -------------------------------------------------
        exists = (
            db.query(models.Tax_type)
            .filter(
                models.Tax_type.Country_ID == str(country.id),
                func.lower(models.Tax_type.Tax_Name)
                == tax_name.strip().lower(),
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tax already exists for this country"
            )

        # -------------------------------------------------
        # CREATE TAX
        # -------------------------------------------------
        tax = models.Tax_type(
            Country_ID=str(country.id),   # 🔥 FK stored safely
            Tax_Name=tax_name.strip(),
            Tax_Percentage=str(tax_percentage),
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(tax)
        db.commit()
        db.refresh(tax)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Tax created successfully",
            "data": {
                "id": tax.id,
                "country_id": country.id,
                "country_name": country.Country_Name,
                "tax_name": tax.Tax_Name,
                "tax_percentage": tax.Tax_Percentage,
                "company_id": tax.company_id,
                "created_by": tax.created_by,
                "created_at": tax.created_at
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
# GET TAX BY ID
# =====================================================
@router.get("/tax/{tax_id}", status_code=status.HTTP_200_OK)
def get_tax_by_id(
    tax_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if tax_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tax id"
            )

        # -------------------------------------------------
        # FETCH TAX + COUNTRY
        # -------------------------------------------------
        result = (
            db.query(
                models.Tax_type,
                models.Country_Courrency.Country_Name
            )
            .join(
                models.Country_Courrency,
                models.Country_Courrency.id
                == models.Tax_type.Country_ID
            )
            .filter(
                models.Tax_type.id == tax_id,
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax not found"
            )

        tax, country_name = result

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": tax.id,
                "country_id": tax.Country_ID,
                "country_name": country_name,
                "tax_name": tax.Tax_Name,
                "tax_percentage": tax.Tax_Percentage,
                "company_id": tax.company_id,
                "created_by": tax.created_by,
                "created_at": tax.created_at,
                "updated_at": tax.updated_at
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
# UPDATE TAX
# =====================================================
@router.put("/tax", status_code=status.HTTP_200_OK)
async def update_tax(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        tax_id = payload.get("id")
        country_id = payload.get("country_id")
        tax_name = payload.get("tax_name")
        tax_percentage = payload.get("tax_percentage")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(tax_id, int) or tax_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid tax id is required"
            )

        if not isinstance(country_id, int) or country_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid country_id is required"
            )

        if not tax_name or not isinstance(tax_name, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_name is required"
            )

        if tax_percentage is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_percentage is required"
            )

        try:
            tax_percentage = float(tax_percentage)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_percentage must be a number"
            )

        if not (0 < tax_percentage <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tax_percentage must be between 1 and 100"
            )

        # -------------------------------------------------
        # CHECK COUNTRY EXISTS
        # -------------------------------------------------
        country = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.id == country_id,
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        duplicate = (
            db.query(models.Tax_type)
            .filter(
                models.Tax_type.id != tax_id,
                models.Tax_type.Country_ID == str(country_id),
                func.lower(models.Tax_type.Tax_Name) == tax_name.lower(),
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tax already exists for this country"
            )

        # -------------------------------------------------
        # FETCH TAX
        # -------------------------------------------------
        tax = (
            db.query(models.Tax_type)
            .filter(
                models.Tax_type.id == tax_id,
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS
            )
            .first()
        )

        if not tax:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax not found"
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------
        tax.Country_ID = str(country_id)
        tax.Tax_Name = tax_name
        tax.Tax_Percentage = str(tax_percentage)
        tax.updated_by = user_id

        db.commit()
        db.refresh(tax)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Tax updated successfully",
            "data": {
                "id": tax.id,
                "country_id": tax.Country_ID,
                "tax_name": tax.Tax_Name,
                "tax_percentage": tax.Tax_Percentage,
                "updated_by": tax.updated_by,
                "updated_at": tax.updated_at
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
# DELETE TAX (SOFT DELETE)
# =====================================================
@router.delete("/tax/{tax_id}", status_code=status.HTTP_200_OK)
def delete_tax(
    tax_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if tax_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid tax_id is required"
            )

        # -------------------------------------------------
        # FETCH TAX
        # -------------------------------------------------
        tax = (
            db.query(models.Tax_type)
            .filter(
                models.Tax_type.id == tax_id,
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS
            )
            .first()
        )

        if not tax:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        tax.status = CommonWords.UNSTATUS
        tax.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Tax deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL PAYMENT METHODS
# =====================================================
@router.get("/payment_methods", status_code=status.HTTP_200_OK)
def get_payment_methods(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payments = (
            db.query(models.Payment_Methods)
            .filter(
                models.Payment_Methods.company_id == company_id,
                models.Payment_Methods.status == CommonWords.STATUS
            )
            .order_by(models.Payment_Methods.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": payments
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE PAYMENT METHOD
# =====================================================
@router.post("/payment_methods", status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        payment_method = payload.get("payment_method")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([payment_method, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payment_method, company_id and created_by are required"
            )

        exists = db.query(models.Payment_Methods).filter(
            func.lower(models.Payment_Methods.payment_method) == payment_method.lower(),
            models.Payment_Methods.company_id == company_id,
            models.Payment_Methods.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment method already exists"
            )

        payment = models.Payment_Methods(
            payment_method=payment_method,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "status": "success",
            "message": "Payment method created successfully",
            "data": payment
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET PAYMENT METHOD BY ID
# =====================================================
@router.get("/payment_methods/{payment_id}", status_code=status.HTTP_200_OK)
def get_payment_method_by_id(
    payment_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payment = db.query(models.Payment_Methods).filter(
            models.Payment_Methods.id == payment_id,
            models.Payment_Methods.company_id == company_id,
            models.Payment_Methods.status == CommonWords.STATUS
        ).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )

        return {
            "status": "success",
            "data": payment
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE PAYMENT METHOD
# =====================================================
@router.put("/payment_methods", status_code=status.HTTP_200_OK)
async def update_payment_method(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        payment_id = payload.get("id")
        payment_method = payload.get("payment_method")
        company_id = payload.get("company_id")

        if not all([payment_id, payment_method, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, payment_method and company_id are required"
            )

        duplicate = db.query(models.Payment_Methods).filter(
            models.Payment_Methods.id != payment_id,
            func.lower(models.Payment_Methods.payment_method) == payment_method.lower(),
            models.Payment_Methods.company_id == company_id,
            models.Payment_Methods.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment method already exists"
            )

        payment = db.query(models.Payment_Methods).filter(
            models.Payment_Methods.id == payment_id,
            models.Payment_Methods.company_id == company_id,
            models.Payment_Methods.status == CommonWords.STATUS
        ).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )

        payment.payment_method = payment_method
        db.commit()
        db.refresh(payment)

        return {
            "status": "success",
            "message": "Payment method updated successfully",
            "data": payment
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE PAYMENT METHOD (SOFT DELETE)
# =====================================================
@router.delete("/payment_methods/{payment_id}", status_code=status.HTTP_200_OK)
def delete_payment_method(
    payment_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payment = db.query(models.Payment_Methods).filter(
            models.Payment_Methods.id == payment_id,
            models.Payment_Methods.company_id == company_id,
            models.Payment_Methods.status == CommonWords.STATUS
        ).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )

        payment.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Payment method deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL IDENTITY PROOFS
# =====================================================
@router.get("/identity_proof", status_code=status.HTTP_200_OK)
def get_identity_proofs(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        proofs = (
            db.query(models.Identity_Proofs)
            .filter(
                models.Identity_Proofs.company_id == company_id,
                models.Identity_Proofs.status == CommonWords.STATUS
            )
            .order_by(models.Identity_Proofs.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": proofs
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE IDENTITY PROOF
# =====================================================
@router.post("/identity_proof", status_code=status.HTTP_201_CREATED)
async def create_identity_proof(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        proof_name = payload.get("proof_name")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([proof_name, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="proof_name, company_id and created_by are required"
            )

        exists = db.query(models.Identity_Proofs).filter(
            func.lower(models.Identity_Proofs.Proof_Name) == proof_name.lower(),
            models.Identity_Proofs.company_id == company_id,
            models.Identity_Proofs.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Identity proof already exists"
            )

        proof = models.Identity_Proofs(
            Proof_Name=proof_name,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(proof)
        db.commit()
        db.refresh(proof)

        return {
            "status": "success",
            "message": "Identity proof created successfully",
            "data": proof
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET IDENTITY PROOF BY ID
# =====================================================
@router.get("/identity_proof/{proof_id}", status_code=status.HTTP_200_OK)
def get_identity_proof_by_id(
    proof_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        proof = db.query(models.Identity_Proofs).filter(
            models.Identity_Proofs.id == proof_id,
            models.Identity_Proofs.company_id == company_id,
            models.Identity_Proofs.status == CommonWords.STATUS
        ).first()

        if not proof:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Identity proof not found"
            )

        return {
            "status": "success",
            "data": proof
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE IDENTITY PROOF
# =====================================================
@router.put("/identity_proof", status_code=status.HTTP_200_OK)
async def update_identity_proof(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        proof_id = payload.get("id")
        proof_name = payload.get("proof_name")
        company_id = payload.get("company_id")

        if not all([proof_id, proof_name, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, proof_name and company_id are required"
            )

        duplicate = db.query(models.Identity_Proofs).filter(
            models.Identity_Proofs.id != proof_id,
            func.lower(models.Identity_Proofs.Proof_Name) == proof_name.lower(),
            models.Identity_Proofs.company_id == company_id,
            models.Identity_Proofs.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Identity proof already exists"
            )

        proof = db.query(models.Identity_Proofs).filter(
            models.Identity_Proofs.id == proof_id,
            models.Identity_Proofs.company_id == company_id,
            models.Identity_Proofs.status == CommonWords.STATUS
        ).first()

        if not proof:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Identity proof not found"
            )

        proof.Proof_Name = proof_name
        db.commit()
        db.refresh(proof)

        return {
            "status": "success",
            "message": "Identity proof updated successfully",
            "data": proof
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE IDENTITY PROOF (SOFT DELETE)
# =====================================================
@router.delete("/identity_proof/{proof_id}", status_code=status.HTTP_200_OK)
def delete_identity_proof(
    proof_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        proof = db.query(models.Identity_Proofs).filter(
            models.Identity_Proofs.id == proof_id,
            models.Identity_Proofs.company_id == company_id,
            models.Identity_Proofs.status == CommonWords.STATUS
        ).first()

        if not proof:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Identity proof not found"
            )

        proof.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Identity proof deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL COUNTRIES & CURRENCIES
# =====================================================
@router.get("/country_currency", status_code=status.HTTP_200_OK)
def get_country_currency(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH DATA
        # -------------------------------------------------
        countries = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .order_by(models.Country_Courrency.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": c.id,
                "country_name": c.Country_Name,
                "currency_name": c.Courrency_Name,
                "symbol": c.Symbol,
                "company_id": c.company_id,
                "created_by": c.created_by,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in countries
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
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE COUNTRY & CURRENCY
# =====================================================
@router.post("/country_currency", status_code=status.HTTP_201_CREATED)
async def create_country_currency(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        country_name = payload.get("country_name")
        currency_name = payload.get("currency_name")
        symbol = payload.get("symbol")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not country_name or not country_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_name is required"
            )

        if not currency_name or not currency_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="currency_name is required"
            )

        if not symbol or not symbol.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="symbol is required"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        exists = (
            db.query(models.Country_Courrency)
            .filter(
                func.lower(models.Country_Courrency.Country_Name)
                == country_name.strip().lower(),
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Country already exists"
            )

        # -------------------------------------------------
        # CREATE COUNTRY & CURRENCY
        # -------------------------------------------------
        country_currency = models.Country_Courrency(
            Country_Name=country_name.strip(),
            Courrency_Name=currency_name.strip(),
            Symbol=symbol.strip(),
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(country_currency)
        db.commit()
        db.refresh(country_currency)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Country & currency created successfully",
            "data": {
                "id": country_currency.id,
                "country_name": country_currency.Country_Name,
                "currency_name": country_currency.Courrency_Name,
                "symbol": country_currency.Symbol,
                "company_id": country_currency.company_id,
                "created_by": country_currency.created_by,
                "created_at": country_currency.created_at
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
# GET COUNTRY & CURRENCY BY ID
# =====================================================
@router.get("/country_currency/{country_id}", status_code=status.HTTP_200_OK)
def get_country_currency_by_id(
    request: Request,
    country_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(country_id, int) or country_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid country id is required"
            )

        # -------------------------------------------------
        # FETCH COUNTRY & CURRENCY
        # -------------------------------------------------
        country = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.id == country_id,
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": country.id,
                "country_name": country.Country_Name,
                "currency_name": country.Courrency_Name,
                "symbol": country.Symbol,
                "company_id": country.company_id,
                "created_by": country.created_by,
                "created_at": country.created_at,
                "updated_at": country.updated_at
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
# UPDATE COUNTRY & CURRENCY
# =====================================================
@router.put("/country_currency", status_code=status.HTTP_200_OK)
async def update_country_currency(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE PARSE)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        country_id = payload.get("id")
        country_name = payload.get("country_name")
        currency_name = payload.get("currency_name")
        symbol = payload.get("symbol")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(country_id, int) or country_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid country id is required"
            )

        if not country_name or not country_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_name is required"
            )

        if not currency_name or not currency_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="currency_name is required"
            )

        if not symbol or not symbol.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="symbol is required"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        duplicate = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.id != country_id,
                func.lower(models.Country_Courrency.Country_Name)
                == country_name.strip().lower(),
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Country already exists"
            )

        # -------------------------------------------------
        # FETCH RECORD
        # -------------------------------------------------
        country = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.id == country_id,
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------
        country.Country_Name = country_name.strip()
        country.Courrency_Name = currency_name.strip()
        country.Symbol = symbol.strip()
        country.updated_by = user_id

        db.commit()
        db.refresh(country)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Country & currency updated successfully",
            "data": {
                "id": country.id,
                "country_name": country.Country_Name,
                "currency_name": country.Courrency_Name,
                "symbol": country.Symbol,
                "company_id": country.company_id,
                "updated_by": country.updated_by,
                "updated_at": country.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE COUNTRY & CURRENCY (SOFT DELETE)
# =====================================================
@router.delete("/country_currency/{country_id}", status_code=status.HTTP_200_OK)
def delete_country_currency(
    request: Request,
    country_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(country_id, int) or country_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid country id is required"
            )

        # -------------------------------------------------
        # FETCH COUNTRY
        # -------------------------------------------------
        country = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.id == country_id,
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .first()
        )

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        country.status = CommonWords.UNSTATUS
        country.updated_by = user_id
        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Country & currency deleted successfully",
            "data": {
                "id": country.id,
                "country_name": country.Country_Name,
                "company_id": country.company_id
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL TASK TYPES
# =====================================================
@router.get("/task_type", status_code=status.HTTP_200_OK)
def get_task_types(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        task_types = (
            db.query(models.Task_Type)
            .filter(
                models.Task_Type.company_id == company_id,
                models.Task_Type.status == CommonWords.STATUS
            )
            .order_by(models.Task_Type.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": task_types
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE TASK TYPE
# =====================================================
@router.post("/task_type", status_code=status.HTTP_201_CREATED)
async def create_task_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        task_name = payload.get("task_name")
        color = payload.get("color")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([task_name, color, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="task_name, color, company_id and created_by are required"
            )

        exists = db.query(models.Task_Type).filter(
            func.lower(models.Task_Type.Type_Name) == task_name.lower(),
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task type already exists"
            )

        task_type = models.Task_Type(
            Type_Name=task_name,
            Color=color,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        return {
            "status": "success",
            "message": "Task type created successfully",
            "data": task_type
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET TASK TYPE BY ID
# =====================================================
@router.get("/task_type/{task_type_id}", status_code=status.HTTP_200_OK)
def get_task_type_by_id(
    task_type_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        task_type = db.query(models.Task_Type).filter(
            models.Task_Type.id == task_type_id,
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).first()

        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task type not found"
            )

        return {
            "status": "success",
            "data": task_type
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE TASK TYPE
# =====================================================
@router.put("/task_type", status_code=status.HTTP_200_OK)
async def update_task_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        task_type_id = payload.get("id")
        task_name = payload.get("task_name")
        color = payload.get("color")
        company_id = payload.get("company_id")

        if not all([task_type_id, task_name, color, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, task_name, color and company_id are required"
            )

        duplicate = db.query(models.Task_Type).filter(
            models.Task_Type.id != task_type_id,
            func.lower(models.Task_Type.Type_Name) == task_name.lower(),
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task type already exists"
            )

        task_type = db.query(models.Task_Type).filter(
            models.Task_Type.id == task_type_id,
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).first()

        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task type not found"
            )

        task_type.Type_Name = task_name
        task_type.Color = color

        db.commit()
        db.refresh(task_type)

        return {
            "status": "success",
            "message": "Task type updated successfully",
            "data": task_type
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE TASK TYPE (SOFT DELETE)
# =====================================================
@router.delete("/task_type/{task_type_id}", status_code=status.HTTP_200_OK)
def delete_task_type(
    task_type_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        task_type = db.query(models.Task_Type).filter(
            models.Task_Type.id == task_type_id,
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).first()

        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task type not found"
            )

        task_type.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Task type deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL ROOM COMPLEMENTARIES
# =====================================================
@router.get("/complementry", status_code=status.HTTP_200_OK)
def get_room_complementries(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH COMPLEMENTARIES
        # -------------------------------------------------
        complementries = (
            db.query(models.Room_Complementry)
            .filter(
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .order_by(models.Room_Complementry.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": comp.id,
                "complementry_name": comp.Complementry_Name,
                "company_id": comp.company_id,
                "created_by": comp.created_by,
                "created_at": comp.created_at,
                "updated_at": comp.updated_at
            }
            for comp in complementries
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
        # ✅ Preserve correct HTTP status codes
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE ROOM COMPLEMENTARY
# =====================================================
@router.post("/complementry", status_code=status.HTTP_201_CREATED)
async def create_room_complementry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE PARSE)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        complementry_name = payload.get("complementry_name")
        description = payload.get("description")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not complementry_name or not complementry_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="complementry_name is required"
            )

        if not description or not description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description is required"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        exists = (
            db.query(models.Room_Complementry)
            .filter(
                func.lower(models.Room_Complementry.Complementry_Name)
                == complementry_name.strip().lower(),
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room complementary already exists"
            )

        # -------------------------------------------------
        # CREATE COMPLEMENTARY
        # -------------------------------------------------
        complementry = models.Room_Complementry(
            Complementry_Name=complementry_name.strip(),
            Description=description.strip(),
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(complementry)
        db.commit()
        db.refresh(complementry)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room complementary created successfully",
            "data": {
                "id": complementry.id,
                "complementry_name": complementry.Complementry_Name,
                "description": complementry.Description,
                "company_id": complementry.company_id,
                "created_by": complementry.created_by,
                "created_at": complementry.created_at
            }
        }

    except HTTPException:
        # ✅ Preserve real HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ROOM COMPLEMENTARY BY ID
# =====================================================
@router.get("/complementry/{complementry_id}", status_code=status.HTTP_200_OK)
def get_room_complementry_by_id(
    request: Request,
    complementry_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(complementry_id, int) or complementry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid complementry id is required"
            )

        # -------------------------------------------------
        # FETCH COMPLEMENTARY
        # -------------------------------------------------
        complementry = (
            db.query(models.Room_Complementry)
            .filter(
                models.Room_Complementry.id == complementry_id,
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .first()
        )

        if not complementry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room complementary not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": complementry.id,
                "complementry_name": complementry.Complementry_Name,
                "description": complementry.Description,
                "company_id": complementry.company_id,
                "created_by": complementry.created_by,
                "created_at": complementry.created_at,
                "updated_at": complementry.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve real HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE ROOM COMPLEMENTARY
# =====================================================
@router.put("/complementry", status_code=status.HTTP_200_OK)
async def update_room_complementry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE PARSE)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        complementry_id = payload.get("id")
        complementry_name = payload.get("complementry_name")
        description = payload.get("description")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(complementry_id, int) or complementry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid complementry id is required"
            )

        if not complementry_name or not complementry_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="complementry_name is required"
            )

        if not description or not description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description is required"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        duplicate = (
            db.query(models.Room_Complementry)
            .filter(
                models.Room_Complementry.id != complementry_id,
                func.lower(models.Room_Complementry.Complementry_Name)
                == complementry_name.strip().lower(),
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room complementary already exists"
            )

        # -------------------------------------------------
        # FETCH COMPLEMENTARY
        # -------------------------------------------------
        complementry = (
            db.query(models.Room_Complementry)
            .filter(
                models.Room_Complementry.id == complementry_id,
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .first()
        )

        if not complementry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room complementary not found"
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------
        complementry.Complementry_Name = complementry_name.strip()
        complementry.Description = description.strip()
        complementry.updated_by = user_id

        db.commit()
        db.refresh(complementry)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room complementary updated successfully",
            "data": {
                "id": complementry.id,
                "complementry_name": complementry.Complementry_Name,
                "description": complementry.Description,
                "company_id": complementry.company_id,
                "updated_by": complementry.updated_by,
                "updated_at": complementry.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE ROOM COMPLEMENTARY (SOFT DELETE)
# =====================================================
@router.delete("/complementry/{complementry_id}", status_code=status.HTTP_200_OK)
def delete_room_complementry(
    request: Request,
    complementry_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(complementry_id, int) or complementry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid complementry id is required"
            )

        # -------------------------------------------------
        # FETCH COMPLEMENTARY
        # -------------------------------------------------
        complementry = (
            db.query(models.Room_Complementry)
            .filter(
                models.Room_Complementry.id == complementry_id,
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .first()
        )

        if not complementry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room complementary not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        complementry.status = CommonWords.UNSTATUS
        complementry.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room complementary deleted successfully",
            "data": {
                "id": complementry.id,
                "complementry_name": complementry.Complementry_Name,
                "company_id": complementry.company_id
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL RESERVATION STATUSES
# =====================================================
@router.get("/reservation_status", status_code=status.HTTP_200_OK)
def get_reservation_status(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        statuses = (
            db.query(models.Reservation_Status)
            .filter(
                models.Reservation_Status.company_id == company_id,
                models.Reservation_Status.status == CommonWords.STATUS
            )
            .order_by(models.Reservation_Status.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": statuses
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE RESERVATION STATUS
# =====================================================
@router.post("/reservation_status", status_code=status.HTTP_201_CREATED)
async def create_reservation_status(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        status_name = payload.get("status_name")
        color = payload.get("color")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([status_name, color, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="status_name, color, company_id and created_by are required"
            )

        exists = db.query(models.Reservation_Status).filter(
            func.lower(models.Reservation_Status.Status_Name) == status_name.lower(),
            models.Reservation_Status.company_id == company_id,
            models.Reservation_Status.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Reservation status already exists"
            )

        reservation_status = models.Reservation_Status(
            Status_Name=status_name,
            Color=color,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(reservation_status)
        db.commit()
        db.refresh(reservation_status)

        return {
            "status": "success",
            "message": "Reservation status created successfully",
            "data": reservation_status
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc
# =====================================================
# GET RESERVATION STATUS BY ID
# =====================================================
@router.get("/reservation_status/{status_id}", status_code=status.HTTP_200_OK)
def get_reservation_status_by_id(
    status_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        reservation_status = db.query(models.Reservation_Status).filter(
            models.Reservation_Status.id == status_id,
            models.Reservation_Status.company_id == company_id,
            models.Reservation_Status.status == CommonWords.STATUS
        ).first()

        if not reservation_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation status not found"
            )

        return {
            "status": "success",
            "data": reservation_status
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE RESERVATION STATUS
# =====================================================
@router.put("/reservation_status", status_code=status.HTTP_200_OK)
async def update_reservation_status(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        status_id = payload.get("id")
        status_name = payload.get("status_name")
        color = payload.get("color")
        company_id = payload.get("company_id")

        if not all([status_id, status_name, color, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, status_name, color and company_id are required"
            )

        duplicate = db.query(models.Reservation_Status).filter(
            models.Reservation_Status.id != status_id,
            func.lower(models.Reservation_Status.Status_Name) == status_name.lower(),
            models.Reservation_Status.company_id == company_id,
            models.Reservation_Status.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Reservation status already exists"
            )

        reservation_status = db.query(models.Reservation_Status).filter(
            models.Reservation_Status.id == status_id,
            models.Reservation_Status.company_id == company_id,
            models.Reservation_Status.status == CommonWords.STATUS
        ).first()

        if not reservation_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation status not found"
            )

        reservation_status.Status_Name = status_name
        reservation_status.Color = color

        db.commit()
        db.refresh(reservation_status)

        return {
            "status": "success",
            "message": "Reservation status updated successfully",
            "data": reservation_status
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE RESERVATION STATUS (SOFT DELETE)
# =====================================================
@router.delete("/reservation_status/{status_id}", status_code=status.HTTP_200_OK)
def delete_reservation_status(
    status_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        reservation_status = db.query(models.Reservation_Status).filter(
            models.Reservation_Status.id == status_id,
            models.Reservation_Status.company_id == company_id,
            models.Reservation_Status.status == CommonWords.STATUS
        ).first()

        if not reservation_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation status not found"
            )

        reservation_status.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Reservation status deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

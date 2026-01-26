from enum import verify
from fastapi import APIRouter, Depends, status, HTTPException, Request, UploadFile, File
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
@router.get("/bed_type", status_code=status.HTTP_200_OK)
def get_bed_types(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        bed_types = (
            db.query(models.Bed_Type)
            .filter(
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            )
            .order_by(models.Bed_Type.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": bed_types
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE BED TYPE
# =====================================================
@router.post("/bed_type", status_code=status.HTTP_201_CREATED)
async def create_bed_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        bed_type_name = payload.get("bed_type")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([bed_type_name, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bed_type, company_id and created_by are required"
            )

        exists = db.query(models.Bed_Type).filter(
            func.lower(models.Bed_Type.Type_Name) == bed_type_name.lower(),
            models.Bed_Type.company_id == company_id,
            models.Bed_Type.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bed type already exists"
            )

        bed_type = models.Bed_Type(
            Type_Name=bed_type_name,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(bed_type)
        db.commit()
        db.refresh(bed_type)

        return {
            "status": "success",
            "message": "Bed type created successfully",
            "data": bed_type
        }

    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc
    
# =====================================================
# GET BED TYPE BY ID
# =====================================================
@router.get("/bed_type/{bed_type_id}", status_code=status.HTTP_200_OK)
def get_bed_type_by_id(
    bed_type_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        bed_type = db.query(models.Bed_Type).filter(
            models.Bed_Type.id == bed_type_id,
            models.Bed_Type.company_id == company_id,
            models.Bed_Type.status == CommonWords.STATUS
        ).first()

        if not bed_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed type not found"
            )

        return {
            "status": "success",
            "data": bed_type
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc
    
# =====================================================
# UPDATE BED TYPE
# =====================================================
@router.put("/bed_type", status_code=status.HTTP_200_OK)
async def update_bed_type(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        bed_type_id = payload.get("id")
        bed_type_name = payload.get("bed_type")
        company_id = payload.get("company_id")

        if not all([bed_type_id, bed_type_name, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, bed_type and company_id are required"
            )

        duplicate = db.query(models.Bed_Type).filter(
            models.Bed_Type.id != bed_type_id,
            func.lower(models.Bed_Type.Type_Name) == bed_type_name.lower(),
            models.Bed_Type.company_id == company_id,
            models.Bed_Type.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bed type name already exists"
            )

        bed_type = db.query(models.Bed_Type).filter(
            models.Bed_Type.id == bed_type_id,
            models.Bed_Type.company_id == company_id,
            models.Bed_Type.status == CommonWords.STATUS
        ).first()

        if not bed_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed type not found"
            )

        bed_type.Type_Name = bed_type_name
        db.commit()
        db.refresh(bed_type)

        return {
            "status": "success",
            "message": "Bed type updated successfully",
            "data": bed_type
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE BED TYPE (SOFT DELETE)
# =====================================================
@router.delete("/bed_type/{bed_type_id}", status_code=status.HTTP_200_OK)
def delete_bed_type(
    bed_type_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        bed_type = db.query(models.Bed_Type).filter(
                models.Bed_Type.id == bed_type_id,
                models.Bed_Type.company_id == company_id,
                models.Bed_Type.status == CommonWords.STATUS
            ).first()
        if not bed_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed type not found"
            )

        bed_type.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Bed type deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL HALL / FLOOR
# =====================================================
@router.get("/hall_floor", status_code=status.HTTP_200_OK)
def get_hall_floors(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        halls = (
            db.query(models.TableHallNames)
            .filter(
                models.TableHallNames.company_id == company_id,
                models.TableHallNames.status == CommonWords.STATUS
            )
            .order_by(models.TableHallNames.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": halls
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE HALL / FLOOR
# =====================================================
@router.post("/hall_floor", status_code=status.HTTP_201_CREATED)
async def create_hall_floor(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        hall_name = payload.get("hall_name")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([hall_name, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hall_name, company_id and created_by are required"
            )

        exists = db.query(models.TableHallNames).filter(
            func.lower(models.TableHallNames.hall_name) == hall_name.lower(),
            models.TableHallNames.company_id == company_id,
            models.TableHallNames.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hall / Floor already exists"
            )

        hall = models.TableHallNames(
            hall_name=hall_name,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(hall)
        db.commit()
        db.refresh(hall)

        return {
            "status": "success",
            "message": "Hall / Floor created successfully",
            "data": hall
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc
    
# =====================================================
# GET HALL / FLOOR BY ID
# =====================================================
@router.get("/hall_floor/{hall_id}", status_code=status.HTTP_200_OK)
def get_hall_floor_by_id(
    hall_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        hall = db.query(models.TableHallNames).filter(
            models.TableHallNames.id == hall_id,
            models.TableHallNames.company_id == company_id,
            models.TableHallNames.status == CommonWords.STATUS
        ).first()

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall / Floor not found"
            )

        return {
            "status": "success",
            "data": hall
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE HALL / FLOOR
# =====================================================
@router.put("/hall_floor", status_code=status.HTTP_200_OK)
async def update_hall_floor(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        hall_id = payload.get("id")
        hall_name = payload.get("hall_name")
        company_id = payload.get("company_id")

        if not all([hall_id, hall_name, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, hall_name and company_id are required"
            )

        duplicate = db.query(models.TableHallNames).filter(
            models.TableHallNames.id != hall_id,
            func.lower(models.TableHallNames.hall_name) == hall_name.lower(),
            models.TableHallNames.company_id == company_id,
            models.TableHallNames.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hall / Floor name already exists"
            )

        hall = db.query(models.TableHallNames).filter(
            models.TableHallNames.id == hall_id,
            models.TableHallNames.company_id == company_id,
            models.TableHallNames.status == CommonWords.STATUS
        ).first()

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall / Floor not found"
            )

        hall.hall_name = hall_name
        db.commit()
        db.refresh(hall)

        return {
            "status": "success",
            "message": "Hall / Floor updated successfully",
            "data": hall
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE HALL / FLOOR (SOFT DELETE)
# =====================================================
@router.delete("/hall_floor/{hall_id}", status_code=status.HTTP_200_OK)
def delete_hall_floor(
    hall_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        hall = db.query(models.TableHallNames).filter(
            models.TableHallNames.id == hall_id,
            models.TableHallNames.company_id == company_id,
            models.TableHallNames.status == CommonWords.STATUS
        ).first()

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall / Floor not found"
            )

        hall.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Hall / Floor deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL ROOMS
# =====================================================
@router.get("/room", status_code=status.HTTP_200_OK)
def get_rooms(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        rooms = (
            db.query(models.Room)
            .filter(
                models.Room.company_id == company_id,
                models.Room.status == CommonWords.STATUS
            )
            .order_by(models.Room.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": rooms
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE ROOM
# =====================================================
@router.post("/room", status_code=status.HTTP_201_CREATED)
async def create_room(
    request: Request,
    room_no: str,
    room_name: str,
    room_type: str,
    bed_type: str,
    tele_no: str,
    max_adult: str,
    max_child: str,
    company_id: str,
    created_by: str,
    image_1: UploadFile = File(...),
    image_2: UploadFile = File(...),
    image_3: UploadFile = File(...),
    image_4: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        exists = db.query(models.Room).filter(
            models.Room.Room_No == room_no,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

        def save_image(file: UploadFile):
            ext = file.content_type.split("/")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            filepath = os.path.join(UPLOAD_PATH, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return filename

        img1 = save_image(image_1)
        img2 = save_image(image_2)
        img3 = save_image(image_3)
        img4 = save_image(image_4)

        room = models.Room(
            Room_No=room_no,
            Room_Name=room_name,
            Room_Type_ID=room_type,
            Bed_Type_ID=bed_type,
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
            created_by=created_by,
            company_id=company_id
        )

        db.add(room)
        db.commit()
        db.refresh(room)

        return {
            "status": "success",
            "message": "Room created successfully",
            "data": room
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ROOM BY ID
# =====================================================
@router.get("/room/{room_id}", status_code=status.HTTP_200_OK)
def get_room_by_id(
    room_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        room = db.query(models.Room).filter(
            models.Room.id == room_id,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        return {
            "status": "success",
            "data": room
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE ROOM
# =====================================================
@router.put("/room", status_code=status.HTTP_200_OK)
async def update_room(
    room_id: int,
    room_no: str,
    room_name: str,
    room_type: str,
    bed_type: str,
    tele_no: str,
    max_adult: str,
    max_child: str,
    room_condition: str,
    company_id: str,
    image_1: Optional[UploadFile] = File(None),
    image_2: Optional[UploadFile] = File(None),
    image_3: Optional[UploadFile] = File(None),
    image_4: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        duplicate = db.query(models.Room).filter(
            models.Room.id != room_id,
            models.Room.Room_No == room_no,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

        room = db.query(models.Room).filter(
            models.Room.id == room_id,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        def replace_image(file: UploadFile, old_name: str):
            ext = file.content_type.split("/")[-1]
            filename = f"{old_name.split('.')[0]}.{ext}"
            filepath = os.path.join(UPLOAD_PATH, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return filename

        if image_1:
            room.Room_Image_1 = replace_image(image_1, room.Room_Image_1)
        if image_2:
            room.Room_Image_2 = replace_image(image_2, room.Room_Image_2)
        if image_3:
            room.Room_Image_3 = replace_image(image_3, room.Room_Image_3)
        if image_4:
            room.Room_Image_4 = replace_image(image_4, room.Room_Image_4)

        room.Room_No = room_no
        room.Room_Name = room_name
        room.Room_Type_ID = room_type
        room.Bed_Type_ID = bed_type
        room.Room_Telephone = tele_no
        room.Max_Adult_Occupy = max_adult
        room.Max_Child_Occupy = max_child
        room.Room_Status = room_condition

        db.commit()
        db.refresh(room)

        return {
            "status": "success",
            "message": "Room updated successfully",
            "data": room
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE ROOM (SOFT DELETE)
# =====================================================
@router.delete("/room/{room_id}", status_code=status.HTTP_200_OK)
def delete_room(
    room_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        room = db.query(models.Room).filter(
            models.Room.id == room_id,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        room.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Room deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL DISCOUNTS
# =====================================================
@router.get("/discount", status_code=status.HTTP_200_OK)
def get_discounts(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        discounts = (
            db.query(models.Discount_Data)
            .filter(
                models.Discount_Data.company_id == company_id,
                models.Discount_Data.status == CommonWords.STATUS
            )
            .order_by(models.Discount_Data.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": discounts
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE DISCOUNT
# =====================================================
@router.post("/discount", status_code=status.HTTP_201_CREATED)
async def create_discount(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        country_id = payload.get("country_id")
        discount_name = payload.get("discount_name")
        discount_percentage = payload.get("discount_percentage")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([country_id, discount_name, discount_percentage, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_id, discount_name, discount_percentage, company_id, created_by are required"
            )

        exists = db.query(models.Discount_Data).filter(
            func.lower(models.Discount_Data.Country_ID) == country_id.lower(),
            func.lower(models.Discount_Data.Discount_Name) == discount_name.lower(),
            models.Discount_Data.company_id == company_id,
            models.Discount_Data.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Discount already exists for this country"
            )

        discount = models.Discount_Data(
            Country_ID=country_id,
            Discount_Name=discount_name,
            Discount_Percentage=discount_percentage,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(discount)
        db.commit()
        db.refresh(discount)

        return {
            "status": "success",
            "message": "Discount created successfully",
            "data": discount
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET DISCOUNT BY ID
# =====================================================
@router.get("/discount/{discount_id}", status_code=status.HTTP_200_OK)
def get_discount_by_id(
    discount_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        discount = db.query(models.Discount_Data).filter(
            models.Discount_Data.id == discount_id,
            models.Discount_Data.company_id == company_id,
            models.Discount_Data.status == CommonWords.STATUS
        ).first()

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )

        return {
            "status": "success",
            "data": discount
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE DISCOUNT
# =====================================================
@router.put("/discount", status_code=status.HTTP_200_OK)
async def update_discount(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        discount_id = payload.get("id")
        country_id = payload.get("country_id")
        discount_name = payload.get("discount_name")
        discount_percentage = payload.get("discount_percentage")
        company_id = payload.get("company_id")

        if not all([discount_id, country_id, discount_name, discount_percentage, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, country_id, discount_name, discount_percentage, company_id are required"
            )

        duplicate = db.query(models.Discount_Data).filter(
            models.Discount_Data.id != discount_id,
            func.lower(models.Discount_Data.Country_ID) == country_id.lower(),
            func.lower(models.Discount_Data.Discount_Name) == discount_name.lower(),
            models.Discount_Data.company_id == company_id,
            models.Discount_Data.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Discount already exists for this country"
            )

        discount = db.query(models.Discount_Data).filter(
            models.Discount_Data.id == discount_id,
            models.Discount_Data.company_id == company_id,
            models.Discount_Data.status == CommonWords.STATUS
        ).first()

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )

        discount.Country_ID = country_id
        discount.Discount_Name = discount_name
        discount.Discount_Percentage = discount_percentage

        db.commit()
        db.refresh(discount)

        return {
            "status": "success",
            "message": "Discount updated successfully",
            "data": discount
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE DISCOUNT (SOFT DELETE)
# =====================================================
@router.delete("/discount/{discount_id}", status_code=status.HTTP_200_OK)
def delete_discount(
    discount_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        discount = db.query(models.Discount_Data).filter(
            models.Discount_Data.id == discount_id,
            models.Discount_Data.company_id == company_id,
            models.Discount_Data.status == CommonWords.STATUS
        ).first()

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )

        discount.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Discount deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ALL TAX TYPES
# =====================================================
@router.get("/tax", status_code=status.HTTP_200_OK)
def get_taxes(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        taxes = (
            db.query(models.Tax_type)
            .filter(
                models.Tax_type.company_id == company_id,
                models.Tax_type.status == CommonWords.STATUS
            )
            .order_by(models.Tax_type.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": taxes
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE TAX
# =====================================================
@router.post("/tax", status_code=status.HTTP_201_CREATED)
async def create_tax(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        country_id = payload.get("country_id")
        tax_name = payload.get("tax_name")
        tax_percentage = payload.get("tax_percentage")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([country_id, tax_name, tax_percentage, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_id, tax_name, tax_percentage, company_id, created_by are required"
            )

        exists = db.query(models.Tax_type).filter(
            func.lower(models.Tax_type.Country_ID) == country_id.lower(),
            func.lower(models.Tax_type.Tax_Name) == tax_name.lower(),
            models.Tax_type.company_id == company_id,
            models.Tax_type.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tax already exists for this country"
            )

        tax = models.Tax_type(
            Country_ID=country_id,
            Tax_Name=tax_name,
            Tax_Percentage=tax_percentage,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(tax)
        db.commit()
        db.refresh(tax)

        return {
            "status": "success",
            "message": "Tax created successfully",
            "data": tax
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET TAX BY ID
# =====================================================
@router.get("/tax/{tax_id}", status_code=status.HTTP_200_OK)
def get_tax_by_id(
    tax_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        tax = db.query(models.Tax_type).filter(
            models.Tax_type.id == tax_id,
            models.Tax_type.company_id == company_id,
            models.Tax_type.status == CommonWords.STATUS
        ).first()

        if not tax:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax not found"
            )

        return {
            "status": "success",
            "data": tax
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE TAX
# =====================================================
@router.put("/tax", status_code=status.HTTP_200_OK)
async def update_tax(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        tax_id = payload.get("id")
        country_id = payload.get("country_id")
        tax_name = payload.get("tax_name")
        tax_percentage = payload.get("tax_percentage")
        company_id = payload.get("company_id")

        if not all([tax_id, country_id, tax_name, tax_percentage, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, country_id, tax_name, tax_percentage, company_id are required"
            )

        duplicate = db.query(models.Tax_type).filter(
            models.Tax_type.id != tax_id,
            func.lower(models.Tax_type.Country_ID) == country_id.lower(),
            func.lower(models.Tax_type.Tax_Name) == tax_name.lower(),
            models.Tax_type.company_id == company_id,
            models.Tax_type.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tax already exists for this country"
            )

        tax = db.query(models.Tax_type).filter(
            models.Tax_type.id == tax_id,
            models.Tax_type.company_id == company_id,
            models.Tax_type.status == CommonWords.STATUS
        ).first()

        if not tax:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax not found"
            )

        tax.Country_ID = country_id
        tax.Tax_Name = tax_name
        tax.Tax_Percentage = tax_percentage

        db.commit()
        db.refresh(tax)

        return {
            "status": "success",
            "message": "Tax updated successfully",
            "data": tax
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE TAX (SOFT DELETE)
# =====================================================
@router.delete("/tax/{tax_id}", status_code=status.HTTP_200_OK)
def delete_tax(
    tax_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        tax = db.query(models.Tax_type).filter(
            models.Tax_type.id == tax_id,
            models.Tax_type.company_id == company_id,
            models.Tax_type.status == CommonWords.STATUS
        ).first()

        if not tax:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax not found"
            )

        tax.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Tax deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

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
@router.get("/country_courrency", status_code=status.HTTP_200_OK)
def get_country_courrency(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        countries = (
            db.query(models.Country_Courrency)
            .filter(
                models.Country_Courrency.company_id == company_id,
                models.Country_Courrency.status == CommonWords.STATUS
            )
            .order_by(models.Country_Courrency.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": countries
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE COUNTRY & CURRENCY
# =====================================================
@router.post("/country_courrency", status_code=status.HTTP_201_CREATED)
async def create_country_courrency(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        country_name = payload.get("country_name")
        currency_name = payload.get("currency_name")
        symbol = payload.get("symbol")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([country_name, currency_name, symbol, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="country_name, currency_name, symbol, company_id and created_by are required"
            )

        exists = db.query(models.Country_Courrency).filter(
            func.lower(models.Country_Courrency.Country_Name) == country_name.lower(),
            models.Country_Courrency.company_id == company_id,
            models.Country_Courrency.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Country already exists"
            )

        country = models.Country_Courrency(
            Country_Name=country_name,
            Courrency_Name=currency_name,
            Symbol=symbol,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(country)
        db.commit()
        db.refresh(country)

        return {
            "status": "success",
            "message": "Country & currency created successfully",
            "data": country
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET COUNTRY & CURRENCY BY ID
# =====================================================
@router.get("/country_courrency/{country_id}", status_code=status.HTTP_200_OK)
def get_country_courrency_by_id(
    country_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        country = db.query(models.Country_Courrency).filter(
            models.Country_Courrency.id == country_id,
            models.Country_Courrency.company_id == company_id,
            models.Country_Courrency.status == CommonWords.STATUS
        ).first()

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        return {
            "status": "success",
            "data": country
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE COUNTRY & CURRENCY
# =====================================================
@router.put("/country_courrency", status_code=status.HTTP_200_OK)
async def update_country_courrency(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        country_id = payload.get("id")
        country_name = payload.get("country_name")
        currency_name = payload.get("currency_name")
        symbol = payload.get("symbol")
        company_id = payload.get("company_id")

        if not all([country_id, country_name, currency_name, symbol, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, country_name, currency_name, symbol and company_id are required"
            )

        duplicate = db.query(models.Country_Courrency).filter(
            models.Country_Courrency.id != country_id,
            func.lower(models.Country_Courrency.Country_Name) == country_name.lower(),
            models.Country_Courrency.company_id == company_id,
            models.Country_Courrency.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Country already exists"
            )

        country = db.query(models.Country_Courrency).filter(
            models.Country_Courrency.id == country_id,
            models.Country_Courrency.company_id == company_id,
            models.Country_Courrency.status == CommonWords.STATUS
        ).first()

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        country.Country_Name = country_name
        country.Courrency_Name = currency_name
        country.Symbol = symbol

        db.commit()
        db.refresh(country)

        return {
            "status": "success",
            "message": "Country & currency updated successfully",
            "data": country
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE COUNTRY & CURRENCY (SOFT DELETE)
# =====================================================
@router.delete("/country_courrency/{country_id}", status_code=status.HTTP_200_OK)
def delete_country_courrency(
    country_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        country = db.query(models.Country_Courrency).filter(
            models.Country_Courrency.id == country_id,
            models.Country_Courrency.company_id == company_id,
            models.Country_Courrency.status == CommonWords.STATUS
        ).first()

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        country.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Country & currency deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

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
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        complementries = (
            db.query(models.Room_Complementry)
            .filter(
                models.Room_Complementry.company_id == company_id,
                models.Room_Complementry.status == CommonWords.STATUS
            )
            .order_by(models.Room_Complementry.id.desc())
            .all()
        )

        return {
            "status": "success",
            "data": complementries
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# CREATE ROOM COMPLEMENTARY
# =====================================================
@router.post("/complementry", status_code=status.HTTP_201_CREATED)
async def create_room_complementry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        complementry_name = payload.get("complementry_name")
        description = payload.get("description")
        company_id = payload.get("company_id")
        created_by = payload.get("created_by")

        if not all([complementry_name, description, company_id, created_by]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="complementry_name, description, company_id and created_by are required"
            )

        exists = db.query(models.Room_Complementry).filter(
            func.lower(models.Room_Complementry.Complementry_Name) == complementry_name.lower(),
            models.Room_Complementry.company_id == company_id,
            models.Room_Complementry.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room complementry already exists"
            )

        complementry = models.Room_Complementry(
            Complementry_Name=complementry_name,
            Description=description,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(complementry)
        db.commit()
        db.refresh(complementry)

        return {
            "status": "success",
            "message": "Room complementry created successfully",
            "data": complementry
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# GET ROOM COMPLEMENTARY BY ID
# =====================================================
@router.get("/complementry/{complementry_id}", status_code=status.HTTP_200_OK)
def get_room_complementry_by_id(
    complementry_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        complementry = db.query(models.Room_Complementry).filter(
            models.Room_Complementry.id == complementry_id,
            models.Room_Complementry.company_id == company_id,
            models.Room_Complementry.status == CommonWords.STATUS
        ).first()

        if not complementry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room complementry not found"
            )

        return {
            "status": "success",
            "data": complementry
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# UPDATE ROOM COMPLEMENTARY
# =====================================================
@router.put("/complementry", status_code=status.HTTP_200_OK)
async def update_room_complementry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        complementry_id = payload.get("id")
        complementry_name = payload.get("complementry_name")
        description = payload.get("description")
        company_id = payload.get("company_id")

        if not all([complementry_id, complementry_name, description, company_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id, complementry_name, description and company_id are required"
            )

        duplicate = db.query(models.Room_Complementry).filter(
            models.Room_Complementry.id != complementry_id,
            func.lower(models.Room_Complementry.Complementry_Name) == complementry_name.lower(),
            models.Room_Complementry.company_id == company_id,
            models.Room_Complementry.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room complementry already exists"
            )

        complementry = db.query(models.Room_Complementry).filter(
            models.Room_Complementry.id == complementry_id,
            models.Room_Complementry.company_id == company_id,
            models.Room_Complementry.status == CommonWords.STATUS
        ).first()

        if not complementry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room complementry not found"
            )

        complementry.Complementry_Name = complementry_name
        complementry.Description = description

        db.commit()
        db.refresh(complementry)

        return {
            "status": "success",
            "message": "Room complementry updated successfully",
            "data": complementry
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

# =====================================================
# DELETE ROOM COMPLEMENTARY (SOFT DELETE)
# =====================================================
@router.delete("/complementry/{complementry_id}", status_code=status.HTTP_200_OK)
def delete_room_complementry(
    complementry_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        user_id, user_role, token = verify_authentication(request)
        complementry = db.query(models.Room_Complementry).filter(
            models.Room_Complementry.id == complementry_id,
            models.Room_Complementry.company_id == company_id,
            models.Room_Complementry.status == CommonWords.STATUS
        ).first()

        if not complementry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room complementry not found"
            )

        complementry.status = CommonWords.UNSTATUS
        db.commit()

        return {
            "status": "success",
            "message": "Room complementry deleted successfully"
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

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

from fastapi import APIRouter, Depends, status, HTTPException, Request,UploadFile,File,Form
from sqlalchemy.orm import Session
from datetime import datetime
from resources.utils import verify_authentication
from models import get_db, models
from configs.base_config import CommonWords
import os
import shutil
import uuid


router = APIRouter()


UPLOAD_DIR = "templates/static/room_incidents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/roomincident_log", status_code=status.HTTP_200_OK)
def get_roomincident_log(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        roomincidentlog = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .order_by(models.HousekeeperRoomIncident.id.desc())
            .all()
        )

        data = [
            {
                "id": roomincident.id,
                "room_no": roomincident.room_no,
                "incident_date": roomincident.incident_date,
                "incident_time": roomincident.incident_time,
                "incident_description": roomincident.incident_description,
                "involved_staff": roomincident.involved_staff,
                "severity": roomincident.severity,
                "witness": roomincident.witnesses,
                "actions_taken": roomincident.actions_taken,
                "reported_by": roomincident.reported_by,
                "report_date": roomincident.report_date,
                "attachment_file": roomincident.attachment_file,
            }
            for roomincident in roomincidentlog
        ]

        return {"status": "success", "count": len(data), "data": data}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/roomincident_log/{incident_id}", status_code=status.HTTP_200_OK)
def get_roomincident_log_by_id(
    incident_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        roomincident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .first()
        )

        if not roomincident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room incident log not found",
            )

        return {
            "status": "success",
            "data": {
                "id": roomincident.id,
                "room_no": roomincident.room_no,
                "incident_date": roomincident.incident_date,
                "incident_time": roomincident.incident_time,
                "incident_description": roomincident.incident_description,
                "involved_staff": roomincident.involved_staff,
                "severity": roomincident.severity,
                "witness": roomincident.witnesses,
                "actions_taken": roomincident.actions_taken,
                "reported_by": roomincident.reported_by,
                "report_date": roomincident.report_date,
                "attachment_file": roomincident.attachment_file, 
                "created_by": roomincident.created_by,
                "created_at": roomincident.created_at,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )




@router.post("/roomincident_log", status_code=status.HTTP_201_CREATED)
async def create_roomincidentlog(
    request: Request,
    room_no: str = Form(...),
    incident_date: str = Form(...),
    incident_time: str = Form(...),
    incident_description: str = Form(...),
    witness: str = Form(...),
    involved_staff: str = Form(None),
    severity: str = Form(None),
    actions_taken: str = Form(None),
    reported_by: str = Form(None),
    report_date: str = Form(None),
    attachment_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # -----------------------------
        # File upload handling
        # -----------------------------
        file_path = None
        if attachment_file:
            upload_dir = "uploads/room_incidents"
            os.makedirs(upload_dir, exist_ok=True)

            file_path = f"{upload_dir}/{attachment_file.filename}"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(attachment_file.file, buffer)

        roomincident = models.HousekeeperRoomIncident(
            room_no=room_no.strip(),
            incident_date=incident_date.strip(),
            incident_time=incident_time.strip(),
            incident_description=incident_description.strip(),
            involved_staff=involved_staff,
            severity=severity,
            witnesses=witness.strip(),
            actions_taken=actions_taken,
            reported_by=reported_by,
            report_date=report_date,
            attachment_file=file_path, 
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id,
        )

        db.add(roomincident)
        db.commit()
        db.refresh(roomincident)

        return {
            "status": "success",
            "message": "Room incident log created successfully",
            "data": {
                "id": roomincident.id,
                "room_no": roomincident.room_no,
                "incident_date": roomincident.incident_date,
                "incident_time": roomincident.incident_time,
                "incident_description": roomincident.incident_description,
                "attachment_file": roomincident.attachment_file,
                "created_at": roomincident.created_at,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/roomincident_log", status_code=status.HTTP_200_OK)
async def update_roomincidentlog(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body",
            )

        incident_id = payload.get("id")
        room_no = payload.get("room_no", "").strip()
        incident_date = payload.get("incident_date", "").strip()
        incident_time = payload.get("incident_time", "").strip()
        incident_description = payload.get("incident_description", "").strip()

        involved_staff = payload.get("involved_staff", "").strip() or None
        severity = payload.get("severity", "").strip() or None
        witnesses = payload.get("witness", "").strip() or None
        actions_taken = payload.get("actions_taken", "").strip() or None
        reported_by = payload.get("reported_by", "").strip() or None
        report_date = payload.get("report_date") or None
        attachment_file = payload.get("attachment_file", "").strip() or None

        if not incident_id or not isinstance(incident_id, int) or incident_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid room incident id is required",
            )

        if not room_no:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_no is required",
            )
        if not incident_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incident_date is required",
            )
        if not incident_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incident_time is required",
            )
        if not incident_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incident_description is required",
            )

        roomincident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .first()
        )

        if not roomincident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room incident log not found",
            )

        roomincident.room_no = room_no
        roomincident.incident_date = incident_date
        roomincident.incident_time = incident_time
        roomincident.incident_description = incident_description
        roomincident.involved_staff = involved_staff
        roomincident.severity = severity
        roomincident.witnesses = witnesses
        roomincident.actions_taken = actions_taken
        roomincident.reported_by = reported_by
        roomincident.report_date = report_date
        roomincident.attachment_file = attachment_file
        roomincident.company_id = company_id

        db.commit()
        db.refresh(roomincident)

        return {
            "status": "success",
            "message": "Room incident log updated successfully",
            "data": {
                "id": roomincident.id,
                "room_no": roomincident.room_no,
                "incident_date": roomincident.incident_date,
                "incident_time": roomincident.incident_time,
                "incident_description": roomincident.incident_description,
                "involved_staff": roomincident.involved_staff,
                "severity": roomincident.severity,
                "witness": roomincident.witnesses,
                "actions_taken": roomincident.actions_taken,
                "reported_by": roomincident.reported_by,
                "report_date": roomincident.report_date,
                "attachment_file": roomincident.attachment_file,
                "status": roomincident.status,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/roomincident_log/{incident_id}", status_code=status.HTTP_200_OK
)
def delete_roomincident_log(
    request: Request, incident_id: int, db: Session = Depends(get_db)
):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        roomincident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .first()
        )

        if not roomincident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room incident log not found",
            )

        roomincident.status = CommonWords.UNSTATUS
        roomincident.updated_by = user_id

        db.commit()

        return {
            "status": "success",
            "message": "Room incident log deleted successfully",
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    

from fastapi import APIRouter, Depends, status, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os, shutil, uuid

from models import models, get_db
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

UPLOAD_PATH = "templates/static/room_incidents"
os.makedirs(UPLOAD_PATH, exist_ok=True)


@router.get("/housekeeper_tasks", status_code=status.HTTP_200_OK)
def get_housekeeper_tasks(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        housekeepertasks = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .order_by(models.HousekeeperTask.id.desc())
            .all()
        )
        data = [
            {
                "id": housekeeper.id,
                "employee_id": housekeeper.employee_id,
                "first_name": housekeeper.first_name,
                "last_name": housekeeper.last_name,
                "schedule_date": housekeeper.schedule_date,
                "schedule_time": housekeeper.schedule_time,
                "room_no": housekeeper.room_no,
                "task_type": housekeeper.task_type,
                "assign_staff": housekeeper.assign_staff,
                "task_status": housekeeper.task_status,
                "room_status": housekeeper.room_status,
                "lost_found": housekeeper.lost_found,
                "special_instructions": housekeeper.special_instructions,
            }
            for housekeeper in housekeepertasks
        ]

        return {"status": "success", "count": len(data), "data": data}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/housekeeper_tasks", status_code=status.HTTP_201_CREATED)
async def create_housekeepertasks(request: Request, db: Session = Depends(get_db)):
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
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
            )

        first_name = payload.get("first_name", "").strip()
        last_name = payload.get("last_name", "").strip()
        room_no = payload.get("room_no","")
        assign_staff = payload.get("assign_staff", "").strip()
        schedule_date = payload.get("schedule_date").strip()
        schedule_time = payload.get("schedule_time").strip()

        employee_id = payload.get("employee_id", "").strip() or None
        task_status = payload.get("task_status", "").strip() or None

        task_type = payload.get("task_type", "").strip() or None
        lost_found = payload.get("lost_found", "").strip() or None
        room_status = payload.get("room_status", "").strip() or None
        special_instructions = payload.get("special_instructions", "").strip() or None

        if not first_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="first_name is required"
            )
        if not last_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="last_name is required"
            )
        if not room_no:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="room_no is required"
            )
        if not assign_staff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="assign_staff is required",
            )
        if not schedule_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schedule_date is required",
            )
        if not schedule_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schedule_time is required",
            )

        housekeeper_tasks = models.HousekeeperTask(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            schedule_date=schedule_date,
            schedule_time=schedule_time,
            room_no=room_no,
            room_status=room_status,
            task_status=task_status,
            task_type=task_type,
            assign_staff=assign_staff,
            lost_found=lost_found,
            special_instructions=special_instructions,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id,
        )

        db.add(housekeeper_tasks)
        db.commit()
        db.refresh(housekeeper_tasks)

        return {
            "status": "success",
            "message": "Housekeeper Tasks created successfully",
            "data": {
                "id": housekeeper_tasks.id,
                "employee_id": housekeeper_tasks.employee_id,
                "first_name": housekeeper_tasks.first_name,
                "last_name": housekeeper_tasks.last_name,
                "schedule_date": housekeeper_tasks.schedule_date,
                "schedule_time": housekeeper_tasks.schedule_time,
                "room_no": housekeeper_tasks.room_no,
                "room_status": housekeeper_tasks.room_status,
                "task_status": housekeeper_tasks.task_status,
                "task_type": housekeeper_tasks.task_type,
                "assign_staff": housekeeper_tasks.assign_staff,
                "lost_found": housekeeper_tasks.lost_found,
                "special_instructions": housekeeper_tasks.special_instructions,
                "created_by": housekeeper_tasks.created_by,
                "created_at": housekeeper_tasks.created_at,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/housekeeper_tasks/{task_id}", status_code=status.HTTP_200_OK)
def gethousekeeper_task_id(
    task_id: int, request: Request, db: Session = Depends(get_db)
):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task_id"
            )
        housekeeper = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.id == task_id,
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .first()
        )

        if not housekeeper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Housekeeper task not found",
            )

        data = {
            "id": housekeeper.id,
            "employee_id": housekeeper.employee_id,
            "first_name": housekeeper.first_name,
            "last_name": housekeeper.last_name,
            "schedule_date": housekeeper.schedule_date,
            "schedule_time": housekeeper.schedule_time,
            "room_no": housekeeper.room_no,
            "task_type": housekeeper.task_type,
            "assign_staff": housekeeper.assign_staff,
            "task_status": housekeeper.task_status,
            "room_status": housekeeper.room_status,
            "lost_found": housekeeper.lost_found,
            "special_instructions": housekeeper.special_instructions,
            "created_by": housekeeper.created_by,
            "created_at": housekeeper.created_at,
            "updated_at": housekeeper.updated_at,
            "company_id": housekeeper.company_id,
        }

        return {"status": "success", "data": data}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/housekeeper_tasks", status_code=status.HTTP_200_OK)
async def update_inquiry(request: Request, db: Session = Depends(get_db)):
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
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
            )

        housekeepertasks_id = payload.get("id")
        first_name = payload.get("first_name", "").strip()
        last_name = payload.get("last_name", "").strip()
        room_no = payload.get("room_no")
        assign_staff = payload.get("assign_staff", "").strip()
        schedule_date = payload.get("schedule_date")
        schedule_time = payload.get("schedule_time")

        employee_id = payload.get("employee_id", "").strip() or None
        task_status = payload.get("task_status", "").strip() or None

        task_type = payload.get("task_type", "").strip() or None
        lost_found = payload.get("lost_found", "").strip() or None
        room_status = payload.get("room_status", "").strip() or None
        special_instructions = payload.get("special_instructions", "").strip() or None

        if (
            not housekeepertasks_id
            or not isinstance(housekeepertasks_id, int)
            or housekeepertasks_id <= 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid Housekeeper Tasks id is required",
            )

        if not first_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="first_name is required"
            )
        if not last_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="last_name is required"
            )
        if not room_no:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="room_no is required"
            )
        if not assign_staff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="assign_staff is required",
            )
        if not schedule_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schedule_date is required",
            )
        if not schedule_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schedule_time is required",
            )

        housekeeper_tasks = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.id == housekeepertasks_id,
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .first()
        )

        if not housekeeper_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="housekeeper_tasks not found"
            )

        housekeeper_tasks.first_name = first_name
        housekeeper_tasks.last_name = last_name
        housekeeper_tasks.schedule_date = schedule_date
        housekeeper_tasks.schedule_time = schedule_time
        housekeeper_tasks.room_no = room_no
        housekeeper_tasks.room_status = room_status
        housekeeper_tasks.task_status = task_status
        housekeeper_tasks.task_type = task_type
        housekeeper_tasks.assign_staff = assign_staff
        housekeeper_tasks.lost_found = lost_found
        housekeeper_tasks.special_instructions = special_instructions
        housekeeper_tasks.company_id = company_id

        db.commit()
        db.refresh(housekeeper_tasks)

        return {
            "status": "success",
            "message": "Housekeeper task updated successfully",
            "data": {
                "id": housekeeper_tasks.id,
                "employee_id": housekeeper_tasks.employee_id,
                "first_name": housekeeper_tasks.first_name,
                "last_name": housekeeper_tasks.last_name,
                "schedule_date": housekeeper_tasks.schedule_date,
                "schedule_time": housekeeper_tasks.schedule_time,
                "room_no": housekeeper_tasks.room_no,
                "room_status": housekeeper_tasks.room_status,
                "task_status": housekeeper_tasks.task_status,
                "task_type": housekeeper_tasks.task_type,
                "assign_staff": housekeeper_tasks.assign_staff,
                "lost_found": housekeeper_tasks.lost_found,
                "special_instructions": housekeeper_tasks.special_instructions,
                "status": housekeeper_tasks.status,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/housekeeper_tasks/{housekeepertasks_id}", status_code=status.HTTP_200_OK
)
def delete_housekeeper_tasks(
    request: Request, housekeepertasks_id: int, db: Session = Depends(get_db)
):
    try:
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        housekeeper_tasks = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.id == housekeepertasks_id,
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .first()
        )

        if not housekeeper_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="housekeeper_tasks not found"
            )
        housekeeper_tasks.status = CommonWords.UNSTATUS
        housekeeper_tasks.updated_by = user_id

        db.commit()

        return {"status": "success", "message": "housekeeper_tasks deleted successfully"}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# =====================================================
# CREATE HOUSEKEEPER ROOM INCIDENT
# =====================================================
@router.post("/roomincident_log", status_code=status.HTTP_201_CREATED)
async def create_roomincident_log(
    request: Request,

    # ---- REQUIRED ----
    room_id: int = Form(...),                       # master room table id
    incident_date: str = Form(...),                 # YYYY-MM-DD
    incident_time: str = Form(...),                 # HH:MM:SS
    incident_description: str = Form(...),

    # ---- OPTIONAL ----
    involved_staff: str = Form(None),
    severity: str = Form(None),
    witnesses: str = Form(None),
    actions_taken: str = Form(None),
    reported_by: str = Form(None),
    report_date: str = Form(None),                  # YYYY-MM-DD
    attachment_file: UploadFile = File(None),

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
        # FILE UPLOAD (OPTIONAL)
        # -------------------------------------------------
        file_path = None
        if attachment_file:
            extension = attachment_file.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{extension}"
            file_path = os.path.join(UPLOAD_PATH, filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(attachment_file.file, buffer)

        # -------------------------------------------------
        # CREATE INCIDENT RECORD
        # -------------------------------------------------
        incident = models.HousekeeperRoomIncident(
            room_no=room_id,  # ✅ storing master DB room id
            incident_date=datetime.strptime(incident_date, "%Y-%m-%d").date(),
            incident_time=datetime.strptime(incident_time, "%H:%M").time(),
            incident_description=incident_description.strip(),

            involved_staff=involved_staff,
            severity=severity,
            witnesses=witnesses,
            actions_taken=actions_taken,
            reported_by=reported_by,
            report_date=datetime.strptime(report_date, "%Y-%m-%d").date() if report_date else None,

            attachment_file=file_path,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room incident created successfully",
            "data": {
                "id": incident.id,
                "room_id": incident.room_no,
                "incident_date": incident.incident_date,
                "incident_time": incident.incident_time,
                "severity": incident.severity,
                "attachment_file": incident.attachment_file,
                "created_at": incident.created_at
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
# GET ALL HOUSEKEEPER ROOM INCIDENTS
# =====================================================
@router.get("/roomincident_log", status_code=status.HTTP_200_OK)
def get_all_roomincident_logs(
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
        # FETCH INCIDENTS
        # -------------------------------------------------
        incidents = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS
            )
            .order_by(models.HousekeeperRoomIncident.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": incident.id,
                "room_id": incident.room_no,                 # master DB room id
                "incident_date": incident.incident_date,
                "incident_time": incident.incident_time,
                "incident_description": incident.incident_description,
                "involved_staff": incident.involved_staff,
                "severity": incident.severity,
                "witnesses": incident.witnesses,
                "actions_taken": incident.actions_taken,
                "reported_by": incident.reported_by,
                "report_date": incident.report_date,
                "attachment_file": incident.attachment_file,
                "created_by": incident.created_by,
                "created_at": incident.created_at
            }
            for incident in incidents
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
# GET HOUSEKEEPER ROOM INCIDENT BY ID
# =====================================================
@router.get("/roomincident_log/{incident_id}", status_code=status.HTTP_200_OK)
def get_roomincident_log_by_id(
    request: Request,
    incident_id: int,
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
        if incident_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid incident_id"
            )

        # -------------------------------------------------
        # FETCH INCIDENT
        # -------------------------------------------------
        incident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS
            )
            .first()
        )

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room incident not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": incident.id,
                "room_id": incident.room_no,             # master DB room id
                "incident_date": incident.incident_date,
                "incident_time": incident.incident_time,
                "incident_description": incident.incident_description,
                "involved_staff": incident.involved_staff,
                "severity": incident.severity,
                "witnesses": incident.witnesses,
                "actions_taken": incident.actions_taken,
                "reported_by": incident.reported_by,
                "report_date": incident.report_date,
                "attachment_file": incident.attachment_file,
                "created_by": incident.created_by,
                "created_at": incident.created_at,
                "updated_at": incident.updated_at
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
# UPDATE HOUSEKEEPER ROOM INCIDENT
# =====================================================
@router.put("/roomincident_log", status_code=status.HTTP_200_OK)
async def update_roomincident_log(
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
        # REQUEST BODY (JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------
        incident_id = payload.get("id")
        room_id = payload.get("room_id")
        incident_date = payload.get("incident_date")
        incident_time = payload.get("incident_time")
        incident_description = payload.get("incident_description")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not incident_id or not isinstance(incident_id, int) or incident_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid incident id is required"
            )

        if not room_id or not isinstance(room_id, int) or room_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid room_id is required"
            )

        if not incident_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incident_date is required"
            )

        if not incident_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incident_time is required"
            )

        if not incident_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incident_description is required"
            )

        # -------------------------------------------------
        # FETCH INCIDENT
        # -------------------------------------------------
        incident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS
            )
            .first()
        )

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room incident not found"
            )

        # -------------------------------------------------
        # UPDATE FIELDS
        # -------------------------------------------------
        incident.room_no = room_id
        incident.incident_date = datetime.strptime(incident_date, "%Y-%m-%d").date()
        incident.incident_time = datetime.strptime(incident_time, "%H:%M:%S").time()
        incident.incident_description = incident_description.strip()

        incident.involved_staff = payload.get("involved_staff")
        incident.severity = payload.get("severity")
        incident.witnesses = payload.get("witnesses")
        incident.actions_taken = payload.get("actions_taken")
        incident.reported_by = payload.get("reported_by")

        report_date = payload.get("report_date")
        incident.report_date = (
            datetime.strptime(report_date, "%Y-%m-%d").date()
            if report_date else None
        )

        incident.updated_by = user_id

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------
        db.commit()
        db.refresh(incident)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room incident updated successfully",
            "data": {
                "id": incident.id,
                "room_id": incident.room_no,
                "incident_date": incident.incident_date,
                "incident_time": incident.incident_time,
                "incident_description": incident.incident_description,
                "severity": incident.severity,
                "updated_at": incident.updated_at
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
# DELETE HOUSEKEEPER ROOM INCIDENT (SOFT DELETE)
# =====================================================
@router.delete("/roomincident_log/{incident_id}", status_code=status.HTTP_200_OK)
def delete_roomincident_log(
    request: Request,
    incident_id: int,
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
        if incident_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid incident_id"
            )

        # -------------------------------------------------
        # FETCH INCIDENT
        # -------------------------------------------------
        incident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS
            )
            .first()
        )

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room incident not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        incident.status = CommonWords.UNSTATUS
        incident.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room incident deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
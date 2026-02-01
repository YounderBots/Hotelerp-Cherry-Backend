from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from resources.utils import verify_authentication
from models import get_db, models
from configs.base_config import CommonWords

router = APIRouter()

# =====================================================
# CREATE HOUSEKEEPER TASK
# =====================================================
@router.post("/housekeeper_tasks", status_code=status.HTTP_201_CREATED)
async def create_housekeeper_task(
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

        # -------------------------------------------------
        # DATE & TIME CONVERSION
        # -------------------------------------------------
        try:
            schedule_date = datetime.strptime(
                payload.get("schedule_date"), "%Y-%m-%d"
            ).date()

            schedule_time = datetime.strptime(
                payload.get("schedule_time"), "%H:%M:%S"
            ).time()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schedule_date must be YYYY-MM-DD and schedule_time must be HH:MM:SS"
            )

        # -------------------------------------------------
        # PAYLOAD VALUES
        # -------------------------------------------------
        employee_id = payload.get("employee_id")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        room_no = payload.get("room_no")
        task_type = payload.get("task_type")
        assign_staff = payload.get("assign_staff")
        task_status = payload.get("task_status")
        room_status = payload.get("room_status")
        lost_found = payload.get("lost_found")
        special_instructions = payload.get("special_instructions")

        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------
        if not all([
            employee_id,
            first_name,
            last_name,
            room_no,
            task_type,
            assign_staff,
            task_status,
            room_status
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All required fields must be provided"
            )

        # -------------------------------------------------
        # VALIDATE ROOM
        # -------------------------------------------------
        room = db.query(models.Room).filter(
            models.Room.id == room_no,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        # -------------------------------------------------
        # VALIDATE EMPLOYEE
        # -------------------------------------------------
        employee = db.query(models.Users).filter(
            models.Users.id == employee_id,
            models.Users.company_id == company_id,
            models.Users.status == CommonWords.STATUS
        ).first()

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # -------------------------------------------------
        # VALIDATE ASSIGNED STAFF
        # -------------------------------------------------
        staff = db.query(models.Users).filter(
            models.Users.id == assign_staff,
            models.Users.company_id == company_id,
            models.Users.status == CommonWords.STATUS
        ).first()

        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned staff not found"
            )

        # -------------------------------------------------
        # VALIDATE TASK TYPE
        # -------------------------------------------------
        task = db.query(models.Task_Type).filter(
            models.Task_Type.id == task_type,
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task type not found"
            )

        # -------------------------------------------------
        # CREATE TASK
        # -------------------------------------------------
        new_task = models.HousekeeperTask(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            schedule_date=schedule_date,
            schedule_time=schedule_time,
            room_no=room_no,
            task_type=task_type,
            assign_staff=assign_staff,
            task_status=task_status,
            room_status=room_status,
            lost_found=lost_found,
            special_instructions=special_instructions,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Housekeeper task created successfully",
            "data": {
                "id": new_task.id,
                "room_id": room.id,
                "room_name": room.Room_Name,
                "employee_id": employee.id,
                "assigned_staff": staff.id,
                "task_type": task.Type_Name,
                "task_status": new_task.task_status,
                "schedule_date": str(new_task.schedule_date),
                "schedule_time": str(new_task.schedule_time)
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

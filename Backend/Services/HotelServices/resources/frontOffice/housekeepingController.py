from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session 

from resources.utils import verify_authentication
from models import models
from models import get_db
from configs.base_config import CommonWords


router = APIRouter()

# =====================================================
# CREATE HOUSEKEEPER TASK (ASSIGN TASK)
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
        # REQUEST BODY (SAFE JSON)
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
        required_fields = [
            "employee_id",
            "first_name",
            "last_name",
            "schedule_date",
            "schedule_time",
            "room_no",
            "task_type",
            "task_status",
            "room_status"
        ]

        for field in required_fields:
            if not payload.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field} is required"
                )

        # -------------------------------------------------
        # CREATE TASK
        # -------------------------------------------------
        task = models.HousekeeperTask(
            employee_id=payload.get("employee_id"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),

            schedule_date=payload.get("schedule_date"),
            schedule_time=payload.get("schedule_time"),

            room_no=payload.get("room_no"),
            task_type=payload.get("task_type"),           # Cleaning | Inspection | Maintenance
            assign_staff=payload.get("assign_staff"),
            task_status=payload.get("task_status"),       # Pending | In-Progress | Completed
            room_status=payload.get("room_status"),       # Clean | Dirty | Out of Order

            lost_found=payload.get("lost_found"),
            special_instructions=payload.get("special_instructions"),

            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Housekeeper task assigned successfully",
            "data": {
                "id": task.id,
                "employee_id": task.employee_id,
                "room_no": task.room_no,
                "task_type": task.task_type,
                "task_status": task.task_status,
                "schedule_date": task.schedule_date,
                "schedule_time": task.schedule_time,
                "created_at": task.created_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

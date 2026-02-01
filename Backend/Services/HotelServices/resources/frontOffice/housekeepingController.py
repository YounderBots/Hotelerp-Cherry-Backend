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
        # REQUEST BODY
        # -------------------------------------------------
        payload = await request.json()

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------
        required_fields = [
            "employee_id",      # ✅ users.id
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
            if payload.get(field) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field} is required"
                )

        # -------------------------------------------------
        # VALIDATE EMPLOYEE (USERS TABLE)
        # -------------------------------------------------
        employee = (
            db.query(models.Users)
            .filter(
                models.Users.id == payload["employee_id"],
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS
            )
            .first()
        )

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # -------------------------------------------------
        # CREATE TASK
        # -------------------------------------------------
        task = models.HousekeeperTask(
            employee_id=str(employee.id),   # ✅ STORE users.id
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),

            schedule_date=payload.get("schedule_date"),
            schedule_time=payload.get("schedule_time"),

            room_no=payload.get("room_no"),
            task_type=payload.get("task_type"),
            assign_staff=payload.get("assign_staff"),
            task_status=payload.get("task_status"),
            room_status=payload.get("room_status"),

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
                "employee_id": employee.id,
                "employee_name": f"{employee.First_Name} {employee.Last_Name}",
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
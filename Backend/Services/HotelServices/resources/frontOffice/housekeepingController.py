from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from resources.utils import verify_authentication
from models import get_db, models
from configs.base_config import CommonWords

router = APIRouter()


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

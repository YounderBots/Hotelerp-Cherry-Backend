# =============================== House Keeping – HSK Task List  

from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime

from models import get_db, models
from configs.base_config import BaseConfig, CommonWords

router = APIRouter()


@router.get("/hsk_task", status_code=status.HTTP_200_OK)
async def get_hsk_tasks(
    request: Request,
    db: Session = Depends(get_db)
):
    # ---------------- Session Validation ----------------
    if "sessid" not in request.session:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    try:
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        if not created_by or not company_id:
            return RedirectResponse(
                CommonWords.LOGINER_URL,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )

        # ---------------- Master Data ----------------
        rooms = db.query(models.Room).filter(
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).all()

        task_types = db.query(models.Task_Type).filter(
            models.Task_Type.company_id == company_id,
            models.Task_Type.status == CommonWords.STATUS
        ).all()

        housekeepers = db.query(models.Employee_Data).filter(
            models.Employee_Data.company_id == company_id,
            models.Employee_Data.Role_id == CommonWords.HouseKeeper_RoleID,
            models.Employee_Data.status == CommonWords.STATUS
        ).all()

        employees = db.query(models.Employee_Data).filter(
            models.Employee_Data.company_id == company_id,
            models.Employee_Data.Role_id != CommonWords.HouseKeeper_RoleID,
            models.Employee_Data.status == CommonWords.STATUS
        ).all()

        # ---------------- HSK Tasks ----------------
        tasks = db.query(models.Housekeeper_Task).filter(
            models.Housekeeper_Task.company_id == company_id,
            models.Housekeeper_Task.status == CommonWords.STATUS
        ).order_by(models.Housekeeper_Task.id.desc()).all()

        task_list = []
        for t in tasks:
            staff = db.query(models.Employee_Data).filter(
                models.Employee_Data.id == t.Assign_Staff,
                models.Employee_Data.status == CommonWords.STATUS
            ).first()

            room = db.query(models.Room).filter(
                models.Room.id == t.Room_No,
                models.Room.status == CommonWords.STATUS
            ).first()

            task_type = db.query(models.Task_Type).filter(
                models.Task_Type.id == t.Task_Type,
                models.Task_Type.status == CommonWords.STATUS
            ).first()

            task_list.append({
                "id": t.id,
                "employee_id": t.Employee_ID,
                "room_id": t.Room_No,
                "room_no": room.Room_No if room else None,
                "task_type_id": t.Task_Type,
                "task_type": task_type.Type_Name if task_type else None,
                "task_color": task_type.Color if task_type else None,
                "assign_staff_id": t.Assign_Staff,
                "assign_staff_name": f"{staff.First_Name} {staff.Last_Name}" if staff else None,
                "task_status": t.Task_Status,
                "room_status": t.Room_Status,
                "scheduled_date": t.Sch_Date.strftime("%Y-%m-%d") if t.Sch_Date else None,
                "scheduled_time": t.Sch_Time.strftime("%H:%M") if t.Sch_Time else None,
                "special_instructions": t.Special_Instructions
            })

        # ---------------- Response ----------------
        return JSONResponse(
            content={
                "status": "success",
                "meta": {
                    "today_date": datetime.today().strftime("%Y-%m-%d"),
                    "today_time": datetime.today().strftime("%H:%M")
                },
                "masters": {
                    "rooms": rooms,
                    "task_types": task_types,
                    "housekeepers": housekeepers,
                    "employees": employees
                },
                "tasks": task_list
            },
            status_code=status.HTTP_200_OK
        )

    except JWTError:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# =============================== Get Employee Details

@router.get("/get-employee-details/{emp_id}", status_code=status.HTTP_200_OK)
async def get_employee_details(
    request: Request,
    emp_id: int,
    db: Session = Depends(get_db)
):
    # ---------- Session Check ----------
    if "sessid" not in request.session:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    try:
        # ---------- JWT Decode ----------
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        if not created_by or not company_id:
            return RedirectResponse(
                CommonWords.LOGINER_URL,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )

        # ---------- Fetch Employee ----------
        emp_data = db.query(models.Employee_Data).filter(
            models.Employee_Data.id == emp_id,
            models.Employee_Data.company_id == company_id,
            models.Employee_Data.status == CommonWords.STATUS
        ).first()

        if not emp_data:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Employee not found"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        # ---------- Response ----------
        return JSONResponse(
            content={
                "status": "success",
                "data": jsonable_encoder(emp_data)
            },
            status_code=status.HTTP_200_OK
        )

    except JWTError:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# =============================== Add Housekeeper Task

@router.post("/housekeeper_task", status_code=status.HTTP_200_OK)
async def add_housekeeper_task(
    request: Request,
    emps_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    sch_date: str = Form(...),
    sch_time: str = Form(...),
    room_status: str = Form(...),
    room_number: int = Form(...),
    task_type: str = Form(...),
    assign_staff: str = Form(...),
    task_status: str = Form(...),
    notes: str = Form(...),
    lost_found: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # ---------- Session Check ----------
    if "sessid" not in request.session:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    try:
        # ---------- JWT Decode ----------
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        if not created_by or not company_id:
            return RedirectResponse(
                CommonWords.LOGINER_URL,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )

        # ---------- Validate Room ----------
        room = db.query(models.Room).filter(
            models.Room.id == room_number,
            models.Room.company_id == company_id,
            models.Room.status == CommonWords.STATUS
        ).first()

        if not room:
            return JSONResponse(
                content={"status": "error", "message": "Room not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        # ---------- Duplicate Check ----------
        duplicate = db.query(models.Housekeeper_Task).filter(
            models.Housekeeper_Task.Employee_ID == emps_id,
            models.Housekeeper_Task.Sch_Date == sch_date,
            models.Housekeeper_Task.Sch_Time == sch_time,
            models.Housekeeper_Task.Room_No == room_number,
            models.Housekeeper_Task.Task_Type == task_type,
            models.Housekeeper_Task.company_id == company_id,
            models.Housekeeper_Task.status == CommonWords.STATUS
        ).first()

        if duplicate:
            return JSONResponse(
                content={"status": "error", "message": "Task already assigned"},
                status_code=status.HTTP_409_CONFLICT
            )

        # ---------- Create Task ----------
        housekeeper_task = models.Housekeeper_Task(
            Employee_ID=emps_id,
            First_Name=first_name,
            Sur_Name=last_name,
            Sch_Date=sch_date,
            Sch_Time=sch_time,
            Room_No=room_number,
            Task_Type=task_type,
            Assign_Staff=assign_staff,
            Task_Status=task_status,
            Room_Status=room_status,
            Lost_Found=lost_found or "",
            Special_Instructions=notes,
            status=CommonWords.STATUS,
            created_by=created_by,
            company_id=company_id
        )

        db.add(housekeeper_task)
        db.commit()
        db.refresh(housekeeper_task)

        # ---------- Update Room Status ----------
        db.query(models.Room).filter(
            models.Room.id == room_number,
            models.Room.company_id == company_id
        ).update({
            "Room_Status": room_status,
            "Room_Booking_status": task_type
        })

        db.commit()

        # ---------- Response ----------
        return JSONResponse(
            content={"status": "success", "message": "Housekeeper task created successfully"},
            status_code=status.HTTP_200_OK
        )

    except JWTError:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# =============================== Get Housekeeper Task By ID

@router.get("/housekeepertask_id/{housekeeper_id}", status_code=status.HTTP_200_OK)
async def housekeepertask_id_taking(
    request: Request,
    housekeeper_id: int,
    db: Session = Depends(get_db)
):
    # ---------- Session Validation ----------
    if "sessid" not in request.session:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    try:
        # ---------- JWT Decode ----------
        payload = jwt.decode(
            request.session["sessid"],
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        company_id = payload.get("company_id")

        if not created_by or not company_id:
            return RedirectResponse(
                CommonWords.LOGINER_URL,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )

        # ---------- Fetch Task ----------
        housekeeper_task = db.query(models.Housekeeper_Task).filter(
            models.Housekeeper_Task.id == housekeeper_id,
            models.Housekeeper_Task.company_id == company_id,
            models.Housekeeper_Task.status == CommonWords.STATUS
        ).first()

        if not housekeeper_task:
            return JSONResponse(
                content={"status": "error", "message": "Housekeeper task not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        # ---------- Response ----------
        return JSONResponse(
            content={
                "status": "success",
                "data": jsonable_encoder(housekeeper_task)
            },
            status_code=status.HTTP_200_OK
        )

    except JWTError:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


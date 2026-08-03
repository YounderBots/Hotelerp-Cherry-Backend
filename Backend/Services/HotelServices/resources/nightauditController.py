import io
import pandas as pd
from fastapi import APIRouter, Depends, Request, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from jose import JWTError
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, timedelta
import datetime as dt

from models import get_db, models
from configs.base_config import BaseConfig, CommonWords
from fastapi import HTTPException


router = APIRouter()

#=====================================>>> User Activity Log

@router.get("/user_activity_log", status_code=status.HTTP_200_OK)
def user_activity_log(
    company_id: str,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # -------------------------------
    # Date validation (EXACT logic)
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Room Reservation Activity
    # -------------------------------
    room_data = (
        db.query(models.RoomReservation)
        .filter(
            models.RoomReservation.company_id == company_id,
            models.RoomReservation.arrival_date.between(from_date, to_date)
        )
        .all()
    )

    formatted_room_data = [
        {
            "id": r.id,
            "room_no": ", ".join(str(n) for n in r.room_no) if isinstance(r.room_no, list) else r.room_no,
            "reservation_id": r.room_reservation_id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "phone": r.phone_number,
            "email": r.email,
            "arrival_date": r.arrival_date,
            "departure_date": r.departure_date,
            "booking_status": r.reservation_status,
        }
        for r in room_data
    ]

    # -------------------------------
    # Housekeeping / Staff Activity
    # (HousekeeperTask already carries staff name + task type inline —
    # Employee_Data/Task_Type are separate microservices, not joinable here)
    # -------------------------------
    keeper_data = (
        db.query(models.HousekeeperTask)
        .filter(
            models.HousekeeperTask.company_id == company_id,
            models.HousekeeperTask.schedule_date.between(from_date, to_date)
        )
        .all()
    )

    formatted_keeper_data = [
        {
            "id": k.id,
            "employee_id": k.employee_id,
            "employee_name": f"{k.first_name} {k.last_name}",
            "room_no": k.room_no,
            "task_type": k.task_type,
            "task_status": k.task_status
        }
        for k in keeper_data
    ]

    # -------------------------------
    # Final Response
    # -------------------------------
    return {
        "status": "success",
        "filters": {
            "from_date": from_date,
            "to_date": to_date
        },
        "data": {
            "room_activity": formatted_room_data,
            "housekeeping_activity": formatted_keeper_data
        }
    }

#=====================================>>> Reservation Info

@router.get("/reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def get_reservation_info(
    reservation_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    reservation = db.query(models.RoomReservation).filter(
        models.RoomReservation.id == reservation_id,
        models.RoomReservation.company_id == company_id
    ).first()

    if not reservation:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Reservation not found"
            },
            status_code=404
        )

    return {
        "status": "success",
        "data": jsonable_encoder(reservation)
    }

#=====================================>>> Keeper Info

@router.get("/keeper_info/{task_id}", status_code=status.HTTP_200_OK)
def keeper_info(
    task_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    keeper = (
        db.query(models.HousekeeperTask)
        .filter(
            models.HousekeeperTask.id == task_id,
            models.HousekeeperTask.company_id == company_id
        )
        .first()
    )

    if not keeper:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Keeper info not found"
            },
            status_code=404
        )

    formatted_keeper_info = {
        "id": keeper.id,
        "employee_id": keeper.employee_id,
        "employee_name": f"{keeper.first_name} {keeper.last_name}",
        "room_no": keeper.room_no,
        "task_type": keeper.task_type,
        "task_status": keeper.task_status,
        "schedule_date": keeper.schedule_date,
        "schedule_time": keeper.schedule_time,
        "room_status": keeper.room_status,
        "special_instructions": keeper.special_instructions,
        "status": keeper.status
    }

    return {
        "status": "success",
        "data": formatted_keeper_info
    }

#=====================================>>> Get Paid Amount

@router.get("/paid_amount", status_code=status.HTTP_200_OK)
def get_paid_amount(
    company_id: str,
    db: Session = Depends(get_db)
):
    today = date.today()

    total_paid_amount = db.query(
        func.coalesce(func.sum(models.RoomReservation.paid_amount), 0)
    ).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.arrival_date == today
    ).scalar()

    return {
        "status": "success",
        "date": today,
        "total_paid_amount": float(total_paid_amount)
    }

#=====================================>>> Settlement Summary

@router.get("/settlement_summary", status_code=status.HTTP_200_OK)
def settlement_summary(
    company_id: str,
    db: Session = Depends(get_db)
):
    current_date = date.today()

    # Room reservation list for today
    room_data = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.arrival_date == current_date
    ).all()

    # Total paid amount
    total_paid = db.query(
        func.coalesce(func.sum(models.RoomReservation.paid_amount), 0)
    ).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.arrival_date == current_date
    ).scalar()

    # Total due amount
    total_due = db.query(
        func.coalesce(func.sum(models.RoomReservation.balance_amount), 0)
    ).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.arrival_date == current_date
    ).scalar()

    return {
        "status": "success",
        "date": current_date,
        "summary": {
            "total_paid": float(total_paid),
            "total_due": float(total_due)
        },
        "data": jsonable_encoder(room_data)
    }

#=====================================>>> Room Sales (REACT API)

@router.get("/room_sales", status_code=status.HTTP_200_OK)
def room_sales(
    company_id: str,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # -------------------------------
    # Date validation (same logic)
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Room sales data
    # -------------------------------
    room_data = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.status == CommonWords.STATUS,
        models.RoomReservation.arrival_date.between(from_date, to_date)
    ).order_by(
        models.RoomReservation.arrival_date
    ).all()

    return {
        "status": "success",
        "filters": {
            "from_date": from_date,
            "to_date": to_date
        },
        "data": jsonable_encoder(room_data)
    }

#-------------- Night Auditing Export -------------------------------
#-------------- User Activity Log  ------------------------

@router.get("/export_user_activity", status_code=status.HTTP_200_OK)
def export_user_activity(
    company_id: str,
    db: Session = Depends(get_db),
    format: str = Query("excel", enum=["excel", "json"]),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None)
):
    # -------------------------------
    # Date validation (exact logic)
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Fetch reservation data
    # -------------------------------
    reservations = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        (
            models.RoomReservation.arrival_date.between(from_date, to_date)
        ) | (
            models.RoomReservation.departure_date.between(from_date, to_date)
        )
    ).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for reservation in reservations:
        full_name = f"{reservation.first_name} {reservation.last_name}"
        data.append({
            "Reservation ID": reservation.room_reservation_id,
            "Guest Name": full_name,
            "Phone Number": reservation.phone_number,
            "Arrival Date": reservation.arrival_date,
            "Departure Date": reservation.departure_date,
            "Booking Status": reservation.reservation_status
        })

    df = pd.DataFrame(data)

    # -------------------------------
    # Excel Export
    # -------------------------------
    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="User Activity Log")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=User_Activity_Log.xlsx"
            }
        )

    # -------------------------------
    # JSON Export
    # -------------------------------
    json_data = df.to_json(orient="records", date_format="iso")

    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=User_Activity_Log.json"
        }
    )

#-------------- Room Booked Details Export ----------------

@router.get("/export_room_booked_details", status_code=status.HTTP_200_OK)
def export_room_booked_details(
    company_id: str,
    db: Session = Depends(get_db),
    format: str = Query("excel", enum=["excel", "json"]),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None)
):
    # -------------------------------
    # Date validation
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Fetch reservation data
    # -------------------------------
    reservations = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.arrival_date.between(from_date, to_date)
    ).order_by(models.RoomReservation.arrival_date.asc()).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for reservation in reservations:
        full_name = f"{reservation.first_name} {reservation.last_name}"
        data.append({
            "Reservation ID": reservation.room_reservation_id,
            "Guest Name": full_name,
            "Phone Number": reservation.phone_number,
            "Arrival Date": reservation.arrival_date,
            "Departure Date": reservation.departure_date,
            "Booking Status": reservation.reservation_status
        })

    df = pd.DataFrame(data)

    # -------------------------------
    # Excel Export
    # -------------------------------
    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Room Booked Details")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=Room_Booked_Details.xlsx"
            }
        )

    # -------------------------------
    # JSON Export
    # -------------------------------
    json_data = df.to_json(orient="records", date_format="iso")

    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=Room_Booked_Details.json"
        }
    )

#-------------- HSK Task Details Export ----------------

@router.get("/export_hsk_details", status_code=status.HTTP_200_OK)
def export_hsk_details(
    company_id: str,
    db: Session = Depends(get_db),
    format: str = Query("excel", enum=["excel", "json"]),
    sch_date: Optional[str] = Query(None)
):
    # -------------------------------
    # Date validation
    # -------------------------------
    if sch_date:
        try:
            sch_date = dt.datetime.strptime(sch_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        sch_date = date.today()

    # -------------------------------
    # Fetch HSK task data
    # -------------------------------
    hsk_tasks = db.query(models.HousekeeperTask).filter(
        models.HousekeeperTask.company_id == company_id,
        models.HousekeeperTask.schedule_date == sch_date
    ).order_by(models.HousekeeperTask.room_no.asc()).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for task in hsk_tasks:
        full_name = f"{task.first_name} {task.last_name}"
        data.append({
            "Employee ID": task.employee_id,
            "Employee Name": full_name,
            "Room Number": task.room_no,
            "Task Type": task.task_type,
            "Assigned Staff": task.assign_staff,
            "Task Status": task.task_status,
            "Schedule Date": task.schedule_date
        })

    df = pd.DataFrame(data)

    # -------------------------------
    # Excel Export
    # -------------------------------
    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="HSK Task Details")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=HSK_Task_Details.xlsx"
            }
        )

    # -------------------------------
    # JSON Export
    # -------------------------------
    json_data = df.to_json(orient="records", date_format="iso")

    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=HSK_Task_Details.json"
        }
    )

# Settlement Summary Export

@router.get("/export_settlement_summary")
async def export_settlement_summary(
    db: Session = Depends(get_db),
    format: str = Query("excel"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    company_id: str = Query(...)
):
    # Validate & prepare dates
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Expected YYYY-MM-DD"
            )
    else:
        today = date.today()
        from_date = today - timedelta(days=1)
        to_date = today

    # Fetch reservation data
    settlement_data = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.arrival_date.between(from_date, to_date)
    ).all()

    data = []
    total_paid = 0
    total_overall = 0

    for row in settlement_data:
        paid_amount = row.paid_amount or 0
        overall_amount = row.overall_amount or 0

        total_paid += paid_amount
        total_overall += overall_amount

        data.append({
            "Room Reservation ID": row.room_reservation_id,
            "Name": f"{row.first_name} {row.last_name}",
            "Overall Amount": overall_amount,
            "Paid Amount": paid_amount,
            "Balance Amount": row.balance_amount,
            "Arrival Date": row.arrival_date,
            "Departure Date": row.departure_date,
            "Reservation Status": row.reservation_status
        })

    df = pd.DataFrame(data)

    # Append totals row
    totals_row = pd.DataFrame([{
        "Room Reservation ID": "Total",
        "Name": "",
        "Overall Amount": total_overall,
        "Paid Amount": total_paid,
        "Balance Amount": total_overall - total_paid,
        "Arrival Date": "",
        "Departure Date": "",
        "Reservation Status": ""
    }])

    df = pd.concat([df, totals_row], ignore_index=True)

    # Export handling
    if format == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Settlement Summary")
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=Settlement_Summary.xlsx"}
        )

    if format == "json":
        json_data = df.to_json(orient="records")
        return StreamingResponse(
            io.BytesIO(json_data.encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=Settlement_Summary.json"}
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported format. Use 'excel' or 'json'"
    )

# Night Audit Process (React API)

@router.get("/night_audit_process")
async def night_audit_process(
    request: Request,
    db: Session = Depends(get_db)
):
    # Session validation
    if "sessid" not in request.session:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    try:
        # JWT validation
        token = request.session["sessid"]
        payload = jwt.decode(
            token,
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

        # Audit date (yesterday)
        audit_date = (dt.datetime.now() - timedelta(days=1)).date()

        # Reservation position for the audit date (stays spanning that night)
        reservations = db.query(models.RoomReservation).filter(
            models.RoomReservation.company_id == company_id,
            models.RoomReservation.arrival_date <= audit_date,
            models.RoomReservation.departure_date >= audit_date,
            models.RoomReservation.status == CommonWords.STATUS
        ).all()

        # Room revenue booked to arrive on the audit date
        room_revenue = db.query(
            func.coalesce(func.sum(models.RoomReservation.room_amount), 0)
        ).filter(
            models.RoomReservation.company_id == company_id,
            models.RoomReservation.arrival_date == audit_date,
            models.RoomReservation.status == CommonWords.STATUS
        ).scalar()

        # Extra charges (RoomReservation carries this as a plain column here,
        # not a separate Extra_Charges table)
        extra_charges = db.query(
            func.coalesce(func.sum(models.RoomReservation.extra_charges), 0)
        ).filter(
            models.RoomReservation.company_id == company_id,
            models.RoomReservation.arrival_date == audit_date,
            models.RoomReservation.status == CommonWords.STATUS
        ).scalar()

        # Payment summary by payment_method_id (PaymentMethod master lives in
        # MasterDataServices, so only the id is available here)
        payment_summary_query = (
            db.query(
                models.RoomReservation.payment_method_id,
                func.coalesce(func.sum(models.RoomReservation.paid_amount), 0).label("total_amount")
            )
            .filter(
                models.RoomReservation.company_id == company_id,
                models.RoomReservation.arrival_date == audit_date,
                models.RoomReservation.status == CommonWords.STATUS
            )
            .group_by(models.RoomReservation.payment_method_id)
            .all()
        )

        payment_summary = [
            {
                "payment_method_id": payment_method_id,
                "amount": amount
            }
            for payment_method_id, amount in payment_summary_query
        ]

        total_payments = sum(item["amount"] for item in payment_summary)

        # Final audit report
        audit_report = {
            "audit_date": audit_date,
            "reservations_count": len(reservations),
            "room_revenue": room_revenue,
            "extra_charges": extra_charges,
            "payment_summary": payment_summary,
            "total_payments": total_payments
        }

        return JSONResponse(
            content=jsonable_encoder(audit_report),
            status_code=status.HTTP_200_OK
        )

    except JWTError:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

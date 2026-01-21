import io
from turtle import pd
from fastapi import APIRouter, Depends, Request, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, RedirectResponse, StreamingResponse
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
    # Room Reservation + Room Status
    # -------------------------------
    room_data = (
        db.query(
            models.Room_Reservation,
            models.Housekeeper_Task.Room_Status
        )
        .outerjoin(
            models.Housekeeper_Task,
            models.Room_Reservation.Room_No == models.Housekeeper_Task.Room_No
        )
        .filter(
            models.Room_Reservation.company_id == company_id,
            models.Room_Reservation.Arrival_Date.between(from_date, to_date)
        )
        .all()
    )

    formatted_room_data = [
        {
            "id": r.Room_Reservation.id,
            "room_no": r.Room_Reservation.Room_No,
            "reservation_id": r.Room_Reservation.Room_Reservation_ID,
            "first_name": r.Room_Reservation.First_Name,
            "last_name": r.Room_Reservation.Last_Name,
            "phone": r.Room_Reservation.Phone_Number,
            "email": r.Room_Reservation.Email,
            "arrival_date": r.Room_Reservation.Arrival_Date,
            "departure_date": r.Room_Reservation.Departure_Date,
            "booking_status": r.Room_Reservation.Booking_Status,
            "room_status": r.Room_Status if r.Room_Status else "Unknown"
        }
        for r in room_data
    ]

    # -------------------------------
    # Housekeeping / Staff Activity
    # -------------------------------
    keeper_data = (
        db.query(
            models.Housekeeper_Task,
            models.Employee_Data.First_Name,
            models.Employee_Data.Last_Name,
            models.Task_Type.Type_Name,
            models.Task_Type.Color
        )
        .join(
            models.Employee_Data,
            models.Housekeeper_Task.Assign_Staff == models.Employee_Data.id
        )
        .join(
            models.Task_Type,
            models.Housekeeper_Task.Task_Type == models.Task_Type.id
        )
        .filter(
            models.Housekeeper_Task.company_id == company_id,
            models.Housekeeper_Task.Sch_Date.between(from_date, to_date)
        )
        .all()
    )

    formatted_keeper_data = [
        {
            "id": k.Housekeeper_Task.id,
            "employee_id": k.Housekeeper_Task.Employee_ID,
            "employee_name": f"{k.First_Name} {k.Last_Name}",
            "room_no": k.Housekeeper_Task.Room_No,
            "task_type": k.Type_Name,
            "task_color": k.Color,
            "task_status": k.Housekeeper_Task.Task_Status
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
    reservation = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.id == reservation_id,
        models.Room_Reservation.company_id == company_id
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
        "data": reservation
    }

#=====================================>>> Keeper Info  

@router.get("/keeper_info/{task_id}", status_code=status.HTTP_200_OK)
def keeper_info(
    task_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    keeper = (
        db.query(
            models.Housekeeper_Task,
            models.Employee_Data.First_Name,
            models.Employee_Data.Last_Name,
            models.Task_Type.Type_Name,
            models.Task_Type.Color
        )
        .join(
            models.Employee_Data,
            models.Housekeeper_Task.Assign_Staff == models.Employee_Data.id
        )
        .join(
            models.Task_Type,
            models.Housekeeper_Task.Task_Type == models.Task_Type.id
        )
        .filter(
            models.Housekeeper_Task.id == task_id,
            models.Housekeeper_Task.company_id == company_id
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
        "id": keeper.Housekeeper_Task.id,
        "employee_id": keeper.Housekeeper_Task.Employee_ID,
        "employee_name": f"{keeper.First_Name} {keeper.Last_Name}",
        "room_no": keeper.Housekeeper_Task.Room_No,
        "task_type": keeper.Type_Name,
        "task_color": keeper.Color,
        "task_status": keeper.Housekeeper_Task.Task_Status,
        "schedule_date": keeper.Housekeeper_Task.Sch_Date,
        "schedule_time": keeper.Housekeeper_Task.Sch_Time,
        "room_status": keeper.Housekeeper_Task.Room_Status,
        "special_instructions": keeper.Housekeeper_Task.Special_Instructions,
        "status": keeper.Housekeeper_Task.status
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
        func.coalesce(func.sum(models.Room_Reservation.Paid_Amount), 0)
    ).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Arrival_Date == today
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
    room_data = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Arrival_Date == current_date
    ).all()

    # Total paid amount
    total_paid = db.query(
        func.coalesce(func.sum(models.Room_Reservation.Paid_Amount), 0)
    ).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Arrival_Date == current_date
    ).scalar()

    # Total due amount
    total_due = db.query(
        func.coalesce(func.sum(models.Room_Reservation.Balance_Amount), 0)
    ).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Arrival_Date == current_date
    ).scalar()

    return {
        "status": "success",
        "date": current_date,
        "summary": {
            "total_paid": float(total_paid),
            "total_due": float(total_due)
        },
        "data": room_data
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
    room_data = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Booking_Status.in_(["confirmed", "available"]),
        models.Room_Reservation.Arrival_Date.between(from_date, to_date)
    ).order_by(
        models.Room_Reservation.Room_No
    ).all()

    return {
        "status": "success",
        "filters": {
            "from_date": from_date,
            "to_date": to_date
        },
        "data": room_data
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
    reservations = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.company_id == company_id,
        (
            models.Room_Reservation.Arrival_Date.between(from_date, to_date)
        ) | (
            models.Room_Reservation.Departure_Date.between(from_date, to_date)
        )
    ).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for reservation in reservations:
        full_name = f"{reservation.First_Name} {reservation.Last_Name}"
        data.append({
            "Reservation ID": reservation.Room_Reservation_ID,
            "Guest Name": full_name,
            "Phone Number": reservation.Phone_Number,
            "Arrival Date": reservation.Arrival_Date,
            "Departure Date": reservation.Departure_Date,
            "Booking Status": reservation.Booking_Status
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
    reservations = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Arrival_Date.between(from_date, to_date)
    ).order_by(models.Room_Reservation.Arrival_Date.asc()).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for reservation in reservations:
        full_name = f"{reservation.First_Name} {reservation.Last_Name}"
        data.append({
            "Reservation ID": reservation.Room_Reservation_ID,
            "Guest Name": full_name,
            "Phone Number": reservation.Phone_Number,
            "Arrival Date": reservation.Arrival_Date,
            "Departure Date": reservation.Departure_Date,
            "Booking Status": reservation.Booking_Status
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
    hsk_tasks = db.query(models.Housekeeper_Task).filter(
        models.Housekeeper_Task.company_id == company_id,
        models.Housekeeper_Task.Sch_Date == sch_date
    ).order_by(models.Housekeeper_Task.Room_No.asc()).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for task in hsk_tasks:
        full_name = f"{task.First_Name} {task.Sur_Name}"
        data.append({
            "Employee ID": task.Employee_ID,
            "Employee Name": full_name,
            "Room Number": task.Room_No,
            "Task Type": task.Task_Type,
            "Assigned Staff": task.Assign_Staff,
            "Task Status": task.Task_Status,
            "Schedule Date": task.Sch_Date
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
    settlement_data = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.company_id == company_id,
        models.Room_Reservation.Arrival_Date.between(from_date, to_date)
    ).all()

    data = []
    total_paid = 0
    total_overall = 0

    for row in settlement_data:
        paid_amount = row.Paid_Amount or 0
        overall_amount = row.Overall_Amount or 0

        total_paid += paid_amount
        total_overall += overall_amount

        data.append({
            "Room Reservation ID": row.Room_Reservation_ID,
            "Name": f"{row.First_Name} {row.Last_Name}",
            "Overall Amount": overall_amount,
            "Paid Amount": paid_amount,
            "Balance Amount": row.Balance_Amount,
            "Arrival Date": row.Arrival_Date,
            "Departure Date": row.Departure_Date,
            "Reservation Status": row.Booking_Status
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

        # 1. Reservation Position Check
        reservations = db.query(models.Room_Reservation).filter(
            models.Room_Reservation.company_id == company_id,
            models.Room_Reservation.Arrival_Date <= audit_date,
            models.Room_Reservation.Departure_Date >= audit_date,
            models.Room_Reservation.status == CommonWords.STATUS
        ).all()

        # 2. Room Tariff Verification
        room_tariffs = db.query(models.Room_Tariff).filter(
            models.Room_Tariff.company_id == company_id,
            models.Room_Tariff.Effective_Date <= audit_date,
            models.Room_Tariff.Expiry_Date >= audit_date,
            models.Room_Tariff.status == CommonWords.STATUS
        ).all()

        # 3. Settlement Verification
        settlements = db.query(models.Payment_Transactions).filter(
            models.Payment_Transactions.company_id == company_id,
            func.date(models.Payment_Transactions.Transaction_Date) == audit_date,
            models.Payment_Transactions.status == CommonWords.STATUS
        ).all()

        # 4. Room Revenue Calculation
        room_revenue = db.query(
            func.coalesce(func.sum(models.Room_Reservation.Paid_Amount), 0)
        ).filter(
            models.Room_Reservation.company_id == company_id,
            func.date(models.Room_Reservation.Arrival_Date) == audit_date,
            models.Room_Reservation.status == CommonWords.STATUS
        ).scalar()

        # 5. Extra Charges Calculation
        extra_charges = db.query(
            func.coalesce(func.sum(models.Extra_Charges.Amount), 0)
        ).filter(
            models.Extra_Charges.company_id == company_id,
            func.date(models.Extra_Charges.Charge_Date) == audit_date,
            models.Extra_Charges.status == CommonWords.STATUS
        ).scalar()

        # 6. Payment Summary
        payment_summary_query = (
            db.query(
                models.Payment_Mode.Mode_Name,
                func.coalesce(func.sum(models.Payment_Transactions.Amount), 0).label("total_amount")
            )
            .join(
                models.Payment_Transactions,
                models.Payment_Transactions.Payment_Mode == models.Payment_Mode.id
            )
            .filter(
                models.Payment_Transactions.company_id == company_id,
                func.date(models.Payment_Transactions.Transaction_Date) == audit_date,
                models.Payment_Transactions.status == CommonWords.STATUS
            )
            .group_by(models.Payment_Mode.Mode_Name)
            .all()
        )

        payment_summary = [
            {
                "mode": mode,
                "amount": amount
            }
            for mode, amount in payment_summary_query
        ]

        total_payments = sum(item["amount"] for item in payment_summary)

        # Final audit report
        audit_report = {
            "audit_date": audit_date,
            "reservations_count": len(reservations),
            "room_tariffs_count": len(room_tariffs),
            "settlements_count": len(settlements),
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

# Settlement Summary (React API)

@router.get("/settlement_summary")
async def settlement_summary(
    request: Request,
    db: Session = Depends(get_db),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
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

        # Date handling
        if from_date and to_date:
            try:
                from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
            except ValueError:
                return JSONResponse(
                    content={"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            today = date.today()
            from_date = today - timedelta(days=1)
            to_date = today

        # Fetch settlement data
        room_data = db.query(models.Room_Reservation).filter(
            models.Room_Reservation.company_id == company_id,
            models.Room_Reservation.Arrival_Date.between(from_date, to_date),
            models.Room_Reservation.status == CommonWords.STATUS
        ).order_by(models.Room_Reservation.Arrival_Date.asc()).all()

        # Calculate totals
        total_paid = db.query(
            func.coalesce(func.sum(models.Room_Reservation.Paid_Amount), 0)
        ).filter(
            models.Room_Reservation.company_id == company_id,
            models.Room_Reservation.Arrival_Date.between(from_date, to_date),
            models.Room_Reservation.status == CommonWords.STATUS
        ).scalar()

        total_due = db.query(
            func.coalesce(func.sum(models.Room_Reservation.Balance_Amount), 0)
        ).filter(
            models.Room_Reservation.company_id == company_id,
            models.Room_Reservation.Arrival_Date.between(from_date, to_date),
            models.Room_Reservation.status == CommonWords.STATUS
        ).scalar()

        total_overall = db.query(
            func.coalesce(func.sum(models.Room_Reservation.Overall_Amount), 0)
        ).filter(
            models.Room_Reservation.company_id == company_id,
            models.Room_Reservation.Arrival_Date.between(from_date, to_date),
            models.Room_Reservation.status == CommonWords.STATUS
        ).scalar()

        # Format response data
        data = []
        for r in room_data:
            data.append({
                "reservation_id": r.Room_Reservation_ID,
                "guest_name": f"{r.First_Name} {r.Last_Name}",
                "room_no": r.Room_No,
                "arrival_date": r.Arrival_Date,
                "departure_date": r.Departure_Date,
                "overall_amount": r.Overall_Amount,
                "paid_amount": r.Paid_Amount,
                "balance_amount": r.Balance_Amount,
                "booking_status": r.Booking_Status
            })

        return JSONResponse(
            content={
                "status": "success",
                "filters": {
                    "from_date": from_date,
                    "to_date": to_date
                },
                "summary": {
                    "total_overall": total_overall,
                    "total_paid": total_paid,
                    "total_due": total_due
                },
                "data": data
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


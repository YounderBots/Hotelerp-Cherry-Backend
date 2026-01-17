from fastapi import APIRouter, Depends,UploadFile,status, Request, Form ,File,Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse,FileResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import and_
from typing import Optional,List
from configs import BaseConfig
from fastapi import HTTPException
from datetime import  timedelta, date
import datetime as dt
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.sessions import SessionMiddleware
import bcrypt,uuid,shutil,datetime,json,random,sqlalchemy
from jose import jwt, JWTError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi.responses import StreamingResponse
from configs.base_config import BaseConfig,CommonWords
import pandas as pd
import io

router = APIRouter()
templates = Jinja2Templates(directory="templates")

#=====================================>>> Night Auditing
@router.get("/user_activity_log")
async def user_activity_log(
    request: Request, 
    db: Session = Depends(get_db),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            
            color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()

            # Set default dates to yesterday and today if not provided
            if from_date and to_date:
                from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
            else:
                today = date.today()
                yesterday = today - timedelta(days=1)
                from_date = yesterday
                to_date = today

            
            room_data = (
                db.query(
                    models.Room_Reservation,
                    models.Housekeeper_Task.Room_Status
                )
                .outerjoin(
                    models.Housekeeper_Task,
                    models.Room_Reservation.Room_No == models.Housekeeper_Task.Room_No
                )
                .filter(models.Room_Reservation.Arrival_Date.between(from_date, to_date))
                .all()
            )

            formatted_room_data = [
                {
                    'id': r.Room_Reservation.id,
                    'room_no': r.Room_Reservation.Room_No,
                    'Room_Reservation_ID': r.Room_Reservation.Room_Reservation_ID,
                    'First_Name': r.Room_Reservation.First_Name,
                    'Last_Name': r.Room_Reservation.Last_Name,
                    'Phone_Number': r.Room_Reservation.Phone_Number,
                    'Email': r.Room_Reservation.Email,
                    'Arrival_Date': r.Room_Reservation.Arrival_Date,
                    'Departure_Date': r.Room_Reservation.Departure_Date,
                    'Booking_Status': r.Room_Reservation.Booking_Status,
                    'Room_Status': r.Room_Status if r.Room_Status else 'Unknown'
                }
                for r in room_data
            ]

            
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
                .filter(models.Housekeeper_Task.Sch_Date.between(from_date, to_date))  
                .all()
            )
            
            
            formatted_keeper_data = [
                {
                    'id': k.Housekeeper_Task.id,
                    'Employee_ID': k.Housekeeper_Task.Employee_ID,
                    'First_Name': k.Housekeeper_Task.First_Name,
                    'Sur_Name': k.Housekeeper_Task.Sur_Name,
                    'Room_No': k.Housekeeper_Task.Room_No,
                    'task_type': k.Type_Name,
                    'Assign_Staff': f"{k.First_Name} {k.Last_Name}",
                    'Task_Status': k.Housekeeper_Task.Task_Status
                }
                for k in keeper_data
            ]
           
            return templates.TemplateResponse(
                'night_auditing/user_activity_log.html',
                context={
                    'request': request,
                    'color_theme': color_theme,
                    'room_data': formatted_room_data,
                    'keeper_data': formatted_keeper_data,
                    'from_date': from_date,
                    'to_date': to_date
                }
            )
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
       return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
      
@router.get("/reservation_info/{reservationId}")
async def reservation_info(request: Request,reservationId:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                particular_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.id==reservationId).first()

                return JSONResponse(content=jsonable_encoder(particular_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/keeper_info/{roomid}")
async def keeper_info(request: Request, roomid: int, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
               
                keeper_info = (
                        db.query(
                            models.Housekeeper_Task,
                            models.Employee_Data.First_Name,
                            models.Employee_Data.Last_Name,
                            models.Task_Type.Type_Name,
                            models.Task_Type.Color
                        )
                        .select_from(models.Housekeeper_Task)  
                        .join(
                            models.Employee_Data,
                            models.Housekeeper_Task.Assign_Staff == models.Employee_Data.id
                        )
                        .join(
                            models.Task_Type,
                            models.Housekeeper_Task.Task_Type == models.Task_Type.id  
                        )
                        .filter(models.Housekeeper_Task.id == roomid)
                        .first()
                    )


               
                if not keeper_info:
                    return JSONResponse(content={"message": "Keeper info not found"}, status_code=status.HTTP_404_NOT_FOUND)

                formatted_keeper_info = {
                    'id': keeper_info.Housekeeper_Task.id,
                    'Employee_ID': keeper_info.Housekeeper_Task.Employee_ID,
                    'First_Name': keeper_info.Housekeeper_Task.First_Name,
                    'Sur_Name': keeper_info.Housekeeper_Task.Sur_Name,
                    'Room_No': keeper_info.Housekeeper_Task.Room_No,
                    'Task_Type': keeper_info.Type_Name,  
                    'Task_Color': keeper_info.Color,    
                    'Assign_Staff': f"{keeper_info.First_Name} {keeper_info.Last_Name}",
                    'Task_Status': keeper_info.Housekeeper_Task.Task_Status,
                    'Sch_Date': keeper_info.Housekeeper_Task.Sch_Date,
                    'Sch_Time': keeper_info.Housekeeper_Task.Sch_Time,
                    'Room_Status': keeper_info.Housekeeper_Task.Room_Status,
                    'Special_Instructions': keeper_info.Housekeeper_Task.Special_Instructions,
                    'status': keeper_info.Housekeeper_Task.status
                }

                return JSONResponse(content=jsonable_encoder(formatted_keeper_info), status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
       return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
       
@router.get("/get_paid_amount")
async def get_paid_amount(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                # Calculate the total paid amount for reservations on today's date
                today = date.today()
                total_paid_amount = db.query(func.coalesce(func.sum(models.Room_Reservation.Paid_Amount), 0)) \
                .filter(models.Room_Reservation.Arrival_Date == today) \
                .scalar()
                return JSONResponse(content=jsonable_encoder(total_paid_amount),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    

@router.get("/settlement_summary")
async def settlement_summary(request: Request, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by = payload.get("user_id")
            company_id = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            
            color_theme = db.query(models.Themes).filter(
                models.Themes.status == CommonWords.STATUS
            ).first()
            
            current_date = date.today()
            
            # Get all settlements for today
            room_data = db.query(models.Room_Reservation).filter(
                models.Room_Reservation.Arrival_Date == current_date
            ).all()
            
            # Calculate totals
            total_paid = db.query(func.sum(models.Room_Reservation.Paid_Amount)).filter(
                models.Room_Reservation.Arrival_Date == current_date
            ).scalar() or 0
            
            total_due = db.query(func.sum(models.Room_Reservation.Balance_Amount)).filter(
                models.Room_Reservation.Arrival_Date == current_date
            ).scalar() or 0
            
            return templates.TemplateResponse(
                'night_auditing/settlement_summary.html', 
                context={
                    'request': request,
                    'color_theme': color_theme,
                    'room_data': room_data,
                    'total_paid': total_paid,
                    'total_due': total_due
                }
            )
            
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/room_sales")
async def room_sales(
    request: Request, 
    db: Session = Depends(get_db),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            
            color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()

            # Set default dates to yesterday and today if not provided
            if from_date and to_date:
                from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
            else:
                today = date.today()
                yesterday = today - timedelta(days=1)
                from_date = yesterday
                to_date = today

            # Query room data with date filtering
            room_data = db.query(models.Room_Reservation).filter(
                models.Room_Reservation.Booking_Status.in_(["confirmed", "available"]),
                models.Room_Reservation.Arrival_Date.between(from_date, to_date)
            ).order_by(models.Room_Reservation.Room_No).all()

            return templates.TemplateResponse(
                'night_auditing/room_sales.html', 
                context={
                    'request': request,
                    'color_theme': color_theme,
                    'room_data': room_data,
                    'from_date': from_date,
                    'to_date': to_date
                }
            )
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
       return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#-------------- Night Auditing Export -------------------------------

#-------------- User Activity Log -------


@router.get("/export_user_activity/")
async def export_user_activity(
    db: Session = Depends(get_db),
    format: str = Query("excel"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    # Set default dates to yesterday and today if not provided
    if from_date and to_date:
        from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    reservations = db.query(models.Room_Reservation).filter(
        (models.Room_Reservation.Arrival_Date.between(from_date, to_date)) |
        (models.Room_Reservation.Departure_Date.between(from_date, to_date))
    ).all()

    data = []
    for reservation in reservations:
        full_name = f"{reservation.First_Name} {reservation.Last_Name}"
        data.append({
            "Room Reservation ID": reservation.Room_Reservation_ID,
            "Name": full_name,
            "Phone Number": reservation.Phone_Number,
            "Arrival Date": reservation.Arrival_Date,
            "Departure Date": reservation.Departure_Date,
            "Reservation Status": reservation.Booking_Status,
        })

    
    df = pd.DataFrame(data)

    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='User Activity Log')
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename=User_Activity_Log.xlsx"})

    elif format == "json":
        
        json_data = df.to_json(orient="records")
        return StreamingResponse(io.BytesIO(json_data.encode()), media_type="application/json",
                                 headers={"Content-Disposition": "attachment; filename=User_Activity_Log.json"})


#-------------- Room Booked Details Export -------


@router.get("/export_room_booked_details/")
async def export_room_booked_details(
    db: Session = Depends(get_db),
    format: str = Query("excel"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    # Set default dates to yesterday and today if not provided
    if from_date and to_date:
        from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    reservations = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.Arrival_Date.between(from_date, to_date)
    ).all()
    
    data = []
    for reservation in reservations:
        full_name = f"{reservation.First_Name} {reservation.Last_Name}"
        data.append({
            "Room Reservation ID": reservation.Room_Reservation_ID,
            "Name": full_name,  
            "Phone Number": reservation.Phone_Number,
            "Arrival Date": reservation.Arrival_Date,
            "Departure Date": reservation.Departure_Date, 
            "Reservation Status": reservation.Booking_Status,   
        })

    df = pd.DataFrame(data)

    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Room Booked Details')
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename= Room_Booked_Details.xlsx"})
    
    elif format == "json":
        json_data = df.to_json(orient="records")
        return StreamingResponse(io.BytesIO(json_data.encode()), media_type="application/json",
                                 headers={"Content-Disposition": "attachment; filename= Room_Booked_Details.json"})

#-------------- Hsk Task Details Export -------


@router.get("/export_hsk_details/")
async def export_hsk_details(
    db: Session = Depends(get_db),
    format: str = Query("excel")  
):

    hsk_tasks = db.query(models.Housekeeper_Task).all()

    today = date.today()

    hsk_tasks = db.query(models.Housekeeper_Task).filter((models.Housekeeper_Task.Sch_Date == today)).all()
    
    data = []
    for  hsk_task in hsk_tasks :
        full_name = f"{hsk_task.First_Name} {hsk_task.Sur_Name}"
        data.append({
            "Employee ID": hsk_task.Employee_ID,
            "Name": full_name,  
            "Room Number": hsk_task.Room_No,
            "Task Type": hsk_task.Task_Type,
            "Assign Staff": hsk_task.Assign_Staff, 
            "Task Status": hsk_task.Task_Status,   
        })

    df = pd.DataFrame(data)

    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='HSK Task Details')
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename= HSK_Task_Details.xlsx"})
    
    elif format == "json":

        json_data = df.to_json(orient="records")
        return StreamingResponse(io.BytesIO(json_data.encode()), media_type="application/json",
                                 headers={"Content-Disposition": "attachment; filename= HSK_Task_Details.json"})


#-------------- Settlement Summary Export -------


@router.get("/export_settlement_summary/")
async def export_settlement_summary(
    db: Session = Depends(get_db),
    format: str = Query("excel"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    # Set default dates to yesterday and today if not provided
    if from_date and to_date:
        from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    settlement_data = db.query(models.Room_Reservation).filter(
        models.Room_Reservation.Arrival_Date.between(from_date, to_date)
    ).all()

    data = []
    total_paid = 0
    total_overall = 0
    
    for settlement_summary in settlement_data:
        full_name = f"{settlement_summary.First_Name} {settlement_summary.Last_Name}"
        total_paid += settlement_summary.Paid_Amount
        total_overall += settlement_summary.Overall_Amount
        data.append({
            "Room Reservation ID": settlement_summary.Room_Reservation_ID,
            "Name": full_name,
            "Overall Amount": settlement_summary.Overall_Amount,
            "Paid Amount": settlement_summary.Paid_Amount,
            "Balance Amount": settlement_summary.Balance_Amount,
            "Arrival Date": settlement_summary.Arrival_Date,
            "Departure Date": settlement_summary.Departure_Date,
            "Reservation Status": settlement_summary.Booking_Status,
        })

    df = pd.DataFrame(data)

    totals = pd.DataFrame([{
        "Room Reservation ID": "Total", 
        "Name": "",
        "Overall Amount": total_overall, 
        "Paid Amount": total_paid,
        "Balance Amount": total_overall - total_paid,
        "Arrival Date": "",
        "Departure Date": "",
        "Reservation Status": ""
    }])
    
    df = pd.concat([df, totals], ignore_index=True)

    if format == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Settlement Summary')
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=Settlement_Summary.xlsx"
            }
        )
    elif format == "json":
        json_data = df.to_json(orient="records")
        return StreamingResponse(
            io.BytesIO(json_data.encode()), 
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=Settlement_Summary.json"
            }
        )
    else:
        return {"error": "Unsupported format requested. Please choose either 'excel' or 'json'."}
    

# Add this new route for the night audit process
@router.get("/night_audit_process")
async def night_audit_process(request: Request, db: Session = Depends(get_db)):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    try:
        token = request.session["sessid"]
        payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
        created_by = payload.get("user_id")
        company_id = payload.get("company_id")
        
        if not created_by:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        audit_date = yesterday.date()
        
        # 1. Check Reservations Position
        reservations = db.query(models.Room_Reservation).filter(
            models.Room_Reservation.Arrival_Date <= audit_date,
            models.Room_Reservation.Departure_Date >= audit_date
        ).all()
        
        # 2. Room Tariff Verification
        room_tariffs = db.query(models.Room_Tariff).filter(
            models.Room_Tariff.Effective_Date <= audit_date,
            models.Room_Tariff.Expiry_Date >= audit_date
        ).all()
        
        # 3. Settlements Verification
        settlements = db.query(models.Payment_Transactions).filter(
            func.date(models.Payment_Transactions.Transaction_Date) == audit_date
        ).all()
        
        # 4. Room Revenue Calculation
        room_revenue = db.query(func.sum(models.Room_Reservation.Paid_Amount)).filter(
            func.date(models.Room_Reservation.Arrival_Date) == audit_date
        ).scalar() or 0
        
        # 5. Extra Charges Calculation
        extra_charges = db.query(func.sum(models.Extra_Charges.Amount)).filter(
            func.date(models.Extra_Charges.Charge_Date) == audit_date
        ).scalar() or 0
        
        # 6. Payment Summary
        payment_summary = db.query(
            models.Payment_Mode.Mode_Name,
            func.sum(models.Payment_Transactions.Amount).label("total_amount")
        ).join(
            models.Payment_Transactions,
            models.Payment_Transactions.Payment_Mode == models.Payment_Mode.id
        ).filter(
            func.date(models.Payment_Transactions.Transaction_Date) == audit_date
        ).group_by(models.Payment_Mode.Mode_Name).all()
        
        # Prepare audit report data
        audit_report = {
            "audit_date": audit_date,
            "reservations_count": len(reservations),
            "room_tariffs_count": len(room_tariffs),
            "settlements_count": len(settlements),
            "room_revenue": room_revenue,
            "extra_charges": extra_charges,
            "payment_summary": [
                {"mode": mode, "amount": amount} 
                for mode, amount in payment_summary
            ],
            "total_payments": sum(amount for _, amount in payment_summary)
        }
        
        return JSONResponse(content=audit_report, status_code=status.HTTP_200_OK)
        
    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settlement_summary")
async def settlement_summary(
    request: Request, 
    db: Session = Depends(get_db),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by = payload.get("user_id")
            company_id = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            
            color_theme = db.query(models.Themes).filter(
                models.Themes.status == CommonWords.STATUS
            ).first()
            
            # Set default dates to yesterday and today if not provided
            if from_date and to_date:
                from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
            else:
                today = date.today()
                yesterday = today - timedelta(days=1)
                from_date = yesterday
                to_date = today

            # Get all settlements for the date range
            room_data = db.query(models.Room_Reservation).filter(
                models.Room_Reservation.Arrival_Date.between(from_date, to_date)
            ).all()
            
            # Calculate totals for the filtered date range
            total_paid = db.query(func.sum(models.Room_Reservation.Paid_Amount)).filter(
                models.Room_Reservation.Arrival_Date.between(from_date, to_date)
            ).scalar() or 0
            
            total_due = db.query(func.sum(models.Room_Reservation.Balance_Amount)).filter(
                models.Room_Reservation.Arrival_Date.between(from_date, to_date)
            ).scalar() or 0
            
            total_overall = db.query(func.sum(models.Room_Reservation.Overall_Amount)).filter(
                models.Room_Reservation.Arrival_Date.between(from_date, to_date)
            ).scalar() or 0
            
            return templates.TemplateResponse(
                'night_auditing/settlement_summary.html', 
                context={
                    'request': request,
                    'color_theme': color_theme,
                    'room_data': room_data,
                    'total_paid': total_paid,
                    'total_due': total_due,
                    'total_overall': total_overall,
                    'from_date': from_date,
                    'to_date': to_date,
                    'date_format': lambda d: d.strftime('%d-%b-%Y')  # Add date formatter
                }
            )
            
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
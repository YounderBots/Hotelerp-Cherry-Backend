from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_
from configs import BaseConfig
from datetime import timedelta
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from resources.utils import create_access_token
from starlette.middleware.sessions import SessionMiddleware
import bcrypt
from icecream import ic
from jose import jwt, JWTError
from sqlalchemy import func

from configs.base_config import BaseConfig, CommonWords

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard")
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by:
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                
                total_rooms = db.query(models.Room).count()
                vacant_rooms = db.query(models.Room).filter(models.Room.Room_Booking_status == 'Available').count()
                occupied_rooms = db.query(models.Room).filter(models.Room.Room_Booking_status == 'Occupied').count()
                blocked_rooms = db.query(models.Room).filter(models.Room.Room_Status == 'Blocked').count()

                total_reservations = db.query(models.Room_Reservation).filter(models.Room_Reservation.Booking_Status != 'departures').count()
                arrival_reservations = db.query(models.Room_Reservation).filter(models.Room_Reservation.Booking_Status == 'Arrived').count()
                pending_arrival_reservations = db.query(models.Room_Reservation).filter(models.Room_Reservation.Booking_Status == 'Confirmed').count()
                cancelled_reservations = db.query(models.Room_Reservation).filter(models.Room_Reservation.Booking_Status == 'Cancelled').count()

                total_departures_1 = db.query(func.count(models.Room_Reservation.id)).filter(
                    models.Room_Reservation.Booking_Status == 'Arrived',
                    models.Room_Reservation.Arrival_Date <= CommonWords.CURRENTDATE,
                    models.Room_Reservation.status == CommonWords.STATUS
                ).scalar()

                total_departures_2 = db.query(func.count(models.Room_Booking.id)).filter(
                    models.Room_Booking.Departure_Date >= CommonWords.CURRENTDATE,
                    models.Room_Booking.status == CommonWords.STATUS
                ).scalar()

                checkout = db.query(models.Room_Reservation).filter(models.Room_Reservation.Booking_Status == 'departures').count()

                total_departures = total_departures_1 + total_departures_2 + checkout

                
                pending_out_departures = total_departures - checkout

                today = datetime.now()
                start_of_week = (today - timedelta(days=today.weekday())).date()
                end_of_week = start_of_week + timedelta(days=6)

                occupancy_per_day = {start_of_week + timedelta(days=i): 0 for i in range(7)}

                reservation_occupancy = db.query(
                    models.Room_Reservation.Arrival_Date,
                    models.Room_Reservation.Departure_Date,
                    func.sum(models.Room_Reservation.No_Of_Adults + models.Room_Reservation.No_Of_Childs).label('occupancy_count')
                ).filter(
                    and_(
                        models.Room_Reservation.Arrival_Date <= end_of_week, 
                        models.Room_Reservation.Departure_Date > start_of_week 
                    )
                ).group_by(models.Room_Reservation.Arrival_Date, models.Room_Reservation.Departure_Date).all()

                booking_occupancy = db.query(
                    models.Room_Booking.Arrival_Date,
                    models.Room_Booking.Departure_Date,
                    func.sum(models.Room_Booking.No_Of_Adults + models.Room_Booking.No_Of_Childs).label('occupancy_count')
                ).filter(
                    and_(
                        models.Room_Booking.Arrival_Date <= end_of_week,  
                        models.Room_Booking.Departure_Date > start_of_week
                    )
                ).group_by(models.Room_Booking.Arrival_Date, models.Room_Booking.Departure_Date).all()
                
                for record in reservation_occupancy + booking_occupancy:
                    arrival_date = record.Arrival_Date
                    departure_date = record.Departure_Date
                    occupancy_count = record.occupancy_count
                    
                    current_date = arrival_date
                    while current_date < departure_date: 
                        if start_of_week <= current_date <= end_of_week:
                            occupancy_per_day[current_date] += occupancy_count
                        current_date += timedelta(days=1)
                                
                occupancy_per_day = {date.strftime('%a'): occupancy for date, occupancy in occupancy_per_day.items()}
                
                return templates.TemplateResponse('dashboard/dashboard.html', context={
                    'request': request,
                    'color_theme': color_theme,
                    'total_rooms': total_rooms,
                    'vacant_rooms': vacant_rooms,
                    'occupied_rooms': occupied_rooms,
                    'blocked_rooms': blocked_rooms,
                    'total_reservations': total_reservations,
                    'arrival_reservations': arrival_reservations,
                    'pending_arrival_reservations': pending_arrival_reservations,
                    'cancelled_reservations': cancelled_reservations,
                    'checkout': checkout,
                    "total_departures": total_departures,
                    'pending_out_departures': pending_out_departures,
                    'occupancy_data': occupancy_per_day
                })
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/dashboard/room-status")
async def room_status(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by:
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                
                detailed_rooms = db.query(models.Room).all()  

                for det in detailed_rooms:
                    Room_Type = db.query(models.Room_Type).filter(models.Room_Type.id == det.Room_Type_ID,models.Room_Type.status=="ACTIVE").first()
                    det.Room_Type = Room_Type.Type_Name

                return templates.TemplateResponse('dashboard/room_status_details.html', {
                    'request': request,
                    'color_theme': color_theme,
                    'rooms': detailed_rooms
                })
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/dashboard/reservation-details")
async def reservation_details(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by:
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                
                reservations = db.query(models.Room_Reservation).all()

                for res in reservations:
                    res.Guest_Name = res.First_Name + res.Last_Name
                    res.booking_id = res.Room_Reservation_ID

                return templates.TemplateResponse('dashboard/reservation_details.html', {
                    'request': request,
                    'color_theme': color_theme,
                    'reservations': reservations
                })
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/dashboard/departure-details")
async def departure_details(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by:
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                
                # Get all departures from Room_Reservation table
                departures_query = db.query(models.Room_Reservation).filter(
                    models.Room_Reservation.Booking_Status.in_(['departures', 'Checked Out']),
                    models.Room_Reservation.status == CommonWords.STATUS,
                    models.Room_Reservation.company_id == company_id
                ).all()

                # Format for frontend
                departures = []
                for dep in departures_query:
                    room_names = []
                    if dep.Room_No:
                        for room_id in dep.Room_No:
                            room = db.query(models.Room).filter(models.Room.id == int(room_id)).first()
                            if room:
                                room_names.append(room.Room_Name)
                    else:
                        room_names.append("N/A")

                    departures.append({
                        'Room_Number': ', '.join(room_names),
                        'Guest_Name': f"{dep.First_Name or ''} {dep.Last_Name or ''}".strip(),
                        'Scheduled_Departure': dep.Departure_Date,
                        'Actual_Departure': dep.updated_at.date() if dep.Booking_Status == 'Departures' else None,
                        'Status': 'Departures' if dep.Booking_Status == 'Departures' else 'Scheduled'
                    })

                return templates.TemplateResponse('dashboard/departure_details.html', {
                    'request': request,
                    'color_theme': color_theme,
                    'departures': departures
                })
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

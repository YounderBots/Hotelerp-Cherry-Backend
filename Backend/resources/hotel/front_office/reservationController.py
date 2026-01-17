from fastapi import APIRouter, Depends,UploadFile,status, Request, Form ,File,Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse,FileResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import and_,or_
from typing import Optional,List
from configs import BaseConfig
from datetime import datetime, timedelta, date

from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.sessions import SessionMiddleware
import bcrypt,uuid,shutil,json,random,sqlalchemy
from jose import jwt, JWTError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi.responses import StreamingResponse
import pandas as pd
import io
from configs.base_config import BaseConfig,CommonWords

router = APIRouter()
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


LOGINER_URL = '/login'    
STATUS = 'ACTIVE'
UNSTATUS = 'INACTIVE'
AVAILABLE = 'AVAILABLE'
RESERVED = 'RESERVED'
CANCELLED = 'CANCELLED'
OCCUPIED = 'OCCUPIED'
WORK_STATUS = 'Not Assigne'
RESERVATION="RESERVATION"
GROUP_RESERVATION="GROUP_RESERVATION"
CHECKIN = "CHECKIN"
BLOCKING = "Blocking"
UNBLOCKING = "UnBlocking"

TODAY = datetime.today()

#=====================================>>> Reservation List
@router.get("/reservation_list")
def Reservation_List(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                permision_control = (db.query(models.Role_Permission).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first())
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.status==CommonWords.STATUS).order_by(models.Room_Reservation.id.desc()).all()
                for resd in reservation_data:
                    if resd.Arrival_Date <= datetime.today().date() <= resd.Departure_Date:
                        resd.currentdate = "yes"
                    else:
                        resd.currentdate = "no"
                payment_method = db.query(models.Payment_Methods).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
              
                identity_proofs = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status == "ACTIVE").all()

                return templates.TemplateResponse('front_office/reservation/reservation_list.html', context={'request': request,'color_theme':color_theme,'reservation_data':reservation_data,'permision_control':permision_control,
                                                                                          'identity_proofs':identity_proofs,'loginer_data':loginer_data,'payment_method':payment_method})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#Get Reservation Amount Details
@router.get("/reservation_amount_details/{id}")
def Reservation_Amount_Details(request: Request,id: str, db: Session = Depends(get_db)):
   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                amount_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token == id).filter(models.Room_Reservation.status==CommonWords.STATUS).first()             
           
            error = {'message':"Details Displayed",'amount_details':amount_details}
            return JSONResponse(content=jsonable_encoder(error), status_code=status.HTTP_200_OK)
                
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/reservation_refund_details/{id}")
def Reservation_Amount_Details(request: Request,id: str, db: Session = Depends(get_db)):
   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                refund_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token == id).filter(models.Room_Reservation.status==CommonWords.STATUS).first()               
                
            error = {'message':"Details Displayed",'refund_details':refund_details}
            return JSONResponse(content=jsonable_encoder(error), status_code=status.HTTP_200_OK)
                
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#Reservation Payment update
@router.post("/reservation_paymentupdate")
async def Reservation_PaymentUpdate(request: Request,db: Session = Depends(get_db),reservation_token:str=Form(...),paying_amount:str=Form(...),payment_method:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                old_reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==reservation_token).filter(models.Room_Reservation.status==CommonWords.STATUS).first()
                if old_reservation_data:
                    total_balance_amount = old_reservation_data.Balance_Amount
                    total_paid_amount = old_reservation_data.Paid_Amount
                    new_balance_amount = float(total_balance_amount)-float(paying_amount)
                    new_paid_amount = float(total_paid_amount)+float(paying_amount)
                    
                    db.query(models.Room_Reservation).filter(models.Room_Reservation.id==old_reservation_data.id).update({'Paid_Amount':new_paid_amount,'Balance_Amount':new_balance_amount})                    
                    db.commit()
                    
                    paying_amount = models.Reser_AmountPaidHistory(Reservation_Id=old_reservation_data.id,user_id=old_reservation_data.Email,Amount=paying_amount,paid_date=CommonWords.CURRENTDATE,payment_method=payment_method,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                
                    db.add(paying_amount)
                    db.commit()
                    db.refresh(paying_amount)
                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.post("/process_reservation_refund")
async def Reservation_PaymentUpdate(request: Request,db: Session = Depends(get_db),reservation_token:str=Form(...), refund_amount:str=Form(...),refund_method:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                old_reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==reservation_token).filter(models.Room_Reservation.status==CommonWords.STATUS).first()
                if old_reservation_data:
                    extra_amount = old_reservation_data.Extra_Amount
                    new_extra_amount = float(extra_amount)-float(refund_amount)
                    
                    db.query(models.Room_Reservation).filter(models.Room_Reservation.id==old_reservation_data.id).update({'Extra_Amount':new_extra_amount})                    
                    db.commit()
                    
                    # refunding_amount = models.Reser_AmountPaidHistory(Reservation_Id=old_reservation_data.id,user_id=old_reservation_data.Email,Amount=paying_amount,paid_date=CommonWords.CURRENTDATE,payment_method=payment_method,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                
                    # db.add(refunding_amount)
                    # db.commit()
                    # db.refresh(refunding_amount)
                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Reservation Invoice
@router.get("/reservation_invoice/{id}")
def Reservation_Invoice(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                reservation_data =''
                reser_room_data =''
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                permision_control = (db.query(models.Role_Permission).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first())
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                findres_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.id==findres_details.id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    reser_room_data = db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id==findres_details.id,models.Room_Details.status==CommonWords.STATUS).all()
                    for resdat in reser_room_data:
                        roomtype_data = db.query(models.Room_Type).filter(models.Room_Type.id==resdat.Room_category,models.Room_Type.status==CommonWords.STATUS).first() 
                        if roomtype_data:
                            resdat.room_type = roomtype_data.Type_Name 
                        room_data = db.query(models.Room).filter(models.Room.id==resdat.Available_rooms,models.Room.status==CommonWords.STATUS).first() 
                        if room_data:
                            resdat.room_no = room_data.Room_No 
                if findres_details:
                    payment_data = db.query(models.Reser_AmountPaidHistory).filter(models.Reser_AmountPaidHistory.Reservation_Id==findres_details.id,models.Reser_AmountPaidHistory.status==CommonWords.STATUS).all()
                   
                return templates.TemplateResponse('front_office/reservation/invoice.html', context={'request': request,'color_theme':color_theme,'reservation_data':reservation_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,'today_date':CommonWords.Today_DateFormated,'reser_room_data':reser_room_data,'payment_data':payment_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#=====================================>>> View Reservation Details
@router.get("/view_reservation_details/{id}")
def View_Reservation_Details(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                reservation_data =''
                reser_room_data =''
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                permision_control = (db.query(models.Role_Permission).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first())
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                findres_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.id==findres_details.id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    reser_room_data = db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id==findres_details.id,models.Room_Details.status==CommonWords.STATUS).all()
                    for resdat in reser_room_data:
                        roomtype_data = db.query(models.Room_Type).filter(models.Room_Type.id==resdat.Room_category,models.Room_Type.status==CommonWords.STATUS).first() 
                        if roomtype_data:
                            resdat.room_type = roomtype_data.Type_Name 
                        room_data = db.query(models.Room).filter(models.Room.id==resdat.Available_rooms,models.Room.status==CommonWords.STATUS).first() 
                        if room_data:
                            resdat.room_no = room_data.Room_No 
                if findres_details:
                    payment_data = db.query(models.Reser_AmountPaidHistory).filter(models.Reser_AmountPaidHistory.Reservation_Id==findres_details.id,models.Reser_AmountPaidHistory.status==CommonWords.STATUS).all()
                   
                return templates.TemplateResponse('front_office/reservation/view_reservation_details.html', context={'request': request,'color_theme':color_theme,'reservation_data':reservation_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,'today_date':CommonWords.Today_DateFormated,'reser_room_data':reser_room_data,'payment_data':payment_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.delete("/delete_reservation/{id}")
async def Delete_Reservation(request: Request, id: str, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                findres_details = db.query(models.Room_Reservation).filter(
                    models.Room_Reservation.token == id,
                    models.Room_Reservation.status == CommonWords.STATUS
                ).first()
                
                if findres_details:
                    # Check if reservation is currently active
                    if findres_details.Arrival_Date <= datetime.today().date() <= findres_details.Departure_Date:
                        for room_id in findres_details.Room_No:
                            db.query(models.Room).filter(
                                models.Room.id == room_id,
                                models.Room.Room_Booking_status != CommonWords.Arrived
                            ).update({'Room_Booking_status': CommonWords.AVAILABLE})                    
                            db.commit()
                    
                    # Update room details status
                    db.query(models.Room_Details).filter(
                        models.Room_Details.Reservation_Id == findres_details.id
                    ).update({'Booking_Status': CommonWords.Cancelled, 'status': UNSTATUS})
                    db.commit()
                    
                    # Update reservation status
                    db.query(models.Room_Reservation).filter(
                        models.Room_Reservation.id == findres_details.id
                    ).update({'Booking_Status': CommonWords.Cancelled, 'status': UNSTATUS})
                    db.commit()
                    
                    # Return success message
                    return JSONResponse(
                        content=jsonable_encoder({'success': True, 'message': 'Reservation Deleted Successfully'}),
                        status_code=status.HTTP_200_OK
                    )
                else:
                    return JSONResponse(
                        content=jsonable_encoder({'success': False, 'message': 'Reservation not found'}),
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                    
        except JWTError:
            return JSONResponse(
                content=jsonable_encoder({'success': False, 'message': 'Authentication failed'}),
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    


#==============================================>>> Room Reservation


#Reservation Home page
@router.get("/add_reservation")
async def Rooms_add_page(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")

            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                today_date = datetime.today().strftime('%Y-%m-%d')
                color_theme = db.query(models.Themes).filter(models.Themes.status == STATUS).first()
                # permision_control = (db.query(models.Role_Permission.Modules_Data).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==STATUS).first())[0]
                # loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==STATUS).first()
                today_rooms_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.Arrival_Date == today_date).filter(models.Room_Reservation.status == STATUS).all()
                customer_data = db.query(models.Customer_Data).filter(models.Customer_Data.status == STATUS).all()
                rooms_data = db.query(models.Room).filter(models.Room.Room_Booking_status == "AVAILABLE").all()
                Room_Type =  db.query(models.Room_Type).filter(models.Room_Type.status == STATUS).all()
                Res_Status = db.query(models.Reservation_Status).filter(models.Reservation_Status.status == STATUS).all()
                identity_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status == STATUS).all()

                
                all_rooms_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.status == STATUS).all()

                def generate_resve_id():
                    latest_reservation = db.query(models.Room_Reservation).order_by(models.Room_Reservation.id.desc()).first()
                
                    if latest_reservation:
                        return 'ROOM_RESERV_'+str(int(latest_reservation.id)+int(1))
                    else:
                        return 'ROOM_RESERV_1'

                calender_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.status == STATUS).all()
                for i in calender_data:
                    if i.updated_at is None:
                        i.updated_at = "null"
                

                return templates.TemplateResponse('front_office/reservation/add_reservation.html', context={'request': request, 'color_theme': color_theme, 'today_rooms_data': today_rooms_data,'rooms_data':rooms_data,
                                                                                                 'customer_data':customer_data,'generate_resve_id':generate_resve_id(),
                                                                                                 'identity_data':identity_data,'Room_Type':Room_Type,'all_rooms_data': all_rooms_data, 'today': today_date,'rooms_data':rooms_data,'graph_data':jsonable_encoder(calender_data),'Res_Status':Res_Status})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#Get Available Rooms
@router.get("/room_availability/{room_id}")
def get_rooms(request: Request,room_id: int, db: Session = Depends(get_db)):
   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                rooms = db.query(models.Room).filter(models.Room.Room_Type_ID == room_id).filter(models.Room.Room_Booking_status=="AVAILABLE").filter(models.Room.Room_Status=="UnBlocking").all()               
               
            return  {"rooms": [{"room_type": Room.id, "room_no": Room.Room_No,"max_adult":Room.Max_Adult_Occupy,"max_child":Room.Max_Child_Occupy} for Room in rooms]}
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)



#Add Room Reservation
@router.post("/room_Reservation")
async def add_room_reservation(
    request: Request,
    db: Session = Depends(get_db),
    genereate_id: str = Form(...),
    salutation: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    mail: str = Form(...),
    mobile_no: int = Form(...),
    Start_Date: str = Form(...),
    End_Date: str = Form(...),
    room_count: str = Form(...),
    no_of_nights: int = Form(...),
    Room_category: str = Form(...),
    available_rooms: str = Form(...),  
    no_of_adults: int = Form(...),
    no_of_childs: int = Form(...),
    Reservation_Status: str = Form(...),
    complementry: str = Form(...),
    personal_id: str = Form(...),
    identity_file: UploadFile = File(...)
):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")

            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

            def generate_code():
                capital_letters = random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4)
                numbers = random.choices('0123456789', k=4)
                return ''.join(capital_letters + numbers)

            start_date = datetime.strptime(Start_Date, "%Y-%m-%d")
            end_date = datetime.strptime(End_Date, "%Y-%m-%d")

           
            available_rooms_list = available_rooms.split(',')
            available_rooms_list = [room.strip() for room in available_rooms_list]  
            available_rooms_set = set(available_rooms_list)

           
            overlapping_reservations = db.query(models.Room_Reservation).filter(
                and_(
                    models.Room_Reservation.Arrival_Date <= end_date,
                    models.Room_Reservation.Departure_Date >= start_date
                )
            ).filter(or_(models.Room_Reservation.Booking_Status == CommonWords.Arrived,models.Room_Reservation.Booking_Status == CommonWords.Confirmed)).all()

           
            existing_reservations = set()
            for res in overlapping_reservations:
                if isinstance(res.Room_No, list):
                    existing_reservations.update(res.Room_No)
                else:
                    
                    existing_reservations.update(res.Room_No.split(','))

           
            room_conflict = not available_rooms_set.isdisjoint(existing_reservations)

            id_proof_type = identity_file.content_type
            extension_1 = id_proof_type.split('/')[-1]
            profile_pick = str(uuid.uuid4())+'.'+str(extension_1)
                       
            with open(f"./templates/static/upload_image/{profile_pick}", "wb+") as file_object_1:
                        shutil.copyfileobj(identity_file.file, file_object_1)
      
            room_amount = db.query(models.Room_Type).filter(models.Room_Type.id==Room_category).first()
            noofnigamt = room_amount.Room_Cost * no_of_nights
            roomcat = []
            roomcat.append(Room_category) 
            if not room_conflict:
                # Debug: Print the Reservation_Status value
                print(f"Reservation Status from form: '{Reservation_Status}'")
                print(f"Reservation Status lower: '{Reservation_Status.lower()}'")
                
                new_reservation = models.Room_Reservation(
                    Room_Reservation_ID=genereate_id,
                    Salutation=salutation,
                    First_Name=first_name,
                    Last_Name=last_name,
                    Phone_Number=mobile_no,
                    Email=mail,
                    Arrival_Date=Start_Date,
                    Departure_Date=End_Date,
                    No_of_rooms=room_count,
                    No_of_nights=no_of_nights,
                    Room_Type=roomcat,
                    Room_No=available_rooms_list,  
                    No_Of_Adults=no_of_adults,
                    No_Of_Childs=no_of_childs,
                    Extra_Bed_Count="0",
                    Extra_Bed_cost="0",
                    Total_Amount=noofnigamt,
                    Tax_Percentage="0",
                    Tax_Amount="0",
                    Discount_Percentage="0",
                    Discount_Amount="0",
                    Overall_Amount=noofnigamt,
                    Room_Complementry=complementry,
                    Booking_Status=Reservation_Status.lower(), 
                    Identity_type=personal_id,
                    Proof_Document=profile_pick,
                    Reservation_Type="Reservation",
                    status="ACTIVE",
                    Confirmation_code=generate_code(),
                    created_by=created_by,
                    company_id=company_id
                )
                db.add(new_reservation)
                db.commit()
                new_record = models.Room_Details(
                    Reservation_Id=new_reservation.id,
                    Room_category=Room_category,
                    Available_rooms=new_reservation.Room_No,
                    Total_Adults=no_of_adults,
                    Total_Child=no_of_childs,
                    Arrival_Date=new_reservation.Arrival_Date,
                    Departure_Date=new_reservation.Departure_Date,
                    Booking_Status=new_reservation.Booking_Status,
                    Reservation_Type=new_reservation.Reservation_Type,
                    Extra_Bed_Count="0",
                    Extra_Bed_cost="0",
                    Room_Complementry=complementry,
                    total_Amount=noofnigamt,
                    status="ACTIVE",
                    created_by=created_by,
                    company_id=company_id
                )

                db.add(new_record)
                db.commit()
                start_date = datetime.strptime(Start_Date, "%Y-%m-%d")
                end_date = datetime.strptime(End_Date, "%Y-%m-%d")

                if start_date.date() <= datetime.today().date() <= end_date.date():
                    if Reservation_Status == "Arrived":
                        db.query(models.Room).filter(models.Room.id==new_reservation.Room_No).update({'Room_Booking_status':Reservation_Status})                    
                        db.commit()
                    if Reservation_Status == "Departures" or Reservation_Status == "Cancelled":
                        db.query(models.Room).filter(models.Room.id==new_reservation.Room_No).update({'Room_Booking_status':"Available"})                    
                        db.commit()
                new_reservation = {"token": new_reservation.token}
                details={'status':"Room Reserved Successfully",'redirectlink':f"/reservation_payment/{new_reservation['token']}" }
                return JSONResponse(content=jsonable_encoder(details), status_code=status.HTTP_200_OK)
            else:
                details={'status':"Room Not Available"}
                return JSONResponse(content=jsonable_encoder(details), status_code=status.HTTP_200_OK)

        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#---------------------------->Reservation Payment 
#Reservation Home page
@router.get("/reservation_payment/{id}")
def Reservation_Payment(request: Request,id:str, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")

            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                today_date = datetime.today().strftime('%Y-%m-%d')
                color_theme = db.query(models.Themes).filter(models.Themes.status == STATUS).first()
                # permision_control = (db.query(models.Role_Permission.Modules_Data).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==STATUS).first())[0]
                # loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==STATUS).first()
                today_rooms_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.Arrival_Date == today_date).filter(models.Room_Reservation.status == STATUS).all()
                rooms_data = db.query(models.Room).filter(models.Room.Room_Booking_status == "AVAILABLE").all()
                Room_Type =  db.query(models.Room_Type).filter(models.Room_Type.status == STATUS).all()
                
                all_rooms_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.token == id,models.Room_Reservation.status == "ACTIVE").first()
                roomdetails_data = db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id == all_rooms_data.id,models.Room_Details.status == "ACTIVE").first()
                Particular_roomtype_data =  db.query(models.Room_Type).filter(models.Room_Type.id == roomdetails_data.Room_category,models.Room_Type.status == STATUS).first()
               
                customers_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.status == STATUS).all()
                dis_data = db.query(models.Discount_Data).filter(models.Discount_Data.status == "ACTIVE").all()
                tax_data = db.query(models.Tax_type).filter(models.Tax_type.status == "ACTIVE").all()
                paymentmethod_data = db.query(models.Payment_Methods).filter(models.Payment_Methods.status == "ACTIVE").all()


              
                

                return templates.TemplateResponse('front_office/reservation/reservation_payment.html', context={'request': request, 'color_theme': color_theme, 'today_rooms_data': today_rooms_data,'rooms_data':rooms_data,
                                                                                            
                                                                                                 'Room_Type':Room_Type,'all_rooms_data': all_rooms_data,'roomdetails_data':roomdetails_data,'Particular_roomtype_data':Particular_roomtype_data,'today': today_date,'rooms_data':rooms_data,'customers_data':customers_data,'dis_data':dis_data,'tax_data':tax_data,'paymentmethod_data':paymentmethod_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)



@router.get("/tax_type/{tax_id}")
def get_tax_type(request: Request,tax_id: int, db: Session = Depends(get_db)):
   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                tax = db.query(models.Tax_type).filter(models.Tax_type.id == tax_id).filter(models.Tax_type.status=="ACTIVE").all()               
               
            return  {"tax": [{"tax_id": Tax_type.id, "tax_type": Tax_type.Tax_Name,"tax_per":Tax_type.Tax_Percentage} for Tax_type in tax]}
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)





@router.get("/dis_type/{dis_id}")
def get_dis_type(request: Request,dis_id: int, db: Session = Depends(get_db)):
   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                dis = db.query(models.Discount_Data).filter(models.Discount_Data.id == dis_id).filter(models.Discount_Data.status=="ACTIVE").all()               
               
            return  {"dis": [{"dis_id": Discount_Data.id, "dis_type": Discount_Data.Discount_Name,"dis_per":Discount_Data.Discount_Percentage} for Discount_Data in dis]}
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/reservation_payment")
async def Reservation_Payment(
    request: Request,
    db: Session = Depends(get_db),
    payment_token: str = Form(...),
    room_amount: str = Form(...),
    extra_bed_count: str = Form(...),
    extra_bed_cost: str = Form(...),
    tax_perce: str = Form(...),
    tax_percentage: str = Form(...),
    discount_perce: str = Form(...),
    discount_percentage: str = Form(...),
    overall_amount: str = Form(...),
    payment: Optional[str] = Form(None),
    paying_amt: str = Form(...),
    balance_amount: str = Form(...),

):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")

            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

            reserv_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==payment_token).first()
            if reserv_data:
                db.query(models.Room_Reservation).filter(models.Room_Reservation.id==reserv_data.id).update({'Extra_Bed_cost':extra_bed_cost,'Total_Amount':float(room_amount)+float(extra_bed_cost),'Tax_Percentage':tax_perce,'Tax_Amount':tax_percentage,'Discount_Percentage':discount_perce,'Discount_Amount':discount_percentage,'Overall_Amount':overall_amount,'Paid_Amount':paying_amt,'Balance_Amount':balance_amount,'Payment_mode':payment})
                db.commit()
                db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id==reserv_data.id).update({'Extra_Bed_cost':extra_bed_cost})
                db.commit()
                if float(paying_amt)>0:
                    payhistory = models.Reser_AmountPaidHistory(Reservation_Id=reserv_data.id,user_id=reserv_data.Email,Amount=paying_amt,paid_date=CommonWords.CURRENTDATE,payment_method=payment,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(payhistory)
                    db.commit()
                    db.refresh(payhistory)
            details={'status':"Payment Updated Successfully",'redirectlink':f"/reservation_list" }
            return JSONResponse(content=jsonable_encoder(details), status_code=status.HTTP_200_OK)
            
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)



#---------------------------------->Room View
@router.get("/room_view")
async def room_view(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status == STATUS).first()
                
                #
                rooms = db.query(
                    models.Room,
                    models.Room_Type.Type_Name .label('type_name')  
                ).join(models.Room_Type, models.Room.Room_Type_ID == models.Room_Type.id) \
                 .filter(models.Room.status == "active") \
                 .all()

             

                arrived_rooms = [{"room": room, "type_name": type_name} for room, type_name in rooms if room.Room_Booking_status == "Arrived"]
                available_rooms = [{"room": room, "type_name": type_name} for room, type_name in rooms if room.Room_Booking_status == "Available"]
                confirmed_rooms = [{"room": room, "type_name": type_name} for room, type_name in rooms if room.Room_Booking_status == "Confirmed"]

               
                rooms_with_type_names = [
                    {
                        "room": room,
                        "type_name": type_name
                    }
                    for room, type_name in rooms
                ]
                

              
                return templates.TemplateResponse('front_office/reservation/room_view.html', context={
                    'request': request,
                    'color_theme': color_theme,
                    'arrived_rooms': arrived_rooms,
                    'available_rooms': available_rooms,
                    'confirmed_rooms': confirmed_rooms,
                    'rooms_with_type_names': rooms_with_type_names,  
                })
        except JWTError as e:
            
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
       
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#get single rooms data
@router.get("/get_roomdetails/{room_id}")
async def get_room_details(request: Request,room_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                room_data = db.query(models.Room).filter(models.Room.id==room_id).filter(models.Room.status=="ACTIVE").first()
                if room_data:
                    rmtype = db.query(models.Room_Type).filter(models.Room_Type.id==room_data.Room_Type_ID).filter(models.Room_Type.status=="ACTIVE").first()
                    if rmtype:
                         room_data.roomtypename = rmtype.Type_Name
                    bedyype = db.query(models.Bed_Type).filter(models.Bed_Type.id==room_data.Bed_Type_ID).filter(models.Bed_Type.status=="ACTIVE").first()
                    if bedyype:
                        room_data.bedtypename = bedyype.Type_Name
                  
                return JSONResponse(content=jsonable_encoder(room_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#------------------------------->Reservation View
@router.get("/reservation_view")
async def reservation_view(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status == STATUS).first()
               
                # Get all reservations
                room_reservations = db.query(models.Room_Reservation).all()

                for reservation in room_reservations:
                    if reservation.Booking_Status:
                        reservation.Booking_Status = reservation.Booking_Status.lower()
              
                # IMPORTANT: Count based on EXACT status values from your database
                # Use the same status values that are stored in your database
                arrived_count = len([res for res in room_reservations if res.Booking_Status == "arrived"])
                departure_count = len([res for res in room_reservations if res.Booking_Status == "departures"])
                confirmed_count = len([res for res in room_reservations if res.Booking_Status == "confirmed"])
                cancelled_count = len([res for res in room_reservations if res.Booking_Status == "cancelled"])
                total_reservations = len(room_reservations)

                # Debug: Print counts to verify
                print(f"Arrived count: {arrived_count}")
                print(f"Departures count: {departure_count}")
                print(f"Confirmed count: {confirmed_count}")
                print(f"Cancelled count: {cancelled_count}")
                print(f"Total: {total_reservations}")

                return templates.TemplateResponse('front_office/reservation/reservation_view.html', context={
                    'request': request,
                    'color_theme': color_theme,
                    'reservations': room_reservations,
                    'arrived_count': arrived_count,
                    'departure_count': departure_count,
                    'confirmed_count': confirmed_count,
                    'cancelled_count': cancelled_count,
                    'total_reservations': total_reservations
                })
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)



#-------------------------------------------------->Booking

@router.get("/booking")
async def Booking(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==STATUS).first()
                bed_type_data = db.query(models.Bed_Type).filter(models.Bed_Type.status==STATUS).all()
                room_type_data = db.query(models.Room_Type).filter(models.Room_Type.status==STATUS).all()
                room_data = db.query(models.Room_Booking).filter(models.Room_Booking.status==STATUS).all()
                return templates.TemplateResponse('front_office/reservation/booking.html', context={'request': request,'color_theme':color_theme,'room_data':room_data,
                                                                                          'bed_type_data':bed_type_data,'room_type_data':room_type_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.post("/booking")
async def Booking_Post(
    request: Request,
    db: Session = Depends(get_db),
    Salutation: str = Form(...),
    First_Name: str = Form(...),
    Last_Name: str = Form(...),
    Phone_Number: str = Form(...),
    Email: str = Form(...),
    Arrival_Date: str = Form(...),
    Departure_Date: str = Form(...),
    No_of_nights: str = Form(...),
    No_of_rooms: str = Form(...),
    No_Of_Adults: str = Form(...),
    No_Of_Childs: str = Form(...),
    Room_Type: List[str] = Form(...),  
):
 
    if len(Room_Type) == 1 and isinstance(Room_Type[0], str):
        Room_Type = Room_Type[0].split(',') if ',' in Room_Type[0] else Room_Type
        
   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                existing_count = db.query(func.count(models.Room_Booking.id)).scalar()
                new_room_booking_id = f"ROOM_BOOK_{existing_count + 1}"

                if isinstance(Room_Type, str):
                    Room_Type = Room_Type.split(',')
                
                room_types = jsonable_encoder(Room_Type)
                
                new_room = models.Room_Booking(
                    Room_Booking_Id=new_room_booking_id,
                    Salutation=Salutation,
                    First_Name=First_Name,
                    Last_Name=Last_Name,
                    Phone_Number=Phone_Number,
                    Email=Email,
                    Arrival_Date=Arrival_Date,
                    Departure_Date=Departure_Date,
                    No_of_nights=No_of_nights,
                    Room_Type=room_types,  
                    No_of_rooms=No_of_rooms,
                    No_Of_Adults=No_Of_Adults,
                    No_Of_Childs=No_Of_Childs,
                    status=STATUS,
                    created_by=created_by,
                    company_id=company_id,
                )

                db.add(new_room)
                db.commit()
                db.refresh(new_room)
                
                return JSONResponse(content=jsonable_encoder('Room Added Successfully'), status_code=status.HTTP_200_OK)

        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            
@router.get("/booking_data_info/{table_id}")
async def Booking_Data_Information(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                particular_data = db.query(models.Room_Booking).filter(models.Room_Booking.id==table_id).filter(models.Room_Booking.status==STATUS).first()
                return JSONResponse(content=jsonable_encoder(particular_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
 
@router.post("/update_booking")
async def update_Booking(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_Salutation : str=Form(...),edit_First_Name:str=Form(...),edit_Last_Name:str=Form(...),edit_room_type:List[str]=Form(...),edit_Phone_Number:str=Form(...),edit_Email:str=Form(...),edit_Arrival_Date:str=Form(...),edit_Departure_Date:str=Form(...),edit_No_of_nights:str=Form(...),edit_No_of_rooms:str=Form(...),edit_No_Of_Childs :str=Form(...),edit_No_Of_Adults:str=Form(...)):   
    if len(edit_room_type) == 1 and isinstance(edit_room_type[0], str):
        Room_Type = edit_room_type[0].split(',') if ',' in edit_room_type[0] else edit_room_type
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                    if isinstance(Room_Type, str):
                       Room_Type = Room_Type.split(',')
                    room_types = jsonable_encoder(Room_Type)
                    db.query(models.Room_Booking).filter(models.Room_Booking.id==edit_id).update({'Salutation':edit_Salutation,'First_Name':edit_First_Name,'Last_Name':edit_Last_Name,
                                                                                  'Room_Type':room_types,'Phone_Number':edit_Phone_Number,
                                                                                  'Email':edit_Email,'Arrival_Date':edit_Arrival_Date,
                                                                                  'Departure_Date':edit_Departure_Date,'No_of_nights':edit_No_of_nights,
                                                                                  'No_of_rooms':edit_No_of_rooms,'No_Of_Adults':edit_No_Of_Adults,'No_Of_Childs':edit_No_Of_Childs})                    
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Room Updated Successfully'),status_code=status.HTTP_200_OK)
                
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/delete_booking_id/{table_id}")
async def Delete_Booking(request: Request, table_id: int, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                # Check if the room exists before deleting
                room_exists = db.query(models.Room_Booking).filter(
                    models.Room_Booking.id == table_id,
                    models.Room_Booking.status == STATUS
                ).first()
                
                if room_exists:
                    # Soft delete (update status to UNSTATUS)
                    db.query(models.Room_Booking).filter(models.Room_Booking.id == table_id).update({'status': UNSTATUS})
                    db.commit()
                    
                    # Return success message
                    return JSONResponse(
                        content=jsonable_encoder({'success': True, 'message': 'Room Deleted Successfully'}),
                        status_code=status.HTTP_200_OK
                    )
                else:
                    # Room not found
                    return JSONResponse(
                        content=jsonable_encoder({'success': False, 'message': 'Room not found'}),
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                    
        except JWTError:
            return JSONResponse(
                content=jsonable_encoder({'success': False, 'message': 'Authentication failed'}),
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    
@router.get("/room_booking")
async def Room_Booking(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                hallnames_results = db.query(models.Room_Type).filter(models.Room_Type.status == "ACTIVE").all()
                for ham in hallnames_results:
                    ham.tablecount = db.query(models.Room).filter(models.Room.Room_Type_ID ==ham.id,models.Room.status == "ACTIVE").count()
                    ham.tableall = db.query(models.Room).filter(models.Room.Room_Type_ID ==ham.id,models.Room.status == "ACTIVE").all()
                    for tbda in ham.tableall:
                        tableall = db.query(models.Reservation_Status).filter(models.Reservation_Status.Reservation_Status == tbda.Room_Booking_status,models.Reservation_Status.status == "ACTIVE").first()
                        if tableall:
                            tbda.roomcolor = tableall.Color
                           
                def generate_resve_id():
                    latest_reservation = db.query(models.Room_Reservation).order_by(models.Room_Reservation.id.desc()).first()
                
                    if latest_reservation:
                        return 'ROOM_RESERV_'+str(int(latest_reservation.id)+int(1))
                    else:
                        return 'ROOM_RESERV_1' 

                color_theme = db.query(models.Themes).filter(models.Themes.status==STATUS).first()
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==STATUS).first()
                
                role_data = db.query(models.Role).filter(models.Role.status==STATUS).all()
                
                Res_Status = db.query(models.Reservation_Status).filter(models.Reservation_Status.status == STATUS).all()
                identity_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status == STATUS).all()
                return templates.TemplateResponse('front_office/reservation/take_order.html', context={'request': request,'color_theme':color_theme,
                                                                                 'loginer_data':loginer_data,'role_data':role_data,'hallnames_results':hallnames_results,'generate_resve_id':generate_resve_id(),'identity_data':identity_data,'Res_Status':Res_Status})
        except JWTError:
            return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.put('/check_rooms/{check}')
def Check_Rooms(request: Request,check: str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                selectable = check.split(',')
                int_chairs = [int(chair) for chair in selectable]
                tabdetai = []
                for intsel in int_chairs:
                    tabdetails=db.query(models.Room).filter(models.Room.id==str(intsel),models.Room.status=="ACTIVE").first()
                    
                    if tabdetails:
                        roomtydetails=db.query(models.Room_Type).filter(models.Room_Type.id==tabdetails.Room_Type_ID,models.Room_Type.status=="ACTIVE").first()
                   
                        tabdetai1={
                            "roomtype_id" : roomtydetails.id,
                            "roomtype_name" : roomtydetails.Type_Name,
                            "room_id" : tabdetails.id,
                            "room_no" : tabdetails.Room_No,
                            "max_adult" : tabdetails.Max_Adult_Occupy,
                            "max_child" : tabdetails.Max_Child_Occupy,
                        }  
                        tabdetai.append(tabdetai1)  
                
                json_compatible_item_data = jsonable_encoder(tabdetai)
                return JSONResponse(content=json_compatible_item_data)
            
        except JWTError:
            return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# Add Room Reservation Group
@router.post("/group_reservation")
async def add_room_reservation(
    request: Request,
    db: Session = Depends(get_db),
    genereate_id: str = Form(...),
    salutation: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    mail: str = Form(...),
    mobile_no: int = Form(...),
    Start_Date: str = Form(...),
    End_Date: str = Form(...),
    room_count: str = Form(...),
    no_of_nights: int = Form(...),
    roomtype_id: List[str] = Form(...),
    room_id: List[str] = Form(...),
    rate_type: List[str] = Form(...),
    no_of_adults: List[str] = Form(...),
    no_of_childs: List[str] = Form(...),
    complementry: Optional[List[str]] = Form(None),
    Reservation_Status: str = Form(...),
    personal_id: str = Form(...),
    identity_file: UploadFile = File(...)
):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by = payload.get("user_id")
            company_id = payload.get("company_id")

            if created_by is None:
                return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

            totamt = 0
            totadult = 0
            totchild = 0

            def generate_code():
                return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4) + random.choices('0123456789', k=4))

            start_date = datetime.strptime(Start_Date, "%Y-%m-%d")
            end_date = datetime.strptime(End_Date, "%Y-%m-%d")

            available_rooms_set = set(room_id)

            overlapping_reservations = db.query(models.Room_Reservation).filter(
                and_(
                    models.Room_Reservation.Arrival_Date <= end_date,
                    models.Room_Reservation.Departure_Date >= start_date
                )
            ).filter(
                or_(
                    models.Room_Reservation.Booking_Status == CommonWords.Arrived,
                    models.Room_Reservation.Booking_Status == CommonWords.Confirmed
                )
            ).all()

            existing_reservations = set()
            for res in overlapping_reservations:
                if isinstance(res.Room_No, list):
                    existing_reservations.update(res.Room_No)
                else:
                    existing_reservations.update(res.Room_No.split(','))

            if not available_rooms_set.isdisjoint(existing_reservations):
                return JSONResponse(content={"status": "Room Not Available", "redirectlink": "/room_booking"}, status_code=200)

            id_proof_type = identity_file.content_type
            extension_1 = id_proof_type.split('/')[-1]
            profile_pick = f"{uuid.uuid4()}.{extension_1}"

            with open(f"./templates/static/upload_image/{profile_pick}", "wb+") as file_object_1:
                shutil.copyfileobj(identity_file.file, file_object_1)

            reservation_type = 'Reservation' if len(room_id) == 1 else 'Group Reservation'

            # Calculate total amount based on rate type
            for room_cat, availro, rt, na, nc in zip(roomtype_id, room_id, rate_type, no_of_adults, no_of_childs):
                room_amount = db.query(models.Room_Type).filter(models.Room_Type.id == room_cat).first()
                rate_value = 0

                if rt == "daily_rate":
                    rate_value = room_amount.Daily_Rate
                elif rt == "weekly_rate":
                    rate_value = room_amount.Weekly_Rate
                elif rt == "bed_only_rate":
                    rate_value = room_amount.Bed_Only_Rate
                elif rt == "bed_breakfast_rate":
                    rate_value = room_amount.Bed_And_Breakfast_Rate
                elif rt == "half_board_rate":
                    rate_value = room_amount.Half_Board_Rate
                elif rt == "full_board_rate":
                    rate_value = room_amount.Full_Board_Rate
                else:
                    rate_value = room_amount.Room_Cost

                totamt += float(rate_value) * no_of_nights
                totadult += int(na)
                totchild += int(nc)
            new_reservation = models.Room_Reservation(
                Room_Reservation_ID=genereate_id,
                Salutation=salutation,
                First_Name=first_name,
                Last_Name=last_name,
                Phone_Number=mobile_no,
                Email=mail,
                Arrival_Date=Start_Date,
                Departure_Date=End_Date,
                No_of_rooms=room_count,
                No_of_nights=no_of_nights,
                Room_Type=', '.join(roomtype_id),
                Rate_Type=', '.join(rate_type),
                Room_No=', '.join(room_id),
                No_Of_Adults=totadult,
                No_Of_Childs=totchild,
                Extra_Bed_Count="0",
                Extra_Bed_cost="0",
                Total_Amount=totamt,
                Tax_Percentage="0",
                Tax_Amount="0",
                Discount_Percentage="0",
                Discount_Amount="0",
                Overall_Amount=totamt,
                Booking_Status=Reservation_Status,
                Identity_type=personal_id,
                Proof_Document=profile_pick,
                Room_Complementry=', '.join(complementry) if complementry else 'no',
                Reservation_Type=reservation_type,
                status="ACTIVE",
                Confirmation_code=generate_code(),
                created_by=created_by,
                company_id=company_id
            )
            db.add(new_reservation)
            db.commit()

            
            complementry = complementry or ["no"] * len(room_id)

            for room_cat, availro, rt, na, nc, rc in zip(roomtype_id, room_id, rate_type, no_of_adults, no_of_childs, complementry):
                room_amount = db.query(models.Room_Type).filter(models.Room_Type.id == room_cat).first()

                if rt == "daily_rate":
                    rate_value = room_amount.Daily_Rate
                elif rt == "weekly_rate":
                    rate_value = room_amount.Weekly_Rate
                elif rt == "bed_only_rate":
                    rate_value = room_amount.Bed_Only_Rate
                elif rt == "bed_breakfast_rate":
                    rate_value = room_amount.Bed_And_Breakfast_Rate
                elif rt == "half_board_rate":
                    rate_value = room_amount.Half_Board_Rate
                elif rt == "full_board_rate":
                    rate_value = room_amount.Full_Board_Rate
                else:
                    rate_value = room_amount.Room_Cost

                tottamt = float(rate_value) * no_of_nights

                new_record = models.Room_Details(
                    Reservation_Id=new_reservation.id,
                    Room_category=room_cat,
                    Available_rooms=availro,
                    Total_Adults=na,
                    Total_Child=nc,
                    Arrival_Date=Start_Date,
                    Departure_Date=End_Date,
                    Booking_Status=Reservation_Status,
                    Reservation_Type=reservation_type,
                    Extra_Bed_Count="0",
                    Extra_Bed_cost="0",
                    Room_Complementry= rc if rc else 'no',
                    total_Amount=tottamt,
                    status="ACTIVE",
                    created_by=created_by,
                    company_id=company_id
                )
                db.add(new_record)
                db.commit()

                if start_date.date() <= datetime.today().date() <= end_date.date():
                    if Reservation_Status == "Arrived":
                        db.query(models.Room).filter(models.Room.id == availro).update({'Room_Booking_status': Reservation_Status})
                        db.commit()
                    if Reservation_Status in ["Departures", "Cancelled"]:
                        db.query(models.Room).filter(models.Room.id == availro).update({'Room_Booking_status': "Available"})
                        db.commit()

            return JSONResponse(
                content={"status": "Room Reserved Successfully", "redirectlink": f"/reservationgroup_payment/{new_reservation.token}"},
                status_code=200
            )

        except JWTError:
            return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
#---------------------------->Reservation Group Payment 
#Reservation Group Payment
@router.get("/reservationgroup_payment/{id}")
def ReservationGroup_Payment(request: Request, id: str, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")

            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

            today_date = datetime.today().strftime('%Y-%m-%d')
            color_theme = db.query(models.Themes).filter(models.Themes.status == STATUS).first()
            today_rooms_data = db.query(models.Room_Reservation).filter(
                models.Room_Reservation.Arrival_Date == today_date,
                models.Room_Reservation.status == STATUS
            ).all()
            rooms_data = db.query(models.Room).filter(models.Room.Room_Booking_status == "AVAILABLE").all()
            Room_Type = db.query(models.Room_Type).filter(models.Room_Type.status == STATUS).all()

            all_rooms_data = db.query(models.Room_Reservation).filter(
                models.Room_Reservation.token == id,
                models.Room_Reservation.status == "ACTIVE"
            ).first()

            roomdetails_data = db.query(models.Room_Details).filter(
                models.Room_Details.Reservation_Id == all_rooms_data.id,
                models.Room_Details.status == "ACTIVE"
            ).all()

            customers_data = db.query(models.Room_Reservation).filter(
                models.Room_Reservation.status == STATUS
            ).all()
            dis_data = db.query(models.Discount_Data).filter(models.Discount_Data.status == "ACTIVE").all()
            tax_data = db.query(models.Tax_type).filter(models.Tax_type.status == "ACTIVE").all()
            paymentmethod_data = db.query(models.Payment_Methods).filter(models.Payment_Methods.status == "ACTIVE").all()

            # 🔑 Calculate total amount using selected rate type
            calculated_total = 0
            for room_detail in roomdetails_data:
                room_type_obj = db.query(models.Room_Type).filter(
                    models.Room_Type.id == room_detail.Room_category
                ).first()

                selected_rate = None
                if all_rooms_data.Rate_Type and isinstance(all_rooms_data.Rate_Type, list):
                    index = all_rooms_data.Room_No.index(room_detail.Available_rooms)
                    rate_type_selected = all_rooms_data.Rate_Type[index]

                    if rate_type_selected == "daily_rate":
                        selected_rate = room_type_obj.Daily_Rate
                    elif rate_type_selected == "weekly_rate":
                        selected_rate = room_type_obj.Weekly_Rate
                    elif rate_type_selected == "bed_only_rate":
                        selected_rate = room_type_obj.Bed_Only_Rate
                    elif rate_type_selected == "bed_breakfast_rate":
                        selected_rate = room_type_obj.Bed_And_Breakfast_Rate
                    elif rate_type_selected == "half_board_rate":
                        selected_rate = room_type_obj.Half_Board_Rate
                    elif rate_type_selected == "full_board_rate":
                        selected_rate = room_type_obj.Full_Board_Rate

                    calculated_total += float(selected_rate)

                else:
                    rate_type_selected = None
                
                # Fallback to Room_Cost
                if not selected_rate:
                    selected_rate = room_type_obj.Room_Cost
                    calculated_total += float(selected_rate) * all_rooms_data.No_of_nights

            return templates.TemplateResponse(
                'front_office/reservation/reservationgroup_payment.html',
                context={
                    'request': request,
                    'color_theme': color_theme,
                    'today_rooms_data': today_rooms_data,
                    'rooms_data': rooms_data,
                    'Room_Type': Room_Type,
                    'all_rooms_data': all_rooms_data,
                    'roomdetails_data': roomdetails_data,
                    'today': today_date,
                    'customers_data': customers_data,
                    'dis_data': dis_data,
                    'tax_data': tax_data,
                    'paymentmethod_data': paymentmethod_data,
                    'calculated_total': calculated_total  # 💰 Pass calculated total
                }
            )

        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/reservationgroup_payment")
async def Reservation_Payment(
    request: Request,
    db: Session = Depends(get_db),
    payment_token: str = Form(...),
    room_amount: str = Form(...),
    extra_bed_count: str = Form(...),
    extra_bed_cost: str = Form(...),
    tax_perce: str = Form(...),
    tax_percentage: str = Form(...),
    discount_perce: str = Form(...),
    discount_percentage: str = Form(...),
    overall_amount: str = Form(...),
    payment: Optional[str] = Form(None),
    paying_amt: str = Form(...),
    balance_amount: str = Form(...),
    extra_amount: str = Form(...),
    extra_charges: str = Form(...)

):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")

            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

            reserv_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==payment_token).first()
            if reserv_data:
                db.query(models.Room_Reservation).filter(models.Room_Reservation.id==reserv_data.id).update({'Extra_Bed_cost':extra_bed_cost,'extra_charges':extra_charges,'Total_Amount':room_amount,'Tax_Percentage':tax_perce,'Tax_Amount':tax_percentage,'Discount_Percentage':discount_perce,'Discount_Amount':discount_percentage,'Overall_Amount':overall_amount,'Paid_Amount':paying_amt,'Balance_Amount':balance_amount,'Extra_Amount':extra_amount,'Payment_mode':payment})
                db.commit()
                db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id==reserv_data.id).update({'Extra_Bed_cost':extra_bed_cost})
                db.commit()
                if float(paying_amt)>0:
                    payhistory = models.Reser_AmountPaidHistory(Reservation_Id=reserv_data.id,user_id=reserv_data.Email,Amount=paying_amt,paid_date=CommonWords.CURRENTDATE,payment_method=payment,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(payhistory)
                    db.commit()
                    db.refresh(payhistory)
            details={'status':"Payment Updated Successfully",'redirectlink':f"/reservation_list" }
            return JSONResponse(content=jsonable_encoder(details), status_code=status.HTTP_200_OK)
            
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)



#=====================================>>> CheckOut List
@router.get("/checkout_list")
def Checkout_List(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                permision_control = (db.query(models.Role_Permission).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first())
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.Booking_Status==CommonWords.Arrived).filter(models.Room_Reservation.Arrival_Date <= CommonWords.CURRENTDATE,models.Room_Reservation.status==CommonWords.STATUS).all()
                payment_method = db.query(models.Payment_Methods).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
              
                return templates.TemplateResponse('front_office/reservation/checkout_list.html', context={'request': request,'color_theme':color_theme,'reservation_data':reservation_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,'payment_method':payment_method})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/reservation_checkout/{id}")
async def Reservation_Checkout(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                reserva_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==id,models.Room_Reservation.status==STATUS).first()
                if reserva_data:
                    room_data = db.query(models.Room_Details).filter(models.Room_Details.Booking_Status==CommonWords.Arrived).filter(models.Room_Details.Reservation_Id==reserva_data.id,models.Room_Details.status==STATUS).all()
                    if room_data:
                        for rd in room_data:
                            db.query(models.Room).filter(models.Room.id==rd.Available_rooms).update({'Room_Booking_status':CommonWords.AVAILABLE})
                            db.commit()
                            db.query(models.Room_Details).filter(models.Room_Details.id==rd.id).update({'Booking_Status':CommonWords.Departures})
                            db.commit()
                    db.query(models.Room_Reservation).filter(models.Room_Reservation.id==reserva_data.id).update({'Booking_Status':CommonWords.Departures})
                    db.commit()
                    
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                permision_control = (db.query(models.Role_Permission).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first())
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.Reservation_Type==CommonWords.Reser_Type_Reservation,models.Room_Reservation.status==CommonWords.STATUS).order_by(models.Room_Reservation.id.desc()).all()
                for resd in reservation_data:
                    if resd.Arrival_Date <= datetime.today().date() <= resd.Departure_Date:
                        resd.currentdate = "yes"
                    else:
                        resd.currentdate = "no"
                       
                payment_method = db.query(models.Payment_Methods).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
              
                identity_proofs = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status == "ACTIVE").all()

                return templates.TemplateResponse('front_office/reservation/reservation_list.html', context={'request': request,'color_theme':color_theme,'reservation_data':reservation_data,'permision_control':permision_control,
                                                                                          'identity_proofs':identity_proofs,'loginer_data':loginer_data,'payment_method':payment_method})
                                            
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)




#-------------------------------->Group Reservation


#=====================================>>> Group Reservation List
@router.get("/groupreservation_list")
def Checkout_List(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                permision_control = (db.query(models.Role_Permission).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first())
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.Reservation_Type == CommonWords.Reser_Type_GroupReservation,models.Room_Reservation.status==CommonWords.STATUS).order_by(models.Room_Reservation.id.desc()).all()
                for resd in reservation_data:
                    if resd.Arrival_Date <= datetime.today().date() <= resd.Departure_Date:
                        resd.currentdate = "yes"
                    else:
                        resd.currentdate = "no"
                       
                payment_method = db.query(models.Payment_Methods).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
              
                return templates.TemplateResponse('front_office/reservation/reservationgroup_list.html', context={'request': request,'color_theme':color_theme,'reservation_data':reservation_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,'payment_method':payment_method})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)



#----------------------------->Room Reservation Edit

#get single rooms data
@router.get("/get_room_id/{room_id}")
async def room_id_taking(request: Request,room_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                service_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.id==room_id).filter(models.Room_Reservation.status=="ACTIVE").first()
                return JSONResponse(content=jsonable_encoder(service_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)




# Update reservation details
@router.post("/rooms_Reservation_update")
async def update_rooms_reservation(
    request: Request, 
    db: Session = Depends(get_db), 
    edit_id: str = Form(...),
    edit_salutation: str = Form(...),
    edit_first_name: str = Form(...),
    edit_last_name: str = Form(...),
    edit_mail: str = Form(...),
    edit_mobile_no: int = Form(...),
    edit_Start_Date: str = Form(...),
    edit_End_Date: str = Form(...),
    edit_room_count: str = Form(...),
    edit_no_of_nights: int = Form(...),
    edit_Room_category: str = Form(...),
    edit_available_rooms: str = Form(...),  
    edit_no_of_adults: int = Form(...),
    edit_no_of_childs: int = Form(...),
    edit_Reservation_Status: str = Form(...),
    edit_complementry: Optional[bool] = Form(False),
    edit_personal_id: str = Form(...),
    edit_identity_file: UploadFile = File(...)):   
    
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
              
                
                # Update the database
                db.query(models.Room_Reservation).filter(models.Room_Reservation.id == edit_id).update({
                    'Salutation': edit_salutation,
                    'First_Name': edit_first_name,
                    'Last_Name': edit_last_name,
                    'Email': edit_mail,
                    'Phone_Number': edit_mobile_no,
                    'Arrival_Date': edit_Start_Date,
                    'Departure_Date': edit_End_Date,
                    'No_of_rooms': edit_room_count,
                    'No_of_nights': edit_no_of_nights,
                    'Room_Type': edit_Room_category,
                    'Room_No': edit_available_rooms,
                    'No_Of_Adults': edit_no_of_adults,
                    'No_Of_Childs': edit_no_of_childs,
                    'Booking_Status': edit_Reservation_Status,
                    'Room_Complementry': edit_complementry,
                    'Identity_type': edit_personal_id,
                    'Proof_Document': edit_identity_file,  # Store the file path
                })
                
                db.commit()
                return JSONResponse(content=jsonable_encoder('Room Reserved Updated Successfully'), status_code=status.HTTP_200_OK)

        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse('../login/login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/edit_reservation/{id}")
async def Edit_reservation(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                hallnames_results = db.query(models.Room_Type).filter(models.Room_Type.status == "ACTIVE").all()
                for ham in hallnames_results:
                    ham.tablecount = db.query(models.Room).filter(models.Room.Room_Type_ID ==ham.id,models.Room.status == "ACTIVE").count()
                    ham.tableall = db.query(models.Room).filter(models.Room.Room_Type_ID ==ham.id,models.Room.status == "ACTIVE").all()
                    for tbda in ham.tableall:
                        tableall = db.query(models.Reservation_Status).filter(models.Reservation_Status.Reservation_Status == tbda.Room_Booking_status,models.Reservation_Status.status == "ACTIVE").first()
                        if tableall:
                            tbda.roomcolor = tableall.Color
                           
                def generate_resve_id():
                    latest_reservation = db.query(models.Room_Reservation).order_by(models.Room_Reservation.id.desc()).first()
                
                    if latest_reservation:
                        return 'ROOM_RESERV_'+str(int(latest_reservation.id)+int(1))
                    else:
                        return 'ROOM_RESERV_1' 

                color_theme = db.query(models.Themes).filter(models.Themes.status==STATUS).first()
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==STATUS).first()
                
                role_data = db.query(models.Role).filter(models.Role.status==STATUS).all()
                
                Res_Status = db.query(models.Reservation_Status).filter(models.Reservation_Status.status == STATUS).all()
                identity_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status == STATUS).all()
                
                findres_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    reservation_data = db.query(models.Room_Reservation).filter(models.Room_Reservation.id==findres_details.id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    reser_room_data = db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id==findres_details.id,models.Room_Details.status==CommonWords.STATUS).all()
                    for resdat in reser_room_data:
                        roomtype_data = db.query(models.Room_Type).filter(models.Room_Type.id==resdat.Room_category,models.Room_Type.status==CommonWords.STATUS).first() 
                        if roomtype_data:
                            resdat.room_type = roomtype_data.Type_Name
                            resdat.roomcost = roomtype_data.Room_Cost
                            resdat.extraonebetcost = roomtype_data.Bed_Cost 
                        room_data = db.query(models.Room).filter(models.Room.id==resdat.Available_rooms,models.Room.status==CommonWords.STATUS).first() 
                        if room_data:
                            resdat.room_no = room_data.Room_No 
                if findres_details:
                    payment_data = db.query(models.Reser_AmountPaidHistory).filter(models.Reser_AmountPaidHistory.Reservation_Id==findres_details.id,models.Reser_AmountPaidHistory.status==CommonWords.STATUS).all()
                
                
                
                
                return templates.TemplateResponse('front_office/reservation/edit_reservation.html', context={'request': request,'color_theme':color_theme,
                                                                                 'reser_room_data':reser_room_data,'reservation_data':reservation_data,'loginer_data':loginer_data,'role_data':role_data,'hallnames_results':hallnames_results,'generate_resve_id':generate_resve_id(),'identity_data':identity_data,'Res_Status':Res_Status})
        except JWTError:
            return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/add_item1/{id}")
async def Bar_OrderAddItem1(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                find=db.query(models.Room).filter(models.Room.id==id,models.Room.status==STATUS).first()
                if find:
                    roomtype=db.query(models.Room_Type).filter(models.Room_Type.id==find.Room_Type_ID,models.Room_Type.status==STATUS).first()
                    if roomtype:
                        find.roomtypename = roomtype.Type_Name
                        find.roomcost = roomtype.Room_Cost
                        find.extraonebetcost = roomtype.Bed_Cost
                json_compatible_item_data = jsonable_encoder(find)
                return JSONResponse(content=json_compatible_item_data,status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# Update Group Reservation Details
@router.post("/groupeservation_update")
async def Group_Reservation_Update(
    request: Request, 
    db: Session = Depends(get_db), 
    edit_token: str = Form(...),
    edit_roomdetails_id: List[str] = Form(...),
    old_room_type: List[str] = Form(...),
    old_roomname: List[str] = Form(...),
    max_adult: List[str] = Form(...),
    max_child: List[str] = Form(...),
    complementry: List[str] = Form(...),
    old_bed_count: List[str] = Form(...),
    old_extr_bed_amt: List[str] = Form(...),
    old_room_amt: List[str] = Form(...),
    new_room_type: List[str] = Form(...),
    new_roomname: List[str] = Form(...),
    new_max_adult: List[str] = Form(...),
    new_max_child: List[str] = Form(...),
    new_complementry: List[str] = Form(...),
    extra_bed_count: List[str] = Form(...),  
    extr_bed_amt: List[str] = Form(...),
    room_amt: List[str] = Form(...),
    overall_amount: str = Form(...),
    tax_amount: str = Form(...),
    discount_amount: str = Form(...),
    final_pay_amount: str = Form(...),
    oldtotroom: str = Form(...),newtotroom: str = Form(...)
    ,arrival_date: str = Form(...),depature_date: str = Form(...),total_days: str = Form(...)):   
    
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            Loginer_Role: str = payload.get("user_role_id")
            
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                oldtotadult = 0
                oldtotchild = 0
                newtotadult = 0
                newtotchild = 0
                ovtotadult = 0
                ovtotchild = 0
                ovtotrooms = int(oldtotroom) + int(newtotroom)
                oldexbedcount = 0
                newexbedcount = 0
                ovexbedcount=0
                ovroomtype = []
                ovroomno = []
                findres_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==edit_token,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    edit_roomdetails_id = json.loads(edit_roomdetails_id[0])
                    old_room_type = json.loads(old_room_type[0])
                    old_roomname = json.loads(old_roomname[0])
                    max_adult = json.loads(max_adult[0])
                    max_child = json.loads(max_child[0])
                    complementry = json.loads(complementry[0])
                    old_bed_count = json.loads(old_bed_count[0])
                    old_extr_bed_amt = json.loads(old_extr_bed_amt[0])
                    old_room_amt = json.loads(old_room_amt[0])
                    for s,d,i,j,k,l,m,n,o in zip(old_room_type,old_roomname,edit_roomdetails_id,max_adult,max_child,complementry,old_bed_count,old_extr_bed_amt,old_room_amt):
                        if i:
                            db.query(models.Room_Details).filter(models.Room_Details.id == i).update({
                                'Total_Adults':j,'Total_Child':k,'Room_Complementry':l,'Extra_Bed_Count':m,'Extra_Bed_cost':n,'total_Amount':o
                            })
                        
                            db.commit()
                            oldtotadult += int(j)
                            oldtotchild += int(k)
                            oldexbedcount += int(m)
                            ovroomtype.append(s)
                            ovroomno.append(d)
                    new_room_type = json.loads(new_room_type[0])
                    new_roomname = json.loads(new_roomname[0])
                    new_max_adult = json.loads(new_max_adult[0])
                    new_max_child = json.loads(new_max_child[0])
                    new_complementry = json.loads(new_complementry[0])
                    extra_bed_count = json.loads(extra_bed_count[0])
                    extr_bed_amt = json.loads(extr_bed_amt[0])
                    room_amt = json.loads(room_amt[0])
                    
                    for gg,hh,ii,jj,kk,ll,mm,nn in zip(new_room_type,new_roomname,new_max_adult,new_max_child,new_complementry,extra_bed_count,extr_bed_amt,room_amt):
                        if gg:
                         
                            new_record = models.Room_Details(
                                Reservation_Id=findres_details.id,
                                Room_category=gg,
                                Available_rooms=hh,
                                Total_Adults=ii,
                                Total_Child=jj,
                                Arrival_Date=arrival_date,
                                Departure_Date=depature_date,
                                Booking_Status=findres_details.Booking_Status,
                                Reservation_Type=findres_details.Reservation_Type,
                                Extra_Bed_Count=ll,
                                Extra_Bed_cost=mm,
                                Room_Complementry=kk,
                                total_Amount=nn,
                                status="ACTIVE",
                                created_by=created_by,
                                company_id=company_id
                            )

                            db.add(new_record)
                            db.commit()
                            newtotadult +=int(ii)
                            newexbedcount +=int(jj)
                            oldexbedcount +=int(ll)
                            ovroomtype.append(gg)
                            ovroomno.append(hh)
                            start_date = datetime.strptime(str(arrival_date), "%Y-%m-%d")
                            end_date = datetime.strptime(str(depature_date), "%Y-%m-%d")

                            if start_date.date() <= datetime.today().date() <= end_date.date():
                                if findres_details.Booking_Status == "Confirmed" or findres_details.Booking_Status == "Arrived":
                                    db.query(models.Room).filter(models.Room.id==hh).update({'Room_Booking_status':findres_details.Booking_Status})                    
                                    db.commit()
                                if findres_details.Booking_Status == "Departures" or findres_details.Booking_Status == "Cancelled":
                                    db.query(models.Room).filter(models.Room.id==hh).update({'Room_Booking_status':"Available"})                    
                                    db.commit()
                                
                    ovtotadult = oldtotadult + newtotadult
                    ovtotchild = oldtotchild +  newtotchild 
                    ovexbedcount = oldexbedcount +  newexbedcount
                    db.query(models.Room_Reservation).filter(models.Room_Reservation.id == findres_details.id).update({
                        'Arrival_Date':arrival_date,'Departure_Date':depature_date,'No_of_nights':total_days,'Room_Type':ovroomtype,'Room_No':ovroomno,'No_of_rooms':ovtotrooms,'No_Of_Adults':ovtotadult,'No_Of_Childs':ovtotchild,'Extra_Bed_Count':ovexbedcount,'Total_Amount':overall_amount,'Tax_Amount':tax_amount,'Discount_Amount':discount_amount,'Overall_Amount':final_pay_amount
                    })
                
                    db.commit()
                return JSONResponse(content=jsonable_encoder('Room Reserved Updated Successfully'), status_code=status.HTTP_200_OK)

        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse('../login/login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#Delete Room Reserved Update Reservation
@router.delete("/delete_roomreserved/{id}")
async def Delete_RoomReservation(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                findrom_details = db.query(models.Room_Details).filter(models.Room_Details.token==id,models.Room_Details.status==CommonWords.STATUS).first()
                if findrom_details:
                    findrom_oldromcat = findrom_details.Room_category
                    findrom_oldavailrooms = findrom_details.Available_rooms
                    findrom_oldtotadu = findrom_details.Total_Adults
                    findrom_oldtotchild = findrom_details.Total_Child
                    findrom_oldexbedcount = findrom_details.Extra_Bed_Count
                    findrom_oldexbedcos = findrom_details.Extra_Bed_cost 
                    findrom_oldtotamt = findrom_details.total_Amount 
                   
                    findres_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.id==findrom_details.Reservation_Id,models.Room_Reservation.status==CommonWords.STATUS).first()
                    findres_oldromtype = findres_details.Room_Type
                    findres_oldromno = findres_details.Room_No
                    findres_oldnoofroms = findres_details.No_of_rooms 
                    findres_oldnoofadul = findres_details.No_Of_Adults 
                    findres_oldnoofchild = findres_details.No_Of_Childs 
                    findres_oldextbedcou = findres_details.Extra_Bed_Count
                    findres_oldextbedcost = findres_details.Extra_Bed_cost 
                    findres_oldtotamt = findres_details.Total_Amount 
                    findres_oldtaxper = findres_details.Tax_Percentage
                    findres_oldtaxamot = findres_details.Tax_Amount 
                    findres_olddisper = findres_details.Discount_Percentage
                    findres_olddisamt = findres_details.Discount_Amount
                    findres_oldovamt = findres_details.Overall_Amount 
                    findres_oldromtype.remove(str(findrom_oldromcat))
                    findres_oldromno.remove(str(findrom_oldavailrooms))
                    new_noofroms = findres_oldnoofroms - 1
                    new_noofadult = int(findres_oldnoofadul) - int(findrom_oldtotadu)
                    new_noofchild = int(findres_oldnoofchild) - int(findrom_oldtotchild)
                    new_exbedcount = int(findres_oldextbedcou) - int(findrom_oldexbedcount)
                    new_extbedcost = findres_oldextbedcost - findrom_oldexbedcos
                    new_romtotamt = findres_oldtotamt - findrom_oldtotamt
                    new_taxamt = new_romtotamt*findres_oldtaxper/100
                    new_disamt = new_romtotamt*findres_olddisper/100
                    new_ovamt = new_romtotamt + new_taxamt + new_disamt
                    
                    db.query(models.Room_Reservation).filter(models.Room_Reservation.id==findres_details.id).update({'Room_Type':findres_oldromtype,'Room_No':findres_oldromno,'No_of_rooms':new_noofroms,'No_Of_Adults':new_noofadult,'No_Of_Childs':new_noofchild,'Extra_Bed_Count':new_exbedcount,'Extra_Bed_cost':new_extbedcost,'Total_Amount':new_romtotamt,'Tax_Amount':new_taxamt,'Discount_Amount':new_disamt,'Overall_Amount':new_ovamt})                    
                    db.commit()
                    db.query(models.Room_Details).filter(models.Room_Details.token==id).delete()
                    db.commit()
                return "Success"
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#Checkout Room Reserved Update Reservation
@router.get("/checkout_roomreserved/{id}")
async def Checkout_RoomReserved(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                findres_details = db.query(models.Room_Details).filter(models.Room_Details.token==id,models.Room_Details.status==CommonWords.STATUS).first()
                if findres_details:
                    db.query(models.Room_Details).filter(models.Room_Details.token==id).update({'Departure_Date':CommonWords.CURRENTDATE,'Booking_Status':CommonWords.Departures})
                    db.commit()
                    
                    if findres_details.Arrival_Date <= datetime.today().date() <= findres_details.Departure_Date:
                        db.query(models.Room).filter(models.Room.id==findres_details.Available_rooms,models.Room.Room_Booking_status==CommonWords.Arrived).update({'Room_Booking_status':CommonWords.AVAILABLE})                    
                        db.commit()
            
                return "Success"
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#Check In Reservation (Group Reservation list, Reservation List)
@router.get("/checkinreservation/{id}")
async def Checkin_Reservation(request: Request,id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                findres_details = db.query(models.Room_Reservation).filter(models.Room_Reservation.token==id,models.Room_Reservation.status==CommonWords.STATUS).first()
                if findres_details:
                    roomdet = db.query(models.Room_Details).filter(models.Room_Details.Reservation_Id==findres_details.id,models.Room_Details.status==CommonWords.STATUS).all()
                    if roomdet:
                        for i in roomdet:
                            db.query(models.Room_Details).filter(models.Room_Details.id==i.id).update({'Booking_Status':CommonWords.Arrived})
                            db.commit()
                            if findres_details.Arrival_Date <= datetime.today().date() <= findres_details.Departure_Date:
                                db.query(models.Room).filter(models.Room.id==i.Available_rooms).update({'Room_Booking_status':CommonWords.Arrived})                    
                                db.commit()
                          
                    db.query(models.Room_Reservation).filter(models.Room_Reservation.id==findres_details.id).update({'Booking_Status':CommonWords.Arrived})
                    db.commit()
                   
                return "Success"
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/export_reservations/")
async def export_reservations(
    db: Session = Depends(get_db),
    format: str = Query("excel")  # Default to Excel
):
    # Fetch reservation data from the database
    reservations = db.query(models.Room_Reservation).filter(models.Room_Reservation.Reservation_Type =="Reservation").all()
    
    # Prepare data for export
    data = []
    for reservation in reservations:
        data.append({
            "Room_Reservation_ID": reservation.Room_Reservation_ID,
            "Salutation": reservation.Salutation,
            "First_Name": reservation.First_Name,
            "Last_Name": reservation.Last_Name,
            "Phone_Number": reservation.Phone_Number,
            "Email": reservation.Email,
            "Arrival_Date": reservation.Arrival_Date,
            "Departure_Date": reservation.Departure_Date,
            "No_of_nights": reservation.No_of_nights,
            "Room_Type": reservation.Room_Type,
            "Room_No": reservation.Room_No,
            "No_of_rooms": reservation.No_of_rooms,
            "No_Of_Adults": reservation.No_Of_Adults,
            "No_Of_Childs": reservation.No_Of_Childs,
            "Payment_mode": reservation.Payment_mode,
            "Total_Amount": reservation.Total_Amount,
            "Booking_Status": reservation.Booking_Status,
            "Confirmation_code": reservation.Confirmation_code,
           
        })

    # Convert data to DataFrame
    df = pd.DataFrame(data)
    if format == "excel":
        # Create a BytesIO buffer to hold the Excel file
        buffer = io.BytesIO()
        # Write the DataFrame to the buffer as an Excel file
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Reservations')
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename=Reservation.xlsx"})
    
    elif format == "json":
        # Convert DataFrame to JSON
        json_data = df.to_json(orient="records")
        return StreamingResponse(io.BytesIO(json_data.encode()), media_type="application/json",
                                 headers={"Content-Disposition": "attachment; filename=Reservation.json"})

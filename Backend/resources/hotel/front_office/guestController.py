from fastapi import APIRouter, Depends, HTTPException,status, Request, Form ,File,UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from configs import BaseConfig
from typing import Optional
from datetime import  datetime 
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from resources.utils import create_access_token
from starlette.middleware.sessions import SessionMiddleware
import bcrypt,uuid,shutil
from icecream import ic
from jose import jwt, JWTError

from configs.base_config import BaseConfig,CommonWords

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/guest")
async def hotel_crm_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse('../login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                customer_data = db.query(models.Customer_Data).filter(models.Customer_Data.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('front_office/HOTEL/customer_table.html', context={'request': request,'color_theme':color_theme,'customer_data':customer_data})
        except JWTError:
            return RedirectResponse('CommonWords.LOGINER_URL', status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse('CommonWords.LOGINER_URL/login',status_code=303)

@router.get("/add_guest")
async def customer_newly_add(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse('CommonWords.LOGINER_URL', status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                customer_data = db.query(models.Customer_Data).filter(models.Customer_Data.status==CommonWords.STATUS).all()
                customer_new_id = ''
                if len(customer_data):
                    customer_new_id = 'CUST_ID'+str(int(len(customer_data))+1)
                else:
                    customer_new_id = 'CUST_ID1'
                identity_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status==CommonWords.STATUS).all()
                
                return templates.TemplateResponse('front_office/HOTEL/customer_add.html', context={'request': request,'color_theme':color_theme,
                                                                                                   'customer_new_id':customer_new_id,'identity_data':identity_data})
        except JWTError:
            return RedirectResponse('CommonWords.LOGINER_URL', status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse('CommonWords.LOGINER_URL/login',status_code=303)

@router.get("/genertate_reservid")
async def customer_newly_add(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                customer_data = db.query(models.Customer_Data).filter(models.Customer_Data.status==CommonWords.STATUS).all()
                customer_new_id = ''
                if len(customer_data):
                    customer_new_id = 'RESRV_ID'+str(int(len(customer_data))+1)
                else:
                    customer_new_id = 'RESRV_ID1'
                return JSONResponse(content={'reserv_id':customer_new_id},status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/guest_profile_page/{customer_id}")
async def customer_newly_add(request: Request,customer_id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse('../login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                customer_data = db.query(models.Customer_Data).filter(models.Customer_Data.Customer_ID==customer_id).filter(models.Customer_Data.status==CommonWords.STATUS).first()
                return templates.TemplateResponse('front_office/HOTEL/customer_profile.html', context={'request': request,'color_theme':color_theme,
                                                                                                       'customer_data':customer_data})
        except JWTError:
            return RedirectResponse('../login', status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse('../login/login',status_code=303)

@router.post("/add_guest")
async def customer_newly_add(request: Request,db: Session = Depends(get_db),customer_id:str=Form(...),customer_image:UploadFile=File(...),id_proof:UploadFile=File(...),purpose_visit:Optional[str]=Form('No Data'),emy_name:str=Form(...),emy_phone:str=Form(...),emy_relate:str=Form(...),fir_name:str=Form(...),las_name:str=Form(...),mobe:str=Form(...),mail:str=Form(...),dob:str=Form(...),city:str=Form(...),state:str=Form(...),gender:str=Form(...),postal_cd:str=Form(...),coun:str=Form(...),marital:str=Form(...),vip:str=Form(...),id_type:str=Form(...),c_card:Optional[str]=Form('No Data'),d_card:Optional[str]=Form('No Data'),data_use:str=Form(...),policies:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                check_previous_data = db.query(models.Customer_Data).filter(models.Customer_Data.Mobile==mobe,models.Customer_Data.Email==mail).filter(models.Customer_Data.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    photo_type = customer_image.content_type
                    id_proof_type = id_proof.content_type
                    extension_1 = photo_type.split('/')[-1]
                    extension_2 = id_proof_type.split('/')[-1]
                    profile_pick = str(uuid.uuid4())+'.'+str(extension_1)
                    proof_file = str(uuid.uuid4())+'.'+str(extension_2)
                    
                    with open(f"./templates/static/upload_image/{profile_pick}", "wb+") as file_object_1:
                        shutil.copyfileobj(customer_image.file, file_object_1)

                    with open(f"./templates/static/upload_image/{proof_file}", "wb+") as file_object_2:
                        shutil.copyfileobj(id_proof.file, file_object_2)
                       
                    new_customer_data = models.Customer_Data(Customer_ID=customer_id,Gender=gender,Photo=profile_pick,First_Name=fir_name,Last_Name=las_name,Email=mail,Mobile=mobe,D_O_B=dob,Address=str(city+','+state+','+postal_cd+','+coun),City=city,State=state,Postal_code=postal_cd,Country=coun,Marital_status=marital,VIP_status=vip,Number_Of_Guests=0,Number_Of_Adults=0,Names_Of_Adults=0,Number_Of_Childs=0,Names_Of_Childs=0,Identification_Type_id=id_type,Identification_Proof=proof_file,Emergency_Name=emy_name,Emergency_Contact=emy_phone,Emergency_Relationship=emy_relate,Consent_for_Data_Use=data_use,Acknowledgment_of_Hotel_Policies=policies,Credit_card_Info=c_card,Debit_card_Info=d_card,Purpose_Of_Visit=purpose_visit,status=Commonwords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_customer_data)
                    db.commit()
                    db.refresh(new_customer_data)
                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_208_ALREADY_REPORTED)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
                    
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/room_booking_page")
async def customer_newly_add(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                room_type_data = db.query(models.Room_Type).filter(models.Room_Type.status==CommonWords.STATUS).all()
                guest_data = db.query(models.Customer_Data).filter(models.Customer_Data.status==CommonWords.STATUS).all()
                today_date = datetime.today().date()
                return templates.TemplateResponse('front_office/HOTEL/room_booking.html', context={'request': request,'color_theme':color_theme,
                                                                                                   'guest_data':guest_data,'today_date':today_date,'room_type_data':room_type_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/get_guest_data/{table_id}")
async def customer_newly_add(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                guest_data = db.query(models.Customer_Data).filter(models.Customer_Data.id==table_id).filter(models.Customer_Data.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(guest_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/get_room_types")
async def customer_newly_add(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                room_type_data = db.query(models.Room_Type).filter(models.Room_Type.status==CommonWords.STATUS).all()
                return JSONResponse(content=jsonable_encoder(room_type_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/get_filtered_rooms/{table_id}")
async def customer_newly_add(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                room_data = db.query(models.Room).filter(models.Room.Room_Type_ID==table_id,models.Room.Room_Booking_status==AVAILABLE).filter(models.Room.status==CommonWords.STATUS).all()
                return JSONResponse(content=jsonable_encoder(room_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/get_filtered_rooms_details/{table_id}")
async def customer_newly_add(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
            else:
                room_data = db.query(models.Room).filter(models.Room.id==table_id).filter(models.Room.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(room_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

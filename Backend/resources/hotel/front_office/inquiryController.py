from fastapi import APIRouter, Depends,UploadFile,status, Request, Form ,File 
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from configs import BaseConfig
from datetime import  timedelta 
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from resources.utils import create_access_token
from starlette.middleware.sessions import SessionMiddleware
import bcrypt,uuid,shutil,datetime
from icecream import ic
from jose import jwt, JWTError

from configs.base_config import BaseConfig,CommonWords
router = APIRouter()
templates = Jinja2Templates(directory="templates")

#=====================================>>> Inquriy Page
@router.get("/inquiry")
def Inquiry_Page(request: Request,db: Session = Depends(get_db)):   
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
                inquiry_data = db.query(models.Inquiry).filter(models.Inquiry.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('front_office/inquiry/inquiry.html', context={'request': request,'color_theme':color_theme,'inquiry_data':inquiry_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>>Add Inquriy
@router.post("/inquiry")
def Add_Inquiry(request: Request,db: Session = Depends(get_db),inquiry_mode:str=Form(...),guest_name:str=Form(None),response:Optional[str]=Form(None),followup:Optional[str]=Form(None),incidents:Optional[str]=Form(None),inquiry_status:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by:
                if  response:
                    response=response
                else:
                    response=""   
                if  followup:
                    followup=followup
                else:
                    followup=""  
                if  incidents:
                    incidents=incidents
                else:
                    incidents=""    
                new_room = models.Inquiry(inquiry_mode=inquiry_mode,guest_name=guest_name,response=response,followup=followup,incidents=incidents,inquiry_status=inquiry_status,status=CommonWords.STATUS,created_by=created_by,updated_by="",company_id=company_id)
            
                db.add(new_room)
                db.commit()
                db.refresh(new_room)

                return JSONResponse(content=jsonable_encoder('Sucessfully Inserted'),status_code=status.HTTP_200_OK)
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>>Inquiry Get Particular Data
@router.get("/get_inquiry/{id}")
def Get_Inquriy(request: Request,id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by:
                inquiry_data = db.query(models.Inquiry).filter(models.Inquiry.id==id).filter(models.Inquiry.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(inquiry_data),status_code=status.HTTP_200_OK)
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
          
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>>Update Enquiry
@router.post("/update_inquiry")
def Update_Inquiry(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_inquiry_mode:str=Form(...),edit_guest_name:str=Form(...),edit_response:Optional[str]=Form(None),edit_followup:Optional[str]=Form(None),edit_incidents:Optional[str]=Form(None),edit_inquiry_status:str=Form(None)):  
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by:
                if  edit_response:
                    edit_response=edit_response
                else:
                    edit_response=""   
                if  edit_followup:
                    edit_followup=edit_followup
                else:
                    edit_followup=""  
                if  edit_incidents:
                    edit_incidents=edit_incidents
                else:
                    edit_incidents="" 
                db.query(models.Inquiry).filter(models.Inquiry.id==edit_id).update({'inquiry_mode':edit_inquiry_mode,'guest_name':edit_guest_name,'response':edit_response,'followup':edit_followup,'incidents':edit_incidents,'inquiry_status':edit_inquiry_status,'updated_by':created_by})                    
                db.commit()
                return JSONResponse(content=jsonable_encoder('Sucessfully Updated'),status_code=status.HTTP_200_OK)
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
          
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>>Delete Inquriy
@router.delete("/delete_inquiry/{id}")
def Delete_Inquiry(request: Request,id:int,db: Session = Depends(get_db)):  
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            Loginer_Role: str= payload.get("user_role_id")
            
            if created_by:
                db.query(models.Inquiry).filter(models.Inquiry.id==id).update({'status':CommonWords.UNSTATUS})
                db.commit()
                return JSONResponse(content=jsonable_encoder('Sucessfully Updated'),status_code=status.HTTP_200_OK)
            else:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
       
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

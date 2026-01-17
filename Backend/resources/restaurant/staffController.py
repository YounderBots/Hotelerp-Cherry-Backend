from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from configs.base_config import BaseConfig, CommonWords
from models import get_db, models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/staff_master")
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
                return templates.TemplateResponse('restaurant/staff/staff_master.html', context={'request': request,'color_theme':color_theme,'inquiry_data':inquiry_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/shift_planning")
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
                return templates.TemplateResponse('restaurant/staff/shift_planning.html', context={'request': request,'color_theme':color_theme,'inquiry_data':inquiry_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)
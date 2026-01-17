from fastapi import APIRouter, Depends, HTTPException,status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from configs import BaseConfig
from datetime import  timedelta 
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from resources.utils import create_access_token
from starlette.middleware.sessions import SessionMiddleware
import bcrypt
from icecream import ic
from resources.utils import create_access_token

from configs.base_config import BaseConfig,CommonWords

router = APIRouter()
templates = Jinja2Templates(directory="templates")

        
@router.get("/login")
async def login_page(request: Request,db: Session = Depends(get_db)):
    color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
    return templates.TemplateResponse('login/login.html', context={'request': request,'color_theme':color_theme})

@router.post("/login")
async def check_loginer(request: Request,db: Session = Depends(get_db),loginer_mail:str=Form(...),loginer_password:str=Form(...),loginer_registerid:str=Form(...)):   
    check_employee_data = db.query(models.Employee_Data).filter(models.Employee_Data.Company_Email == loginer_mail ).filter(models.Employee_Data.status == CommonWords.STATUS ).first()
    if check_employee_data:
        if bcrypt.checkpw(loginer_password.encode('utf-8'), check_employee_data.Password.encode('utf-8')):
            access_token_expires = timedelta(minutes=BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"user_id": check_employee_data.id,"company_id": check_employee_data.company_id},expires_delta=access_token_expires)
            sessid = access_token
            request.session["sessid"] = sessid
            error = {"message": "Success","linkdetails": "/dashboard"}
            return JSONResponse(content=jsonable_encoder(error), status_code=status.HTTP_200_OK)
        else:
            error = {"message": "Passwor Wrong"}
            return JSONResponse(content=jsonable_encoder(error), status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        error = {"message": "Please Enter Correct Email"}
        return JSONResponse(content=jsonable_encoder(error), status_code=status.HTTP_403_FORBIDDEN)
    

@router.get('/logout')
def user_logout(request: Request, db: Session = Depends(get_db)):
    if "sessid" in request.session:
        del request.session["sessid"]
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
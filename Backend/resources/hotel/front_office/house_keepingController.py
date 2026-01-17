from fastapi import APIRouter, Depends,UploadFile,status, Request, Form ,File 
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional,Dict,List
from configs.base_config import BaseConfig,CommonWords

from datetime import  timedelta ,date
from datetime import datetime as dt
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from resources.utils import create_access_token
from starlette.middleware.sessions import SessionMiddleware
import bcrypt,uuid,shutil,datetime,json,random
from icecream import ic
from jose import jwt, JWTError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import os


from configs.base_config import BaseConfig,CommonWords

router = APIRouter()
templates = Jinja2Templates(directory="templates")


#----------------------------------- House Keeping - HSK Masters --------->


# Housekeeping/HSK_Masters Page
@router.get("/hsk_task")
async def Hsk_Task_Assign(request: Request, db: Session = Depends(get_db)):
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
                today_date = datetime.datetime.today().strftime('%Y-%m-%d')
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                emp_data = db.query(models.Employee_Data).filter(models.Employee_Data.Role_id != CommonWords.HouseKeeper_RoleID,models.Employee_Data.status == CommonWords.STATUS).all()
                housekeepingdata = db.query(models.Employee_Data).filter(models.Employee_Data.Role_id == CommonWords.HouseKeeper_RoleID,models.Employee_Data.status == CommonWords.STATUS).all()
               
                room_data = db.query(models.Room).filter(models.Room.status == CommonWords.STATUS).all()
                task_data = db.query(models.Task_Type).filter(models.Task_Type.status == CommonWords.STATUS).all()
                
                all_housekeeper_task = db.query(models.Housekeeper_Task).filter(models.Housekeeper_Task.status == CommonWords.STATUS).all()
                for i in all_housekeeper_task:
                    i.Sch_Date = i.Sch_Date.strftime('%d-%m-%Y')
                    i.Sch_Time = i.Sch_Time.strftime('%I:%M %p')
                    i.staff_data = db.query(models.Employee_Data).filter(models.Employee_Data.id == i.Assign_Staff,models.Employee_Data.status == CommonWords.STATUS).first()
                    i.room_data = db.query(models.Room).filter(models.Room.id == i.Room_No,models.Room.status == CommonWords.STATUS).first()
                    
                

                return templates.TemplateResponse('front_office/house_keeping/hsk_master.html', context={'request': request, 'color_theme': color_theme,'task_data':task_data,"emp_data": emp_data,"room_data": room_data,"all_housekeeper_task":all_housekeeper_task,'housekeepingdata':housekeepingdata,'today':CommonWords.CURRENTDATE,'todaytime':CommonWords.CURRENTTIME})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse('../login/login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/get-employee-details/{emp_id}")
async def get_employee_details(request:Request,emp_id: int,db: Session = Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                emp_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==emp_id).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(emp_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#--------Housekeeper Task Details -->

#Add Housekeeper_task
@router.post("/housekeeper_task")
async def add_housekeeper_task(request: Request,db: Session = Depends(get_db),lost_found:Optional[str]=Form(None),emps_id:str=Form(...),first_name:str=Form(...),last_name:str=Form(...),sch_date:str=Form(...),sch_time:str=Form(...),room_status:str=Form(...),room_number:int=Form(...),task_type:str=Form(...),assign_staff:str=Form(...),task_status:str=Form(...),notes:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                check_previous_data = db.query(models.Housekeeper_Task).filter(models.Housekeeper_Task.Employee_ID==emps_id,models.Housekeeper_Task.Sch_Date==sch_date,models.Housekeeper_Task.Sch_Time==sch_time,models.Housekeeper_Task.Room_No==room_number,models.Housekeeper_Task.Task_Type==task_type,models.Housekeeper_Task.status==CommonWords.STATUS).first()
                if check_previous_data:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)    
                else:
                    if lost_found is None:
                        lost_found = ""
                    else:
                        lost_found=lost_found
                    housekeeper = models.Housekeeper_Task(Employee_ID=emps_id,First_Name=first_name,Sur_Name=last_name,Sch_Date=sch_date,Sch_Time=sch_time,Room_No=room_number,Task_Type=task_type,Assign_Staff=assign_staff,Task_Status=task_status,Room_Status=room_status,Lost_Found=lost_found,Special_Instructions=notes,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(housekeeper)
                    db.commit()
                    db.refresh(housekeeper)
                    db.query(models.Room).filter(models.Room.id==room_number).update({'Room_Status':room_status,'Room_Booking_status':task_type})
                    db.commit() 
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)



@router.get("/housekeepertask_id/{housekeeper_id}")
async def housekeepertask_id_taking(request: Request,housekeeper_id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                housekeeper_task_data = db.query(models.Housekeeper_Task).filter(models.Housekeeper_Task.id==housekeeper_id).filter(models.Housekeeper_Task.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(housekeeper_task_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/update_housekeeper_task")
async def update_housekeeper_task(request: Request,db: Session = Depends(get_db),edit_lost_found:Optional[str] = Form(None),edit_id:int=Form(...),edit_emps_id:str=Form(...),edit_first_name:str=Form(...),edit_last_name:str=Form(...),edit_sch_date:str=Form(...),edit_sch_time:str=Form(...),edit_room_number:int=Form(...),edit_task_type:str=Form(...),edit_assign_staff:str=Form(...),edit_task_status:str=Form(...),edit_room_status:str=Form(...),edit_notes:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:

                check_previous_data = db.query(models.Housekeeper_Task).filter(models.Housekeeper_Task.id!=edit_id,models.Housekeeper_Task.Employee_ID==edit_emps_id,models.Housekeeper_Task.Sch_Date==edit_sch_date,models.Housekeeper_Task.Sch_Time==edit_sch_time,models.Housekeeper_Task.status==CommonWords.STATUS).first()
                if check_previous_data:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)    
                else:
                    if edit_lost_found is None:
                        edit_lost_found = ""
                    else:
                        edit_lost_found=edit_lost_found
                    db.query(models.Housekeeper_Task).filter(models.Housekeeper_Task.id==edit_id).update({'Employee_ID':edit_emps_id,'First_Name':edit_first_name,'Sur_Name':edit_last_name,'Sch_Date':edit_sch_date,'Sch_Time':edit_sch_time,'Room_No':edit_room_number,'Task_Type':edit_task_type,'Assign_Staff':edit_assign_staff,'Task_Status':edit_task_status,'Room_Status':edit_room_status,'Special_Instructions':edit_notes,'Lost_Found':edit_lost_found})
                    db.commit()
                    db.query(models.Room).filter(models.Room.id==edit_room_number).update({'Room_Status':edit_room_status,'Room_Booking_status':edit_task_type})
                    db.commit() 
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/delete_housekeeper_task/{emps_id}")
async def deleting_housekeeper_task_data(request: Request,emps_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                db.query(models.Housekeeper_Task).filter(models.Housekeeper_Task.id==emps_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#-------------- Room Incident -------

# Housekeeping/HSK_Masters Page
@router.get("/room_incidents")
async def Room_Incidents(request: Request, db: Session = Depends(get_db)):
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
                today_date = datetime.datetime.today().strftime('%Y-%m-%d')
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                emp_data = db.query(models.Employee_Data).filter(models.Employee_Data.Role_id != CommonWords.HouseKeeper_RoleID,models.Employee_Data.status == CommonWords.STATUS).all()
                housekeepingdata = db.query(models.Employee_Data).filter(models.Employee_Data.Role_id == CommonWords.HouseKeeper_RoleID,models.Employee_Data.status == CommonWords.STATUS).all()
               
                room_data = db.query(models.Room).filter(models.Room.status == CommonWords.STATUS).all()
                task_data = db.query(models.Task_Type).filter(models.Task_Type.status == CommonWords.STATUS).all()
                
                all_hskroom_incident = db.query(models.HSK_Room_Incident).filter(models.HSK_Room_Incident.status == CommonWords.STATUS).all()
                for i in all_hskroom_incident:
                #     i.Sch_Date = i.Sch_Date.strftime('%d-%m-%Y')
                #     i.Sch_Time = i.Sch_Time.strftime('%I:%M %p')
                #     i.staff_data = db.query(models.Employee_Data).filter(models.Employee_Data.id == i.Assign_Staff,models.Employee_Data.status == CommonWords.STATUS).first()
                    i.room_data = db.query(models.Room).filter(models.Room.id == i.Room_No,models.Room.status == CommonWords.STATUS).first()
                   

                return templates.TemplateResponse('front_office/house_keeping/room_incident.html', context={'request': request, 'color_theme': color_theme,'task_data':task_data,"emp_data": emp_data,"room_data": room_data,"all_hskroom_incident":all_hskroom_incident,'housekeepingdata':housekeepingdata,'today':CommonWords.CURRENTDATE,'todaytime':CommonWords.CURRENTTIME})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse('../login/login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/add_room_incident")
async def Add_Room_Incident(request: Request,db: Session = Depends(get_db),room_no:int=Form(...),date_of_incident:str=Form(...),time_of_incident:str=Form(...),incident_desc:str=Form(...),hsk_involved_staff:str=Form(...),severity:str=Form(...),witnesses:str=Form(...),actions_taken: str = Form(...),reported_by:str = Form(...),date_of_report:str = Form(...),upload_file:UploadFile = File(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                upload_file1 = upload_file.content_type
                extention = upload_file1.split('/')[-1]
                token_photo = str(uuid.uuid4())+'.'+str(extention)
                file_location = f"./templates/static/upload_image/{token_photo}"
                with open (file_location,'wb+') as file_object:
                    shutil.copyfileobj(upload_file.file,file_object)

                check_previous_data = db.query(models.HSK_Room_Incident).filter(models.HSK_Room_Incident.Room_No ==room_no,models.HSK_Room_Incident.Date_of_Incident ==date_of_incident,models.HSK_Room_Incident.Time_of_Incident ==time_of_incident).filter(models.HSK_Room_Incident.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    hsk_room_incident = models.HSK_Room_Incident(Room_No=room_no,Date_of_Incident=date_of_incident,Time_of_Incident=time_of_incident,Incident_Desc=incident_desc,HSK_Involved_Staff=hsk_involved_staff,Severity=severity,Witnesses=witnesses,Actions_Taken= actions_taken,Reported_By = reported_by,Date_of_Report = date_of_report,File=token_photo,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(hsk_room_incident)
                    db.commit()
                    db.refresh(hsk_room_incident)
                    return JSONResponse(content=jsonable_encoder('Successfully Inserted'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Already Added'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/HSK_Room_Incident_id/{housekeeper_id}")
async def hsk_room_incident_id_taking(request: Request,housekeeper_id:str,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                hsk_room_incident = db.query(models.HSK_Room_Incident).filter(models.HSK_Room_Incident.id==housekeeper_id).filter(models.HSK_Room_Incident.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(hsk_room_incident),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/edit_room_incident")
async def Edit_Room_Incident(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_room_no:int=Form(...),edit_incident_date:str=Form(...),edit_incident_time:str=Form(...),edit_incident_desc:str=Form(...),edit_staff_involved:str=Form(...),edit_incident_severity:str=Form(...),edit_witnesses:str=Form(...),edit_actions_taken: str = Form(...),edit_reported_by:str = Form(...),edit_report_date:str = Form(...),edit_file:Optional[UploadFile] = File(None)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:

                check_previous_data = db.query(models.HSK_Room_Incident).filter((models.HSK_Room_Incident.Room_No) ==edit_room_no,func.lower(models.HSK_Room_Incident.Date_of_Incident) ==edit_incident_date.lower(),func.lower(models.HSK_Room_Incident.Time_of_Incident) ==edit_incident_time.lower(),func.lower(models.HSK_Room_Incident.Incident_Desc) ==edit_incident_desc.lower(),func.lower(models.HSK_Room_Incident.HSK_Involved_Staff) ==edit_staff_involved.lower(),func.lower(models.HSK_Room_Incident.Severity) ==edit_severity.lower(),func.lower(models.HSK_Room_Incident.Witnesses) == edit_witnesses.lower(),func.lower(models.HSK_Room_Incident.Actions_Taken) == edit_actions_taken.lower(),func.lower(models.HSK_Room_Incident.Reported_By) == edit_reported_by.lower(),func.lower(models.HSK_Room_Incident.Date_of_Report) == edit_date_of_report.lower(),(models.HSK_Room_Incident.File) ==edit_file) .filter(models.HSK_Room_Incident.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    if edit_file is not None : 
                        upload_file1 = edit_file.content_type
                        extention = upload_file1.split('/')[-1]
                        token_photo = str(uuid.uuid4())+'.'+str(extention)
                        file_location = f"./templates/static/upload_image/{token_photo}"
                        with open (file_location,'wb+') as file_object:
                            shutil.copyfileobj(edit_file.file,file_object)
                        db.query(models.HSK_Room_Incident).filter(models.HSK_Room_Incident.id==edit_id).update({'File':token_photo})
                  
                        
                    db.query(models.HSK_Room_Incident).filter(models.HSK_Room_Incident.id==edit_id).update({'Room_No':edit_room_no,'Date_of_Incident':edit_date_of_incident,'Time_of_Incident':edit_time_of_incident,'Incident_Desc':edit_incident_desc,'HSK_Involved_Staff':edit_hsk_involved_staff,'Severity':edit_severity,'Witnesses':edit_witnesses,'Actions_Taken':edit_actions_taken,'Reported_By':edit_reported_by,'Date_of_Report':edit_date_of_report,'File':edit_file})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/delete_hsk_room_incident/{room_id}")
async def deleting_hsk_room_incident(request: Request,room_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                db.query(models.HSK_Room_Incident).filter(models.HSK_Room_Incident.id==room_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

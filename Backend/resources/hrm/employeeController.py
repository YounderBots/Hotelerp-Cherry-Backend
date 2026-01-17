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
from fpdf import FPDF
from io import StringIO

from configs.base_config import BaseConfig,CommonWords

router = APIRouter()
templates = Jinja2Templates(directory="templates")
  
#==============================================>>>. Employee Profiles     
@router.get("/employee")
async def employee_home_page(request: Request,db: Session = Depends(get_db)):   
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
                permision_control = db.query(models.Role_Permission.Modules_Data).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first()
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                employee_data = db.query(models.Employee_Data).filter(models.Employee_Data.status==CommonWords.STATUS).all()
                
                return templates.TemplateResponse('hr/employee_list.html', context={'request': request,'color_theme':color_theme,'employee_data':employee_data,'loginer_data':loginer_data,'permision_control':permision_control})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/employee_add")
async def employee_add_home_page(request: Request,db: Session = Depends(get_db)):   
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
                permision_control = db.query(models.Role_Permission.Modules_Data).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first()
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                role_data = db.query(models.Role).filter(models.Role.status==CommonWords.STATUS).all()
                def generate_employee_id():
                    all_customer_data = db.query(models.Employee_Data).filter(models.Employee_Data.status==CommonWords.STATUS).all()
                    if len(all_customer_data) > 0:
                        return 'EMP_'+str(len(all_customer_data)+1)
                    else:
                        return 'EMP_1'
                    
                return templates.TemplateResponse('hr/add_employee_page.html', context={'request': request,'color_theme':color_theme,'permision_control':permision_control,
                                                                                        'loginer_data':loginer_data,'generate_employee_id':generate_employee_id(),'role_data':role_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/employee_edit/{table_id}")
async def employee_edit_home_page(request: Request,table_id:str,db: Session = Depends(get_db)):   
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
                permision_control = db.query(models.Role_Permission.Modules_Data).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first()
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                role_data = db.query(models.Role).filter(models.Role.status==CommonWords.STATUS).all()
                emp_data = db.query(models.Employee_Data).filter(models.Employee_Data.Employee_ID==table_id).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                return templates.TemplateResponse('hr/edit_employee_page.html', context={'request': request,'color_theme':color_theme,'emp_data':emp_data,'permision_control':permision_control,
                                                                                         'loginer_data':loginer_data,'role_data':role_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/employee")
async def facilities_post(request: Request,db: Session = Depends(get_db),employee_image:UploadFile=File(...),notes:str=Form(...),emy_name:str=Form(...),emy_phone:str=Form(...),emy_relate:str=Form(...),employee_id:str=Form(...),fir_name:str=Form(...),las_name:str=Form(...),passkey:str=Form(...),mail:str=Form(...),mobe:str=Form(...),alter_mobe:str=Form(...),dob:str=Form(...),gender:str=Form(...),city:str=Form(...),state:str=Form(...),postal_cd:str=Form(...),coun:str=Form(...),role_id:str=Form(...),joining:str=Form(...),salary:str=Form(...),expericence:str=Form(...),marital:str=Form(...),policies:str=Form(...)):   
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
                check_previous_data = db.query(models.Employee_Data).filter(
                    (func.lower(models.Employee_Data.Personal_Email) == mail.lower()) | 
                    (func.lower(models.Employee_Data.Mobile) == mobe.lower())
                ).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                
                if check_previous_data:
                    return JSONResponse({
                        "status": "error",
                        "message": "Employee with this email or mobile already exists!"
                    }, status_code=status.HTTP_400_BAD_REQUEST)
                
                file_type = employee_image.content_type
                extention1 = file_type.split('/')[-1]
                image_file1 = str(uuid.uuid4())+ '.' + str(extention1)
                with open(f"./templates/static/upload_image/{image_file1}", "wb+") as file_object_1:
                    shutil.copyfileobj(employee_image.file, file_object_1)
                
                company_mail = str(mail.split('@')[0])+'@hotel.com'
                hash_password = bcrypt.hashpw(passkey.encode('utf-8'), bcrypt.gensalt(14))
                full_address = city+','+state+','+coun+','+postal_cd
                role_data = db.query(models.Role).filter(models.Role.id==int(role_id)).filter(models.Role.status==CommonWords.STATUS).first()

                new_employee = models.Employee_Data(Employee_ID=employee_id,Photo=image_file1,First_Name=fir_name,Last_Name=las_name,
                                                Personal_Email=mail,Company_Email=company_mail,Password=hash_password,Mobile=mobe,
                                                Alternative_Mobile=alter_mobe,D_O_B=dob,Gender=gender,Address=full_address,City=city,
                                                State=state,Postal_code=postal_cd,Country=coun,Role_id=role_id,Department_id=role_data.role_name,
                                                Date_Of_Joining=joining,Salary_details=salary,Experience=expericence,Register_Code=1,
                                                Notes=notes,Emergency_Name=emy_name,Emergency_Contact=emy_phone,Emergency_Relationship=emy_relate,
                                                Acknowledgment_of_Hotel_Policies=policies,Marital_Status=marital,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                db.add(new_employee)
                db.commit()
                db.refresh(new_employee)
                
                return JSONResponse({
                    "status": "success",
                    "message": "Employee added successfully!"
                })
                
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/employee_view_data/{employee_id}")
async def employee_view_data(
    request: Request,
    employee_id: str,
    db: Session = Depends(get_db)
):
    emp = db.query(models.Employee_Data)\
        .filter(models.Employee_Data.Employee_ID == employee_id)\
        .filter(models.Employee_Data.status == CommonWords.STATUS)\
        .first()

    return JSONResponse(content=jsonable_encoder(emp))

    
@router.post("/password_change")
async def changing_to_new_password(request: Request,db: Session = Depends(get_db),employee_id:str=Form(...),new_Passkey:str=Form(...)):   
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
                hash_password = bcrypt.hashpw(new_Passkey.encode('utf-8'), bcrypt.gensalt(14))
                
                db.query(models.Employee_Data).filter(models.Employee_Data.Employee_ID==employee_id).update({'Password':hash_password})  
                db.commit()
                         
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/get_roles_data/{table_id}")
async def employee_add_home_page(request: Request,table_id:str,db: Session = Depends(get_db)):   
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
                selective_employee_data = db.query(models.Employee_Data).filter(models.Employee_Data.Employee_ID==table_id).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                selective_role_data = db.query(models.Role).filter(models.Role.id==int(selective_employee_data.Role_id)).filter(models.Role.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(selective_role_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_employee")
async def updating_proffile_employee(request: Request,db: Session = Depends(get_db),edit_employee_image:Optional[UploadFile]=File(None),edit_notes:str=Form(...),edit_emy_name:str=Form(...),edit_emy_phone:str=Form(...),edit_emy_relate:str=Form(...),edit_employee_id:str=Form(...),edit_fir_name:str=Form(...),edit_las_name:str=Form(...),edit_mail:str=Form(...),edit_mobe:str=Form(...),edit_alter_mobe:str=Form(...),edit_dob:str=Form(...),edit_gender:str=Form(...),edit_city:str=Form(...),edit_state:str=Form(...),edit_postal_cd:str=Form(...),edit_coun:str=Form(...),edit_role_id:str=Form(...),edit_joining:str=Form(...),edit_salary:str=Form(...),edit_expericence:str=Form(...)):   
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
                # Check if email or mobile already exists for other employees
                check_previous_data = db.query(models.Employee_Data).filter(
                    models.Employee_Data.Employee_ID != edit_employee_id,
                    func.lower(models.Employee_Data.Personal_Email) == edit_mail.lower()
                ).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                
                if check_previous_data:
                    return JSONResponse({
                        "status": "error",
                        "message": "Email already exists for another employee!"
                    }, status_code=status.HTTP_400_BAD_REQUEST)
                
                check_mobile_data = db.query(models.Employee_Data).filter(
                    models.Employee_Data.Employee_ID != edit_employee_id,
                    func.lower(models.Employee_Data.Mobile) == edit_mobe.lower()
                ).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                
                if check_mobile_data:
                    return JSONResponse({
                        "status": "error",
                        "message": "Mobile number already exists for another employee!"
                    }, status_code=status.HTTP_400_BAD_REQUEST)
                
                # Handle image upload if provided
                if edit_employee_image:
                    previous_data = db.query(models.Employee_Data).filter(
                        models.Employee_Data.Employee_ID==edit_employee_id
                    ).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                    
                    if previous_data and previous_data.Photo:
                        # Delete old image if exists
                        import os
                        old_image_path = f"./templates/static/upload_image/{previous_data.Photo}"
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    file_type = edit_employee_image.content_type
                    extention1 = file_type.split('/')[-1]
                    image_file1 = str(uuid.uuid4())+ '.' + str(extention1)
                    
                    with open(f"./templates/static/upload_image/{image_file1}", "wb+") as file_object_1:
                        shutil.copyfileobj(edit_employee_image.file, file_object_1)
                    
                    # Update with new image filename
                    db.query(models.Employee_Data).filter(
                        models.Employee_Data.Employee_ID==edit_employee_id
                    ).update({'Photo': image_file1})
                    db.commit()
                
                # Update other employee details
                company_mail = str(edit_mail.split('@')[0])+'@hotel.com'
                full_address = f"{edit_city},{edit_state},{edit_coun},{edit_postal_cd}"
                role_data = db.query(models.Role).filter(
                    models.Role.id==int(edit_role_id)
                ).filter(models.Role.status==CommonWords.STATUS).first()
                
                update_data = {
                    'First_Name': edit_fir_name,
                    'Last_Name': edit_las_name,
                    'Personal_Email': edit_mail,
                    'Company_Email': company_mail,
                    'Mobile': edit_mobe,
                    'Alternative_Mobile': edit_alter_mobe,
                    'D_O_B': edit_dob,
                    'Gender': edit_gender,
                    'Address': full_address,
                    'City': edit_city,
                    'State': edit_state,
                    'Postal_code': edit_postal_cd,
                    'Country': edit_coun,
                    'Role_id': edit_role_id,
                    'Department_id': role_data.role_name if role_data else '',
                    'Date_Of_Joining': edit_joining,
                    'Salary_details': edit_salary,
                    'Experience': edit_expericence,
                    'Notes': edit_notes,
                    'Emergency_Name': edit_emy_name,
                    'Emergency_Contact': edit_emy_phone,
                    'Emergency_Relationship': edit_emy_relate
                }
                
                db.query(models.Employee_Data).filter(
                    models.Employee_Data.Employee_ID==edit_employee_id
                ).update(update_data)
                db.commit()
                
                return JSONResponse({
                    "status": "success",
                    "message": "Employee Updated Successfully!"
                }, status_code=status.HTTP_200_OK)
                
        except Exception as e:
            return JSONResponse({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/delete_employee_data/{table_id}")
async def deleting_employee_profile(request: Request,table_id:str,db: Session = Depends(get_db)):   
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
                db.query(models.Employee_Data).filter(models.Employee_Data.Employee_ID==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=======================>>> Employee Attendance
@router.get("/employee_attendance")
async def employee_home_page(request: Request,db: Session = Depends(get_db)):   
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
                permision_control = db.query(models.Role_Permission.Modules_Data).filter(models.Role_Permission.Role_ID==Loginer_Role).filter(models.Role_Permission.status==CommonWords.STATUS).first()
                loginer_data = db.query(models.Employee_Data).filter(models.Employee_Data.id==created_by).filter(models.Employee_Data.status==CommonWords.STATUS).first()
                employee_data = db.query(models.Employee_Data).filter(models.Employee_Data.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('hr/employee_attendance.html', context={'request': request,'color_theme':color_theme,'employee_data':employee_data,'loginer_data':loginer_data,'permision_control':permision_control})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

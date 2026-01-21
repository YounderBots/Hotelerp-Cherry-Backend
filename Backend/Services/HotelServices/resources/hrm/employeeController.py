from fastapi import APIRouter, Depends, Request, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import uuid, shutil
import bcrypt

from models import models
from models import get_db
from configs.base_config import CommonWords

#==============================================>>> Employee Profiles

router = APIRouter()

@router.get("/employee", status_code=status.HTTP_200_OK)
def get_employee_list(
    company_id: str,
    db: Session = Depends(get_db)
):
    employee_data = db.query(models.Employee_Data).filter(
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).order_by(models.Employee_Data.id.desc()).all()

    return {
        "status": "success",
        "data": employee_data
    }

#==============================================>>> Employee Add 

@router.get("/employee_add", status_code=status.HTTP_200_OK)
def employee_add_data(
    company_id: str,
    db: Session = Depends(get_db)
):
    # Generate Employee ID
    employee_count = db.query(models.Employee_Data).filter(
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).count()

    employee_code = f"EMP_{employee_count + 1}" if employee_count > 0 else "EMP_1"

    # Role list
    role_data = db.query(models.Role).filter(
        models.Role.status == CommonWords.STATUS
    ).all()

    return {
        "status": "success",
        "data": {
            "employee_code": employee_code,
            "roles": role_data
        }
    }

#==============================================>>> Employee Edit  

@router.get("/employee_edit/{employee_id}", status_code=status.HTTP_200_OK)
def employee_edit_data(
    employee_id: str,
    company_id: str,
    db: Session = Depends(get_db)
):
    # Employee data
    emp_data = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == employee_id,
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not emp_data:
        return JSONResponse(content="Employee not found", status_code=404)

    # Role list
    role_data = db.query(models.Role).filter(
        models.Role.status == CommonWords.STATUS
    ).all()

    return {
        "status": "success",
        "data": {
            "employee": emp_data,
            "roles": role_data
        }
    }

#==============================================>>> Employee Create  

@router.post("/employee", status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_image: UploadFile = File(...),
    notes: str = Form(...),
    emy_name: str = Form(...),
    emy_phone: str = Form(...),
    emy_relate: str = Form(...),
    employee_id: str = Form(...),
    fir_name: str = Form(...),
    las_name: str = Form(...),
    passkey: str = Form(...),
    mail: str = Form(...),
    mobe: str = Form(...),
    alter_mobe: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    postal_cd: str = Form(...),
    coun: str = Form(...),
    role_id: str = Form(...),
    joining: str = Form(...),
    salary: str = Form(...),
    expericence: str = Form(...),
    marital: str = Form(...),
    policies: str = Form(...),

    company_id: str = Form(...),
    created_by: str = Form(...),

    db: Session = Depends(get_db)
):
    # Duplicate check (email or mobile)
    existing_employee = db.query(models.Employee_Data).filter(
        (
            func.lower(models.Employee_Data.Personal_Email) == mail.lower()
        ) | (
            func.lower(models.Employee_Data.Mobile) == mobe.lower()
        ),
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if existing_employee:
        return JSONResponse(
            {
                "status": "error",
                "message": "Employee with this email or mobile already exists!"
            },
            status_code=400
        )

    # Save image
    file_type = employee_image.content_type
    extension = file_type.split("/")[-1]
    image_name = f"{uuid.uuid4()}.{extension}"

    with open(f"./templates/static/upload_image/{image_name}", "wb+") as file_object:
        shutil.copyfileobj(employee_image.file, file_object)

    # Prepare data
    company_mail = f"{mail.split('@')[0]}@hotel.com"
    hashed_password = bcrypt.hashpw(passkey.encode("utf-8"), bcrypt.gensalt(14))
    full_address = f"{city},{state},{coun},{postal_cd}"

    role_data = db.query(models.Role).filter(
        models.Role.id == int(role_id),
        models.Role.status == CommonWords.STATUS
    ).first()

    # Create employee
    new_employee = models.Employee_Data(
        Employee_ID=employee_id,
        Photo=image_name,
        First_Name=fir_name,
        Last_Name=las_name,
        Personal_Email=mail,
        Company_Email=company_mail,
        Password=hashed_password,
        Mobile=mobe,
        Alternative_Mobile=alter_mobe,
        D_O_B=dob,
        Gender=gender,
        Address=full_address,
        City=city,
        State=state,
        Postal_code=postal_cd,
        Country=coun,
        Role_id=role_id,
        Department_id=role_data.role_name if role_data else None,
        Date_Of_Joining=joining,
        Salary_details=salary,
        Experience=expericence,
        Register_Code=1,
        Notes=notes,
        Emergency_Name=emy_name,
        Emergency_Contact=emy_phone,
        Emergency_Relationship=emy_relate,
        Acknowledgment_of_Hotel_Policies=policies,
        Marital_Status=marital,
        status=CommonWords.STATUS,
        created_by=created_by,
        company_id=company_id
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
        "status": "success",
        "message": "Employee added successfully!"
    }

#==============================================>>> Employee View  

@router.get("/employee/{employee_id}", status_code=status.HTTP_200_OK)
def employee_view_data(
    employee_id: str,
    company_id: str,
    db: Session = Depends(get_db)
):
    emp = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == employee_id,
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not emp:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Employee not found"
            },
            status_code=404
        )

    return {
        "status": "success",
        "data": emp
    }

#==============================================>>> Employee Password Change  

@router.post("/employee/password_change", status_code=status.HTTP_200_OK)
async def change_employee_password(
    employee_id: str = Form(...),
    new_passkey: str = Form(...),
    company_id: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check employee exists
    employee = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == employee_id,
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not employee:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Employee not found"
            },
            status_code=404
        )

    # Hash new password
    hashed_password = bcrypt.hashpw(
        new_passkey.encode("utf-8"),
        bcrypt.gensalt(14)
    )

    # Update password
    db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == employee_id,
        models.Employee_Data.company_id == company_id
    ).update({
        "Password": hashed_password
    })

    db.commit()

    return {
        "status": "success",
        "message": "Password updated successfully"
    }

#==============================================>>> Get Employee Role  

@router.get("/employee/{employee_id}/role", status_code=status.HTTP_200_OK)
def get_employee_role_data(
    employee_id: str,
    company_id: str,
    db: Session = Depends(get_db)
):
    # Get employee
    employee = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == employee_id,
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not employee:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Employee not found"
            },
            status_code=404
        )

    # Get role
    role = db.query(models.Role).filter(
        models.Role.id == int(employee.Role_id),
        models.Role.status == CommonWords.STATUS
    ).first()

    if not role:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Role not found"
            },
            status_code=404
        )

    return {
        "status": "success",
        "data": role
    }

#==============================================>>> Employee Update  

@router.put("/employee", status_code=status.HTTP_200_OK)
async def update_employee(
    edit_employee_id: str = Form(...),

    edit_fir_name: str = Form(...),
    edit_las_name: str = Form(...),
    edit_mail: str = Form(...),
    edit_mobe: str = Form(...),
    edit_alter_mobe: str = Form(...),
    edit_dob: str = Form(...),
    edit_gender: str = Form(...),

    edit_city: str = Form(...),
    edit_state: str = Form(...),
    edit_postal_cd: str = Form(...),
    edit_coun: str = Form(...),

    edit_role_id: str = Form(...),
    edit_joining: str = Form(...),
    edit_salary: str = Form(...),
    edit_expericence: str = Form(...),

    edit_notes: str = Form(...),
    edit_emy_name: str = Form(...),
    edit_emy_phone: str = Form(...),
    edit_emy_relate: str = Form(...),

    company_id: str = Form(...),

    edit_employee_image: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db)
):
    # Check employee exists
    employee = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == edit_employee_id,
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not employee:
        return JSONResponse(
            content={"status": "error", "message": "Employee not found"},
            status_code=404
        )

    # Duplicate email check
    email_exists = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID != edit_employee_id,
        func.lower(models.Employee_Data.Personal_Email) == edit_mail.lower(),
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if email_exists:
        return JSONResponse(
            content={"status": "error", "message": "Email already exists"},
            status_code=400
        )

    # Duplicate mobile check
    mobile_exists = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID != edit_employee_id,
        func.lower(models.Employee_Data.Mobile) == edit_mobe.lower(),
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if mobile_exists:
        return JSONResponse(
            content={"status": "error", "message": "Mobile already exists"},
            status_code=400
        )

    # Handle image update
    if edit_employee_image:
        import os

        if employee.Photo:
            old_path = f"./templates/static/upload_image/{employee.Photo}"
            if os.path.exists(old_path):
                os.remove(old_path)

        ext = edit_employee_image.content_type.split("/")[-1]
        image_name = f"{uuid.uuid4()}.{ext}"

        with open(f"./templates/static/upload_image/{image_name}", "wb+") as f:
            shutil.copyfileobj(edit_employee_image.file, f)

        employee.Photo = image_name

    # Role → Department
    role = db.query(models.Role).filter(
        models.Role.id == int(edit_role_id),
        models.Role.status == CommonWords.STATUS
    ).first()

    company_mail = f"{edit_mail.split('@')[0]}@hotel.com"
    full_address = f"{edit_city},{edit_state},{edit_coun},{edit_postal_cd}"

    # Update fields
    employee.First_Name = edit_fir_name
    employee.Last_Name = edit_las_name
    employee.Personal_Email = edit_mail
    employee.Company_Email = company_mail
    employee.Mobile = edit_mobe
    employee.Alternative_Mobile = edit_alter_mobe
    employee.D_O_B = edit_dob
    employee.Gender = edit_gender
    employee.Address = full_address
    employee.City = edit_city
    employee.State = edit_state
    employee.Postal_code = edit_postal_cd
    employee.Country = edit_coun
    employee.Role_id = edit_role_id
    employee.Department_id = role.role_name if role else None
    employee.Date_Of_Joining = edit_joining
    employee.Salary_details = edit_salary
    employee.Experience = edit_expericence
    employee.Notes = edit_notes
    employee.Emergency_Name = edit_emy_name
    employee.Emergency_Contact = edit_emy_phone
    employee.Emergency_Relationship = edit_emy_relate

    db.commit()

    return {
        "status": "success",
        "message": "Employee updated successfully"
    }

#==============================================>>> Employee Delete  
@router.delete("/employee/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee(
    employee_id: str,
    company_id: str,
    db: Session = Depends(get_db)
):
    # Check employee exists
    employee = db.query(models.Employee_Data).filter(
        models.Employee_Data.Employee_ID == employee_id,
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not employee:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Employee not found"
            },
            status_code=404
        )

    # Soft delete
    employee.status = CommonWords.UNSTATUS
    db.commit()

    return {
        "status": "success",
        "message": "Employee deleted successfully"
    }

#=======================>>> Employee Attendance  
@router.get("/employee_attendance", status_code=status.HTTP_200_OK)
def get_employee_attendance_data(
    company_id: str,
    db: Session = Depends(get_db)
):
    employees = db.query(models.Employee_Data).filter(
        models.Employee_Data.company_id == company_id,
        models.Employee_Data.status == CommonWords.STATUS
    ).order_by(models.Employee_Data.id.desc()).all()

    return {
        "status": "success",
        "data": employees
    }

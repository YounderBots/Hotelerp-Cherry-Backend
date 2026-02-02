from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt
import uuid
import os
import uuid
import bcrypt
from fastapi import Form, UploadFile, File
from resources.utils import verify_authentication
from models import models
from models import get_db
from configs.base_config import CommonWords

router = APIRouter()

# =====================================================
# HELPER FUNCTION: GENERATE USER CODE
# =====================================================
def generate_user_code(db: Session, company_id: str) -> str:
    """
    Generate a unique user code for a company.
    Format: EMP_YYYY_0001, EMP_YYYY_0002, etc.
    """
    from datetime import datetime
    
    year = datetime.now().year
    prefix = f"EMP_{year}"
    
    # Get the last user code for this company and year
    last_user = (
        db.query(models.Users)
        .filter(
            models.Users.company_id == company_id,
            models.Users.User_Code.like(f"{prefix}%")
        )
        .order_by(models.Users.User_Code.desc())
        .first()
    )
    
    if last_user and last_user.User_Code:
        # Extract the number from the last code
        try:
            last_number = int(last_user.User_Code.split("_")[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1
    
    # Format with leading zeros (4 digits)
    user_code = f"{prefix}_{next_number:04d}"
    
    return user_code

UPLOAD_DIR = "templates/static/users"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =====================================================
# CREATE USER / EMPLOYEE (WITH PHOTO)
# =====================================================
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,

    # ---------------- BASIC ----------------
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),

    # ---------------- CONTACT ----------------
    personal_email: str = Form(...),
    company_email: str = Form(...),
    password: str = Form(...),
    mobile: str = Form(...),
    alternative_mobile: str = Form(None),

    # ---------------- PERSONAL ----------------
    dob: str = Form(...),
    gender: str = Form(...),
    marital_status: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    postal_code: str = Form(...),
    country: str = Form(...),

    # ---------------- ORGANIZATION ----------------
    department_id: str = Form(...),
    designation_id: str = Form(...),
    role_id: str = Form(...),
    shift_id: str = Form(...),
    date_of_joining: str = Form(...),
    experience: str = Form(...),
    salary_details: str = Form(...),
    register_code: str = Form(...),

    # ---------------- EMERGENCY ----------------
    emergency_name: str = Form(...),
    emergency_contact: str = Form(...),
    emergency_relationship: str = Form(...),

    # ---------------- POLICY ----------------
    acknowledgment_of_hotel_policies: bool = Form(False),

    # ---------------- PHOTO ----------------
    photo: UploadFile = File(None),

    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        auth_user_id, auth_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # NORMALIZATION
        # -------------------------------------------------
        username = username.strip()
        company_email = company_email.strip().lower()
        personal_email = personal_email.strip().lower()

        # -------------------------------------------------
        # EMAIL VALIDATION
        # -------------------------------------------------
        if "@" not in company_email or "." not in company_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid company_email format"
            )

        if "@" not in personal_email or "." not in personal_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid personal_email format"
            )

        # -------------------------------------------------
        # DUPLICATE CHECKS
        # -------------------------------------------------
        if db.query(models.Users).filter(
            func.lower(models.Users.username) == username.lower(),
            models.Users.company_id == company_id,
            models.Users.status == CommonWords.STATUS
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        if db.query(models.Users).filter(
            func.lower(models.Users.Company_Email) == company_email,
            models.Users.company_id == company_id,
            models.Users.status == CommonWords.STATUS
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company email already exists"
            )

        # -------------------------------------------------
        # PASSWORD HASH
        # -------------------------------------------------
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # -------------------------------------------------
        # PHOTO UPLOAD
        # -------------------------------------------------
        photo_path = None
        if photo:
            if photo.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only JPG and PNG images are allowed"
                )

            ext = photo.filename.split(".")[-1]
            filename = f"user_{uuid.uuid4().hex}.{ext}"
            photo_path = os.path.join(UPLOAD_DIR, filename)

            with open(photo_path, "wb") as buffer:
                buffer.write(await photo.read())

        # -------------------------------------------------
        # USER CODE
        # -------------------------------------------------
        user_code = generate_user_code(db, company_id)

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------
        user = models.Users(
            User_Code=user_code,
            Photo=photo_path,
            username=username,
            First_Name=first_name,
            Last_Name=last_name,
            Personal_Email=personal_email,
            Company_Email=company_email,
            Password=hashed_password,
            Mobile=mobile,
            Alternative_Mobile=alternative_mobile,
            D_O_B=dob,
            Gender=gender,
            Marital_Status=marital_status,
            Address=address,
            City=city,
            State=state,
            Postal_Code=postal_code,
            Country=country,
            Department_ID=department_id,
            Designation_ID=designation_id,
            Role_ID=role_id,
            Shift_ID=shift_id,
            Date_Of_Joining=date_of_joining,
            Experience=experience,
            Salary_Details=salary_details,
            Register_Code=register_code,
            Emergency_Name=emergency_name,
            Emergency_Contact=emergency_contact,
            Emergency_Relationship=emergency_relationship,
            Acknowledgment_of_Hotel_Policies=acknowledgment_of_hotel_policies,
            status=CommonWords.STATUS,
            created_by=auth_user_id,
            company_id=company_id
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "User created successfully",
            "data": {
                "id": user.id,
                "user_code": user.User_Code,
                "username": user.username,
                "company_email": user.Company_Email,
                "photo": user.Photo,
                "created_at": user.created_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL USERS
# =====================================================
@router.get("/users", status_code=status.HTTP_200_OK)
def get_all_users(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        auth_user_id, auth_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH USERS
        # -------------------------------------------------
        users = (
            db.query(models.Users)
            .filter(
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS
            )
            .order_by(models.Users.id.desc())
            .all()
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(users),
            "data": [
                {
                    "id": user.id,
                    "user_code": user.User_Code,
                    "photo": user.Photo,
                    "username": user.username,

                    "first_name": user.First_Name,
                    "last_name": user.Last_Name,

                    "personal_email": user.Personal_Email,
                    "company_email": user.Company_Email,
                    "password": user.Password,
                    "mobile": user.Mobile,
                    "alternative_mobile": user.Alternative_Mobile,
                    "dob": user.D_O_B,
                    "gender": user.Gender,
                    "marital_status": user.Marital_Status,
                    "address": user.Address,
                    "city": user.City,
                    "state": user.State,
                    "postal_code": user.Postal_Code,
                    "country": user.Country,
                    "department_id": user.Department_ID,
                    "designation_id": user.Designation_ID,
                    "role_id": user.Role_ID,
                    "shift_id": user.Shift_ID,

                    "date_of_joining": user.Date_Of_Joining,
                    "experience": user.Experience,
                    "salary_details": user.Salary_Details,
                    "register_code": user.Register_Code,
                    "emergency_name": user.Emergency_Name,
                    "emergency_contact": user.Emergency_Contact,
                    "emergency_relationship": user.Emergency_Relationship,
                    "acknowledgment_of_hotel_policies": user.Acknowledgment_of_Hotel_Policies,

                    "status": user.status,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                for user in users
            ]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET USER BY ID
# =====================================================
@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        auth_user_id, auth_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id"
            )

        # -------------------------------------------------
        # FETCH USER
        # -------------------------------------------------
        user = (
            db.query(models.Users)
            .filter(
                models.Users.id == user_id,
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": user.id,
                "user_code": user.User_Code,
                "photo": user.Photo,
                "username": user.username,

                "first_name": user.First_Name,
                "last_name": user.Last_Name,

                "personal_email": user.Personal_Email,
                "company_email": user.Company_Email,
                "mobile": user.Mobile,
                "alternative_mobile": user.Alternative_Mobile,

                "dob": user.D_O_B,
                "gender": user.Gender,
                "marital_status": user.Marital_Status,

                "address": user.Address,
                "city": user.City,
                "state": user.State,
                "postal_code": user.Postal_Code,
                "country": user.Country,

                "department_id": user.Department_ID,
                "designation_id": user.Designation_ID,
                "role_id": user.Role_ID,
                "shift_id": user.Shift_ID,

                "date_of_joining": user.Date_Of_Joining,
                "experience": user.Experience,
                "salary_details": user.Salary_Details,
                "register_code": user.Register_Code,

                "emergency_name": user.Emergency_Name,
                "emergency_contact": user.Emergency_Contact,
                "emergency_relationship": user.Emergency_Relationship,

                "acknowledgment_of_hotel_policies": user.Acknowledgment_of_Hotel_Policies,

                "status": user.status,
                "company_id": user.company_id,
                "created_by": user.created_by,
                "created_at": user.created_at,
                "updated_by": user.updated_by,
                "updated_at": user.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET USER BY EMAIL (LOGIN USER)
# =====================================================
@router.get("/login_user/{usermail}", status_code=status.HTTP_200_OK)
def get_user_by_mail(
    usermail: str,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not usermail or "@" not in usermail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid email is required"
            )

        # -------------------------------------------------
        # FETCH USER (CASE INSENSITIVE)
        # -------------------------------------------------
        user = (
            db.query(models.Users)
            .filter(
                func.lower(models.Users.Company_Email) == usermail.lower(),
                models.Users.status == CommonWords.STATUS
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # -------------------------------------------------
        # RESPONSE (FOR AUTH SERVICE)
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": user.id,
                "user_code": user.User_Code,
                "username": user.username,

                "first_name": user.First_Name,
                "last_name": user.Last_Name,

                "personal_email": user.Personal_Email,
                "company_email": user.Company_Email,

                # ⚠️ REQUIRED FOR LOGIN PASSWORD VERIFICATION
                "password": user.Password,

                "mobile": user.Mobile,
                "alternative_mobile": user.Alternative_Mobile,

                "dob": user.D_O_B,
                "gender": user.Gender,
                "marital_status": user.Marital_Status,

                "address": user.Address,
                "city": user.City,
                "state": user.State,
                "postal_code": user.Postal_Code,
                "country": user.Country,

                "department_id": user.Department_ID,
                "designation_id": user.Designation_ID,
                "role_id": user.Role_ID,
                "shift_id": user.Shift_ID,

                "date_of_joining": user.Date_Of_Joining,
                "experience": user.Experience,
                "salary_details": user.Salary_Details,
                "register_code": user.Register_Code,

                "emergency_name": user.Emergency_Name,
                "emergency_contact": user.Emergency_Contact,
                "emergency_relationship": user.Emergency_Relationship,

                "acknowledgment_of_hotel_policies": user.Acknowledgment_of_Hotel_Policies,

                "status": user.status,
                "company_id": user.company_id,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE USER
# =====================================================
@router.put("/users", status_code=status.HTTP_200_OK)
async def update_user(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        auth_user_id, auth_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        user_id = payload.get("id")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(user_id, int) or user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid id is required"
            )

        # -------------------------------------------------
        # FETCH USER
        # -------------------------------------------------
        user = (
            db.query(models.Users)
            .filter(
                models.Users.id == user_id,
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # -------------------------------------------------
        # DUPLICATE CHECKS
        # -------------------------------------------------
        if payload.get("company_email"):
            duplicate_email = (
                db.query(models.Users)
                .filter(
                    models.Users.id != user_id,
                    func.lower(models.Users.Company_Email)
                    == payload["company_email"].lower(),
                    models.Users.company_id == company_id,
                    models.Users.status == CommonWords.STATUS
                )
                .first()
            )

            if duplicate_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Company email already exists"
                )

        if payload.get("username"):
            duplicate_username = (
                db.query(models.Users)
                .filter(
                    models.Users.id != user_id,
                    func.lower(models.Users.username)
                    == payload["username"].lower(),
                    models.Users.company_id == company_id,
                    models.Users.status == CommonWords.STATUS
                )
                .first()
            )

            if duplicate_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists"
                )

        # -------------------------------------------------
        # UPDATE FIELDS (SAFE)
        # -------------------------------------------------
        user.username = payload.get("username", user.username)
        user.First_Name = payload.get("first_name", user.First_Name)
        user.Last_Name = payload.get("last_name", user.Last_Name)
        user.Personal_Email = payload.get("personal_email", user.Personal_Email)
        user.Company_Email = payload.get("company_email", user.Company_Email)
        user.Mobile = payload.get("mobile", user.Mobile)
        user.Alternative_Mobile = payload.get(
            "alternative_mobile", user.Alternative_Mobile
        )

        user.D_O_B = payload.get("dob", user.D_O_B)
        user.Gender = payload.get("gender", user.Gender)
        user.Marital_Status = payload.get("marital_status", user.Marital_Status)

        user.Address = payload.get("address", user.Address)
        user.City = payload.get("city", user.City)
        user.State = payload.get("state", user.State)
        user.Postal_Code = payload.get("postal_code", user.Postal_Code)
        user.Country = payload.get("country", user.Country)

        user.Department_ID = payload.get("department_id", user.Department_ID)
        user.Designation_ID = payload.get("designation_id", user.Designation_ID)
        user.Role_ID = payload.get("role_id", user.Role_ID)
        user.Shift_ID = payload.get("shift_id", user.Shift_ID)

        user.Date_Of_Joining = payload.get(
            "date_of_joining", user.Date_Of_Joining
        )
        user.Experience = payload.get("experience", user.Experience)
        user.Salary_Details = payload.get(
            "salary_details", user.Salary_Details
        )
        user.Register_Code = payload.get("register_code", user.Register_Code)

        user.Emergency_Name = payload.get(
            "emergency_name", user.Emergency_Name
        )
        user.Emergency_Contact = payload.get(
            "emergency_contact", user.Emergency_Contact
        )
        user.Emergency_Relationship = payload.get(
            "emergency_relationship", user.Emergency_Relationship
        )

        user.Acknowledgment_of_Hotel_Policies = payload.get(
            "acknowledgment_of_hotel_policies",
            user.Acknowledgment_of_Hotel_Policies
        )

        user.updated_by = auth_user_id

        db.commit()
        db.refresh(user)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "User updated successfully",
            "data": {
                "id": user.id,
                "username": user.username,
                "company_email": user.Company_Email,
                "company_id": user.company_id,
                "updated_at": user.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE USER (SOFT DELETE)
# =====================================================
@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        auth_user_id, auth_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id"
            )

        # -------------------------------------------------
        # FETCH USER
        # -------------------------------------------------
        user = (
            db.query(models.Users)
            .filter(
                models.Users.id == user_id,
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        user.status = CommonWords.UNSTATUS
        user.updated_by = auth_user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "User deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE ROLE
# =====================================================
@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        role_name = payload.get("role_name", "").strip()
        description = payload.get("description", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not role_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="role_name is required"
            )

        if not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description is required"
            )

        if len(role_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="role_name must not exceed 100 characters"
            )

        if len(description) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description must not exceed 255 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Roles)
            .filter(
                func.lower(models.Roles.role_name) == role_name.lower(),
                models.Roles.company_id == company_id,
                models.Roles.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists"
            )

        # -------------------------------------------------
        # CREATE ROLE
        # -------------------------------------------------
        role = models.Roles(
            role_name=role_name,
            description=description,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(role)
        db.commit()
        db.refresh(role)

        # -------------------------------------------------
        # RESPONSE (UI FRIENDLY)
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Role created successfully",
            "data": {
                "id": role.id,
                "role_name": role.role_name,
                "description": role.description,
                "company_id": role.company_id,
                "created_by": role.created_by,
                "created_at": role.created_at
            }
        }

    except HTTPException:
        # ✅ Preserve proper HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL ROLES
# =====================================================
@router.get("/roles", status_code=status.HTTP_200_OK)
def get_all_roles(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH ROLES
        # -------------------------------------------------
        roles = (
            db.query(models.Roles)
            .filter(
                models.Roles.company_id == company_id,
                models.Roles.status == CommonWords.STATUS
            )
            .order_by(models.Roles.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE (NO ORM OBJECTS)
        # -------------------------------------------------
        data = [
            {
                "id": role.id,
                "role_name": role.role_name,
                "description": role.description,
                "company_id": role.company_id,
                "created_by": role.created_by,
                "created_at": role.created_at,
                "updated_at": role.updated_at
            }
            for role in roles
        ]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }

    except HTTPException:
        # ✅ Preserve proper HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ROLE BY ID
# =====================================================
@router.get("/roles/{role_id}", status_code=status.HTTP_200_OK)
def get_role_by_id(
    request: Request,
    role_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if role_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )

        # -------------------------------------------------
        # FETCH ROLE
        # -------------------------------------------------
        role_data = (
            db.query(models.Roles)
            .filter(
                models.Roles.id == role_id,
                models.Roles.company_id == company_id,
                models.Roles.status == CommonWords.STATUS
            )
            .first()
        )

        if not role_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # -------------------------------------------------
        # RESPONSE (NO ORM OBJECT)
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": role_data.id,
                "role_name": role_data.role_name,
                "description": role_data.description,
                "company_id": role_data.company_id,
                "created_by": role_data.created_by,
                "created_at": role_data.created_at,
                "updated_at": role_data.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE ROLE
# =====================================================
@router.put("/roles", status_code=status.HTTP_200_OK)
async def update_role(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        role_id_payload = payload.get("id")
        role_name = payload.get("role_name", "").strip()
        description = payload.get("description", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(role_id_payload, int) or role_id_payload <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid id is required"
            )

        if not role_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="role_name is required"
            )

        if len(role_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="role_name must not exceed 100 characters"
            )

        if description and len(description) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description must not exceed 255 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Roles)
            .filter(
                models.Roles.id != role_id_payload,
                func.lower(models.Roles.role_name) == role_name.lower(),
                models.Roles.company_id == company_id,
                models.Roles.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists"
            )

        # -------------------------------------------------
        # FETCH ROLE
        # -------------------------------------------------
        role = (
            db.query(models.Roles)
            .filter(
                models.Roles.id == role_id_payload,
                models.Roles.company_id == company_id,
                models.Roles.status == CommonWords.STATUS
            )
            .first()
        )

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # -------------------------------------------------
        # UPDATE ROLE
        # -------------------------------------------------
        role.role_name = role_name
        role.description = description
        role.updated_by = user_id

        db.commit()
        db.refresh(role)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Role updated successfully",
            "data": {
                "id": role.id,
                "role_name": role.role_name,
                "description": role.description,
                "company_id": role.company_id,
                "updated_by": role.updated_by,
                "updated_at": role.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE ROLE (SOFT DELETE)
# =====================================================
@router.delete("/roles/{role_id}", status_code=status.HTTP_200_OK)
def delete_role(
    request: Request,
    role_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if role_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )

        # -------------------------------------------------
        # FETCH ROLE
        # -------------------------------------------------
        role_data = (
            db.query(models.Roles)
            .filter(
                models.Roles.id == role_id,
                models.Roles.company_id == company_id,
                models.Roles.status == CommonWords.STATUS
            )
            .first()
        )

        if not role_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        role_data.status = CommonWords.UNSTATUS
        role_data.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Role deleted successfully"
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE ROLE PERMISSION
# =====================================================
@router.post("/role_permissions", status_code=status.HTTP_201_CREATED)
async def create_role_permission(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        role_id_payload = payload.get("role_id")
        menu_id = payload.get("menu_id")
        submenu_id = payload.get("submenu_id")

        view_permission = payload.get("view_permission", False)
        create_permission = payload.get("create_permission", False)
        edit_permission = payload.get("edit_permission", False)
        delete_permission = payload.get("delete_permission", False)

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(role_id_payload, int) or role_id_payload <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid role_id is required"
            )

        if not isinstance(menu_id, int) or menu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid menu_id is required"
            )

        if submenu_id is not None and (not isinstance(submenu_id, int) or submenu_id <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid submenu_id"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------
        exists = (
            db.query(models.RolePermissions)
            .filter(
                models.RolePermissions.role_id == role_id_payload,
                models.RolePermissions.menu_id == menu_id,
                models.RolePermissions.submenu_id == submenu_id,
                models.RolePermissions.company_id == company_id,
                models.RolePermissions.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists for this role"
            )

        # -------------------------------------------------
        # CREATE ROLE PERMISSION
        # -------------------------------------------------
        permission = models.RolePermissions(
            role_id=role_id_payload,
            menu_id=menu_id,
            submenu_id=submenu_id,
            view_permission=view_permission,
            create_permission=create_permission,
            edit_permission=edit_permission,
            delete_permission=delete_permission,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Role permission assigned successfully",
            "data": {
                "id": permission.id,
                "role_id": permission.role_id,
                "menu_id": permission.menu_id,
                "submenu_id": permission.submenu_id,
                "permissions": {
                    "view": permission.view_permission,
                    "create": permission.create_permission,
                    "edit": permission.edit_permission,
                    "delete": permission.delete_permission
                }
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL ROLE PERMISSIONS
# =====================================================
@router.get("/role_permissions", status_code=status.HTTP_200_OK)
def get_all_role_permissions(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH ROLE PERMISSIONS
        # -------------------------------------------------
        permissions = (
            db.query(models.RolePermissions)
            .filter(
                models.RolePermissions.company_id == company_id,
                models.RolePermissions.status == CommonWords.STATUS
            )
            .all()
        )

        roles_map: dict[int, dict] = {}

        for permission in permissions:
            # 🔴 Skip if no permission at all
            if not any([
                permission.view_permission,
                permission.create_permission,
                permission.edit_permission,
                permission.delete_permission,
            ]):
                continue

            # ------------------ ROLE ------------------
            role = (
                db.query(models.Roles)
                .filter(
                    models.Roles.id == permission.role_id,
                    models.Roles.company_id == company_id,
                    models.Roles.status == CommonWords.STATUS
                )
                .first()
            )

            if not role:
                continue

            if role.id not in roles_map:
                roles_map[role.id] = {
                    "role_id": role.id,
                    "role_name": role.role_name,
                    "menus": {}
                }

            # ------------------ MENU ------------------
            menu = (
                db.query(models.Menus)
                .filter(
                    models.Menus.id == permission.menu_id,
                    models.Menus.company_id == company_id,
                    models.Menus.status == CommonWords.STATUS
                )
                .first()
            )

            if not menu:
                continue

            menus_map = roles_map[role.id]["menus"]

            if menu.id not in menus_map:
                menus_map[menu.id] = {
                    "id": menu.id,
                    "order_no": menu.order,
                    "label": menu.menu_name,
                    "path": menu.menu_link,
                    "icon": menu.menu_icon,
                    "permissions": {
                        "add": permission.create_permission,
                        "edit": permission.edit_permission,
                        "delete": permission.delete_permission,
                        "view": permission.view_permission
                    },
                    "children": []
                }

            # ------------------ SUBMENU ------------------
            if permission.submenu_id:
                submenu = (
                    db.query(models.Submenus)
                    .filter(
                        models.Submenus.id == permission.submenu_id,
                        models.Submenus.company_id == company_id,
                        models.Submenus.status == CommonWords.STATUS
                    )
                    .first()
                )

                if submenu:
                    menus_map[menu.id]["children"].append({
                        "id": submenu.id,
                        "label": submenu.submenu_name,
                        "path": submenu.submenu_link,
                        "order_no": submenu.order,
                        "permissions": {
                            "add": permission.create_permission,
                            "edit": permission.edit_permission,
                            "delete": permission.delete_permission,
                            "view": permission.view_permission
                        }
                    })

        # ------------------ SORT MENUS & SUBMENUS ------------------
        result = []

        for role_data in roles_map.values():
            menus_list = list(role_data["menus"].values())

            for menu in menus_list:
                menu["children"].sort(key=lambda x: x.get("order_no", 0))

            menus_list.sort(key=lambda x: x.get("order_no", 0))

            result.append({
                "role_id": role_data["role_id"],
                "role_name": role_data["role_name"],
                "menus": menus_list
            })

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(result),
            "data": result
        }

    except HTTPException:
        # ✅ Preserve proper HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ROLE PERMISSIONS BY ROLE
# =====================================================
@router.get("/role_permissions/{role_id}", status_code=status.HTTP_200_OK)
def get_permissions_by_role(
    request: Request,
    role_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if role_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )

        # -------------------------------------------------
        # FETCH ROLE PERMISSIONS
        # -------------------------------------------------
        permissions = (
            db.query(models.RolePermissions)
            .filter(
                models.RolePermissions.role_id == role_id,
                models.RolePermissions.company_id == company_id,
                models.RolePermissions.status == CommonWords.STATUS
            )
            .all()
        )

        menus: dict[int, dict] = {}

        for permission in permissions:
            # 🔴 Skip if no permission at all
            if not any([
                permission.view_permission,
                permission.create_permission,
                permission.edit_permission,
                permission.delete_permission,
            ]):
                continue

            # ------------------ MENU ------------------
            menu = (
                db.query(models.Menus)
                .filter(
                    models.Menus.id == permission.menu_id,
                    models.Menus.company_id == company_id,
                    models.Menus.status == CommonWords.STATUS
                )
                .first()
            )

            if not menu:
                continue

            if menu.id not in menus:
                menus[menu.id] = {
                    "id": menu.id,
                    "order_no": menu.order,
                    "label": menu.menu_name,
                    "path": menu.menu_link,
                    "icon": menu.menu_icon,
                    "permissions": {
                        "add": permission.create_permission,
                        "edit": permission.edit_permission,
                        "delete": permission.delete_permission,
                        "view": permission.view_permission,
                    },
                    "children": []
                }

            # ------------------ SUBMENU ------------------
            if permission.submenu_id:
                submenu = (
                    db.query(models.Submenus)
                    .filter(
                        models.Submenus.id == permission.submenu_id,
                        models.Submenus.company_id == company_id,
                        models.Submenus.status == CommonWords.STATUS
                    )
                    .first()
                )

                if submenu:
                    menus[menu.id]["children"].append({
                        "id": submenu.id,
                        "label": submenu.submenu_name,
                        "path": submenu.submenu_link,
                        "order_no": submenu.order,
                        "permissions": {
                            "add": permission.create_permission,
                            "edit": permission.edit_permission,
                            "delete": permission.delete_permission,
                            "view": permission.view_permission,
                        }
                    })

        # ------------------ SORT MENUS & SUBMENUS ------------------
        for menu in menus.values():
            menu["children"].sort(key=lambda x: x.get("order_no", 0))

        sorted_menus = sorted(menus.values(), key=lambda x: x.get("order_no", 0))

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "menus": sorted_menus
            }
        }

    except HTTPException:
        # ✅ Keep correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# UPDATE ROLE PERMISSION
# =====================================================
@router.put("/role_permissions", status_code=status.HTTP_200_OK)
async def update_role_permission(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        permission_id = payload.get("id")

        view_permission = payload.get("view_permission")
        create_permission = payload.get("create_permission")
        edit_permission = payload.get("edit_permission")
        delete_permission = payload.get("delete_permission")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(permission_id, int) or permission_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid permission id is required"
            )

        if all(v is None for v in [
            view_permission,
            create_permission,
            edit_permission,
            delete_permission
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one permission must be provided"
            )

        # -------------------------------------------------
        # FETCH ROLE PERMISSION
        # -------------------------------------------------
        permission = (
            db.query(models.RolePermissions)
            .filter(
                models.RolePermissions.id == permission_id,
                models.RolePermissions.company_id == company_id,
                models.RolePermissions.status == CommonWords.STATUS
            )
            .first()
        )

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permission not found"
            )

        # -------------------------------------------------
        # UPDATE PERMISSIONS
        # -------------------------------------------------
        if view_permission is not None:
            permission.view_permission = view_permission

        if create_permission is not None:
            permission.create_permission = create_permission

        if edit_permission is not None:
            permission.edit_permission = edit_permission

        if delete_permission is not None:
            permission.delete_permission = delete_permission

        permission.updated_by = user_id

        db.commit()
        db.refresh(permission)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Role permission updated successfully",
            "data": {
                "id": permission.id,
                "role_id": permission.role_id,
                "menu_id": permission.menu_id,
                "submenu_id": permission.submenu_id,
                "permissions": {
                    "view": permission.view_permission,
                    "create": permission.create_permission,
                    "edit": permission.edit_permission,
                    "delete": permission.delete_permission
                },
                "updated_by": permission.updated_by,
                "updated_at": permission.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE ROLE PERMISSION (SOFT DELETE)
# =====================================================
@router.delete("/role_permissions/{permission_id}", status_code=status.HTTP_200_OK)
def delete_role_permission(
    request: Request,
    permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if permission_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid permission_id"
            )

        # -------------------------------------------------
        # FETCH ROLE PERMISSION
        # -------------------------------------------------
        permission = (
            db.query(models.RolePermissions)
            .filter(
                models.RolePermissions.id == permission_id,
                models.RolePermissions.company_id == company_id,
                models.RolePermissions.status == CommonWords.STATUS
            )
            .first()
        )

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permission not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        permission.status = CommonWords.UNSTATUS
        permission.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Role permission removed successfully"
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE MENU
# =====================================================
@router.post("/menus", status_code=status.HTTP_201_CREATED)
async def create_menu(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        menu_name = payload.get("menu_name", "").strip()
        menu_link = payload.get("menu_link", "").strip()
        menu_icon = payload.get("menu_icon", "").strip()
        order_no = payload.get("order_no")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not menu_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="menu_name is required"
            )

        if not menu_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="menu_link is required"
            )

        if len(menu_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="menu_name must not exceed 100 characters"
            )

        if order_no is not None and (not isinstance(order_no, int) or order_no <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="order_no must be a positive integer"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Menus)
            .filter(
                func.lower(models.Menus.menu_name) == menu_name.lower(),
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Menu already exists"
            )

        # -------------------------------------------------
        # CREATE MENU
        # -------------------------------------------------
        menu = models.Menus(
            menu_name=menu_name,
            menu_link=menu_link,
            menu_icon=menu_icon,
            order=order_no,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(menu)
        db.commit()
        db.refresh(menu)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Menu created successfully",
            "data": {
                "id": menu.id,
                "menu_name": menu.menu_name,
                "menu_link": menu.menu_link,
                "menu_icon": menu.menu_icon,
                "order_no": menu.order,
                "company_id": menu.company_id,
                "created_by": menu.created_by,
                "created_at": menu.created_at
            }
        }

    except HTTPException:
        # ✅ Preserve proper HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL MENUS
# =====================================================
@router.get("/menus", status_code=status.HTTP_200_OK)
def get_all_menus(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH MENUS
        # -------------------------------------------------
        menus = (
            db.query(models.Menus)
            .filter(
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .order_by(models.Menus.order.asc(), models.Menus.id.asc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE (NO ORM OBJECTS)
        # -------------------------------------------------
        data = [
            {
                "id": menu.id,
                "menu_name": menu.menu_name,
                "menu_link": menu.menu_link,
                "menu_icon": menu.menu_icon,
                "order_no": menu.order,
                "company_id": menu.company_id,
                "created_by": menu.created_by,
                "created_at": menu.created_at,
                "updated_at": menu.updated_at
            }
            for menu in menus
        ]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET MENU BY ID
# =====================================================
@router.get("/menus/{menu_id}", status_code=status.HTTP_200_OK)
def get_menu_by_id(
    request: Request,
    menu_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if menu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu_id"
            )

        # -------------------------------------------------
        # FETCH MENU
        # -------------------------------------------------
        menu = (
            db.query(models.Menus)
            .filter(
                models.Menus.id == menu_id,
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )

        # -------------------------------------------------
        # RESPONSE (NO ORM OBJECT)
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": menu.id,
                "menu_name": menu.menu_name,
                "menu_link": menu.menu_link,
                "menu_icon": menu.menu_icon,
                "order_no": menu.order,
                "company_id": menu.company_id,
                "created_by": menu.created_by,
                "created_at": menu.created_at,
                "updated_at": menu.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE MENU
# =====================================================
@router.put("/menus", status_code=status.HTTP_200_OK)
async def update_menu(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        menu_id = payload.get("id")
        menu_name = payload.get("menu_name", "").strip()
        menu_link = payload.get("menu_link", "").strip()
        menu_icon = payload.get("menu_icon", "").strip()
        order_no = payload.get("order_no")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(menu_id, int) or menu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid id is required"
            )

        if not menu_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="menu_name is required"
            )

        if not menu_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="menu_link is required"
            )

        if len(menu_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="menu_name must not exceed 100 characters"
            )

        if order_no is not None and (not isinstance(order_no, int) or order_no <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="order_no must be a positive integer"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Menus)
            .filter(
                models.Menus.id != menu_id,
                func.lower(models.Menus.menu_name) == menu_name.lower(),
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Menu already exists"
            )

        # -------------------------------------------------
        # FETCH MENU
        # -------------------------------------------------
        menu = (
            db.query(models.Menus)
            .filter(
                models.Menus.id == menu_id,
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )

        # -------------------------------------------------
        # UPDATE MENU
        # -------------------------------------------------
        menu.menu_name = menu_name
        menu.menu_link = menu_link
        menu.menu_icon = menu_icon
        menu.order = order_no
        menu.updated_by = user_id

        db.commit()
        db.refresh(menu)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Menu updated successfully",
            "data": {
                "id": menu.id,
                "menu_name": menu.menu_name,
                "menu_link": menu.menu_link,
                "menu_icon": menu.menu_icon,
                "order_no": menu.order,
                "company_id": menu.company_id,
                "updated_by": menu.updated_by,
                "updated_at": menu.updated_at
            }
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE MENU (SOFT DELETE)
# =====================================================
@router.delete("/menus/{menu_id}", status_code=status.HTTP_200_OK)
def delete_menu(
    request: Request,
    menu_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if menu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu_id"
            )

        # -------------------------------------------------
        # FETCH MENU
        # -------------------------------------------------
        menu = (
            db.query(models.Menus)
            .filter(
                models.Menus.id == menu_id,
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        menu.status = CommonWords.UNSTATUS
        menu.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Menu deleted successfully"
        }

    except HTTPException:
        # ✅ Preserve correct HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE SUBMENU
# =====================================================
@router.post("/submenus", status_code=status.HTTP_201_CREATED)
async def create_submenu(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        menu_id = payload.get("menu_id")
        submenu_name = payload.get("submenu_name", "").strip()
        submenu_link = payload.get("submenu_link", "").strip()
        order_no = payload.get("order_no")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(menu_id, int) or menu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid menu_id is required"
            )

        if not submenu_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submenu_name is required"
            )

        if not submenu_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submenu_link is required"
            )

        if len(submenu_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submenu_name must not exceed 100 characters"
            )

        if order_no is not None and (not isinstance(order_no, int) or order_no <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="order_no must be a positive integer"
            )

        # -------------------------------------------------
        # CHECK PARENT MENU
        # -------------------------------------------------
        menu = (
            db.query(models.Menus)
            .filter(
                models.Menus.id == menu_id,
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent menu not found"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (MENU + COMPANY SCOPED)
        # -------------------------------------------------
        exists = (
            db.query(models.Submenus)
            .filter(
                func.lower(models.Submenus.submenu_name) == submenu_name.lower(),
                models.Submenus.menu_id == menu_id,
                models.Submenus.company_id == company_id,
                models.Submenus.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Submenu already exists under this menu"
            )

        # -------------------------------------------------
        # CREATE SUBMENU
        # -------------------------------------------------
        submenu = models.Submenus(
            menu_id=menu_id,
            submenu_name=submenu_name,
            submenu_link=submenu_link,
            order=order_no,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(submenu)
        db.commit()
        db.refresh(submenu)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Submenu created successfully",
            "data": {
                "id": submenu.id,
                "menu_id": submenu.menu_id,
                "submenu_name": submenu.submenu_name,
                "submenu_link": submenu.submenu_link,
                "order_no": submenu.order,
                "company_id": submenu.company_id,
                "created_by": submenu.created_by,
                "created_at": submenu.created_at
            }
        }

    except HTTPException:
        # ✅ Preserve business errors
        raise

    except Exception as e:
        # ❌ Catch DB integrity or unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/submenus/by-menu/{menu_id}", status_code=status.HTTP_200_OK)
def get_submenus_by_menu(menu_id: int, company_id: str, db: Session = Depends(get_db)):
    submenus = db.query(models.Submenus).filter(
        models.Submenus.menu_id == str(menu_id),
        models.Submenus.company_id == company_id,
        models.Submenus.status == CommonWords.STATUS
    ).order_by(models.Submenus.id.asc()).all()

    return {
        "status": "success",
        "data": [
            {
                "id": s.id,
                "submenu_name": s.submenu_name,
                "submenu_link": s.submenu_link
            } for s in submenus
        ]
    }

# =====================================================
# GET ALL SUBMENUS
# =====================================================
@router.get("/submenus", status_code=status.HTTP_200_OK)
def get_all_submenus(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH SUBMENUS
        # -------------------------------------------------
        submenus = (
            db.query(models.Submenus)
            .filter(
                models.Submenus.company_id == company_id,
                models.Submenus.status == CommonWords.STATUS
            )
            .order_by(models.Submenus.order.asc(), models.Submenus.id.asc())
            .all()
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(submenus),
            "data": [
                {
                    "id": submenu.id,
                    "menu_id": submenu.menu_id,
                    "submenu_name": submenu.submenu_name,
                    "submenu_link": submenu.submenu_link,
                    "order_no": submenu.order,
                    "created_by": submenu.created_by,
                    "created_at": submenu.created_at,
                    "updated_at": submenu.updated_at
                }
                for submenu in submenus
            ]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET SUBMENU BY ID
# =====================================================
@router.get("/submenus/{submenu_id}", status_code=status.HTTP_200_OK)
def get_submenu_by_id(
    request: Request,
    submenu_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if submenu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid submenu_id"
            )

        # -------------------------------------------------
        # FETCH SUBMENU
        # -------------------------------------------------
        submenu = (
            db.query(models.Submenus)
            .filter(
                models.Submenus.id == submenu_id,
                models.Submenus.company_id == company_id,
                models.Submenus.status == CommonWords.STATUS
            )
            .first()
        )

        if not submenu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submenu not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": submenu.id,
                "menu_id": submenu.menu_id,
                "submenu_name": submenu.submenu_name,
                "submenu_link": submenu.submenu_link,
                "order_no": submenu.order,
                "company_id": submenu.company_id,
                "created_by": submenu.created_by,
                "created_at": submenu.created_at,
                "updated_at": submenu.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE SUBMENU
# =====================================================
@router.put("/submenus", status_code=status.HTTP_200_OK)
async def update_submenu(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        submenu_id = payload.get("id")
        menu_id = payload.get("menu_id")
        submenu_name = payload.get("submenu_name", "").strip()
        submenu_link = payload.get("submenu_link", "").strip()
        order_no = payload.get("order_no")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(submenu_id, int) or submenu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid id is required"
            )

        if not isinstance(menu_id, int) or menu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid menu_id is required"
            )

        if not submenu_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submenu_name is required"
            )

        if not submenu_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submenu_link is required"
            )

        if len(submenu_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="submenu_name must not exceed 100 characters"
            )

        if order_no is not None and (not isinstance(order_no, int) or order_no <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="order_no must be a positive integer"
            )

        # -------------------------------------------------
        # CHECK PARENT MENU
        # -------------------------------------------------
        menu = (
            db.query(models.Menus)
            .filter(
                models.Menus.id == menu_id,
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS
            )
            .first()
        )

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent menu not found"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (MENU + COMPANY SCOPED)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Submenus)
            .filter(
                models.Submenus.id != submenu_id,
                func.lower(models.Submenus.submenu_name) == submenu_name.lower(),
                models.Submenus.menu_id == menu_id,
                models.Submenus.company_id == company_id,
                models.Submenus.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Submenu already exists under this menu"
            )

        # -------------------------------------------------
        # FETCH SUBMENU
        # -------------------------------------------------
        submenu = (
            db.query(models.Submenus)
            .filter(
                models.Submenus.id == submenu_id,
                models.Submenus.company_id == company_id,
                models.Submenus.status == CommonWords.STATUS
            )
            .first()
        )

        if not submenu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submenu not found"
            )

        # -------------------------------------------------
        # UPDATE SUBMENU
        # -------------------------------------------------
        submenu.menu_id = menu_id
        submenu.submenu_name = submenu_name
        submenu.submenu_link = submenu_link
        submenu.order = order_no
        submenu.updated_by = user_id

        db.commit()
        db.refresh(submenu)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Submenu updated successfully",
            "data": {
                "id": submenu.id,
                "menu_id": submenu.menu_id,
                "submenu_name": submenu.submenu_name,
                "submenu_link": submenu.submenu_link,
                "order_no": submenu.order,
                "updated_by": submenu.updated_by,
                "updated_at": submenu.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE SUBMENU (SOFT DELETE)
# =====================================================
@router.delete("/submenus/{submenu_id}", status_code=status.HTTP_200_OK)
def delete_submenu(
    request: Request,
    submenu_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if submenu_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid submenu_id"
            )

        # -------------------------------------------------
        # FETCH SUBMENU
        # -------------------------------------------------
        submenu = (
            db.query(models.Submenus)
            .filter(
                models.Submenus.id == submenu_id,
                models.Submenus.company_id == company_id,
                models.Submenus.status == CommonWords.STATUS
            )
            .first()
        )

        if not submenu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submenu not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        submenu.status = CommonWords.UNSTATUS
        submenu.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Submenu deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL DEPARTMENTS
# =====================================================
@router.get("/departments", status_code=status.HTTP_200_OK)
def get_departments(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # SAFETY CHECK (AUTH SHOULD GUARANTEE THIS)
        # -------------------------------------------------
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH DEPARTMENTS
        # -------------------------------------------------
        departments = (
            db.query(models.Department)
            .filter(
                models.Department.company_id == company_id,
                models.Department.status == CommonWords.STATUS
            )
            .order_by(models.Department.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE DATA
        # -------------------------------------------------
        data = [
            {
                "id": department.id,
                "department_name": department.Department_Name,
                "company_id": department.company_id,
                "created_by": department.created_by,
                "created_at": department.created_at,
                "updated_at": department.updated_at,
            }
            for department in departments
        ]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }

    except HTTPException:
        # ✅ Keep expected HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only q
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE DEPARTMENT
# =====================================================
@router.post("/departments", status_code=status.HTTP_201_CREATED)
async def create_department(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        department_name = payload.get("department_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not department_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="department_name is required"
            )

        if len(department_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="department_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Department)
            .filter(
                func.lower(models.Department.Department_Name) == department_name.lower(),
                models.Department.company_id == company_id,
                models.Department.status == CommonWords.STATUS,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department already exists"
            )

        # -------------------------------------------------
        # CREATE DEPARTMENT
        # -------------------------------------------------
        department = models.Department(
            Department_Name=department_name,
            company_id=company_id,
            created_by=user_id,
            status=CommonWords.STATUS,
        )

        db.add(department)
        db.commit()
        db.refresh(department)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Department created successfully",
            "data": {
                "id": department.id,
                "department_name": department.Department_Name,
                "company_id": department.company_id,
                "created_by": department.created_by,
                "created_at": department.created_at,
            },
        }

    except HTTPException:
        # Keep intended HTTP errors
        raise

    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
# =====================================================
# GET DEPARTMENT BY ID
# =====================================================
@router.get("/departments/{department_id}", status_code=status.HTTP_200_OK)
def get_department_by_id(
    request: Request,
    department_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if department_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department_id"
            )

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH DEPARTMENT
        # -------------------------------------------------
        department = (
            db.query(models.Department)
            .filter(
                models.Department.id == department_id,
                models.Department.company_id == company_id,
                models.Department.status == CommonWords.STATUS,
            )
            .first()
        )

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": department.id,
                "department_name": department.Department_Name,
                "company_id": department.company_id,
                "created_by": department.created_by,
                "created_at": department.created_at,
                "updated_at": department.updated_at,
            }
        }

    except HTTPException:
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# UPDATE DEPARTMENT
# =====================================================
@router.put("/departments", status_code=status.HTTP_200_OK)
async def update_department(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        department_id = payload.get("id")
        department_name = payload.get("department_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not department_id or not isinstance(department_id, int) or department_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid department id is required"
            )

        if not department_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="department_name is required"
            )

        if len(department_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="department_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE NAME CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Department)
            .filter(
                models.Department.id != department_id,
                func.lower(models.Department.Department_Name) == department_name.lower(),
                models.Department.company_id == company_id,
                models.Department.status == CommonWords.STATUS,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists"
            )

        # -------------------------------------------------
        # FETCH DEPARTMENT
        # -------------------------------------------------
        department = (
            db.query(models.Department)
            .filter(
                models.Department.id == department_id,
                models.Department.company_id == company_id,
                models.Department.status == CommonWords.STATUS,
            )
            .first()
        )

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

        # -------------------------------------------------
        # UPDATE DEPARTMENT
        # -------------------------------------------------
        department.Department_Name = department_name
        department.updated_by = user_id if hasattr(department, "updated_by") else None

        db.commit()
        db.refresh(department)
        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Department updated successfully",
            "data": {
                "id": department.id,
                "department_name": department.Department_Name,
                "company_id": department.company_id,
                "updated_at": department.updated_at,
            },
        }

    except HTTPException:
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# =====================================================
# DELETE Department (SOFT DELETE)
# =====================================================
@router.delete("/departments/{department_id}", status_code=status.HTTP_200_OK)
def delete_department(
    request: Request,
    department_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if department_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department_id"
            )

        # -------------------------------------------------
        # FETCH DEPARTMENT
        # -------------------------------------------------
        department = (
            db.query(models.Department)
            .filter(
                models.Department.id == department_id,
                models.Department.company_id == company_id,
                models.Department.status == CommonWords.STATUS,
            )
            .first()
        )

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        department.status = CommonWords.UNSTATUS
        department.updated_by = user_id if hasattr(department, "updated_by") else None

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Department deleted successfully"
        }

    except HTTPException:
        # ✅ Keep expected HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL DESIGNATIONS
# =====================================================
@router.get("/designations", status_code=status.HTTP_200_OK)
def get_designations(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # SAFETY CHECK (AUTH SHOULD GUARANTEE THIS)
        # -------------------------------------------------
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH DESIGNATIONS
        # -------------------------------------------------
        designations = (
            db.query(models.Designation)
            .filter(
                models.Designation.company_id == company_id,
                models.Designation.status == CommonWords.STATUS
            )
            .order_by(models.Designation.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE DATA
        # -------------------------------------------------
        data = [
            {
                "id": designation.id,
                "designation_name": designation.Designation_Name,
                "company_id": designation.company_id,
                "created_by": designation.created_by,
                "created_at": designation.created_at,
                "updated_at": designation.updated_at,
            }
            for designation in designations
        ]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }

    except HTTPException:
        # ✅ Keep expected HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE DESIGNATION
# =====================================================
@router.post("/designations", status_code=status.HTTP_201_CREATED)
async def create_designation(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        designation_name = payload.get("designation_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not designation_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="designation_name is required"
            )

        if len(designation_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="designation_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        exists = (
            db.query(models.Designation)
            .filter(
                func.lower(models.Designation.Designation_Name) == designation_name.lower(),
                models.Designation.company_id == company_id,
                models.Designation.status == CommonWords.STATUS,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Designation already exists"
            )

        # -------------------------------------------------
        # CREATE DESIGNATION
        # -------------------------------------------------
        designation = models.Designation(
            Designation_Name=designation_name,
            company_id=company_id,
            created_by=user_id,
            status=CommonWords.STATUS,
        )

        db.add(designation)
        db.commit()
        db.refresh(designation)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Designation created successfully",
            "data": {
                "id": designation.id,
                "designation_name": designation.Designation_Name,
                "company_id": designation.company_id,
                "created_by": designation.created_by,
                "created_at": designation.created_at,
            },
        }

    except HTTPException:
        # Keep intended HTTP errors
        raise

    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
# =====================================================
# GET DESIGNATION BY ID
# =====================================================
@router.get("/designations/{designation_id}", status_code=status.HTTP_200_OK)
def get_designation_by_id(
    request: Request,
    designation_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if designation_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid designation_id"
            )

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH DESIGNATION
        # -------------------------------------------------
        designation = (
            db.query(models.Designation)
            .filter(
                models.Designation.id == designation_id,
                models.Designation.company_id == company_id,
                models.Designation.status == CommonWords.STATUS,
            )
            .first()
        )

        if not designation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Designation not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": designation.id,
                "designation_name": designation.Designation_Name,
                "company_id": designation.company_id,
                "created_by": designation.created_by,
                "created_at": designation.created_at,
                "updated_at": designation.updated_at,
            }
        }

    except HTTPException:
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# UPDATE DESIGNATION
# =====================================================
@router.put("/designations", status_code=status.HTTP_200_OK)
async def update_designation(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        designation_id = payload.get("id")
        designation_name = payload.get("designation_name", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not designation_id or not isinstance(designation_id, int) or designation_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid designation id is required"
            )

        if not designation_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="designation_name is required"
            )

        if len(designation_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="designation_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE NAME CHECK (CASE-INSENSITIVE)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Designation)
            .filter(
                models.Designation.id != designation_id,
                func.lower(models.Designation.Designation_Name) == designation_name.lower(),
                models.Designation.company_id == company_id,
                models.Designation.status == CommonWords.STATUS,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Designation name already exists"
            )

        # -------------------------------------------------
        # FETCH DESIGNATION
        # -------------------------------------------------
        designation = (
            db.query(models.Designation)
            .filter(
                models.Designation.id == designation_id,
                models.Designation.company_id == company_id,
                models.Designation.status == CommonWords.STATUS,
            )
            .first()
        )

        if not designation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Designation not found"
            )

        # -------------------------------------------------
        # UPDATE DESIGNATION
        # -------------------------------------------------
        designation.Designation_Name = designation_name
        designation.updated_by = user_id if hasattr(designation, "updated_by") else None

        db.commit()
        db.refresh(designation)
        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Designation updated successfully",
            "data": {
                "id": designation.id,
                "designation_name": designation.Designation_Name,
                "company_id": designation.company_id,
                "updated_at": designation.updated_at,
            },
        }

    except HTTPException:
        # ✅ Keep intended HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# =====================================================
# DELETE DESIGNATION (SOFT DELETE)
# =====================================================
@router.delete("/designations/{designation_id}", status_code=status.HTTP_200_OK)
def delete_designation(
    request: Request,
    designation_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if designation_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid designation_id"
            )

        # -------------------------------------------------
        # FETCH DESIGNATION
        # -------------------------------------------------
        designation = (
            db.query(models.Designation)
            .filter(
                models.Designation.id == designation_id,
                models.Designation.company_id == company_id,
                models.Designation.status == CommonWords.STATUS,
            )
            .first()
        )

        if not designation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Designation not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        designation.status = CommonWords.UNSTATUS
        designation.updated_by = user_id if hasattr(designation, "updated_by") else None

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Designation deleted successfully"
        }

    except HTTPException:
        # ✅ Keep expected HTTP errors
        raise

    except Exception as e:
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE SHIFT
# =====================================================
@router.post("/shifts", status_code=status.HTTP_201_CREATED)
async def create_shift(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        shift_name = payload.get("shift_name", "").strip()
        start_time = payload.get("start_time", "").strip()
        end_time = payload.get("end_time", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not shift_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="shift_name is required"
            )

        if not start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time is required"
            )

        if not end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_time is required"
            )

        if len(shift_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="shift_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (SHIFT NAME + COMPANY)
        # -------------------------------------------------
        exists = (
            db.query(models.Shift)
            .filter(
                func.lower(models.Shift.Shift_Name) == shift_name.lower(),
                models.Shift.company_id == company_id,
                models.Shift.status == CommonWords.STATUS
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shift already exists"
            )

        # -------------------------------------------------
        # CREATE SHIFT
        # -------------------------------------------------
        shift = models.Shift(
            Shift_Name=shift_name,
            Start_Time=start_time,
            End_Time=end_time,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id
        )

        db.add(shift)
        db.commit()
        db.refresh(shift)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Shift created successfully",
            "data": {
                "id": shift.id,
                "shift_name": shift.Shift_Name,
                "start_time": shift.Start_Time,
                "end_time": shift.End_Time,
                "company_id": shift.company_id,
                "created_by": shift.created_by,
                "created_at": shift.created_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL SHIFTS
# =====================================================
@router.get("/shifts", status_code=status.HTTP_200_OK)
def get_all_shifts(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # FETCH SHIFTS
        # -------------------------------------------------
        shifts = (
            db.query(models.Shift)
            .filter(
                models.Shift.company_id == company_id,
                models.Shift.status == CommonWords.STATUS
            )
            .order_by(models.Shift.id.desc())
            .all()
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "count": len(shifts),
            "data": [
                {
                    "id": shift.id,
                    "shift_name": shift.Shift_Name,
                    "start_time": shift.Start_Time,
                    "end_time": shift.End_Time,
                    "company_id": shift.company_id,
                    "created_by": shift.created_by,
                    "created_at": shift.created_at,
                    "updated_at": shift.updated_at
                }
                for shift in shifts
            ]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET SHIFT BY ID
# =====================================================
@router.get("/shifts/{shift_id}", status_code=status.HTTP_200_OK)
def get_shift_by_id(
    request: Request,
    shift_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if shift_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid shift_id"
            )

        # -------------------------------------------------
        # FETCH SHIFT
        # -------------------------------------------------
        shift = (
            db.query(models.Shift)
            .filter(
                models.Shift.id == shift_id,
                models.Shift.company_id == company_id,
                models.Shift.status == CommonWords.STATUS
            )
            .first()
        )

        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": shift.id,
                "shift_name": shift.Shift_Name,
                "start_time": shift.Start_Time,
                "end_time": shift.End_Time,
                "company_id": shift.company_id,
                "created_by": shift.created_by,
                "created_at": shift.created_at,
                "updated_by": shift.updated_by,
                "updated_at": shift.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# UPDATE SHIFT
# =====================================================
@router.put("/shifts", status_code=status.HTTP_200_OK)
async def update_shift(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (SAFE JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

        shift_id = payload.get("id")
        shift_name = payload.get("shift_name", "").strip()
        start_time = payload.get("start_time", "").strip()
        end_time = payload.get("end_time", "").strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not isinstance(shift_id, int) or shift_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid id is required"
            )

        if not shift_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="shift_name is required"
            )

        if not start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time is required"
            )

        if not end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_time is required"
            )

        if len(shift_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="shift_name must not exceed 100 characters"
            )

        # -------------------------------------------------
        # DUPLICATE CHECK (SHIFT NAME + COMPANY)
        # -------------------------------------------------
        duplicate = (
            db.query(models.Shift)
            .filter(
                models.Shift.id != shift_id,
                func.lower(models.Shift.Shift_Name) == shift_name.lower(),
                models.Shift.company_id == company_id,
                models.Shift.status == CommonWords.STATUS
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shift already exists"
            )

        # -------------------------------------------------
        # FETCH SHIFT
        # -------------------------------------------------
        shift = (
            db.query(models.Shift)
            .filter(
                models.Shift.id == shift_id,
                models.Shift.company_id == company_id,
                models.Shift.status == CommonWords.STATUS
            )
            .first()
        )

        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found"
            )

        # -------------------------------------------------
        # UPDATE SHIFT
        # -------------------------------------------------
        shift.Shift_Name = shift_name
        shift.Start_Time = start_time
        shift.End_Time = end_time
        shift.updated_by = user_id

        db.commit()
        db.refresh(shift)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Shift updated successfully",
            "data": {
                "id": shift.id,
                "shift_name": shift.Shift_Name,
                "start_time": shift.Start_Time,
                "end_time": shift.End_Time,
                "company_id": shift.company_id,
                "updated_by": shift.updated_by,
                "updated_at": shift.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# DELETE SHIFT (SOFT DELETE)
# =====================================================
@router.delete("/shifts/{shift_id}", status_code=status.HTTP_200_OK)
def delete_shift(
    request: Request,
    shift_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, user_role, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if shift_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid shift_id"
            )

        # -------------------------------------------------
        # FETCH SHIFT
        # -------------------------------------------------
        shift = (
            db.query(models.Shift)
            .filter(
                models.Shift.id == shift_id,
                models.Shift.company_id == company_id,
                models.Shift.status == CommonWords.STATUS
            )
            .first()
        )

        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        shift.status = CommonWords.UNSTATUS
        shift.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Shift deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt
import uuid

from resources.utils import verify_authentication
from models import models
from models import get_db
from configs.base_config import CommonWords

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, user_role, token = verify_authentication(request)
        payload = await request.json()

        required_fields = [
            "username","first_name","last_name","personal_email","company_email",
            "password","mobile","dob","gender","marital_status","address",
            "city","state","postal_code","country","department_id","role_id",
            "shift_id","date_of_joining","experience","salary_details",
            "register_code","emergency_name","emergency_contact",
            "emergency_relationship","created_by","company_id"
        ]

        for field in required_fields:
            if not payload.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field} is required"
                )

        # Duplicate company email check
        exists = db.query(models.Users).filter(
            func.lower(models.Users.Company_Email) == payload["company_email"].lower(),
            models.Users.status == CommonWords.STATUS
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company email already exists"
            )

        hashed_password = bcrypt.hashpw(
            payload["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        user_code = f"EMP-{uuid.uuid4().hex[:8].upper()}"

        user = models.Users(
            User_Code=user_code,
            username=payload["username"],
            First_Name=payload["first_name"],
            Last_Name=payload["last_name"],
            Personal_Email=payload["personal_email"],
            Company_Email=payload["company_email"],
            Password=hashed_password,
            Mobile=payload["mobile"],
            D_O_B=payload["dob"],
            Gender=payload["gender"],
            Marital_Status=payload["marital_status"],
            Address=payload["address"],
            City=payload["city"],
            State=payload["state"],
            Postal_Code=payload["postal_code"],
            Country=payload["country"],
            Department_ID=payload["department_id"],
            Role_ID=payload["role_id"],
            Shift_ID=payload["shift_id"],
            Date_Of_Joining=payload["date_of_joining"],
            Experience=payload["experience"],
            Salary_Details=payload["salary_details"],
            Register_Code=payload["register_code"],
            Emergency_Name=payload["emergency_name"],
            Emergency_Contact=payload["emergency_contact"],
            Emergency_Relationship=payload["emergency_relationship"],
            status=CommonWords.STATUS,
            created_by=payload["created_by"],
            company_id=payload["company_id"]
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "User created successfully",
            "data": {
                "id": user.id,
                "user_code": user.User_Code,
                "username": user.username,
                "company_email": user.Company_Email
            }
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(http_exc.detail)) from http_exc

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
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
            "role_id": user.Role_ID,
            "shift_id": user.Shift_ID,
            "date_of_joining": user.Date_Of_Joining,
            "experience": user.Experience,
            "salary_details": user.Salary_Details,
            "register_code": user.Register_Code,
            "emergency_name": user.Emergency_Name,
            "emergency_contact": user.Emergency_Contact,
            "emergency_relationship": user.Emergency_Relationship,
            "status": user.status,
            "company_id": user.company_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    }


@router.get("/login_user/{usermail}", status_code=status.HTTP_200_OK)
def get_user_by_mail(
    usermail: str,
    # company_id: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(models.Users)
        .filter(
            models.Users.Company_Email == usermail,
            # models.Users.company_id == company_id,
            models.Users.status == CommonWords.STATUS
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

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
            "role_id": user.Role_ID,
            "shift_id": user.Shift_ID,
            "date_of_joining": user.Date_Of_Joining,
            "experience": user.Experience,
            "salary_details": user.Salary_Details,
            "register_code": user.Register_Code,
            "emergency_name": user.Emergency_Name,
            "emergency_contact": user.Emergency_Contact,
            "emergency_relationship": user.Emergency_Relationship,
            "status": user.status,
            "company_id": user.company_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    }

@router.put("/users", status_code=status.HTTP_200_OK)
async def update_user(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    user_id = payload.get("id")
    company_id = payload.get("company_id")

    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id and company_id are required"
        )

    user = db.query(models.Users).filter(
        models.Users.id == user_id,
        models.Users.company_id == company_id,
        models.Users.status == CommonWords.STATUS
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # ================= DUPLICATE COMPANY EMAIL CHECK =================
    if payload.get("company_email"):
        duplicate = db.query(models.Users).filter(
            models.Users.id != user_id,
            func.lower(models.Users.Company_Email) == payload["company_email"].lower(),
            models.Users.status == CommonWords.STATUS
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company email already exists"
            )

    # ================= UPDATE FIELDS =================
    user.username = payload.get("username", user.username)
    user.First_Name = payload.get("first_name", user.First_Name)
    user.Last_Name = payload.get("last_name", user.Last_Name)
    user.Personal_Email = payload.get("personal_email", user.Personal_Email)
    user.Company_Email = payload.get("company_email", user.Company_Email)
    user.Mobile = payload.get("mobile", user.Mobile)
    user.Alternative_Mobile = payload.get("alternative_mobile", user.Alternative_Mobile)
    user.D_O_B = payload.get("dob", user.D_O_B)
    user.Gender = payload.get("gender", user.Gender)
    user.Marital_Status = payload.get("marital_status", user.Marital_Status)
    user.Address = payload.get("address", user.Address)
    user.City = payload.get("city", user.City)
    user.State = payload.get("state", user.State)
    user.Postal_Code = payload.get("postal_code", user.Postal_Code)
    user.Country = payload.get("country", user.Country)
    user.Department_ID = payload.get("department_id", user.Department_ID)
    user.Role_ID = payload.get("role_id", user.Role_ID)
    user.Shift_ID = payload.get("shift_id", user.Shift_ID)
    user.Date_Of_Joining = payload.get("date_of_joining", user.Date_Of_Joining)
    user.Experience = payload.get("experience", user.Experience)
    user.Salary_Details = payload.get("salary_details", user.Salary_Details)
    user.Register_Code = payload.get("register_code", user.Register_Code)
    user.Emergency_Name = payload.get("emergency_name", user.Emergency_Name)
    user.Emergency_Contact = payload.get("emergency_contact", user.Emergency_Contact)
    user.Emergency_Relationship = payload.get("emergency_relationship", user.Emergency_Relationship)
    user.updated_by = payload.get("updated_by")

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "User updated successfully",
        "data": {
            "id": user.id,
            "username": user.username,
            "company_email": user.Company_Email,
            "company_id": user.company_id
        }
    }

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    company_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.Users).filter(
        models.Users.id == user_id,
        models.Users.company_id == company_id,
        models.Users.status == CommonWords.STATUS
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.status = CommonWords.UNSTATUS
    db.commit()

    return {
        "status": "success",
        "message": "User deleted successfully"
    }

@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    role_name = payload.get("role_name")
    description = payload.get("description")
    created_by = payload.get("created_by")
    company_id = payload.get("company_id")

    if not all([role_name, created_by, company_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role_name, created_by and company_id are required"
        )

    exists = db.query(models.Roles).filter(
        func.lower(models.Roles.role_name) == role_name.lower(),
        models.Roles.company_id == company_id,
        models.Roles.status == CommonWords.STATUS
    ).first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists"
        )

    role = models.Roles(
        role_name=role_name,
        description=description,
        status=CommonWords.STATUS,
        created_by=created_by,
        company_id=company_id
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return {
        "status": "success",
        "message": "Role created successfully",
        "data": {
            "id": role.id,
            "role_name": role.role_name
        }
    }

@router.get("/roles", status_code=status.HTTP_200_OK)
def get_all_roles(company_id: str, db: Session = Depends(get_db)):
    roles = db.query(models.Roles).filter(
        models.Roles.company_id == company_id,
        models.Roles.status == CommonWords.STATUS
    ).order_by(models.Roles.id.desc()).all()

    return {
        "status": "success",
        "data": [
            {
                "id": r.id,
                "role_name": r.role_name,
                "description": r.description,
                "created_at": r.created_at
            } for r in roles
        ]
    }

@router.get("/roles/{role_id}", status_code=status.HTTP_200_OK)
def get_role_by_id(role_id: int, company_id: str, db: Session = Depends(get_db)):
    role = db.query(models.Roles).filter(
        models.Roles.id == role_id,
        models.Roles.company_id == company_id,
        models.Roles.status == CommonWords.STATUS
    ).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return {
        "status": "success",
        "data": {
            "id": role.id,
            "role_name": role.role_name,
            "description": role.description
        }
    }

@router.put("/roles", status_code=status.HTTP_200_OK)
async def update_role(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    role_id = payload.get("id")
    role_name = payload.get("role_name")
    description = payload.get("description")
    company_id = payload.get("company_id")

    if not all([role_id, role_name, company_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id, role_name and company_id are required"
        )

    duplicate = db.query(models.Roles).filter(
        models.Roles.id != role_id,
        func.lower(models.Roles.role_name) == role_name.lower(),
        models.Roles.company_id == company_id,
        models.Roles.status == CommonWords.STATUS
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role name already exists"
        )

    role = db.query(models.Roles).filter(
        models.Roles.id == role_id,
        models.Roles.company_id == company_id,
        models.Roles.status == CommonWords.STATUS
    ).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    role.role_name = role_name
    role.description = description

    db.commit()
    db.refresh(role)

    return {
        "status": "success",
        "message": "Role updated successfully"
    }

@router.delete("/roles/{role_id}", status_code=status.HTTP_200_OK)
def delete_role(role_id: int, company_id: str, db: Session = Depends(get_db)):
    role = db.query(models.Roles).filter(
        models.Roles.id == role_id,
        models.Roles.company_id == company_id,
        models.Roles.status == CommonWords.STATUS
    ).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    role.status = CommonWords.UNSTATUS
    db.commit()

    return {
        "status": "success",
        "message": "Role deleted successfully"
    }

@router.post("/role-permissions", status_code=status.HTTP_201_CREATED)
async def create_role_permission(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    required_fields = ["role_id", "menu_id", "created_by", "company_id"]
    for field in required_fields:
        if not payload.get(field):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field} is required"
            )

    exists = db.query(models.RolePermissions).filter(
        models.RolePermissions.role_id == payload["role_id"],
        models.RolePermissions.menu_id == payload["menu_id"],
        models.RolePermissions.submenu_id == payload.get("submenu_id"),
        models.RolePermissions.company_id == payload["company_id"],
        models.RolePermissions.status == CommonWords.STATUS
    ).first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already exists for this role"
        )

    permission = models.RolePermissions(
        role_id=payload["role_id"],
        menu_id=payload["menu_id"],
        submenu_id=payload.get("submenu_id"),
        view_permission=payload.get("view_permission", False),
        create_permission=payload.get("create_permission", False),
        edit_permission=payload.get("edit_permission", False),
        delete_permission=payload.get("delete_permission", False),
        status=CommonWords.STATUS,
        created_by=payload["created_by"],
        company_id=payload["company_id"]
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return {
        "status": "success",
        "message": "Role permission assigned successfully",
        "data": {
            "id": permission.id
        }
    }

@router.get("/role-permissions/{role_id}", status_code=status.HTTP_200_OK)
def get_permissions_by_role(
    role_id: str,
    # company_id: str,
    db: Session = Depends(get_db)
):
    permissions = db.query(models.RolePermissions).filter(
        models.RolePermissions.role_id == role_id,
        # models.RolePermissions.company_id == company_id,
        models.RolePermissions.status == CommonWords.STATUS
    ).all()

    return {
        "status": "success",
        "data": [
            {
                "id": p.id,
                "menu_id": p.menu_id,
                "submenu_id": p.submenu_id,
                "view": p.view_permission,
                "create": p.create_permission,
                "edit": p.edit_permission,
                "delete": p.delete_permission
            }
            for p in permissions
        ]
    }

@router.put("/role-permissions", status_code=status.HTTP_200_OK)
async def update_role_permission(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    permission = db.query(models.RolePermissions).filter(
        models.RolePermissions.id == payload.get("id"),
        models.RolePermissions.status == CommonWords.STATUS
    ).first()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    permission.view_permission = payload.get("view_permission", permission.view_permission)
    permission.create_permission = payload.get("create_permission", permission.create_permission)
    permission.edit_permission = payload.get("edit_permission", permission.edit_permission)
    permission.delete_permission = payload.get("delete_permission", permission.delete_permission)
    permission.updated_by = payload.get("updated_by")

    db.commit()

    return {
        "status": "success",
        "message": "Role permission updated successfully"
    }

@router.delete("/role-permissions/{permission_id}", status_code=status.HTTP_200_OK)
def delete_role_permission(permission_id: int, db: Session = Depends(get_db)):
    permission = db.query(models.RolePermissions).filter(
        models.RolePermissions.id == permission_id,
        models.RolePermissions.status == CommonWords.STATUS
    ).first()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    permission.status = CommonWords.UNSTATUS
    db.commit()

    return {
        "status": "success",
        "message": "Role permission removed successfully"
    }

@router.post("/menus", status_code=status.HTTP_201_CREATED)
async def create_menu(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    menu_name = payload.get("menu_name")
    menu_link = payload.get("menu_link")
    menu_icon = payload.get("menu_icon")
    created_by = payload.get("created_by")
    company_id = payload.get("company_id")

    if not all([menu_name, menu_link, created_by, company_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="menu_name, menu_link, created_by and company_id are required"
        )

    exists = db.query(models.Menus).filter(
        func.lower(models.Menus.menu_name) == menu_name.lower(),
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Menu already exists"
        )

    menu = models.Menus(
        menu_name=menu_name,
        menu_link=menu_link,
        menu_icon=menu_icon,
        status=CommonWords.STATUS,
        created_by=created_by,
        company_id=company_id
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    return {
        "status": "success",
        "message": "Menu created successfully",
        "data": {
            "id": menu.id,
            "menu_name": menu.menu_name
        }
    }

@router.get("/menus", status_code=status.HTTP_200_OK)
def get_all_menus(company_id: str, db: Session = Depends(get_db)):
    menus = db.query(models.Menus).filter(
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).order_by(models.Menus.id.asc()).all()

    return {
        "status": "success",
        "data": [
            {
                "id": m.id,
                "menu_name": m.menu_name,
                "menu_link": m.menu_link,
                "menu_icon": m.menu_icon,
                "created_at": m.created_at
            } for m in menus
        ]
    }

@router.get("/menus/{menu_id}", status_code=status.HTTP_200_OK)
def get_menu_by_id(menu_id: int, company_id: str, db: Session = Depends(get_db)):
    menu = db.query(models.Menus).filter(
        models.Menus.id == menu_id,
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    return {
        "status": "success",
        "data": {
            "id": menu.id,
            "menu_name": menu.menu_name,
            "menu_link": menu.menu_link,
            "menu_icon": menu.menu_icon
        }
    }

@router.put("/menus", status_code=status.HTTP_200_OK)
async def update_menu(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    menu_id = payload.get("id")
    menu_name = payload.get("menu_name")
    menu_link = payload.get("menu_link")
    menu_icon = payload.get("menu_icon")
    updated_by = payload.get("updated_by")
    company_id = payload.get("company_id")

    if not all([menu_id, menu_name, menu_link, company_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id, menu_name, menu_link and company_id are required"
        )

    duplicate = db.query(models.Menus).filter(
        models.Menus.id != menu_id,
        func.lower(models.Menus.menu_name) == menu_name.lower(),
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Menu name already exists"
        )

    menu = db.query(models.Menus).filter(
        models.Menus.id == menu_id,
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    menu.menu_name = menu_name
    menu.menu_link = menu_link
    menu.menu_icon = menu_icon
    menu.updated_by = updated_by

    db.commit()
    db.refresh(menu)

    return {
        "status": "success",
        "message": "Menu updated successfully"
    }

@router.delete("/menus/{menu_id}", status_code=status.HTTP_200_OK)
def delete_menu(menu_id: int, company_id: str, db: Session = Depends(get_db)):
    menu = db.query(models.Menus).filter(
        models.Menus.id == menu_id,
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    menu.status = CommonWords.UNSTATUS
    db.commit()

    return {
        "status": "success",
        "message": "Menu deleted successfully"
    }

@router.post("/submenus", status_code=status.HTTP_201_CREATED)
async def create_submenu(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    menu_id = payload.get("menu_id")
    submenu_name = payload.get("submenu_name")
    submenu_link = payload.get("submenu_link")
    created_by = payload.get("created_by")
    company_id = payload.get("company_id")

    if not all([menu_id, submenu_name, submenu_link, created_by, company_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="menu_id, submenu_name, submenu_link, created_by and company_id are required"
        )

    menu_exists = db.query(models.Menus).filter(
        models.Menus.id == int(menu_id),
        models.Menus.company_id == company_id,
        models.Menus.status == CommonWords.STATUS
    ).first()

    if not menu_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent menu not found"
        )

    exists = db.query(models.Submenus).filter(
        func.lower(models.Submenus.submenu_name) == submenu_name.lower(),
        models.Submenus.company_id == company_id,
        models.Submenus.status == CommonWords.STATUS
    ).first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submenu already exists"
        )

    submenu = models.Submenus(
        menu_id=str(menu_id),
        submenu_name=submenu_name,
        submenu_link=submenu_link,
        status=CommonWords.STATUS,
        created_by=created_by,
        company_id=company_id
    )

    db.add(submenu)
    db.commit()
    db.refresh(submenu)

    return {
        "status": "success",
        "message": "Submenu created successfully",
        "data": {
            "id": submenu.id,
            "submenu_name": submenu.submenu_name
        }
    }

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

@router.get("/submenus/{submenu_id}", status_code=status.HTTP_200_OK)
def get_submenu_by_id(submenu_id: int, company_id: str, db: Session = Depends(get_db)):
    submenu = db.query(models.Submenus).filter(
        models.Submenus.id == submenu_id,
        models.Submenus.company_id == company_id,
        models.Submenus.status == CommonWords.STATUS
    ).first()

    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submenu not found"
        )

    return {
        "status": "success",
        "data": {
            "id": submenu.id,
            "menu_id": submenu.menu_id,
            "submenu_name": submenu.submenu_name,
            "submenu_link": submenu.submenu_link
        }
    }

@router.put("/submenus", status_code=status.HTTP_200_OK)
async def update_submenu(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    submenu_id = payload.get("id")
    menu_id = payload.get("menu_id")
    submenu_name = payload.get("submenu_name")
    submenu_link = payload.get("submenu_link")
    updated_by = payload.get("updated_by")
    company_id = payload.get("company_id")

    if not all([submenu_id, menu_id, submenu_name, submenu_link, company_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id, menu_id, submenu_name, submenu_link and company_id are required"
        )

    duplicate = db.query(models.Submenus).filter(
        models.Submenus.id != submenu_id,
        func.lower(models.Submenus.submenu_name) == submenu_name.lower(),
        models.Submenus.company_id == company_id,
        models.Submenus.status == CommonWords.STATUS
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submenu name already exists"
        )

    submenu = db.query(models.Submenus).filter(
        models.Submenus.id == submenu_id,
        models.Submenus.company_id == company_id,
        models.Submenus.status == CommonWords.STATUS
    ).first()

    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submenu not found"
        )

    submenu.menu_id = str(menu_id)
    submenu.submenu_name = submenu_name
    submenu.submenu_link = submenu_link
    submenu.updated_by = updated_by

    db.commit()
    db.refresh(submenu)

    return {
        "status": "success",
        "message": "Submenu updated successfully"
    }

@router.delete("/submenus/{submenu_id}", status_code=status.HTTP_200_OK)
def delete_submenu(submenu_id: int, company_id: str, db: Session = Depends(get_db)):
    submenu = db.query(models.Submenus).filter(
        models.Submenus.id == submenu_id,
        models.Submenus.company_id == company_id,
        models.Submenus.status == CommonWords.STATUS
    ).first()

    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submenu not found"
        )

    submenu.status = CommonWords.UNSTATUS
    db.commit()

    return {
        "status": "success",
        "message": "Submenu deleted successfully"
    }


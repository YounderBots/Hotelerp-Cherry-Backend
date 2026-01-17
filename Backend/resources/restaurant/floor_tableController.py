from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from configs.base_config import BaseConfig, CommonWords
from models import get_db, models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/floor_layout")
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
                return templates.TemplateResponse('restaurant/floor_table/floor_layout.html', context={'request': request,'color_theme':color_theme,'inquiry_data':inquiry_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/edit_floor")
def floor_details_page(
    request: Request,
    floor: str = None,
    db: Session = Depends(get_db)
):
    if "sessid" not in request.session:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    token = request.session["sessid"]
    try:
        payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
        created_by = payload.get("user_id")
        Loginer_Role = payload.get("user_role_id")

        if not created_by:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        # ===== TEMP DATA (replace with DB later) =====
        floor_data = {
            "floor_id": floor,
            "floor_name": "Indoor Floor",
            "description": "Primary dining area with window seating",
            "total_tables": 24,
            "status": "Active"
        }

        tables = [
            {
                "table_id": "T01",
                "table_name": "Window Table 1",
                "capacity": 4,
                "type": "Standard",
                "order_id": "-",
                "server": "-",
                "status": "Available"
            },
            {
                "table_id": "T02",
                "table_name": "Center Table 2",
                "capacity": 6,
                "type": "Large",
                "order_id": "#ORD-2025-001",
                "server": "Mike Chen",
                "status": "Occupied"
            },
            {
                "table_id": "T03",
                "table_name": "Booth 1",
                "capacity": 4,
                "type": "VIP",
                "order_id": "-",
                "server": "-",
                "status": "Reserved"
            }
        ]

        color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
        permision_control = db.query(models.Role_Permission)\
            .filter(models.Role_Permission.Role_ID == Loginer_Role)\
            .filter(models.Role_Permission.status == CommonWords.STATUS).first()
        loginer_data = db.query(models.Employee_Data)\
            .filter(models.Employee_Data.id == created_by)\
            .filter(models.Employee_Data.status == CommonWords.STATUS).first()

        return templates.TemplateResponse(
            "restaurant/floor_table/edit_floor.html",
            {
                "request": request,
                "floor": floor_data,
                "tables": tables,
                "color_theme": color_theme,
                "permision_control": permision_control,
                "loginer_data": loginer_data,
            }
        )

    except JWTError:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/floor_view")
def floor_view_page(
    request: Request,
    floor_id: str,
    db: Session = Depends(get_db)
):
    # ------------------ Session Check ------------------
    if "sessid" not in request.session:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    token = request.session["sessid"]

    try:
        payload = jwt.decode(
            token,
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM]
        )

        created_by = payload.get("user_id")
        loginer_role = payload.get("user_role_id")

        if not created_by:
            return RedirectResponse(
                CommonWords.LOGINER_URL,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )

        # ================= TEMP DATA (Replace with DB) =================

        floor_data = {
            "floor_id": floor_id,
            "floor_name": "Indoor Floor",
            "description": "Primary dining area with window seating",
            "status": "Active",
            "operational_hours": "10:00 AM – 11:00 PM",
            "total_tables": 24,
            "active_tables": 22,
            "inactive_tables": 2,
            "max_capacity": 96,
            "total_orders": 154,
            "current_orders": 12,
            "total_staffs": 8
        }

        tables = [
            {
                "table_id": "T01",
                "table_name": "Window Table",
                "capacity": 4,
                "table_type": "Standard",
                "section": "Indoor",
                "status": "Available",
                "server": "Ramesh"
            },
            {
                "table_id": "T05",
                "table_name": "Corner Booth",
                "capacity": 6,
                "table_type": "VIP",
                "section": "Indoor",
                "status": "Occupied",
                "server": "Suresh"
            }
        ]

        orders = [
            {
                "order_id": "#ORD1245",
                "table_id": "T05",
                "order_type": "Dine-In",
                "order_time": "07:45 PM",
                "total_items": 5,
                "status": "In Progress",
                "server": "Suresh"
            }
        ]

        staffs = [
            {
                "staff_id": "STF105",
                "staff_name": "Suresh",
                "role": "Waiter",
                "shift": "Evening",
                "contact": "9876543210",
                "assigned_tables": 4,
                "status": "Active"
            }
        ]

        # ================= COMMON LAYOUT DATA =================
        color_theme = db.query(models.Themes)\
            .filter(models.Themes.status == CommonWords.STATUS)\
            .first()

        permision_control = db.query(models.Role_Permission)\
            .filter(models.Role_Permission.Role_ID == loginer_role)\
            .filter(models.Role_Permission.status == CommonWords.STATUS)\
            .first()

        loginer_data = db.query(models.Employee_Data)\
            .filter(models.Employee_Data.id == created_by)\
            .filter(models.Employee_Data.status == CommonWords.STATUS)\
            .first()

        # ================= RENDER VIEW =================
        return templates.TemplateResponse(
            "restaurant/floor_table/floor_view.html",
            {
                "request": request,
                "floor": floor_data,
                "tables": tables,
                "orders": orders,
                "staffs": staffs,
                "color_theme": color_theme,
                "permision_control": permision_control,
                "loginer_data": loginer_data,
            }
        )

    except JWTError:
        return RedirectResponse(
            CommonWords.LOGINER_URL,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

@router.get("/table_master")
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
                return templates.TemplateResponse('restaurant/floor_table/table_master.html', context={'request': request,'color_theme':color_theme,'inquiry_data':inquiry_data,'permision_control':permision_control,
                                                                                          'loginer_data':loginer_data,})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        return RedirectResponse(CommonWords.LOGINER_URL,status_code=status.HTTP_307_TEMPORARY_REDIRECT)
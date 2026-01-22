from fastapi import APIRouter, Depends, Form, status, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt
import uuid

from Backend.Services.LoginServices.resources.utils import create_access_token, fetch_from_service
from models import models
from models import get_db
from configs.base_config import CommonWords, ServiceURL

router = APIRouter()
@router.post("/login_post")
async def login_post(
    request: Request,
    usermail: str = Form(...),
    password: str = Form(...),
):
    try:
        name_check = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/login_user/{usermail}"
        )
 
        user_data = name_check.get("user")
 
        if not user_data or user_data.get("password") != password:
            return JSONResponse({"error": "Invalid credentials"}, status_code=401)
 
        access_token = create_access_token(
            data={
                "loginer_name": user_data.get("id"),
                "loginer_role": user_data.get("role_id"),
            }
        )
        request.session["loginer_details"] = access_token
 
        headers = {"Authorization": f"Bearer {access_token}"}
 
        role_permission_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/rolepermission/{user_data.get("role_id")}",
            headers=headers,
        )
 
        menu_link = "/"
 
        if role_permission_response and role_permission_response.get("menus"):
            first_menu = role_permission_response["menus"][0]
            if first_menu.get("submenus"):
                menu_link = first_menu["submenus"][0]["submenu_link"]
            else:
                menu_link = first_menu["menu_link"]
 
        return JSONResponse(
            content={
                "url": menu_link,
                "user": {
                    "id": user_data.get("id"),
                    "email": user_data.get("email", usermail),
                    "role_id": user_data.get("role_id"),
                },
                "rolepermission": role_permission_response,
            }
        )
 
    except HTTPException:
        return JSONResponse(
            {"error": "Login failed"},
            status_code=500,
        )
 
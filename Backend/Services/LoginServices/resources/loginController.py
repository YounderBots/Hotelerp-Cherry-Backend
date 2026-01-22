from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse

from resources.utils import create_access_token, fetch_from_service, verify_password
from configs.base_config import ServiceURL

router = APIRouter()

@router.post("/login_post")
async def login_post(
    request: Request,
    usermail: str = Form(...),
    password: str = Form(...)
):
    try:
        # 1️⃣ Fetch user from USER service
        user_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/login_user/{usermail}"
        )

        user_data = user_response.get("data")

        if not user_data:
            return JSONResponse(
                {"error": "User not found"},
                status_code=404
            )

        # 2️⃣ Verify password
        if not verify_password(password, user_data.get("password")):
            return JSONResponse(
                {"error": "Invalid credentials"},
                status_code=401
            )

        # 3️⃣ Create JWT token
        access_token = create_access_token(
            data={
                "user_id": user_data.get("id"),
                "role_id": user_data.get("role_id")
            }
        )

        # Optional: store in session (for HTML)
        request.session["access_token"] = access_token

        # 4️⃣ Fetch role permissions
        role_permission_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/role-permissions/{user_data.get('role_id')}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # 5️⃣ Decide redirect URL
        redirect_url = "/dashboard"

        if role_permission_response and role_permission_response.get("menus"):
            first_menu = role_permission_response["menus"][0]
            if first_menu.get("submenus"):
                redirect_url = first_menu["submenus"][0]["submenu_link"]
            else:
                redirect_url = first_menu.get("menu_link", "/dashboard")

        # 6️⃣ FINAL RESPONSE FOR FRONTEND
        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "redirect_url": redirect_url,
                "user": {
                    "id": user_data.get("id"),
                    "email": user_data.get("company_email", usermail),
                    "role_id": user_data.get("role_id")
                },
                "role_permissions": role_permission_response
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            {"error": "Login failed"},
            status_code=500
        )

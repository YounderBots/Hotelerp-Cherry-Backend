import httpx
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse

from resources.utils import call_service, create_access_token, fetch_from_service, verify_password
from configs.base_config import ServiceURL

router = APIRouter()

@router.post("/login_post")
async def login_post(
    request: Request,payload: dict
):
    
    try:
        email = payload.get("email")
        password = payload.get("password")
        # 1️⃣ Fetch user from USER service
        user_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/login_user/{email}"
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
                "role_id": user_data.get("role_id"),
                "company_id": user_data.get("company_id")
            }
        )

        # Optional: store in session (for HTML)
        request.session["access_token"] = access_token

        # 4️⃣ Fetch role permissions
        response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/role-permissions/{user_data.get('role_id')}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        role_permission_response = response.get("data", {})

        # 5️⃣ Decide redirect URL
        redirect_url = "/dashboard"

        if role_permission_response and role_permission_response.get("menus"):
            first_menu = role_permission_response["menus"][0]
            if first_menu.get("children"):
                redirect_url = first_menu["children"][0]["path"]
            else:
                redirect_url = first_menu.get("path", "/dashboard")

        # 6️⃣ FINAL RESPONSE FOR FRONTEND
        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "redirect_url": redirect_url,
                "user": {
                    "id": user_data.get("id"),
                    "email": user_data.get("company_email", email),
                    "role_id": user_data.get("role_id")
                },
                "menus": role_permission_response.get("menus", [])
            },
            status_code=200
        )

    except Exception as e:
        print(e)
        return JSONResponse(
            {"error": "Login failed"},
            status_code=500
        )

@router.api_route(
    "/masterdata/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def facilities_proxy(request: Request, path: str):

    auth_header = request.headers.get("Authorization")
    company_id = request.headers.get("company_id")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    params = dict(request.query_params)
    content_type = request.headers.get("content-type", "")

    forward_headers = {
        "Authorization": auth_header
    }
    if company_id:
        forward_headers["company_id"] = company_id

    async with httpx.AsyncClient(timeout=60) as client:

        # =================================================
        # GET / DELETE (NO BODY)
        # =================================================
        if request.method in ["GET", "DELETE"]:
            response = await client.request(
                method=request.method,
                url=f"{ServiceURL.MASTER_SERVICE_URL}/{path}",
                headers=forward_headers,
                params=params
            )

        # =================================================
        # MULTIPART (FILES)
        # =================================================
        elif "multipart/form-data" in content_type:
            form = await request.form()
            data = {}
            files = []

            for key, value in form.items():
                if hasattr(value, "filename"):
                    files.append(
                        (key, (value.filename, await value.read(), value.content_type))
                    )
                else:
                    data[key] = value

            response = await client.request(
                method=request.method,
                url=f"{ServiceURL.MASTER_SERVICE_URL}/{path}",
                headers=forward_headers,
                data=data,
                files=files,
                params=params
            )

        # =================================================
        # JSON (PUT / POST) — EVEN IF CONTENT-TYPE IS MISSING
        # =================================================
        else:
            try:
                body = await request.json()
            except Exception:
                body = None  # allow empty body

            response = await client.request(
                method=request.method,
                url=f"{ServiceURL.MASTER_SERVICE_URL}/{path}",
                headers=forward_headers,
                json=body,
                params=params
            )

    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )


# @router.post("/masterdata")
# async def facilities(
#     request: Request,
#     payload: dict
# ):
#     try:
#         access_token = request.headers.get("Authorization")

#         response = await call_service(
#             method="POST",
#             url=f"{ServiceURL.MASTER_SERVICE_URL}/facilities",
#             headers={
#                 "Authorization": access_token,
#                 "Content-Type": "application/json"
#             },
#             data=payload
#         )

#         return response

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


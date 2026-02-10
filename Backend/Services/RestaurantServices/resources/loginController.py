import httpx
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session 

from resources.utils import call_service, create_access_token, fetch_from_service, verify_password
from configs.base_config import ServiceURL
from models import get_db

router = APIRouter()

# =====================================================
# LOGIN
# =====================================================
@router.post("/login_post", status_code=200)
async def login_post(
    request: Request,
    db: Session = Depends(get_db)  # optional if needed later
):
    try:
        # -------------------------------------------------
        # REQUEST BODY
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON body"
            )

        email = payload.get("email")
        password = payload.get("password")

        if not email or not password:
            raise HTTPException(
                status_code=400,
                detail="email and password are required"
            )

        # -------------------------------------------------
        # FETCH USER FROM USER SERVICE
        # -------------------------------------------------
        user_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/login_user/{email}"
        )

        user_data = user_response.get("data")

        if not user_data:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # -------------------------------------------------
        # VERIFY PASSWORD
        # -------------------------------------------------
        if not verify_password(password, user_data.get("password")):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        # -------------------------------------------------
        # CREATE JWT TOKEN
        # -------------------------------------------------
        access_token = create_access_token(
            data={
                "user_id": user_data.get("id"),
                "role_id": user_data.get("role_id"),
                "company_id": user_data.get("company_id")
            }
        )

        # Optional (for server-side session usage)
        request.session["access_token"] = access_token

        # -------------------------------------------------
        # FETCH ROLE PERMISSIONS
        # -------------------------------------------------
        permission_response = await fetch_from_service(
            f"{ServiceURL.USER_SERVICE_URL}/role_permissions/{user_data.get('role_id')}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        menus = permission_response.get("data", {}).get("menus", [])

        # -------------------------------------------------
        # DECIDE REDIRECT URL
        # -------------------------------------------------
        redirect_url = "/dashboard"

        if menus:
            first_menu = menus[0]
            if first_menu.get("children"):
                redirect_url = first_menu["children"][0].get("path", "/dashboard")
            else:
                redirect_url = first_menu.get("path", "/dashboard")

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "redirect_url": redirect_url,
            "user": {
                "id": user_data.get("id"),
                "email": user_data.get("company_email"),
                "role_id": user_data.get("role_id"),
                "company_id": user_data.get("company_id")
            },
            "menus": menus
        }

    except HTTPException:
        raise

    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Login failed"
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

@router.api_route(
    "/hotel/{path:path}",
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
                url=f"{ServiceURL.HOTEL_SERVICE_URL}/{path}",
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
                url=f"{ServiceURL.HOTEL_SERVICE_URL}/{path}",
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
                url=f"{ServiceURL.HOTEL_SERVICE_URL}/{path}",
                headers=forward_headers,
                json=body,
                params=params
            )

    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )

@router.api_route(
    "/user/{path:path}",
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
                url=f"{ServiceURL.USER_SERVICE_URL}/{path}",
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
                url=f"{ServiceURL.USER_SERVICE_URL}/{path}",
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
                url=f"{ServiceURL.USER_SERVICE_URL}/{path}",
                headers=forward_headers,
                json=body,
                params=params
            )

    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )

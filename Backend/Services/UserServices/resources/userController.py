from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import bcrypt
import uuid
import os
import time
import uuid
import bcrypt
from collections import defaultdict, deque
from fastapi import Form, UploadFile, File
from resources.authorization import has_permission, require_permission, require_any_permission
from resources.utils import verify_authentication
from resources.validation import normalize_email, normalize_phone, validate_email
from models import models
from models import get_db
from configs.base_config import CommonWords
import logging

logger = logging.getLogger("userservice.controller")


# ---------------------------------------------------------------------------
# Rate limit for POST /verify_credentials
# ---------------------------------------------------------------------------
# This endpoint checks a password and is not authenticated -- by design, since
# the login gateway has no token yet when it calls. The gateway rate-limits
# /login_post, but that limiter is keyed on the peer address and sits in front
# of a different route: a caller who posts straight to /user/verify_credentials
# gets unlimited guesses at a bcrypt hash-adjacent oracle, and under
# RBAC_GATEWAY_MODE=audit (the default) the route is reachable.
#
# Keyed on the target account rather than the peer address, because behind the
# proxy every request arrives from the gateway's own address -- a per-peer
# limit here would be one shared bucket for the whole property.
_verify_hits = defaultdict(deque)
VERIFY_RATE_LIMIT_PER_MINUTE = int(os.getenv("VERIFY_RATE_LIMIT_PER_MINUTE", "10"))
_VERIFY_WINDOW_SECONDS = 60.0


def _rate_limit_verify(request: Request, email: str) -> None:
    peer = request.client.host if request.client else "unknown"
    key = f"{peer}|{email.lower()}"
    now = time.monotonic()
    hits = _verify_hits[key]
    while hits and (now - hits[0]) > _VERIFY_WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= VERIFY_RATE_LIMIT_PER_MINUTE:
        logger.warning(
            "verify_credentials_rate_limit_hit peer=%s email=%s", peer, email
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
        )
    hits.append(now)


def _clear_verify_hits(email: str, request: Request) -> None:
    """A successful check empties the account's window.

    Otherwise a user who mistyped twice and then got it right would still be
    counted against the limit on their next legitimate sign-in.
    """
    peer = request.client.host if request.client else "unknown"
    _verify_hits.pop(f"{peer}|{email.lower()}", None)


def _valid_shift_time(value) -> bool:
    """Require the canonical 24-hour HH:MM form used by the time inputs."""
    if not isinstance(value, str):
        return False
    try:
        from datetime import datetime
        parsed = datetime.strptime(value, "%H:%M")
    except (TypeError, ValueError):
        return False
    return parsed.strftime("%H:%M") == value


# Column widths of the `users` table, keyed by the name the API uses. A longer
# value reaching MySQL comes back as a driver "Data too long" error, which the
# generic handler turns into a 500 that says nothing about which field was
# wrong. Checked here so the answer is a 400 naming the field.
_STAFF_FIELD_LIMITS = {
    "username": 100,
    "first_name": 100,
    "last_name": 100,
    "dob": 20,
    "gender": 20,
    "marital_status": 50,
    "address": 255,
    "city": 100,
    "state": 100,
    "postal_code": 20,
    "country": 100,
    "experience": 50,
    "salary_details": 100,
    "register_code": 100,
    "emergency_name": 100,
    "emergency_relationship": 50,
}


def _staff_text(value, field: str, *, required: bool = False):
    """Trim one free-text staff field and enforce its column width.

    Returns the cleaned value (or None when absent and not required) so both
    the create and the update path can assign it directly.
    """
    if value is None:
        if required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field.replace('_', ' ').capitalize()} is required",
            )
        return None
    if not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field.replace('_', ' ').capitalize()} must be text",
        )
    cleaned = value.strip()
    if not cleaned:
        if required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field.replace('_', ' ').capitalize()} is required",
            )
        return None
    limit = _STAFF_FIELD_LIMITS.get(field)
    if limit and len(cleaned) > limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field.replace('_', ' ').capitalize()} must not exceed {limit} characters",
        )
    return cleaned


def _staff_text_in(payload: dict) -> dict:
    """Clean every free-text staff field the caller actually sent (update path).

    Absent keys stay absent so `payload.get(field, current)` keeps working for
    a partial update; a key present but empty is rejected the same way create
    rejects it.
    """
    cleaned = {}
    for field in _STAFF_FIELD_LIMITS:
        if field in payload:
            cleaned[field] = _staff_text(payload[field], field, required=True)
    return cleaned


def _text(payload: dict, key: str, default: str = "") -> str:
    """Read one free-text field out of a JSON body, tolerating `null`.

    `payload.get(key, default)` only falls back when the key is ABSENT. A body
    that carries `"description": null` -- which a form sends the moment a field
    is optional and untouched -- returns None, and `.strip()` on None raises
    AttributeError, which the generic handler turns into a 500 for what is
    ordinary input. JSON `null` means "no value", so it reads as the default.
    """
    value = payload.get(key, default)
    if value is None:
        value = default
    if isinstance(value, (dict, list)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{key.replace('_', ' ').capitalize()} must be text",
        )
    return str(value).strip()


# Pages that read the staff directory. The list is not this file's invention:
# it is ROUTE_PERMISSIONS[("user", "users", "GET")] in
# Services/LoginServices/resources/rbac_map.py, and the two have to stay equal
# or the gateway and the service would answer the same request differently --
# one denying a roster screen the other allows.
USER_DIRECTORY_PAGES = (
    "/bar_roster",
    "/bar_shift_planning",
    "/employee",
    "/restaurant_roster",
    "/restaurant_shift_planning",
    "/room_incident_log",
    "/task_assign",
)


def _may_read_salary(db: Session, role_id, company_id) -> bool:
    """Salary is shown on the Employee screen, so it is gated on that page.

    The directory itself is needed by the rosters and the pickers, but a name
    picker has no business carrying what someone is paid. `edit` counts as
    well as `view`: a role that may change a salary may read the one it is
    changing, and refusing it would leave the required field blank on submit.
    """
    return (
        has_permission(db, role_id, company_id, "/employee", "view") is True
        or has_permission(db, role_id, company_id, "/employee", "edit") is True
    )


def _assert_tenant_role(db: Session, company_id: str, role_id: int) -> None:
    """Refuse a role id this tenant does not own."""
    owned = (
        db.query(models.Roles.id)
        .filter(models.Roles.id == role_id, models.Roles.company_id == company_id)
        .first()
    )
    if not owned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role_id does not belong to this company",
        )


def _assert_tenant_menu(db: Session, company_id: str, menu_id: int) -> None:
    owned = (
        db.query(models.Menus.id)
        .filter(models.Menus.id == menu_id, models.Menus.company_id == company_id)
        .first()
    )
    if not owned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="menu_id does not belong to this company",
        )


def _assert_tenant_submenu(
    db: Session, company_id: str, submenu_id: int, menu_id: int
) -> None:
    """Submenu must belong to the tenant AND hang off the menu just checked.

    Checking only that the submenu exists would let a caller file a
    permission under menu A for a submenu of menu B, which is how the matrix
    ends up with rows nothing can render.
    """
    row = (
        db.query(models.Submenus.id, models.Submenus.menu_id)
        .filter(
            models.Submenus.id == submenu_id,
            models.Submenus.company_id == company_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="submenu_id does not belong to this company",
        )
    if str(row.menu_id) != str(menu_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="submenu_id does not belong to menu_id",
        )


# Staff photos: 5 MB and two formats, both checked against the bytes rather
# than the filename.
MAX_PHOTO_BYTES = int(os.getenv("MAX_PHOTO_BYTES", str(5 * 1024 * 1024)))
_ALLOWED_PHOTOS = {
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
}


async def _save_staff_photo(photo: UploadFile) -> str:
    """Store an uploaded photo under a name this service chose, or refuse it.

    What used to happen: the client's own extension was taken off
    `photo.filename` and appended to a generated name. A file called
    `x.svg` (or `.html`, or `.php`) with `Content-Type: image/png` passed the
    content-type check and was written with the dangerous extension, and the
    static mount then served it back to a browser as markup -- stored XSS off
    an avatar upload. The bytes were also never looked at, so anything could be
    stored as a "photo", and `photo.read()` loaded the whole body into memory
    before anyone counted it.

    So: the extension comes from the declared type, the declared type has to
    match a magic-number signature, and the body is read with a ceiling.
    """
    content_type = (photo.content_type or "").lower()
    if content_type not in _ALLOWED_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG images are allowed",
        )

    body = await photo.read(MAX_PHOTO_BYTES + 1)
    if len(body) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Photo must be {MAX_PHOTO_BYTES // (1024 * 1024)} MB or smaller",
        )
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded photo is empty",
        )

    ext, signature = _ALLOWED_PHOTOS[content_type]
    if not body.startswith(signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid JPG or PNG image",
        )

    filename = f"user_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as buffer:
        buffer.write(body)

    return f"/templates/static/users/{filename}"


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
    # ISO-3166-1 alpha-2 country the numbers above were typed in (e.g. "IN").
    # A national number with no country code is ambiguous, so it is refused
    # rather than guessed -- see resources/validation.py.
    phone_region: str = Form(None),

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


        # The Employee screen (page /employee) is what creates staff -- see
        # Employee.jsx and ROUTE_PERMISSIONS[("user","users","POST")] in
        # LoginServices/resources/rbac_map.py. Gating on /user instead meant a
        # role the SPA showed an "Add" button to could still be refused here,
        # and the two layers disagreed about who may create a staff record.
        require_permission(db, auth_role, company_id, "/employee", "create")
        # -------------------------------------------------
        # NORMALIZATION
        # -------------------------------------------------
        username = username.strip()
        # Emails are validated properly and stored lower-cased, so a lookup and
        # the uniqueness check agree with what was typed. The old rule was
        # `"@" not in x or "." not in x`, which accepts `@.`, `a@b.`, `a b@c.d`
        # and a 10KB string while rejecting nothing useful (C-086).
        if not validate_email(company_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter a valid company email address, for example name@example.com",
            )
        if not validate_email(personal_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter a valid personal email address, for example name@example.com",
            )
        company_email = normalize_email(company_email)
        personal_email = normalize_email(personal_email)

        # -------------------------------------------------
        # PHONE VALIDATION
        # -------------------------------------------------
        # Staff can be from anywhere, so the number is checked against its own
        # country's numbering plan and stored as E.164. `phone_region` is the ISO
        # country the staff member's number was typed in; it is form input, not a
        # column, and a national number without it is refused rather than guessed.
        mobile = normalize_phone(mobile, field="mobile", default_region=phone_region)
        alternative_mobile = normalize_phone(
            alternative_mobile, field="alternative_mobile", default_region=phone_region
        )
        # The emergency number is stored in the same 20-character column and read
        # by the same screens, so it gets the same rule. Left unvalidated it could
        # be any string at all, and anything past 20 characters failed at the
        # driver as "Data too long" -- a 500 for a form field.
        emergency_contact = normalize_phone(
            emergency_contact, field="emergency_contact", default_region=phone_region
        )
        if not emergency_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Emergency contact is required",
            )

        # -------------------------------------------------
        # FREE TEXT (trimmed, width-checked against its column)
        # -------------------------------------------------
        username = _staff_text(username, "username", required=True)
        first_name = _staff_text(first_name, "first_name", required=True)
        last_name = _staff_text(last_name, "last_name", required=True)
        dob = _staff_text(dob, "dob", required=True)
        gender = _staff_text(gender, "gender", required=True)
        marital_status = _staff_text(marital_status, "marital_status", required=True)
        address = _staff_text(address, "address", required=True)
        city = _staff_text(city, "city", required=True)
        state = _staff_text(state, "state", required=True)
        postal_code = _staff_text(postal_code, "postal_code", required=True)
        country = _staff_text(country, "country", required=True)
        experience = _staff_text(experience, "experience", required=True)
        salary_details = _staff_text(salary_details, "salary_details", required=True)
        register_code = _staff_text(register_code, "register_code", required=True)
        emergency_name = _staff_text(emergency_name, "emergency_name", required=True)
        emergency_relationship = _staff_text(
            emergency_relationship, "emergency_relationship", required=True
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
        # PASSWORD POLICY
        # -------------------------------------------------
        # The self-service change endpoint already enforced a minimum; an
        # administrator creating or resetting an account did not, so a staff
        # account could be given a one-character password while the same rule
        # refused it to the account's owner.
        if not isinstance(password, str) or len(password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The password must be at least {PASSWORD_MIN_LENGTH} characters",
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
        # Extension, type and size are decided here, not by the client --
        # see _save_staff_photo.
        photo_path = None
        if photo and photo.filename:
            photo_path = await _save_staff_photo(photo)

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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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

        # The staff directory is not a public list: it carries salary, home
        # address and emergency contacts. Authentication alone used to be
        # enough to read it, so any signed-in role could enumerate the whole
        # property's staff. The gate mirrors the gateway's route map.
        require_any_permission(
            db, auth_role, company_id, USER_DIRECTORY_PAGES, "view"
        )
        read_salary = _may_read_salary(db, auth_role, company_id)

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
                    # Only the Employee page's readers see pay; a roster's name
                    # picker gets the rest of the record but not this.
                    **({"salary_details": user.Salary_Details} if read_salary else {}),
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        # Same gate as the list: one user's full record is the directory's
        # payload, not something a caller is entitled to merely because they
        # know the id.
        require_any_permission(
            db, auth_role, company_id, USER_DIRECTORY_PAGES, "view"
        )
        read_salary = _may_read_salary(db, auth_role, company_id)

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
                # Omitted, not nulled: absent means the caller's role cannot
                # see pay, which is different from "this role is paid nothing".
                **({"salary_details": user.Salary_Details} if read_salary else {}),
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# =====================================================
# VERIFY CREDENTIALS (auth-only; server-side password check)
# =====================================================
#
# Preferred replacement for the legacy `GET /login_user/{email}` endpoint,
# which returned the bcrypt password hash across the service boundary.
# This variant accepts {email, password} and returns only the identity
# fields the auth gateway needs. Password never leaves this service.
@router.post("/verify_credentials", status_code=status.HTTP_200_OK)
def verify_credentials(payload: dict, request: Request, db: Session = Depends(get_db)):
    try:
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""

        if not email or "@" not in email or not password:
            # Unified 401 — never disclose which field was wrong.
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Throttled before the bcrypt work, not after: the comparison is the
        # expensive part and it is exactly what an attacker wants to run.
        _rate_limit_verify(request, email)

        user = (
            db.query(models.Users)
            .filter(
                func.lower(models.Users.Company_Email) == email,
                models.Users.status == CommonWords.STATUS,
            )
            .first()
        )

        ok = False
        if user and user.Password:
            try:
                ok = bcrypt.checkpw(password.encode("utf-8"), user.Password.encode("utf-8"))
            except (ValueError, TypeError):
                ok = False

        if not ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        _clear_verify_hits(email, request)

        role = (
            db.query(models.Roles)
            .filter(
                models.Roles.id == user.Role_ID,
                models.Roles.company_id == user.company_id,
            )
            .first()
        )

        return {
            "status": "success",
            "data": {
                "id": user.id,
                "user_code": user.User_Code,
                "username": user.username,
                "first_name": user.First_Name,
                "last_name": user.Last_Name,
                "company_email": user.Company_Email,
                "role_id": user.Role_ID,
                "role_name": role.role_name if role else None,
                "company_id": user.company_id,
                "status": user.status,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("unhandled_exception")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# =====================================================
# GET USER BY EMAIL — REMOVED
# =====================================================
# `GET /login_user/{usermail}` was unauthenticated and returned full PII
# (personal email, mobile, date of birth, gender, marital status and home
# address) for any email an anonymous caller supplied. It had no callers in
# this repository and was already documented as superseded by
# POST /verify_credentials, which returns only identity fields.


# =====================================================
# THE SIGNED-IN USER'S OWN RECORD
# =====================================================
# WHY THESE ARE SEPARATE FROM /users AND /users/{id}
#     Those two are HRM: they read and write ANY employee, and the gateway
#     rightly gates them behind the /user and /employee pages. But a Front Desk
#     clerk has no HRM permission and still has to be able to see their own
#     profile and change their own password -- gating self-service behind an
#     admin page would deny it to almost everyone who needs it.
#
#     These take no user id. The row is chosen from the JWT alone, so the
#     endpoint cannot be pointed at a colleague however the request is shaped,
#     and no page permission is required because there is nothing here to
#     escalate to. That is what lets them sit in the gateway's ALWAYS_ALLOW set
#     beside the menu reads.
# =====================================================
@router.get("/me", status_code=status.HTTP_200_OK)
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    """The caller's own employee record, resolved from the token."""
    try:
        auth_user_id, auth_role, company_id, token = verify_authentication(request)
        if not auth_user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        user = (
            db.query(models.Users)
            .filter(
                models.Users.id == auth_user_id,
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS,
            )
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Your user record could not be found",
            )

        # Resolved names, not bare ids: this is read by a profile screen, and
        # a screen that shows "Department 3" has told the reader nothing.
        department = (
            db.query(models.Department)
            .filter(models.Department.id == user.Department_ID)
            .first()
        )
        designation = (
            db.query(models.Designation)
            .filter(models.Designation.id == user.Designation_ID)
            .first()
        )
        role = db.query(models.Roles).filter(models.Roles.id == user.Role_ID).first()
        shift = db.query(models.Shift).filter(models.Shift.id == user.Shift_ID).first()

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
                "department_name": getattr(department, "Department_Name", None),
                "designation_id": user.Designation_ID,
                "designation_name": getattr(designation, "Designation_Name", None),
                "role_id": user.Role_ID,
                "role_name": getattr(role, "role_name", None),
                "shift_id": user.Shift_ID,
                "shift_name": getattr(shift, "Shift_Name", None),
                "shift_start": getattr(shift, "Start_Time", None),
                "shift_end": getattr(shift, "End_Time", None),
                "date_of_joining": user.Date_Of_Joining,
                "experience": user.Experience,
                "emergency_name": user.Emergency_Name,
                "emergency_contact": user.Emergency_Contact,
                "emergency_relationship": user.Emergency_Relationship,
                "created_at": user.created_at,
                # Salary is deliberately NOT here. It is on the HRM record for
                # the people who administer pay; a profile screen reachable by
                # everyone is not the place to publish it, and this endpoint
                # bypasses page permissions precisely so it must carry nothing
                # that page permissions were protecting.
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("get_my_profile_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# =====================================================
# THE CALLER'S OWN PHOTO
# =====================================================
# Employee photos live under a StaticFiles mount at
# /templates/static/users/<file>, and the gateway maps that path to the HRM
# Employee page -- correctly, because it can serve ANY colleague's photo and a
# staff directory is not something every role may read.
#
# The consequence was that the avatar on a user's own Profile page 403'd for
# every role except Admin: the screen is reachable by everyone, the photo
# behind it was not.
#
# This route resolves the file from the token instead of from the URL, so it
# can only ever answer with the caller's own photo. That is what lets it sit in
# the gateway's ALWAYS_ALLOW set beside /me and /me/password.
@router.get("/me/photo")
def get_my_photo(request: Request, db: Session = Depends(get_db)):
    """The caller's own profile photo, resolved from the token."""
    auth_user_id, auth_role, company_id, token = verify_authentication(request)
    if not auth_user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = (
        db.query(models.Users)
        .filter(
            models.Users.id == auth_user_id,
            models.Users.company_id == company_id,
        )
        .first()
    )
    if not user or not user.Photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No photo on file")

    # The stored value is a URL path ("/templates/static/users/<file>"). Only
    # its last segment is used, and the result is required to resolve inside
    # the upload directory: a stored value of "../../.env" must not be able to
    # turn this into a file read.
    filename = os.path.basename(str(user.Photo).replace("\\", "/"))
    root = os.path.realpath(UPLOAD_DIR)
    target = os.path.realpath(os.path.join(root, filename))
    if os.path.commonpath([root, target]) != root or not os.path.isfile(target):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No photo on file")

    return FileResponse(target)


# Long enough to resist a guess, short enough that people will not write it on
# a note by the terminal. Matched by the same rule in the UI so the two cannot
# disagree about what is acceptable.
PASSWORD_MIN_LENGTH = 8


@router.put("/me/password", status_code=status.HTTP_200_OK)
def change_my_password(payload: dict, request: Request, db: Session = Depends(get_db)):
    """Change the caller's own password.

    The current password is required even though the caller is already
    authenticated: a token can be an unattended terminal someone walked up to,
    and re-entering the password is what distinguishes the account's owner from
    whoever is standing at their screen.
    """
    try:
        auth_user_id, auth_role, company_id, token = verify_authentication(request)
        if not auth_user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        current_password = (payload or {}).get("current_password") or ""
        new_password = (payload or {}).get("new_password") or ""

        if not current_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both the current and the new password are required",
            )

        if len(new_password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The new password must be at least {PASSWORD_MIN_LENGTH} characters",
            )

        if new_password == current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The new password must be different from the current one",
            )

        user = (
            db.query(models.Users)
            .filter(
                models.Users.id == auth_user_id,
                models.Users.company_id == company_id,
                models.Users.status == CommonWords.STATUS,
            )
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Your user record could not be found",
            )

        ok = False
        if user.Password:
            try:
                ok = bcrypt.checkpw(
                    current_password.encode("utf-8"), user.Password.encode("utf-8")
                )
            except (ValueError, TypeError):
                ok = False

        if not ok:
            # 403 rather than 401: the token is fine, the re-authentication is
            # what failed. A 401 would make the SPA log the user out.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The current password is not correct",
            )

        user.Password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user.updated_by = str(auth_user_id)
        db.commit()

        logger.info("password_changed user=%s", auth_user_id)
        return {"status": "success", "message": "Your password has been changed"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("change_my_password_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
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


        require_permission(db, auth_role, company_id, "/user", "edit")
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
        # FIELD VALIDATION (C-086)
        # -------------------------------------------------
        # The update path wrote whatever arrived: an email that was two characters
        # long, a mobile of "abc". It now runs the same rules as create, and
        # normalises the values it accepts.
        phone_region = payload.get("phone_region")
        if payload.get("company_email") is not None:
            if not validate_email(payload["company_email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Enter a valid company email address, for example name@example.com",
                )
        if payload.get("personal_email") is not None:
            if not validate_email(payload["personal_email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Enter a valid personal email address, for example name@example.com",
                )
        if "mobile" in payload:
            payload["mobile"] = normalize_phone(
                payload["mobile"], field="mobile", default_region=phone_region
            )
        if "alternative_mobile" in payload:
            payload["alternative_mobile"] = normalize_phone(
                payload["alternative_mobile"], field="alternative_mobile",
                default_region=phone_region,
            )
        if "emergency_contact" in payload:
            payload["emergency_contact"] = normalize_phone(
                payload["emergency_contact"], field="emergency_contact",
                default_region=phone_region,
            )
            if not payload["emergency_contact"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Emergency contact is required",
                )

        # Free-text fields: trimmed and width-checked before they reach the
        # column, so an over-long value is a 400 naming the field rather than
        # a driver-level "Data too long" 500.
        cleaned_text = _staff_text_in(payload)
        payload.update(cleaned_text)

        # -------------------------------------------------
        # UPDATE FIELDS (SAFE)
        # -------------------------------------------------
        user.username = payload.get("username", user.username)
        user.First_Name = payload.get("first_name", user.First_Name)
        user.Last_Name = payload.get("last_name", user.Last_Name)
        user.Personal_Email = (
            normalize_email(payload["personal_email"])
            if payload.get("personal_email") is not None
            else user.Personal_Email
        )
        user.Company_Email = (
            normalize_email(payload["company_email"])
            if payload.get("company_email") is not None
            else user.Company_Email
        )

        new_password = payload.get("password")
        if new_password and new_password.strip() != "":
            if len(new_password) < PASSWORD_MIN_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The password must be at least {PASSWORD_MIN_LENGTH} characters",
                )
            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            user.Password = hashed_password


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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, auth_role, company_id, "/user", "delete")
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role_id, company_id, "/roles", "create")
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

        role_name = _text(payload, "role_name")
        description = _text(payload, "description")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not role_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="role_name is required"
            )

        # `description` is nullable in the model and optional in the form: an
        # untouched optional field arrives as null (or not at all), and
        # refusing it turned "create a role without a note" into a 400.
        # The width check still applies to whatever was typed.
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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists",
            )
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role_id, company_id, "/roles", "edit")
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
        role_name = _text(payload, "role_name")
        description = _text(payload, "description")

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

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists",
            )
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role, company_id, "/roles", "delete")
        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if role_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )

        # Do not allow an administrator to remove the role they are currently
        # using; that can lock the tenant out of role administration. A
        # separate administrator must perform the destructive change.
        if str(role_id) == str(role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own role",
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        # The permission matrix is drawn and saved on the /user screen (see
        # User.jsx and ROUTE_PERMISSIONS[("user","role_permissions","POST")]),
        # so it is /user's create bit that gates it -- /roles owns the role
        # records themselves. `role_id` here is the CALLER's role from the
        # token; the target role arrives in the body as `role_id_payload`.
        require_permission(db, role_id, company_id, "/user", "create")

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
        # TENANT OWNERSHIP (C-089)
        # -------------------------------------------------
        # Every id in this body belongs to this company or it is refused. The
        # row was written with the caller's company_id anyway, so a foreign id
        # did not grant the other tenant anything -- but it did create a
        # permission row pointing at a role/menu this tenant cannot see, which
        # shows up as an unresolvable row in the matrix and in
        # `verify_seed.py`'s dangling-reference check. Checked here so it is a
        # 400 naming the field rather than silent corruption.
        _assert_tenant_role(db, company_id, role_id_payload)
        _assert_tenant_menu(db, company_id, menu_id)
        if submenu_id is not None:
            _assert_tenant_submenu(db, company_id, submenu_id, menu_id)

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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
                menu["children"].sort(key=lambda x: x.get("order_no") or 0)

            menus_list.sort(key=lambda x: x.get("order_no") or 0)

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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# =====================================================
# GET ROLE PERMISSIONS BY ROLE
# =====================================================
@router.get("/role_permissions/{role_id}", status_code=status.HTTP_200_OK)
def get_permissions_by_role(
    request: Request,
    role_id: int,
    include_empty: bool = False,
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
            # The login/navigation contract omits empty rows. The permission
            # matrix asks for include_empty so an operator can re-enable a row
            # after deliberately turning every flag off, and so PUT can address
            # the existing permission id instead of attempting a duplicate POST.
            if not include_empty and not any([
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
                    "permission_id": permission.id,
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
                        "permission_id": permission.id,
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
            menu["children"].sort(key=lambda x: x.get("order_no") or 0)

        sorted_menus = sorted(menus.values(), key=lambda x: x.get("order_no") or 0)

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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        # The permission matrix is drawn and saved on the /user screen; matches
        # ROUTE_PERMISSIONS[("user","role_permissions","PUT")]. /roles owns the
        # role records, not the matrix.
        require_permission(db, user_role, company_id, "/user", "edit")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "delete")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "create")
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

        menu_name = _text(payload, "menu_name")
        menu_link = _text(payload, "menu_link")
        menu_icon = _text(payload, "menu_icon")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "edit")
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
        menu_name = _text(payload, "menu_name")
        menu_link = _text(payload, "menu_link")
        menu_icon = _text(payload, "menu_icon")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "delete")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "create")
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
        submenu_name = _text(payload, "submenu_name")
        submenu_link = _text(payload, "submenu_link")
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
        logger.exception("unhandled_exception")
        # ❌ Catch DB integrity or unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/submenus/by-menu/{menu_id}", status_code=status.HTTP_200_OK)
def get_submenus_by_menu(
    menu_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    # `company_id` used to arrive as a caller-supplied query parameter on an
    # unauthenticated route, so anyone could read any tenant's menu structure
    # by guessing an id. It is now taken from the verified token only.
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "edit")
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
        submenu_name = _text(payload, "submenu_name")
        submenu_link = _text(payload, "submenu_link")
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/roles", "delete")
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only q
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role_id, company_id, "/department", "create")
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

        department_name = _text(payload, "department_name")

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
        try:
            db.commit()
        except IntegrityError:
            # A concurrent request can win the read-before-insert race even
            # after the application-level duplicate check.  The active-name
            # index is the final authority; expose the same client error rather
            # than leaking a 500 from MySQL.
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department already exists",
            )
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
        logger.exception("unhandled_exception")
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role_id, company_id, "/department", "edit")
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
        department_name = _text(payload, "department_name")

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

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists",
            )
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
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


        require_permission(db, role_id, company_id, "/department", "delete")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role_id, company_id, "/designation", "create")
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

        designation_name = _text(payload, "designation_name")

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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Designation already exists",
            )
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
        logger.exception("unhandled_exception")
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, role_id, company_id, "/designation", "edit")
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
        designation_name = _text(payload, "designation_name")

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

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Designation name already exists",
            )
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
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


        require_permission(db, role_id, company_id, "/designation", "delete")
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
        logger.exception("unhandled_exception")
        # ❌ Unexpected errors only
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/shift", "create")
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

        shift_name = _text(payload, "shift_name")
        start_time = _text(payload, "start_time")
        end_time = _text(payload, "end_time")

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

        if not _valid_shift_time(start_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be a valid HH:MM time"
            )
        if not _valid_shift_time(end_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_time must be a valid HH:MM time"
            )
        if start_time == end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time and end_time cannot be identical"
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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shift already exists",
            )
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/shift", "edit")
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
        shift_name = _text(payload, "shift_name")
        start_time = _text(payload, "start_time")
        end_time = _text(payload, "end_time")

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

        if not _valid_shift_time(start_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be a valid HH:MM time"
            )
        if not _valid_shift_time(end_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_time must be a valid HH:MM time"
            )
        if start_time == end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time and end_time cannot be identical"
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

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shift already exists",
            )
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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


        require_permission(db, user_role, company_id, "/shift", "delete")
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
        logger.exception("unhandled_exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

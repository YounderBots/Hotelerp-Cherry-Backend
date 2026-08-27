# =============================== Inquiry APIs ==============================
#
# A guest inquiry is the front-office record of someone asking about the hotel
# before they are a guest: who asked, how the request arrived, what was told to
# them, what follow-up is owed, and whether the conversation is still open.
#
# VOCABULARY
# `inquiry_mode` and `inquiry_status` are closed sets, documented on the model
# and matched by every row in the database. They were previously accepted as
# free text, so the SPA could -- and did -- write values ("Phone", "Open",
# "Resolved") that no other part of the system recognises. Both are validated
# here, which is the only place that can hold the line: the columns are plain
# VARCHARs with no CHECK constraint behind them.
#
# NULL HANDLING
# Every optional field used to be read as `payload.get(key, "").strip()`. A
# JSON `null` -- exactly what the SPA sends for an untouched optional field --
# returns None from `.get()`, and `None.strip()` raised, so the request died
# with a 500 carrying the raw Python message. Reading goes through
# `_optional_text` now, which treats null, missing and blank identically.

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from resources.utils import verify_authentication
from models import get_db, models
from configs.base_config import CommonWords

router = APIRouter()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical vocabulary. Keep in step with models.Inquiry and with the frontend
# constants in Frontend/src/Hotel/Guest Enquiry/GuestEnquiry.jsx.
# ---------------------------------------------------------------------------
INQUIRY_MODES = ("Online", "Offline")
INQUIRY_STATUSES = ("In Progress", "Completed")

# Column widths from models.Inquiry, enforced before the write so an oversized
# value returns a readable 400 instead of a driver-level truncation error.
MAX_GUEST_NAME = 255
MAX_NOTE = 255

INTERNAL_ERROR = "Could not complete the request. Please try again."


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


async def _json_body(request: Request) -> dict:
    try:
        payload = await request.json()
    except Exception:
        raise _bad_request("Invalid JSON body")
    if not isinstance(payload, dict):
        raise _bad_request("Request body must be a JSON object")
    return payload


def _required_text(payload: dict, key: str, label: str, limit: int) -> str:
    raw = payload.get(key)
    value = raw.strip() if isinstance(raw, str) else ""
    if not value:
        raise _bad_request(f"{label} is required")
    if len(value) > limit:
        raise _bad_request(f"{label} must be {limit} characters or fewer")
    return value


def _optional_text(payload: dict, key: str, label: str, limit: int):
    """None for missing / null / blank; a trimmed string otherwise."""
    raw = payload.get(key)
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise _bad_request(f"{label} must be text")
    value = raw.strip()
    if not value:
        return None
    if len(value) > limit:
        raise _bad_request(f"{label} must be {limit} characters or fewer")
    return value


def _one_of(value: str, allowed: tuple, label: str) -> str:
    """Validates against a closed set and returns the canonical spelling.

    Matched case-insensitively so a client sending "online" stores "Online"
    rather than adding a second spelling of the same value to the column.
    """
    match = next((a for a in allowed if a.lower() == value.lower()), None)
    if match is None:
        raise _bad_request(f"{label} must be one of: {', '.join(allowed)}")
    return match


def _authenticate(request: Request):
    user_id, _role_id, company_id, _token = verify_authentication(request)
    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return user_id, company_id


def _serialize(inquiry) -> dict:
    return {
        "id": inquiry.id,
        "inquiry_mode": inquiry.inquiry_mode,
        "guest_name": inquiry.guest_name,
        "response": inquiry.response,
        "follow_up": inquiry.follow_up,
        "incidents": inquiry.incidents,
        "inquiry_status": inquiry.inquiry_status,
        "created_by": inquiry.created_by,
        "created_at": inquiry.created_at,
        "updated_at": inquiry.updated_at,
        "updated_by": inquiry.updated_by,
        "company_id": inquiry.company_id,
    }


def _get_owned(db: Session, inquiry_id: int, company_id):
    """The one active inquiry with this id belonging to the caller's company."""
    inquiry = (
        db.query(models.Inquiry)
        .filter(
            models.Inquiry.id == inquiry_id,
            models.Inquiry.company_id == company_id,
            models.Inquiry.status == CommonWords.STATUS,
        )
        .first()
    )
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )
    return inquiry


def _server_error(operation: str, exc: Exception) -> HTTPException:
    """Logs the cause and returns a message that is safe to show a user.

    `detail=str(e)` used to be returned verbatim, which put Python exception
    text -- table names, driver errors -- on the front-office screen.
    """
    logger.exception("inquiry_%s_failed", operation, exc_info=exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=INTERNAL_ERROR,
    )


# =====================================================
# GET ALL INQUIRIES
# =====================================================
@router.get("/inquiry", status_code=status.HTTP_200_OK)
def get_inquiries(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        _user_id, company_id = _authenticate(request)

        inquiries = (
            db.query(models.Inquiry)
            .filter(
                models.Inquiry.company_id == company_id,
                models.Inquiry.status == CommonWords.STATUS,
            )
            .order_by(models.Inquiry.id.desc())
            .all()
        )

        data = [_serialize(inquiry) for inquiry in inquiries]

        return {
            "status": "success",
            "count": len(data),
            "data": data,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise _server_error("list", exc)


# =====================================================
# CREATE GUEST INQUIRY
# =====================================================
@router.post("/inquiry", status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, company_id = _authenticate(request)
        payload = await _json_body(request)

        inquiry_mode = _one_of(
            _required_text(payload, "inquiry_mode", "Inquiry mode", 50),
            INQUIRY_MODES,
            "Inquiry mode",
        )
        guest_name = _required_text(payload, "guest_name", "Guest name", MAX_GUEST_NAME)
        inquiry_status = _one_of(
            _required_text(payload, "inquiry_status", "Inquiry status", 50),
            INQUIRY_STATUSES,
            "Inquiry status",
        )

        response = _optional_text(payload, "response", "Response", MAX_NOTE)
        follow_up = _optional_text(payload, "follow_up", "Follow-up", MAX_NOTE)
        incidents = _optional_text(payload, "incidents", "Incident notes", MAX_NOTE)

        inquiry = models.Inquiry(
            inquiry_mode=inquiry_mode,
            guest_name=guest_name,
            response=response,
            follow_up=follow_up,
            incidents=incidents,
            inquiry_status=inquiry_status,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id,
        )

        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)

        return {
            "status": "success",
            "message": "Guest inquiry created successfully",
            "data": _serialize(inquiry),
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()
        raise _server_error("create", exc)


# =====================================================
# GET INQUIRY BY ID
# =====================================================
@router.get("/inquiry/{inquiry_id}", status_code=status.HTTP_200_OK)
def get_inquiry_by_id(
    request: Request,
    inquiry_id: int,
    db: Session = Depends(get_db)
):
    try:
        _user_id, company_id = _authenticate(request)

        if inquiry_id <= 0:
            raise _bad_request("Invalid inquiry_id")

        inquiry = _get_owned(db, inquiry_id, company_id)

        return {
            "status": "success",
            "data": _serialize(inquiry),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise _server_error("read", exc)


# =====================================================
# UPDATE INQUIRY
# =====================================================
@router.put("/inquiry", status_code=status.HTTP_200_OK)
async def update_inquiry(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id, company_id = _authenticate(request)
        payload = await _json_body(request)

        # `True` is an int in Python, so a plain isinstance(x, int) check passes
        # for a body of {"id": true} and it would reach the query as id 1.
        inquiry_id = payload.get("id")
        if isinstance(inquiry_id, str) and inquiry_id.strip().isdigit():
            inquiry_id = int(inquiry_id)
        if (
            isinstance(inquiry_id, bool)
            or not isinstance(inquiry_id, int)
            or inquiry_id <= 0
        ):
            raise _bad_request("Valid inquiry id is required")

        inquiry_mode = _one_of(
            _required_text(payload, "inquiry_mode", "Inquiry mode", 50),
            INQUIRY_MODES,
            "Inquiry mode",
        )
        guest_name = _required_text(payload, "guest_name", "Guest name", MAX_GUEST_NAME)
        inquiry_status = _one_of(
            _required_text(payload, "inquiry_status", "Inquiry status", 50),
            INQUIRY_STATUSES,
            "Inquiry status",
        )

        response = _optional_text(payload, "response", "Response", MAX_NOTE)
        follow_up = _optional_text(payload, "follow_up", "Follow-up", MAX_NOTE)
        incidents = _optional_text(payload, "incidents", "Incident notes", MAX_NOTE)

        inquiry = _get_owned(db, inquiry_id, company_id)

        inquiry.inquiry_mode = inquiry_mode
        inquiry.guest_name = guest_name
        inquiry.response = response
        inquiry.follow_up = follow_up
        inquiry.incidents = incidents
        inquiry.inquiry_status = inquiry_status
        inquiry.updated_by = user_id

        db.commit()
        db.refresh(inquiry)

        return {
            "status": "success",
            "message": "Inquiry updated successfully",
            "data": _serialize(inquiry),
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()
        raise _server_error("update", exc)


# =====================================================
# DELETE INQUIRY (SOFT DELETE)
# =====================================================
@router.delete("/inquiry/{inquiry_id}", status_code=status.HTTP_200_OK)
def delete_inquiry(
    request: Request,
    inquiry_id: int,
    db: Session = Depends(get_db)
):
    try:
        user_id, company_id = _authenticate(request)

        if inquiry_id <= 0:
            raise _bad_request("Invalid inquiry_id")

        inquiry = _get_owned(db, inquiry_id, company_id)

        # Soft delete: the row stays for reporting, and every read above
        # filters it out through the CommonWords.STATUS predicate.
        inquiry.status = CommonWords.UNSTATUS
        inquiry.updated_by = user_id

        db.commit()

        return {
            "status": "success",
            "message": "Inquiry deleted successfully",
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()
        raise _server_error("delete", exc)

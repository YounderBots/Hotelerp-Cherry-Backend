"""What another service needs from Master Data, in one call -- and the one thing
another service is allowed to write back.

WHY THIS EXISTS
    HotelServices used to read this schema directly over SQL: `room`,
    `room_type`, `tax_type`, `discount_data`, `payment_methods`,
    `identity_proof` and `reservation_status`, mapped as read-only tables on
    its own connection, plus UPDATEs to three columns of `room`. That made the
    Hotel service's MySQL account need privileges in a schema it does not own,
    which nothing provisioned, and the deployment at 168.231.103.18 answered
    500 on every reservation screen for three days over one missing GRANT.

    The rest of the system already crosses service boundaries over HTTP
    (Restaurant and Bar to Users and Master Data; the night audit to `/room`
    here). This module is the Hotel service's half of the same arrangement,
    shaped for how it reads: everything it needs to interpret or price a
    reservation, at once, so a booking costs one round trip and not seven.

THE SNAPSHOT (`GET /snapshot`)
    Every row of the seven tables for the caller's company, ACTIVE or not, each
    carrying its `status`. Inactive rows are included on purpose: a
    reservation booked last year against a payment method that has since been
    retired still has to display that method's name, which the public list
    endpoints -- active only -- cannot supply. The reader decides what
    "selectable" means; this endpoint decides nothing.

    Field names are the same public names the individual endpoints already
    use (`room_no`, `daily_rate`, `tax_percentage`, ...), so a consumer speaks
    one vocabulary to this service and never this schema's column names.

THE STATE WRITE (`PUT /room/{room_id}/state`)
    The three columns of `room` that are statements about operations rather
    than about the room -- occupancy, housekeeping readiness, and whether the
    room is blocked -- and nothing else. The Hotel service keeps them in step
    with reservations and housekeeping tasks; `PUT /room` is the room's OWN
    editor, takes the whole record as a multipart form, and does not touch
    two of these three. Each field is optional and only the fields sent are
    written, so a caller that knows one fact does not have to assert the
    others.

    PUT rather than PATCH, although the semantics are partial: every call
    between services goes through the login gateway, which proxies and
    authorises exactly GET, POST, PUT and DELETE -- the four verbs the whole
    system speaks -- and a fifth verb would have to be threaded through the
    proxy, the permission map and its generator for one route.

WHO MAY CALL THESE
    Both are reached through the gateway on the caller's own token, so the
    gateway's permission map decides: `snapshot` for any page of the Hotel
    module, the state write for any page whose actions cause it (a booking, a
    check-out, a housekeeping task). See Backend/tools/build_rbac_map.py,
    SERVICE_ROWS.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from configs.base_config import CommonWords
from models import get_db, models
from resources.utils import verify_authentication

logger = logging.getLogger("masterdataservice.snapshot")

router = APIRouter()


def _company(request: Request):
    user_id, _role_id, company_id, _token = verify_authentication(request)
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return user_id, company_id


def _all(db: Session, model, company_id):
    return (
        db.query(model)
        .filter(model.company_id == str(company_id))
        .order_by(model.id.asc())
        .all()
    )


# One place per table that says which columns leave this service and under
# what name. The public list endpoints spell these the same way.
def _room(r: models.Room) -> dict:
    return {
        "id": r.id,
        "room_no": r.Room_No,
        "room_name": r.Room_Name,
        "room_type_id": r.Room_Type_ID,
        "bed_type_id": r.Bed_Type_ID,
        "max_adult": r.Max_Adult_Occupy,
        "max_child": r.Max_Child_Occupy,
        "booking_status": r.Room_Booking_status,
        "working_status": r.Room_Working_status,
        "room_status": r.Room_Status,
        "status": r.status,
    }


def _room_type(t: models.Room_Type) -> dict:
    return {
        "id": t.id,
        "room_type_name": t.Type_Name,
        "room_cost": t.Room_Cost,
        "bed_cost": t.Bed_Cost,
        "daily_rate": t.Daily_Rate,
        "weekly_rate": t.Weekly_Rate,
        "bed_only_rate": t.Bed_Only_Rate,
        "bed_breakfast_rate": t.Bed_And_Breakfast_Rate,
        "half_board_rate": t.Half_Board_Rate,
        "full_board_rate": t.Full_Board_Rate,
        "status": t.status,
    }


def _tax(t: models.Tax_type) -> dict:
    return {"id": t.id, "tax_name": t.Tax_Name,
            "tax_percentage": t.Tax_Percentage, "status": t.status}


def _discount(d: models.Discount_Data) -> dict:
    return {"id": d.id, "discount_name": d.Discount_Name,
            "discount_percentage": d.Discount_Percentage, "status": d.status}


def _payment_method(p: models.Payment_Methods) -> dict:
    return {"id": p.id, "payment_method": p.payment_method, "status": p.status}


def _identity_proof(i: models.Identity_Proofs) -> dict:
    return {"id": i.id, "proof_name": i.Proof_Name, "status": i.status}


def _reservation_status(s: models.Reservation_Status) -> dict:
    return {"id": s.id, "reservation_status": s.Reservation_Status,
            "color": s.Color, "status": s.status}


@router.get("/snapshot", status_code=status.HTTP_200_OK)
def snapshot(request: Request, db: Session = Depends(get_db)):
    """Everything a sibling service needs to interpret a reservation."""
    try:
        _user_id, company_id = _company(request)
        return {
            "status": "success",
            "data": {
                "rooms": [_room(r) for r in _all(db, models.Room, company_id)],
                "room_types": [_room_type(t) for t in _all(db, models.Room_Type, company_id)],
                "tax_types": [_tax(t) for t in _all(db, models.Tax_type, company_id)],
                "discounts": [_discount(d) for d in _all(db, models.Discount_Data, company_id)],
                "payment_methods": [
                    _payment_method(p) for p in _all(db, models.Payment_Methods, company_id)
                ],
                "identity_proofs": [
                    _identity_proof(i) for i in _all(db, models.Identity_Proofs, company_id)
                ],
                "reservation_statuses": [
                    _reservation_status(s)
                    for s in _all(db, models.Reservation_Status, company_id)
                ],
            },
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("snapshot_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


class RoomState(BaseModel):
    """The operational facts about a room. Send only what you know."""

    booking_status: Optional[str] = Field(None, max_length=100)
    working_status: Optional[str] = Field(None, max_length=100)
    room_status: Optional[str] = Field(None, max_length=100)


@router.put("/room/{room_id}/state", status_code=status.HTTP_200_OK)
def set_room_state(
    room_id: int,
    body: RoomState,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        user_id, company_id = _company(request)

        changes = {k: v.strip() for k, v in body.model_dump().items() if v is not None}
        if not changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Send at least one of booking_status, working_status, room_status",
            )
        if any(not v for v in changes.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A room state cannot be blank",
            )

        room = (
            db.query(models.Room)
            .filter(
                models.Room.id == room_id,
                models.Room.company_id == str(company_id),
                models.Room.status == CommonWords.STATUS,
            )
            .first()
        )
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Room not found")

        if "booking_status" in changes:
            room.Room_Booking_status = changes["booking_status"]
        if "working_status" in changes:
            room.Room_Working_status = changes["working_status"]
        if "room_status" in changes:
            room.Room_Status = changes["room_status"]
        room.updated_by = str(user_id)
        db.commit()
        db.refresh(room)

        return {"status": "success", "data": _room(room)}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("set_room_state_failed room_id=%s", room_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

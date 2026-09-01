import io
import pandas as pd
from fastapi import APIRouter, Depends, Request, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from jose import JWTError
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import date, timedelta
import datetime as dt

import logging
import os

import httpx

from models import get_db, models
from configs.base_config import BaseConfig, CommonWords
from fastapi import HTTPException
from resources.utils import can_view_any, verify_authentication
from resources import nightAuditService as nas
from resources.nightAuditService import AuditConflict

logger = logging.getLogger("hotelservice.nightaudit")

# The room master lives in MasterDataServices, so the room INVENTORY count is
# not a fact this service owns. It is read over loopback, best-effort, purely
# to turn "8 rooms occupied" into "8 of 25 (32%)" on the audit record. Every
# call site treats a failure as "unknown" and carries on -- see
# `_fetch_rooms_total`.
MASTER_SERVICE_URL = os.getenv("MASTER_SERVICE_URL", "http://127.0.0.1:8030")

router = APIRouter()

#=====================================>>> User Activity Log

@router.get("/user_activity_log", status_code=status.HTTP_200_OK)
def user_activity_log(request: Request,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    # -------------------------------
    # Date validation (EXACT logic)
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Room Reservation Activity
    # -------------------------------
    room_data = (
        db.query(models.RoomReservation)
        .filter(
            models.RoomReservation.company_id == company_id,
            models.RoomReservation.arrival_date.between(from_date, to_date)
        )
        .all()
    )

    # WHO GETS THE GUEST'S PHONE NUMBER AND EMAIL
    #
    # This endpoint serves two screens with different needs. /user_reserved_details
    # is a guest contact list and shows both. /dashboard shows a name, a status
    # and a date -- it renders neither -- yet both fields crossed the wire to it
    # anyway, so anyone who could open the Dashboard could read every guest's
    # contact details straight out of the response.
    #
    # Contact details are therefore included only for a caller who can already
    # view a screen that shows them. This grants nobody anything new: both pages
    # named here display guest contact details in full. It only stops the
    # Dashboard being an undeclared contact export.
    #
    # Decided from the signed `perm` claim rather than a request parameter --
    # a caller-supplied flag would be no boundary at all.
    include_contact = can_view_any(token, "/user_reserved_details", "/reservation")

    formatted_room_data = []
    for r in room_data:
        entry = {
            "id": r.id,
            "room_no": ", ".join(str(n) for n in r.room_no) if isinstance(r.room_no, list) else r.room_no,
            "reservation_id": r.room_reservation_id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "arrival_date": r.arrival_date,
            "departure_date": r.departure_date,
            "booking_status": r.reservation_status,
        }
        if include_contact:
            entry["phone"] = r.phone_number
            entry["email"] = r.email
        formatted_room_data.append(entry)

    # -------------------------------
    # Housekeeping / Staff Activity
    # (HousekeeperTask already carries staff name + task type inline —
    # Employee_Data/Task_Type are separate microservices, not joinable here)
    # -------------------------------
    keeper_data = (
        db.query(models.HousekeeperTask)
        .filter(
            models.HousekeeperTask.company_id == company_id,
            models.HousekeeperTask.schedule_date.between(from_date, to_date)
        )
        .all()
    )

    formatted_keeper_data = [
        {
            "id": k.id,
            "employee_id": k.employee_id,
            "employee_name": f"{k.first_name} {k.last_name}",
            "room_no": k.room_no,
            "task_type": k.task_type,
            "task_status": k.task_status
        }
        for k in keeper_data
    ]

    # -------------------------------
    # Final Response
    # -------------------------------
    return {
        "status": "success",
        "filters": {
            "from_date": from_date,
            "to_date": to_date
        },
        "data": {
            "room_activity": formatted_room_data,
            "housekeeping_activity": formatted_keeper_data
        }
    }

#=====================================>>> Reservation Info

@router.get("/reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def get_reservation_info(request: Request,
    reservation_id: int,
    db: Session = Depends(get_db)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    reservation = db.query(models.RoomReservation).filter(
        models.RoomReservation.id == reservation_id,
        models.RoomReservation.company_id == company_id
    ).first()

    if not reservation:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Reservation not found"
            },
            status_code=404
        )

    return {
        "status": "success",
        "data": jsonable_encoder(reservation)
    }

#=====================================>>> Keeper Info

@router.get("/keeper_info/{task_id}", status_code=status.HTTP_200_OK)
def keeper_info(request: Request,
    task_id: int,
    db: Session = Depends(get_db)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    keeper = (
        db.query(models.HousekeeperTask)
        .filter(
            models.HousekeeperTask.id == task_id,
            models.HousekeeperTask.company_id == company_id
        )
        .first()
    )

    if not keeper:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Keeper info not found"
            },
            status_code=404
        )

    formatted_keeper_info = {
        "id": keeper.id,
        "employee_id": keeper.employee_id,
        "employee_name": f"{keeper.first_name} {keeper.last_name}",
        "room_no": keeper.room_no,
        "task_type": keeper.task_type,
        "task_status": keeper.task_status,
        "schedule_date": keeper.schedule_date,
        "schedule_time": keeper.schedule_time,
        "room_status": keeper.room_status,
        "special_instructions": keeper.special_instructions,
        "status": keeper.status
    }

    return {
        "status": "success",
        "data": formatted_keeper_info
    }

# REMOVED: /paid_amount and /settlement_summary
#
# Two endpoints that summed today's paid and outstanding amounts. Both were
# superseded by /night_audit/preview, which answers the same question for a
# whole night and is what the Settlement Summary screen actually calls. Neither
# had a caller left anywhere in the app -- both sat in rbac_map's
# UNCALLED_ENDPOINTS, so `enforce` already denied them.
#
# They are deleted rather than repaired, because both carried the same money
# defect and repairing a dead duplicate only preserves the chance of the two
# answers diverging later:
#
#   * neither filtered `status == ACTIVE`, so a soft-deleted reservation still
#     contributed its paid and balance amounts -- revenue attributed to a
#     booking that no longer exists;
#   * both keyed off `date.today()` while the rest of this module keys off the
#     hotel business date, so between midnight and the audit they reported a
#     different day than the preview sitting beside them.
#
# /night_audit/preview has neither defect: it reads through
# nightAuditService.active_reservations and takes the business date.

#=====================================>>> Room Sales (REACT API)

@router.get("/room_sales", status_code=status.HTTP_200_OK)
def room_sales(request: Request,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    # -------------------------------
    # Date validation (same logic)
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Room sales data
    # -------------------------------
    room_data = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        models.RoomReservation.status == CommonWords.STATUS,
        models.RoomReservation.arrival_date.between(from_date, to_date)
    ).order_by(
        models.RoomReservation.arrival_date
    ).all()

    return {
        "status": "success",
        "filters": {
            "from_date": from_date,
            "to_date": to_date
        },
        "data": jsonable_encoder(room_data)
    }

#-------------- Night Auditing Export -------------------------------
#-------------- User Activity Log  ------------------------

@router.get("/export_user_activity", status_code=status.HTTP_200_OK)
def export_user_activity(request: Request,
    db: Session = Depends(get_db),
    format: str = Query("excel", enum=["excel", "json"]),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    # -------------------------------
    # Date validation (exact logic)
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Fetch reservation data
    # -------------------------------
    reservations = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == company_id,
        (
            models.RoomReservation.arrival_date.between(from_date, to_date)
        ) | (
            models.RoomReservation.departure_date.between(from_date, to_date)
        )
    ).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for reservation in reservations:
        full_name = f"{reservation.first_name} {reservation.last_name}"
        data.append({
            "Reservation ID": reservation.room_reservation_id,
            "Guest Name": full_name,
            "Phone Number": reservation.phone_number,
            "Arrival Date": reservation.arrival_date,
            "Departure Date": reservation.departure_date,
            "Booking Status": reservation.reservation_status
        })

    df = pd.DataFrame(data)

    # -------------------------------
    # Excel Export
    # -------------------------------
    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="User Activity Log")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=User_Activity_Log.xlsx"
            }
        )

    # -------------------------------
    # JSON Export
    # -------------------------------
    json_data = df.to_json(orient="records", date_format="iso")

    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=User_Activity_Log.json"
        }
    )

#-------------- Room Booked Details Export ----------------

@router.get("/export_room_booked_details", status_code=status.HTTP_200_OK)
def export_room_booked_details(request: Request,
    db: Session = Depends(get_db),
    format: str = Query("excel", enum=["excel", "json"]),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    # -------------------------------
    # Date validation
    # -------------------------------
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        from_date = yesterday
        to_date = today

    # -------------------------------
    # Fetch reservation data
    # -------------------------------
    # `active_reservations` carries the `status == ACTIVE` filter this query
    # was missing: without it a soft-deleted booking was still exported, and
    # still counted toward the totals below, as revenue on a reservation that
    # no longer exists.
    reservations = (
        nas.active_reservations(db, company_id)
        .filter(models.RoomReservation.arrival_date.between(from_date, to_date))
        .order_by(models.RoomReservation.arrival_date.asc())
        .all()
    )

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for reservation in reservations:
        full_name = f"{reservation.first_name} {reservation.last_name}"
        data.append({
            "Reservation ID": reservation.room_reservation_id,
            "Guest Name": full_name,
            "Phone Number": reservation.phone_number,
            "Arrival Date": reservation.arrival_date,
            "Departure Date": reservation.departure_date,
            "Booking Status": reservation.reservation_status
        })

    df = pd.DataFrame(data)

    # -------------------------------
    # Excel Export
    # -------------------------------
    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Room Booked Details")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=Room_Booked_Details.xlsx"
            }
        )

    # -------------------------------
    # JSON Export
    # -------------------------------
    json_data = df.to_json(orient="records", date_format="iso")

    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=Room_Booked_Details.json"
        }
    )

#-------------- HSK Task Details Export ----------------

@router.get("/export_hsk_details", status_code=status.HTTP_200_OK)
def export_hsk_details(request: Request,
    db: Session = Depends(get_db),
    format: str = Query("excel", enum=["excel", "json"]),
    sch_date: Optional[str] = Query(None)):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    # -------------------------------
    # Date validation
    # -------------------------------
    if sch_date:
        try:
            sch_date = dt.datetime.strptime(sch_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        sch_date = date.today()

    # -------------------------------
    # Fetch HSK task data
    # -------------------------------
    hsk_tasks = db.query(models.HousekeeperTask).filter(
        models.HousekeeperTask.company_id == company_id,
        models.HousekeeperTask.schedule_date == sch_date
    ).order_by(models.HousekeeperTask.room_no.asc()).all()

    # -------------------------------
    # Prepare export data
    # -------------------------------
    data = []
    for task in hsk_tasks:
        full_name = f"{task.first_name} {task.last_name}"
        data.append({
            "Employee ID": task.employee_id,
            "Employee Name": full_name,
            "Room Number": task.room_no,
            "Task Type": task.task_type,
            "Assigned Staff": task.assign_staff,
            "Task Status": task.task_status,
            "Schedule Date": task.schedule_date
        })

    df = pd.DataFrame(data)

    # -------------------------------
    # Excel Export
    # -------------------------------
    if format == "excel":
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="HSK Task Details")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=HSK_Task_Details.xlsx"
            }
        )

    # -------------------------------
    # JSON Export
    # -------------------------------
    json_data = df.to_json(orient="records", date_format="iso")

    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=HSK_Task_Details.json"
        }
    )

# Settlement Summary Export

@router.get("/export_settlement_summary")
async def export_settlement_summary(request: Request,
    db: Session = Depends(get_db),
    format: str = Query("excel"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None):
    # company_id now comes from the verified token. It used to be a
    # caller-supplied parameter on an unauthenticated route.
    user_id, role_id, company_id, token = verify_authentication(request)
    # Validate & prepare dates
    if from_date and to_date:
        try:
            from_date = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = dt.datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Expected YYYY-MM-DD"
            )
    else:
        today = date.today()
        from_date = today - timedelta(days=1)
        to_date = today

    # Fetch reservation data
    # Same missing `status == ACTIVE` filter as the booked-details export --
    # see the note there.
    settlement_data = (
        nas.active_reservations(db, company_id)
        .filter(models.RoomReservation.arrival_date.between(from_date, to_date))
        .all()
    )

    data = []
    total_paid = 0
    total_overall = 0

    for row in settlement_data:
        paid_amount = row.paid_amount or 0
        overall_amount = row.overall_amount or 0

        total_paid += paid_amount
        total_overall += overall_amount

        data.append({
            "Room Reservation ID": row.room_reservation_id,
            "Name": f"{row.first_name} {row.last_name}",
            "Overall Amount": overall_amount,
            "Paid Amount": paid_amount,
            "Balance Amount": row.balance_amount,
            "Arrival Date": row.arrival_date,
            "Departure Date": row.departure_date,
            "Reservation Status": row.reservation_status
        })

    df = pd.DataFrame(data)

    # Append totals row
    totals_row = pd.DataFrame([{
        "Room Reservation ID": "Total",
        "Name": "",
        "Overall Amount": total_overall,
        "Paid Amount": total_paid,
        "Balance Amount": total_overall - total_paid,
        "Arrival Date": "",
        "Departure Date": "",
        "Reservation Status": ""
    }])

    df = pd.concat([df, totals_row], ignore_index=True)

    # Export handling
    if format == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Settlement Summary")
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=Settlement_Summary.xlsx"}
        )

    if format == "json":
        json_data = df.to_json(orient="records")
        return StreamingResponse(
            io.BytesIO(json_data.encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=Settlement_Summary.json"}
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported format. Use 'excel' or 'json'"
    )

# =====================================================================
# NIGHT AUDIT
#
# Everything below is the operational module: the business date, the
# readiness check, the run, and the history. The report endpoints above are
# unchanged.
#
# One rule holds throughout: the business date comes from
# `hotel_business_date`, never from `date.today()`. A hotel day ends when the
# audit says it ends, not at midnight, and the whole point of the module is
# that a night which was never closed cannot be quietly skipped.
# =====================================================================


async def _fetch_rooms_total(token: str) -> Optional[int]:
    """Room inventory count from MasterDataServices. Best-effort, never fatal.

    Used only to express occupancy as a percentage. It is fetched BEFORE the
    audit transaction opens and outside it, so a slow or unreachable master
    service can never hold a database lock or fail a run -- the audit simply
    records `rooms_total = null` and the percentage is omitted.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{MASTER_SERVICE_URL}/room",
                headers={"Authorization": f"Bearer {token}"},
            )
        if resp.status_code != 200:
            logger.info("rooms_total_unavailable status=%s", resp.status_code)
            return None
        payload = resp.json() or {}
        count = payload.get("count")
        if isinstance(count, int):
            return count
        data = payload.get("data")
        return len(data) if isinstance(data, list) else None
    except (httpx.HTTPError, ValueError):
        # Occupancy percentage is a nicety; the audit is not.
        logger.info("rooms_total_fetch_failed", exc_info=True)
        return None


def _business_date_payload(bd_row) -> dict:
    return {
        "business_date": bd_row.business_date,
        "next_business_date": bd_row.business_date + timedelta(days=1),
        "last_audit_at": bd_row.last_audit_at,
        "last_audit_by": bd_row.last_audit_by,
        # Exposed so the UI can show "the calendar has moved on, you are
        # behind" rather than leaving an operator to work it out.
        "server_date": date.today(),
        "days_behind": max((date.today() - bd_row.business_date).days, 0),
    }


@router.get("/night_audit/status", status_code=status.HTTP_200_OK)
def night_audit_status(request: Request, db: Session = Depends(get_db)):
    """Business date, readiness and headline counts. The dashboard's first call."""
    user_id, role_id, company_id, token = verify_authentication(request)

    bd_row = nas.ensure_business_date(db, company_id, user_id)
    business_date = bd_row.business_date

    position = nas.compute_position(db, company_id, business_date)
    existing = (
        db.query(models.NightAudit)
        .filter(
            models.NightAudit.company_id == str(company_id),
            models.NightAudit.business_date == business_date,
        )
        .first()
    )
    readiness = nas.build_readiness(position, business_date, existing)

    last_audit = (
        db.query(models.NightAudit)
        .filter(
            models.NightAudit.company_id == str(company_id),
            models.NightAudit.audit_status == nas.AUDIT_COMPLETED,
        )
        .order_by(models.NightAudit.business_date.desc())
        .first()
    )

    return {
        "status": "success",
        "data": {
            **_business_date_payload(bd_row),
            "readiness": readiness,
            "movement": position["movement"],
            "revenue": position["revenue"],
            "settlement": position["settlement"],
            "occupancy": position["occupancy"],
            # A Failed row here is what makes the UI able to offer Retry.
            "current_audit": nas.audit_to_dict(existing) if existing else None,
            "last_completed_audit": nas.audit_to_dict(last_audit) if last_audit else None,
        },
    }


@router.get("/night_audit/preview", status_code=status.HTTP_200_OK)
def night_audit_preview(
    request: Request,
    business_date: Optional[str] = Query(
        None,
        description="Inspect a past night (YYYY-MM-DD). Defaults to the current business date.",
    ),
    db: Session = Depends(get_db),
):
    """The full position for a night, including the reservation lists.

    This is what the operator reviews before running, and it is computed by the
    same `compute_position` the run itself snapshots -- so what is approved on
    screen is exactly what gets recorded. The frontend never adds up a total of
    its own.
    """
    user_id, role_id, company_id, token = verify_authentication(request)

    bd_row = nas.ensure_business_date(db, company_id, user_id)
    target = bd_row.business_date
    if business_date:
        try:
            target = dt.datetime.strptime(business_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

    position = nas.compute_position(db, company_id, target)
    existing = (
        db.query(models.NightAudit)
        .filter(
            models.NightAudit.company_id == str(company_id),
            models.NightAudit.business_date == target,
        )
        .first()
    )

    return {
        "status": "success",
        "data": {
            **_business_date_payload(bd_row),
            "audited_date": target,
            "is_current_business_date": target == bd_row.business_date,
            "readiness": nas.build_readiness(position, target, existing),
            "movement": position["movement"],
            "revenue": position["revenue"],
            "settlement": position["settlement"],
            "occupancy": position["occupancy"],
            "lists": position["lists"],
            "existing_audit": nas.audit_to_dict(existing) if existing else None,
        },
    }


@router.post("/night_audit/run", status_code=status.HTTP_200_OK)
async def night_audit_run(request: Request, db: Session = Depends(get_db)):
    """Close the current business day.

    IDEMPOTENCY
        `night_audit` carries UNIQUE(company_id, business_date), and the run
        holds a FOR UPDATE lock on the business-date row for its whole
        duration. A double-clicked button, a retried request, a refresh
        mid-run, a second tab and a second operator all converge on the same
        outcome: one audit row, one date roll, and a 409 for the loser.

    ATOMICITY
        No-show updates, the snapshot and the date roll commit together or not
        at all. There is no window in which the date has advanced but the night
        was not recorded.

    FAILURE
        The transaction is rolled back and the night is recorded as Failed with
        its reason, so the UI can never show a failure as a completed audit.
        Retrying reuses that row -- the failed run left nothing behind to undo.
    """
    user_id, role_id, company_id, token = verify_authentication(request)

    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    # Defaults to True because an arrival that never happened is the normal
    # thing a night audit resolves, but it stays an explicit operator choice:
    # the run writes to real reservations, and the ids it changed are stored on
    # the audit row so the change is attributable and can be undone by hand.
    mark_no_shows = bool(payload.get("mark_no_shows", True))

    # Required, not optional. The caller has to say which night it believes it
    # is closing; that is what stops a double-click from closing two nights in
    # a row. See run_audit's docstring -- this was added after eight concurrent
    # runs each correctly closed a DIFFERENT night.
    raw_date = payload.get("business_date")
    if not raw_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "business_date is required. Send the date shown on the Night Audit "
                "screen so a stale page cannot close the wrong night."
            ),
        )
    try:
        expected_business_date = dt.datetime.strptime(str(raw_date), "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid business_date format. Use YYYY-MM-DD"
        )

    bd_row = nas.ensure_business_date(db, company_id, user_id)
    business_date = bd_row.business_date

    # Outside the transaction on purpose -- see _fetch_rooms_total.
    rooms_total = await _fetch_rooms_total(token)

    try:
        audit = nas.run_audit(
            db,
            company_id,
            user_id,
            expected_business_date=expected_business_date,
            mark_no_shows=mark_no_shows,
            rooms_total=rooms_total,
        )
        db.commit()
        db.refresh(audit)
    except AuditConflict as conflict:
        db.rollback()
        raise HTTPException(
            status_code=conflict.http_status,
            detail=conflict.message,
        )
    except IntegrityError as exc:
        # uq_night_audit_company_date fired: another run recorded this night
        # between our readiness check and our INSERT. The database is the last
        # line of the idempotency guarantee, and reaching it is not an error
        # condition -- it is the guarantee working. It must read to the
        # operator as "already done", never as "the audit crashed".
        db.rollback()
        if "uq_night_audit_company_date" in str(getattr(exc, "orig", exc)):
            logger.info(
                "night_audit_race_lost date=%s company=%s", business_date, company_id
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"{business_date.isoformat()} has already been audited. "
                    "Refresh to see the completed audit."
                ),
            )
        logger.exception("night_audit_integrity_error date=%s", business_date)
        nas.record_failure(db, company_id, business_date, user_id, str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Night audit failed and was rolled back. No changes were applied.",
        )
    except Exception as exc:
        db.rollback()
        # The rollback discarded the audit row too, so the failure is written
        # again in its own transaction. "We tried and it failed" and "nobody
        # ever ran it" are different facts, and only the first says "retry".
        logger.exception("night_audit_failed date=%s company=%s", business_date, company_id)
        nas.record_failure(db, company_id, business_date, user_id, str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Night audit failed and was rolled back. No changes were applied.",
        )

    fresh_bd = nas.get_business_date_row(db, company_id)
    return {
        "status": "success",
        "message": f"Night audit completed for {business_date.isoformat()}.",
        "data": {
            "audit": nas.audit_to_dict(audit),
            **(_business_date_payload(fresh_bd) if fresh_bd else {}),
        },
    }


@router.get("/night_audit/history", status_code=status.HTTP_200_OK)
def night_audit_history(
    request: Request,
    limit: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Past runs, newest night first. Includes Failed runs -- deliberately.

    A history that hid failures would let a night that blew up look like a
    night that was never due.
    """
    user_id, role_id, company_id, token = verify_authentication(request)

    rows = (
        db.query(models.NightAudit)
        .filter(models.NightAudit.company_id == str(company_id))
        .order_by(models.NightAudit.business_date.desc())
        .limit(limit)
        .all()
    )

    return {
        "status": "success",
        "count": len(rows),
        "data": [nas.audit_to_dict(r) for r in rows],
    }


# Declared AFTER /night_audit/status, /preview, /run and /history: FastAPI
# matches in declaration order, so a `{audit_id}` route placed above them would
# swallow "status" and "history" as ids.
@router.get("/night_audit/{audit_id}", status_code=status.HTTP_200_OK)
def night_audit_detail(
    request: Request,
    audit_id: int,
    db: Session = Depends(get_db),
):
    """One audit as it was recorded. Never recomputed from live reservations."""
    user_id, role_id, company_id, token = verify_authentication(request)

    audit = (
        db.query(models.NightAudit)
        .filter(
            models.NightAudit.id == audit_id,
            models.NightAudit.company_id == str(company_id),
        )
        .first()
    )
    if not audit:
        raise HTTPException(status_code=404, detail="Night audit not found")

    return {"status": "success", "data": nas.audit_to_dict(audit)}


# ---------------------------------------------------------------------------
# Legacy report endpoint, repaired.
#
# WHAT WAS WRONG WITH IT
#   1. It gated on `request.session["sessid"]`. Every external request arrives
#      through the gateway proxy, which forwards a bearer token and no cookie
#      session, so that key was never present and the endpoint returned a 307
#      redirect to the login page on EVERY call. It had never once executed.
#   2. It summed the FULL `room_amount` of reservations *arriving* that day and
#      called the result one day's room revenue. `room_amount` is the whole
#      stay, so a 6-night booking counted six nights of money against its
#      arrival date -- while every guest already in-house that night counted
#      nothing at all.
#   3. It grouped payments by `payment_method_id` off the reservation, which is
#      the method chosen at booking, not the methods actually used to pay.
#
# It now delegates to the same position calculation as the rest of the module,
# so it can no longer disagree with the audit record.
# ---------------------------------------------------------------------------

@router.get("/night_audit_process")
def night_audit_process(
    request: Request,
    business_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id, token = verify_authentication(request)

    bd_row = nas.ensure_business_date(db, company_id, user_id)
    audit_date = bd_row.business_date
    if business_date:
        try:
            audit_date = dt.datetime.strptime(business_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

    position = nas.compute_position(db, company_id, audit_date)

    return {
        "status": "success",
        "data": {
            "audit_date": audit_date,
            "reservations_count": position["movement"]["in_house"],
            "room_revenue": position["revenue"]["room_revenue"],
            "extra_charges": position["revenue"]["extra_charges"],
            "payment_summary": position["settlement"]["payment_breakdown"],
            "total_payments": position["settlement"]["payments_collected"],
        },
    }

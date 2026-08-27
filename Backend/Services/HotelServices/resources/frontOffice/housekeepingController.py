"""Housekeeping: task assignments and room incident logs.

TWO RESOURCES, ONE DEPARTMENT
    housekeeper_task   an assignment: who cleans which room, when, and how far
                       along the work is.
    hsk_room_incident  something that went wrong in a room, who was involved,
                       what was done about it, and an optional photo/report.

WHAT WAS WRONG BEFORE
    Every scalar was read as `payload.get(key, "").strip()`. A JSON `null` --
    which is exactly what the edit form sends back for an empty optional
    column -- and a JSON number -- which is what the create form sent for the
    room and staff ids -- both made that raise AttributeError. The bare
    `except Exception` at the bottom of each handler then re-raised it as a
    500 carrying the raw Python message ("'int' object has no attribute
    'strip'"). Creating a task and editing a task both failed that way, on
    every submission, and the client saw an internal error string.

    Reading is done through `_text` / `_int` / `_date` / `_time` now, so a
    missing or malformed field is a 400 naming the field, an unexpected one is
    logged and answered with a generic 500, and the operational vocabularies
    (task status, room status, severity) are checked against the values the
    columns actually hold instead of being written through unvalidated.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from configs.base_config import BaseConfig, CommonWords
from models import get_db, models
from models.masterdata import MasterRoom
from resources.utils import verify_authentication

logger = logging.getLogger("hotelservice.housekeeping")

router = APIRouter()

UPLOAD_PATH = "./templates/static/room_incidents"
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Images plus PDF: an incident attachment is either a photo of the damage or a
# scanned maintenance report. The base allow-list is images only, so PDF is
# added here rather than widened for every upload in the app.
#
# There was no check at all before -- `attachment_file.filename.split(".")[-1]`
# took whatever the client sent, so a `.exe` was accepted and written into a
# directory the static mount serves, and a file of any size was read into
# memory and onto disk.
ALLOWED_UPLOAD_EXTS = set(BaseConfig.UPLOAD_ALLOWED_EXTENSIONS) | {"pdf"}
UPLOAD_MAX_BYTES = BaseConfig.UPLOAD_MAX_BYTES

# Operational vocabularies. These are the values the columns already hold and
# the ones the UI offers; anything else is a client bug, not data.
TASK_STATUSES = ("Pending", "In-Progress", "Completed")
ROOM_STATUSES = ("Blocking", "Unblocking")
SEVERITIES = ("Low", "Medium", "High", "Critical")

# A task that is not Completed is still holding the room.
OPEN_TASK_STATUSES = frozenset({"pending", "in-progress"})

# masterdata.room spellings. `room.Room_Status` is the sellability flag the
# reservation rules read (`Blocking` = out of order); `Room_Working_status` is
# housekeeping readiness. Note the capital B in "UnBlocking" -- that is the
# spelling the master schema uses (CommonWords.Room_Condition), and it differs
# from the task column's own "Unblocking".
ROOM_BLOCKED = "Blocking"
ROOM_UNBLOCKED = "UnBlocking"
ROOM_READY = "Ready"
ROOM_NOT_READY = "Not Ready"
# The misspelling is the value the schema actually holds; it is what
# MasterDataServices writes on every new room (CommonWords.WORK_STATUS) and
# TableTemplate already renders it as "Unassigned".
ROOM_UNASSIGNED = "Not Assigne"

TEXT_MAX = 255
NAME_MAX = 100


# =====================================================
# PAYLOAD READERS
# =====================================================
def _text(payload: dict, key: str, *, max_len: int = TEXT_MAX) -> Optional[str]:
    """A trimmed string from a JSON body, whatever the client actually sent.

    `null`, a number and a missing key all collapse to None instead of raising,
    which is the whole of the create/update 500 described in the module
    docstring. Values are truncated to the column width so a long paste is a
    trimmed string rather than a MySQL "Data too long" 500.
    """
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        value = str(value)
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value[:max_len] if value else None


def _required_text(payload: dict, key: str, label: str, *, max_len: int = TEXT_MAX) -> str:
    value = _text(payload, key, max_len=max_len)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} is required"
        )
    return value


def _int(payload: dict, key: str, label: str, *, required: bool = False) -> Optional[int]:
    """A positive integer id from a JSON body, sent as a number or a string.

    The room picker posts `Number(id)` on create and the raw string on edit, so
    both have to be accepted for the same field.
    """
    value = payload.get(key)
    if value is None or value == "":
        if required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} is required"
            )
        return None
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} must be a number"
        )
    if number <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} must be a number"
        )
    return number


def _date(value, label: str, *, required: bool = False):
    """A date from `YYYY-MM-DD`, which is what <input type="date"> submits."""
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} is required"
            )
        return None
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label} must be in YYYY-MM-DD format",
        )


def _time(value, label: str, *, required: bool = False):
    """A time from `HH:MM` or `HH:MM:SS`.

    Both forms have to be accepted for the same field: <input type="time">
    submits `HH:MM`, while the value read back out of an existing row is
    `HH:MM:SS`. Create used to accept only the first and update only the
    second, so re-saving an incident without touching its time was a 500
    ("time data '14:35' does not match format '%H:%M:%S'").
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} is required"
            )
        return None
    raw = str(value).strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{label} must be in HH:MM format",
    )


def _one_of(value: Optional[str], allowed: tuple, label: str, default: Optional[str] = None):
    """Constrain a value to a vocabulary, case-insensitively.

    Matching is case-insensitive but the CANONICAL spelling is stored, so the
    column keeps one spelling per value however the caller cased it.
    """
    if not value:
        return default
    for option in allowed:
        if value.lower() == option.lower():
            return option
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{label} must be one of: {', '.join(allowed)}",
    )


def _server_error(exc: Exception) -> HTTPException:
    """Log the detail, return a generic message.

    `detail=str(e)` leaked Python exception text to the browser on every
    unexpected failure, which is both a poor error message and an information
    disclosure.
    """
    logger.exception("unhandled_exception")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
    )


async def _json_body(request: Request) -> dict:
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
        )
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
        )
    return payload


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return user_id, company_id


# =====================================================
# MASTER ROOM: VALIDATION AND WRITE-BACK
# =====================================================
def _load_room(db: Session, company_id, room_id: int):
    """The master room row, or None if it is not an active room here.

    `models.masterdata` maps the MasterData schema on the same server, so this
    is a plain join-able query rather than a call to another service.
    """
    return (
        db.query(MasterRoom)
        .filter(
            MasterRoom.id == room_id,
            MasterRoom.company_id == str(company_id),
            MasterRoom.status == CommonWords.STATUS,
        )
        .first()
    )


def _validate_room(db: Session, company_id, room_id: int) -> None:
    """Reject a room id that is not a room of this property.

    Nothing checked this before, so `room_no: 99999` was accepted and stored;
    the row then rendered as a blank room everywhere it was listed.

    A failure to reach the master schema is logged and allowed through rather
    than turned into a 500: this is a referential check on an id the picker
    already constrains, not the thing standing between the user and their work.
    """
    try:
        room = _load_room(db, company_id, room_id)
    except Exception:
        logger.exception("master_room_lookup_failed room_id=%s", room_id)
        return
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected room does not exist for this property",
        )


def _sync_room_housekeeping(db: Session, company_id, room_ids) -> None:
    """Recompute a room's two housekeeping columns from its active tasks.

    WHY THIS EXISTS
        `housekeeper_task.room_status` (Blocking / Unblocking) and
        `masterdata.room.Room_Status` hold the same vocabulary, and
        `room.Room_Working_status` is the column the Master Data Rooms screen
        labels "Housekeeping" and documents as read-only because it is set by
        operations elsewhere. Nothing in the system ever wrote either of them,
        so blocking a room from the Task Assign screen changed nothing anywhere
        and the control was a dead end -- while the reservation availability
        rules were already refusing to sell a room whose Room_Status is
        "Blocking".

    THE RULE, WHICH IS ORDER-INDEPENDENT ON PURPOSE
        Derived from the full set of that room's active tasks rather than from
        whichever task was just saved, so two tasks on one room cannot leave
        the room in a state that depends on which was edited last:

            blocked  <- any OPEN task on the room says Blocking
            ready    <- the room has tasks and none of them is still open

        A Completed task never blocks: the work it blocked the room for is
        done.

        With no active tasks left, "Not Ready" is a claim that work is
        outstanding when none is, so it reverts to "Not Assigne" -- the third
        value in the column's vocabulary and the one a freshly created room
        carries (CommonWords.WORK_STATUS). "Ready" is left alone in that case:
        a completed clean is a fact about the room, and deleting the task
        record afterwards does not make the room dirty again.

    MINIMAL WRITES
        Each column is written only when the value would actually change, which
        keeps the legacy `Room_Status = 'ACTIVE'` on the rooms housekeeping has
        never blocked (the reservation rules already read anything that is not
        "blocking" as sellable).

    ISOLATION
        Runs after the task write has been committed, in its own transaction.
        A room that fails to sync is logged and left alone; the calculation is
        idempotent, so the next action on any task for that room repairs it.
    """
    targets = {rid for rid in (room_ids or []) if rid}
    if not targets:
        return

    try:
        for room_id in targets:
            room = _load_room(db, company_id, room_id)
            if not room:
                continue

            tasks = (
                db.query(models.HousekeeperTask)
                .filter(
                    models.HousekeeperTask.company_id == company_id,
                    models.HousekeeperTask.room_no == room_id,
                    models.HousekeeperTask.status == CommonWords.STATUS,
                )
                .all()
            )

            open_tasks = [
                task
                for task in tasks
                if (task.task_status or "").strip().lower() in OPEN_TASK_STATUSES
            ]

            want_blocked = any(
                (task.room_status or "").strip().lower() == "blocking"
                for task in open_tasks
            )
            is_blocked = (room.Room_Status or "").strip().lower() == "blocking"
            if want_blocked != is_blocked:
                room.Room_Status = ROOM_BLOCKED if want_blocked else ROOM_UNBLOCKED

            current_work = (room.Room_Working_status or "").strip().lower()
            if tasks:
                want_work = ROOM_NOT_READY if open_tasks else ROOM_READY
            elif current_work == ROOM_NOT_READY.lower():
                want_work = ROOM_UNASSIGNED
            else:
                want_work = None

            if want_work and current_work != want_work.lower():
                room.Room_Working_status = want_work

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("room_housekeeping_sync_failed rooms=%s", sorted(targets))


# =====================================================
# UPLOADS
# =====================================================
def _sanitize_upload(upload: UploadFile) -> tuple[str, bytes]:
    """Validate and read an incoming attachment, or raise.

    Mirrors MasterDataServices._sanitize_upload so both services enforce the
    same rule; only the extension set differs (PDF is allowed here).
    """
    if not upload or not upload.filename:
        raise HTTPException(status_code=400, detail="File is required")
    ext = os.path.splitext(upload.filename)[1].lstrip(".").lower()
    if not ext or ext not in ALLOWED_UPLOAD_EXTS:
        raise HTTPException(
            status_code=400,
            detail="Attachment must be an image (JPG, PNG, GIF, WEBP) or a PDF",
        )
    data = upload.file.read(UPLOAD_MAX_BYTES + 1)
    if len(data) > UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Attachment exceeds the size limit")
    if not data:
        raise HTTPException(status_code=400, detail="Attachment is empty")
    return ext, data


def _write_upload(data: bytes, ext: str) -> str:
    """Persist bytes under UPLOAD_PATH; return the URL path the static mount serves.

    Returns a site-absolute POSIX path. The previous version stored
    `os.path.join(UPLOAD_PATH, name)`, which on Windows produced
    `templates/static/room_incidents\\<file>.png` -- a backslash and no leading
    slash, so the stored value could not be used as a URL at all and the
    attachment was write-only.
    """
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(UPLOAD_PATH, safe_name), "wb") as fh:
        fh.write(data)
    return f"/templates/static/room_incidents/{safe_name}"


# =====================================================
# SERIALISERS
# =====================================================
def _task_row(task) -> dict:
    """One task as the list, detail and write responses all return it.

    `created_at` / `updated_at` are included on list rows so the View dialog
    can show them without a second round trip -- GET /housekeeper_tasks/{id}
    has no page permission mapped to it, so the list is the only read the UI
    can rely on.
    """
    return {
        "id": task.id,
        "employee_id": task.employee_id,
        "first_name": task.first_name,
        "last_name": task.last_name,
        "schedule_date": task.schedule_date,
        "schedule_time": task.schedule_time,
        "room_no": task.room_no,
        "task_type": task.task_type,
        "assign_staff": task.assign_staff,
        "task_status": task.task_status,
        "room_status": task.room_status,
        "lost_found": task.lost_found,
        "special_instructions": task.special_instructions,
        "created_by": task.created_by,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def _incident_row(incident) -> dict:
    return {
        "id": incident.id,
        # `room_no` on the model holds the master room id; the API has always
        # called it room_id on the way out and the UI reads that name.
        "room_id": incident.room_no,
        "incident_date": incident.incident_date,
        "incident_time": incident.incident_time,
        "incident_description": incident.incident_description,
        "involved_staff": incident.involved_staff,
        "severity": incident.severity,
        "witnesses": incident.witnesses,
        "actions_taken": incident.actions_taken,
        "reported_by": incident.reported_by,
        "report_date": incident.report_date,
        "attachment_file": incident.attachment_file,
        "created_by": incident.created_by,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
    }


# =====================================================
# HOUSEKEEPER TASKS
# =====================================================
@router.get("/housekeeper_tasks", status_code=status.HTTP_200_OK)
def get_housekeeper_tasks(request: Request, db: Session = Depends(get_db)):
    try:
        _user_id, company_id = _auth(request)

        tasks = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .order_by(models.HousekeeperTask.id.desc())
            .all()
        )
        data = [_task_row(task) for task in tasks]
        return {"status": "success", "count": len(data), "data": data}

    except HTTPException:
        raise
    except Exception as exc:
        raise _server_error(exc)


@router.post("/housekeeper_tasks", status_code=status.HTTP_201_CREATED)
async def create_housekeeper_task(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, company_id = _auth(request)
        payload = await _json_body(request)

        # The four columns below are all NOT NULL and all describe the one
        # person the task is assigned to: employee_id and assign_staff both
        # hold that user's id, first/last name are the denormalised copy the
        # dashboard and night-audit screens read. The form fills all four from
        # a single staff picker.
        employee_id = _required_text(payload, "employee_id", "Assigned employee", max_len=NAME_MAX)
        assign_staff = _text(payload, "assign_staff", max_len=NAME_MAX) or employee_id
        room_id = _int(payload, "room_no", "Room", required=True)
        _validate_room(db, company_id, room_id)

        task = models.HousekeeperTask(
            employee_id=employee_id,
            first_name=_required_text(payload, "first_name", "First name", max_len=NAME_MAX),
            last_name=_required_text(payload, "last_name", "Last name", max_len=NAME_MAX),
            schedule_date=_date(payload.get("schedule_date"), "Schedule date", required=True),
            schedule_time=_time(payload.get("schedule_time"), "Schedule time", required=True),
            room_no=room_id,
            task_type=_required_text(payload, "task_type", "Task type", max_len=NAME_MAX),
            assign_staff=assign_staff,
            task_status=_one_of(
                _text(payload, "task_status"), TASK_STATUSES, "Task status", TASK_STATUSES[0]
            ),
            room_status=_one_of(
                _text(payload, "room_status"), ROOM_STATUSES, "Room status", ROOM_STATUSES[1]
            ),
            lost_found=_text(payload, "lost_found"),
            special_instructions=_text(payload, "special_instructions"),
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        _sync_room_housekeeping(db, company_id, [task.room_no])

        return {
            "status": "success",
            "message": "Housekeeper task created successfully",
            "data": _task_row(task),
        }

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise _server_error(exc)


@router.get("/housekeeper_tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_housekeeper_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        _user_id, company_id = _auth(request)

        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task id"
            )

        task = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.id == task_id,
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Housekeeper task not found"
            )

        return {"status": "success", "data": _task_row(task)}

    except HTTPException:
        raise
    except Exception as exc:
        raise _server_error(exc)


@router.put("/housekeeper_tasks", status_code=status.HTTP_200_OK)
async def update_housekeeper_task(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, company_id = _auth(request)
        payload = await _json_body(request)

        task_id = _int(payload, "id", "Housekeeper task id", required=True)

        task = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.id == task_id,
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Housekeeper task not found"
            )

        employee_id = _required_text(payload, "employee_id", "Assigned employee", max_len=NAME_MAX)
        room_id = _int(payload, "room_no", "Room", required=True)
        _validate_room(db, company_id, room_id)

        # Both rooms have to be recomputed when a task moves between them, or
        # the room it left keeps a block that nothing holds any more.
        previous_room_id = task.room_no

        task.employee_id = employee_id
        task.first_name = _required_text(payload, "first_name", "First name", max_len=NAME_MAX)
        task.last_name = _required_text(payload, "last_name", "Last name", max_len=NAME_MAX)
        task.schedule_date = _date(payload.get("schedule_date"), "Schedule date", required=True)
        task.schedule_time = _time(payload.get("schedule_time"), "Schedule time", required=True)
        task.room_no = room_id
        task.task_type = _required_text(payload, "task_type", "Task type", max_len=NAME_MAX)
        # employee_id was silently ignored by the old update handler, so
        # re-assigning a task never took effect.
        task.assign_staff = _text(payload, "assign_staff", max_len=NAME_MAX) or employee_id
        task.task_status = _one_of(
            _text(payload, "task_status"), TASK_STATUSES, "Task status", task.task_status
        )
        task.room_status = _one_of(
            _text(payload, "room_status"), ROOM_STATUSES, "Room status", task.room_status
        )
        task.lost_found = _text(payload, "lost_found")
        task.special_instructions = _text(payload, "special_instructions")
        # Was never recorded, so an edited row looked untouched in the audit
        # columns.
        task.updated_by = user_id

        db.commit()
        db.refresh(task)

        _sync_room_housekeeping(db, company_id, [previous_room_id, task.room_no])

        return {
            "status": "success",
            "message": "Housekeeper task updated successfully",
            "data": _task_row(task),
        }

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise _server_error(exc)


@router.delete("/housekeeper_tasks/{task_id}", status_code=status.HTTP_200_OK)
def delete_housekeeper_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    try:
        user_id, company_id = _auth(request)

        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task id"
            )

        task = (
            db.query(models.HousekeeperTask)
            .filter(
                models.HousekeeperTask.id == task_id,
                models.HousekeeperTask.company_id == company_id,
                models.HousekeeperTask.status == CommonWords.STATUS,
            )
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Housekeeper task not found"
            )

        # Soft delete: the row stays for reporting, it just leaves every
        # ACTIVE-filtered read.
        room_id = task.room_no
        task.status = CommonWords.UNSTATUS
        task.updated_by = user_id
        db.commit()

        # Cancelling the task that blocked a room has to release the room.
        _sync_room_housekeeping(db, company_id, [room_id])

        return {"status": "success", "message": "Housekeeper task deleted successfully"}

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise _server_error(exc)


# =====================================================
# ROOM INCIDENTS
# =====================================================
@router.get("/roomincident_log", status_code=status.HTTP_200_OK)
def get_roomincident_logs(request: Request, db: Session = Depends(get_db)):
    try:
        _user_id, company_id = _auth(request)

        incidents = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .order_by(models.HousekeeperRoomIncident.id.desc())
            .all()
        )
        data = [_incident_row(incident) for incident in incidents]
        return {"status": "success", "count": len(data), "data": data}

    except HTTPException:
        raise
    except Exception as exc:
        raise _server_error(exc)


@router.post("/roomincident_log", status_code=status.HTTP_201_CREATED)
async def create_roomincident_log(
    request: Request,
    # ---- required ----
    room_id: int = Form(...),
    incident_date: str = Form(...),
    incident_time: str = Form(...),
    incident_description: str = Form(...),
    # ---- optional ----
    involved_staff: Optional[str] = Form(None),
    severity: Optional[str] = Form(None),
    witnesses: Optional[str] = Form(None),
    actions_taken: Optional[str] = Form(None),
    reported_by: Optional[str] = Form(None),
    report_date: Optional[str] = Form(None),
    attachment_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        user_id, company_id = _auth(request)

        form = {
            "room_id": room_id,
            "incident_description": incident_description,
            "involved_staff": involved_staff,
            "severity": severity,
            "witnesses": witnesses,
            "actions_taken": actions_taken,
            "reported_by": reported_by,
        }

        stored_path = None
        # A multipart part with no file selected still arrives as an
        # UploadFile with an empty filename, so the filename is what decides
        # whether anything was actually attached.
        if attachment_file is not None and attachment_file.filename:
            ext, data = _sanitize_upload(attachment_file)
            stored_path = _write_upload(data, ext)

        incident_room_id = _int(form, "room_id", "Room", required=True)
        _validate_room(db, company_id, incident_room_id)

        incident = models.HousekeeperRoomIncident(
            room_no=incident_room_id,
            incident_date=_date(incident_date, "Incident date", required=True),
            incident_time=_time(incident_time, "Incident time", required=True),
            incident_description=_required_text(form, "incident_description", "Description"),
            involved_staff=_text(form, "involved_staff"),
            severity=_one_of(_text(form, "severity"), SEVERITIES, "Severity"),
            witnesses=_text(form, "witnesses"),
            actions_taken=_text(form, "actions_taken"),
            reported_by=_text(form, "reported_by", max_len=NAME_MAX),
            report_date=_date(report_date, "Report date"),
            attachment_file=stored_path,
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id,
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return {
            "status": "success",
            "message": "Room incident created successfully",
            "data": _incident_row(incident),
        }

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise _server_error(exc)


@router.get("/roomincident_log/{incident_id}", status_code=status.HTTP_200_OK)
def get_roomincident_log(request: Request, incident_id: int, db: Session = Depends(get_db)):
    try:
        _user_id, company_id = _auth(request)

        if incident_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id"
            )

        incident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .first()
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room incident not found"
            )

        return {"status": "success", "data": _incident_row(incident)}

    except HTTPException:
        raise
    except Exception as exc:
        raise _server_error(exc)


@router.put("/roomincident_log", status_code=status.HTTP_200_OK)
async def update_roomincident_log(
    request: Request,
    # ---- required ----
    id: int = Form(...),
    room_id: int = Form(...),
    incident_date: str = Form(...),
    incident_time: str = Form(...),
    incident_description: str = Form(...),
    # ---- optional ----
    involved_staff: Optional[str] = Form(None),
    severity: Optional[str] = Form(None),
    witnesses: Optional[str] = Form(None),
    actions_taken: Optional[str] = Form(None),
    reported_by: Optional[str] = Form(None),
    report_date: Optional[str] = Form(None),
    attachment_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Update an incident, optionally replacing its attachment.

    This used to take JSON and had no way to touch `attachment_file` at all, so
    a file could be added when the incident was first logged and never
    corrected afterwards. It now mirrors the create handler: multipart, with
    the attachment left exactly as it is when no new file is sent.
    """
    try:
        user_id, company_id = _auth(request)

        form = {
            "id": id,
            "room_id": room_id,
            "incident_description": incident_description,
            "involved_staff": involved_staff,
            "severity": severity,
            "witnesses": witnesses,
            "actions_taken": actions_taken,
            "reported_by": reported_by,
        }

        incident_id = _int(form, "id", "Incident id", required=True)

        incident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .first()
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room incident not found"
            )

        # Validate and write the replacement BEFORE mutating the row, so a
        # rejected upload leaves the incident untouched.
        if attachment_file is not None and attachment_file.filename:
            ext, data = _sanitize_upload(attachment_file)
            incident.attachment_file = _write_upload(data, ext)

        incident_room_id = _int(form, "room_id", "Room", required=True)
        _validate_room(db, company_id, incident_room_id)
        incident.room_no = incident_room_id
        incident.incident_date = _date(incident_date, "Incident date", required=True)
        incident.incident_time = _time(incident_time, "Incident time", required=True)
        incident.incident_description = _required_text(
            form, "incident_description", "Description"
        )
        incident.involved_staff = _text(form, "involved_staff")
        incident.severity = _one_of(_text(form, "severity"), SEVERITIES, "Severity")
        incident.witnesses = _text(form, "witnesses")
        incident.actions_taken = _text(form, "actions_taken")
        incident.reported_by = _text(form, "reported_by", max_len=NAME_MAX)
        incident.report_date = _date(report_date, "Report date")
        incident.updated_by = user_id

        db.commit()
        db.refresh(incident)

        return {
            "status": "success",
            "message": "Room incident updated successfully",
            "data": _incident_row(incident),
        }

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise _server_error(exc)


@router.delete("/roomincident_log/{incident_id}", status_code=status.HTTP_200_OK)
def delete_roomincident_log(request: Request, incident_id: int, db: Session = Depends(get_db)):
    try:
        user_id, company_id = _auth(request)

        if incident_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id"
            )

        incident = (
            db.query(models.HousekeeperRoomIncident)
            .filter(
                models.HousekeeperRoomIncident.id == incident_id,
                models.HousekeeperRoomIncident.company_id == company_id,
                models.HousekeeperRoomIncident.status == CommonWords.STATUS,
            )
            .first()
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room incident not found"
            )

        # Soft delete. The attachment stays on disk on purpose: the row is
        # still readable for reporting and an INACTIVE incident can be
        # restored, which a deleted file would make impossible.
        incident.status = CommonWords.UNSTATUS
        incident.updated_by = user_id
        db.commit()

        return {"status": "success", "message": "Room incident deleted successfully"}

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise _server_error(exc)

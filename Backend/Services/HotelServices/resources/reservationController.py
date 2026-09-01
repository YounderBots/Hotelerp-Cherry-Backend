import json
import logging
import os
import uuid
from datetime import date, datetime, timedelta

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from configs.base_config import CommonWords
from models import get_db, models
from models.masterdata import (
    MasterDiscount,
    MasterIdentityProof,
    MasterPaymentMethod,
    MasterReservationStatus,
    MasterRoom,
    MasterRoomType,
    MasterTaxType,
)
from resources import reservation_rules as rules
from resources.utils import verify_authentication

logger = logging.getLogger(__name__)

router = APIRouter()

# =====================================================
# COMMON CONSTANTS & CONFIG
# =====================================================

# ---------------- System Status ----------------
STATUS = "ACTIVE"
UNSTATUS = "INACTIVE"

# ---------------- Reservation Types ----------------
RESERVATION = rules.RESERVATION
GROUP_RESERVATION = rules.GROUP_RESERVATION
CHECKIN = rules.CHECKIN

# ---------------- Upload Paths ----------------
UPLOAD_DIR = "templates/static/identity_proofs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# NOTE: there is deliberately no module-level TODAY / NOW here any more.
# Both used to be evaluated once, at import, so a service that stayed up for a
# week stamped every payment it recorded with the date it was started. Anything
# that needs the current date calls `date.today()` where it needs it.


# =====================================================
# CREATE ROOM BOOKING
# =====================================================
@router.post("/room_booking", status_code=status.HTTP_201_CREATED)
async def create_room_booking(request: Request, db: Session = Depends(get_db)):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # -------------------------------------------------
        # REQUEST BODY (JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
            )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------
        phone_number = payload.get("phone_number")
        arrival_date = payload.get("arrival_date")
        departure_date = payload.get("departure_date")
        room_type_ids = payload.get("room_type")  # list of room_type ids

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="phone_number is required",
            )

        if not arrival_date or not departure_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="arrival_date and departure_date are required",
            )

        if not isinstance(room_type_ids, list) or not room_type_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_type must be a non-empty list of room type ids",
            )

        arrival = datetime.strptime(arrival_date, "%Y-%m-%d").date()
        departure = datetime.strptime(departure_date, "%Y-%m-%d").date()

        if departure <= arrival:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="departure_date must be after arrival_date",
            )

        no_of_nights = (departure - arrival).days

        # -------------------------------------------------
        # CREATE BOOKING ID
        # -------------------------------------------------
        booking_ref = f"RB-{uuid.uuid4().hex[:8].upper()}"

        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------
        booking = models.RoomBooking(
            room_booking_id=booking_ref,
            salutation=payload.get("salutation"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            phone_number=phone_number,
            email=payload.get("email"),
            arrival_date=arrival,
            departure_date=departure,
            no_of_nights=no_of_nights,
            room_type=room_type_ids,  # ✅ ROOM TYPE TABLE IDs STORED HERE
            no_of_rooms=payload.get("no_of_rooms"),
            no_of_adults=payload.get("no_of_adults"),
            no_of_children=payload.get("no_of_children"),
            status=CommonWords.STATUS,
            created_by=user_id,
            company_id=company_id,
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room booking created successfully",
            "data": {
                "id": booking.id,
                "room_booking_id": booking.room_booking_id,
                "phone_number": booking.phone_number,
                "arrival_date": booking.arrival_date,
                "departure_date": booking.departure_date,
                "no_of_nights": booking.no_of_nights,
                "room_type": booking.room_type,
                "created_at": booking.created_at,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# =====================================================
# GET ALL ROOM BOOKINGS
# =====================================================
@router.get("/room_booking", status_code=status.HTTP_200_OK)
def get_all_room_bookings(request: Request, db: Session = Depends(get_db)):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # -------------------------------------------------
        # FETCH BOOKINGS
        # -------------------------------------------------
        bookings = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS,
            )
            .order_by(models.RoomBooking.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE
        # -------------------------------------------------
        data = [
            {
                "id": booking.id,
                "room_booking_id": booking.room_booking_id,
                "salutation": booking.salutation,
                "first_name": booking.first_name,
                "last_name": booking.last_name,
                "phone_number": booking.phone_number,
                "email": booking.email,
                "arrival_date": booking.arrival_date,
                "departure_date": booking.departure_date,
                "no_of_nights": booking.no_of_nights,
                "room_type": booking.room_type,  # room_type table IDs
                "no_of_rooms": booking.no_of_rooms,
                "no_of_adults": booking.no_of_adults,
                "no_of_children": booking.no_of_children,
                "status": booking.status,
                "created_by": booking.created_by,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
            }
            for booking in bookings
        ]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {"status": "success", "count": len(data), "data": data}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# =====================================================
# GET ROOM BOOKING BY ID
# =====================================================
@router.get("/room_booking/{booking_id}", status_code=status.HTTP_200_OK)
def get_room_booking_by_id(
    request: Request, booking_id: int, db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if booking_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking_id"
            )

        # -------------------------------------------------
        # FETCH BOOKING
        # -------------------------------------------------
        booking = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.id == booking_id,
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS,
            )
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room booking not found"
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                "id": booking.id,
                "room_booking_id": booking.room_booking_id,
                "salutation": booking.salutation,
                "first_name": booking.first_name,
                "last_name": booking.last_name,
                "phone_number": booking.phone_number,
                "email": booking.email,
                "arrival_date": booking.arrival_date,
                "departure_date": booking.departure_date,
                "no_of_nights": booking.no_of_nights,
                "room_type": booking.room_type,  # Room_Type table IDs
                "no_of_rooms": booking.no_of_rooms,
                "no_of_adults": booking.no_of_adults,
                "no_of_children": booking.no_of_children,
                "status": booking.status,
                "created_by": booking.created_by,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# =====================================================
# UPDATE ROOM BOOKING
# =====================================================
@router.put("/room_booking", status_code=status.HTTP_200_OK)
async def update_room_booking(request: Request, db: Session = Depends(get_db)):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # -------------------------------------------------
        # REQUEST BODY (JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
            )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------
        booking_id = payload.get("id")
        phone_number = payload.get("phone_number")
        arrival_date = payload.get("arrival_date")
        departure_date = payload.get("departure_date")
        room_type_ids = payload.get("room_type")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if not booking_id or not isinstance(booking_id, int) or booking_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid booking id is required",
            )

        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="phone_number is required",
            )

        if not arrival_date or not departure_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="arrival_date and departure_date are required",
            )

        if not isinstance(room_type_ids, list) or not room_type_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_type must be a non-empty list of room type ids",
            )

        arrival = datetime.strptime(arrival_date, "%Y-%m-%d").date()
        departure = datetime.strptime(departure_date, "%Y-%m-%d").date()

        if departure <= arrival:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="departure_date must be after arrival_date",
            )

        no_of_nights = (departure - arrival).days

        # -------------------------------------------------
        # FETCH BOOKING
        # -------------------------------------------------
        booking = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.id == booking_id,
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS,
            )
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room booking not found"
            )

        # -------------------------------------------------
        # UPDATE BOOKING
        # -------------------------------------------------
        booking.salutation = payload.get("salutation")
        booking.first_name = payload.get("first_name")
        booking.last_name = payload.get("last_name")

        booking.phone_number = phone_number
        booking.email = payload.get("email")

        booking.arrival_date = arrival
        booking.departure_date = departure
        booking.no_of_nights = no_of_nights

        booking.room_type = room_type_ids  # ✅ Room_Type IDs

        booking.no_of_rooms = payload.get("no_of_rooms")
        booking.no_of_adults = payload.get("no_of_adults")
        booking.no_of_children = payload.get("no_of_children")

        booking.updated_by = user_id

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------
        db.commit()
        db.refresh(booking)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room booking updated successfully",
            "data": {
                "id": booking.id,
                "room_booking_id": booking.room_booking_id,
                "arrival_date": booking.arrival_date,
                "departure_date": booking.departure_date,
                "no_of_nights": booking.no_of_nights,
                "room_type": booking.room_type,
                "updated_at": booking.updated_at,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# =====================================================
# DELETE ROOM BOOKING (SOFT DELETE)
# =====================================================
@router.delete("/room_booking/{booking_id}", status_code=status.HTTP_200_OK)
def delete_room_booking(
    request: Request, booking_id: int, db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if booking_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking_id"
            )

        # -------------------------------------------------
        # FETCH BOOKING
        # -------------------------------------------------
        booking = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.id == booking_id,
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS,
            )
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room booking not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        booking.status = CommonWords.UNSTATUS
        booking.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {"status": "success", "message": "Room booking deleted successfully"}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )



# =====================================================
# ROOM RESERVATION
# =====================================================
# Everything below treats the API as the authority. The browser chooses rooms,
# dates, rate types and how much the guest is handing over; the server decides
# whether that is bookable and what it costs. See resources/reservation_rules.py
# for the rules themselves.


# ---------------- Identity proof upload ----------------
ALLOWED_PROOF_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "webp"}
ALLOWED_PROOF_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
UPLOAD_MAX_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", str(5 * 1024 * 1024)))

# A reservation may not start further in the past than this. Back-dating one
# day is routine (a late-night walk-in booked after midnight); back-dating a
# year is a typo that would otherwise silently corrupt occupancy history.
MAX_BACKDATE_DAYS = 1

# Guards against a fat-fingered departure date creating a stay that blocks a
# room for years.
MAX_STAY_NIGHTS = 365
MAX_ROOMS_PER_RESERVATION = 50

# How long an identical submission is treated as a retry of the first rather
# than a second booking. Covers a double-clicked Confirm, a refresh mid-POST
# and a client that retried after a timeout.
REPLAY_WINDOW_SECONDS = 900

# Matches room_reservation.cancellation_reason's column width, so a reason that
# the API accepts can always be stored whole rather than silently truncated.
CANCELLATION_REASON_MAX = 500


def _rule_http(exc: rules.RuleError) -> HTTPException:
    """Business-rule failures reach the client as themselves, not as a 500."""
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


async def _store_identity_proof(identity_file: UploadFile) -> str:
    """Validate and store an identity document. Returns the stored filename.

    The previous version took the extension straight off the client-supplied
    filename and wrote the bytes with no size or type check, into a directory
    this service serves statically -- so an .html or .svg upload became a
    same-origin script. Both the declared content type and the extension have
    to be on the allow-list, and the size cap that already existed in the
    service's .env is finally applied.
    """
    if not identity_file or not identity_file.filename:
        raise HTTPException(status_code=400, detail="Identity document is required")

    extension = identity_file.filename.rsplit(".", 1)[-1].lower() if "." in identity_file.filename else ""
    if extension not in ALLOWED_PROOF_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Identity document must be one of: "
                + ", ".join(sorted(ALLOWED_PROOF_EXTENSIONS))
            ),
        )

    content_type = (identity_file.content_type or "").split(";")[0].strip().lower()
    if content_type and content_type not in ALLOWED_PROOF_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Identity document type '{content_type}' is not accepted",
        )

    # Read through a bounded loop rather than `.read()`: an unbounded read of a
    # multi-gigabyte upload is a memory exhaustion, and checking the size after
    # buffering it defeats the point of a size cap.
    payload = bytearray()
    while True:
        chunk = await identity_file.read(64 * 1024)
        if not chunk:
            break
        payload.extend(chunk)
        if len(payload) > UPLOAD_MAX_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Identity document must be {UPLOAD_MAX_BYTES // (1024 * 1024)} MB or smaller",
            )

    if not payload:
        raise HTTPException(status_code=400, detail="Identity document is empty")

    filename = f"{uuid.uuid4()}.{extension}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as handle:
        handle.write(payload)
    return filename


def _parse_json_list(raw, field: str, *, default=None):
    """A JSON array arriving as a form field."""
    if raw in (None, ""):
        return [] if default is None else default
    if isinstance(raw, list):
        return raw
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"{field} must be a JSON array")
    if not isinstance(parsed, list):
        raise HTTPException(status_code=400, detail=f"{field} must be a JSON array")
    return parsed


def _parse_room_ids(raw) -> list[int]:
    ids = []
    for value in _parse_json_list(raw, "room_ids"):
        try:
            ids.append(int(value))
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400, detail="room_ids must contain only room ids"
            )
    if not ids:
        raise HTTPException(status_code=400, detail="Select at least one room")
    if len(ids) > MAX_ROOMS_PER_RESERVATION:
        raise HTTPException(
            status_code=400,
            detail=f"A reservation can hold at most {MAX_ROOMS_PER_RESERVATION} rooms",
        )
    return ids


def _parse_occupancy(raw, room_ids: list[int], total_adults, total_children):
    """Per-room {room_id: (adults, children)}.

    `room_occupancy` is the precise form and is what the UI sends. When it is
    absent -- an older client, or the Booking screen -- the totals are spread
    across the rooms so occupancy limits can still be checked rather than
    skipped entirely.
    """
    entries = _parse_json_list(raw, "room_occupancy", default=[])
    occupancy: dict[int, tuple[int, int]] = {}

    if entries:
        for entry in entries:
            if not isinstance(entry, dict):
                raise HTTPException(
                    status_code=400,
                    detail="room_occupancy must be a list of {room_id, adults, children}",
                )
            try:
                room_id = int(entry.get("room_id"))
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=400, detail="room_occupancy entries need a room_id"
                )
            occupancy[room_id] = (
                rules.as_int(entry.get("adults"), 0),
                rules.as_int(entry.get("children"), 0),
            )

        missing = [r for r in room_ids if r not in occupancy]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"room_occupancy is missing room {missing[0]}",
            )
        return occupancy

    # Spread the totals as evenly as the rooms allow. Every room gets at least
    # one adult (a room with none is not a booking), and the remainder is dealt
    # round-robin rather than piled onto the first room -- piling it up made a
    # two-room booking for four adults look like a four-adult single, which a
    # room with a two-adult limit would then refuse.
    room_count = len(room_ids)
    adults = max(room_count, rules.as_int(total_adults, room_count))
    children = max(0, rules.as_int(total_children, 0))

    adult_share = [1] * room_count
    child_share = [0] * room_count
    for extra in range(adults - room_count):
        adult_share[extra % room_count] += 1
    for extra in range(children):
        child_share[extra % room_count] += 1

    for index, room_id in enumerate(room_ids):
        occupancy[room_id] = (adult_share[index], child_share[index])
    return occupancy


def _generate_reservation_reference(db: Session, company_id) -> str:
    """A unique, human-readable booking reference. Server-side, always.

    It used to be a form field the browser filled in, which made the reference
    a client's choice: two tabs could submit the same one (a 500 from the
    unique index) and a caller could overwrite the numbering scheme entirely.
    """
    today = date.today().strftime("%Y%m%d")
    for _ in range(10):
        candidate = f"RES-{today}-{uuid.uuid4().hex[:6].upper()}"
        exists = (
            db.query(models.RoomReservation.id)
            .filter(models.RoomReservation.room_reservation_id == candidate)
            .first()
        )
        if not exists:
            return candidate
    raise HTTPException(
        status_code=503,
        detail="Could not allocate a reservation reference; please retry",
    )


def _find_replay(
    db: Session,
    company_id,
    *,
    phone_number: str,
    arrival: date,
    departure: date,
    room_ids: list[int],
):
    """The same booking submitted twice in quick succession, if there is one.

    Once availability is enforced, a double-submit fails anyway -- the second
    attempt finds the room taken by the first. That is safe but reads as
    "Room 304 is already booked", which is baffling when the guest looking at
    it is the one who just booked it. Recognising the retry and handing back
    the original booking is the honest answer.
    """
    cutoff = datetime.now() - timedelta(seconds=REPLAY_WINDOW_SECONDS)
    candidates = (
        db.query(models.RoomReservation)
        .filter(
            models.RoomReservation.company_id == str(company_id),
            models.RoomReservation.status == STATUS,
            models.RoomReservation.phone_number == phone_number,
            models.RoomReservation.arrival_date == arrival,
            models.RoomReservation.departure_date == departure,
            models.RoomReservation.created_at >= cutoff,
        )
        .order_by(models.RoomReservation.id.desc())
        .limit(5)
        .all()
    )
    wanted = sorted(room_ids)
    for candidate in candidates:
        existing = sorted(int(r) for r in (candidate.room_ids or []))
        if existing == wanted:
            return candidate
    return None


# Values as the room master already spells them (see the seeded `room` rows and
# TableTemplate's badge vocabulary) — not a new set invented here.
AVAILABLE_FLAG = "Available"
RESERVED_FLAG = "Reserved"
OCCUPIED_FLAG = "Occupied"


# HOW A PAYMENT IS TIED TO ITS RESERVATION
#
# `reservation_amount_paid_history.reservation_id` is a String column, and the
# two things that write it disagreed about what goes in it. The seeded and
# client data hold the booking REFERENCE ("RES-2026-0001"); the code wrote the
# numeric primary key ("1") and then read back by that same numeric key. So
# every payment recorded before this point was invisible to the endpoint that
# lists it: a reservation showed 15,680 paid and an empty payment history
# beside it, with no error anywhere to say why.
#
# Writes now use the reference, matching the data already in the table. Reads
# accept either, so rows written by the previous code are not orphaned by the
# correction. Neither changes the schema, so no migration is needed and no
# existing row is rewritten.


def _history_keys(reservation) -> list[str]:
    """Every value this reservation's payment rows might be keyed by."""
    keys = [str(reservation.id)]
    if reservation.room_reservation_id:
        keys.append(str(reservation.room_reservation_id))
    return keys


def _history_key(reservation) -> str:
    """What a new payment row is keyed by: the booking reference."""
    return str(reservation.room_reservation_id or reservation.id)


def sync_room_booking_status(db: Session, company_id, room_ids=None) -> None:
    """Recompute the property's room occupancy flags from its reservations.

    `room.Room_Booking_status` is what the Room View board, the Master Data
    room list and -- importantly -- the Dashboard's occupancy figures all read,
    and nothing ever wrote it back. A room flagged Occupied by a stay that
    ended in July was still flagged Occupied in August, so the board and the
    occupancy percentage were both reporting a hotel that no longer existed.

    THE WHOLE PROPERTY, NOT JUST THE ROOMS THAT CHANGED
        Reconciling only the affected rooms would leave the flags that are
        already wrong wrong forever, because nothing will ever touch those
        rooms again to correct them. A property has tens of rooms, not
        millions; recomputing all of them costs two indexed queries and makes
        the board self-healing on the next booking.

    Occupied beats Reserved: a checked-in guest is in the room today, which is
    a stronger statement than a booking that starts next week.

    `room_ids` is accepted so call sites can document which rooms prompted the
    reconcile, and is deliberately not used to narrow it.
    """
    today = date.today()

    rooms = {
        r.id: r
        for r in db.query(MasterRoom)
        .filter(
            MasterRoom.company_id == str(company_id),
            MasterRoom.status == STATUS,
        )
        .all()
    }
    if not rooms:
        return

    # Every reservation that can still say something about a room right now:
    # one that runs to today or beyond, and -- separately -- any guest who is
    # checked in. The second half matters for an overstay: a guest still in
    # the room after their departure date has passed is exactly the case where
    # dropping the row would hand their room to somebody else.
    live = (
        db.query(models.RoomReservation)
        .filter(
            models.RoomReservation.company_id == str(company_id),
            models.RoomReservation.status == STATUS,
            or_(
                models.RoomReservation.departure_date >= today,
                models.RoomReservation.reservation_status == rules.CHECKED_IN,
            ),
        )
        .all()
    )

    terminal = {rules.normalise_status(s) for s in rules.TERMINAL}

    occupied: set[int] = set()
    reserved: set[int] = set()
    for reservation in live:
        # Terminal covers all three ways a stay stops holding a room *now*:
        # cancelled, no-show, and checked out. A guest who has departed does
        # not make the room Reserved just because the booking ran to Friday --
        # that was the shape of the original bug, where nothing ever cleared
        # the flag and rooms stayed Occupied months after the guest left.
        if rules.normalise_status(reservation.reservation_status) in terminal:
            continue
        # Inclusive of the departure date: a guest who has not checked out yet
        # is still in the room on the morning they are due to leave. The
        # half-open comparison that is correct for *availability* (so the next
        # guest can book that night) is the wrong one for *occupancy*.
        is_here_now = rules.normalise_status(
            reservation.reservation_status
        ) == rules.normalise_status(rules.CHECKED_IN) and (
            reservation.arrival_date <= today
        )
        for raw_id in reservation.room_ids or []:
            try:
                room_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            if room_id not in rooms:
                continue
            (occupied if is_here_now else reserved).add(room_id)

    for room_id, room in rooms.items():
        if room_id in occupied:
            wanted = OCCUPIED_FLAG
        elif room_id in reserved:
            wanted = RESERVED_FLAG
        else:
            wanted = AVAILABLE_FLAG
        if room.Room_Booking_status != wanted:
            room.Room_Booking_status = wanted


# ---------------------------------------------------------------------------
# Response shaping
# ---------------------------------------------------------------------------
def _lookup_maps(db: Session, company_id) -> dict:
    """Name lookups so a reservation can be returned with labels, not raw ids.

    The list and detail payloads used to carry `payment_method_id: 2` and
    `tax_type_id: 3` and nothing else, so every screen re-fetched all seven
    master endpoints purely to turn them back into words -- and the print
    receipt, which had no such lookup, printed the digit.
    """
    rooms = {
        r.id: r
        for r in db.query(MasterRoom)
        .filter(MasterRoom.company_id == str(company_id))
        .all()
    }
    room_types = {
        t.id: t
        for t in db.query(MasterRoomType)
        .filter(MasterRoomType.company_id == str(company_id))
        .all()
    }
    payment_methods = {
        p.id: p.payment_method
        for p in db.query(MasterPaymentMethod)
        .filter(MasterPaymentMethod.company_id == str(company_id))
        .all()
    }
    taxes = {
        t.id: t.Tax_Name
        for t in db.query(MasterTaxType)
        .filter(MasterTaxType.company_id == str(company_id))
        .all()
    }
    discounts = {
        d.id: d.Discount_Name
        for d in db.query(MasterDiscount)
        .filter(MasterDiscount.company_id == str(company_id))
        .all()
    }
    identities = {
        i.id: i.Proof_Name
        for i in db.query(MasterIdentityProof)
        .filter(MasterIdentityProof.company_id == str(company_id))
        .all()
    }
    statuses = {
        s.id: s
        for s in db.query(MasterReservationStatus)
        .filter(MasterReservationStatus.company_id == str(company_id))
        .all()
    }
    return {
        "rooms": rooms,
        "room_types": room_types,
        "payment_methods": payment_methods,
        "taxes": taxes,
        "discounts": discounts,
        "identities": identities,
        "statuses": statuses,
    }


def _payment_state(reservation) -> str:
    """Unpaid | Partly paid | Paid — derived, never stored."""
    overall = rules.money(reservation.overall_amount)
    paid = rules.money(reservation.paid_amount)
    if overall <= 0:
        return "Paid"
    if paid <= 0:
        return "Unpaid"
    if paid + 0.01 >= overall:
        return "Paid"
    return "Partly paid"


def _serialise(reservation, maps: dict) -> dict:
    """One reservation as the API returns it.

    Every raw id it always carried is still here -- the edit form binds to
    them, and removing one would break a client mid-upgrade. The `*_name`
    fields alongside them are what a table or a receipt should render.
    """
    room_ids = [int(r) for r in (reservation.room_ids or []) if str(r).strip() != ""]
    room_type_ids = [
        int(t) for t in (reservation.room_type_ids or []) if str(t).strip() != ""
    ]

    rooms = maps["rooms"]
    room_types = maps["room_types"]
    status_row = maps["statuses"].get(reservation.booking_status_id)

    return {
        # ---------------- Reference ----------------
        "id": reservation.id,
        "room_reservation_id": reservation.room_reservation_id,
        # ---------------- Guest Details ----------------
        "salutation": reservation.salutation,
        "first_name": reservation.first_name,
        "last_name": reservation.last_name,
        "guest_name": " ".join(
            p for p in [reservation.first_name, reservation.last_name] if p
        ).strip()
        or None,
        "phone_number": reservation.phone_number,
        "email": reservation.email,
        # ---------------- Stay Details ----------------
        "arrival_date": reservation.arrival_date,
        "departure_date": reservation.departure_date,
        "no_of_nights": reservation.no_of_nights,
        # ---------------- Room Details ----------------
        "room_type_ids": room_type_ids,
        "room_ids": room_ids,
        "room_nos": [
            rooms[r].Room_No for r in room_ids if r in rooms
        ],
        "room_type_names": [
            room_types[t].Type_Name for t in room_type_ids if t in room_types
        ],
        "rate_type": reservation.rate_type or [],
        "no_of_rooms": reservation.no_of_rooms,
        "no_of_adults": reservation.no_of_adults,
        "no_of_children": reservation.no_of_children,
        # ---------------- Payment ----------------
        "payment_method_id": reservation.payment_method_id,
        "payment_method": maps["payment_methods"].get(reservation.payment_method_id),
        "extra_bed_count": reservation.extra_bed_count,
        "extra_bed_cost": reservation.extra_bed_cost,
        "room_amount": reservation.room_amount,
        "tax_type_id": reservation.tax_type_id,
        "tax_name": maps["taxes"].get(reservation.tax_type_id),
        "total_amount": reservation.total_amount,
        "tax_percentage": reservation.tax_percentage,
        "tax_amount": reservation.tax_amount,
        "discount_type_id": reservation.discount_type_id,
        "discount_name": maps["discounts"].get(reservation.discount_type_id),
        "discount_percentage": reservation.discount_percentage,
        "discount_amount": reservation.discount_amount,
        "extra_charges": reservation.extra_charges,
        "overall_amount": reservation.overall_amount,
        "paying_amount": reservation.paying_amount,
        "paid_amount": reservation.paid_amount,
        "balance_amount": reservation.balance_amount,
        "extra_amount": reservation.extra_amount,
        "payment_state": _payment_state(reservation),
        # ---------------- Reservation Info ----------------
        "booking_status_id": reservation.booking_status_id,
        "reservation_type": reservation.reservation_type,
        "reservation_status": reservation.reservation_status,
        "status_color": getattr(status_row, "Color", None),
        "room_complementary": reservation.room_complementary,
        "common_complementary": reservation.common_complementary,
        # ---------------- Identity ----------------
        "identity_type_id": reservation.identity_type_id,
        "identity_type": maps["identities"].get(reservation.identity_type_id),
        "proof_document": reservation.proof_document,
        "confirmation_code": reservation.confirmation_code,
        # ---------------- Cancellation ----------------
        # Null on a booking cancelled before the reason was recorded, and on
        # every booking that was never cancelled. Readers distinguish the two
        # by the status, not by this field.
        "cancellation_reason": reservation.cancellation_reason,
        "cancelled_at": reservation.cancelled_at,
        "cancelled_by": reservation.cancelled_by,
        # ---------------- Lifecycle ----------------
        # What the UI is allowed to offer on this row. Derived from the same
        # transition table the API enforces, so a button can never appear for
        # an action the server would refuse.
        # `can_transition` answers "is this move legal", and it treats staying
        # put as legal -- an edit that does not change the status must not be
        # refused. That makes it the wrong question on its own for a BUTTON:
        # asked directly, it said a cancelled booking could be cancelled, so
        # the View modal offered "Cancel reservation" on a reservation that
        # was already cancelled. `_can_move_to` adds the missing half: the
        # action is offered only when it would actually change something.
        "can_check_in": rules.can_offer(reservation.reservation_status, rules.CHECKED_IN),
        "can_check_out": rules.normalise_status(reservation.reservation_status)
        == rules.normalise_status(rules.CHECKED_IN),
        "can_cancel": rules.can_offer(reservation.reservation_status, rules.CANCELLED),
        "can_mark_no_show": rules.can_offer(reservation.reservation_status, rules.NO_SHOW),
        "is_terminal": rules.normalise_status(reservation.reservation_status)
        in {rules.normalise_status(s) for s in rules.TERMINAL},
        # ---------------- System ----------------
        "token": reservation.token,
        "status": reservation.status,
        "created_by": reservation.created_by,
        "created_at": reservation.created_at,
        "updated_at": reservation.updated_at,
        "updated_by": reservation.updated_by,
        "company_id": reservation.company_id,
    }


# =====================================================
# PRICE A STAY WITHOUT BOOKING IT
# =====================================================
@router.post("/room_reservation_quote", status_code=status.HTTP_200_OK)
async def quote_reservation(request: Request, db: Session = Depends(get_db)):
    """What a stay would cost, priced by the same code that books it.

    The Add Reservation and Edit screens call this instead of doing arithmetic
    of their own. That is the point: the figures the guest is shown before
    confirming are produced by the server that will store them, so the summary
    and the saved booking cannot disagree.
    """
    user_id, role_id, company_id, _ = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    try:
        arrival = _coerce_date(payload.get("arrival_date"), "arrival_date")
        departure = _coerce_date(payload.get("departure_date"), "departure_date")
        _assert_stay_dates(arrival, departure, allow_past=True)
        nights = rules.nights_between(arrival, departure)

        room_ids = [int(r) for r in (payload.get("room_ids") or [])]
        if not room_ids:
            raise rules.RuleError("Select at least one room")

        priced = rules.quote(
            db,
            company_id,
            room_ids=room_ids,
            rate_types=[str(r) for r in (payload.get("rate_type") or [])],
            nights=nights,
            tax_type_id=payload.get("tax_type_id"),
            discount_type_id=payload.get("discount_type_id"),
            extra_charges=payload.get("extra_charges") or 0,
            extra_bed_count=payload.get("extra_bed_count") or 0,
            extra_bed_cost=payload.get("extra_bed_cost"),
            room_amount_override=payload.get("room_amount"),
            paying_amount=payload.get("paying_amount") or 0,
        )
    except rules.RuleError as exc:
        raise _rule_http(exc)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="room_ids must contain only room ids")

    return {"status": "success", "data": priced}


def _coerce_date(value, field: str) -> date:
    if isinstance(value, date):
        return value
    if not value:
        raise HTTPException(status_code=400, detail=f"{field} is required")
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"{field} must be a date in YYYY-MM-DD form"
        )


def _assert_stay_dates(arrival: date, departure: date, *, allow_past: bool = False) -> None:
    """The stay itself has to make sense before anything else is considered."""
    if departure <= arrival:
        raise HTTPException(
            status_code=400,
            detail="Departure date must be after arrival date",
        )

    nights = rules.nights_between(arrival, departure)
    if nights > MAX_STAY_NIGHTS:
        raise HTTPException(
            status_code=400,
            detail=f"A stay cannot exceed {MAX_STAY_NIGHTS} nights",
        )

    if not allow_past:
        earliest = date.today() - timedelta(days=MAX_BACKDATE_DAYS)
        if arrival < earliest:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Arrival date is too far in the past. "
                    f"The earliest bookable arrival is {earliest.isoformat()}."
                ),
            )


# =====================================================
# CREATE ROOM RESERVATION
# =====================================================
@router.post("/room_reservation", status_code=status.HTTP_201_CREATED)
async def create_room_reservation(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    # ---------------- Guest ----------------
    salutation: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone_number: str = Form(...),
    email: str = Form(None),
    # ---------------- Stay ----------------
    arrival_date: date = Form(...),
    departure_date: date = Form(...),
    room_ids: str = Form(...),           # JSON -> [101, 102]
    rate_type: str = Form(None),         # JSON -> ["daily", "weekly"]
    room_occupancy: str = Form(None),    # JSON -> [{room_id, adults, children}]
    no_of_adults: int = Form(None),
    no_of_children: int = Form(None),
    # ---------------- Pricing inputs ----------------
    payment_method_id: int = Form(...),
    tax_type_id: int = Form(None),
    discount_type_id: int = Form(None),
    extra_charges: float = Form(0),
    extra_bed_count: int = Form(0),
    extra_bed_cost: float = Form(None),
    room_amount: float = Form(None),     # negotiated rate; optional override
    paying_amount: float = Form(0),
    # ---------------- Reservation ----------------
    booking_status_id: int = Form(None),
    reservation_type: str = Form(RESERVATION),
    reservation_status: str = Form(None),
    room_complementary: str = Form(None),
    common_complementary: str = Form(None),
    # ---------------- Identity ----------------
    identity_type_id: int = Form(...),
    identity_file: UploadFile = File(...),
):
    """Create a reservation.

    WHAT THE CALLER NO LONGER DECIDES
        `room_reservation_id`, `no_of_nights`, `no_of_rooms`, `room_type_ids`,
        `tax_percentage`, `tax_amount`, `discount_percentage`,
        `discount_amount`, `overall_amount`, `total_amount`, `paid_amount` and
        `balance_amount` were all form fields. Every one of them is now derived
        here. They are still accepted -- an older client posting them gets a
        booking rather than a 422 -- and ignored.

    WHY IT IS ONE TRANSACTION
        Locking the rooms, re-checking availability against that lock and
        inserting the booking have to be indivisible. Split across commits (as
        this used to be) the gap between "the room is free" and "the room is
        mine" is exactly where a second booker fits.
    """
    user_id, role_id, company_id, _ = verify_authentication(request)
    if not user_id or not company_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    phone_number = (phone_number or "").strip()
    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")
    if not (first_name or "").strip():
        raise HTTPException(status_code=400, detail="Guest first name is required")

    _assert_stay_dates(arrival_date, departure_date)
    nights = rules.nights_between(arrival_date, departure_date)

    parsed_room_ids = _parse_room_ids(room_ids)
    rate_types = [str(r) for r in _parse_json_list(rate_type, "rate_type", default=[])]
    occupancy = _parse_occupancy(
        room_occupancy, parsed_room_ids, no_of_adults, no_of_children
    )

    if reservation_type and reservation_type.upper() not in rules.RESERVATION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Reservation type must be one of: {', '.join(rules.RESERVATION_TYPES)}",
        )
    reservation_type = (reservation_type or RESERVATION).upper()

    try:
        # A status may be named directly or picked by its master-data id; the
        # Add screen sends the id, the Edit screen sends the label.
        wanted_status = reservation_status
        if not wanted_status and booking_status_id:
            status_row = (
                db.query(MasterReservationStatus)
                .filter(
                    MasterReservationStatus.id == booking_status_id,
                    MasterReservationStatus.company_id == str(company_id),
                    MasterReservationStatus.status == STATUS,
                )
                .first()
            )
            if not status_row:
                raise rules.RuleError(
                    f"Reservation status {booking_status_id} does not exist for this property"
                )
            wanted_status = status_row.Reservation_Status

        resolved_status = rules.resolve_status(db, company_id, wanted_status)

        # Opening a booking directly in a terminal state is a data-entry error,
        # not a workflow: it would occupy a reference and a reference number for
        # a stay that never existed.
        if rules.normalise_status(resolved_status) in {
            rules.normalise_status(s) for s in rules.TERMINAL
        }:
            raise rules.RuleError(
                f"A new reservation cannot start as {resolved_status}"
            )

        status_id = (
            db.query(MasterReservationStatus.id)
            .filter(
                MasterReservationStatus.company_id == str(company_id),
                MasterReservationStatus.Reservation_Status == resolved_status,
                MasterReservationStatus.status == STATUS,
            )
            .scalar()
        )

        rules.resolve_payment_method(db, payment_method_id, company_id)
        rules.resolve_identity_type(db, identity_type_id, company_id)

        # ---- Retry of a booking already made? Answer with that one. --------
        replay = _find_replay(
            db,
            company_id,
            phone_number=phone_number,
            arrival=arrival_date,
            departure=departure_date,
            room_ids=parsed_room_ids,
        )
        if replay:
            response.status_code = status.HTTP_200_OK
            return {
                "status": "success",
                "message": "This reservation was already created",
                "idempotent_replay": True,
                "data": {
                    "id": replay.id,
                    "room_reservation_id": replay.room_reservation_id,
                    "token": replay.token,
                    "confirmation_code": replay.confirmation_code,
                },
            }

        # ---- Serialise every booker competing for these rooms --------------
        rules.lock_rooms(db, parsed_room_ids)

        rooms = rules.assert_rooms_bookable(
            db,
            company_id,
            parsed_room_ids,
            arrival_date,
            departure_date,
            occupancy=occupancy,
        )

        priced = rules.quote(
            db,
            company_id,
            room_ids=parsed_room_ids,
            rate_types=rate_types,
            nights=nights,
            tax_type_id=tax_type_id,
            discount_type_id=discount_type_id,
            extra_charges=extra_charges,
            extra_bed_count=extra_bed_count,
            extra_bed_cost=extra_bed_cost,
            room_amount_override=room_amount,
            paying_amount=paying_amount,
        )
    except rules.RuleError as exc:
        db.rollback()
        raise _rule_http(exc)

    # The upload is written only once the booking is known to be valid, so a
    # rejected request leaves no orphan file behind.
    proof_document = await _store_identity_proof(identity_file)

    reservation = models.RoomReservation()
    reservation.room_reservation_id = _generate_reservation_reference(db, company_id)

    reservation.salutation = salutation
    reservation.first_name = (first_name or "").strip()
    reservation.last_name = (last_name or "").strip() or None
    reservation.phone_number = phone_number
    reservation.email = (email or "").strip().lower() or None

    reservation.arrival_date = arrival_date
    reservation.departure_date = departure_date
    reservation.no_of_nights = nights

    reservation.room_ids = parsed_room_ids
    reservation.room_type_ids = sorted(
        {rules.as_int(rooms[r].Room_Type_ID) for r in parsed_room_ids}
    )
    reservation.room_no = [rooms[r].Room_No for r in parsed_room_ids]
    reservation.rate_type = [
        line["rate_type"] for line in priced["lines"]
    ] or [rules.DEFAULT_RATE_TYPE]

    reservation.no_of_rooms = len(parsed_room_ids)
    reservation.no_of_adults = sum(a for a, _ in occupancy.values())
    reservation.no_of_children = sum(c for _, c in occupancy.values())

    reservation.payment_method_id = payment_method_id
    rules.apply_quote(reservation, priced)
    reservation.paying_amount = priced["paying_amount"]
    reservation.paid_amount = priced["paid_amount"]
    reservation.balance_amount = priced["balance_amount"]
    reservation.extra_amount = priced["extra_amount"]

    reservation.booking_status_id = status_id
    reservation.reservation_type = reservation_type
    reservation.reservation_status = resolved_status

    reservation.room_complementary = (room_complementary or "").strip() or None
    reservation.common_complementary = (common_complementary or "").strip() or None

    reservation.identity_type_id = identity_type_id
    reservation.proof_document = proof_document

    reservation.confirmation_code = str(uuid.uuid4())[:8].upper()
    reservation.status = STATUS
    reservation.created_by = str(user_id)
    reservation.company_id = str(company_id)

    db.add(reservation)
    db.flush()

    # An opening payment is part of the booking, so it belongs to the same
    # transaction and the same audit trail as every later one.
    if priced["paid_amount"] > 0:
        db.add(
            models.ReservationAmountPaidHistory(
                reservation_id=_history_key(reservation),
                user_id=str(user_id),
                amount=priced["paid_amount"],
                paid_date=date.today(),
                payment_method=_payment_method_name(db, company_id, payment_method_id),
                status=STATUS,
                created_by=str(user_id),
                company_id=str(company_id),
            )
        )

    sync_room_booking_status(db, company_id, parsed_room_ids)

    try:
        db.commit()
    except IntegrityError:
        # The unique index on the reference is the last line of defence behind
        # `_generate_reservation_reference`; report the collision rather than
        # letting it surface as an opaque 500.
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="That reservation reference is already in use; please retry",
        )
    db.refresh(reservation)

    return {
        "status": "success",
        "message": "Room reservation created successfully",
        "data": {
            "id": reservation.id,
            "room_reservation_id": reservation.room_reservation_id,
            "token": reservation.token,
            "confirmation_code": reservation.confirmation_code,
            "reservation_status": reservation.reservation_status,
            "no_of_nights": reservation.no_of_nights,
            "room_amount": reservation.room_amount,
            "tax_amount": reservation.tax_amount,
            "discount_amount": reservation.discount_amount,
            "overall_amount": reservation.overall_amount,
            "paid_amount": reservation.paid_amount,
            "balance_amount": reservation.balance_amount,
        },
    }


def _payment_method_name(db: Session, company_id, payment_method_id) -> str:
    row = (
        db.query(MasterPaymentMethod.payment_method)
        .filter(
            MasterPaymentMethod.id == payment_method_id,
            MasterPaymentMethod.company_id == str(company_id),
        )
        .scalar()
    )
    return row or "Unknown"


# =====================================================
# CHECK ROOM AVAILABILITY FOR A DATE RANGE
# =====================================================
@router.get("/room_availability", status_code=status.HTTP_200_OK)
def get_room_availability(
    request: Request,
    arrival_date: date,
    departure_date: date,
    db: Session = Depends(get_db),
    exclude_reservation_id: int = None,
):
    """Which rooms can be sold for a stay, and which cannot, and why.

    `exclude_reservation_id` is what makes editing a booking work: a
    reservation must not be told its own room is unavailable when the guest is
    simply changing the dates around it.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        _assert_stay_dates(arrival_date, departure_date, allow_past=True)

        conflicts = rules.booked_room_windows(
            db,
            company_id,
            arrival_date,
            departure_date,
            exclude_id=exclude_reservation_id,
        )

        rooms = (
            db.query(MasterRoom)
            .filter(
                MasterRoom.company_id == str(company_id),
                MasterRoom.status == STATUS,
            )
            .order_by(MasterRoom.id.asc())
            .all()
        )

        blocked_ids = {
            r.id for r in rooms if rules.normalise_status(r.Room_Status) == "blocking"
        }

        nights = rules.nights_between(arrival_date, departure_date)
        available = [
            r.id
            for r in rooms
            if r.id not in conflicts and r.id not in blocked_ids
        ]

        return {
            "status": "success",
            "data": {
                "arrival_date": arrival_date,
                "departure_date": departure_date,
                "no_of_nights": nights,
                "booked_room_ids": sorted(conflicts.keys()),
                # Out of order for maintenance. Reported separately from
                # `booked_room_ids` so the UI can say why rather than showing
                # one undifferentiated "unavailable".
                "blocked_room_ids": sorted(blocked_ids),
                "available_room_ids": available,
                "conflicts": {
                    room_id: [
                        {"arrival_date": s, "departure_date": e} for s, e in windows
                    ]
                    for room_id, windows in conflicts.items()
                },
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("room_availability_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# =====================================================
# GET ALL ROOM RESERVATIONS
# =====================================================
@router.get("/room_reservation", status_code=status.HTTP_200_OK)
def get_all_room_reservations(
    request: Request,
    db: Session = Depends(get_db),
    q: str = None,
    reservation_status: str = None,
    reservation_type: str = None,
    room_id: int = None,
    room_type_id: int = None,
    payment_state: str = None,
    from_date: date = None,
    to_date: date = None,
    page: int = 1,
    page_size: int = None,
):
    """List reservations, filtered and paged by the database.

    Filtering happens here rather than in the browser because the browser only
    ever had the rows it had already downloaded -- a "Cancelled" filter over an
    un-paged list is a different answer from the same filter over the whole
    book. `page_size` is opt-in so an unparameterised call keeps returning the
    complete list, which is what the existing screens expect.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        query = db.query(models.RoomReservation).filter(
            models.RoomReservation.company_id == str(company_id),
            models.RoomReservation.status == STATUS,
        )

        if reservation_status:
            # Fold-insensitive so "no-show" from a URL matches "No-Show".
            wanted = rules.normalise_status(reservation_status)
            labels = [
                label
                for label in rules.load_status_vocabulary(db, company_id)
                if rules.normalise_status(label) == wanted
            ]
            query = query.filter(
                models.RoomReservation.reservation_status.in_(labels or [reservation_status])
            )

        if reservation_type:
            query = query.filter(
                models.RoomReservation.reservation_type == reservation_type.upper()
            )

        # Date filtering is on stay overlap, not on the arrival date alone: a
        # guest already in-house on the date being asked about is part of that
        # day's picture even though they arrived last week.
        if from_date:
            query = query.filter(models.RoomReservation.departure_date >= from_date)
        if to_date:
            query = query.filter(models.RoomReservation.arrival_date <= to_date)

        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    models.RoomReservation.room_reservation_id.like(term),
                    models.RoomReservation.confirmation_code.like(term),
                    models.RoomReservation.first_name.like(term),
                    models.RoomReservation.last_name.like(term),
                    models.RoomReservation.phone_number.like(term),
                    models.RoomReservation.email.like(term),
                )
            )

        rows = query.order_by(models.RoomReservation.id.desc()).all()

        # room_ids / room_type_ids are JSON arrays, so these two are matched in
        # Python. Portable across MySQL versions, and the alternative --
        # JSON_CONTAINS -- cannot use an index here either.
        if room_id is not None:
            rows = [r for r in rows if room_id in [int(x) for x in (r.room_ids or [])]]
        if room_type_id is not None:
            rows = [
                r
                for r in rows
                if room_type_id in [int(x) for x in (r.room_type_ids or [])]
            ]

        if payment_state:
            wanted = payment_state.strip().lower()
            rows = [r for r in rows if _payment_state(r).lower() == wanted]

        total = len(rows)

        if page_size:
            page = max(1, int(page or 1))
            page_size = max(1, min(int(page_size), 200))
            start = (page - 1) * page_size
            rows = rows[start : start + page_size]

        maps = _lookup_maps(db, company_id)
        data = [_serialise(r, maps) for r in rows]

        return {
            "status": "success",
            "count": len(data),
            "total": total,
            "page": page if page_size else 1,
            "page_size": page_size or total,
            "data": data,
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("list_reservations_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# =====================================================
# GET ROOM RESERVATION BY ID
# =====================================================
@router.get("/room_reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def get_room_reservation_by_id(
    reservation_id: int, request: Request, db: Session = Depends(get_db)
):
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        if reservation_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid reservation id")

        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == reservation_id,
                models.RoomReservation.company_id == str(company_id),
                models.RoomReservation.status == STATUS,
            )
            .first()
        )
        if not reservation:
            raise HTTPException(status_code=404, detail="Room reservation not found")

        maps = _lookup_maps(db, company_id)
        payload = _serialise(reservation, maps)

        # The per-room breakdown behind the total, so the View screen can show
        # what each room contributed instead of one opaque figure.
        payload["rate_breakdown"] = _rate_breakdown(reservation, maps)

        return {"status": "success", "data": payload}

    except HTTPException:
        raise
    except Exception:
        logger.exception("get_reservation_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


def _rate_breakdown(reservation, maps: dict) -> list[dict]:
    """Reconstruct the per-room lines from what was stored.

    Read from the reservation rather than re-priced from today's rate card: a
    stay booked in July at July's rates must keep showing July's rates.
    """
    rooms = maps["rooms"]
    room_types = maps["room_types"]
    room_ids = [int(r) for r in (reservation.room_ids or [])]
    rate_types = list(reservation.rate_type or [])
    nights = reservation.no_of_nights or 1

    lines = []
    for index, room_id in enumerate(room_ids):
        room = rooms.get(room_id)
        if not room:
            continue
        room_type = room_types.get(rules.as_int(room.Room_Type_ID))
        rate = rate_types[index] if index < len(rate_types) else rules.DEFAULT_RATE_TYPE
        lines.append(
            {
                "room_id": room_id,
                "room_no": room.Room_No,
                "room_type_name": getattr(room_type, "Type_Name", None),
                "rate_type": rate,
                "units": rules.units_for(rate, nights),
            }
        )
    return lines


# =====================================================
# UPDATE ROOM RESERVATION
# =====================================================
@router.put("/room_reservation", status_code=status.HTTP_200_OK)
async def update_room_reservation(
    request: Request,
    db: Session = Depends(get_db),
    id: int = Form(...),
    # ---------------- Guest ----------------
    salutation: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone_number: str = Form(...),
    email: str = Form(None),
    # ---------------- Stay ----------------
    arrival_date: date = Form(...),
    departure_date: date = Form(...),
    room_ids: str = Form(None),
    rate_type: str = Form(None),
    room_occupancy: str = Form(None),
    no_of_adults: int = Form(None),
    no_of_children: int = Form(None),
    # ---------------- Pricing inputs ----------------
    payment_method_id: int = Form(...),
    tax_type_id: int = Form(None),
    discount_type_id: int = Form(None),
    extra_charges: float = Form(0),
    extra_bed_count: int = Form(0),
    extra_bed_cost: float = Form(None),
    room_amount: float = Form(None),
    # ---------------- Reservation ----------------
    booking_status_id: int = Form(None),
    reservation_type: str = Form(None),
    reservation_status: str = Form(None),
    room_complementary: str = Form(None),
    common_complementary: str = Form(None),
):
    """Amend a reservation, re-checking everything the amendment could break.

    An edit is a booking all over again: moving the dates or the room has to
    pass the same availability check the original did, and changing the rate
    type or the discount has to re-derive the total. The previous version
    assigned whatever arrived and committed, so a reservation could be edited
    into a room somebody else was already in, and its total could be set by
    typing a different number into the form.

    `paid_amount` and `balance_amount` are deliberately NOT editable here.
    Money that has changed hands is recorded by the payment and refund
    endpoints, which write an audit row; letting the edit form overwrite the
    paid figure would silently erase that history.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if id <= 0:
            raise HTTPException(status_code=400, detail="Invalid reservation id")

        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == id,
                models.RoomReservation.company_id == str(company_id),
                models.RoomReservation.status == STATUS,
            )
            .first()
        )
        if not reservation:
            raise HTTPException(status_code=404, detail="Room reservation not found")

        previous_status = reservation.reservation_status
        previous_rooms = [int(r) for r in (reservation.room_ids or [])]

        # A finished or abandoned stay is a historical record. Editing one
        # would rewrite revenue that has already been reported.
        if rules.normalise_status(previous_status) in {
            rules.normalise_status(s) for s in rules.TERMINAL
        }:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"This reservation is {previous_status} and can no longer be edited."
                ),
            )

        phone_number = (phone_number or "").strip()
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        if not (first_name or "").strip():
            raise HTTPException(status_code=400, detail="Guest first name is required")

        # Back-dating is allowed on an edit: a booking made last week for last
        # week's arrival is legitimately still being corrected.
        _assert_stay_dates(arrival_date, departure_date, allow_past=True)
        nights = rules.nights_between(arrival_date, departure_date)

        parsed_room_ids = (
            _parse_room_ids(room_ids) if room_ids not in (None, "") else previous_rooms
        )
        if not parsed_room_ids:
            raise HTTPException(status_code=400, detail="Select at least one room")

        rate_types = [
            str(r) for r in _parse_json_list(rate_type, "rate_type", default=[])
        ] or list(reservation.rate_type or [])

        occupancy = _parse_occupancy(
            room_occupancy,
            parsed_room_ids,
            no_of_adults if no_of_adults is not None else reservation.no_of_adults,
            no_of_children if no_of_children is not None else reservation.no_of_children,
        )

        if reservation_type and reservation_type.upper() not in rules.RESERVATION_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Reservation type must be one of: {', '.join(rules.RESERVATION_TYPES)}",
            )

        wanted_status = reservation_status
        if not wanted_status and booking_status_id:
            status_row = (
                db.query(MasterReservationStatus)
                .filter(
                    MasterReservationStatus.id == booking_status_id,
                    MasterReservationStatus.company_id == str(company_id),
                    MasterReservationStatus.status == STATUS,
                )
                .first()
            )
            wanted_status = getattr(status_row, "Reservation_Status", None)

        resolved_status = rules.resolve_status(
            db, company_id, wanted_status or previous_status
        )
        rules.assert_transition(previous_status, resolved_status)

        rules.resolve_payment_method(db, payment_method_id, company_id)

        # Serialise against concurrent bookers for both the rooms being taken
        # and the ones being released.
        rules.lock_rooms(db, set(parsed_room_ids) | set(previous_rooms))

        rooms = rules.assert_rooms_bookable(
            db,
            company_id,
            parsed_room_ids,
            arrival_date,
            departure_date,
            exclude_id=reservation.id,
            occupancy=occupancy,
        )

        priced = rules.quote(
            db,
            company_id,
            room_ids=parsed_room_ids,
            rate_types=rate_types,
            nights=nights,
            tax_type_id=tax_type_id,
            discount_type_id=discount_type_id,
            extra_charges=extra_charges,
            extra_bed_count=extra_bed_count,
            extra_bed_cost=extra_bed_cost,
            room_amount_override=room_amount,
            # Re-pricing must not disturb what has actually been collected.
            paying_amount=rules.money(reservation.paid_amount),
        )

    except rules.RuleError as exc:
        db.rollback()
        raise _rule_http(exc)
    except HTTPException:
        raise

    reservation.salutation = salutation
    reservation.first_name = (first_name or "").strip()
    reservation.last_name = (last_name or "").strip() or None
    reservation.phone_number = phone_number
    reservation.email = (email or "").strip().lower() or None

    reservation.arrival_date = arrival_date
    reservation.departure_date = departure_date
    reservation.no_of_nights = nights

    reservation.room_ids = parsed_room_ids
    reservation.room_type_ids = sorted(
        {rules.as_int(rooms[r].Room_Type_ID) for r in parsed_room_ids}
    )
    reservation.room_no = [rooms[r].Room_No for r in parsed_room_ids]
    reservation.rate_type = [line["rate_type"] for line in priced["lines"]] or [
        rules.DEFAULT_RATE_TYPE
    ]

    reservation.no_of_rooms = len(parsed_room_ids)
    reservation.no_of_adults = sum(a for a, _ in occupancy.values())
    reservation.no_of_children = sum(c for _, c in occupancy.values())

    reservation.payment_method_id = payment_method_id
    rules.apply_quote(reservation, priced)

    # Paid stands; the balance follows from the new total. An amendment that
    # reduces the bill below what was already paid turns the difference into a
    # refundable amount rather than a negative balance.
    reservation.balance_amount = priced["balance_amount"]
    reservation.extra_amount = priced["extra_amount"]

    if reservation_type:
        reservation.reservation_type = reservation_type.upper()
    reservation.reservation_status = resolved_status
    reservation.booking_status_id = (
        db.query(MasterReservationStatus.id)
        .filter(
            MasterReservationStatus.company_id == str(company_id),
            MasterReservationStatus.Reservation_Status == resolved_status,
            MasterReservationStatus.status == STATUS,
        )
        .scalar()
    )

    reservation.room_complementary = (room_complementary or "").strip() or None
    reservation.common_complementary = (common_complementary or "").strip() or None
    reservation.updated_by = str(user_id)

    # Both sets: rooms just released have to go back to Available.
    sync_room_booking_status(db, company_id, set(parsed_room_ids) | set(previous_rooms))

    db.commit()
    db.refresh(reservation)

    return {
        "status": "success",
        "message": "Room reservation updated successfully",
        "data": {
            "id": reservation.id,
            "room_reservation_id": reservation.room_reservation_id,
            "reservation_status": reservation.reservation_status,
            "no_of_nights": reservation.no_of_nights,
            "room_amount": reservation.room_amount,
            "tax_amount": reservation.tax_amount,
            "discount_amount": reservation.discount_amount,
            "overall_amount": reservation.overall_amount,
            "paid_amount": reservation.paid_amount,
            "balance_amount": reservation.balance_amount,
            "extra_amount": reservation.extra_amount,
            "updated_at": reservation.updated_at,
        },
    }


# =====================================================
# DELETE ROOM RESERVATION (SOFT DELETE)
# =====================================================
@router.delete("/room_reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def delete_room_reservation(
    reservation_id: int, request: Request, db: Session = Depends(get_db)
):
    """Remove a reservation from the book.

    Deleting is for a booking that should never have existed -- a test row, a
    duplicate. A guest who is not coming should be *cancelled*, which keeps the
    record and its money visible; that is what `/room_reservation_cancel` is
    for. The two are refused here because a soft delete hides the row from the
    reservation list, from search and from the revenue figures, and doing that
    to a stay that is under way or has been paid for loses real information.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        if reservation_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid reservation id")

        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == reservation_id,
                models.RoomReservation.company_id == str(company_id),
                models.RoomReservation.status == STATUS,
            )
            .first()
        )
        if not reservation:
            raise HTTPException(status_code=404, detail="Room reservation not found")

        if rules.normalise_status(reservation.reservation_status) in {
            rules.normalise_status(rules.CHECKED_IN),
            rules.normalise_status(rules.CHECKED_OUT),
        }:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"This guest is {reservation.reservation_status}, so the "
                    "reservation cannot be deleted. Check the guest out first."
                ),
            )

        if rules.money(reservation.paid_amount) > 0:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"{rules.money(reservation.paid_amount)} has been paid against this "
                    "reservation. Cancel it instead so the payment stays on record."
                ),
            )

        room_ids = [int(r) for r in (reservation.room_ids or [])]

        reservation.status = UNSTATUS
        reservation.updated_by = str(user_id)

        sync_room_booking_status(db, company_id, room_ids)
        db.commit()

        return {"status": "success", "message": "Room reservation deleted successfully"}

    except HTTPException:
        raise
    except Exception:
        logger.exception("delete_reservation_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# =====================================================
# STATUS TRANSITIONS
# =====================================================
def _load_by_token(db: Session, company_id, token: str):
    reservation = (
        db.query(models.RoomReservation)
        .filter(
            models.RoomReservation.token == token,
            models.RoomReservation.company_id == str(company_id),
            models.RoomReservation.status == STATUS,
        )
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


def _load_by_id_or_token(db: Session, company_id, key: str):
    """Accept either the numeric id or the token.

    Check-in was keyed by id and check-out by token, for no reason anyone
    recorded. Both work on both now so a caller does not have to remember
    which endpoint wants which.
    """
    if str(key).isdigit():
        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == int(key),
                models.RoomReservation.company_id == str(company_id),
                models.RoomReservation.status == STATUS,
            )
            .first()
        )
        if reservation:
            return reservation
    return _load_by_token(db, company_id, key)


def _apply_status(db: Session, reservation, company_id, user_id, target: str):
    """Move a reservation to `target`, enforcing the transition table."""
    resolved = rules.resolve_status(db, company_id, target)
    rules.assert_transition(reservation.reservation_status, resolved)

    reservation.reservation_status = resolved
    reservation.booking_status_id = (
        db.query(MasterReservationStatus.id)
        .filter(
            MasterReservationStatus.company_id == str(company_id),
            MasterReservationStatus.Reservation_Status == resolved,
            MasterReservationStatus.status == STATUS,
        )
        .scalar()
    )
    reservation.updated_by = str(user_id)
    return resolved


@router.post("/room_reservation_checkin/{key}")
def reservation_checkin(key: str, request: Request, db: Session = Depends(get_db)):
    """Arrive a guest.

    This endpoint did not work at all. It required `reservation_status ==
    "Booked"`, and "Booked" has never been one of this property's statuses --
    the master list is Confirmed / Checked-In / Checked-Out / Cancelled /
    No-Show / Pending / On Hold. Every check-in returned 400, and the frontend
    only drew the button for the same impossible status, so the failure was
    invisible. Which statuses may arrive is now the transition table's answer.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        reservation = _load_by_id_or_token(db, company_id, key)

        # Arriving before the booking starts is a real front-desk situation
        # (an early arrival), but arriving after it has ended is not.
        if reservation.departure_date <= date.today():
            raise HTTPException(
                status_code=409,
                detail=(
                    "This reservation's departure date has already passed; "
                    "amend the dates before checking the guest in."
                ),
            )

        _apply_status(db, reservation, company_id, user_id, rules.CHECKED_IN)
        sync_room_booking_status(
            db, company_id, [int(r) for r in (reservation.room_ids or [])]
        )
        db.commit()
        db.refresh(reservation)

        return {
            "status": "success",
            "message": "Check-in successful",
            "data": {
                "id": reservation.id,
                "reservation_status": reservation.reservation_status,
                "balance_amount": reservation.balance_amount,
            },
        }

    except rules.RuleError as exc:
        db.rollback()
        raise _rule_http(exc)
    except HTTPException:
        raise
    except Exception:
        logger.exception("checkin_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


def _early_checkout_position(db: Session, company_id, reservation) -> dict:
    """What the folio looks like if the guest leaves today.

    An early departure is two separate facts, and conflating them is how a
    system gets this wrong: the ROOM is free from today, and the BILL may or
    may not shrink. Whether it shrinks is policy -- a flexible rate refunds the
    unused nights, a non-refundable one does not -- and this module has no
    rate-plan configuration to read that from.

    So it computes both answers and decides neither. The desk is shown what
    each costs and picks; `adjust_stay` on the checkout call carries the
    choice. Nothing here writes.
    """
    today = date.today()
    booked_nights = reservation.no_of_nights or rules.nights_between(
        reservation.arrival_date, reservation.departure_date
    )

    is_early, actual_nights, nights_unused = rules.early_departure(
        reservation.arrival_date, reservation.departure_date, booked_nights, today
    )

    position = {
        "is_early": bool(is_early),
        "today": today,
        "arrival_date": reservation.arrival_date,
        "booked_departure_date": reservation.departure_date,
        "booked_nights": booked_nights,
        "actual_nights": actual_nights,
        "nights_unused": nights_unused,
        "current_total": rules.money(reservation.overall_amount),
        "paid_amount": rules.money(reservation.paid_amount),
        "balance_amount": rules.money(reservation.balance_amount),
    }

    if not is_early:
        position["repriced"] = None
        return position

    # Re-price the stay as if it had been booked for the nights actually used.
    # Every other input is held constant, so the only thing that moves is the
    # night count.
    try:
        priced = rules.quote(
            db,
            company_id,
            room_ids=[int(r) for r in (reservation.room_ids or [])],
            rate_types=list(reservation.rate_type or []),
            nights=actual_nights,
            tax_type_id=reservation.tax_type_id,
            discount_type_id=reservation.discount_type_id,
            extra_charges=reservation.extra_charges,
            extra_bed_count=reservation.extra_bed_count,
            paying_amount=rules.money(reservation.paid_amount),
        )
    except rules.RuleError:
        # A room or rate that no longer resolves cannot be re-priced. The
        # keep-the-charge path still works, so checkout is not blocked -- the
        # desk simply is not offered the re-price.
        position["repriced"] = None
        return position

    position["repriced"] = {
        "room_amount": priced["room_amount"],
        "tax_amount": priced["tax_amount"],
        "discount_amount": priced["discount_amount"],
        "overall_amount": priced["overall_amount"],
        "balance_amount": priced["balance_amount"],
        "refund_due": priced["extra_amount"],
        "difference": rules.money(
            priced["overall_amount"] - rules.money(reservation.overall_amount)
        ),
    }
    return position


@router.get("/room_reservation_checkout_preview/{key}", status_code=status.HTTP_200_OK)
def reservation_checkout_preview(
    key: str, request: Request, db: Session = Depends(get_db)
):
    """What checking this guest out now would do, before anything is done.

    Read-only. The Check-out button opens this first, so the desk sees an early
    departure and its two possible bills rather than discovering afterwards
    that the guest was charged for nights they did not stay.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        reservation = _load_by_id_or_token(db, company_id, key)

        if rules.normalise_status(
            reservation.reservation_status
        ) != rules.normalise_status(rules.CHECKED_IN):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"This reservation is {reservation.reservation_status}; "
                    "only a checked-in guest can be checked out."
                ),
            )

        return {
            "status": "success",
            "data": _early_checkout_position(db, company_id, reservation),
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("checkout_preview_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/room_reservation_checkout/{key}")
async def reservation_checkout(
    key: str, request: Request, db: Session = Depends(get_db)
):
    """Depart a guest, once the folio is settled.

    `adjust_stay` (JSON body, default false) carries the early-departure
    decision:

        false  the guest is charged for the stay as booked, and the room is
               released from today. What a non-refundable rate implies.
        true   the departure date moves to today and the stay is re-priced to
               the nights actually used. Any overpayment becomes refundable.

    It is deliberately NOT defaulted to the guest-friendly option. Silently
    reducing a bill is as wrong as silently keeping it -- either way the system
    would be choosing a refund policy it has no configuration for. Defaulting
    to "no change" means an ordinary checkout behaves exactly as it always did,
    and a reduction only ever happens because somebody asked for one.

    Checking out with money still owed is refused rather than allowed and
    reported later: after checkout the reservation is terminal and can no
    longer be edited, so an unsettled balance at that point is a debt with
    nothing left to attach it to. The balance is judged AFTER any re-pricing,
    so a guest who leaves early and drops below what they have already paid is
    never asked for money they no longer owe.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        try:
            payload = await request.json()
        except Exception:
            payload = {}
        adjust_stay = bool((payload or {}).get("adjust_stay", False))

        reservation = _load_by_id_or_token(db, company_id, key)
        position = _early_checkout_position(db, company_id, reservation)

        if adjust_stay:
            if not position["is_early"]:
                raise HTTPException(
                    status_code=400,
                    detail="This stay is not ending early, so there is nothing to re-price.",
                )
            if not position["repriced"]:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "This stay cannot be re-priced -- its room or rate no longer "
                        "resolves. Check out without adjusting, then correct the folio."
                    ),
                )

            priced = rules.quote(
                db,
                company_id,
                room_ids=[int(r) for r in (reservation.room_ids or [])],
                rate_types=list(reservation.rate_type or []),
                nights=position["actual_nights"],
                tax_type_id=reservation.tax_type_id,
                discount_type_id=reservation.discount_type_id,
                extra_charges=reservation.extra_charges,
                extra_bed_count=reservation.extra_bed_count,
                paying_amount=rules.money(reservation.paid_amount),
            )
            reservation.departure_date = position["today"]
            reservation.no_of_nights = position["actual_nights"]
            rules.apply_quote(reservation, priced)
            reservation.balance_amount = priced["balance_amount"]
            reservation.extra_amount = priced["extra_amount"]

        outstanding = rules.money(reservation.balance_amount)
        if outstanding > 0:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail=(
                    f"This guest still owes {outstanding:.2f}. "
                    "Record the payment before checking out."
                ),
            )

        _apply_status(db, reservation, company_id, user_id, rules.CHECKED_OUT)
        sync_room_booking_status(
            db, company_id, [int(r) for r in (reservation.room_ids or [])]
        )
        db.commit()
        db.refresh(reservation)

        return {
            "status": "success",
            "message": "Check-out successful",
            "data": {
                "id": reservation.id,
                "reservation_status": reservation.reservation_status,
                "stay_adjusted": adjust_stay,
                "departure_date": reservation.departure_date,
                "no_of_nights": reservation.no_of_nights,
                "overall_amount": reservation.overall_amount,
                "paid_amount": reservation.paid_amount,
                "balance_amount": reservation.balance_amount,
                # Money the property now owes back, if re-pricing took the
                # total below what the guest had already paid.
                "extra_amount": reservation.extra_amount,
            },
        }

    except rules.RuleError as exc:
        db.rollback()
        raise _rule_http(exc)
    except HTTPException:
        raise
    except Exception:
        logger.exception("checkout_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/room_reservation_cancel/{key}", status_code=status.HTTP_200_OK)
async def reservation_cancel(key: str, request: Request, db: Session = Depends(get_db)):
    """Cancel a booking, releasing its rooms, and record why.

    Distinct from delete: the record stays, so the booking is still searchable,
    still shows what was paid, and still appears in the day's figures as a
    cancellation. The availability engine stops counting it the moment the
    status changes -- see `releases_inventory`.

    THE REASON IS REQUIRED
        A cancellation with no reason is the record nobody can use afterwards.
        "Why is 304 free on the 5th?" has four different answers -- the guest
        changed their mind, the desk resolved an overbooking, it was a
        duplicate, the property closed the room -- and the status alone tells
        none of them apart. Asking once, at the moment somebody knows, is the
        only point at which the answer is free.

        Reservations cancelled before this endpoint recorded reasons keep a
        null one, and are reported as "not recorded" rather than back-filled
        with a guess.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Body is optional on the wire so a malformed request fails on the
        # reason check below with a useful message, not on JSON parsing.
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        reason = str((payload or {}).get("cancellation_reason") or "").strip()
        if not reason:
            raise HTTPException(
                status_code=400,
                detail="A cancellation reason is required.",
            )
        if len(reason) > CANCELLATION_REASON_MAX:
            raise HTTPException(
                status_code=400,
                detail=f"Cancellation reason must be {CANCELLATION_REASON_MAX} characters or fewer.",
            )

        reservation = _load_by_id_or_token(db, company_id, key)
        _apply_status(db, reservation, company_id, user_id, rules.CANCELLED)

        reservation.cancellation_reason = reason
        reservation.cancelled_at = datetime.now()
        reservation.cancelled_by = str(user_id)

        sync_room_booking_status(
            db, company_id, [int(r) for r in (reservation.room_ids or [])]
        )
        db.commit()
        db.refresh(reservation)

        refundable = rules.money(reservation.paid_amount)
        return {
            "status": "success",
            "message": "Reservation cancelled",
            "data": {
                "id": reservation.id,
                "reservation_status": reservation.reservation_status,
                "cancellation_reason": reservation.cancellation_reason,
                "cancelled_at": reservation.cancelled_at,
                # Surfaced rather than moved automatically: whether a
                # cancellation is refundable is a policy decision, and this
                # module has no cancellation-policy configuration to consult.
                "amount_already_paid": refundable,
            },
        }

    except rules.RuleError as exc:
        db.rollback()
        raise _rule_http(exc)
    except HTTPException:
        raise
    except Exception:
        logger.exception("cancel_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/room_reservation_no_show/{key}", status_code=status.HTTP_200_OK)
def reservation_no_show(key: str, request: Request, db: Session = Depends(get_db)):
    """Mark a booking as a no-show: the guest never arrived.

    Like a cancellation it releases the rooms, but it is a different fact and
    the two must not be conflated -- a no-show is usually chargeable and a
    cancellation usually is not.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        reservation = _load_by_id_or_token(db, company_id, key)

        # Transition first, then the date rule. Asked to no-show a cancelled
        # booking, "Cancelled cannot become No-Show" is the useful answer;
        # "it has not arrived yet" is true but beside the point.
        rules.assert_transition(reservation.reservation_status, rules.NO_SHOW)

        if reservation.arrival_date > date.today():
            raise HTTPException(
                status_code=409,
                detail=(
                    "This reservation has not arrived yet, so it cannot be a "
                    f"no-show until {reservation.arrival_date.isoformat()}."
                ),
            )

        _apply_status(db, reservation, company_id, user_id, rules.NO_SHOW)
        sync_room_booking_status(
            db, company_id, [int(r) for r in (reservation.room_ids or [])]
        )
        db.commit()
        db.refresh(reservation)

        return {
            "status": "success",
            "message": "Reservation marked as no-show",
            "data": {
                "id": reservation.id,
                "reservation_status": reservation.reservation_status,
                "balance_amount": reservation.balance_amount,
            },
        }

    except rules.RuleError as exc:
        db.rollback()
        raise _rule_http(exc)
    except HTTPException:
        raise
    except Exception:
        logger.exception("no_show_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


# =====================================================
# PAYMENTS
# =====================================================
@router.post("/room_reservation_pay/{key}", status_code=status.HTTP_200_OK)
async def reservation_pay_due_amount(
    key: str, request: Request, db: Session = Depends(get_db)
):
    """Record a payment against the outstanding balance."""
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        payment_method = (payload.get("payment_method") or "").strip()
        if not payment_method:
            raise HTTPException(status_code=400, detail="Payment method is required")

        try:
            paying_amount = rules.money(float(payload.get("paying_amount")))
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Paying amount must be a number")

        if paying_amount <= 0:
            raise HTTPException(
                status_code=400, detail="Paying amount must be greater than 0"
            )

        reservation = _load_by_id_or_token(db, company_id, key)

        if rules.normalise_status(reservation.reservation_status) in {
            rules.normalise_status(rules.CANCELLED)
        }:
            raise HTTPException(
                status_code=409,
                detail="This reservation is cancelled; no further payment can be taken.",
            )

        balance = rules.money(reservation.balance_amount)
        if paying_amount > balance:
            raise HTTPException(
                status_code=400,
                detail=f"Paying amount cannot exceed the outstanding balance of {balance:.2f}",
            )

        reservation.paid_amount = rules.money(
            (reservation.paid_amount or 0) + paying_amount
        )
        reservation.balance_amount = rules.money(balance - paying_amount)
        reservation.updated_by = str(user_id)

        db.add(
            models.ReservationAmountPaidHistory(
                reservation_id=_history_key(reservation),
                user_id=str(user_id),
                amount=paying_amount,
                # date.today() at call time, not a module constant captured at
                # import -- a service that stays up for a week was stamping
                # every payment with the day it started.
                paid_date=date.today(),
                payment_method=payment_method,
                status=STATUS,
                created_by=str(user_id),
                company_id=str(company_id),
            )
        )

        db.commit()
        db.refresh(reservation)

        return {
            "status": "success",
            "message": "Payment recorded successfully",
            "data": {
                "paid_amount": reservation.paid_amount,
                "balance_amount": reservation.balance_amount,
                "payment_state": _payment_state(reservation),
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("payment_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/room_reservation_refund/{key}", status_code=status.HTTP_200_OK)
async def reservation_refund_extra_amount(
    key: str, request: Request, db: Session = Depends(get_db)
):
    """Refund an overpayment.

    The refund now writes a history row of its own, as a negative amount, so
    the payment history sums to the cash actually held. Previously it moved
    `extra_amount` down and left no trace, which meant the only record that a
    refund had happened was that a number had got smaller.
    """
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        refund_method = (payload.get("refund_method") or "").strip()
        if not refund_method:
            raise HTTPException(status_code=400, detail="Refund method is required")

        try:
            refund_amount = rules.money(float(payload.get("refund_amount")))
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Refund amount must be a number")

        if refund_amount <= 0:
            raise HTTPException(
                status_code=400, detail="Refund amount must be greater than 0"
            )

        reservation = _load_by_id_or_token(db, company_id, key)

        refundable = rules.money(reservation.extra_amount)
        if refund_amount > refundable:
            raise HTTPException(
                status_code=400,
                detail=f"Refund amount cannot exceed the refundable amount of {refundable:.2f}",
            )

        reservation.extra_amount = rules.money(refundable - refund_amount)
        # The money leaves, so what the property holds goes down with it.
        reservation.paid_amount = rules.money(
            max(0.0, (reservation.paid_amount or 0) - refund_amount)
        )
        reservation.updated_by = str(user_id)

        db.add(
            models.ReservationAmountPaidHistory(
                reservation_id=_history_key(reservation),
                user_id=str(user_id),
                amount=-refund_amount,
                paid_date=date.today(),
                payment_method=f"Refund - {refund_method}",
                status=STATUS,
                created_by=str(user_id),
                company_id=str(company_id),
            )
        )

        db.commit()
        db.refresh(reservation)

        return {
            "status": "success",
            "message": "Refund processed successfully",
            "data": {
                "extra_amount": reservation.extra_amount,
                "paid_amount": reservation.paid_amount,
                "balance_amount": reservation.balance_amount,
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("refund_failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/room_reservation_payments/{key}", status_code=status.HTTP_200_OK)
def get_reservation_payment_history(
    key: str, request: Request, db: Session = Depends(get_db)
):
    try:
        user_id, role_id, company_id, _ = verify_authentication(request)
        if not company_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        reservation = _load_by_id_or_token(db, company_id, key)

        history = (
            db.query(models.ReservationAmountPaidHistory)
            .filter(
                models.ReservationAmountPaidHistory.reservation_id.in_(
                    _history_keys(reservation)
                ),
                models.ReservationAmountPaidHistory.status == STATUS,
            )
            .order_by(
                models.ReservationAmountPaidHistory.paid_date.desc(),
                models.ReservationAmountPaidHistory.id.desc(),
            )
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "id": h.id,
                    "amount": h.amount,
                    "paid_date": h.paid_date,
                    "payment_method": h.payment_method,
                    # A refund is stored as a negative amount; labelling the
                    # direction saves every reader re-deriving it from the sign.
                    "kind": "Refund" if (h.amount or 0) < 0 else "Payment",
                }
                for h in history
            ],
            "summary": {
                "overall_amount": reservation.overall_amount,
                "paid_amount": reservation.paid_amount,
                "balance_amount": reservation.balance_amount,
                "extra_amount": reservation.extra_amount,
                "payment_state": _payment_state(reservation),
            },
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("payment_history_failed")
        raise HTTPException(status_code=500, detail="Internal server error")

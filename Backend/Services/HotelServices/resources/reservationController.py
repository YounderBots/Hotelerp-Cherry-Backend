import os, json
from fastapi import APIRouter, Depends, status, HTTPException, Request, Form, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
import shutil

from models import models, get_db
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

# =====================================================
# COMMON CONSTANTS & CONFIG
# =====================================================
import os
from datetime import datetime, date

# ---------------- System Status ----------------
STATUS = "ACTIVE"
UNSTATUS = "INACTIVE"

# ---------------- Reservation Types ----------------
RESERVATION = "RESERVATION"
GROUP_RESERVATION = "GROUP_RESERVATION"
CHECKIN = "CHECKIN"

# ---------------- Room Status ----------------
AVAILABLE = "AVAILABLE"
RESERVED = "RESERVED"
OCCUPIED = "OCCUPIED"
CANCELLED = "CANCELLED"

# ---------------- Upload Paths ----------------
UPLOAD_DIR = "templates/static/identity_proofs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- Date Helpers ----------------
TODAY = date.today()
NOW = datetime.now()

# =====================================================
# CREATE ROOM BOOKING
# =====================================================
@router.post("/room_booking", status_code=status.HTTP_201_CREATED)
async def create_room_booking(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
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
                detail="phone_number is required"
            )

        if not arrival_date or not departure_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="arrival_date and departure_date are required"
            )

        if not isinstance(room_type_ids, list) or not room_type_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_type must be a non-empty list of room type ids"
            )

        arrival = datetime.strptime(arrival_date, "%Y-%m-%d").date()
        departure = datetime.strptime(departure_date, "%Y-%m-%d").date()

        if departure <= arrival:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="departure_date must be after arrival_date"
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
            company_id=company_id
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
                "created_at": booking.created_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ALL ROOM BOOKINGS
# =====================================================
@router.get("/room_booking", status_code=status.HTTP_200_OK)
def get_all_room_bookings(
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
        # FETCH BOOKINGS
        # -------------------------------------------------
        bookings = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS
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
                "updated_at": booking.updated_at
            }
            for booking in bookings
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
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# GET ROOM BOOKING BY ID
# =====================================================
@router.get("/room_booking/{booking_id}", status_code=status.HTTP_200_OK)
def get_room_booking_by_id(
    request: Request,
    booking_id: int,
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
        # VALIDATION
        # -------------------------------------------------
        if booking_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking_id"
            )

        # -------------------------------------------------
        # FETCH BOOKING
        # -------------------------------------------------
        booking = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.id == booking_id,
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS
            )
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room booking not found"
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
                "updated_at": booking.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# UPDATE ROOM BOOKING
# =====================================================
@router.put("/room_booking", status_code=status.HTTP_200_OK)
async def update_room_booking(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # REQUEST BODY (JSON)
        # -------------------------------------------------
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
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
                detail="Valid booking id is required"
            )

        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="phone_number is required"
            )

        if not arrival_date or not departure_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="arrival_date and departure_date are required"
            )

        if not isinstance(room_type_ids, list) or not room_type_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="room_type must be a non-empty list of room type ids"
            )

        arrival = datetime.strptime(arrival_date, "%Y-%m-%d").date()
        departure = datetime.strptime(departure_date, "%Y-%m-%d").date()

        if departure <= arrival:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="departure_date must be after arrival_date"
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
                models.RoomBooking.status == CommonWords.STATUS
            )
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room booking not found"
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
                "updated_at": booking.updated_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# DELETE ROOM BOOKING (SOFT DELETE)
# =====================================================
@router.delete("/room_booking/{booking_id}", status_code=status.HTTP_200_OK)
def delete_room_booking(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if booking_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking_id"
            )

        # -------------------------------------------------
        # FETCH BOOKING
        # -------------------------------------------------
        booking = (
            db.query(models.RoomBooking)
            .filter(
                models.RoomBooking.id == booking_id,
                models.RoomBooking.company_id == company_id,
                models.RoomBooking.status == CommonWords.STATUS
            )
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room booking not found"
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
        return {
            "status": "success",
            "message": "Room booking deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# CREATE ROOM RESERVATION
# =====================================================
@router.post("/room_reservation", status_code=status.HTTP_201_CREATED)
async def create_room_reservation(
    request: Request,
    db: Session = Depends(get_db),

    # ---------------- Guest ----------------
    room_reservation_id: str = Form(...),
    salutation: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone_number: str = Form(...),
    email: str = Form(None),

    # ---------------- Stay ----------------
    arrival_date: date = Form(...),
    departure_date: date = Form(...),
    no_of_nights: int = Form(...),

    room_type_ids: str = Form(...),   # JSON → [1,2]
    room_ids: str = Form(...),        # JSON → [101,102]
    rate_type: str = Form(...),       # JSON → ["daily","daily"]

    no_of_rooms: int = Form(...),
    no_of_adults: int = Form(...),
    no_of_children: int = Form(...),

    # ---------------- Payment ----------------
    payment_method_id: int = Form(...),

    extra_bed_count: int = Form(0),
    extra_bed_cost: float = Form(0),

    total_amount: float = Form(...),
    tax_percentage: float = Form(0),
    tax_amount: float = Form(0),

    discount_percentage: float = Form(0),
    discount_amount: float = Form(0),

    extra_charges: float = Form(0),

    overall_amount: float = Form(...),
    paid_amount: float = Form(0),
    balance_amount: float = Form(0),
    extra_amount: float = Form(0),

    # ---------------- Reservation ----------------
    booking_status_id: int = Form(...),
    reservation_type: str = Form(RESERVATION),

    room_complementary: str = Form(None),
    common_complementary: str = Form(None),

    # ---------------- Identity ----------------
    identity_type_id: int = Form(...),
    identity_file: UploadFile = File(...),
):
    # -------------------------------------------------
    # AUTHENTICATION
    # -------------------------------------------------
    user_id, role_id, company_id, token = verify_authentication(request)
    if not user_id or not company_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # -------------------------------------------------
    # DATE VALIDATION
    # -------------------------------------------------
    if departure_date <= arrival_date:
        raise HTTPException(
            status_code=400,
            detail="departure_date must be greater than arrival_date"
        )

    # -------------------------------------------------
    # JSON VALIDATION
    # -------------------------------------------------
    try:
        room_type_ids_json = json.loads(room_type_ids)
        room_ids_json = json.loads(room_ids)
        rate_type_json = json.loads(rate_type)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="room_type_ids, room_ids, rate_type must be valid JSON arrays"
        )

    # -------------------------------------------------
    # FILE UPLOAD
    # -------------------------------------------------
    ext = identity_file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(identity_file.file, f)

    # -------------------------------------------------
    # CREATE RESERVATION (SAFE ASSIGNMENT)
    # -------------------------------------------------
    reservation = models.RoomReservation()

    reservation.room_reservation_id = room_reservation_id
    reservation.salutation = salutation
    reservation.first_name = first_name
    reservation.last_name = last_name
    reservation.phone_number = phone_number
    reservation.email = email

    reservation.arrival_date = arrival_date
    reservation.departure_date = departure_date
    reservation.no_of_nights = no_of_nights

    reservation.room_type_ids = room_type_ids_json
    reservation.room_ids = room_ids_json
    reservation.rate_type = rate_type_json

    reservation.no_of_rooms = no_of_rooms
    reservation.no_of_adults = no_of_adults
    reservation.no_of_children = no_of_children

    reservation.payment_method_id = payment_method_id

    reservation.extra_bed_count = extra_bed_count
    reservation.extra_bed_cost = extra_bed_cost

    reservation.total_amount = total_amount
    reservation.tax_percentage = tax_percentage
    reservation.tax_amount = tax_amount

    reservation.discount_percentage = discount_percentage
    reservation.discount_amount = discount_amount

    reservation.extra_charges = extra_charges

    reservation.overall_amount = overall_amount
    reservation.paid_amount = paid_amount
    reservation.balance_amount = balance_amount
    reservation.extra_amount = extra_amount

    reservation.booking_status_id = booking_status_id
    reservation.reservation_type = reservation_type

    reservation.room_complementary = room_complementary
    reservation.common_complementary = common_complementary

    reservation.identity_type_id = identity_type_id
    reservation.proof_document = filename

    reservation.confirmation_code = str(uuid.uuid4())[:8].upper()
    reservation.status = STATUS
    reservation.created_by = user_id
    reservation.company_id = company_id

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------
    return {
        "status": "success",
        "message": "Room reservation created successfully",
        "data": {
            "id": reservation.id,
            "room_reservation_id": reservation.room_reservation_id,
            "token": reservation.token
        }
    }

# =====================================================
# GET ALL ROOM RESERVATIONS
# =====================================================
@router.get("/room_reservation", status_code=status.HTTP_200_OK)
def get_all_room_reservations(
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
        # FETCH ROOM RESERVATIONS
        # -------------------------------------------------
        reservations = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.company_id == company_id,
                models.RoomReservation.status == STATUS
            )
            .order_by(models.RoomReservation.id.desc())
            .all()
        )

        # -------------------------------------------------
        # FORMAT RESPONSE (MODEL ORDER)
        # -------------------------------------------------
        data = [
            {
                # ---------------- Reference ----------------
                "id": r.id,
                "room_reservation_id": r.room_reservation_id,

                # ---------------- Guest Details ----------------
                "salutation": r.salutation,
                "first_name": r.first_name,
                "last_name": r.last_name,
                "phone_number": r.phone_number,
                "email": r.email,

                # ---------------- Stay Details ----------------
                "arrival_date": r.arrival_date,
                "departure_date": r.departure_date,
                "no_of_nights": r.no_of_nights,

                # ---------------- Room Details ----------------
                "room_type_ids": r.room_type_ids,
                "room_ids": r.room_ids,
                "rate_type": r.rate_type,

                "no_of_rooms": r.no_of_rooms,
                "no_of_adults": r.no_of_adults,
                "no_of_children": r.no_of_children,

                # ---------------- Payment ----------------
                "payment_method_id": r.payment_method_id,

                "extra_bed_count": r.extra_bed_count,
                "extra_bed_cost": r.extra_bed_cost,

                "total_amount": r.total_amount,
                "tax_percentage": r.tax_percentage,
                "tax_amount": r.tax_amount,

                "discount_percentage": r.discount_percentage,
                "discount_amount": r.discount_amount,

                "extra_charges": r.extra_charges,

                "overall_amount": r.overall_amount,
                "paid_amount": r.paid_amount,
                "balance_amount": r.balance_amount,
                "extra_amount": r.extra_amount,

                # ---------------- Reservation Info ----------------
                "booking_status_id": r.booking_status_id,
                "reservation_type": r.reservation_type,

                "room_complementary": r.room_complementary,
                "common_complementary": r.common_complementary,

                # ---------------- Identity ----------------
                "identity_type_id": r.identity_type_id,
                "proof_document": r.proof_document,

                "confirmation_code": r.confirmation_code,

                # ---------------- System ----------------
                "token": r.token,
                "status": r.status,
                "created_by": r.created_by,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "updated_by": r.updated_by,
                "company_id": r.company_id,
            }
            for r in reservations
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
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# GET ROOM RESERVATION BY ID
# =====================================================
@router.get("/room_reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def get_room_reservation_by_id(
    reservation_id: int,
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
        # VALIDATION
        # -------------------------------------------------
        if reservation_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reservation_id"
            )

        # -------------------------------------------------
        # FETCH RESERVATION
        # -------------------------------------------------
        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == reservation_id,
                models.RoomReservation.company_id == company_id,
                models.RoomReservation.status == STATUS
            )
            .first()
        )

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room reservation not found"
            )

        # -------------------------------------------------
        # RESPONSE (MODEL ORDER)
        # -------------------------------------------------
        return {
            "status": "success",
            "data": {
                # ---------------- Reference ----------------
                "id": reservation.id,
                "room_reservation_id": reservation.room_reservation_id,

                # ---------------- Guest Details ----------------
                "salutation": reservation.salutation,
                "first_name": reservation.first_name,
                "last_name": reservation.last_name,
                "phone_number": reservation.phone_number,
                "email": reservation.email,

                # ---------------- Stay Details ----------------
                "arrival_date": reservation.arrival_date,
                "departure_date": reservation.departure_date,
                "no_of_nights": reservation.no_of_nights,

                # ---------------- Room Details ----------------
                "room_type_ids": reservation.room_type_ids,
                "room_ids": reservation.room_ids,
                "rate_type": reservation.rate_type,

                "no_of_rooms": reservation.no_of_rooms,
                "no_of_adults": reservation.no_of_adults,
                "no_of_children": reservation.no_of_children,

                # ---------------- Payment ----------------
                "payment_method_id": reservation.payment_method_id,

                "extra_bed_count": reservation.extra_bed_count,
                "extra_bed_cost": reservation.extra_bed_cost,

                "total_amount": reservation.total_amount,
                "tax_percentage": reservation.tax_percentage,
                "tax_amount": reservation.tax_amount,

                "discount_percentage": reservation.discount_percentage,
                "discount_amount": reservation.discount_amount,

                "extra_charges": reservation.extra_charges,

                "overall_amount": reservation.overall_amount,
                "paid_amount": reservation.paid_amount,
                "balance_amount": reservation.balance_amount,
                "extra_amount": reservation.extra_amount,

                # ---------------- Reservation Info ----------------
                "booking_status_id": reservation.booking_status_id,
                "reservation_type": reservation.reservation_type,

                "room_complementary": reservation.room_complementary,
                "common_complementary": reservation.common_complementary,

                # ---------------- Identity ----------------
                "identity_type_id": reservation.identity_type_id,
                "proof_document": reservation.proof_document,

                "confirmation_code": reservation.confirmation_code,

                # ---------------- System ----------------
                "token": reservation.token,
                "status": reservation.status,
                "created_by": reservation.created_by,
                "created_at": reservation.created_at,
                "updated_at": reservation.updated_at,
                "updated_by": reservation.updated_by,
                "company_id": reservation.company_id
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# UPDATE ROOM RESERVATION
# =====================================================
@router.put("/room_reservation", status_code=status.HTTP_200_OK)
async def update_room_reservation(
    request: Request,
    db: Session = Depends(get_db),

    # -------- REQUIRED IDENTIFIER --------
    id: int = Form(...),  # room_reservation.id

    # -------- Guest --------
    salutation: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone_number: str = Form(...),
    email: str = Form(None),

    # -------- Stay --------
    arrival_date: date = Form(...),
    departure_date: date = Form(...),
    no_of_nights: int = Form(...),

    room_type_ids: str = Form(...),   # JSON → [room_type_id]
    room_ids: str = Form(...),        # JSON → [room_id]
    rate_type: str = Form(...),       # JSON → ["daily"]

    no_of_rooms: int = Form(...),
    no_of_adults: int = Form(...),
    no_of_children: int = Form(...),

    # -------- Payment --------
    payment_method_id: int = Form(...),

    extra_bed_count: int = Form(0),
    extra_bed_cost: float = Form(0),

    total_amount: float = Form(...),
    tax_percentage: float = Form(0),
    tax_amount: float = Form(0),
    discount_percentage: float = Form(0),
    discount_amount: float = Form(0),
    extra_charges: float = Form(0),

    overall_amount: float = Form(...),
    paid_amount: float = Form(0),
    balance_amount: float = Form(0),
    extra_amount: float = Form(0),

    # -------- Reservation --------
    booking_status_id: int = Form(...),
    reservation_type: str = Form(...),

    room_complementary: str = Form(None),
    common_complementary: str = Form(None),
):
    try:
        # -------------------------------------------------
        # AUTH
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)
        if not user_id or not company_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if id <= 0:
            raise HTTPException(status_code=400, detail="Invalid reservation id")

        if departure_date <= arrival_date:
            raise HTTPException(
                status_code=400,
                detail="departure_date must be greater than arrival_date"
            )

        # -------------------------------------------------
        # FETCH
        # -------------------------------------------------
        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == id,
                models.RoomReservation.company_id == company_id,
                models.RoomReservation.status == STATUS
            )
            .first()
        )

        if not reservation:
            raise HTTPException(
                status_code=404,
                detail="Room reservation not found"
            )

        # -------------------------------------------------
        # UPDATE (SAFE ASSIGNMENT)
        # -------------------------------------------------
        reservation.salutation = salutation
        reservation.first_name = first_name
        reservation.last_name = last_name
        reservation.phone_number = phone_number
        reservation.email = email

        reservation.arrival_date = arrival_date
        reservation.departure_date = departure_date
        reservation.no_of_nights = no_of_nights

        reservation.room_type_ids = json.loads(room_type_ids)
        reservation.room_ids = json.loads(room_ids)
        reservation.rate_type = json.loads(rate_type)

        reservation.no_of_rooms = no_of_rooms
        reservation.no_of_adults = no_of_adults
        reservation.no_of_children = no_of_children

        reservation.payment_method_id = payment_method_id

        reservation.extra_bed_count = extra_bed_count
        reservation.extra_bed_cost = extra_bed_cost

        reservation.total_amount = total_amount
        reservation.tax_percentage = tax_percentage
        reservation.tax_amount = tax_amount
        reservation.discount_percentage = discount_percentage
        reservation.discount_amount = discount_amount
        reservation.extra_charges = extra_charges

        reservation.overall_amount = overall_amount
        reservation.paid_amount = paid_amount
        reservation.balance_amount = balance_amount
        reservation.extra_amount = extra_amount

        reservation.booking_status_id = booking_status_id
        reservation.reservation_type = reservation_type

        reservation.room_complementary = room_complementary
        reservation.common_complementary = common_complementary

        reservation.updated_by = user_id

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------
        db.commit()
        db.refresh(reservation)

        return {
            "status": "success",
            "message": "Room reservation updated successfully",
            "data": {
                "id": reservation.id,
                "room_reservation_id": reservation.room_reservation_id,
                "updated_at": reservation.updated_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# DELETE ROOM RESERVATION (SOFT DELETE)
# =====================================================
@router.delete("/room_reservation/{reservation_id}", status_code=status.HTTP_200_OK)
def delete_room_reservation(
    reservation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------
        user_id, role_id, company_id, token = verify_authentication(request)

        if not user_id or not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        if reservation_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reservation_id"
            )

        # -------------------------------------------------
        # FETCH RECORD
        # -------------------------------------------------
        reservation = (
            db.query(models.RoomReservation)
            .filter(
                models.RoomReservation.id == reservation_id,
                models.RoomReservation.company_id == company_id,
                models.RoomReservation.status == STATUS
            )
            .first()
        )

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room reservation not found"
            )

        # -------------------------------------------------
        # SOFT DELETE
        # -------------------------------------------------
        reservation.status = UNSTATUS
        reservation.updated_by = user_id

        db.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        return {
            "status": "success",
            "message": "Room reservation deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
# =====================================================
# CREATE ROOM DETAILS (AFTER RESERVATION)
# =====================================================
@router.post("/room_details", status_code=status.HTTP_201_CREATED)
async def create_room_details(
    request: Request,
    db: Session = Depends(get_db),

    # -------- Reference --------
    reservation_id: str = Form(...),           # room_reservation.id or token

    # -------- Room Info --------
    room_category: int = Form(...),             # room_type.id
    available_rooms: int = Form(...),           # room.id

    total_adults: int = Form(...),
    total_children: int = Form(...),

    arrival_date: date = Form(...),
    departure_date: date = Form(...),

    booking_status: str = Form(...),            # RESERVED / CHECKIN / etc
    reservation_type: str = Form(...),          # RESERVATION / GROUP_RESERVATION

    # -------- Extra --------
    extra_bed_count: int = Form(0),
    extra_bed_cost: float = Form(0),
    total_amount: float = Form(...),

    room_complementary: str = Form("No"),       # Yes / No
):
    # -------------------------------------------------
    # AUTH
    # -------------------------------------------------
    user_id, role_id, company_id, token = verify_authentication(request)

    if not user_id or not company_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # -------------------------------------------------
    # VALIDATE RESERVATION
    # -------------------------------------------------
    reservation = db.query(models.RoomReservation).filter(
        models.RoomReservation.id == reservation_id,
        models.RoomReservation.status == STATUS
    ).first()

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    # -------------------------------------------------
    # CREATE ROOM DETAILS
    # -------------------------------------------------
    new_record = models.RoomDetails(
        reservation_id=reservation.id,

        room_category=room_category,
        available_rooms=available_rooms,

        total_adults=total_adults,
        total_children=total_children,

        arrival_date=arrival_date,
        departure_date=departure_date,

        booking_status=booking_status,
        reservation_type=reservation_type,

        extra_bed_count=extra_bed_count,
        extra_bed_cost=extra_bed_cost,
        total_amount=total_amount,

        room_complementary=room_complementary,

        status=STATUS,
        created_by=user_id,
        company_id=company_id
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    # -------------------------------------------------
    # UPDATE ROOM STATUS (OPTIONAL BUT IMPORTANT)
    # -------------------------------------------------
    if booking_status in ["RESERVED", "CHECKIN"]:
        db.query(models.Room).filter(
            models.Room.id == available_rooms
        ).update({
            "Room_Booking_status": booking_status
        })
        db.commit()

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------
    return {
        "status": "success",
        "message": "Room details added successfully",
        "data": {
            "room_details_id": new_record.id,
            "token": new_record.token
        }
    }

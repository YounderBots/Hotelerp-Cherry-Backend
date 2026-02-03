from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid

from models import models, get_db
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()


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
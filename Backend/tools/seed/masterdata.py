"""hotelerp_masterdata: the configuration every other module reads.

This is the authoritative source the brief calls Master Data: room inventory,
rate plans, tax, discount, payment methods, the reservation status vocabulary.
Nothing downstream may hardcode any of it.

RATE PLANS ARE REAL COLUMNS, NOT DECORATION
    `reservation_rules.RATE_COLUMN` maps a booking's `rate_type` onto one of
    six columns on `room_type` -- Daily_Rate, Weekly_Rate, Bed_Only_Rate,
    Bed_And_Breakfast_Rate, Half_Board_Rate, Full_Board_Rate. Every one is
    populated below and every one is priced consistently (board plans add the
    cost of the meals they include), so a booking on any plan prices correctly
    instead of silently falling back to the daily rate.

THE STATUS VOCABULARY IS FIXED BY THE TRANSITION TABLE
    `reservation_rules` names Confirmed / Checked-In / Checked-Out / Cancelled
    / No-Show and treats the master table as the authority on which of them are
    selectable. Renaming one here breaks the transition table; the two INACTIVE
    duplicate "Occupied" rows the previous dataset carried are dropped, because
    occupancy is a ROOM state, not a reservation status.
"""

from __future__ import annotations

import os

from . import images as im
from . import photos
from .common import audit, insert, upload_dir

# Search terms per room type, specific first. Four photographs per type, shared
# by every room of that type -- a hotel's Deluxe rooms genuinely do look alike,
# so this is honest as well as cheaper than 100 separate downloads.
ROOM_TYPE_QUERIES = {
    "Standard Room": [
        ["hotel standard room interior", "hotel room twin bed"],
        ["hotel room bed interior", "hotel bedroom"],
        ["hotel guest room interior", "hotel room desk chair"],
        ["hotel bathroom interior", "hotel ensuite bathroom"],
    ],
    "Deluxe Room": [
        ["hotel deluxe room interior", "hotel room double bed"],
        ["hotel room king bed", "hotel bedroom interior"],
        ["hotel room seating area", "hotel room armchair"],
        ["hotel bathroom marble", "hotel bathroom interior"],
    ],
    "Super Deluxe": [
        ["hotel superior room interior", "hotel room luxury bed"],
        ["hotel room interior design", "hotel bedroom luxury"],
        ["hotel suite room interior", "hotel room seating"],
        ["hotel bathroom luxury", "hotel bathroom"],
    ],
    "Executive Room": [
        ["hotel executive room", "hotel business room interior"],
        ["hotel room writing desk", "hotel bedroom desk"],
        ["hotel room king size bed", "hotel bedroom"],
        ["hotel bathroom modern", "hotel bathroom"],
    ],
    "Family Suite": [
        ["hotel family suite", "hotel suite living room"],
        ["hotel suite bedroom", "hotel room two beds"],
        ["hotel suite sofa", "hotel living room interior"],
        ["hotel bathroom family", "hotel bathroom"],
    ],
    "VIP Suite": [
        ["hotel luxury suite interior", "luxury hotel suite"],
        ["hotel suite bedroom luxury", "luxury hotel bedroom"],
        ["hotel suite lounge", "luxury hotel living room"],
        ["luxury hotel bathroom", "hotel bathroom marble"],
    ],
    "Presidential Suite": [
        ["presidential suite hotel", "luxury hotel penthouse suite"],
        ["luxury hotel suite bedroom", "luxury hotel bedroom"],
        ["luxury hotel suite dining", "hotel suite living room"],
        ["luxury hotel bathroom suite", "luxury hotel bathroom"],
    ],
    "Dormitory": [
        ["hostel dormitory bunk beds", "hostel dorm room"],
        ["hostel room bunk bed", "dormitory beds"],
        ["hostel dormitory room", "hostel bunk room"],
        ["hostel bathroom shared", "hostel bathroom"],
    ],
}

# ---------------------------------------------------------------------------
# Rate plans
# ---------------------------------------------------------------------------
# (id, name, room_cost, bed_cost, daily, weekly, bed_only, b&b, half, full)
# Weekly is six nights' price for seven, the usual long-stay concession.
ROOM_TYPES = [
    (1, "Standard Room",      3500,  800,  3500,  21000,  3200,  3800,  4600,  5400),
    (2, "Deluxe Room",        5200, 1000,  5200,  31200,  4800,  5600,  6600,  7600),
    (3, "Super Deluxe",       6800, 1000,  6800,  40800,  6300,  7300,  8500,  9700),
    (4, "Executive Room",     8500, 1200,  8500,  51000,  7900,  9100, 10500, 11900),
    (5, "Family Suite",      11000, 1200, 11000,  66000, 10200, 12000, 14000, 16000),
    (6, "VIP Suite",         14500, 1500, 14500,  87000, 13500, 15700, 18100, 20500),
    (7, "Presidential Suite", 22000, 1500, 22000, 132000, 20500, 23500, 27000, 30500),
    (8, "Dormitory",          1200,  400,  1200,   7200,  1100,  1500,  2100,  2700),
]

BED_TYPES = [
    "Single Bed", "Twin Bed", "Double Bed", "Queen Bed",
    "King Bed", "Sofa Bed", "Bunk Bed", "Extra Bed",
]

# (room_no, type_id, bed_type_id, max_adult, max_child)
# A real floor plan: standards low, suites high, one presidential at the top.
ROOMS = [
    ("101", 1, 3, 2, 1), ("102", 1, 3, 2, 1), ("103", 1, 2, 2, 1),
    ("104", 1, 3, 2, 1), ("105", 1, 2, 2, 1), ("106", 1, 3, 2, 1),
    ("107", 1, 1, 1, 0), ("108", 8, 7, 6, 0),
    ("201", 2, 4, 3, 1), ("202", 2, 4, 3, 1), ("203", 2, 3, 2, 2),
    ("204", 2, 4, 3, 1), ("205", 2, 3, 2, 2), ("206", 2, 4, 3, 1),
    ("301", 3, 5, 3, 2), ("302", 3, 5, 3, 2), ("303", 3, 4, 3, 1),
    ("304", 3, 5, 3, 2), ("305", 3, 4, 3, 1),
    ("401", 4, 5, 3, 2), ("402", 4, 5, 3, 2), ("403", 4, 5, 3, 2),
    ("501", 5, 5, 4, 3), ("502", 6, 5, 4, 2),
    ("601", 7, 5, 4, 3),
]

FACILITIES = [
    "Air Conditioning", "Free Wi-Fi", "Television", "Mini Bar", "Room Service",
    "Laundry Service", "Airport Pickup", "Swimming Pool", "Gymnasium", "Spa",
    "Conference Hall", "Parking", "Restaurant", "Bar", "Doctor on Call",
]

COMPLEMENTARY = [
    ("Welcome Drink", "Fresh juice or tender coconut on arrival"),
    ("Breakfast Buffet", "Buffet breakfast for registered occupants"),
    ("Airport Pickup", "One-way transfer from the airport"),
    ("Evening Tea", "Tea and snacks served in the lounge"),
    ("Fruit Basket", "Seasonal fruit placed in the room"),
    ("Late Checkout", "Checkout extended to 14:00, subject to availability"),
    ("Newspaper", "Daily newspaper delivered to the room"),
]

TASK_TYPES = [
    ("Daily Cleaning", "#3B82F6"), ("Deep Cleaning", "#8B5CF6"),
    ("Linen Change", "#10B981"), ("Turndown Service", "#F59E0B"),
    ("Maintenance Check", "#EF4444"), ("Inspection", "#6B7280"),
    ("Restocking", "#14B8A6"), ("Pest Control", "#A16207"),
]

HALLS = ["Ground Floor", "First Floor", "Second Floor", "Poolside",
         "Rooftop Terrace", "Banquet Hall", "Private Dining"]

CURRENCIES = [
    ("India", "Indian Rupee", "₹"),
    ("United States", "US Dollar", "$"),
    ("United Kingdom", "Pound Sterling", "£"),
    ("United Arab Emirates", "UAE Dirham", "د.إ"),
    ("Singapore", "Singapore Dollar", "S$"),
]

# Indian hotel tax as actually levied: CGST and SGST at half each, plus the
# combined rates for the slabs the property bills at.
TAXES = [
    ("CGST", "6"), ("SGST", "6"), ("GST 12%", "12"),
    ("GST 18%", "18"), ("Luxury Tax", "28"), ("No Tax", "0"),
]

DISCOUNTS = [
    ("Early Bird Discount", "10"), ("Corporate Rate", "15"),
    ("Loyalty Member", "5"), ("Festive Season Offer", "20"),
    ("Long Stay (7+ nights)", "12"), ("No Discount", "0"),
]

PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "UPI",
                   "Net Banking", "Bank Transfer", "Corporate Billing"]

IDENTITY_PROOFS = ["Aadhaar Card", "Passport", "Driving License",
                   "Voter ID Card", "PAN Card", "Company ID Card"]

# The vocabulary reservation_rules transitions between. Colour drives the badge.
RESERVATION_STATUSES = [
    ("Confirmed", "#10B981"), ("Checked-In", "#3B82F6"),
    ("Checked-Out", "#6B7280"), ("Cancelled", "#EF4444"),
    ("No-Show", "#F59E0B"), ("Pending", "#FBBF24"), ("On Hold", "#8B5CF6"),
]

DEPARTMENTS = ["Front Office", "Housekeeping", "Food & Beverage", "Kitchen",
               "Maintenance", "Accounts", "Human Resources", "Security",
               "Stores", "Management"]

DESIGNATIONS = ["General Manager", "Front Office Manager", "Front Desk Executive",
                "Reservation Executive", "Housekeeping Supervisor",
                "Room Attendant", "Restaurant Manager", "Chef", "Bartender",
                "Accountant"]


def seed(conn) -> dict:
    def simple(table, column, names, extra=None):
        insert(conn, table, [
            dict(id=i, **{column: n}, **(extra(i, n) if extra else {}), **audit())
            for i, n in enumerate(names, start=1)
        ])

    simple("bed_type", "Type_Name", BED_TYPES)
    simple("facility", "Facility_Name", FACILITIES)
    simple("department", "Department_Name", DEPARTMENTS)
    simple("designation", "Designation_Name", DESIGNATIONS)
    simple("table_hall_names", "hall_name", HALLS)
    simple("payment_methods", "payment_method", PAYMENT_METHODS)
    simple("identity_proof", "Proof_Name", IDENTITY_PROOFS)

    insert(conn, "room_complementry", [
        dict(id=i, Complementry_Name=n, Description=d, **audit())
        for i, (n, d) in enumerate(COMPLEMENTARY, start=1)
    ])
    insert(conn, "task_type", [
        dict(id=i, Type_Name=n, Color=c, **audit())
        for i, (n, c) in enumerate(TASK_TYPES, start=1)
    ])
    insert(conn, "countries_currency", [
        dict(id=i, Country_Name=c, Currency_Name=cur, Symbol=s, **audit())
        for i, (c, cur, s) in enumerate(CURRENCIES, start=1)
    ])
    insert(conn, "tax_type", [
        dict(id=i, Country_ID="1", Tax_Name=n, Tax_Percentage=p, **audit())
        for i, (n, p) in enumerate(TAXES, start=1)
    ])
    insert(conn, "discount_data", [
        dict(id=i, Country_ID="1", Discount_Name=n, Discount_Percentage=p, **audit())
        for i, (n, p) in enumerate(DISCOUNTS, start=1)
    ])
    insert(conn, "reservation_status", [
        dict(id=i, Reservation_Status=n, Color=c, **audit())
        for i, (n, c) in enumerate(RESERVATION_STATUSES, start=1)
    ])
    insert(conn, "room_type", [
        dict(id=i, Type_Name=n, Room_Cost=rc, Bed_Cost=bc,
             Complementry="1", Daily_Rate=d, Weekly_Rate=w, Bed_Only_Rate=bo,
             Bed_And_Breakfast_Rate=bb, Half_Board_Rate=hb, Full_Board_Rate=fb,
             **audit())
        for i, n, rc, bc, d, w, bo, bb, hb, fb in ROOM_TYPES
    ])

    # --- rooms, each with four real photographs ----------------------------
    type_name = {i: n for i, n, *_ in ROOM_TYPES}
    photo_dir = upload_dir("hotelerp_masterdata", "upload_image")

    # Four photographs per room TYPE, downloaded once and shared by every room
    # of that type. A drawn fallback covers a query that finds nothing, so a
    # room can never end up with a path to an image that was never written.
    by_type: dict[int, list[str]] = {}
    seen: set[str] = set()
    for type_id, name, *_ in ROOM_TYPES:
        shots = []
        for variant, queries in enumerate(ROOM_TYPE_QUERIES.get(name, [])):
            fname = im.hex_name("jpg")
            got = photos.best_photo(queries, prefer="openverse", skip=seen)
            if got:
                img, meta = got
                photos.cover(img, (1024, 683)).save(
                    os.path.join(photo_dir, fname), "JPEG", quality=86, optimize=True)
                photos.record(f"{name} (view {variant + 1})", meta, fname)
            else:
                im.save(im.room_image("", name, variant), photo_dir, fname)
            shots.append(f"/templates/static/upload_image/{fname}")
        while len(shots) < 4:                       # a type with no query set
            fname = im.hex_name("jpg")
            im.save(im.room_image("", name, len(shots)), photo_dir, fname)
            shots.append(f"/templates/static/upload_image/{fname}")
        by_type[type_id] = shots
        print(f"      {name:<20} {len(shots)} photo(s)")

    rows = []
    for idx, (room_no, type_id, bed_id, adults, children) in enumerate(ROOMS, start=1):
        shots = by_type[type_id]
        rows.append(dict(
            id=idx,
            Room_No=room_no,
            Room_Name=f"{type_name[type_id]} {room_no}",
            Room_Type_ID=str(type_id),
            Bed_Type_ID=str(bed_id),
            Room_Telephone=f"1{room_no}",
            Room_Image_1=shots[0], Room_Image_2=shots[1],
            Room_Image_3=shots[2], Room_Image_4=shots[3],
            Max_Adult_Occupy=str(adults),
            Max_Child_Occupy=str(children),
            # Occupancy is DERIVED from reservations by
            # `sync_room_booking_status`; every room starts free and the hotel
            # seed reconciles it once the bookings exist.
            Room_Booking_status="Available",
            Room_Working_status="Ready",
            Room_Status="UnBlocking",
            **audit(),
        ))
    insert(conn, "room", rows)

    return {"rooms": len(rows), "room_images": len(rows) * 4,
            "room_types": len(ROOM_TYPES)}

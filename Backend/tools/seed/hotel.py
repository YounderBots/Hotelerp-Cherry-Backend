"""hotelerp_hotel: a property mid-operation, told as one consistent story.

WHAT "FLOW-WISE" MEANS HERE
    Not twenty rows with assorted statuses. A booking's status, its dates, the
    money on its folio, the payments recorded against it, the state of its
    rooms and the night audit that closed the books all have to agree, because
    every screen in the application cross-checks them:

      a Checked-Out stay      is in the past, fully settled, and its rooms are
                              free to sell but flagged dirty for housekeeping
      an in-house stay        spans today, its room reads Occupied, and its
                              balance is what the guest still owes at checkout
      an arrival due today    is Confirmed with the room held, not occupied
      a Cancelled booking     carries a reason, a timestamp and an author, and
                              releases its room back to inventory
      a No-Show               is a Confirmed arrival whose date has passed
      the night audit         reports exactly the occupancy and revenue that
                              the reservations above imply for its date

    Money is computed, never typed: every folio below is derived from the rate
    plan on the room type, so `room_amount`, tax, discount and balance
    reconcile to the paisa and the Night Audit's per-night accrual adds up.

NO TWO STAYS SHARE A ROOM ON THE SAME NIGHT
    Room allocation goes through `hold`, which enforces the same half-open
    overlap rule the API does (`arrival < other.departure AND departure >
    other.arrival`). A seed that double-books a room would make the very
    availability screen this dataset exists to demonstrate report a conflict.
"""

from __future__ import annotations

import datetime as dt
import json
import uuid

from . import images as im
from .common import COMPANY, SYSTEM, at, audit, day, insert, money, upload_dir
from .masterdata import ROOM_TYPES, ROOMS

RATE_BY_TYPE = {i: dict(daily=d, weekly=w, bed_only=bo, bed_breakfast=bb,
                        half_board=hb, full_board=fb, bed_cost=bc)
                for i, _n, _rc, bc, d, w, bo, bb, hb, fb in ROOM_TYPES}
TYPE_NAME = {i: n for i, n, *_ in ROOM_TYPES}
ROOM_BY_NO = {no: (idx, tid) for idx, (no, tid, *_r) in enumerate(ROOMS, start=1)}

# Master Data ids seeded by masterdata.py, referenced by name for readability.
TAX_GST12, TAX_GST18, TAX_NONE = 3, 4, 6
DISC_EARLY, DISC_CORP, DISC_LOYAL, DISC_FESTIVE, DISC_LONG, DISC_NONE = 1, 2, 3, 4, 5, 6
PM_CASH, PM_CREDIT, PM_DEBIT, PM_UPI, PM_NETBANK, PM_TRANSFER, PM_CORP = 1, 2, 3, 4, 5, 6, 7
ID_AADHAAR, ID_PASSPORT, ID_DL, ID_VOTER, ID_PAN, ID_COMPANY = 1, 2, 3, 4, 5, 6

DISCOUNT_PCT = {1: 10.0, 2: 15.0, 3: 5.0, 4: 20.0, 5: 12.0, 6: 0.0}
TAX_PCT = {1: 6.0, 2: 6.0, 3: 12.0, 4: 18.0, 5: 28.0, 6: 0.0}

CONFIRMED, CHECKED_IN, CHECKED_OUT = "Confirmed", "Checked-In", "Checked-Out"
CANCELLED, NO_SHOW, PENDING, ON_HOLD = "Cancelled", "No-Show", "Pending", "On Hold"


# ---------------------------------------------------------------------------
# The guest list. (salutation, first, last, id_type)
# ---------------------------------------------------------------------------
GUESTS = [
    ("Mr.", "Rohan", "Mehta", ID_AADHAAR),
    ("Ms.", "Priya", "Nair", ID_AADHAAR),
    ("Mr.", "Arjun", "Kapoor", ID_PAN),
    ("Mrs.", "Sana", "Sheikh", ID_PASSPORT),
    ("Mr.", "Vikram", "Rao", ID_DL),
    ("Ms.", "Neha", "Gupta", ID_AADHAAR),
    ("Mr.", "Karan", "Malhotra", ID_VOTER),
    ("Ms.", "Ananya", "Iyer", ID_AADHAAR),
    ("Mr.", "Farhan", "Khan", ID_PASSPORT),
    ("Ms.", "Divya", "Menon", ID_AADHAAR),
    ("Mr.", "Aditya", "Verma", ID_COMPANY),
    ("Ms.", "Ritu", "Chawla", ID_PAN),
    ("Mr.", "Suresh", "Pillai", ID_AADHAAR),
    ("Ms.", "Meera", "Desai", ID_DL),
    ("Mr.", "Ibrahim", "Ansari", ID_PASSPORT),
    ("Ms.", "Lakshmi", "Krishnan", ID_AADHAAR),
    ("Mr.", "Yusuf", "Sheikh", ID_VOTER),
    ("Ms.", "Pooja", "Bhatt", ID_AADHAAR),
    ("Mr.", "Rithvik", "Prabhu", ID_PAN),
    ("Ms.", "Kavya", "Reddy", ID_AADHAAR),
    ("Mr.", "Nikhil", "Joshi", ID_COMPANY),
    ("Ms.", "Fatima", "Begum", ID_PASSPORT),
    ("Mr.", "Sandeep", "Kulkarni", ID_DL),
    ("Ms.", "Anjali", "Saxena", ID_AADHAAR),
]


class Ledger:
    """Allocates rooms without ever double-booking one."""

    def __init__(self):
        self.held: list[tuple[str, dt.date, dt.date]] = []

    def free(self, room_no: str, arrival: dt.date, departure: dt.date) -> bool:
        # Half-open: a departure and an arrival may share a date (same-day turnover).
        return not any(
            no == room_no and arrival < end and departure > start
            for no, start, end in self.held
        )

    def hold(self, wanted: list[str], arrival: dt.date, departure: dt.date) -> list[str]:
        for room_no in wanted:
            if not self.free(room_no, arrival, departure):
                raise AssertionError(
                    f"seed would double-book room {room_no} "
                    f"for {arrival}..{departure}"
                )
            self.held.append((room_no, arrival, departure))
        return wanted


def folio(room_nos, rate_type, nights, *, tax_id, discount_id,
          extra_beds=0, extra_charges=0.0):
    """Price a stay from the rate plan. The only place money is decided."""
    room_amount = 0.0
    bed_cost_total = 0.0
    for no in room_nos:
        _idx, type_id = ROOM_BY_NO[no]
        rates = RATE_BY_TYPE[type_id]
        if rate_type == "weekly":
            weeks, spare = divmod(nights, 7)
            room_amount += rates["weekly"] * weeks + rates["daily"] * spare
        else:
            room_amount += rates[rate_type] * nights
        bed_cost_total += rates["bed_cost"] * extra_beds * nights

    room_amount = money(room_amount)
    extra_bed_cost = money(bed_cost_total)
    extra_charges = money(extra_charges)

    gross = money(room_amount + extra_bed_cost + extra_charges)
    discount_pct = DISCOUNT_PCT[discount_id]
    discount_amount = money(gross * discount_pct / 100.0)
    taxable = money(gross - discount_amount)
    tax_pct = TAX_PCT[tax_id]
    tax_amount = money(taxable * tax_pct / 100.0)
    overall = money(taxable + tax_amount)

    return dict(
        room_amount=room_amount, extra_bed_cost=extra_bed_cost,
        extra_charges=extra_charges, total_amount=room_amount,
        discount_percentage=discount_pct, discount_amount=discount_amount,
        tax_percentage=tax_pct, tax_amount=tax_amount,
        overall_amount=overall,
    )


# ---------------------------------------------------------------------------
# The bookings. Each entry is one stay in the property's current picture.
# (guest_index, rooms, arrival_offset, nights, status, rate_type, tax, discount,
#  payments, extra_beds, extra_charges, room_comp, common_comp, note)
# `payments` is a list of (offset_from_arrival, fraction_of_overall, method).
# ---------------------------------------------------------------------------
BOOKINGS = [
    # ---- settled history: checked out, paid in full -----------------------
    (0,  ["101"],        -22, 3, CHECKED_OUT, "daily",         TAX_GST12, DISC_EARLY,
     [(-14, 0.30, PM_UPI), (3, 0.70, PM_CREDIT)], 0, 0,    "Welcome Drink", "", None),
    (1,  ["203"],        -18, 4, CHECKED_OUT, "bed_breakfast", TAX_GST12, DISC_NONE,
     [(0, 1.00, PM_CREDIT)], 0, 1200, "Breakfast Buffet", "Airport Pickup", None),
    (2,  ["301"],        -15, 5, CHECKED_OUT, "half_board",    TAX_GST18, DISC_CORP,
     [(0, 0.50, PM_TRANSFER), (5, 0.50, PM_TRANSFER)], 1, 0, "", "Evening Tea", None),
    (3,  ["401"],        -12, 2, CHECKED_OUT, "daily",         TAX_GST18, DISC_LOYAL,
     [(0, 1.00, PM_CASH)], 0, 850,  "Fruit Basket", "", None),
    (4,  ["102", "103"], -10, 3, CHECKED_OUT, "daily",         TAX_GST12, DISC_FESTIVE,
     [(-2, 0.40, PM_UPI), (3, 0.60, PM_DEBIT)], 0, 0, "", "Newspaper", None),
    (5,  ["502"],        -8,  4, CHECKED_OUT, "full_board",    TAX_GST18, DISC_NONE,
     [(0, 1.00, PM_CREDIT)], 2, 3400, "Late Checkout", "Spa", None),

    # ---- in house right now ----------------------------------------------
    (6,  ["201"],        -3,  6, CHECKED_IN,  "bed_breakfast", TAX_GST12, DISC_NONE,
     [(0, 0.50, PM_UPI)], 0, 0,     "Breakfast Buffet", "", None),
    (7,  ["302"],        -2,  5, CHECKED_IN,  "daily",         TAX_GST18, DISC_CORP,
     [(0, 0.60, PM_CORP)], 0, 1500, "", "Conference Hall", None),
    (8,  ["402"],        -4,  8, CHECKED_IN,  "weekly",        TAX_GST18, DISC_LONG,
     [(0, 0.35, PM_TRANSFER)], 1, 0, "Welcome Drink", "", None),
    (9,  ["104"],        -1,  4, CHECKED_IN,  "daily",         TAX_GST12, DISC_LOYAL,
     [(0, 1.00, PM_CASH)], 0, 0,    "", "", None),
    # departing today -- the two rows the Departures panel is meant to show
    (10, ["205"],        -2,  2, CHECKED_IN,  "bed_breakfast", TAX_GST12, DISC_NONE,
     [(0, 0.70, PM_UPI)], 0, 620,   "Breakfast Buffet", "", None),
    (11, ["303"],        -5,  5, CHECKED_IN,  "half_board",    TAX_GST18, DISC_EARLY,
     [(0, 0.50, PM_CREDIT), (4, 0.25, PM_UPI)], 0, 0, "", "Evening Tea", None),

    # ---- arriving today ---------------------------------------------------
    (12, ["105"],         0,  2, CONFIRMED,   "daily",         TAX_GST12, DISC_NONE,
     [(0, 0.25, PM_UPI)], 0, 0,     "Welcome Drink", "", None),
    (13, ["206"],         0,  3, CONFIRMED,   "bed_breakfast", TAX_GST12, DISC_EARLY,
     [(-5, 0.30, PM_CREDIT)], 0, 0, "Breakfast Buffet", "Airport Pickup", None),
    (14, ["601"],         0,  4, CONFIRMED,   "full_board",    TAX_GST18, DISC_CORP,
     [(-7, 0.50, PM_TRANSFER)], 0, 5000, "Fruit Basket", "Spa", None),

    # ---- future, confirmed ------------------------------------------------
    (15, ["304"],         3,  3, CONFIRMED,   "daily",         TAX_GST18, DISC_NONE,
     [(-1, 0.20, PM_UPI)], 0, 0,    "", "", None),
    (16, ["106", "107"],  5,  2, CONFIRMED,   "daily",         TAX_GST12, DISC_FESTIVE,
     [], 0, 0,                      "Welcome Drink", "", None),
    (17, ["403"],         8,  5, CONFIRMED,   "half_board",    TAX_GST18, DISC_LONG,
     [(-2, 0.30, PM_CREDIT)], 1, 0, "", "Gymnasium", None),
    (18, ["501"],        12,  4, CONFIRMED,   "full_board",    TAX_GST18, DISC_NONE,
     [], 1, 2200,                   "Late Checkout", "Spa", None),
    (19, ["202"],        16,  3, CONFIRMED,   "bed_breakfast", TAX_GST12, DISC_LOYAL,
     [], 0, 0,                      "Breakfast Buffet", "", None),

    # ---- not proceeding ---------------------------------------------------
    (20, ["305"],         6,  3, CANCELLED,   "daily",         TAX_GST18, DISC_NONE,
     [], 0, 0, "", "", "Guest request — travel plans changed"),
    (21, ["108"],         9,  2, CANCELLED,   "daily",         TAX_GST12, DISC_NONE,
     [(-3, 0.20, PM_UPI)], 0, 0, "", "", "Duplicate booking — kept RES on 106"),
    (22, ["204"],        -6,  2, NO_SHOW,     "daily",         TAX_GST12, DISC_NONE,
     [], 0, 0, "", "", None),

    # ---- enquiries not yet firm -------------------------------------------
    (23, ["301"], 20, 3, PENDING, "daily", TAX_GST12, DISC_NONE,
     [], 0, 0, "", "", None),
    # A held option the desk has not released or confirmed yet.
    (2,  ["401"], 25, 2, ON_HOLD, "daily", TAX_GST18, DISC_NONE,
     [], 0, 0, "", "", None),
]


def seed(conn, business_date: dt.date) -> dict:
    proof_dir = upload_dir("hotelerp_hotel", "identity_proofs")
    incident_dir = upload_dir("hotelerp_hotel", "room_incidents")

    ledger = Ledger()
    reservations, payments = [], []
    payment_id = 1
    occupied_today, dirty_rooms = set(), set()

    for n, entry in enumerate(BOOKINGS, start=1):
        (gi, rooms, arr_off, nights, status, rate_type, tax_id, disc_id,
         pays, beds, extras, room_comp, common_comp, note) = entry

        salutation, first, last, id_type = GUESTS[gi % len(GUESTS)]
        arrival = day(arr_off)
        departure = arrival + dt.timedelta(days=nights)

        # A cancelled or no-show booking never held inventory.
        if status not in (CANCELLED, NO_SHOW):
            ledger.hold(rooms, arrival, departure)

        f = folio(rooms, rate_type, nights, tax_id=tax_id, discount_id=disc_id,
                  extra_beds=beds, extra_charges=extras)

        ref = f"RES-{business_date:%Y%m}-{n:04d}"
        token = str(uuid.uuid4())
        created = at(arrival - dt.timedelta(days=max(1, 3 + n % 9)), 10, 30)

        # Identity proof: a real specimen file per reservation.
        proof_name = None
        if status != PENDING:
            proof_name = im.dashed_name("jpg")
            im.save(
                im.identity_document(f"{first} {last}",
                                     ["Aadhaar Card", "Passport", "Driving License",
                                      "Voter ID Card", "PAN Card", "Company ID Card"][id_type - 1],
                                     ref),
                proof_dir, proof_name)

        paid = 0.0
        for off, fraction, method_id in pays:
            amount = money(f["overall_amount"] * fraction)
            paid = money(paid + amount)
            payments.append(dict(
                id=payment_id, reservation_id=ref, user_id=SYSTEM, amount=amount,
                paid_date=arrival + dt.timedelta(days=off),
                payment_method=["Cash", "Credit Card", "Debit Card", "UPI",
                                "Net Banking", "Bank Transfer",
                                "Corporate Billing"][method_id - 1],
                # Each payment carries its OWN token: the column is uniquely
                # indexed, so reusing the reservation's would collide on the
                # second instalment. The link back to the booking is
                # `reservation_id`, which holds the reservation reference.
                token=str(uuid.uuid4()),
                **audit(created=at(arrival + dt.timedelta(days=off), 12, 15)),
            ))
            payment_id += 1

        # A completed stay is settled in full: the closing payment is whatever
        # the folio still shows, so no checked-out booking carries a balance.
        if status == CHECKED_OUT and paid < f["overall_amount"]:
            amount = money(f["overall_amount"] - paid)
            payments.append(dict(
                id=payment_id, reservation_id=ref, user_id=SYSTEM, amount=amount,
                paid_date=departure, payment_method="Credit Card",
                token=str(uuid.uuid4()),
                **audit(created=at(departure, 11, 0))))
            payment_id += 1
            paid = f["overall_amount"]

        balance = money(f["overall_amount"] - paid)

        if status == CHECKED_IN:
            occupied_today.update(rooms)
        if status == CHECKED_OUT:
            dirty_rooms.update(rooms)

        cancelled_at = cancelled_by = None
        if status == CANCELLED:
            cancelled_at = at(arrival - dt.timedelta(days=2), 15, 40)
            cancelled_by = SYSTEM

        reservations.append(dict(
            id=n,
            room_reservation_id=ref,
            salutation=salutation, first_name=first, last_name=last,
            email=f"{first.lower()}.{last.lower().replace(chr(39), '')}@gmail.com",
            phone_number=f"98{40000000 + n * 137:08d}"[:10],
            arrival_date=arrival, departure_date=departure,
            no_of_nights=nights, no_of_rooms=len(rooms),
            reservation_status=status,
            identity_type_id=id_type,
            proof_document=proof_name,
            room_ids=json.dumps([ROOM_BY_NO[r][0] for r in rooms]),
            room_type_ids=json.dumps([ROOM_BY_NO[r][1] for r in rooms]),
            room_no=json.dumps(rooms),
            rate_type=json.dumps([rate_type] * len(rooms)),
            no_of_adults=min(2 + n % 2, 4), no_of_children=n % 3,
            room_complementary=room_comp, common_complementary=common_comp,
            tax_type_id=tax_id, discount_type_id=disc_id,
            room_amount=f["room_amount"], extra_charges=f["extra_charges"],
            tax_percentage=f["tax_percentage"], tax_amount=f["tax_amount"],
            discount_percentage=f["discount_percentage"],
            discount_amount=f["discount_amount"],
            overall_amount=f["overall_amount"],
            payment_method_id=(pays[0][2] if pays else PM_CASH),
            paying_amount=paid, paid_amount=paid, balance_amount=balance,
            extra_amount=0.0, extra_bed_count=beds,
            extra_bed_cost=f["extra_bed_cost"], total_amount=f["total_amount"],
            booking_status_id=None,
            reservation_type="CHECKIN" if status == CHECKED_IN else "RESERVATION",
            confirmation_code=uuid.uuid4().hex[:8].upper(),
            token=token,
            cancellation_reason=note if status == CANCELLED else None,
            cancelled_at=cancelled_at, cancelled_by=cancelled_by,
            **audit(created=created),
        ))

    insert(conn, "room_reservation", reservations)
    insert(conn, "reservation_amount_paid_history", payments)

    return {
        "reservations": len(reservations),
        "payments": len(payments),
        "occupied_today": sorted(occupied_today),
        "dirty_rooms": sorted(dirty_rooms),
        "proofs": sum(1 for r in reservations if r["proof_document"]),
        "incident_dir": incident_dir,
    }


# ---------------------------------------------------------------------------
# Housekeeping, incidents, enquiries and the closed night
# ---------------------------------------------------------------------------

HOUSEKEEPING_STAFF = [
    ("5", "Imran", "Khan"),
    ("6", "Lakshmi", "Iyer"),
]

INCIDENTS = [
    ("204", -6, "18:20", "Bathroom tap dripping; floor wet on arrival.", "Medium",
     "Imran Khan", "Tap washer replaced, floor dried and room re-inspected."),
    ("302", -3, "09:05", "Guest reported air conditioning not cooling.", "High",
     "Lakshmi Iyer", "Maintenance recharged the unit; guest confirmed satisfied."),
    ("108", -1, "21:40", "Reading lamp shade cracked in dormitory bay 3.", "Low",
     "Imran Khan", "Shade replaced from stores; no charge raised to guest."),
]

ENQUIRIES = [
    ("Online", "Deepak Anand", "Asked for tariff on two Deluxe rooms in October.",
     "Rate sheet emailed; awaiting confirmation.", "In Progress"),
    ("Offline", "Sridevi Raman", "Walk-in asking about banquet hall for a reception.",
     "Banquet manager to call back with availability.", "In Progress"),
    ("Online", "Michael Fernandes", "Airport pickup availability for a late arrival.",
     "Confirmed pickup can be arranged with 12 hours' notice.", "Completed"),
    ("Online", "Aisha Rahman", "Requested a quiet room away from the lift.",
     "Noted on the booking; room 305 allocated.", "Completed"),
    ("Offline", "Ganesh Iyer", "Corporate tie-up enquiry for monthly stays.",
     "Corporate rate card shared with the company's admin.", "In Progress"),
    ("Online", "Sarah Thomas", "Asked whether the pool is open to day guests.",
     "Advised pool access is for in-house guests only.", "Completed"),
]

BOOKING_ENQUIRIES = [
    ("Mr.", "Deepak", "Anand", "9840155501", [2, 2], 30, 3, 2, 0),
    ("Ms.", "Sridevi", "Raman", "9840155502", [5], 34, 2, 2, 2),
    ("Mr.", "Ganesh", "Iyer", "9840155503", [4], 40, 5, 1, 0),
]


def seed_operations(conn, business_date, occupied_today, dirty_rooms, incident_dir):
    """Everything that surrounds the reservations: housekeeping, incidents,
    enquiries, the business date and the last completed night audit."""

    # --- housekeeping tasks -------------------------------------------------
    # Departed rooms are queued for cleaning; occupied rooms get their daily
    # service. This is the same handover `mark_rooms_for_housekeeping` performs
    # at checkout, expressed as the tasks a supervisor would actually raise.
    tasks, tid = [], 1
    for i, room_no in enumerate(sorted(dirty_rooms)):
        emp_id, first, last = HOUSEKEEPING_STAFF[i % len(HOUSEKEEPING_STAFF)]
        tasks.append(dict(
            id=tid, employee_id=emp_id, first_name=first, last_name=last,
            schedule_date=business_date, schedule_time=dt.time(9 + i % 4, 0),
            room_no=int(room_no), task_type="Deep Cleaning",
            assign_staff=f"{first} {last}", task_status="Pending",
            room_status="Not Ready", lost_found=None,
            special_instructions="Departure clean before the room is re-sold.",
            status="ACTIVE", created_by=1, created_at=at(business_date, 8, 30),
            updated_at=None, updated_by=None, company_id=int(COMPANY)))
        tid += 1

    for i, room_no in enumerate(sorted(occupied_today)):
        emp_id, first, last = HOUSEKEEPING_STAFF[i % len(HOUSEKEEPING_STAFF)]
        tasks.append(dict(
            id=tid, employee_id=emp_id, first_name=first, last_name=last,
            schedule_date=business_date, schedule_time=dt.time(10 + i % 5, 30),
            room_no=int(room_no), task_type="Daily Cleaning",
            assign_staff=f"{first} {last}",
            task_status="Completed" if i % 2 == 0 else "In Progress",
            room_status="Occupied", lost_found=None,
            special_instructions="Guest in house — service while the room is vacant.",
            status="ACTIVE", created_by=1, created_at=at(business_date, 8, 30),
            updated_at=None, updated_by=None, company_id=int(COMPANY)))
        tid += 1
    insert(conn, "housekeeper_task", tasks)

    # --- incident log, each with a photograph -------------------------------
    incidents = []
    for i, (room_no, off, time_s, desc, severity, staff, action) in enumerate(
            INCIDENTS, start=1):
        fname = im.hex_name("jpg")
        im.save(im.incident_photo(room_no, desc), incident_dir, fname)
        hh, mm = map(int, time_s.split(":"))
        incidents.append(dict(
            id=i, room_no=int(room_no), incident_date=day(off),
            incident_time=dt.time(hh, mm), incident_description=desc,
            involved_staff=staff, severity=severity,
            witnesses="Duty Manager", actions_taken=action,
            reported_by=staff, report_date=day(off),
            attachment_file=fname,
            **audit(created=at(day(off), hh, mm))))
    insert(conn, "hsk_room_incident", incidents)

    # --- guest enquiries ----------------------------------------------------
    insert(conn, "inquiry", [
        dict(id=i, inquiry_mode=mode, guest_name=name, response=resp,
             follow_up=follow, incidents=None, inquiry_status=state,
             **audit(created=at(day(-(i % 7)), 11, 0)))
        for i, (mode, name, resp, follow, state) in enumerate(ENQUIRIES, start=1)
    ])

    # --- booking enquiries not yet turned into reservations -----------------
    insert(conn, "room_booking", [
        dict(id=i, room_booking_id=f"RB-{uuid.uuid4().hex[:8].upper()}",
             salutation=sal, first_name=first, last_name=last,
             phone_number=phone,
             email=f"{first.lower()}.{last.lower()}@gmail.com",
             arrival_date=day(arr), departure_date=day(arr + nights),
             no_of_nights=nights, room_type=json.dumps(types),
             no_of_rooms=len(types), no_of_adults=adults, no_of_children=children,
             **audit(created=at(day(-2), 16, 20)))
        for i, (sal, first, last, phone, types, arr, nights, adults, children)
        in enumerate(BOOKING_ENQUIRIES, start=1)
    ])

    # --- the business date and the night that closed it ---------------------
    # The audit covers YESTERDAY: today is open and still trading, which is what
    # a live property looks like at any moment during the day.
    audited = business_date - dt.timedelta(days=1)
    insert(conn, "hotel_business_date", [dict(
        id=1, business_date=business_date,
        last_audit_at=at(business_date, 2, 15), last_audit_by=SYSTEM,
        status="ACTIVE", created_by=SYSTEM, created_at=at(audited, 2, 15),
        updated_at=at(business_date, 2, 15), updated_by=SYSTEM,
        company_id=COMPANY)])
    return {"tasks": len(tasks), "incidents": len(incidents),
            "enquiries": len(ENQUIRIES), "booking_enquiries": len(BOOKING_ENQUIRIES),
            "audited_date": audited}

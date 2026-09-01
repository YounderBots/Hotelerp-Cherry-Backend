"""The Reservation module's business rules: availability, pricing, status.

WHY THIS IS A MODULE AND NOT INLINE IN THE CONTROLLER
    Three rules decide whether a booking is valid, and every one of them was
    previously either absent or implemented in the browser:

      * whether a room can be sold for a date range  -- was not checked at all,
        so two guests could hold the same room on the same night;
      * what the stay costs                          -- was computed in
        payment.jsx and posted as a plain form field, so `overall_amount=1` on
        an 11,000-a-night suite was accepted verbatim;
      * which status may follow which                -- was unconstrained, so a
        cancelled booking could be edited straight to checked-in.

    They are collected here so create, update, check-in, check-out and cancel
    all reach the same answer, and so each rule can be read (and tested)
    without a running HTTP stack.

THE MONEY RULE, STATED ONCE
    The client supplies *inputs* -- which rooms, which dates, which rate type,
    which tax and discount rows, staff-entered extra charges, and a negotiated
    room amount if there is one. It never supplies *results*. Every derived
    figure (tax, discount, overall, balance, extra) is computed here from
    master data and returned to the caller. A total that arrives in a request
    body is ignored, not validated -- validating it would still leave the
    client deciding what "correct" means.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Iterable, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from models import models
from models.masterdata import (
    MasterDiscount,
    MasterIdentityProof,
    MasterPaymentMethod,
    MasterReservationStatus,
    MasterRoom,
    MasterRoomType,
    MasterTaxType,
)

ACTIVE = "ACTIVE"

# ---------------------------------------------------------------------------
# Rate types
# ---------------------------------------------------------------------------
# Maps a selectable rate type onto the column of `room_type` that prices it.
# Everything bills per night except `weekly`, which bills per started week.
#
# The frontend key set and this table are the contract between the two; the
# previous frontend copy of this map spelled bed & breakfast
# "bed_and_breakfast_rate" while the API returns "bed_breakfast_rate", so
# choosing that rate silently priced the room at zero.
RATE_COLUMN = {
    "daily": "Daily_Rate",
    "weekly": "Weekly_Rate",
    "bed_only": "Bed_Only_Rate",
    "bed_breakfast": "Bed_And_Breakfast_Rate",
    "half_board": "Half_Board_Rate",
    "full_board": "Full_Board_Rate",
}
DEFAULT_RATE_TYPE = "daily"
WEEKLY_RATE_TYPE = "weekly"

# ---------------------------------------------------------------------------
# Reservation types
# ---------------------------------------------------------------------------
RESERVATION = "RESERVATION"
GROUP_RESERVATION = "GROUP_RESERVATION"
CHECKIN = "CHECKIN"
RESERVATION_TYPES = (RESERVATION, GROUP_RESERVATION, CHECKIN)

# ---------------------------------------------------------------------------
# Status vocabulary
# ---------------------------------------------------------------------------
# The labels below MUST exist as rows in masterdata.reservation_status. They
# are named here only so the transition table can refer to them; whether a
# given status is selectable is still decided by the master table at runtime
# (see `load_status_vocabulary`).
CONFIRMED = "Confirmed"
CHECKED_IN = "Checked-In"
CHECKED_OUT = "Checked-Out"
CANCELLED = "Cancelled"
NO_SHOW = "No-Show"
PENDING = "Pending"
ON_HOLD = "On Hold"

# Statuses that release the room back to inventory. Compared case- and
# punctuation-insensitively so a master row spelled "No Show" still counts.
NON_BLOCKING_STATUSES = {"cancelled", "canceled", "noshow"}

# Pre-arrival states: the booking is held but the guest has not walked in.
PRE_ARRIVAL = (PENDING, ON_HOLD, CONFIRMED)

# Terminal states: the stay is over or was abandoned. Nothing follows.
TERMINAL = (CHECKED_OUT, CANCELLED, NO_SHOW)

# The allowed moves. A status may always stay where it is (an edit that does
# not change status must not be blocked), which is handled in `can_transition`
# rather than by listing every self-edge here.
#
# Cancelled -> Checked-In is the transition this table exists to refuse: the
# API used to accept it, which both resurrected a released room and let a
# cancelled booking start accruing revenue.
ALLOWED_TRANSITIONS = {
    PENDING: (CONFIRMED, ON_HOLD, CHECKED_IN, CANCELLED, NO_SHOW),
    ON_HOLD: (CONFIRMED, PENDING, CHECKED_IN, CANCELLED, NO_SHOW),
    CONFIRMED: (CHECKED_IN, ON_HOLD, CANCELLED, NO_SHOW),
    CHECKED_IN: (CHECKED_OUT,),
    CHECKED_OUT: (),
    CANCELLED: (),
    NO_SHOW: (),
}


class RuleError(Exception):
    """A business rule refused the operation.

    `status_code` distinguishes "you asked for something impossible" (400) from
    "someone else got there first" (409), which the availability check needs so
    a losing concurrent booker can be told to pick another room rather than
    told their input was malformed.
    """

    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def money(value) -> float:
    """Round to 2dp for storage and comparison.

    Every figure that reaches the database goes through this. Without it the
    binary float for 1680.0000000000002 is what gets stored, and the View modal
    then shows a total that does not equal the sum of its parts.
    """
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def as_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def as_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalise_status(value) -> str:
    """Fold a status label for comparison: case, spaces and hyphens all drop out."""
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())


def releases_inventory(status) -> bool:
    """True when a reservation in this status no longer occupies its rooms."""
    return normalise_status(status) in NON_BLOCKING_STATUSES


def nights_between(arrival: date, departure: date) -> int:
    """Nights in a stay. 10 Aug -> 12 Aug is 2.

    Derived here and nowhere else. `no_of_nights` used to be a form field, and
    the API accepted 99 for a two-night stay (and -5 for any stay), which then
    flowed into the rate calculation.
    """
    return (departure - arrival).days


# ---------------------------------------------------------------------------
# Master data lookups
# ---------------------------------------------------------------------------
def load_status_vocabulary(db: Session, company_id) -> list[str]:
    """The property's active reservation statuses, in master-data order."""
    rows = (
        db.query(MasterReservationStatus)
        .filter(
            MasterReservationStatus.company_id == str(company_id),
            MasterReservationStatus.status == ACTIVE,
        )
        .order_by(MasterReservationStatus.id.asc())
        .all()
    )
    return [r.Reservation_Status for r in rows]


def resolve_status(db: Session, company_id, requested) -> str:
    """Match `requested` against the master vocabulary, or raise.

    Matching is fold-insensitive so "no show", "No-Show" and "NOSHOW" all
    resolve to whichever spelling the property actually stores, and the stored
    spelling is what gets written. That keeps one canonical value in the column
    no matter how the caller spelled it.
    """
    if not requested or not str(requested).strip():
        raise RuleError("reservation_status is required")

    vocabulary = load_status_vocabulary(db, company_id)
    if not vocabulary:
        raise RuleError(
            "No reservation statuses are configured for this property. "
            "Add them under Master Data → Reservation Status first.",
            status_code=409,
        )

    wanted = normalise_status(requested)
    for label in vocabulary:
        if normalise_status(label) == wanted:
            return label

    raise RuleError(
        f"'{requested}' is not a configured reservation status. "
        f"Valid statuses: {', '.join(vocabulary)}"
    )


def can_transition(current: Optional[str], target: str) -> bool:
    """Whether `current -> target` is a legal move."""
    if normalise_status(current) == normalise_status(target):
        return True  # not a transition at all
    if not current:
        return True  # creating: any status is an opening position

    for source, targets in ALLOWED_TRANSITIONS.items():
        if normalise_status(source) != normalise_status(current):
            continue
        return any(normalise_status(t) == normalise_status(target) for t in targets)

    # A status the transition table does not know about (a property-defined
    # extra row in reservation_status). Constraining it would refuse a status
    # the operator deliberately configured, so it is left open.
    return True


def early_departure(
    arrival: date, booked_departure: date, booked_nights: int, on_date: date
) -> tuple[bool, int, int]:
    """Nights actually used when a guest leaves on `on_date`.

    Returns (is_early, actual_nights, nights_unused).

    `on_date` is passed in rather than read from the clock so the caller owns
    "today" -- the same reason the Night Audit module keeps a business date.
    It also makes this testable without freezing time.

    THE TWO EDGES THAT MATTER
        Leaving on or after the booked departure is not an early departure at
        all; it is an ordinary checkout and nothing is re-priced.

        Leaving on the arrival date is a same-day departure, and it still bills
        one night. A hotel does not sell a zero-night stay, and treating it as
        one would price the room at nothing.
    """
    if on_date >= booked_departure or on_date <= arrival:
        return False, booked_nights, 0

    actual = max(1, nights_between(arrival, on_date))
    return True, actual, max(0, booked_nights - actual)


def stay_has_ended(departure: date, on_date: date) -> bool:
    """Whether a stay is over, for the purpose of refusing a check-in.

    STRICTLY earlier than the departure date, not on-or-earlier. A one-night
    stay that arrived yesterday departs TODAY, and checking that guest in
    today is ordinary front-desk work -- a late-night arrival written up after
    midnight, or a booking the desk is catching up on.

    The first version of this guard used <=, so it refused every same-day
    departure with a message claiming the departure date had already passed
    when it had not.
    """
    return departure < on_date


def can_offer(current: Optional[str], target: str) -> bool:
    """Whether `target` is worth OFFERING as an action on a booking at `current`.

    `can_transition` answers a different question -- "is this move legal" --
    and it deliberately treats staying put as legal, because an edit that does
    not change the status must not be refused.

    That makes it the wrong test for a button. Asked directly, it said a
    cancelled booking could be cancelled, so the UI offered "Cancel
    reservation" on a reservation that was already cancelled. An action that
    would change nothing reads as one that silently failed.
    """
    if normalise_status(current) == normalise_status(target):
        return False
    return can_transition(current, target)


def assert_transition(current: Optional[str], target: str) -> None:
    if can_transition(current, target):
        return
    raise RuleError(
        f"A reservation that is {current} cannot become {target}.",
        status_code=409,
    )


def _lookup_or_raise(db, model, pk, company_id, label: str, *, required: bool):
    """Fetch an active master row by id, or explain which one was wrong."""
    if pk in (None, "", 0):
        if required:
            raise RuleError(f"{label} is required")
        return None
    try:
        pk = int(pk)
    except (TypeError, ValueError):
        raise RuleError(f"{label} must be a number")

    row = (
        db.query(model)
        .filter(
            model.id == pk,
            model.company_id == str(company_id),
            model.status == ACTIVE,
        )
        .first()
    )
    if not row:
        raise RuleError(f"{label} {pk} does not exist for this property")
    return row


def resolve_payment_method(db, pk, company_id, *, required=True):
    return _lookup_or_raise(db, MasterPaymentMethod, pk, company_id, "Payment method", required=required)


def resolve_identity_type(db, pk, company_id, *, required=True):
    return _lookup_or_raise(db, MasterIdentityProof, pk, company_id, "Identity type", required=required)


def resolve_tax_type(db, pk, company_id):
    return _lookup_or_raise(db, MasterTaxType, pk, company_id, "Tax type", required=False)


def resolve_discount_type(db, pk, company_id):
    return _lookup_or_raise(db, MasterDiscount, pk, company_id, "Discount type", required=False)


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------
def overlapping_reservations(
    db: Session,
    company_id,
    arrival: date,
    departure: date,
    *,
    exclude_id: Optional[int] = None,
):
    """Live reservations whose stay intersects [arrival, departure).

    The comparison is half-open on purpose: a departure on the 5th and an
    arrival on the 5th are NOT a conflict, because the first guest leaves in
    the morning and the second arrives in the afternoon. `arrival < other.departure
    AND departure > other.arrival` expresses exactly that, and is what makes
    same-day turnover bookable.
    """
    query = db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == str(company_id),
        models.RoomReservation.status == ACTIVE,
        models.RoomReservation.arrival_date < departure,
        models.RoomReservation.departure_date > arrival,
    )
    if exclude_id is not None:
        query = query.filter(models.RoomReservation.id != exclude_id)
    return query.all()


def booked_room_windows(
    db: Session,
    company_id,
    arrival: date,
    departure: date,
    *,
    exclude_id: Optional[int] = None,
) -> dict[int, list[tuple[date, date]]]:
    """{room_id: [(from, to), ...]} for rooms that are taken in the window.

    Windows are clipped to the query range and merged, so a room held by two
    back-to-back bookings reports one continuous blocked span rather than two
    the caller has to stitch together.
    """
    raw: dict[int, list[tuple[date, date]]] = {}

    for reservation in overlapping_reservations(
        db, company_id, arrival, departure, exclude_id=exclude_id
    ):
        # A cancelled or no-show booking never occupies the room.
        if releases_inventory(reservation.reservation_status):
            continue

        start = max(reservation.arrival_date, arrival)
        end = min(reservation.departure_date, departure)

        for room_id in reservation.room_ids or []:
            try:
                room_id = int(room_id)
            except (TypeError, ValueError):
                continue
            raw.setdefault(room_id, []).append((start, end))

    merged: dict[int, list[tuple[date, date]]] = {}
    for room_id, windows in raw.items():
        out: list[tuple[date, date]] = []
        for start, end in sorted(windows):
            if out and start <= out[-1][1]:
                out[-1] = (out[-1][0], max(out[-1][1], end))
            else:
                out.append((start, end))
        merged[room_id] = out
    return merged


def lock_rooms(db: Session, room_ids: Iterable[int]) -> None:
    """Take a row lock on each room for the rest of the transaction.

    THIS IS THE DOUBLE-BOOKING GUARD.

    Checking availability and then inserting is two statements, and between
    them another request can run the same check and reach the same answer --
    both see the room free, both book it. Re-reading more carefully does not
    help; the two transactions genuinely do not see each other's uncommitted
    rows.

    Locking the master `room` rows first makes the pair atomic: the second
    booker blocks on `SELECT ... FOR UPDATE` until the first commits, and by
    the time it proceeds the first booking is visible to its availability
    check. The room row is the natural mutex because it is the thing being
    contended, it already exists, and every booking path touches it.

    Ordering by id prevents the classic deadlock where two multi-room bookings
    grab the same pair of rooms in opposite order.
    """
    ids = sorted({int(r) for r in room_ids})
    if not ids:
        return
    placeholders = ", ".join(f":r{i}" for i in range(len(ids)))
    params = {f"r{i}": rid for i, rid in enumerate(ids)}
    from models.masterdata import MASTERDATA_SCHEMA

    db.execute(
        text(
            f"SELECT id FROM `{MASTERDATA_SCHEMA}`.`room` "
            f"WHERE id IN ({placeholders}) FOR UPDATE"
        ),
        params,
    )


def load_rooms(db: Session, company_id, room_ids: Iterable[int]) -> dict[int, MasterRoom]:
    ids = [int(r) for r in room_ids]
    if not ids:
        return {}
    rows = (
        db.query(MasterRoom)
        .filter(
            MasterRoom.id.in_(ids),
            MasterRoom.company_id == str(company_id),
            MasterRoom.status == ACTIVE,
        )
        .all()
    )
    return {r.id: r for r in rows}


def load_room_types(db: Session, company_id, type_ids: Iterable[int]) -> dict[int, MasterRoomType]:
    ids = [int(t) for t in type_ids if t not in (None, "")]
    if not ids:
        return {}
    rows = (
        db.query(MasterRoomType)
        .filter(
            MasterRoomType.id.in_(ids),
            MasterRoomType.company_id == str(company_id),
            MasterRoomType.status == ACTIVE,
        )
        .all()
    )
    return {r.id: r for r in rows}


def assert_rooms_bookable(
    db: Session,
    company_id,
    room_ids: list[int],
    arrival: date,
    departure: date,
    *,
    exclude_id: Optional[int] = None,
    occupancy: Optional[dict[int, tuple[int, int]]] = None,
) -> dict[int, MasterRoom]:
    """Every gate a room has to pass before it can be sold. Returns the rooms.

    Call `lock_rooms` first if this is guarding a write -- on its own this is
    a read, and a read cannot stop a concurrent booking.

    Deliberately NOT a gate: `Room_Booking_status`. That column is a snapshot
    of whether the room is occupied *right now*, and the UI was treating it as
    a booking gate, so a room occupied today could not be booked for any future
    date -- thirteen of this property's twenty-five rooms were unsellable for
    every date in the calendar. Whether a room is free on a given night is a
    question about that night's reservations, which is what the overlap check
    below answers.
    """
    if not room_ids:
        raise RuleError("Select at least one room")

    if len(set(room_ids)) != len(room_ids):
        raise RuleError("The same room was selected more than once")

    rooms = load_rooms(db, company_id, room_ids)

    missing = [r for r in room_ids if r not in rooms]
    if missing:
        raise RuleError(
            f"Room {missing[0]} does not exist for this property"
            if len(missing) == 1
            else f"Rooms {', '.join(str(m) for m in missing)} do not exist for this property"
        )

    # Out of order. `Room_Status` holds Blocking/UnBlocking; only an explicit
    # block is disqualifying, because the column also carries the legacy value
    # "ACTIVE" on rows created before that vocabulary settled.
    blocked = [
        rooms[r].Room_No for r in room_ids
        if normalise_status(rooms[r].Room_Status) == "blocking"
    ]
    if blocked:
        raise RuleError(
            f"Room {', '.join(blocked)} is blocked / out of order and cannot be booked"
        )

    # Occupancy against the room's own limits.
    if occupancy:
        for room_id in room_ids:
            room = rooms[room_id]
            adults, children = occupancy.get(room_id, (0, 0))
            max_adult = as_int(room.Max_Adult_Occupy, 0)
            max_child = as_int(room.Max_Child_Occupy, 0)
            if adults < 1:
                raise RuleError(f"Room {room.Room_No} needs at least one adult")
            if max_adult and adults > max_adult:
                raise RuleError(
                    f"Room {room.Room_No} takes at most {max_adult} adult(s)"
                )
            if children < 0:
                raise RuleError(f"Room {room.Room_No} cannot have negative children")
            if max_child and children > max_child:
                raise RuleError(
                    f"Room {room.Room_No} takes at most {max_child} child(ren)"
                )

    # The date-range conflict. This is the actual double-booking check.
    taken = booked_room_windows(
        db, company_id, arrival, departure, exclude_id=exclude_id
    )
    clashes = []
    for room_id in room_ids:
        windows = taken.get(room_id)
        if not windows:
            continue
        spans = ", ".join(f"{s.isoformat()} to {e.isoformat()}" for s, e in windows)
        clashes.append(f"Room {rooms[room_id].Room_No} is already booked {spans}")
    if clashes:
        raise RuleError("; ".join(clashes), status_code=409)

    return rooms


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------
def rate_for(room_type: MasterRoomType, rate_type: str) -> float:
    """Per-unit price for a rate type, falling back to the daily rate.

    `Room_Cost` is the last resort: a property that has not filled in the rate
    columns still has a room cost, and pricing a stay at zero because a rate
    column is null is worse than pricing it at the base cost.
    """
    column = RATE_COLUMN.get(str(rate_type or "").strip().lower())
    if column:
        value = getattr(room_type, column, None)
        if value not in (None, ""):
            return as_float(value)

    if room_type.Daily_Rate not in (None, ""):
        return as_float(room_type.Daily_Rate)
    return as_float(room_type.Room_Cost)


def units_for(rate_type: str, nights: int) -> int:
    """Billable units. Weekly rates bill per started week; everything else per night."""
    nights = max(1, int(nights or 1))
    if str(rate_type or "").strip().lower() == WEEKLY_RATE_TYPE:
        return max(1, math.ceil(nights / 7))
    return nights


def quote(
    db: Session,
    company_id,
    *,
    room_ids: list[int],
    rate_types: list[str],
    nights: int,
    tax_type_id=None,
    discount_type_id=None,
    extra_charges: float = 0.0,
    extra_bed_count: int = 0,
    extra_bed_cost: Optional[float] = None,
    room_amount_override: Optional[float] = None,
    paying_amount: float = 0.0,
) -> dict:
    """Price a stay from master data. The single source of every total.

    Inputs that are genuinely the operator's call -- extra charges, how many
    extra beds, a negotiated room amount, how much the guest is paying now --
    are accepted. Everything else is looked up, and every total is derived:

        room             = SUM over rooms of rate(rate_type) x units
        extra bed total  = count x per-bed cost for the stay
        taxable          = room + extra charges + extra beds
        tax              = taxable x tax%        (tax% from master data)
        discount         = taxable x discount%   (discount% from master data)
        overall          = taxable + tax - discount
        balance          = max(0, overall - paying)
        extra (refund)   = max(0, paying - overall)

    Tax and discount percentages are never taken from the request. They used to
    be, alongside the amounts they were supposed to produce, so a client could
    post a 0% tax on a taxable rate or a 900% discount -- both of which the API
    stored without comment.
    """
    nights = max(1, int(nights or 1))

    rooms = load_rooms(db, company_id, room_ids)
    type_ids = {as_int(rooms[r].Room_Type_ID) for r in rooms}
    room_types = load_room_types(db, company_id, type_ids)

    lines = []
    room_total = 0.0
    for index, room_id in enumerate(room_ids):
        room = rooms.get(int(room_id))
        if not room:
            continue
        room_type = room_types.get(as_int(room.Room_Type_ID))
        if not room_type:
            raise RuleError(
                f"Room {room.Room_No} has no active room type, so it cannot be priced"
            )

        rate_type = (
            rate_types[index]
            if index < len(rate_types) and rate_types[index]
            else DEFAULT_RATE_TYPE
        )
        unit_rate = rate_for(room_type, rate_type)
        units = units_for(rate_type, nights)
        line_total = money(unit_rate * units)
        room_total += line_total

        lines.append(
            {
                "room_id": room.id,
                "room_no": room.Room_No,
                "room_type_id": room_type.id,
                "room_type_name": room_type.Type_Name,
                "rate_type": rate_type,
                "unit_rate": money(unit_rate),
                "units": units,
                "line_total": line_total,
            }
        )

    room_total = money(room_total)

    # A negotiated rate replaces the computed room amount but changes nothing
    # else: tax, discount and the overall are still derived from it here.
    if room_amount_override is not None:
        override = money(room_amount_override)
        if override < 0:
            raise RuleError("Room amount cannot be negative")
        room_amount = override
    else:
        room_amount = room_total

    # Per-bed cost for the whole stay, from the first room's type unless the
    # caller priced it explicitly.
    extra_bed_count = max(0, as_int(extra_bed_count))
    if extra_bed_cost is None:
        first_type = None
        if lines:
            first_type = room_types.get(lines[0]["room_type_id"])
        per_bed_per_night = as_float(getattr(first_type, "Bed_Cost", 0))
        extra_bed_cost = money(per_bed_per_night * nights)
    else:
        extra_bed_cost = money(extra_bed_cost)
        if extra_bed_cost < 0:
            raise RuleError("Extra bed cost cannot be negative")

    extra_charges = money(extra_charges)
    if extra_charges < 0:
        raise RuleError("Extra charges cannot be negative")

    extra_bed_total = money(extra_bed_count * extra_bed_cost)
    taxable = money(room_amount + extra_charges + extra_bed_total)

    tax_row = resolve_tax_type(db, tax_type_id, company_id)
    discount_row = resolve_discount_type(db, discount_type_id, company_id)

    tax_percentage = as_float(getattr(tax_row, "Tax_Percentage", 0)) if tax_row else 0.0
    discount_percentage = (
        as_float(getattr(discount_row, "Discount_Percentage", 0)) if discount_row else 0.0
    )

    # Master data stores these as free-text strings, so a typo there must not
    # become a negative total here.
    if not 0 <= tax_percentage <= 100:
        raise RuleError(
            f"Tax '{tax_row.Tax_Name}' is configured at {tax_percentage}%, "
            "which is outside 0-100. Fix it under Master Data → Tax."
        )
    if not 0 <= discount_percentage <= 100:
        raise RuleError(
            f"Discount '{discount_row.Discount_Name}' is configured at "
            f"{discount_percentage}%, which is outside 0-100. "
            "Fix it under Master Data → Discount."
        )

    tax_amount = money(taxable * tax_percentage / 100)
    discount_amount = money(taxable * discount_percentage / 100)
    overall_amount = money(taxable + tax_amount - discount_amount)

    paying_amount = money(paying_amount)
    if paying_amount < 0:
        raise RuleError("Paying amount cannot be negative")

    balance_amount = money(max(0.0, overall_amount - paying_amount))
    extra_amount = money(max(0.0, paying_amount - overall_amount))

    return {
        "lines": lines,
        "nights": nights,
        "room_amount": room_amount,
        "computed_room_amount": room_total,
        "room_amount_overridden": room_amount_override is not None
        and money(room_amount_override) != room_total,
        "extra_charges": extra_charges,
        "extra_bed_count": extra_bed_count,
        "extra_bed_cost": extra_bed_cost,
        "extra_bed_total": extra_bed_total,
        "taxable_amount": taxable,
        "tax_type_id": tax_row.id if tax_row else None,
        "tax_name": tax_row.Tax_Name if tax_row else None,
        "tax_percentage": money(tax_percentage),
        "tax_amount": tax_amount,
        "discount_type_id": discount_row.id if discount_row else None,
        "discount_name": discount_row.Discount_Name if discount_row else None,
        "discount_percentage": money(discount_percentage),
        "discount_amount": discount_amount,
        "overall_amount": overall_amount,
        # `total_amount` has always mirrored the overall in this schema; kept
        # so existing readers (night audit, exports, the print receipt) do not
        # change meaning.
        "total_amount": overall_amount,
        "paying_amount": paying_amount,
        "paid_amount": paying_amount,
        "balance_amount": balance_amount,
        "extra_amount": extra_amount,
    }


def apply_quote(reservation: models.RoomReservation, priced: dict) -> None:
    """Write a quote onto a reservation. The only place money is assigned."""
    reservation.room_amount = priced["room_amount"]
    reservation.extra_charges = priced["extra_charges"]
    reservation.extra_bed_count = priced["extra_bed_count"]
    reservation.extra_bed_cost = priced["extra_bed_cost"]
    reservation.tax_type_id = priced["tax_type_id"]
    reservation.tax_percentage = priced["tax_percentage"]
    reservation.tax_amount = priced["tax_amount"]
    reservation.discount_type_id = priced["discount_type_id"]
    reservation.discount_percentage = priced["discount_percentage"]
    reservation.discount_amount = priced["discount_amount"]
    reservation.overall_amount = priced["overall_amount"]
    reservation.total_amount = priced["total_amount"]

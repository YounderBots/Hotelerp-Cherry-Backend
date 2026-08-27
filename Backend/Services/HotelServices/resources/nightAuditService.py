"""Night Audit business logic, kept out of the HTTP layer so it can be reasoned
about -- and tested -- on its own.

WHAT A NIGHT AUDIT IS IN *THIS* APPLICATION
    A night audit closes one hotel day. Reading the schema tells you what that
    can and cannot mean here:

    * `room_reservation` carries the WHOLE STAY's money in columns computed
      once, at booking time -- `room_amount` is the full stay, not a nightly
      rate, and `overall_amount = room_amount + extra_charges + tax_amount -
      discount_amount` holds for every row in the database.
    * There is no folio table, no charge ledger, and no posting table.

    So this application has nothing to post. An audit that "posted room
    charges" would be inventing a second copy of money the reservation already
    carries, which is precisely the double-charge the module must never
    produce. What the audit does instead is: work out the position for the
    night, record it permanently, optionally resolve arrivals that never
    showed up, and move the business date on.

STRAIGHT-LINE ACCRUAL
    Because the stay total is a single number, a night's share of it has to be
    derived. `nightly_share` splits a stay total across its nights so that the
    nightly amounts sum EXACTLY back to the stay total -- no cent is created or
    lost by rounding, which is the property that makes a run of audits add up
    to the same figure the reservations already show.

WHAT COUNTS AS OCCUPYING A NIGHT
    A reservation occupies the night of D when `arrival_date <= D <
    departure_date` and its status is neither Cancelled nor No-Show. That is
    deliberately the same rule `get_room_availability` in reservationController
    uses to decide whether a room is blocked, so occupancy here and
    availability there can never disagree about the same night.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Iterable, Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import models

logger = logging.getLogger("hotelservice.nightaudit")

# ---------------------------------------------------------------------------
# Vocabulary
#
# Every status string below is taken from the `reservation_status` master table
# in MasterDataServices (Confirmed / Checked-In / Checked-Out / Cancelled /
# No-Show / Pending / On Hold). Nothing here invents a status, and nothing here
# writes a status that an operator could not have chosen from that master list.
# ---------------------------------------------------------------------------

ACTIVE = "ACTIVE"

STATUS_CHECKED_IN = "Checked-In"
STATUS_CHECKED_OUT = "Checked-Out"
STATUS_CANCELLED = "Cancelled"
STATUS_NO_SHOW = "No-Show"

# Statuses meaning "booked but the guest is not here yet". These are the rows
# that become no-shows if their arrival date passes without a check-in.
ARRIVAL_PENDING_STATUSES = ("Confirmed", "Pending", "On Hold")

# A reservation in one of these never holds a room, so it neither occupies a
# night nor earns revenue. Mirrors NON_BLOCKING_STATUSES in
# reservationController.get_room_availability.
NON_OCCUPYING_STATUSES = ("Cancelled", "No-Show", "no show")

# Run states for a night_audit row.
AUDIT_RUNNING = "Running"
AUDIT_COMPLETED = "Completed"
AUDIT_FAILED = "Failed"


class AuditConflict(Exception):
    """A run was refused because the property's state does not allow it.

    Carries the HTTP status the controller should return, so the decision about
    *why* a run is impossible stays with the business logic rather than being
    re-derived from a message string in the route.
    """

    def __init__(self, message: str, code: str = "conflict", http_status: int = 409):
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status


# ---------------------------------------------------------------------------
# Money
# ---------------------------------------------------------------------------

def money(value: Any) -> float:
    """A float rounded to 2dp, treating None/garbage as zero.

    Every amount leaving this module goes through here so a stray None in a
    nullable column cannot turn a total into NaN or a TypeError mid-audit.
    """
    try:
        if value is None:
            return 0.0
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def nightly_share(total: Any, nights: int, index: int) -> float:
    """One night's share of a stay total, split so the nights sum EXACTLY.

    The obvious implementation -- `round(total / nights, 2)` -- does not add
    up: 100.00 over 3 nights gives 33.33 three times, and 0.01 vanishes. Over a
    month of audits that drift is a real reconciliation problem, and it is
    exactly the kind of thing a night audit exists to prevent.

    Taking the difference between two running cumulative totals instead means
    the shares always re-sum to the original amount, with the odd cent landing
    on a specific night rather than disappearing:

        >>> [nightly_share(100, 3, i) for i in range(3)]
        [33.33, 33.33, 33.34]
    """
    amount = money(total)
    if nights <= 0:
        # A same-day or malformed stay is treated as a single night, so its
        # money is still accounted for rather than silently dropped.
        return amount if index <= 0 else 0.0
    if index < 0 or index >= nights:
        return 0.0
    upto_here = round(amount * (index + 1) / nights, 2)
    upto_prev = round(amount * index / nights, 2)
    return round(upto_here - upto_prev, 2)


def stay_nights(reservation) -> int:
    """Nights in the stay, trusting the dates over the stored counter.

    `no_of_nights` is user-supplied at booking and is not constrained to agree
    with the dates. The dates are what every other query in the service filters
    on, so they win here; the counter is only a fallback for a row whose dates
    are unusable.
    """
    arrival = reservation.arrival_date
    departure = reservation.departure_date
    if arrival and departure:
        span = (departure - arrival).days
        if span > 0:
            return span
    try:
        return max(int(reservation.no_of_nights or 0), 0)
    except (TypeError, ValueError):
        return 0


def night_index(reservation, business_date: date) -> int:
    """Which night of the stay `business_date` is (0 = first night)."""
    if not reservation.arrival_date:
        return 0
    return (business_date - reservation.arrival_date).days


# ---------------------------------------------------------------------------
# Business date
# ---------------------------------------------------------------------------

def get_business_date_row(db: Session, company_id: str, *, for_update: bool = False):
    """The company's business-date row, or None."""
    query = db.query(models.HotelBusinessDate).filter(
        models.HotelBusinessDate.company_id == str(company_id),
    )
    if for_update:
        # Serialises concurrent audits for this property: the second caller
        # blocks here until the first has committed (or rolled back), and then
        # re-reads a business date that already moved.
        #
        # populate_existing() is load-bearing, not decoration. This row has
        # almost always been read already this request (ensure_business_date),
        # so it sits in the session's identity map; without this, SQLAlchemy
        # hands back the CACHED object and the lock buys nothing -- the loser
        # of a race wakes up still believing the old business date. Measured,
        # not theorised: eight concurrent runs, and the seven losers each
        # carried on with the stale date until the unique constraint stopped
        # them at INSERT.
        query = query.populate_existing().with_for_update()
    return query.first()


def ensure_business_date(db: Session, company_id: str, user_id: Any) -> models.HotelBusinessDate:
    """Return the business-date row, seeding it on first use.

    A property that has never run an audit has no row. Rather than refusing to
    show the module until somebody sets a date by hand, the first read seeds it
    from the server's calendar date -- the only moment in the module where the
    system clock is allowed to decide a business date.

    The insert can lose a race with another request doing the same thing; the
    unique constraint on company_id turns that into an IntegrityError, which is
    recovered by re-reading the row the winner wrote.
    """
    row = get_business_date_row(db, company_id)
    if row:
        return row

    row = models.HotelBusinessDate(
        business_date=date.today(),
        status=ACTIVE,
        created_by=str(user_id),
        company_id=str(company_id),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        row = get_business_date_row(db, company_id)
        if row is None:
            raise
        return row
    db.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Position for a night
# ---------------------------------------------------------------------------

def _active_reservations(db: Session, company_id: str):
    return db.query(models.RoomReservation).filter(
        models.RoomReservation.company_id == str(company_id),
        models.RoomReservation.status == ACTIVE,
    )


def _guest_name(r) -> str:
    return " ".join(p for p in (r.salutation, r.first_name, r.last_name) if p).strip()


def _room_label(r) -> str:
    """Human room numbers, never the raw room ids.

    `room_no` is a JSON list of the numbers a guest can read off a door;
    `room_ids` are database keys. Only the former belongs on screen.
    """
    numbers = r.room_no
    if isinstance(numbers, list):
        return ", ".join(str(n) for n in numbers if n not in (None, ""))
    if numbers in (None, ""):
        return ""
    return str(numbers)


def _reservation_brief(r, business_date: date) -> dict:
    """The shape every Night Audit list renders, resolved server-side."""
    nights = stay_nights(r)
    idx = night_index(r, business_date)
    return {
        "id": r.id,
        "reservation_id": r.room_reservation_id,
        "token": r.token,
        "guest_name": _guest_name(r),
        "phone_number": r.phone_number,
        "room_no": _room_label(r),
        "arrival_date": r.arrival_date,
        "departure_date": r.departure_date,
        "no_of_nights": nights,
        "reservation_status": r.reservation_status,
        "overall_amount": money(r.overall_amount),
        "paid_amount": money(r.paid_amount),
        "balance_amount": money(r.balance_amount),
        # What this one night contributes, not the whole stay.
        "night_room_revenue": nightly_share(r.room_amount, nights, idx),
        "night_tax": nightly_share(r.tax_amount, nights, idx),
        "night_discount": nightly_share(r.discount_amount, nights, idx),
        "night_extra_charges": nightly_share(r.extra_charges, nights, idx),
    }


def occupies_night(r, business_date: date) -> bool:
    """Whether this reservation holds a room on the night of `business_date`."""
    if not r.arrival_date or not r.departure_date:
        return False
    if (r.reservation_status or "").strip().lower() in {
        s.lower() for s in NON_OCCUPYING_STATUSES
    }:
        return False
    return r.arrival_date <= business_date < r.departure_date


def compute_position(db: Session, company_id: str, business_date: date) -> dict:
    """Everything the audit needs to know about one night.

    Read-only. `preview` renders this, and `run_audit` snapshots it, so what an
    operator approves on screen is byte-for-byte what gets recorded -- the
    frontend never recomputes a total of its own.
    """
    reservations = _active_reservations(db, company_id).all()

    occupying: list = []
    in_house: list = []
    arrivals_expected: list = []
    arrivals_completed: list = []
    no_show_candidates: list = []
    departures_expected: list = []
    departures_completed: list = []
    overdue_departures: list = []
    unsettled: list = []

    room_revenue = 0.0
    extra_charges = 0.0
    tax_amount = 0.0
    discount_amount = 0.0
    occupied_room_ids: set = set()
    room_nights = 0
    outstanding = 0.0

    for r in reservations:
        status = (r.reservation_status or "").strip()
        brief = _reservation_brief(r, business_date)

        # ---- revenue + occupancy for this night ----
        if occupies_night(r, business_date):
            room_revenue += brief["night_room_revenue"]
            tax_amount += brief["night_tax"]
            discount_amount += brief["night_discount"]
            extra_charges += brief["night_extra_charges"]
            room_nights += 1
            for rid in (r.room_ids or []):
                try:
                    occupied_room_ids.add(int(rid))
                except (TypeError, ValueError):
                    continue
            # Every reservation holding a room tonight, whatever its status.
            # This is exactly the set the revenue totals are summed from, so
            # the Room Booked report can show the figure line by line and an
            # operator can reconcile a night's revenue by reading it rather
            # than by trusting it.
            occupying.append(brief)
            if status == STATUS_CHECKED_IN:
                in_house.append(brief)

        # ---- arrivals due on this date ----
        if r.arrival_date == business_date and status != STATUS_CANCELLED:
            if status != STATUS_NO_SHOW:
                arrivals_expected.append(brief)
            if status in (STATUS_CHECKED_IN, STATUS_CHECKED_OUT):
                arrivals_completed.append(brief)
            elif status in ARRIVAL_PENDING_STATUSES:
                # Booked, due today, never checked in: the classic no-show.
                no_show_candidates.append(brief)

        # ---- departures due on this date ----
        if r.departure_date == business_date and status in (
            STATUS_CHECKED_IN,
            STATUS_CHECKED_OUT,
        ):
            departures_expected.append(brief)
            if status == STATUS_CHECKED_OUT:
                departures_completed.append(brief)

        # ---- guests who should already have left but are still checked in ----
        if (
            r.departure_date
            and r.departure_date <= business_date
            and status == STATUS_CHECKED_IN
        ):
            overdue_departures.append(brief)

        # ---- money still owed by guests who have arrived ----
        if (
            r.arrival_date
            and r.arrival_date <= business_date
            and status not in (STATUS_CANCELLED, STATUS_NO_SHOW)
        ):
            balance = money(r.balance_amount)
            if balance > 0.005:
                outstanding += balance
                unsettled.append(brief)

    # ---- cash actually taken on this date ----
    # Summed from the payment history by date, which needs no join back to the
    # reservation -- deliberate, because `reservation_amount_paid_history.
    # reservation_id` is written inconsistently (seeded rows hold the
    # 'RES-...' reference, rows written by /room_reservation_pay hold the
    # numeric id), so any join here would silently miss half the payments.
    payment_rows = (
        db.query(
            models.ReservationAmountPaidHistory.payment_method,
            func.coalesce(func.sum(models.ReservationAmountPaidHistory.amount), 0).label("amount"),
        )
        .filter(
            models.ReservationAmountPaidHistory.company_id == str(company_id),
            models.ReservationAmountPaidHistory.status == ACTIVE,
            models.ReservationAmountPaidHistory.paid_date == business_date,
        )
        .group_by(models.ReservationAmountPaidHistory.payment_method)
        .all()
    )
    payment_breakdown = [
        {"payment_method": method or "Unspecified", "amount": money(amount)}
        for method, amount in payment_rows
    ]
    payments_collected = money(sum(p["amount"] for p in payment_breakdown))

    room_revenue = money(room_revenue)
    tax_amount = money(tax_amount)
    discount_amount = money(discount_amount)
    extra_charges = money(extra_charges)
    # Same composition the reservation rows themselves use, so a night's gross
    # is directly comparable to `overall_amount`.
    gross_revenue = money(room_revenue + extra_charges + tax_amount - discount_amount)

    return {
        "business_date": business_date,
        "movement": {
            "arrivals_expected": len(arrivals_expected),
            "arrivals_completed": len(arrivals_completed),
            "departures_expected": len(departures_expected),
            "departures_completed": len(departures_completed),
            "in_house": len(in_house),
            "stayovers": len(in_house),
            "no_show_candidates": len(no_show_candidates),
            "overdue_departures": len(overdue_departures),
            "unsettled_folios": len(unsettled),
        },
        "revenue": {
            "room_revenue": room_revenue,
            "extra_charges": extra_charges,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "gross_revenue": gross_revenue,
        },
        "settlement": {
            "payments_collected": payments_collected,
            "payment_breakdown": payment_breakdown,
            "outstanding_balance": money(outstanding),
        },
        "occupancy": {
            "rooms_occupied": len(occupied_room_ids),
            "room_nights": room_nights,
            "rooms_sold": len(occupying),
        },
        "lists": {
            "occupying": occupying,
            "in_house": in_house,
            "arrivals_expected": arrivals_expected,
            "no_show_candidates": no_show_candidates,
            "departures_expected": departures_expected,
            "overdue_departures": overdue_departures,
            "unsettled_folios": unsettled,
        },
    }


# ---------------------------------------------------------------------------
# Readiness
# ---------------------------------------------------------------------------

def build_readiness(
    position: dict,
    business_date: date,
    existing_audit,
    today: Optional[date] = None,
) -> dict:
    """Turn the position into the checklist the operator sees.

    Blockers stop a run; warnings are conditions an operator is told about and
    then decides on. The split matters: refusing to close a day because one
    guest still owes money would leave the property permanently unable to
    audit, since that balance may never be collected. Refusing to close a day
    that has already been closed, on the other hand, is the whole point.

    This is the ONLY definition of readiness. `status`, `preview` and `run` all
    call it, so the screen cannot say "Ready" while the run endpoint disagrees.
    """
    today = today or date.today()
    movement = position["movement"]

    blockers: list[dict] = []
    warnings: list[dict] = []

    if existing_audit is not None and existing_audit.audit_status == AUDIT_COMPLETED:
        blockers.append({
            "code": "already_audited",
            "label": "Business date already audited",
            "detail": (
                f"{business_date.isoformat()} was audited on "
                f"{existing_audit.completed_at:%d %b %Y %H:%M}"
                if existing_audit.completed_at
                else f"{business_date.isoformat()} has already been audited."
            ),
        })

    if existing_audit is not None and existing_audit.audit_status == AUDIT_RUNNING:
        blockers.append({
            "code": "audit_in_progress",
            "label": "An audit is already running",
            "detail": "Another audit for this business date is still in progress.",
        })

    if business_date > today:
        blockers.append({
            "code": "future_business_date",
            "label": "Business date is in the future",
            "detail": (
                f"The business date ({business_date.isoformat()}) is ahead of the "
                f"server date ({today.isoformat()}). A night that has not happened "
                "yet cannot be closed."
            ),
        })

    if movement["no_show_candidates"]:
        warnings.append({
            "code": "pending_arrivals",
            "label": "Arrivals not checked in",
            "count": movement["no_show_candidates"],
            "detail": (
                f"{movement['no_show_candidates']} reservation(s) due to arrive were "
                "never checked in. They will be marked No-Show if you choose that "
                "option below."
            ),
        })

    if movement["overdue_departures"]:
        warnings.append({
            "code": "overdue_departures",
            "label": "Guests past their departure date",
            "count": movement["overdue_departures"],
            "detail": (
                f"{movement['overdue_departures']} guest(s) are still checked in "
                "after their departure date. Check them out or extend the stay."
            ),
        })

    if movement["unsettled_folios"]:
        warnings.append({
            "code": "outstanding_balance",
            "label": "Outstanding balances",
            "count": movement["unsettled_folios"],
            "detail": (
                f"{movement['unsettled_folios']} arrived reservation(s) still owe "
                f"{position['settlement']['outstanding_balance']:.2f}. The audit "
                "records the balance; it does not clear it."
            ),
        })

    return {
        "ready": not blockers,
        "blockers": blockers,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------

def _existing_audit(db: Session, company_id: str, business_date: date):
    return (
        db.query(models.NightAudit)
        .filter(
            models.NightAudit.company_id == str(company_id),
            models.NightAudit.business_date == business_date,
        )
        .first()
    )


def _new_audit_reference(business_date: date) -> str:
    return f"NA-{business_date:%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"


def run_audit(
    db: Session,
    company_id: str,
    user_id: Any,
    *,
    expected_business_date: date,
    mark_no_shows: bool = True,
    rooms_total: Optional[int] = None,
) -> models.NightAudit:
    """Close one specific business day. One transaction, all or nothing.

    WHY THE CALLER MUST NAME THE DATE
        `expected_business_date` is what makes this operation idempotent, and
        it was added because locking alone demonstrably is not enough. With the
        lock working correctly, eight concurrent runs serialised perfectly and
        then each closed the NEXT open night -- eight nights shut in one
        double-click. Every individual run was correct; the sequence was not.

        A run that names its date cannot do that. The second click still says
        "close 2026-08-01", the property has already moved to 08-02, and the
        request is refused as stale. Closing 08-02 becomes what it should be:
        a separate decision, taken after looking at 08-02.

        This is also what makes catching up on missed nights safe. An operator
        who really does need to close three nights closes them one at a time,
        seeing each night's figures before approving it, instead of a single
        click silently swallowing all three.

    THE ORDER MATTERS
        The business-date row is locked FOR UPDATE first, before anything is
        read or written. Everything after it -- the readiness re-check, the
        no-show updates, the snapshot insert, the date roll -- happens while
        that lock is held, so two operators pressing Run at the same instant
        cannot both pass the "already audited?" check. The second one blocks,
        then wakes to find the date has moved and is refused.

    WHY READINESS IS CHECKED AGAIN HERE
        The screen checked it too, but that answer is as old as the last page
        load. A check-in completed 30 seconds ago has to be able to change the
        outcome, so the decision is made from data read inside this
        transaction and never from anything the client sent.

    ON FAILURE
        The caller rolls back, which undoes the no-show updates, the snapshot
        and the date roll together. There is no state in which the date has
        moved but the night was not recorded, or the night was recorded twice.
    """
    # End any read transaction this request already opened. MySQL's default
    # REPEATABLE READ pins a transaction's snapshot at its FIRST consistent
    # read, and the endpoint has already read the business date once to know
    # which night it is about to close. Without this rollback the audit runs
    # against that older snapshot, so a competing run's freshly committed rows
    # are invisible no matter how long we waited for the lock.
    db.rollback()

    # Lock FIRST, as the opening statement of the new transaction. A locking
    # read always sees the latest committed row, and taking it here means the
    # snapshot for every plain read below is established afterwards -- so the
    # loser of a race reads a world in which the winner has already finished.
    bd_row = get_business_date_row(db, company_id, for_update=True)
    if bd_row is None:
        raise AuditConflict(
            "No business date is set for this property.",
            code="no_business_date",
            http_status=409,
        )

    business_date = bd_row.business_date

    # Read under the lock, so this comparison is against the property's real
    # current date and not the one the client's page was rendered with.
    if expected_business_date != business_date:
        raise AuditConflict(
            (
                f"This screen is showing {expected_business_date.isoformat()}, but the "
                f"property has already moved on to {business_date.isoformat()}. "
                "Refresh to review the current night before closing it."
            ),
            code="business_date_moved",
            http_status=409,
        )

    existing = _existing_audit(db, company_id, business_date)

    position = compute_position(db, company_id, business_date)
    readiness = build_readiness(position, business_date, existing)
    if not readiness["ready"]:
        first = readiness["blockers"][0]
        raise AuditConflict(first["detail"], code=first["code"], http_status=409)

    started_at = datetime.now()

    # ---- resolve arrivals that never showed up ----
    no_show_ids: list[int] = []
    if mark_no_shows:
        candidates = position["lists"]["no_show_candidates"]
        if candidates:
            candidate_ids = [c["id"] for c in candidates]
            rows = (
                db.query(models.RoomReservation)
                .filter(
                    models.RoomReservation.id.in_(candidate_ids),
                    models.RoomReservation.company_id == str(company_id),
                    models.RoomReservation.status == ACTIVE,
                    # Re-asserted rather than assumed: between computing the
                    # position and this update a night clerk may have checked
                    # the guest in, and that check-in must win over a no-show.
                    models.RoomReservation.reservation_status.in_(ARRIVAL_PENDING_STATUSES),
                )
                .all()
            )
            for row in rows:
                row.reservation_status = STATUS_NO_SHOW
                row.updated_by = str(user_id)
                no_show_ids.append(row.id)

    # ---- write the snapshot ----
    occupancy = position["occupancy"]
    revenue = position["revenue"]
    settlement = position["settlement"]
    movement = position["movement"]

    occupancy_percent = None
    if rooms_total and rooms_total > 0:
        occupancy_percent = round(occupancy["rooms_occupied"] * 100.0 / rooms_total, 2)

    # A previous Failed run for this date left its row behind (the unique
    # constraint allows only one). Reusing it is what makes retry safe: a
    # failed run rolled everything back, so there is nothing of its to undo.
    audit = existing if existing is not None else models.NightAudit(
        night_audit_id=_new_audit_reference(business_date),
        business_date=business_date,
        created_by=str(user_id),
        company_id=str(company_id),
        status=ACTIVE,
    )

    audit.next_business_date = business_date + timedelta(days=1)
    audit.audit_status = AUDIT_COMPLETED
    audit.started_at = started_at
    audit.completed_at = datetime.now()
    audit.run_by = str(user_id)
    audit.error_message = None
    audit.updated_by = str(user_id)

    audit.rooms_total = rooms_total
    audit.rooms_occupied = occupancy["rooms_occupied"]
    audit.occupancy_percent = occupancy_percent
    audit.room_nights = occupancy["room_nights"]

    audit.arrivals_expected = movement["arrivals_expected"]
    audit.arrivals_completed = movement["arrivals_completed"]
    audit.departures_expected = movement["departures_expected"]
    audit.departures_completed = movement["departures_completed"]
    audit.in_house = movement["in_house"]
    audit.stayovers = movement["stayovers"]
    audit.no_shows_marked = len(no_show_ids)
    audit.no_show_reservation_ids = no_show_ids

    audit.room_revenue = revenue["room_revenue"]
    audit.extra_charges = revenue["extra_charges"]
    audit.tax_amount = revenue["tax_amount"]
    audit.discount_amount = revenue["discount_amount"]
    audit.gross_revenue = revenue["gross_revenue"]

    audit.payments_collected = settlement["payments_collected"]
    audit.payment_breakdown = settlement["payment_breakdown"]
    audit.outstanding_balance = settlement["outstanding_balance"]

    if existing is None:
        db.add(audit)

    # ---- roll the property on to the next day ----
    bd_row.business_date = audit.next_business_date
    bd_row.last_audit_at = audit.completed_at
    bd_row.last_audit_by = str(user_id)
    bd_row.updated_by = str(user_id)

    return audit


def record_failure(
    db: Session,
    company_id: str,
    business_date: date,
    user_id: Any,
    message: str,
) -> None:
    """Persist a Failed audit row after the run's transaction was rolled back.

    Runs in its own transaction, on purpose: the rollback that brought us here
    discarded the audit row along with everything else, so the failure has to
    be written again from scratch. A night that blew up must not look like a
    night that was never attempted -- "no record" and "we tried and it failed"
    are different facts, and only the second one tells an operator to retry.

    Best-effort by design. If even this write fails, the original error is what
    the caller reports; a logging failure must not replace it.
    """
    try:
        audit = _existing_audit(db, company_id, business_date)
        if audit is None:
            audit = models.NightAudit(
                night_audit_id=_new_audit_reference(business_date),
                business_date=business_date,
                created_by=str(user_id),
                company_id=str(company_id),
                status=ACTIVE,
            )
            db.add(audit)
        elif audit.audit_status == AUDIT_COMPLETED:
            # A completed night is immutable. If we somehow got here with one
            # already recorded, leave it exactly as it is.
            return
        audit.audit_status = AUDIT_FAILED
        audit.completed_at = datetime.now()
        audit.run_by = str(user_id)
        audit.updated_by = str(user_id)
        audit.error_message = (message or "Night audit failed.")[:500]
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("night_audit_failure_record_failed")


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def audit_to_dict(audit: models.NightAudit) -> dict:
    """One audit row as the API exposes it -- no internal keys."""
    return {
        "id": audit.id,
        "night_audit_id": audit.night_audit_id,
        "business_date": audit.business_date,
        "next_business_date": audit.next_business_date,
        "audit_status": audit.audit_status,
        "started_at": audit.started_at,
        "completed_at": audit.completed_at,
        "run_by": audit.run_by,
        "error_message": audit.error_message,
        "occupancy": {
            "rooms_total": audit.rooms_total,
            "rooms_occupied": audit.rooms_occupied,
            "occupancy_percent": audit.occupancy_percent,
            "room_nights": audit.room_nights,
        },
        "movement": {
            "arrivals_expected": audit.arrivals_expected,
            "arrivals_completed": audit.arrivals_completed,
            "departures_expected": audit.departures_expected,
            "departures_completed": audit.departures_completed,
            "in_house": audit.in_house,
            "stayovers": audit.stayovers,
            "no_shows_marked": audit.no_shows_marked,
            "no_show_reservation_ids": audit.no_show_reservation_ids or [],
        },
        "revenue": {
            "room_revenue": audit.room_revenue,
            "extra_charges": audit.extra_charges,
            "tax_amount": audit.tax_amount,
            "discount_amount": audit.discount_amount,
            "gross_revenue": audit.gross_revenue,
        },
        "settlement": {
            "payments_collected": audit.payments_collected,
            "payment_breakdown": audit.payment_breakdown or [],
            "outstanding_balance": audit.outstanding_balance,
        },
    }

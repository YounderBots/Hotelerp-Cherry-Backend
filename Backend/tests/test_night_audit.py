"""Night Audit correctness guards. Run from inside HotelServices:

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_night_audit.py -v

No MySQL required -- the schema is built in in-memory SQLite.

WHY THIS EXISTS
The Night Audit module decides financial figures that are recorded permanently
and moves a date that cannot be moved back from the UI. Three classes of defect
matter enough to be pinned down by tests:

  MONEY THAT DOES NOT ADD UP
      Room charges in this application are stored per STAY, not per night, so a
      night's revenue has to be derived. The obvious `total / nights` loses
      cents, and a night audit that quietly loses cents is worse than useless.

  A NIGHT RECORDED TWICE, OR A DATE MOVED TWICE
      A double-clicked button, a retried request, two tabs and two operators
      all have to converge on one audit row and one date roll.

  A FAILURE THAT LOOKS LIKE A SUCCESS
      A run that blows up must leave nothing behind, must not advance the date,
      and must be visible as Failed rather than as a night nobody attempted.

The concurrency guarantee itself (FOR UPDATE serialisation) cannot be
meaningfully exercised on SQLite, so it is verified against MySQL separately;
what IS covered here is every decision the run makes before and after that lock.
"""

from datetime import date, timedelta

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

import models.models as models
from resources import nightAuditService as nas

TENANT = "1"
USER = "1"
OTHER_TENANT = "2"


@pytest.fixture()
def db():
    engine = sa.create_engine("sqlite://")
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


_counter = {"n": 0}


def make_reservation(
    db,
    arrival,
    departure,
    status="Checked-In",
    room_amount=0.0,
    tax_amount=0.0,
    discount_amount=0.0,
    extra_charges=0.0,
    paid_amount=0.0,
    balance_amount=0.0,
    rooms=(1,),
    company_id=TENANT,
    row_status="ACTIVE",
):
    _counter["n"] += 1
    n = _counter["n"]
    nights = max((departure - arrival).days, 1)
    reservation = models.RoomReservation(
        room_reservation_id=f"RES-{n:04d}",
        first_name="Test",
        last_name=f"Guest{n}",
        phone_number="9000000000",
        arrival_date=arrival,
        departure_date=departure,
        no_of_nights=nights,
        no_of_rooms=len(rooms),
        reservation_status=status,
        room_ids=list(rooms),
        room_no=[str(100 + r) for r in rooms],
        room_amount=room_amount,
        extra_charges=extra_charges,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        overall_amount=room_amount + extra_charges + tax_amount - discount_amount,
        paid_amount=paid_amount,
        balance_amount=balance_amount,
        reservation_type="Reservation",
        status=row_status,
        created_by=USER,
        company_id=company_id,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def make_payment(db, amount, paid_date, method="Cash", company_id=TENANT):
    _counter["n"] += 1
    db.add(models.ReservationAmountPaidHistory(
        reservation_id=str(_counter["n"]),
        user_id=USER,
        amount=amount,
        paid_date=paid_date,
        payment_method=method,
        status="ACTIVE",
        created_by=USER,
        company_id=company_id,
    ))
    db.commit()


def set_business_date(db, value, company_id=TENANT):
    row = models.HotelBusinessDate(
        business_date=value, status="ACTIVE", created_by=USER, company_id=company_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ==========================================================================
# Straight-line accrual -- the money has to add back up
# ==========================================================================

@pytest.mark.parametrize("total,nights", [
    (100.0, 3),        # the classic: 33.33 x 3 loses a cent
    (28000.0, 5),
    (115560.0, 6),
    (0.01, 3),         # less than one cent per night
    (999.99, 7),
    (10.0, 3),
])
def test_nightly_shares_sum_exactly_to_the_stay_total(total, nights):
    shares = [nas.nightly_share(total, nights, i) for i in range(nights)]
    assert round(sum(shares), 2) == round(total, 2), (
        f"{nights} nights of {total} summed to {sum(shares)}"
    )


def test_nightly_share_is_the_documented_example():
    assert [nas.nightly_share(100, 3, i) for i in range(3)] == [33.33, 33.34, 33.33]


def test_nightly_share_outside_the_stay_is_zero():
    assert nas.nightly_share(100, 3, 3) == 0.0
    assert nas.nightly_share(100, 3, -1) == 0.0


def test_zero_night_stay_still_accounts_for_its_money():
    """A same-day or malformed stay must not silently drop its revenue."""
    assert nas.nightly_share(500, 0, 0) == 500.0
    assert nas.nightly_share(500, 0, 1) == 0.0


def test_money_survives_none_and_garbage():
    assert nas.money(None) == 0.0
    assert nas.money("not a number") == 0.0
    assert nas.money("12.345") == 12.35


# ==========================================================================
# Which reservations hold a room on a given night
# ==========================================================================

def test_stay_spans_arrival_night_but_not_departure_night(db):
    r = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3))
    assert nas.occupies_night(r, date(2026, 7, 31)) is False
    assert nas.occupies_night(r, date(2026, 8, 1)) is True
    assert nas.occupies_night(r, date(2026, 8, 2)) is True
    # Departure day: the room is free that night.
    assert nas.occupies_night(r, date(2026, 8, 3)) is False


@pytest.mark.parametrize("status", ["Cancelled", "No-Show"])
def test_cancelled_and_no_show_never_hold_a_room(db, status):
    """Mirrors NON_BLOCKING_STATUSES in reservationController.room_availability.

    If these two rules ever diverge, Night Audit and room availability would
    disagree about whether the same room was occupied on the same night.
    """
    r = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status=status)
    assert nas.occupies_night(r, date(2026, 8, 1)) is False


@pytest.mark.parametrize("status", ["Confirmed", "Checked-In", "Checked-Out", "Pending", "On Hold"])
def test_every_other_status_holds_the_room(db, status):
    r = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status=status)
    assert nas.occupies_night(r, date(2026, 8, 1)) is True


def test_stay_nights_trusts_the_dates_over_the_stored_counter(db):
    r = make_reservation(db, date(2026, 8, 1), date(2026, 8, 6))
    r.no_of_nights = 99            # user-supplied and wrong
    assert nas.stay_nights(r) == 5


# ==========================================================================
# The night's position
# ==========================================================================

def test_revenue_is_the_night_share_not_the_whole_stay(db):
    """The defect the old /night_audit_process had.

    It summed the FULL room_amount of reservations ARRIVING that day, so a
    six-night booking counted six nights of money against its arrival date
    while every guest already in-house counted nothing.
    """
    set_business_date(db, date(2026, 8, 1))
    # 5 nights x 5000/night, arriving well before the audited night.
    make_reservation(db, date(2026, 7, 30), date(2026, 8, 4), room_amount=25000.0,
                     tax_amount=3000.0)

    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    assert pos["revenue"]["room_revenue"] == 5000.0
    assert pos["revenue"]["tax_amount"] == 600.0
    assert pos["movement"]["in_house"] == 1


def test_gross_revenue_matches_the_reservation_composition(db):
    """gross = room + extra + tax - discount, the same identity every
    room_reservation row satisfies for overall_amount."""
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2), room_amount=1000.0,
                     extra_charges=100.0, tax_amount=120.0, discount_amount=50.0)

    rev = nas.compute_position(db, TENANT, date(2026, 8, 1))["revenue"]
    assert rev["gross_revenue"] == round(1000.0 + 100.0 + 120.0 - 50.0, 2)


def test_a_full_stay_accrues_back_to_its_own_total(db):
    """Auditing every night of a stay must reproduce the stay's own figure."""
    arrival, departure = date(2026, 8, 1), date(2026, 8, 8)
    set_business_date(db, arrival)
    make_reservation(db, arrival, departure, room_amount=99999.99, tax_amount=12345.67)

    nightly = [
        nas.compute_position(db, TENANT, arrival + timedelta(days=i))["revenue"]
        for i in range((departure - arrival).days)
    ]
    assert round(sum(n["room_revenue"] for n in nightly), 2) == 99999.99
    assert round(sum(n["tax_amount"] for n in nightly), 2) == 12345.67


def test_rooms_occupied_counts_distinct_rooms(db):
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2), rooms=(1, 2, 3))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2), rooms=(3, 4))

    occ = nas.compute_position(db, TENANT, date(2026, 8, 1))["occupancy"]
    assert occ["rooms_occupied"] == 4      # room 3 counted once
    assert occ["rooms_sold"] == 2          # two reservations


def test_payments_are_the_cash_that_moved_on_that_date(db):
    set_business_date(db, date(2026, 8, 1))
    make_payment(db, 500.0, date(2026, 8, 1), "Cash")
    make_payment(db, 250.0, date(2026, 8, 1), "UPI")
    make_payment(db, 100.0, date(2026, 8, 1), "Cash")
    make_payment(db, 999.0, date(2026, 7, 31), "Cash")   # a different day

    s = nas.compute_position(db, TENANT, date(2026, 8, 1))["settlement"]
    assert s["payments_collected"] == 850.0
    assert {p["payment_method"]: p["amount"] for p in s["payment_breakdown"]} == {
        "Cash": 600.0, "UPI": 250.0,
    }


def test_outstanding_counts_only_guests_who_have_arrived(db):
    set_business_date(db, date(2026, 8, 1))
    # Arrived and owes money -> counts.
    make_reservation(db, date(2026, 7, 30), date(2026, 8, 5), balance_amount=400.0)
    # Books later; not yet the hotel's problem on this night.
    make_reservation(db, date(2026, 9, 1), date(2026, 9, 3), status="Confirmed",
                     balance_amount=900.0)
    # Cancelled balances are not owed.
    make_reservation(db, date(2026, 7, 20), date(2026, 8, 5), status="Cancelled",
                     balance_amount=700.0)

    s = nas.compute_position(db, TENANT, date(2026, 8, 1))["settlement"]
    assert s["outstanding_balance"] == 400.0


def test_another_company_is_never_visible(db):
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2), room_amount=5000.0)
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2), room_amount=999999.0,
                     company_id=OTHER_TENANT)
    make_payment(db, 12345.0, date(2026, 8, 1), company_id=OTHER_TENANT)

    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    assert pos["revenue"]["room_revenue"] == 5000.0
    assert pos["settlement"]["payments_collected"] == 0.0


def test_soft_deleted_reservations_are_excluded(db):
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2), room_amount=5000.0,
                     row_status="INACTIVE")
    assert nas.compute_position(db, TENANT, date(2026, 8, 1))["revenue"]["room_revenue"] == 0.0


# ==========================================================================
# Readiness
# ==========================================================================

def test_a_clean_night_is_ready(db):
    set_business_date(db, date(2026, 8, 1))
    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    r = nas.build_readiness(pos, date(2026, 8, 1), None, today=date(2026, 8, 2))
    assert r["ready"] is True
    assert r["blockers"] == []


def test_an_already_audited_night_is_blocked(db):
    set_business_date(db, date(2026, 8, 1))
    audit = models.NightAudit(
        night_audit_id="NA-1", business_date=date(2026, 8, 1),
        audit_status="Completed", status="ACTIVE", created_by=USER, company_id=TENANT,
    )
    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    r = nas.build_readiness(pos, date(2026, 8, 1), audit, today=date(2026, 8, 2))
    assert r["ready"] is False
    assert r["blockers"][0]["code"] == "already_audited"


def test_a_night_that_has_not_happened_is_blocked(db):
    set_business_date(db, date(2026, 8, 10))
    pos = nas.compute_position(db, TENANT, date(2026, 8, 10))
    r = nas.build_readiness(pos, date(2026, 8, 10), None, today=date(2026, 8, 2))
    assert r["ready"] is False
    assert r["blockers"][0]["code"] == "future_business_date"


def test_a_failed_audit_does_not_block_a_retry(db):
    set_business_date(db, date(2026, 8, 1))
    failed = models.NightAudit(
        night_audit_id="NA-1", business_date=date(2026, 8, 1),
        audit_status="Failed", status="ACTIVE", created_by=USER, company_id=TENANT,
    )
    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    r = nas.build_readiness(pos, date(2026, 8, 1), failed, today=date(2026, 8, 2))
    assert r["ready"] is True


def test_money_owed_warns_but_never_blocks(db):
    """A balance that is never collected must not make the property
    permanently unable to close a day."""
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 7, 30), date(2026, 8, 5), balance_amount=5000.0)
    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    r = nas.build_readiness(pos, date(2026, 8, 1), None, today=date(2026, 8, 2))

    assert r["ready"] is True
    assert [w["code"] for w in r["warnings"]] == ["outstanding_balance"]


def test_unarrived_bookings_are_warned_about_as_no_show_candidates(db):
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status="Confirmed")
    pos = nas.compute_position(db, TENANT, date(2026, 8, 1))
    r = nas.build_readiness(pos, date(2026, 8, 1), None, today=date(2026, 8, 2))

    assert r["ready"] is True
    codes = [w["code"] for w in r["warnings"]]
    assert "pending_arrivals" in codes
    assert pos["movement"]["no_show_candidates"] == 1


# ==========================================================================
# The run
# ==========================================================================

def test_a_successful_run_records_the_night_and_rolls_the_date(db):
    bd = set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), room_amount=2000.0,
                     tax_amount=240.0)

    audit = nas.run_audit(db, TENANT, USER,
                          expected_business_date=date(2026, 8, 1), rooms_total=20)
    db.commit()
    db.refresh(bd)

    assert audit.audit_status == "Completed"
    assert audit.business_date == date(2026, 8, 1)
    assert audit.next_business_date == date(2026, 8, 2)
    assert audit.room_revenue == 1000.0
    assert audit.rooms_total == 20
    assert audit.occupancy_percent == 5.0        # 1 of 20
    assert bd.business_date == date(2026, 8, 2)


def test_the_run_refuses_a_date_the_caller_did_not_expect(db):
    """A stale page must not close a night the operator never looked at."""
    set_business_date(db, date(2026, 8, 2))
    with pytest.raises(nas.AuditConflict) as exc:
        nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))
    assert exc.value.code == "business_date_moved"
    assert exc.value.http_status == 409


def test_running_the_same_night_twice_is_refused(db):
    set_business_date(db, date(2026, 8, 1))
    nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))
    db.commit()

    # The date has moved on, so the same request is now stale.
    with pytest.raises(nas.AuditConflict):
        nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))


def test_the_unique_constraint_is_the_last_line_of_defence(db):
    """Even bypassing every application check, the database refuses a second
    audit row for the same night."""
    set_business_date(db, date(2026, 8, 1))
    for _ in range(2):
        db.add(models.NightAudit(
            night_audit_id=f"NA-{_}", business_date=date(2026, 8, 1),
            audit_status="Completed", status="ACTIVE",
            created_by=USER, company_id=TENANT,
        ))
    with pytest.raises(sa.exc.IntegrityError):
        db.commit()
    db.rollback()


def test_no_shows_are_marked_and_recorded(db):
    set_business_date(db, date(2026, 8, 1))
    arrived = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status="Checked-In")
    never_came = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status="Confirmed")

    audit = nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1),
                          mark_no_shows=True)
    db.commit()
    db.refresh(arrived)
    db.refresh(never_came)

    assert never_came.reservation_status == "No-Show"
    assert arrived.reservation_status == "Checked-In"     # untouched
    assert audit.no_shows_marked == 1
    assert audit.no_show_reservation_ids == [never_came.id]


def test_no_shows_can_be_declined(db):
    set_business_date(db, date(2026, 8, 1))
    never_came = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status="Confirmed")

    audit = nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1),
                          mark_no_shows=False)
    db.commit()
    db.refresh(never_came)

    assert never_came.reservation_status == "Confirmed"
    assert audit.no_shows_marked == 0


def test_a_late_check_in_beats_the_no_show(db):
    """The run re-asserts the pending status in its UPDATE, so a guest checked
    in between the position being computed and the update landing keeps their
    check-in rather than being overwritten as a no-show."""
    set_business_date(db, date(2026, 8, 1))
    late = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status="Confirmed")

    original = nas.compute_position

    def check_in_first(session, company_id, business_date):
        position = original(session, company_id, business_date)
        row = session.query(models.RoomReservation).filter_by(id=late.id).first()
        row.reservation_status = "Checked-In"
        session.flush()
        return position

    nas.compute_position = check_in_first
    try:
        audit = nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))
        db.commit()
    finally:
        nas.compute_position = original

    db.refresh(late)
    assert late.reservation_status == "Checked-In"
    assert audit.no_shows_marked == 0


def test_a_failed_run_leaves_nothing_behind(db):
    bd = set_business_date(db, date(2026, 8, 1))
    booking = make_reservation(db, date(2026, 8, 1), date(2026, 8, 3), status="Confirmed")

    try:
        nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))
        raise RuntimeError("simulated failure after the no-show writes")
    except RuntimeError:
        db.rollback()

    db.refresh(bd)
    db.refresh(booking)
    assert booking.reservation_status == "Confirmed"      # not marked No-Show
    assert bd.business_date == date(2026, 8, 1)           # date did not move
    assert db.query(models.NightAudit).count() == 0


def test_a_failure_is_recorded_so_it_can_be_retried(db):
    set_business_date(db, date(2026, 8, 1))
    nas.record_failure(db, TENANT, date(2026, 8, 1), USER, "database went away")

    row = db.query(models.NightAudit).filter_by(business_date=date(2026, 8, 1)).one()
    assert row.audit_status == "Failed"
    assert "database went away" in row.error_message
    assert not row.gross_revenue


def test_a_completed_night_is_never_overwritten_by_a_failure_record(db):
    """Immutability of a closed night, even against a late failure report."""
    set_business_date(db, date(2026, 8, 1))
    nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))
    db.commit()

    nas.record_failure(db, TENANT, date(2026, 8, 1), USER, "a late, spurious error")

    row = db.query(models.NightAudit).filter_by(business_date=date(2026, 8, 1)).one()
    assert row.audit_status == "Completed"
    assert row.error_message is None


def test_retry_reuses_the_failed_row_rather_than_duplicating_it(db):
    set_business_date(db, date(2026, 8, 1))
    nas.record_failure(db, TENANT, date(2026, 8, 1), USER, "first attempt died")
    failed_id = db.query(models.NightAudit).one().id

    audit = nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1))
    db.commit()

    assert audit.id == failed_id
    assert audit.audit_status == "Completed"
    assert audit.error_message is None
    assert db.query(models.NightAudit).count() == 1


def test_occupancy_percent_is_omitted_when_inventory_is_unknown(db):
    """rooms_total comes from another service over HTTP and may be
    unavailable; the audit must still record, without inventing a percentage."""
    set_business_date(db, date(2026, 8, 1))
    make_reservation(db, date(2026, 8, 1), date(2026, 8, 2))

    audit = nas.run_audit(db, TENANT, USER, expected_business_date=date(2026, 8, 1),
                          rooms_total=None)
    db.commit()
    assert audit.rooms_occupied == 1
    assert audit.rooms_total is None
    assert audit.occupancy_percent is None


def test_business_date_is_seeded_once_and_reused(db):
    first = nas.ensure_business_date(db, TENANT, USER)
    second = nas.ensure_business_date(db, TENANT, USER)
    assert first.id == second.id
    assert db.query(models.HotelBusinessDate).count() == 1

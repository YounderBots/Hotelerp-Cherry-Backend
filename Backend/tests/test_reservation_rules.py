"""Reservation business rules. Run from inside HotelServices:

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_reservation_rules.py -v

No database required -- everything here is a pure function of its arguments.

WHY THIS EXISTS
Reservation is the module where a wrong answer costs money or a room, and
three kinds of wrong answer are worth pinning down:

  A STATUS MOVE THAT SHOULD BE IMPOSSIBLE
      The API used to accept Cancelled -> Checked-In, which resurrected a
      room that had already been released and let an abandoned booking start
      accruing revenue again. The transition table is the only thing standing
      between the front desk and that, so it is asserted move by move rather
      than in aggregate.

  A NIGHT COUNTED WRONGLY
      Room charges are per night and `no_of_nights` used to arrive as a form
      field -- the API accepted 99 nights for a two-night stay. Everything now
      derives from the dates, so the derivation is pinned.

  AN ACTION OFFERED THAT WOULD DO NOTHING
      `can_transition` treats staying put as legal, because an edit that does
      not change the status must not be refused. Used directly to decide
      whether to draw a button, that said a cancelled booking could be
      cancelled. `can_offer` is the distinction, and it is easy to lose again.
"""

from datetime import date

import pytest

from resources import reservation_rules as rules


# ---------------------------------------------------------------------------
# Status vocabulary folding
# ---------------------------------------------------------------------------
# The labels are Master Data and a property can retype them, so every
# comparison folds case, spaces and hyphens. "No-Show", "No Show" and "noshow"
# are the same status.

@pytest.mark.parametrize("value,expected", [
    ("No-Show", "noshow"),
    ("No Show", "noshow"),
    ("NOSHOW", "noshow"),
    ("Checked-In", "checkedin"),
    ("checked in", "checkedin"),
    ("On Hold", "onhold"),
    (None, ""),
    ("", ""),
])
def test_status_folding(value, expected):
    assert rules.normalise_status(value) == expected


@pytest.mark.parametrize("status", ["Cancelled", "cancelled", "No-Show", "No Show", "noshow"])
def test_cancelled_and_no_show_release_the_room(status):
    """These two are why a cancelled booking stops blocking its dates."""
    assert rules.releases_inventory(status) is True


@pytest.mark.parametrize("status", ["Confirmed", "Checked-In", "Checked-Out", "Pending", "On Hold"])
def test_every_other_status_still_holds_the_room(status):
    # Checked-Out included on purpose: those nights were sold and cannot be
    # sold again, even though the guest has left.
    assert rules.releases_inventory(status) is False


# ---------------------------------------------------------------------------
# Transitions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("current,target", [
    ("Confirmed", "Checked-In"),
    ("Confirmed", "Cancelled"),
    ("Confirmed", "No-Show"),
    ("Pending", "Confirmed"),
    ("Pending", "Checked-In"),
    ("On Hold", "Confirmed"),
    ("On Hold", "Cancelled"),
    ("Checked-In", "Checked-Out"),
])
def test_legal_transitions_are_allowed(current, target):
    assert rules.can_transition(current, target) is True


@pytest.mark.parametrize("current,target", [
    # The one this table exists to refuse.
    ("Cancelled", "Checked-In"),
    ("Cancelled", "Confirmed"),
    ("Cancelled", "Checked-Out"),
    ("No-Show", "Checked-In"),
    ("No-Show", "Confirmed"),
    ("Checked-Out", "Checked-In"),
    ("Checked-Out", "Confirmed"),
    ("Checked-Out", "Cancelled"),
    # A guest cannot depart without having arrived.
    ("Confirmed", "Checked-Out"),
    ("Pending", "Checked-Out"),
    # Nor be marked a no-show once they are in the room.
    ("Checked-In", "No-Show"),
    ("Checked-In", "Cancelled"),
])
def test_illegal_transitions_are_refused(current, target):
    assert rules.can_transition(current, target) is False


@pytest.mark.parametrize("status", ["Confirmed", "Cancelled", "Checked-Out", "No-Show"])
def test_staying_put_is_always_legal(status):
    """An edit that does not change the status must not be refused by it."""
    assert rules.can_transition(status, status) is True


def test_a_new_reservation_may_open_in_any_status():
    """There is no prior status to move from when one is being created."""
    assert rules.can_transition(None, rules.CONFIRMED) is True
    assert rules.can_transition("", rules.PENDING) is True


def test_a_property_defined_status_is_not_constrained():
    """`reservation_status` is Master Data; a property may add its own row.

    Refusing a status the operator deliberately configured would be this
    module overruling their configuration, so unknown statuses stay open.
    """
    assert rules.can_transition("Awaiting Deposit", rules.CANCELLED) is True


def test_assert_transition_raises_with_a_409_and_names_both_states():
    with pytest.raises(rules.RuleError) as exc:
        rules.assert_transition("Cancelled", rules.CHECKED_IN)
    assert exc.value.status_code == 409
    assert "Cancelled" in exc.value.detail
    assert "Checked-In" in exc.value.detail


# ---------------------------------------------------------------------------
# Cancelling is not idempotent, so it must not be offered twice
# ---------------------------------------------------------------------------

def test_cancelling_an_already_cancelled_booking_is_not_offered():
    """The rule the endpoint now enforces before writing.

    `POST /room_reservation_cancel/{key}` used to accept a second call. It
    re-applied the status and then overwrote `cancellation_reason`,
    `cancelled_at` and `cancelled_by` -- so the record of WHY a booking was
    cancelled, the one thing the endpoint insists on asking for, was silently
    replaceable by anyone who could reach the URL.

    `can_offer` (not `can_transition`) is the correct test: staying put is
    legal for an edit that changes nothing, but a repeat cancel writes over
    the reason.
    """
    assert rules.can_offer("Cancelled", rules.CANCELLED) is False


@pytest.mark.parametrize("current", ["Checked-In", "Checked-Out", "No-Show"])
def test_cancelling_a_booking_past_the_point_is_not_offered(current):
    """A guest who has arrived or departed cannot be cancelled either; the
    folio is settled through checkout, and a no-show is a different fact."""
    assert rules.can_offer(current, rules.CANCELLED) is False


@pytest.mark.parametrize("current", ["Pending", "On Hold", "Confirmed"])
def test_a_live_booking_can_still_be_cancelled(current):
    """The other half: the guard must not refuse a cancellation that should
    happen, or a front desk could not release a room at all."""
    assert rules.can_offer(current, rules.CANCELLED) is True


def test_the_button_and_the_endpoint_agree_by_construction():
    """The UI's Cancel button is drawn from the serialised `can_cancel` flag,
    which is `can_offer(status, CANCELLED)`. The endpoint's guard now consults
    the same call. Asserted here so the two cannot drift: if one is ever
    re-expressed, this is what notices.

    (reservationController.py, the `_serialise` dict:
        "can_cancel": rules.can_offer(reservation.reservation_status,
                                      rules.CANCELLED),
     and reservation_cancel, immediately before writing:
        if not rules.can_offer(reservation.reservation_status, rules.CANCELLED):
    )
    """
    import inspect
    import pathlib
    import re

    src = pathlib.Path(__file__).resolve().parents[1] / "Services" / "HotelServices" / \
        "resources" / "reservationController.py"
    text = src.read_text(encoding="utf-8")
    guard = re.search(
        r"if not rules\.can_offer\(\s*reservation\.reservation_status,\s*rules\.CANCELLED\s*\)\s*:",
        text)
    assert guard, "reservation_cancel no longer guards on can_offer(status, CANCELLED)"
    assert '"can_cancel": rules.can_offer(' in text, (
        "the serialised can_cancel flag no longer comes from can_offer"
    )


# ---------------------------------------------------------------------------
# The controller's guard, exercised through the real function
# ---------------------------------------------------------------------------
# The tests above pin the RULE. This pins the ENDPOINT, because the defect was
# in the endpoint not consulting it: `POST /room_reservation_cancel/{key}`
# accepted a second call and overwrote `cancellation_reason`, `cancelled_at` and
# `cancelled_by`.
#
# `reservation_cancel` is called directly with the three collaborators stubbed
# -- the JWT check, the Master Data snapshot and the row lookup. Nothing touches
# a database, so this is the regression test for the fix and it fails against
# the pre-fix controller.

def _call_cancel(reservation, monkeypatch):
    """Invoke the real `reservation_cancel` against a stand-in reservation.

    It is `async def`, so it is driven through asyncio rather than called
    directly -- calling it and expecting an exception would pass silently,
    because an un-awaited coroutine never runs its body.
    """
    import asyncio

    from fastapi import HTTPException
    from resources import reservationController as rc

    class _Db:
        def commit(self):
            pass

        def refresh(self, _r):
            pass

        def rollback(self):
            pass

    class _Snapshot:
        def __getattr__(self, _name):
            return {}

    monkeypatch.setattr(rc, "verify_authentication",
                        lambda _r: (1, "1", "1", "tok"))
    monkeypatch.setattr(rc, "_load_by_id_or_token",
                        lambda db, company_id, key: reservation)
    monkeypatch.setattr(rc.MasterData, "for_token", staticmethod(lambda _t: _Snapshot()))
    monkeypatch.setattr(rc, "sync_room_booking_status", lambda *a, **k: None)
    monkeypatch.setattr(rc, "server_error", lambda *a, **k: None)
    # A reason is mandatory, and it is read off the request body. Supplying one
    # is deliberate: the point of these tests is the guard AFTER the reason
    # check, so the request has to get past it to reach it.
    async def _body(_request, optional=False):
        return {"cancellation_reason": "supplied by the caller"}
    monkeypatch.setattr(rc, "_json_object", _body)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(rc.reservation_cancel("any-key", None, _Db()))
    return exc.value


def _reservation(status, **kw):
    r = type("R", (), {})()
    r.reservation_status = status
    r.reservation_token = "tok"
    r.token = "tok"
    r.room_ids = [1]
    r.paid_amount = 0.0
    r.cancellation_reason = None
    r.cancelled_at = None
    r.cancelled_by = None
    for k, v in kw.items():
        setattr(r, k, v)
    return r


def test_cancelling_twice_is_refused_and_keeps_the_original_reason(monkeypatch):
    """The defect, restated as an assertion: the second call must be refused."""
    original = "guest changed their mind"
    res = _reservation(rules.CANCELLED, cancellation_reason=original,
                       cancelled_at="2026-10-15 12:20:44", cancelled_by="4")

    exc = _call_cancel(res, monkeypatch)

    assert exc.status_code == 409
    # The caller is told what the record already says, not merely that it failed.
    assert original in exc.detail
    assert "2026-10-15 12:20:44" in exc.detail
    # And nothing was written.
    assert res.cancellation_reason == original
    assert res.cancelled_at == "2026-10-15 12:20:44"
    assert res.cancelled_by == "4"


def test_cancelling_a_departed_guest_is_refused_with_a_useful_answer(monkeypatch):
    """Checked-Out reaches the same guard through a different branch, and the
    message must not claim it was already cancelled."""
    res = _reservation(rules.CHECKED_OUT)
    exc = _call_cancel(res, monkeypatch)
    assert exc.status_code == 409
    assert "Checked-Out" in exc.detail
    assert "already cancelled" not in exc.detail


def test_a_booking_past_the_point_is_not_told_to_amend_it(monkeypatch):
    """The already-cancelled branch suggests amending the booking; that advice
    would be nonsense for a guest who has already left."""
    res = _reservation(rules.CHECKED_IN)
    exc = _call_cancel(res, monkeypatch)
    assert exc.status_code == 409
    assert "amend the booking" not in exc.detail
    assert "checkout" in exc.detail


# ---------------------------------------------------------------------------
# can_offer -- legal AND a change
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status,target", [
    ("Cancelled", rules.CANCELLED),
    ("No-Show", rules.NO_SHOW),
    ("Checked-In", rules.CHECKED_IN),
    ("Checked-Out", rules.CHECKED_OUT),
])
def test_an_action_that_would_change_nothing_is_not_offered(status, target):
    """This is the bug it was extracted for: the View modal offered
    "Cancel reservation" on a reservation that was already cancelled."""
    assert rules.can_transition(status, target) is True   # legal, but...
    assert rules.can_offer(status, target) is False       # ...pointless


@pytest.mark.parametrize("target", [rules.CHECKED_IN, rules.CANCELLED, rules.NO_SHOW])
def test_a_terminal_reservation_offers_nothing(target):
    for terminal in rules.TERMINAL:
        assert rules.can_offer(terminal, target) is False


@pytest.mark.parametrize("status,target", [
    ("Confirmed", rules.CHECKED_IN),
    ("Confirmed", rules.CANCELLED),
    ("On Hold", rules.NO_SHOW),
    ("Pending", rules.CHECKED_IN),
])
def test_a_real_move_is_offered(status, target):
    assert rules.can_offer(status, target) is True


# ---------------------------------------------------------------------------
# Nights
# ---------------------------------------------------------------------------

def test_the_worked_example_from_the_spec():
    """10 Aug -> 12 Aug is two nights, not three and not one."""
    assert rules.nights_between(date(2026, 8, 10), date(2026, 8, 12)) == 2


@pytest.mark.parametrize("arrival,departure,expected", [
    (date(2026, 8, 1), date(2026, 8, 2), 1),
    (date(2026, 8, 1), date(2026, 8, 8), 7),
    # Across a month boundary, and across a leap day.
    (date(2026, 1, 30), date(2026, 2, 2), 3),
    (date(2028, 2, 27), date(2028, 3, 1), 3),
])
def test_night_counts(arrival, departure, expected):
    assert rules.nights_between(arrival, departure) == expected


# ---------------------------------------------------------------------------
# Billable units -- weekly rates bill per STARTED week
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nights,expected", [(1, 1), (7, 1), (8, 2), (14, 2), (15, 3)])
def test_weekly_rate_bills_per_started_week(nights, expected):
    assert rules.units_for("weekly", nights) == expected


@pytest.mark.parametrize("rate", ["daily", "bed_only", "bed_breakfast", "half_board", "full_board"])
def test_every_other_rate_bills_per_night(rate):
    assert rules.units_for(rate, 5) == 5


def test_a_stay_always_bills_at_least_one_unit():
    """Guards the zero-night edge rather than pricing a stay at nothing."""
    assert rules.units_for("daily", 0) == 1
    assert rules.units_for("weekly", 0) == 1


# ---------------------------------------------------------------------------
# Rate lookup
# ---------------------------------------------------------------------------

class _RoomType:
    """Just enough of a room type, as the Master Data API sends it, to price a line."""

    def __init__(self, **kw):
        self.daily_rate = kw.get("daily")
        self.weekly_rate = kw.get("weekly")
        self.bed_only_rate = kw.get("bed_only")
        self.bed_breakfast_rate = kw.get("bed_breakfast")
        self.half_board_rate = kw.get("half_board")
        self.full_board_rate = kw.get("full_board")
        self.room_cost = kw.get("room_cost", 0)


def test_bed_and_breakfast_reads_the_column_it_is_stored_in():
    """The frontend's old copy of this map spelled the column
    `bed_and_breakfast_rate` while the API returns `bed_breakfast_rate`, so
    choosing that rate looked up a field that was not there and priced the
    room at zero."""
    rt = _RoomType(daily=3500, bed_breakfast=3850)
    assert rules.rate_for(rt, "bed_breakfast") == 3850


def test_an_unpriced_rate_type_falls_back_to_daily():
    rt = _RoomType(daily=3500, room_cost=3000)
    assert rules.rate_for(rt, "half_board") == 3500


def test_a_room_type_with_no_rates_at_all_falls_back_to_room_cost():
    """Pricing a stay at zero is worse than pricing it at the base cost."""
    rt = _RoomType(room_cost=2750)
    assert rules.rate_for(rt, "daily") == 2750


def test_an_unknown_rate_type_is_priced_daily():
    rt = _RoomType(daily=3500)
    assert rules.rate_for(rt, "nonsense") == 3500


# ---------------------------------------------------------------------------
# Money rounding
# ---------------------------------------------------------------------------

def test_money_rounds_to_two_places():
    # 14000 * 0.12 is 1680.0000000000002 in binary floating point; stored
    # unrounded, the View modal shows a total that does not equal its parts.
    assert rules.money(14000 * 0.12) == 1680.0
    assert rules.money(0.1 + 0.2) == 0.3


@pytest.mark.parametrize("value", [None, "", "abc", object()])
def test_money_treats_unusable_input_as_zero(value):
    assert rules.money(value) == 0.0


# ---------------------------------------------------------------------------
# Early departure
# ---------------------------------------------------------------------------
# A guest leaving before their booked departure is two separate facts: the room
# is free from that day, and the bill may or may not shrink. This decides only
# the first half -- how many nights were actually used -- and the checkout
# endpoint carries the policy decision about the second.

ARRIVE = date(2026, 8, 10)
DEPART = date(2026, 8, 15)          # 5 nights booked


def test_leaving_early_counts_only_the_nights_slept():
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 5, date(2026, 8, 12))
    assert (early, actual, unused) == (True, 2, 3)


def test_leaving_on_the_booked_departure_is_not_early():
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 5, DEPART)
    assert (early, actual, unused) == (False, 5, 0)


def test_overstaying_is_not_an_early_departure():
    """Past the booked departure there is nothing to refund."""
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 5, date(2026, 8, 20))
    assert (early, actual, unused) == (False, 5, 0)


def test_leaving_on_the_arrival_day_still_bills_one_night():
    """A hotel does not sell a zero-night stay; treating a same-day departure
    as one would price the room at nothing."""
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 5, ARRIVE)
    assert early is False
    assert actual == 5


def test_leaving_the_morning_after_arrival_bills_one_night():
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 5, date(2026, 8, 11))
    assert (early, actual, unused) == (True, 1, 4)


@pytest.mark.parametrize("day,expected_actual", [
    (date(2026, 8, 11), 1),
    (date(2026, 8, 12), 2),
    (date(2026, 8, 13), 3),
    (date(2026, 8, 14), 4),
])
def test_every_night_of_the_stay(day, expected_actual):
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 5, day)
    assert early is True
    assert actual == expected_actual
    assert actual + unused == 5


def test_unused_nights_never_go_negative():
    """Guards a booked_nights that disagrees with the dates -- legacy rows
    exist where it was a form field the client could set to anything."""
    early, actual, unused = rules.early_departure(ARRIVE, DEPART, 1, date(2026, 8, 14))
    assert unused == 0


# ---------------------------------------------------------------------------
# Check-in date guard
# ---------------------------------------------------------------------------

def test_a_stay_departing_today_has_not_ended():
    """A one-night stay that arrived yesterday departs today, and checking
    that guest in today is ordinary. The first version of this guard used <=
    and refused every same-day departure, claiming the date had passed."""
    assert rules.stay_has_ended(date(2026, 9, 1), date(2026, 9, 1)) is False


def test_a_stay_departing_in_the_past_has_ended():
    assert rules.stay_has_ended(date(2026, 8, 30), date(2026, 9, 1)) is True


def test_a_future_stay_has_not_ended():
    """An early arrival is legitimate; the booking is still ahead of them."""
    assert rules.stay_has_ended(date(2026, 9, 5), date(2026, 9, 1)) is False


# ---------------------------------------------------------------------------
# Deletion guard messages
#
# Found live: the delete endpoint gave a Checked-In and a Checked-Out
# reservation the SAME message -- "cannot be deleted, check the guest out
# first" -- which is actionable advice for the first and nonsense for the
# second, since a Checked-Out guest has already been checked out. The block
# itself was correct in both cases; only the wording lied about there being a
# next step for a stay that is actually terminal.
# ---------------------------------------------------------------------------

def test_a_checked_in_guest_gets_actionable_advice():
    reason = rules.deletion_block_reason("Checked-In", 0)
    assert reason is not None
    assert "check the guest out" in reason.lower()


def test_a_checked_out_stay_is_not_told_to_check_out_again():
    """The bug this guards: telling an already-departed guest's record to
    'check the guest out first' describes an action that cannot be taken."""
    reason = rules.deletion_block_reason("Checked-Out", 0)
    assert reason is not None
    assert "check the guest out" not in reason.lower()
    assert "complete" in reason.lower() or "history" in reason.lower()


def test_a_checked_out_stay_is_blocked_even_with_no_balance():
    """The historical record is protected regardless of what is still owed --
    it is the STATUS that makes it terminal, not the money."""
    assert rules.deletion_block_reason("Checked-Out", 0) is not None


def test_an_unpaid_unarrived_reservation_may_be_deleted():
    assert rules.deletion_block_reason("Confirmed", 0) is None


def test_a_paid_but_not_yet_arrived_reservation_must_be_cancelled_not_deleted():
    reason = rules.deletion_block_reason("Confirmed", 1500)
    assert reason is not None
    assert "cancel" in reason.lower()


def test_cancelled_and_no_show_reservations_may_be_deleted():
    """Terminal statuses that carry no money owed are not protected the way
    Checked-Out is -- there was never a completed stay to preserve."""
    assert rules.deletion_block_reason("Cancelled", 0) is None
    assert rules.deletion_block_reason("No-Show", 0) is None

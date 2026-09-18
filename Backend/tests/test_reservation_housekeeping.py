"""The checkout -> housekeeping handover. Run from inside HotelServices:

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_reservation_housekeeping.py -v

No MySQL and no HTTP. The Hotel schema is an in-memory SQLite database; Master
Data is `fake_master.FakeMaster`, an in-memory stand-in for the
MasterDataServices API behind the real client, so every room-state write here
goes through the same `PUT /room/{id}/state` call production makes -- and
`master.writes()` says exactly what was written.

WHY THIS EXISTS
When a guest departs, two separate facts become true and BOTH have to be
recorded or the property loses track of the room:

    the room is free to sell again   -- `Room_Booking_status`, recomputed from
                                        reservations by sync_room_booking_status
    the room is dirty                -- `Room_Working_status`, which nothing
                                        derives, because once a cleaner marks a
                                        room Ready only housekeeping knows that

The second is what this module writes, once, at the moment of checkout. It is
deliberately NOT part of the reconcile: folding it in would re-dirty a room
every time the reconcile ran, erasing the cleaner's work on the next booking.
That one-way property is the thing most likely to be "tidied up" by a later
change, so it is pinned here.
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models.models as models
from fake_master import FakeMaster
from resources import reservationController as rc
from resources.master_client import MasterData

TENANT = "1"

READY = "Ready"
NOT_READY = "Not Ready"
UNASSIGNED = "Not Assigne"  # the master schema's own spelling


@pytest.fixture()
def db():
    """The Hotel schema -- and only the Hotel schema."""
    engine = sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture()
def master() -> FakeMaster:
    """Master Data, as the property's own service would answer for it.

    Whatever is in here IS this property's master data: the real service
    scopes the snapshot by the caller's company, so another tenant's room
    is simply not in it.
    """
    return FakeMaster()


@pytest.fixture()
def md(master) -> MasterData:
    """One request's client. A later request is `MasterData(master)` again."""
    return MasterData(master)


def make_room(master, room_id, room_no=None, working=READY,
              room_status="UnBlocking", status="ACTIVE", **more):
    return master.add_room(
        id=room_id, room_no=room_no or str(100 + room_id),
        working_status=working, room_status=room_status, status=status, **more,
    )


def working_status(master, room_id):
    """What Master Data now holds -- the fixture, not the client's copy."""
    return master.room(room_id)["working_status"]


# ---------------------------------------------------------------------------
# The handover itself
# ---------------------------------------------------------------------------

def test_a_departed_room_is_flagged_for_cleaning(db, md, master):
    make_room(master, 1, room_no="101", working=READY)

    marked = rc.mark_rooms_for_housekeeping(md, [1])

    assert marked == ["101"]
    assert working_status(master, 1) == NOT_READY


def test_every_room_on_a_multi_room_booking_is_flagged(db, md, master):
    make_room(master, 1, room_no="101")
    make_room(master, 2, room_no="102")
    make_room(master, 3, room_no="103")

    marked = rc.mark_rooms_for_housekeeping(md, [1, 2, 3])

    assert sorted(marked) == ["101", "102", "103"]
    assert all(working_status(master, r) == NOT_READY for r in (1, 2, 3))


def test_a_room_already_dirty_is_not_reported_as_newly_marked(db, md, master):
    """The return value drives the message the desk is shown, so it lists only
    what actually changed. A room already awaiting cleaning is left alone."""
    make_room(master, 1, room_no="101", working=NOT_READY)

    marked = rc.mark_rooms_for_housekeeping(md, [1])

    assert marked == []
    assert working_status(master, 1) == NOT_READY


def test_an_unassigned_room_is_moved_to_needs_cleaning(db, md, master):
    """'Not Assigne' is the master schema's third readiness value. A guest has
    just left the room, so it needs cleaning regardless of what it said before."""
    make_room(master, 1, room_no="101", working=UNASSIGNED)

    marked = rc.mark_rooms_for_housekeeping(md, [1])

    assert marked == ["101"]
    assert working_status(master, 1) == NOT_READY


# ---------------------------------------------------------------------------
# What it must NOT touch
# ---------------------------------------------------------------------------

def test_an_out_of_order_room_is_left_alone(db, md, master):
    """Blocked means out of order, which is a stronger statement than "needs
    cleaning" and is not this module's to overwrite. Downgrading it would put a
    broken room back into housekeeping's ordinary queue."""
    make_room(master, 1, room_no="101", working=READY, room_status="Blocking")

    marked = rc.mark_rooms_for_housekeeping(md, [1])

    assert marked == []
    assert working_status(master, 1) == READY


def test_another_tenants_room_is_never_touched(db, md, master):
    """Master Data scopes the snapshot by the caller's company, so a room that
    belongs to another property is not in it at all -- there is nothing here
    to reach across to. What a reservation names and the snapshot lacks is
    left alone, and no write is attempted."""
    marked = rc.mark_rooms_for_housekeeping(md, [1])

    assert marked == []
    assert master.writes() == []


def test_a_soft_deleted_room_is_never_touched(db, md, master):
    make_room(master, 1, room_no="101", status="INACTIVE", working=READY)

    marked = rc.mark_rooms_for_housekeeping(md, [1])

    assert marked == []
    assert working_status(master, 1) == READY


def test_an_unknown_room_id_is_ignored_rather_than_raising(db, md, master):
    """A reservation can name a room that has since been deleted from Master
    Data. Checkout must still succeed -- the guest has left either way."""
    make_room(master, 1, room_no="101")

    marked = rc.mark_rooms_for_housekeeping(md, [1, 999])

    assert marked == ["101"]


@pytest.mark.parametrize("room_ids", [None, [], ()])
def test_no_rooms_is_a_no_op(db, md, master, room_ids):
    assert rc.mark_rooms_for_housekeeping(md, room_ids) == []


def test_duplicate_room_ids_are_collapsed(db, md, master):
    """`room_ids` comes off the reservation, which has carried duplicates."""
    make_room(master, 1, room_no="101")

    marked = rc.mark_rooms_for_housekeeping(md, [1, 1, 1])

    assert marked == ["101"]


def test_string_room_ids_are_accepted(db, md, master):
    """JSON round trips have turned these into strings before now."""
    make_room(master, 7, room_no="107")

    marked = rc.mark_rooms_for_housekeeping(md, ["7"])

    assert marked == ["107"]
    assert working_status(master, 7) == NOT_READY


# ---------------------------------------------------------------------------
# The one-way property
# ---------------------------------------------------------------------------

def test_the_reconcile_does_not_undo_housekeepings_work(db, md, master):
    """THE POINT OF THE WHOLE DESIGN.

    A cleaner marks the room Ready. Something then triggers the booking-status
    reconcile -- a new booking, an edit, another checkout. The room must still
    be Ready afterwards: `sync_room_booking_status` recomputes occupancy from
    reservations and has no business touching readiness, which is not derivable
    from reservations at all.

    If someone ever folds the housekeeping flag into the reconcile "so it stays
    consistent", this fails.
    """
    make_room(master, 1, room_no="101", working=READY)

    rc.mark_rooms_for_housekeeping(md, [1])
    assert working_status(master, 1) == NOT_READY

    # Housekeeping cleans it -- in Master Data, from its own screen.
    master.room(1)["working_status"] = READY

    # Anything at all triggers the reconcile, on a later request.
    rc.sync_room_booking_status(db, MasterData(master), TENANT, [1])
    db.commit()

    assert working_status(master, 1) == READY
    # And the reconcile never sent a word about readiness over the wire.
    assert all("working_status" not in body for _rid, body in master.writes()[1:])


def test_the_reconcile_frees_the_room_for_sale_without_cleaning_it(db, md, master):
    """The two facts are independent: sellable again, and still dirty."""
    make_room(master, 1, room_no="101", working=READY, booking_status="Occupied")

    rc.mark_rooms_for_housekeeping(md, [1])
    rc.sync_room_booking_status(db, md, TENANT, [1])
    db.commit()

    row = master.room(1)
    assert row["booking_status"] == "Available"   # free to sell
    assert row["working_status"] == NOT_READY     # and dirty
    # Two facts, two writes, each carrying only its own fact.
    assert master.writes() == [(1, {"working_status": NOT_READY}),
                               (1, {"booking_status": "Available"})]


# ---------------------------------------------------------------------------
# Who is shown a guest's contact details
#
# `/hotel/user_activity_log` serves two screens. /user_reserved_details is a
# guest contact list; /dashboard shows a name and a status and renders neither
# the phone nor the email -- but both used to cross the wire to it anyway.
#
# The decision is made inside the service from the SIGNED `perm` claim, not
# from a request parameter and not by the gateway. That matters: the gateway
# ships in `audit` mode by default, where it logs a refusal instead of making
# one, so a route-level rule alone would not actually withhold anything.
# ---------------------------------------------------------------------------

from resources.utils import PERM_VIEW, can_view_any, token_permissions  # noqa: E402


def _token(perm):
    """Mint a token the same way the gateway does, for claim-reading tests."""
    import sys
    from pathlib import Path

    login = Path(__file__).resolve().parents[1] / "Services" / "LoginServices"
    if str(login) not in sys.path:
        sys.path.insert(0, str(login))
    # HotelServices and LoginServices share SECRET_KEY/ALGORITHM/JWT_ISSUER --
    # that shared secret is what lets a service trust the gateway's claim.
    from jose import jwt as jose_jwt

    from configs import BaseConfig

    import datetime as _dt

    now = _dt.datetime.now(_dt.timezone.utc)
    payload = {
        "user_id": 1,
        "company_id": "1",
        "iss": BaseConfig.JWT_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + _dt.timedelta(minutes=5)).timestamp()),
    }
    if perm is not None:
        payload["perm"] = perm
    return jose_jwt.encode(payload, BaseConfig.SECRET_KEY, algorithm=BaseConfig.ALGORITHM)


def test_a_contact_list_role_sees_contact_details():
    token = _token({"/user_reserved_details": PERM_VIEW})
    assert can_view_any(token, "/user_reserved_details", "/reservation") is True


def test_a_reservation_role_sees_contact_details():
    """Not a new capability: /reservation already shows phone and email."""
    token = _token({"/reservation": PERM_VIEW})
    assert can_view_any(token, "/user_reserved_details", "/reservation") is True


def test_a_dashboard_only_role_does_not():
    token = _token({"/dashboard": PERM_VIEW})
    assert can_view_any(token, "/user_reserved_details", "/reservation") is False


def test_a_page_held_without_view_does_not_count():
    """Holding edit but not view on a page is not permission to read it."""
    token = _token({"/reservation": 4})  # EDIT only
    assert can_view_any(token, "/reservation") is False


def test_an_empty_claim_grants_nothing():
    """The gateway mints `perm: {}` when the permission service is unreachable.
    Such a token must not unlock more than a fully-specified one."""
    assert can_view_any(_token({}), "/reservation") is False


def test_a_token_without_a_perm_claim_grants_nothing():
    assert can_view_any(_token(None), "/reservation") is False
    assert token_permissions(_token(None)) == {}


def test_an_unreadable_token_grants_nothing_rather_than_raising():
    """Callers are already authenticated by this point; a claim that cannot be
    read must degrade to 'no extra permissions', never to a 500."""
    assert token_permissions("not-a-jwt") == {}
    assert can_view_any("not-a-jwt", "/reservation") is False


def test_a_forged_claim_is_rejected_with_the_signature():
    """The claim is only trustworthy because the token is signed. A token
    signed with the wrong key must not be read at all."""
    from jose import jwt as jose_jwt

    forged = jose_jwt.encode(
        {"user_id": 1, "perm": {"/reservation": PERM_VIEW}},
        "not-the-real-secret",
        algorithm="HS256",
    )
    assert can_view_any(forged, "/reservation") is False

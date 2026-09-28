"""Validation contract for the room-booking (enquiry) write endpoints.

The browser validates the booking form, but the API is independently callable.
These tests pin the service-boundary checks that prevent malformed or dangling
enquiry rows from being persisted.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from resources import reservationController as controller


class _FakeMaster:
    def __init__(self):
        self.calls = 0

    def active_room_types(self):
        self.calls += 1
        return {1: object(), 2: object()}


@pytest.fixture()
def fake_master(monkeypatch):
    master = _FakeMaster()
    monkeypatch.setattr(
        controller.MasterData,
        "for_token",
        classmethod(lambda cls, token: master),
    )
    return master


def payload(**overrides):
    value = {
        "salutation": "Mr.",
        "first_name": "QA",
        "last_name": "Booking",
        "phone_number": "+1 555 123 4567",
        "email": "QA.BOOKING@example.com",
        "arrival_date": "2026-12-01",
        "departure_date": "2026-12-02",
        "room_type": [1],
        "no_of_rooms": 1,
        "no_of_adults": 1,
        "no_of_children": 0,
    }
    value.update(overrides)
    return value


def assert_bad(call, detail_part):
    with pytest.raises(HTTPException) as raised:
        call()
    assert raised.value.status_code == 400
    assert detail_part in raised.value.detail


def test_valid_payload_is_canonicalised_and_room_types_are_checked(fake_master):
    result = controller._validate_booking_payload(payload(), "token")

    assert result["email"] == "qa.booking@example.com"
    assert result["room_type_ids"] == [1]
    assert result["no_of_rooms"] == 1
    assert fake_master.calls == 1


@pytest.mark.parametrize(
    "overrides, detail",
    [
        ({"arrival_date": "not-a-date"}, "valid ISO date"),
        ({"departure_date": "2026-11-30"}, "after arrival"),
        ({"phone_number": ""}, "phone_number"),
        ({"first_name": ""}, "first_name"),
        ({"no_of_rooms": 0}, "at least 1"),
        ({"no_of_adults": 0}, "at least 1"),
        ({"no_of_children": -1}, "at least 0"),
        ({"room_type": []}, "non-empty"),
        ({"room_type": [1, 2]}, "exactly one room type"),
        ({"room_type": [True]}, "integer"),
    ],
)
def test_invalid_boundaries_are_client_errors(fake_master, overrides, detail):
    assert_bad(
        lambda: controller._validate_booking_payload(payload(**overrides), "token"),
        detail,
    )
    # Fail-fast boundaries do not need a dependency round trip.
    if detail not in {"exactly one room type", "non-empty"}:
        assert fake_master.calls == 0


def test_unknown_room_type_is_rejected_after_master_data_lookup(fake_master):
    assert_bad(
        lambda: controller._validate_booking_payload(payload(room_type=[999]), "token"),
        "Unknown or inactive room type",
    )
    assert fake_master.calls == 1


def test_boolean_id_is_not_accepted_as_an_integer(fake_master):
    assert_bad(
        lambda: controller._validate_booking_payload(
            payload(room_type=[True]), "token"
        ),
        "integer",
    )

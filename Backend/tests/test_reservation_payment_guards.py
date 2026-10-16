"""Hotel payment and refund amounts must be finite. Run from HotelServices:

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_reservation_payment_guards.py -q

`rules.money` is `round(float(x), 2)`, and `round(nan, 2)` is nan. Python's
json decoder accepts a bare `NaN`, so `{"paying_amount": NaN}` reached the
endpoint as nan, passed both `<= 0` and `> balance` (every comparison with nan
is False), and failed only at the insert, as a 500. The venue billing code has
refused non-finite amounts for a while (`billingController._finite`); this is
the same rule on the hotel side.

The refusal happens before the reservation is loaded, so no database is
needed: authentication, Master Data and the method lookup are stubbed.
"""

import asyncio
import json

import pytest
from fastapi import HTTPException

from resources import reservationController as rc


class _Request:
    def __init__(self, raw: str):
        self._raw = raw

    async def json(self):
        return json.loads(self._raw)


class _Touched(BaseException):
    """BaseException, so the endpoints' `except Exception -> 500` lets it through."""


class _Db:
    """Any database access means the guard did not fire first."""

    def __getattr__(self, name):
        raise _Touched(name)


@pytest.fixture(autouse=True)
def stubs(monkeypatch):
    monkeypatch.setattr(rc, "verify_authentication", lambda request: ("1", "1", "1", "tok"))
    monkeypatch.setattr(rc.MasterData, "for_token", classmethod(lambda cls, token: object()))
    monkeypatch.setattr(rc, "_resolve_method_name", lambda md, name, label: name)


def _call(handler, raw):
    return asyncio.run(handler("RES-1", _Request(raw), _Db()))


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity", '"nan"', '"inf"'])
def test_payment_refuses_a_non_finite_amount(literal):
    raw = f'{{"payment_method": "Cash", "paying_amount": {literal}}}'
    with pytest.raises(HTTPException) as exc:
        _call(rc.reservation_pay_due_amount, raw)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("literal", ["NaN", "Infinity", '"nan"'])
def test_refund_refuses_a_non_finite_amount(literal):
    raw = f'{{"refund_method": "Cash", "refund_amount": {literal}}}'
    with pytest.raises(HTTPException) as exc:
        _call(rc.reservation_refund_extra_amount, raw)
    assert exc.value.status_code == 400


def test_a_finite_amount_gets_past_the_guard():
    """Control: a real amount goes on to load the reservation."""
    with pytest.raises(_Touched):
        _call(rc.reservation_pay_due_amount, '{"payment_method": "Cash", "paying_amount": 500}')

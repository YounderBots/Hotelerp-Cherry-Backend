"""Bill payment money guards. Run from inside BarServices or RestaurantServices:

    cd Backend/Services/BarServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_bill_payment.py -v

Both services expose the same POST /bill/{id}/payment with the same shape, so
this module detects which one it is running inside and exercises that service's
models. No MySQL is required -- the schema is built in in-memory SQLite.

WHY THIS EXISTS
Before these guards, record_payment checked only that the bill existed, was not
cancelled, and that the amount was positive. Nothing stopped a 50,000 payment
against a 500 bill, or a second full payment on a bill already marked Paid.
`total_paid` then exceeded `grand_total` with no record of the excess, and the
`max(..., 0)` clamp on the balance in the response hid the result rather than
preventing it. The hotel side already refused this; billing was newer code that
never got the same check.
"""

from datetime import date, time

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

import models.models as models
from resources import billingController

# Which service are we running inside?
if hasattr(models, "BarBill"):
    Bill, Payment = models.BarBill, models.BarBillPayment
    Method = models.BarPaymentMethod
elif hasattr(models, "RestaurantBill"):
    Bill, Payment = models.RestaurantBill, models.RestaurantBillPayment
    Method = models.PaymentMethod
else:  # pragma: no cover - guards a wrong cwd
    raise RuntimeError("run this from BarServices or RestaurantServices")

TENANT = "1"
USER = "1"
METHOD_ID = 1


@pytest.fixture()
def db():
    engine = sa.create_engine("sqlite://")
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    # Every property has its payment methods configured before it takes money,
    # so the fixture has one. Without it these tests describe a property that
    # cannot be paid at all, and the money arithmetic they exist to check never
    # runs -- see test_refuses_a_payment_method_the_property_has_not_configured
    # for the case where it is deliberately absent.
    session.add(Method(id=METHOD_ID, method_name="Cash", status="ACTIVE",
                       created_by=USER, company_id=TENANT, branch_id="MAIN"))
    session.commit()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def stub_auth(monkeypatch):
    """The guards under test are about money, not authentication."""
    monkeypatch.setattr(billingController, "_auth", lambda request: (USER, "1", TENANT))


def make_bill(db, grand_total, bill_status="Open", payment_status="Pending"):
    bill = Bill(
        bill_number="B-1", bill_date=date.today(), bill_time=time(12, 0),
        order_id=1, order_number="O-1", grand_total=grand_total,
        bill_status=bill_status, payment_status=payment_status,
        sub_total=grand_total, status="ACTIVE", created_by=USER, company_id=TENANT,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def add_payment(db, bill, amount, payment_status="Success"):
    db.add(Payment(
        bill_id=bill.id, payment_method_id=1, paid_amount=amount,
        payment_date=date.today(), payment_time=time(12, 0),
        payment_status=payment_status, status="ACTIVE",
        created_by=USER, company_id=TENANT,
    ))
    db.commit()


def pay(db, bill, amount):
    payload = billingController.PaymentIn(payment_method_id=1, paid_amount=amount)
    return billingController.record_payment(bill.id, payload, None, db)


# --------------------------------------------------------------------------
# The guards this module was written for
# --------------------------------------------------------------------------

def test_rejects_payment_larger_than_the_bill(db):
    bill = make_bill(db, 500.0)
    with pytest.raises(HTTPException) as exc:
        pay(db, bill, 50_000.0)
    assert exc.value.status_code == 400
    assert "outstanding balance" in exc.value.detail


def test_rejects_a_second_payment_on_a_fully_paid_bill(db):
    bill = make_bill(db, 500.0)
    add_payment(db, bill, 500.0)
    with pytest.raises(HTTPException) as exc:
        pay(db, bill, 100.0)
    assert exc.value.status_code == 400
    assert "already fully paid" in exc.value.detail


def test_rejects_a_part_payment_that_would_overshoot(db):
    bill = make_bill(db, 500.0)
    add_payment(db, bill, 400.0)
    with pytest.raises(HTTPException) as exc:
        pay(db, bill, 200.0)          # only 100 outstanding
    assert exc.value.status_code == 400
    assert "outstanding balance" in exc.value.detail


def test_a_refunded_payment_frees_the_balance_again(db):
    """Only Success payments count toward what has been paid."""
    bill = make_bill(db, 500.0)
    add_payment(db, bill, 500.0, payment_status="Refunded")
    pay(db, bill, 500.0)              # must not raise
    total = sum(p.paid_amount for p in db.query(Payment)
                .filter(Payment.bill_id == bill.id,
                        Payment.payment_status == "Success").all())
    assert total == 500.0


# --------------------------------------------------------------------------
# Legitimate payments must still go through
# --------------------------------------------------------------------------

def test_accepts_payment_of_the_exact_balance(db):
    bill = make_bill(db, 500.0)
    pay(db, bill, 500.0)
    db.refresh(bill)
    assert bill.payment_status == "Paid"


def test_accepts_part_payments_that_add_up(db):
    bill = make_bill(db, 500.0)
    pay(db, bill, 200.0)
    db.refresh(bill)
    assert bill.payment_status == "Partial"
    pay(db, bill, 300.0)
    db.refresh(bill)
    assert bill.payment_status == "Paid"


# --------------------------------------------------------------------------
# Pre-existing guards, kept under test so the new code cannot drop them
# --------------------------------------------------------------------------

def test_still_rejects_a_zero_or_negative_amount(db):
    bill = make_bill(db, 500.0)
    for amount in (0.0, -10.0):
        with pytest.raises(HTTPException) as exc:
            pay(db, bill, amount)
        assert exc.value.status_code == 400
        assert "greater than zero" in exc.value.detail


def test_still_rejects_paying_a_cancelled_bill(db):
    bill = make_bill(db, 500.0, bill_status="Cancelled")
    with pytest.raises(HTTPException) as exc:
        pay(db, bill, 100.0)
    assert exc.value.status_code == 400
    assert "cancelled" in exc.value.detail.lower()


def test_still_rejects_an_unknown_bill(db):
    payload = billingController.PaymentIn(payment_method_id=1, paid_amount=10.0)
    with pytest.raises(HTTPException) as exc:
        billingController.record_payment(9999, payload, None, db)
    assert exc.value.status_code == 404


def test_refuses_a_payment_method_the_property_has_not_configured(db):
    """A 400 naming the field, never a 500 from the foreign key.

    This is the bug the end-to-end sweep of 17 September 2026 found. The
    endpoint validated the amount and the outstanding balance but never the
    method, so an unknown `payment_method_id` reached the INSERT and the
    foreign key rejected it -- `POST /bill/{id}/payment` answered 500 with an
    unhandled IntegrityError, and a till operator was told "Internal server
    error" with no indication of what was wrong.

    It survived a green run because `fnb_flow.py` asserted the refusal as
    `status >= 400`, which a 500 satisfies. Both halves are fixed: the guard
    here, and `api.refused()` there.
    """
    bill = make_bill(db, 500.0)
    payload = billingController.PaymentIn(payment_method_id=999_999, paid_amount=100.0)
    with pytest.raises(HTTPException) as exc:
        billingController.record_payment(bill.id, payload, None, db)
    assert exc.value.status_code == 400
    assert "999999" in exc.value.detail.replace(",", "")
    assert "payment method" in exc.value.detail.lower()


def test_refuses_another_property_s_payment_method(db):
    """Configured, but not by this tenant. Same refusal.

    The method table is shared by every property in the deployment, so an id
    that exists is not by itself an id this company may charge against.
    """
    db.add(Method(id=77, method_name="Other Co Card", status="ACTIVE",
                  created_by=USER, company_id="999", branch_id="MAIN"))
    db.commit()
    bill = make_bill(db, 500.0)
    payload = billingController.PaymentIn(payment_method_id=77, paid_amount=100.0)
    with pytest.raises(HTTPException) as exc:
        billingController.record_payment(bill.id, payload, None, db)
    assert exc.value.status_code == 400

"""What the quote engine puts on a folio. Run from inside HotelServices:

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest \
        ../../tests/test_reservation_pricing.py -v

No MySQL and no HTTP: Master Data is answered by `fake_master.FakeMaster`,
an in-memory stand-in for the MasterDataServices API behind the real client
(`resources/master_client.py`), so the engine prices from records shaped
exactly as production receives them.

WHY THIS SUITE EXISTS
    `quote()` is "the single source of every total", and nothing tested it.
    test_reservation_rules.py covers the pure helpers around it -- rounding,
    nights, status advice -- but the engine that decides money needs a database
    to run, so it had no suite at all. The end-to-end sweep of 17 September
    2026 found what was living in that gap.

    THE FOLIO IDENTITY. `verify_seed.py` asserts, of every reservation:

        room + extra beds + extra charges - discount + tax = overall

    It held for the 25 seeded reservations and failed for every reservation
    booked through the API, because two writers disagreed about one column.
    `extra_bed_cost` is the cost of ONE bed for the whole stay -- the API
    stores it that way and the reservation view draws the pair as
    "1,600.00 x 2" -- but the seed wrote the total for all of them, and the
    invariant was written to match the seed. So the check validated the
    fixtures and rejected the product.

    A RATE FOR BEDS NOBODY BOOKED. Worse, and the half that actually broke the
    sum: the engine derived a per-bed rate from the room type whether or not
    any extra bed was requested, and stored it. A booking with no extra bed
    carried a bed cost on its folio, the reservation view drew
    "1,600.00 x 0", and the identity failed by exactly that rate -- while the
    money charged was right the whole time. That is the worst shape a money
    bug can take: correct totals, wrong record, and an invariant that could
    not tell anyone because it was reading the column the other way.

    Both halves are pinned below.
"""

from __future__ import annotations

import pytest

from fake_master import fake_master
from resources import reservation_rules as rules

ROOM_ID = 1
TYPE_ID = 7

DAILY_RATE = 5000.0
BED_COST = 800.0          # per bed, per night
NIGHTS = 2

# One bed for the whole stay, which is what the folio column holds.
PER_BED_FOR_STAY = BED_COST * NIGHTS          # 1600
ROOM_TOTAL = DAILY_RATE * NIGHTS              # 10000


@pytest.fixture()
def db():
    """The Master Data this property has, as the API would send it."""
    md, master = fake_master()
    master.add_room_type(
        id=TYPE_ID, room_type_name="Deluxe", room_cost=DAILY_RATE, bed_cost=BED_COST,
        daily_rate=DAILY_RATE, weekly_rate=DAILY_RATE * 6,
    )
    master.add_room(id=ROOM_ID, room_no="101", room_type_id=str(TYPE_ID))
    # Percentages are free text in the master schema, exactly as in production.
    master.add_tax(id=3, tax_name="GST 12", tax_percentage="12")
    master.add_discount(id=4, discount_name="Corporate 10", discount_percentage="10")
    return md


def price(md, **kw):
    kw.setdefault("room_ids", [ROOM_ID])
    kw.setdefault("rate_types", ["daily"])
    kw.setdefault("nights", NIGHTS)
    return rules.quote(md, **kw)


def folio_identity_holds(q) -> bool:
    """The sum verify_seed asserts of every stored reservation.

    Deliberately written from the columns as they are PERSISTED
    (`apply_quote`), not from the engine's internal `extra_bed_total`: the
    stored row is what every later reader -- the folio print, the night audit,
    verify_seed -- has to be able to add up.
    """
    left = (q["room_amount"]
            + q["extra_bed_count"] * q["extra_bed_cost"]
            + q["extra_charges"]
            - q["discount_amount"]
            + q["tax_amount"])
    return abs(left - q["overall_amount"]) <= 0.02


# ---------------------------------------------------------------------------
# The bug this suite was written for
# ---------------------------------------------------------------------------

def test_no_extra_bed_means_no_extra_bed_cost(db):
    """The regression. A rate is not a charge.

    The engine derives a per-bed rate from the room type to quote with. When
    no extra bed is taken, that rate must not land on the folio: it was never
    billed, and the row has to stay addable.
    """
    q = price(db, extra_bed_count=0)
    assert q["extra_bed_count"] == 0
    assert q["extra_bed_cost"] == 0
    assert q["extra_bed_total"] == 0
    assert q["overall_amount"] == ROOM_TOTAL
    assert folio_identity_holds(q)


def test_an_explicitly_priced_bed_is_still_dropped_when_none_is_taken(db):
    """Same rule when the caller supplies the rate instead of the room type."""
    q = price(db, extra_bed_count=0, extra_bed_cost=999.0)
    assert q["extra_bed_cost"] == 0
    assert folio_identity_holds(q)


def test_the_stored_bed_cost_is_the_rate_not_the_total(db):
    """`extra_bed_cost` x `extra_bed_count` is the charge.

    The reservation view draws exactly that pair, so storing the total here
    would render a folio line at twice what was billed -- which is what the
    seeded data did before this was fixed.
    """
    q = price(db, extra_bed_count=2)
    assert q["extra_bed_cost"] == PER_BED_FOR_STAY        # 1600, not 3200
    assert q["extra_bed_total"] == PER_BED_FOR_STAY * 2   # the charge
    assert folio_identity_holds(q)


@pytest.mark.parametrize("beds", [0, 1, 2, 5])
def test_the_folio_adds_up_for_any_number_of_beds(db, beds):
    """Including 1, where a rate and a total are the same number.

    That coincidence is why this survived: the seed's only multi-bed booking
    was a single row, and every other seeded stay had one bed or none.
    """
    q = price(db, extra_bed_count=beds, extra_charges=250.0,
              tax_type_id=3, discount_type_id=4)
    assert folio_identity_holds(q)
    assert q["extra_bed_total"] == q["extra_bed_count"] * q["extra_bed_cost"]


def test_the_beds_are_taxed_and_discounted_with_everything_else(db):
    """Beds are part of the taxable base, not a line added after tax."""
    q = price(db, extra_bed_count=2, tax_type_id=3, discount_type_id=4)
    taxable = ROOM_TOTAL + PER_BED_FOR_STAY * 2
    assert q["taxable_amount"] == taxable
    assert q["tax_amount"] == pytest.approx(taxable * 0.12, abs=0.02)
    assert q["discount_amount"] == pytest.approx(taxable * 0.10, abs=0.02)
    assert folio_identity_holds(q)


# ---------------------------------------------------------------------------
# Guards around it that must not be lost to the change above
# ---------------------------------------------------------------------------

def test_a_negative_bed_cost_is_still_refused(db):
    with pytest.raises(rules.RuleError):
        price(db, extra_bed_count=1, extra_bed_cost=-1.0)


def test_a_negative_bed_count_cannot_credit_the_folio(db):
    """A negative count would subtract money if it reached the arithmetic."""
    q = price(db, extra_bed_count=-3)
    assert q["extra_bed_count"] == 0
    assert q["extra_bed_total"] == 0
    assert folio_identity_holds(q)

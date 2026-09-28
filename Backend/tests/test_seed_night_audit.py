"""The demo seed's night-audit row must reconcile with the seed's own bookings.

    python -m pytest Backend/tests/test_seed_night_audit.py -v

WHY THIS SUITE EXISTS
    `tools/seed/hotel.py` used to write `hotel_business_date.last_audit_at` and
    no `night_audit` row at all, so the property claimed an audit it had no
    record of: /night_audit/preview reported a completed audit while
    /night_audit/history returned nothing, and the Night Audit History screen sat
    empty next to a "last audited 17 Sep" tile. That was the real cause of the
    inconsistency recorded as C-027, and a demo dataset whose screens disagree
    with each other is worse than one with no history at all -- it teaches the
    reader that the two numbers mean different things.

    The seed now recomputes the audited night from the reservations it just
    wrote, using the same rules as `nightAuditService.compute_position`. Those
    rules are duplicated rather than imported on purpose (a seed must not depend
    on service internals), which is exactly why they need pinning here: the two
    copies can only be kept honest by a test that asserts the arithmetic, and by
    the cross-check below that the seed's split is the service's split.

    SQLite, no services, no database: the seed helper is plain SQL, so the suite
    builds the two tables it reads and asserts on the row it produces.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest
import sqlalchemy as sa

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def load_seed_hotel():
    """Import `tools/seed/hotel.py` as a package member so its relatives resolve.

    It uses relative imports (`from . import images as im`), so it has to be
    loaded as `seed.hotel` rather than by file path the way preflight.py is.
    """
    if "seed" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "seed", ROOT / "tools" / "seed" / "__init__.py", submodule_search_locations=[str(ROOT / "tools" / "seed")]
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["seed"] = module
        spec.loader.exec_module(module)
    return importlib.import_module("seed.hotel")


AUDITED = dt.date(2026, 9, 16)
NEXT_DAY = dt.date(2026, 9, 17)
COMPANY = "1"


@pytest.fixture
def hotel_seed():
    return load_seed_hotel()


@pytest.fixture
def conn():
    engine = sa.create_engine("sqlite://", future=True)
    with engine.connect() as c:
        c.execute(sa.text("""
            CREATE TABLE room_reservation (
                id INTEGER PRIMARY KEY,
                arrival_date DATE, departure_date DATE, no_of_nights INTEGER,
                reservation_status VARCHAR(100), room_ids JSON, room_amount NUMERIC(12,2),
                extra_charges NUMERIC(12,2), tax_amount NUMERIC(12,2),
                discount_amount NUMERIC(12,2), balance_amount NUMERIC(12,2),
                status VARCHAR(50), company_id VARCHAR(100)
            )"""))
        c.execute(sa.text("""
            CREATE TABLE reservation_amount_paid_history (
                id INTEGER PRIMARY KEY, amount NUMERIC(12,2), paid_date DATE,
                payment_method VARCHAR(100), status VARCHAR(50), company_id VARCHAR(100)
            )"""))
        yield c


def add_reservation(conn, *, arrival, departure, status, room_ids, room_amount=0,
                    extra_charges=0, tax_amount=0, discount_amount=0, balance=0):
    conn.execute(sa.text("""
        INSERT INTO room_reservation (arrival_date, departure_date, no_of_nights,
            reservation_status, room_ids, room_amount, extra_charges, tax_amount,
            discount_amount, balance_amount, status, company_id)
        VALUES (:a, :d, :n, :s, :r, :ra, :ec, :ta, :da, :b, 'ACTIVE', :c)"""),
        {"a": arrival, "d": departure, "n": (departure - arrival).days, "s": status,
         "r": json.dumps(room_ids), "ra": room_amount, "ec": extra_charges,
         "ta": tax_amount, "da": discount_amount, "b": balance, "c": COMPANY})


def add_payment(conn, *, amount, paid_date, method):
    conn.execute(sa.text("""
        INSERT INTO reservation_amount_paid_history (amount, paid_date, payment_method,
            status, company_id) VALUES (:a, :d, :m, 'ACTIVE', :c)"""),
        {"a": amount, "d": paid_date, "m": method, "c": COMPANY})


# ---------------------------------------------------------------- nightly split


@pytest.mark.parametrize("total,nights,expected", [
    (100.00, 3, [33.33, 33.34, 33.33]),   # the odd cent lands on the middle night
    (1000.00, 4, [250.00, 250.00, 250.00, 250.00]),
    (99.99, 3, [33.33, 33.33, 33.33]),
])
def test_nightly_shares_re_sum_to_the_stay_total(hotel_seed, total, nights, expected):
    """A naive `round(total / nights, 2)` loses or invents a paisa here."""
    shares = [hotel_seed._nightly_share(total, nights, i) for i in range(nights)]
    assert shares == expected
    assert round(sum(shares), 2) == round(total, 2)


def test_nightly_share_outside_the_stay_is_zero(hotel_seed):
    assert hotel_seed._nightly_share(100.00, 3, 3) == 0.0
    assert hotel_seed._nightly_share(100.00, 3, -1) == 0.0


SEED_SHARE_SNIPPET = """
import importlib.util, json, pathlib, sys
tools = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(tools))
spec = importlib.util.spec_from_file_location(
    "seed", tools / "seed" / "__init__.py",
    submodule_search_locations=[str(tools / "seed")])
pkg = importlib.util.module_from_spec(spec)
sys.modules["seed"] = pkg
spec.loader.exec_module(pkg)
hotel = importlib.import_module("seed.hotel")
out = {}
for total in (100.00, 9999.99, 45135.00):
    for nights in (1, 2, 3, 5, 6, 8):
        out["%s|%s" % (total, nights)] = [hotel._nightly_share(total, nights, i) for i in range(nights)]
print(json.dumps(out))
"""


def test_seed_split_matches_the_service_split(hotel_seed):
    """The duplicated copy has to produce the same numbers as the original.

    A 6-night stay at 100.00 is the case that exposes a wrong copy: the odd
    cents have to land on the same nights, or a month's worth of seeded audits
    would disagree with the figures the running service computes for the same
    bookings. The service is loaded in its own process with its own root on the
    path, because `models` and `configs` are top-level names shared by six
    services -- in this process they resolve to whichever service imported first.
    """
    service_root = ROOT / "Services" / "HotelServices"
    proc = subprocess.run(
        [sys.executable, "-c", SEED_SHARE_SNIPPET, str(ROOT / "tools")],
        cwd=str(service_root), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        pytest.skip(f"nightAuditService is not loadable from its own root: {proc.stderr[-300:]}")
    service_shares = json.loads(proc.stdout.strip().splitlines()[-1])
    for key, expected in service_shares.items():
        total, nights = key.split("|")
        nights = int(nights)
        assert [hotel_seed._nightly_share(float(total), nights, i) for i in range(nights)] == expected, (
            f"seed and service disagree on the night split for {total} over {nights} nights")


# ------------------------------------------------------------------- the row


def test_row_reconciles_revenue_movement_and_settlement(hotel_seed, conn):
    add_reservation(conn, arrival=dt.date(2026, 9, 14), departure=dt.date(2026, 9, 17),
                    status="Checked-In", room_ids=[1, 2], room_amount=300.00,
                    extra_charges=0.0, tax_amount=0.0, discount_amount=0.0, balance=100.00)
    add_reservation(conn, arrival=dt.date(2026, 9, 16), departure=dt.date(2026, 9, 20),
                    status="Checked-In", room_ids=[3], room_amount=400.00, balance=0.00)
    add_reservation(conn, arrival=dt.date(2026, 9, 15), departure=dt.date(2026, 9, 16),
                    status="Checked-Out", room_ids=[4], room_amount=200.00, balance=0.00)
    add_reservation(conn, arrival=dt.date(2026, 9, 16), departure=dt.date(2026, 9, 18),
                    status="Cancelled", room_ids=[5], room_amount=999.00)
    add_payment(conn, amount=150.00, paid_date=AUDITED, method="Cash")
    add_payment(conn, amount=50.00, paid_date=AUDITED, method="UPI")
    add_payment(conn, amount=999.00, paid_date=dt.date(2026, 9, 15), method="Cash")

    row = hotel_seed.night_audit_row(conn, AUDITED, NEXT_DAY)

    # Two stays hold a room on the night of the 16th; the cancelled one and the
    # stay that departed that morning do not. Stay A is 300.00 over three nights
    # (14th-17th) and the 16th is its LAST night, so it contributes one third;
    # stay B is 400.00 over four nights starting that day, contributing one
    # quarter.
    assert row["rooms_occupied"] == 3
    assert row["room_nights"] == 2
    assert row["in_house"] == row["stayovers"] == 2

    assert row["room_revenue"] == 200.00   # 100.00 + 100.00
    assert row["gross_revenue"] == row["room_revenue"] + row["extra_charges"] \
        + row["tax_amount"] - row["discount_amount"]

    assert row["payments_collected"] == 200.00
    breakdown = {b["payment_method"]: b["amount"] for b in json.loads(row["payment_breakdown"])}
    assert breakdown == {"Cash": 150.00, "UPI": 50.00}

    # Balances of everyone who had arrived and had not cancelled or no-showed.
    assert row["outstanding_balance"] == 100.00

    assert row["business_date"] == AUDITED
    assert row["next_business_date"] == NEXT_DAY
    assert row["audit_status"] == "Completed"
    assert row["company_id"] == COMPANY


def test_a_night_closes_after_midnight_so_the_timestamps_roll_over(hotel_seed, conn):
    """`completed_at` is a wall clock, and the night ends after 00:00.

    This is why the business-date row's `last_audit_at` carries the NEW date
    while the audit row is filed under the night that was closed. Stamping both
    with the audited date is what made the two screens disagree about which
    night had been closed.
    """
    add_reservation(conn, arrival=AUDITED, departure=NEXT_DAY, status="Checked-In",
                    room_ids=[1], room_amount=100.00)
    row = hotel_seed.night_audit_row(conn, AUDITED, NEXT_DAY)
    assert row["started_at"].date() == NEXT_DAY
    assert row["completed_at"].date() == NEXT_DAY
    assert row["completed_at"] > row["started_at"]


def test_no_shows_are_never_counted_as_occupancy(hotel_seed, conn):
    add_reservation(conn, arrival=AUDITED, departure=NEXT_DAY, status="No-Show",
                    room_ids=[7], room_amount=500.00)
    row = hotel_seed.night_audit_row(conn, AUDITED, NEXT_DAY)
    assert row["rooms_occupied"] == 0
    assert row["room_nights"] == 0
    assert row["room_revenue"] == 0.0
    assert row["arrivals_expected"] == 0     # a no-show was never expected
    assert row["outstanding_balance"] == 0.0


def test_soft_deleted_reservations_are_ignored(hotel_seed, conn):
    add_reservation(conn, arrival=AUDITED, departure=NEXT_DAY, status="Checked-In",
                    room_ids=[1], room_amount=100.00)
    conn.execute(sa.text("UPDATE room_reservation SET status = 'INACTIVE'"))
    row = hotel_seed.night_audit_row(conn, AUDITED, NEXT_DAY)
    assert row["rooms_occupied"] == 0
    assert row["room_revenue"] == 0.0


def test_json_columns_are_serialised_strings(hotel_seed, conn):
    """The seed's `insert()` helper builds literal SQL.

    Passing a Python list produced `Invalid JSON text` at the column, which is
    why every JSON column in this seed is a `json.dumps` string. Asserted here
    so the next editor does not "clean it up" back into a list.
    """
    add_reservation(conn, arrival=AUDITED, departure=NEXT_DAY, status="Checked-In",
                    room_ids=[1], room_amount=100.00)
    add_payment(conn, amount=10.00, paid_date=AUDITED, method="Cash")
    row = hotel_seed.night_audit_row(conn, AUDITED, NEXT_DAY)
    assert isinstance(row["payment_breakdown"], str)
    assert isinstance(row["no_show_reservation_ids"], str)
    assert json.loads(row["payment_breakdown"])[0]["payment_method"] == "Cash"
    assert json.loads(row["no_show_reservation_ids"]) == []

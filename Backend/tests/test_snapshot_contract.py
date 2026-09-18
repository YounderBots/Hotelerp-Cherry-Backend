"""The wire between Master Data and the Hotel service, from both ends at once.

    cd Backend/Services/MasterDataServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest \\
        ../../tests/test_snapshot_contract.py -v

WHY THIS SUITE EXISTS
    HotelServices no longer reads Master Data's tables; it reads
    `GET /snapshot` and writes `PATCH /room/{id}/state`, both served by
    `resources/snapshotController.py` here. Two services, one contract, and
    nothing in either process can see the other -- so the usual way this
    breaks is one side renaming a field and every reservation quietly
    pricing at zero.

    This suite serves the REAL endpoints (over SQLite, with a real token) and
    hands their JSON to the REAL Hotel client, loaded by path from the other
    service. If a field the Hotel side reads stops being sent, or the state
    write stops landing in the column the Hotel side expects, it fails here,
    in one process, before either service is deployed.

    Loading the client by path works because it depends only on `httpx` and a
    `BaseConfig` -- and every service ships a `configs.BaseConfig`. It never
    touches this service's models.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import time

import pytest
import sqlalchemy as sa
from jose import jwt
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

import main
from configs import BaseConfig
from models import get_db, models

HERE = pathlib.Path(__file__).resolve().parent
HOTEL_CLIENT = HERE.parents[0] / "Services" / "HotelServices" / "resources" / "master_client.py"

TENANT = "1"


def load_hotel_client():
    spec = importlib.util.spec_from_file_location("hotel_master_client", HOTEL_CLIENT)
    mod = importlib.util.module_from_spec(spec)
    # Registered before execution: its dataclasses resolve their (string)
    # annotations through sys.modules, as `from __future__ import annotations`
    # makes every annotation a string.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hotel():
    return load_hotel_client()


@pytest.fixture()
def db():
    engine = sa.create_engine("sqlite://", connect_args={"check_same_thread": False},
                              poolclass=StaticPool)
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    base = dict(status="ACTIVE", created_by="1", company_id=TENANT)
    session.add(models.Room_Type(id=7, Type_Name="Deluxe", Room_Cost=4500, Bed_Cost=800,
                                 Complementry="1", Daily_Rate=5000, Weekly_Rate=30000, **base))
    session.add(models.Room_Type(id=8, Type_Name="Old Suite", Room_Cost=1, Bed_Cost=1,
                                 Complementry="1", status="INACTIVE", created_by="1",
                                 company_id=TENANT))
    session.add(models.Room(id=1, Room_No="101", Room_Name="Room 101", Room_Type_ID="7",
                            Bed_Type_ID="1", Room_Telephone="101", Room_Image_1="", Room_Image_2="",
                            Room_Image_3="", Room_Image_4="", Max_Adult_Occupy="2",
                            Max_Child_Occupy="1", Room_Booking_status="Available",
                            Room_Working_status="Ready", Room_Status="UnBlocking", **base))
    session.add(models.Room(id=2, Room_No="201", Room_Name="Other property", Room_Type_ID="7",
                            Bed_Type_ID="1", Room_Telephone="", Room_Image_1="", Room_Image_2="",
                            Room_Image_3="", Room_Image_4="", Max_Adult_Occupy="2",
                            Max_Child_Occupy="1", Room_Booking_status="Available",
                            Room_Working_status="Ready", Room_Status="UnBlocking",
                            status="ACTIVE", created_by="1", company_id="2"))
    session.add(models.Tax_type(id=3, Country_ID="1", Tax_Name="GST 12", Tax_Percentage="12", **base))
    session.add(models.Discount_Data(id=4, Country_ID="1", Discount_Name="Corporate",
                                     Discount_Percentage="10", **base))
    session.add(models.Payment_Methods(id=2, payment_method="Cash", **base))
    session.add(models.Payment_Methods(id=9, payment_method="Cheque", status="INACTIVE",
                                       created_by="1", company_id=TENANT))
    session.add(models.Identity_Proofs(id=5, Proof_Name="Passport", **base))
    session.add(models.Reservation_Status(id=11, Reservation_Status="Confirmed", Color="#0a0", **base))
    session.add(models.Reservation_Status(id=12, Reservation_Status="Checked-In", Color="#00a", **base))
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def client(db):
    main.app.dependency_overrides[get_db] = lambda: db
    try:
        yield TestClient(main.app, raise_server_exceptions=False)
    finally:
        main.app.dependency_overrides.pop(get_db, None)


def token(company_id=TENANT):
    now = int(time.time())
    return jwt.encode(
        {"user_id": 1, "role_id": 1, "company_id": company_id, "iat": now, "exp": now + 600,
         "iss": BaseConfig.JWT_ISSUER},
        BaseConfig.SECRET_KEY, algorithm=BaseConfig.ALGORITHM,
    )


def auth(company_id=TENANT):
    return {"Authorization": f"Bearer {token(company_id)}"}


class ServedTransport:
    """The Hotel client's Transport, answered by this service's real routes."""

    def __init__(self, client, headers):
        self.client, self.headers = client, headers

    def get(self, service, path):
        assert service == "master"
        r = self.client.get(path, headers=self.headers)
        return None if r.status_code == 404 else r.json()

    def patch(self, service, path, body):
        assert service == "master"
        r = self.client.patch(path, json=body, headers=self.headers)
        return None if r.status_code == 404 else r.json()


# ---------------------------------------------------------------------------
# GET /snapshot
# ---------------------------------------------------------------------------
class TestSnapshot:
    def test_needs_a_token(self, client):
        assert client.get("/snapshot").status_code == 401

    def test_is_scoped_to_the_callers_company(self, client):
        data = client.get("/snapshot", headers=auth()).json()["data"]
        assert [r["room_no"] for r in data["rooms"]] == ["101"]
        data2 = client.get("/snapshot", headers=auth("2")).json()["data"]
        assert [r["room_no"] for r in data2["rooms"]] == ["201"]

    def test_carries_inactive_rows_with_their_status(self, client):
        """A retired payment method still labels the folios that used it."""
        data = client.get("/snapshot", headers=auth()).json()["data"]
        by_id = {p["id"]: p for p in data["payment_methods"]}
        assert by_id[9]["status"] == "INACTIVE" and by_id[2]["status"] == "ACTIVE"
        assert {t["id"]: t["status"] for t in data["room_types"]} == {7: "ACTIVE", 8: "INACTIVE"}

    def test_sends_every_field_the_hotel_client_reads(self, client, hotel):
        """The contract, field by field, from the receiving side's definitions.

        Each record class in the Hotel client declares what it reads. Every
        one of those names must be a key this endpoint sends, for every list,
        or the Hotel side silently gets None where a rate or a status was.
        """
        import dataclasses
        data = client.get("/snapshot", headers=auth()).json()["data"]
        expects = {
            "rooms": hotel.Room, "room_types": hotel.RoomType, "tax_types": hotel.TaxType,
            "discounts": hotel.Discount, "payment_methods": hotel.PaymentMethod,
            "identity_proofs": hotel.IdentityProof, "reservation_statuses": hotel.ReservationStatus,
        }
        for key, cls in expects.items():
            assert data[key], key
            wanted = {f.name for f in dataclasses.fields(cls)}
            for row in data[key]:
                missing = wanted - set(row)
                assert not missing, f"{key}: endpoint does not send {sorted(missing)}"


# ---------------------------------------------------------------------------
# The Hotel client, fed by these routes
# ---------------------------------------------------------------------------
class TestHotelClientOverTheRealRoutes:
    def test_reads_what_reservation_needs(self, client, hotel):
        md = hotel.MasterData(ServedTransport(client, auth()))
        assert md.rooms[1].room_no == "101"
        assert md.rooms[1].room_type_id == "7"                   # a string, as stored
        assert md.active_room_types()[7].daily_rate == 5000
        assert set(md.room_types) == {7, 8} and set(md.active_room_types()) == {7}
        assert md.tax_types[3].tax_percentage == "12"
        assert md.discounts[4].discount_percentage == "10"
        assert md.payment_methods[9].status == "INACTIVE"
        assert md.identity_proofs[5].proof_name == "Passport"
        assert [s.reservation_status for s in md.active_statuses()] == ["Confirmed", "Checked-In"]
        assert md.status_id("Checked-In") == 12
        assert md.status_by_id(11).color == "#0a0"

    def test_writes_room_state_into_the_columns_master_data_keeps(self, client, hotel, db):
        md = hotel.MasterData(ServedTransport(client, auth()))
        updated = md.set_room_state(1, booking_status="Occupied", working_status="Not Ready")

        assert (updated.booking_status, updated.working_status) == ("Occupied", "Not Ready")
        db.expire_all()
        row = db.query(models.Room).filter(models.Room.id == 1).one()
        assert row.Room_Booking_status == "Occupied"
        assert row.Room_Working_status == "Not Ready"
        assert row.Room_Status == "UnBlocking"                 # untouched: not sent
        assert row.updated_by == "1"

    def test_cannot_write_another_companys_room(self, client, hotel, db):
        md = hotel.MasterData(ServedTransport(client, auth()))
        assert md.set_room_state(2, booking_status="Occupied") is None   # 404 for this caller
        db.expire_all()
        assert db.query(models.Room).filter(models.Room.id == 2).one().Room_Booking_status == "Available"


# ---------------------------------------------------------------------------
# PATCH /room/{id}/state on its own
# ---------------------------------------------------------------------------
class TestRoomState:
    def test_refuses_an_empty_change(self, client):
        r = client.patch("/room/1/state", json={}, headers=auth())
        assert r.status_code == 400

    def test_refuses_a_blank_value(self, client):
        r = client.patch("/room/1/state", json={"room_status": "  "}, headers=auth())
        assert r.status_code == 400

    def test_writes_only_the_fields_sent(self, client, db):
        r = client.patch("/room/1/state", json={"room_status": "Blocking"}, headers=auth())
        assert r.status_code == 200
        assert r.json()["data"]["room_status"] == "Blocking"
        db.expire_all()
        row = db.query(models.Room).filter(models.Room.id == 1).one()
        assert (row.Room_Status, row.Room_Booking_status, row.Room_Working_status) == \
            ("Blocking", "Available", "Ready")

    def test_unknown_room_is_404(self, client):
        assert client.patch("/room/999/state", json={"room_status": "Blocking"},
                            headers=auth()).status_code == 404

    def test_the_rooms_own_editor_does_not_own_these_columns(self):
        """`PUT /room` is the whole-record form; it never sets occupancy or
        readiness, which is why this endpoint exists. Pinned so nobody
        'simplifies' the Hotel service back onto PUT."""
        import inspect
        from resources import masterController
        src = inspect.getsource(masterController.update_room)
        assert "Room_Booking_status" not in src and "Room_Working_status" not in src

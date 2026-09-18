"""The Hotel service's view of Master Data and Users, over HTTP.

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest \\
        ../../tests/test_master_client.py -v

WHY THIS SUITE EXISTS
    The reservation module used to read Master Data's tables directly, as
    SQLAlchemy mappings onto another schema on the same MySQL server, and the
    deployment at 168.231.103.18 answered 500 on every reservation screen for
    three days because its database account lacked one GRANT in a schema it
    does not own. Every such read now goes through `resources/master_client`
    and the wire, and this service's account never leaves its own schema.

    What is pinned here is the boundary itself:

      * what the client makes of the wire -- which rows count as selectable,
        which are kept only for labelling, what a write sends and what it
        skips;
      * what a sibling being down looks like from the browser (a 503 that
        names the service, never a 500) and from /readyz;
      * that the double-booking lock is taken on THIS schema's `room_lock`,
        and never again on anything of Master Data's.

    The wire shape itself is pinned from the other side, in
    MasterDataServices' test_snapshot_contract.py, which serves the real
    endpoints and feeds their JSON to this very client.
"""

from __future__ import annotations

import logging

import httpx
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fake_master import FakeMaster
from resources import master_client as mc
from resources import reservation_rules as rules
from resources.master_client import MasterData, MasterDataUnavailable
from resources.utils import server_error

RealClient = httpx.Client


def mock_http(monkeypatch, handler):
    """Every httpx.Client the module opens answers from `handler`."""
    monkeypatch.setattr(mc.httpx, "Client",
                        lambda **kw: RealClient(transport=httpx.MockTransport(handler), **kw))


@pytest.fixture()
def master():
    m = FakeMaster()
    m.add_room(id=1, room_no="101", room_type_id="7", working_status="Ready")
    m.add_room(id=2, room_no="102", room_type_id="7", status="INACTIVE")
    m.add_room_type(id=7, room_type_name="Deluxe", daily_rate=5000, room_cost=4500)
    m.add_room_type(id=8, room_type_name="Old Suite", status="INACTIVE")
    m.add_tax(id=3, tax_name="GST 12", tax_percentage="12")
    m.add_discount(id=4, discount_name="Corporate", discount_percentage="10")
    m.add_payment_method(id=2, payment_method="Cash")
    m.add_payment_method(id=9, payment_method="Cheque", status="INACTIVE")
    m.add_identity_proof(id=5, proof_name="Passport")
    m.add_status(id=11, reservation_status="Confirmed")
    m.add_status(id=12, reservation_status="Checked-In")
    m.add_status(id=13, reservation_status="Retired", status="INACTIVE")
    m.add_staff(id=42, first_name="Imran", last_name="Khan")
    m.add_staff(id=43, first_name="Gone", status="INACTIVE")
    return m


@pytest.fixture()
def md(master):
    return MasterData(master)


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------
class TestSnapshot:
    def test_one_round_trip_serves_every_lookup(self, md, master):
        """A booking touches seven tables; the wire is crossed once."""
        md.rooms, md.room_types, md.tax_types, md.discounts
        md.payment_methods, md.identity_proofs, md.statuses
        assert [c[:3] for c in master.calls] == [("GET", "master", "/snapshot")]

    def test_nothing_is_fetched_until_something_is_read(self, md, master):
        assert master.calls == []

    def test_records_speak_the_apis_names(self, md):
        room = md.rooms[1]
        assert (room.room_no, room.room_type_id, room.working_status) == ("101", "7", "Ready")
        assert md.room_types[7].daily_rate == 5000
        assert md.tax_types[3].tax_percentage == "12"          # free text, untouched

    def test_inactive_rows_are_kept_for_labelling_only(self, md):
        """A booking against a retired payment method still has to say which.

        The full maps carry every row; the active views carry what may be
        chosen today. Getting this backwards either blanks old folios or lets
        a clerk book a room that was deleted.
        """
        assert 9 in md.payment_methods and md.payment_methods[9].status == "INACTIVE"
        assert 2 in md.rooms and 2 not in md.active_rooms()
        assert set(md.active_rooms()) == {1}
        assert set(md.active_room_types()) == {7}
        assert [s.reservation_status for s in md.active_statuses()] == ["Confirmed", "Checked-In"]
        assert md.status_by_id(13) is None
        assert md.status_id("Retired") is None

    def test_status_lookups(self, md):
        assert md.status_by_id(12).reservation_status == "Checked-In"
        assert md.status_by_id("12").reservation_status == "Checked-In"
        assert md.status_by_id("x") is None
        assert md.status_id("Confirmed") == 11
        assert md.status_id("confirmed") is None    # exact spelling: the rules fold, this does not

    def test_a_snapshot_without_data_is_a_dependency_failure(self):
        """Reachable and answering, but not the Master Data this build knows:
        an older MasterDataServices, or another program on that port -- which
        is exactly what a default URL hits when a deployment moved the ports."""
        class Old:
            def get(self, service, path):
                return {"detail": "Not Found"}     # a MasterData build that predates /snapshot
            def patch(self, *a):                   # pragma: no cover
                raise AssertionError
            def base_url(self, service):
                return "http://127.0.0.1:8030"
        with pytest.raises(MasterDataUnavailable) as e:
            MasterData(Old()).rooms
        assert "http://127.0.0.1:8030/snapshot returned no data" in e.value.detail
        assert e.value.where() == " at http://127.0.0.1:8030 (MASTER_SERVICE_URL)"

    def test_a_transport_with_no_address_still_raises_a_usable_error(self):
        class Old:
            def get(self, service, path):
                return None
            def patch(self, *a):                   # pragma: no cover
                raise AssertionError
        with pytest.raises(MasterDataUnavailable) as e:
            MasterData(Old()).rooms
        assert e.value.where() == "" and "/snapshot" in e.value.detail


class TestStaff:
    def test_an_active_member_of_staff(self, md, master):
        assert md.staff(42).first_name == "Imran"
        md.staff(42)
        assert [c for c in master.calls if c[1] == "users"] == [("GET", "users", "/users/42", None)]

    def test_inactive_and_unknown_are_both_nobody(self, md):
        assert md.staff(43) is None
        assert md.staff(999) is None
        assert md.staff("not-a-number") is None


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------
class TestSetRoomState:
    def test_only_a_change_is_a_write(self, md, master):
        assert md.set_room_state(1, working_status="Ready") is md.rooms[1]
        assert master.writes() == []

    def test_only_the_changed_fields_are_sent(self, md, master):
        md.set_room_state(1, booking_status="Occupied", working_status="Ready", room_status=None)
        assert master.writes() == [(1, {"booking_status": "Occupied"})]

    def test_the_held_copy_follows_the_write(self, md, master):
        """A later read in the same request sees what was written."""
        md.set_room_state(1, booking_status="Occupied")
        assert md.rooms[1].booking_status == "Occupied"
        assert master.room(1)["booking_status"] == "Occupied"
        assert len(master.calls) == 2                       # one GET, one PATCH -- no refetch

    def test_a_room_master_data_no_longer_has_is_skipped(self, md, master):
        assert md.set_room_state(2, booking_status="Occupied") is None   # inactive there
        assert master.writes() == [(2, {"booking_status": "Occupied"})]

    def test_a_write_while_master_data_is_down_raises(self, md, master):
        md.rooms  # snapshot in hand
        master.down = True
        with pytest.raises(MasterDataUnavailable):
            md.set_room_state(1, booking_status="Occupied")


# ---------------------------------------------------------------------------
# The rules read through the client
# ---------------------------------------------------------------------------
class TestRulesThroughTheClient:
    def test_load_rooms_returns_only_active_rooms(self, md):
        assert set(rules.load_rooms(md, [1, 2, 3])) == {1}

    def test_a_retired_id_does_not_exist_for_this_property(self, md):
        with pytest.raises(rules.RuleError, match="Payment method 9 does not exist"):
            rules.resolve_payment_method(md, 9)
        assert rules.resolve_payment_method(md, 2).payment_method == "Cash"
        assert rules.resolve_tax_type(md, None) is None

    def test_the_vocabulary_is_the_active_statuses_in_order(self, md):
        assert rules.load_status_vocabulary(md) == ["Confirmed", "Checked-In"]
        assert rules.resolve_status(md, "CHECKED IN") == "Checked-In"

    def test_quote_needs_no_database_at_all(self, md):
        q = rules.quote(md, room_ids=[1], rate_types=["daily"], nights=2,
                        tax_type_id=3, discount_type_id=4)
        assert (q["room_amount"], q["tax_amount"], q["discount_amount"]) == (10000.0, 1200.0, 1000.0)


# ---------------------------------------------------------------------------
# The lock stays home
# ---------------------------------------------------------------------------
class TestLock:
    def test_locks_this_schemas_room_lock_rows_in_id_order(self):
        """The one thing that used to still need another schema."""
        class Bind:
            dialect = type("D", (), {"name": "mysql"})
        seen = []
        class DB:
            def get_bind(self):
                return Bind()
            def execute(self, clause, params=None):
                seen.append((str(clause), params))
        rules.lock_rooms(DB(), [3, 1, 3, 2])
        sql = "\n".join(s for s, _ in seen)
        assert "room_lock" in sql and "FOR UPDATE" in sql
        assert "masterdata" not in sql and "`room`" not in sql
        assert [p["rid"] for _, p in seen[:-1]] == [1, 2, 3]       # INSERT IGNORE, ordered
        assert seen[-1][1] == {"r0": 1, "r1": 2, "r2": 3}

    def test_sqlite_is_left_to_serialise_writers_itself(self):
        engine = sa.create_engine("sqlite://", connect_args={"check_same_thread": False},
                                  poolclass=StaticPool)
        db = sessionmaker(bind=engine)()
        rules.lock_rooms(db, [1, 2])          # no FOR UPDATE, no error
        db.close()

    def test_no_rooms_is_a_no_op(self):
        class DB:
            def get_bind(self):            # pragma: no cover
                raise AssertionError("must not touch the database")
        rules.lock_rooms(DB(), [])


# ---------------------------------------------------------------------------
# When the sibling is down: what the browser and the journal see
# ---------------------------------------------------------------------------
class TestUnavailable:
    def test_the_controllers_answer_503_naming_the_service_and_the_address(self, caplog):
        """The 503 says where this service looked and which .env key put it there.

        The address is a loopback URL and an environment variable's name --
        nothing anyone can use -- and the person reading the browser is the
        one who has to change it. Kept only in the log, it went unread for a
        day on a box whose stale main.py had no /readyz to say it either.
        """
        log = logging.getLogger("test.hotel")
        exc = MasterDataUnavailable("master", "http://127.0.0.1:8030/snapshot is unreachable",
                                    base_url="http://127.0.0.1:8030", env_var="MASTER_SERVICE_URL")
        with caplog.at_level("ERROR", logger="test.hotel"):
            err = server_error(log, exc, "list_reservations_failed")
        assert err.status_code == 503
        assert err.detail.startswith(
            "The Master Data service is unavailable at http://127.0.0.1:8030 (MASTER_SERVICE_URL)")
        assert ".env" in err.detail and "restart" in err.detail
        assert "127.0.0.1:8030/snapshot" in caplog.records[-1].getMessage()

    def test_a_refusal_with_no_address_still_names_the_service(self):
        err = server_error(logging.getLogger("test.hotel"),
                           MasterDataUnavailable("users", "no data"), "x_failed")
        assert err.status_code == 503
        assert err.detail.startswith("The Users service is unavailable, so")

    def test_an_ordinary_crash_is_still_a_plain_500(self):
        err = server_error(logging.getLogger("test.hotel"), KeyError("room"), "x_failed")
        assert (err.status_code, err.detail) == (500, "Internal server error")

    def test_the_transport_turns_connection_errors_into_unavailable(self, monkeypatch):
        def refuse(request):
            raise httpx.ConnectError("connection refused", request=request)
        mock_http(monkeypatch, refuse)
        t = mc.HttpTransport("tok", master_url="http://127.0.0.1:1", users_url="http://127.0.0.1:2")
        with pytest.raises(MasterDataUnavailable) as e:
            t.get("master", "/snapshot")
        assert "MASTER_SERVICE_URL" in e.value.detail and "ConnectError" in e.value.detail
        assert (e.value.base_url, e.value.env_var) == ("http://127.0.0.1:1", "MASTER_SERVICE_URL")
        assert e.value.where() == " at http://127.0.0.1:1 (MASTER_SERVICE_URL)"

    def test_a_rejected_token_is_a_deploy_fault_not_the_callers(self, monkeypatch):
        """Our caller was accepted here and refused there: the services are
        not verifying the same JWT. Say so, rather than 401ing the user."""
        def reject(request):
            return httpx.Response(401, json={"detail": "Invalid or expired token"})
        mock_http(monkeypatch, reject)
        t = mc.HttpTransport("tok", master_url="http://m", users_url="http://u")
        with pytest.raises(MasterDataUnavailable) as e:
            t.get("master", "/snapshot")
        assert "JWT_SECRET_KEY" in e.value.detail

    def test_the_transport_forwards_the_callers_token_and_reads_404_as_none(self, monkeypatch):
        seen = {}
        def answer(request):
            seen["auth"] = request.headers.get("authorization")
            seen["url"] = str(request.url)
            return httpx.Response(404, json={"detail": "User not found"})
        mock_http(monkeypatch, answer)
        t = mc.HttpTransport("tok-123", master_url="http://m/", users_url="http://u/")
        assert t.get("users", "/users/7") is None
        assert seen == {"auth": "Bearer tok-123", "url": "http://u/users/7"}


class TestReadiness:
    def _probe_with(self, monkeypatch, handler):
        mock_http(monkeypatch, handler)

    def test_reachable(self, monkeypatch):
        self._probe_with(monkeypatch, lambda r: httpx.Response(200, json={"status": "ok"}))
        ok, detail = mc.probe("Master Data", "http://127.0.0.1:8030", "MASTER_SERVICE_URL", "x")
        assert ok and "reachable" in detail

    def test_unreachable_names_the_url_and_the_env_key(self, monkeypatch):
        def refuse(request):
            raise httpx.ConnectError("refused", request=request)
        self._probe_with(monkeypatch, refuse)
        ok, detail = mc.probe("Master Data", "http://127.0.0.1:8030", "MASTER_SERVICE_URL",
                              "Every reservation screen answers 503 until it is.")
        assert not ok
        for needle in ("http://127.0.0.1:8030/healthz", "MASTER_SERVICE_URL", "503"):
            assert needle in detail

    def test_readyz_reports_both_siblings(self, monkeypatch):
        """The service's own probe, wired to the real checks."""
        import main
        from starlette.testclient import TestClient

        def refuse(request):
            raise httpx.ConnectError("refused", request=request)
        self._probe_with(monkeypatch, refuse)
        resp = TestClient(main.app, raise_server_exceptions=False).get("/readyz")
        assert resp.status_code == 503
        body = resp.json()
        assert body["degraded"] == ["masterdata", "users"]
        assert "MASTER_SERVICE_URL" in body["checks"]["masterdata"]["detail"]
        assert "USER_SERVICE_URL" in body["checks"]["users"]["detail"]

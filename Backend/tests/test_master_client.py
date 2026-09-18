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
            def put(self, *a):                     # pragma: no cover
                raise AssertionError
            def base_url(self, service):
                return "http://127.0.0.1:8000"
        with pytest.raises(MasterDataUnavailable) as e:
            MasterData(Old()).rooms
        assert "http://127.0.0.1:8000/masterdata/snapshot returned no data" in e.value.detail
        assert e.value.where() == " at http://127.0.0.1:8000 (API_GATEWAY_URL)"

    def test_a_transport_with_no_address_still_raises_a_usable_error(self):
        class Old:
            def get(self, service, path):
                return None
            def put(self, *a):                     # pragma: no cover
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
        assert len(master.calls) == 2                       # one GET, one PUT -- no refetch

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
        exc = MasterDataUnavailable("master", "http://127.0.0.1:8000/masterdata/snapshot is unreachable",
                                    base_url="http://127.0.0.1:8000", env_var="API_GATEWAY_URL")
        with caplog.at_level("ERROR", logger="test.hotel"):
            err = server_error(log, exc, "list_reservations_failed")
        assert err.status_code == 503
        assert err.detail.startswith(
            "The Master Data service is unavailable at http://127.0.0.1:8000 (API_GATEWAY_URL)")
        assert "127.0.0.1:8000/masterdata/snapshot" in caplog.records[-1].getMessage()

    def test_a_refusal_with_no_address_still_names_the_service(self):
        err = server_error(logging.getLogger("test.hotel"),
                           MasterDataUnavailable("users", "no data"), "x_failed")
        assert err.status_code == 503
        assert err.detail.startswith("The Users service is unavailable, so")

    def test_an_ordinary_crash_is_still_a_plain_500(self):
        err = server_error(logging.getLogger("test.hotel"), KeyError("room"), "x_failed")
        assert (err.status_code, err.detail) == (500, "Internal server error")

    def test_every_call_goes_to_the_gateway_under_its_proxy_prefix(self, monkeypatch):
        """The whole point: one address, the frontend's, and the gateway's
        permission map sees the call. `/snapshot` of Master Data is
        `GET {gateway}/masterdata/snapshot`; a staff lookup is
        `GET {gateway}/user/users/{id}`; the state write is a PUT."""
        seen = []
        def answer(request):
            seen.append((request.method, str(request.url), request.headers.get("authorization")))
            return httpx.Response(200, json={"status": "success", "data": {}})
        mock_http(monkeypatch, answer)
        t = mc.HttpTransport("tok-123", gateway_url="http://127.0.0.1:8000/")
        t.get("master", "/snapshot")
        t.get("users", "/users/7")
        t.put("master", "/room/7/state", {"booking_status": "Occupied"})
        assert seen == [
            ("GET", "http://127.0.0.1:8000/masterdata/snapshot", "Bearer tok-123"),
            ("GET", "http://127.0.0.1:8000/user/users/7", "Bearer tok-123"),
            ("PUT", "http://127.0.0.1:8000/masterdata/room/7/state", "Bearer tok-123"),
        ]

    def test_the_transport_turns_connection_errors_into_unavailable(self, monkeypatch):
        def refuse(request):
            raise httpx.ConnectError("connection refused", request=request)
        mock_http(monkeypatch, refuse)
        t = mc.HttpTransport("tok", gateway_url="http://127.0.0.1:1")
        with pytest.raises(MasterDataUnavailable) as e:
            t.get("master", "/snapshot")
        assert "API_GATEWAY_URL" in e.value.detail and "ConnectError" in e.value.detail
        assert (e.value.base_url, e.value.env_var) == ("http://127.0.0.1:1", "API_GATEWAY_URL")
        assert e.value.where() == " at http://127.0.0.1:1 (API_GATEWAY_URL)"

    def test_a_rejected_token_is_a_deploy_fault_not_the_callers(self, monkeypatch):
        """Our caller was accepted here and refused by the gateway: the two are
        not verifying the same JWT. Say so, rather than 401ing the user."""
        def reject(request):
            return httpx.Response(401, json={"detail": "Invalid or expired token"})
        mock_http(monkeypatch, reject)
        t = mc.HttpTransport("tok", gateway_url="http://g")
        with pytest.raises(MasterDataUnavailable) as e:
            t.get("master", "/snapshot")
        assert "JWT_SECRET_KEY" in e.value.detail

    def test_a_gateway_permission_denial_says_to_regenerate_the_map(self, monkeypatch):
        """403 from the gateway is its permission map, not the token: a gateway
        on a build without the service-to-service rows, or a map not
        regenerated since. Named as such, with the gateway's own reason."""
        def deny(request):
            return httpx.Response(403, json={"detail": "no permission mapping for GET /masterdata/snapshot"})
        mock_http(monkeypatch, deny)
        t = mc.HttpTransport("tok", gateway_url="http://g")
        with pytest.raises(MasterDataUnavailable) as e:
            t.get("master", "/snapshot")
        assert "permission map" in e.value.detail and "build_rbac_map" in e.value.detail
        assert "no permission mapping" in e.value.detail
        assert "JWT" not in e.value.detail

    def test_a_gateway_that_cannot_reach_master_data_is_named_as_such(self, monkeypatch):
        def bad_gateway(request):
            return httpx.Response(502, json={"detail": "Upstream unavailable"})
        mock_http(monkeypatch, bad_gateway)
        t = mc.HttpTransport("tok", gateway_url="http://g")
        with pytest.raises(MasterDataUnavailable) as e:
            t.get("master", "/snapshot")
        assert "could not reach the masterdata service" in e.value.detail
        assert "*_SERVICE_URL" in e.value.detail

    def test_404_reads_as_none(self, monkeypatch):
        mock_http(monkeypatch, lambda r: httpx.Response(404, json={"detail": "User not found"}))
        t = mc.HttpTransport("tok-123", gateway_url="http://g/")
        assert t.get("users", "/users/7") is None


class TestReadiness:
    def _probe_with(self, monkeypatch, handler):
        mock_http(monkeypatch, handler)

    def test_reachable(self, monkeypatch):
        seen = []
        def ok_(request):
            seen.append(str(request.url))
            return httpx.Response(200, json={"status": "ok"})
        self._probe_with(monkeypatch, ok_)
        ok, detail = mc.probe("http://127.0.0.1:8000")
        assert ok and "reachable" in detail and "through it" in detail
        assert seen == ["http://127.0.0.1:8000/healthz"]        # no token needed, none sent

    def test_unreachable_names_the_url_and_the_env_key(self, monkeypatch):
        def refuse(request):
            raise httpx.ConnectError("refused", request=request)
        self._probe_with(monkeypatch, refuse)
        ok, detail = mc.probe("http://127.0.0.1:8000")
        assert not ok
        for needle in ("http://127.0.0.1:8000/healthz", "API_GATEWAY_URL", "503", "frontend"):
            assert needle in detail

    def test_readyz_reports_the_gateway(self, monkeypatch):
        """The service's own probe, wired to the real check: one dependency,
        the gateway, because everything else is behind it."""
        import main
        from starlette.testclient import TestClient

        def refuse(request):
            raise httpx.ConnectError("refused", request=request)
        self._probe_with(monkeypatch, refuse)
        resp = TestClient(main.app, raise_server_exceptions=False).get("/readyz")
        assert resp.status_code == 503
        body = resp.json()
        assert body["degraded"] == ["gateway"]
        assert "API_GATEWAY_URL" in body["checks"]["gateway"]["detail"]

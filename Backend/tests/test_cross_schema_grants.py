"""The cross-schema privileges HotelServices cannot work without.

    cd Backend/Services/HotelServices
    ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest \
        ../../tests/test_cross_schema_grants.py -v

WHY THIS SUITE EXISTS
    The deployment at 168.231.103.18 answered 500 on every reservation screen
    for one reason:

        (1142, "SELECT command denied to user 'cherryhotel'@'localhost'
                for table 'room'")

    HotelServices reads the Master Data schema on its own connection so that
    an availability check and the booking that depends on it commit in one
    transaction. That makes the Hotel service's MySQL account need privileges
    in a schema it does not own -- a deployment step nothing provisioned and
    nothing verified.

    Two things about that failure are easy to get wrong twice, and both are
    pinned here because both cost a day the first time:

    THE ACCOUNT.  `'cherryhotel'@'localhost'` is not `'cherryhotel'@'%'`.
        Granting to the second CREATES A NEW, EMPTY ACCOUNT, answers
        "Query OK", and changes nothing about the 500. The fix has to be aimed
        at the account MySQL matched the connection to -- what CURRENT_USER()
        returns -- never at the username in the DSN with a guessed host.

    THE PRIVILEGE.  The error names SELECT, so SELECT is what gets granted.
        But the reservation lifecycle writes the room's occupancy and
        housekeeping flags back, and `lock_rooms()` takes
        `SELECT ... FOR UPDATE`, which MySQL refuses without UPDATE as well as
        SELECT. Grant SELECT alone and the reservation list comes back while
        every attempt to actually book still fails -- the same bug, one screen
        further in, after everyone has agreed it is fixed.

    No MySQL is needed here. The privilege *decisions* are what regress; the
    grants themselves are proven against a real server by
    `grant_cross_schema.py --verify` on the deployment.
"""

from __future__ import annotations

import importlib.util
import logging
import pathlib

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.masterdata import (
    MASTERDATA_SCHEMA,
    USERS_SCHEMA,
    MasterBase,
    StaffUser,
    denied_account,
    grants,
    privilege_refusal,
    probe,
    probe_users,
)

TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"

DENIED_SELECT = (1142, "SELECT command denied to user 'cherryhotel'@'localhost' "
                       "for table 'room'")
DENIED_UPDATE = (1142, "UPDATE command denied to user 'cherryhotel'@'localhost' "
                       "for table 'room'")
# Database-level refusal (1044) is worded differently from the table-level one.
DENIED_DB = (1044, "Access denied for user 'cherryhotel'@'localhost' to database "
                   "'hotelerp_masterdata'")

ACCOUNT = "'cherryhotel'@'localhost'"
GRANT_READ = f"GRANT SELECT ON `{MASTERDATA_SCHEMA}`.* TO {ACCOUNT};"
GRANT_WRITE = f"GRANT UPDATE ON `{MASTERDATA_SCHEMA}`.`room` TO {ACCOUNT};"
GRANT_USERS = f"GRANT SELECT ON `{USERS_SCHEMA}`.`users` TO {ACCOUNT};"


def load_tool():
    """Import grant_cross_schema.py by path -- it is a script, not a module."""
    spec = importlib.util.spec_from_file_location(
        "grant_cross_schema_under_test", TOOLS / "grant_cross_schema.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tool():
    return load_tool()


# ---------------------------------------------------------------------------
# A session stand-in. The probe calls exactly three things, so a fake states
# the failure mode under test precisely -- which a real MySQL cannot be made
# to do in CI, and a real SQLite has no privileges to withhold.
# ---------------------------------------------------------------------------
class FakeDB:
    def __init__(self, dialect="mysql", read_error=None, explain_error=None,
                 users_error=None):
        self.dialect = dialect
        self.read_error = read_error
        self.explain_error = explain_error
        self.users_error = users_error
        self.executed = []

    def get_bind(self):
        return type("Bind", (), {"dialect": type("D", (), {"name": self.dialect})})

    def query(self, column):
        # The two probes read one column each; answer for the schema whose
        # mapping it belongs to, by class rather than by name.
        owner = getattr(getattr(column, "parent", None), "class_", None)
        err = self.users_error if owner is StaffUser else self.read_error
        db = self

        class Q:
            def limit(self, _n):
                return self

            def all(self):
                if err:
                    raise sa.exc.OperationalError("SELECT ...", {}, Exception(err))
                db.executed.append("read")
                return []

        return Q()

    def execute(self, clause):
        self.executed.append(str(clause))
        if self.explain_error:
            raise sa.exc.OperationalError("EXPLAIN ...", {},
                                          Exception(self.explain_error))
        return []


# ---------------------------------------------------------------------------
# The probe: what /readyz and the boot log are allowed to call healthy
# ---------------------------------------------------------------------------
class TestProbe:
    def test_read_denied_is_not_ready(self):
        ok, detail = probe(FakeDB(read_error=DENIED_SELECT))
        assert ok is False
        assert MASTERDATA_SCHEMA in detail
        assert "grant_cross_schema" in detail

    def test_write_denied_is_not_ready_either(self):
        """The regression this suite exists for.

        A deployment granted SELECT and nothing else reads rooms perfectly and
        cannot take a booking. Reporting it ready is how that reaches a guest
        at a front desk rather than an operator at a terminal.
        """
        ok, detail = probe(FakeDB(explain_error=DENIED_UPDATE))
        assert ok is False
        assert "cannot write" in detail
        assert "UPDATE" in detail

    def test_both_present_is_ready(self):
        db = FakeDB()
        ok, detail = probe(db)
        assert ok is True
        assert "writable" in detail
        assert any("EXPLAIN" in e for e in db.executed)

    def test_non_mysql_skips_the_privilege_check(self):
        """SQLite under test ATTACHes the schema and has no privileges at all.

        The check must be skipped rather than failed, or every suite that
        builds the cross-schema mapping in SQLite starts reporting a broken
        deployment.
        """
        db = FakeDB(dialect="sqlite")
        ok, _ = probe(db)
        assert ok is True
        assert not any("EXPLAIN" in e for e in db.executed)

    def test_inconclusive_write_check_does_not_fail_readiness(self):
        """An EXPLAIN that fails for a reason other than privileges.

        An ancient MySQL cannot EXPLAIN an UPDATE. The read works, which is
        what serving needs; taking the whole service out of rotation over a
        check that could not answer would be worse than the gap it covers.
        """
        ok, detail = probe(FakeDB(explain_error=(1064, "You have an error in "
                                                       "your SQL syntax")))
        assert ok is True
        assert "inconclusive" in detail

    def test_users_schema_is_its_own_check(self):
        """It fails separately and breaks less, so it is reported separately."""
        ok, detail = probe_users(FakeDB(users_error=DENIED_SELECT))
        assert ok is False
        assert USERS_SCHEMA in detail
        assert "housekeeping" in detail.lower()

    def test_read_denied_states_the_exact_grant(self):
        """The log line is the runbook.

        Whoever reads "1142 ... denied ... for table 'room'" in the journal
        should not then have to find a tool, a README and the right account:
        the statements are on the line, aimed at the account MySQL named --
        host included, so nobody grants to 'cherryhotel'@'%' by guesswork.
        """
        _, detail = probe(FakeDB(read_error=DENIED_SELECT))
        assert GRANT_READ in detail
        assert "@'%'" not in detail

    def test_read_denied_prescribes_the_update_as_well(self):
        """The write probe never ran, so prescribe both or set the trap again.

        Grant only what this failure names -- SELECT -- and the list works
        while every booking fails on the UPDATE nobody was told about.
        """
        _, detail = probe(FakeDB(read_error=DENIED_SELECT))
        assert GRANT_WRITE in detail
        assert GRANT_USERS not in detail       # its own probe, its own line

    def test_write_denied_prescribes_the_update(self):
        _, detail = probe(FakeDB(explain_error=DENIED_UPDATE))
        assert GRANT_WRITE in detail
        assert GRANT_READ not in detail        # SELECT is proven present

    def test_users_denied_prescribes_the_users_grant(self):
        _, detail = probe_users(FakeDB(users_error=DENIED_SELECT))
        assert GRANT_USERS in detail
        assert GRANT_READ not in detail

    def test_a_database_level_refusal_is_read_the_same_way(self):
        """1044 says "denied for user"; 1142 says "denied to user"."""
        _, detail = probe(FakeDB(read_error=DENIED_DB))
        assert GRANT_READ in detail

    def test_a_failure_that_names_no_account_falls_back_to_the_tool(self):
        """No account, nothing exact to say; the tool asks MySQL for it."""
        _, detail = probe(FakeDB(read_error=(2003, "Can't connect to MySQL "
                                                   "server on '127.0.0.1'")))
        assert "GRANT " not in detail
        assert "grant_cross_schema" in detail

    def test_probe_runs_against_a_real_session(self):
        """The fake above states the failures; this proves the shape is right.

        A probe that works on a stand-in and raises AttributeError against an
        actual Session would take down /readyz for the one deployment that is
        healthy.
        """
        engine = sa.create_engine("sqlite://",
                                  connect_args={"check_same_thread": False},
                                  poolclass=StaticPool)
        with engine.connect() as conn:
            conn.exec_driver_sql(f"ATTACH DATABASE ':memory:' AS {MASTERDATA_SCHEMA}")
            conn.exec_driver_sql(f"ATTACH DATABASE ':memory:' AS {USERS_SCHEMA}")
            conn.commit()
        MasterBase.metadata.create_all(bind=engine)
        session = sessionmaker(bind=engine)()
        try:
            assert probe(session)[0] is True
            assert probe_users(session)[0] is True
        finally:
            session.close()


# ---------------------------------------------------------------------------
# The request that fails: what the journal and the browser say about it
# ---------------------------------------------------------------------------
def _refused(err):
    return sa.exc.OperationalError("SELECT ...", {}, Exception(err))


class TestPrivilegeRefusal:
    def test_names_the_account_mysql_matched(self):
        assert denied_account(str(DENIED_SELECT)) == ACCOUNT
        assert denied_account(str(DENIED_DB)) == ACCOUNT
        assert denied_account("Lost connection to MySQL server") is None

    def test_a_refused_request_prescribes_all_three_grants(self):
        """The request only ever names the first privilege it was refused.

        Fix that one alone and the next screen fails on the next one. So the
        remedy for ANY refusal is the whole set, aimed at the account in the
        message -- GRANT is idempotent, and three lines cost nothing.
        """
        fix = privilege_refusal(_refused(DENIED_SELECT))
        assert fix is not None
        for stmt in (GRANT_READ, GRANT_WRITE, GRANT_USERS):
            assert stmt in fix
        assert "RESTART" in fix

    def test_anything_else_is_not_a_privilege_problem(self):
        assert privilege_refusal(KeyError("room")) is None
        assert privilege_refusal(_refused((2003, "Can't connect"))) is None

    def test_the_500_handler_says_the_fix_and_answers_503(self, caplog):
        """The two places the operator actually looks.

        The browser banner said "Internal server error" and the journal ended
        in forty lines of pymysql. Now the banner names the class of failure
        and the last line of the journal before the access log IS the GRANT.
        503 rather than 500: the code is fine and a dependency is not, which
        is what /readyz reports for the same state.
        """
        import main
        from starlette.testclient import TestClient

        @main.app.get("/__test_refused")
        def refused():
            raise _refused(DENIED_SELECT)

        client = TestClient(main.app, raise_server_exceptions=False)
        with caplog.at_level("CRITICAL", logger="hotelservice"):
            resp = client.get("/__test_refused")

        assert resp.status_code == 503
        assert "MySQL privilege is missing" in resp.json()["detail"]
        critical = [r for r in caplog.records if r.levelname == "CRITICAL"]
        assert len(critical) == 1
        assert GRANT_READ in critical[0].getMessage()
        assert "'cherryhotel'@'localhost'" in critical[0].getMessage()

    def test_the_controllers_own_catch_says_the_same(self, caplog):
        """The path the real request takes -- and the one a handler misses.

        Every controller wraps its body in `except Exception` and raises its
        own HTTPException(500), so the app-level handler above never sees the
        MySQL error on a real request: `GET /room_reservation` went through
        `list_reservations_failed` and came out as "Internal server error"
        with the fix nowhere. The shared helper is what the controllers call.
        """
        from resources.utils import PRIVILEGE_MISSING, server_error
        log = logging.getLogger("test.controller")

        with caplog.at_level("CRITICAL", logger="test.controller"):
            err = server_error(log, _refused(DENIED_SELECT), "list_reservations_failed")
        assert err.status_code == 503
        assert err.detail == PRIVILEGE_MISSING
        assert "'cherryhotel'@'localhost'" not in err.detail   # the log's, not the browser's
        critical = [r for r in caplog.records if r.levelname == "CRITICAL"]
        assert len(critical) == 1 and GRANT_WRITE in critical[0].getMessage()

        err = server_error(log, KeyError("room"), "list_reservations_failed")
        assert (err.status_code, err.detail) == (500, "Internal server error")

    def test_an_ordinary_crash_is_still_a_plain_500(self):
        import main
        from starlette.testclient import TestClient

        @main.app.get("/__test_crash")
        def crash():
            raise KeyError("room")

        resp = TestClient(main.app, raise_server_exceptions=False).get("/__test_crash")
        assert resp.status_code == 500
        assert resp.json() == {"detail": "Internal server error"}


# ---------------------------------------------------------------------------
# The tool: what it would run on the server
# ---------------------------------------------------------------------------
class TestSchemaDerivation:
    def test_derives_both_siblings_from_the_hotel_schema(self, tool):
        assert tool.derive_schemas("hotelerp_hotel") == {
            "masterdata": "hotelerp_masterdata",
            "users": "hotelerp_users",
        }

    def test_honours_a_non_default_prefix(self, tool):
        """A second property on the same server is `cherry_hotel`, not ours."""
        assert tool.derive_schemas("cherry_hotel")["masterdata"] == "cherry_masterdata"

    def test_overrides_win(self, tool):
        got = tool.derive_schemas("hotelerp_hotel", md_override="md_custom")
        assert got["masterdata"] == "md_custom"

    def test_matches_what_the_service_itself_resolved(self, tool):
        """The tool must grant on the schema the service will actually query.

        These two derivations live in different files -- the service's in
        models/masterdata.py, the tool's here -- and a tool that grants on
        `hotelerp_masterdata` while the service reads `cherry_masterdata`
        reports success and fixes nothing.
        """
        own = str(MASTERDATA_SCHEMA)
        hotel = own[: -len("_masterdata")] + "_hotel"
        assert tool.derive_schemas(hotel)["masterdata"] == own


class TestDsnParsing:
    def test_percent_encoded_password(self, tool):
        """make_prod_env.py encodes credentials: a '@' otherwise truncates it."""
        got = tool.parse_dsn(
            "mysql+pymysql://cherryhotel:p%40ss%2Fword@127.0.0.1:3306/hotelerp_hotel")
        assert got["user"] == "cherryhotel"
        assert got["password"] == "p@ss/word"
        assert got["db"] == "hotelerp_hotel"

    def test_default_port_and_charset_suffix(self, tool):
        got = tool.parse_dsn(
            "mysql+pymysql://u:p@db.internal/hotelerp_hotel?charset=utf8mb4")
        assert got["port"] == 3306
        assert got["db"] == "hotelerp_hotel"

    def test_rejects_a_non_mysql_dsn(self, tool):
        with pytest.raises(ValueError):
            tool.parse_dsn("postgresql://u:p@h/db")


class TestAccountTargeting:
    def test_grants_name_the_account_it_was_given(self, tool):
        """Not the DSN's username with a guessed host.

        'cherryhotel'@'%' is a DIFFERENT account from 'cherryhotel'@'localhost'.
        Granting to the wrong one silently creates it and leaves the 500 in
        place, which is exactly what the old advice in diag_masterdata.py told
        an operator to do.
        """
        schemas = {"masterdata": "hotelerp_masterdata", "users": "hotelerp_users"}
        account = tool.quote_account("cherryhotel", "localhost")
        assert account == "'cherryhotel'@'localhost'"
        for need in tool.NEEDS:
            assert need.grant(schemas, account).endswith(
                "TO 'cherryhotel'@'localhost';")
            assert "@'%'" not in need.grant(schemas, account)

    def test_refuses_an_account_it_cannot_safely_quote(self, tool):
        with pytest.raises(SystemExit):
            tool.quote_account("bad'name", "localhost")


class TestWhatItGrants:
    def test_the_update_on_room_is_in_the_set(self, tool):
        """The half that is forgotten, because the log only names SELECT.

        Without it the reservation list works and no booking does: the
        lifecycle writes room state back, and a locking read needs UPDATE on
        top of SELECT.
        """
        updates = [n for n in tool.NEEDS if n.privs == ("UPDATE",)]
        assert len(updates) == 1
        assert updates[0].table == "room"
        assert updates[0].schema_key == "masterdata"

    def test_it_grants_nothing_beyond_what_is_read_and_written(self, tool):
        """Least privilege, on schemas two other services own."""
        granted = {p for n in tool.NEEDS for p in n.privs}
        assert granted == {"SELECT", "UPDATE"}
        users = [n for n in tool.NEEDS if n.schema_key == "users"]
        assert [n.table for n in users] == ["users"]   # that one table, not .*

    def test_the_service_and_the_tool_prescribe_the_same_grants(self, tool):
        """One set, two authors: the boot log / 500 handler and the tool.

        If a future cross-schema read is added to one and not the other, the
        journal prescribes a fix that leaves the tool reporting MISSING, or
        the other way round -- and the operator, having done what the log
        said, is told it was not enough.
        """
        schemas = {"masterdata": MASTERDATA_SCHEMA, "users": USERS_SCHEMA}
        assert grants("'u'@'h'") == [n.grant(schemas, "'u'@'h'") for n in tool.NEEDS]

    def test_the_write_probe_touches_no_row(self, tool):
        """It must stay safe to run against production, unattended."""
        sql = [n.probe_sql({"masterdata": "md", "users": "us"})
               for n in tool.NEEDS if n.privs == ("UPDATE",)][0]
        assert sql.startswith("EXPLAIN ")
        assert "`id` = 0" in sql


class TestReporting:
    def _results(self, tool, errors):
        """errors: privilege error text per need, or None when it succeeds."""
        return [(need, err is None, err or "")
                for need, err in zip(tool.NEEDS, errors)]

    def test_only_the_missing_privileges_are_granted(self, tool, capsys):
        """A deployment half-fixed by hand must not be re-granted wholesale."""
        schemas = {"masterdata": "hotelerp_masterdata", "users": "hotelerp_users"}
        results = self._results(tool, [None, "UPDATE command denied to user", None])
        assert tool.report(results, schemas) is False
        assert tool.statements_for(results, schemas, "'u'@'h'") == [
            "GRANT UPDATE ON `hotelerp_masterdata`.`room` TO 'u'@'h';"]
        out = capsys.readouterr().out
        assert "HAVE" in out and "MISSING" in out

    def test_a_missing_schema_is_not_answered_with_a_grant(self, tool, capsys):
        """"Not there" and "not allowed" are different problems.

        A database-level GRANT on a database that does not exist *succeeds* in
        MySQL, so prescribing one for a split deploy reports "applied" and
        fixes nothing. Only MySQL can tell the two apart, and the answer is in
        the error text.
        """
        schemas = {"masterdata": "md", "users": "us"}
        results = self._results(tool, [None, None, "Unknown database 'us'"])
        assert tool.report(results, schemas) is False
        assert tool.statements_for(results, schemas, "'u'@'h'") == []
        assert tool.absent_targets(results, schemas) == ["`us`.`users`"]
        assert "ABSENT" in capsys.readouterr().out

    def test_an_unanswerable_check_is_not_answered_with_a_grant(self, tool, capsys):
        """Neither refused nor absent -- so neither verdict is claimed."""
        schemas = {"masterdata": "md", "users": "us"}
        results = self._results(tool, [None, None, "Lost connection to MySQL server"])
        assert tool.report(results, schemas) is False
        assert tool.statements_for(results, schemas, "'u'@'h'") == []
        assert tool.absent_targets(results, schemas) == []
        assert [n.schema_key for n in tool.unresolved(results)] == ["users"]
        assert "UNKNOWN" in capsys.readouterr().out

    def test_invisibility_is_not_absence(self, tool):
        """The bug the end-to-end reproduction caught.

        `SHOW DATABASES` and information_schema.SCHEMATA list only the schemas
        an account holds SOME privilege on. The account this tool exists to fix
        holds none on `hotelerp_masterdata`, so it cannot see the schema at all
        -- and an earlier version read that invisibility as "the schema is on a
        different MySQL server", printed FATAL, and exited before it ever
        reached the privilege check. The correct diagnosis was one line further
        down.

        So: a refusal must be classified as a missing privilege on its own
        evidence, never cross-checked against what the account can see.
        """
        denied = "SELECT command denied to user 'cherryhotel'@'localhost'"
        assert tool.classify(False, denied) == "missing"
        assert tool.classify(False, "Unknown database 'hotelerp_masterdata'") == "absent"

    def test_a_healthy_deployment_reports_clean(self, tool):
        results = self._results(tool, [None, None, None])
        assert tool.report(results, {"masterdata": "md", "users": "us"}) is True


# ---------------------------------------------------------------------------
# Who applies the grants
# ---------------------------------------------------------------------------
class _Args:
    def __init__(self, admin_user=None, admin_password=None):
        self.admin_user = admin_user
        self.admin_password = admin_password


PROD_SVC = {"user": "cherryhotel", "password": "svc-pw"}
DEV_SVC = {"user": "root", "password": "root-pw"}


class TestAdminCredentials:
    """The default that turned `--confirm` into a guaranteed failure.

    The service's account is the one MISSING the privileges, so it is the one
    account that cannot grant them. Defaulting the admin to that account was
    right only in dev, where the DSN is root's anyway -- and the README told
    the production operator to run exactly the invocation that could not work.
    """

    def _prompt(self, calls):
        def prompt(msg):
            calls.append(msg)
            return "typed"
        return prompt

    def test_on_a_server_it_defaults_to_root_and_asks(self, tool):
        calls = []
        user, pw = tool.admin_credentials(_Args(), PROD_SVC, prompt=self._prompt(calls),
                                          env={}, interactive=True)
        assert (user, pw) == ("root", "typed")
        assert calls == ["MySQL password for root: "]

    def test_in_dev_the_dsn_is_already_root_so_nothing_is_asked(self, tool):
        calls = []
        user, pw = tool.admin_credentials(_Args(), DEV_SVC, prompt=self._prompt(calls),
                                          env={}, interactive=True)
        assert (user, pw) == ("root", "root-pw")
        assert calls == []

    def test_mysql_pwd_is_honoured_so_a_deploy_script_can_set_it_once(self, tool):
        calls = []
        user, pw = tool.admin_credentials(_Args(), PROD_SVC, prompt=self._prompt(calls),
                                          env={"MYSQL_PWD": "from-env"}, interactive=False)
        assert (user, pw) == ("root", "from-env")
        assert calls == []

    def test_dash_always_prompts_even_in_dev(self, tool):
        calls = []
        _, pw = tool.admin_credentials(_Args(admin_password="-"), DEV_SVC,
                                       prompt=self._prompt(calls), env={}, interactive=True)
        assert pw == "typed" and calls

    def test_an_explicit_password_is_used_as_given(self, tool):
        user, pw = tool.admin_credentials(_Args("dba", "s3cret"), PROD_SVC,
                                          prompt=None, env={}, interactive=False)
        assert (user, pw) == ("dba", "s3cret")

    def test_naming_the_service_user_as_admin_reuses_its_password(self, tool):
        """Someone whose service account really can grant, as in some dev setups."""
        user, pw = tool.admin_credentials(_Args("cherryhotel"), PROD_SVC,
                                          prompt=None, env={}, interactive=False)
        assert (user, pw) == ("cherryhotel", "svc-pw")

    def test_no_terminal_and_no_password_refuses_rather_than_hangs(self, tool):
        with pytest.raises(SystemExit) as e:
            tool.admin_credentials(_Args(), PROD_SVC, prompt=None, env={},
                                   interactive=False)
        assert "MYSQL_PWD" in str(e.value)

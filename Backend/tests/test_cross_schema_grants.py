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
    probe,
    probe_users,
)

TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"

DENIED_SELECT = (1142, "SELECT command denied to user 'cherryhotel'@'localhost' "
                       "for table 'room'")
DENIED_UPDATE = (1142, "UPDATE command denied to user 'cherryhotel'@'localhost' "
                       "for table 'room'")


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

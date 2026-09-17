#!/usr/bin/env python3
"""Grant HotelServices the cross-schema privileges it cannot work without.

    python Backend/tools/grant_cross_schema.py                 # report only
    python Backend/tools/grant_cross_schema.py --confirm       # apply them
    python Backend/tools/grant_cross_schema.py --print-sql     # hand to a DBA

WHY THIS EXISTS
    A booking has to check that a room is free and insert the reservation that
    fills it in ONE transaction, or two clerks sell the same room on the same
    night. The room lives in the Master Data schema and the reservation lives
    in the Hotel schema, so HotelServices reads Master Data on its own
    connection (models/masterdata.py) rather than over HTTP -- an HTTP read
    cannot hold the row lock that makes the check mean anything.

    The price is a deployment coupling that nothing provisioned: the Hotel
    service's MySQL account needs privileges in schemas it does not own. Miss
    it and the service still starts, /healthz used to still answer "ok", and
    every reservation screen answers 500:

        (1142, "SELECT command denied to user 'cherryhotel'@'localhost'
                for table 'room'")

    That is this tool's entire job, and it is the last hand-typed step of a
    deploy.

WHAT IT GRANTS, AND WHY EACH ONE
    SELECT on <prefix>_masterdata.*
        rooms, rate cards, tax, discounts, payment methods, identity proofs
        and the reservation-status vocabulary. Without it the reservation
        list, the reservation detail and the availability check all 500.

    UPDATE on <prefix>_masterdata.room
        NOT optional, and the half that gets forgotten -- because the error in
        the log only ever names SELECT.

          * the reservation lifecycle writes the room's own occupancy and
            housekeeping flags back (Room_Booking_status, Room_Working_status,
            Room_Status);
          * lock_rooms() takes SELECT ... FOR UPDATE on those rows, and MySQL
            requires SELECT *plus* one of UPDATE/DELETE/LOCK TABLES for a
            locking read.

        Grant SELECT alone and the reservation list comes back to life while
        every attempt to actually book still fails -- the same bug, one screen
        further in.

    SELECT on <prefix>_users.users
        housekeeping checks that a task's assignee is a real member of staff.

    Nothing else. No INSERT, no DELETE, no privilege on any other table in
    either schema: MasterDataServices and UserServices own their own data.

HOW IT FINDS THE ACCOUNT TO GRANT TO
    By asking MySQL, not by guessing. It connects with the DSN the service
    itself uses and reads SELECT CURRENT_USER(), which returns the account
    MySQL actually matched the connection to -- cherryhotel@localhost, not
    cherryhotel@%. The difference matters more than it looks: granting to
    'cherryhotel'@'%' when the live account is 'cherryhotel'@'localhost'
    CREATES A SECOND, EMPTY ACCOUNT, reports "Query OK", and changes nothing
    about the failure.
"""

from __future__ import annotations

import argparse
import getpass
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import pymysql
except ImportError:                                            # pragma: no cover
    print("ERROR: pymysql is not installed. "
          "pip install -r Backend/requirements.txt", file=sys.stderr)
    raise SystemExit(2)

REPO = Path(__file__).resolve().parents[2]
HOTEL_ENV = REPO / "Backend" / "Services" / "HotelServices" / ".env"

# MySQL account parts we are willing to interpolate into a GRANT. Anything
# outside this is refused rather than escaped: a username that needs quoting is
# a strong sign the DSN was parsed wrong, and building DDL out of it blind is
# how a tool that fixes privileges becomes a tool that grants them to the wrong
# account.
SAFE_ACCOUNT_PART = re.compile(r"^[A-Za-z0-9_.@%\-]{1,255}$")

# MySQL refused on privileges. The schema is reachable and named correctly --
# a GRANT is the fix.
DENIED = re.compile(r"command denied|access denied", re.I)

# MySQL says the thing is not there. A GRANT cannot fix that, and prescribing
# one wastes the operator's next hour.
ABSENT = re.compile(r"unknown database|unknown table|doesn't exist", re.I)


# ---------------------------------------------------------------------------
# What HotelServices needs. One table, so a future cross-schema read is added
# here once and picked up by the report, the SQL and the verification alike.
# ---------------------------------------------------------------------------
def _read(schema, table):
    return "SELECT 1 FROM `{}`.`{}` LIMIT 1".format(schema, table or "room")


def _can_update(schema, table):
    # EXPLAIN performs the privilege check and nothing else: MySQL requires the
    # same privileges to EXPLAIN a statement as to execute it, and no row is
    # touched. `id = 0` matches nothing even if one were.
    return ("EXPLAIN UPDATE `{}`.`{}` SET `Room_Booking_status` = "
            "`Room_Booking_status` WHERE `id` = 0".format(schema, table))


class Need:
    def __init__(self, privs, schema_key, table, why, probe_sql):
        self.privs = privs              # ("SELECT",)
        self.schema_key = schema_key    # "masterdata" | "users"
        self.table = table              # None means the whole schema
        self.why = why
        self._probe_sql = probe_sql     # (schema, table) -> SQL proving the priv

    def target(self, schemas) -> str:
        schema = schemas[self.schema_key]
        if self.table:
            return "`{}`.`{}`".format(schema, self.table)
        return "`{}`.*".format(schema)

    def grant(self, schemas, account) -> str:
        return "GRANT {} ON {} TO {};".format(
            ", ".join(self.privs), self.target(schemas), account)

    def probe_sql(self, schemas) -> str:
        return self._probe_sql(schemas[self.schema_key], self.table)


NEEDS = [
    Need(("SELECT",), "masterdata", None,
         "the reservation list, detail and availability check read rooms, rate "
         "cards, tax, discounts, payment methods, proofs and statuses",
         _read),
    Need(("UPDATE",), "masterdata", "room",
         "the reservation lifecycle writes the room's occupancy and "
         "housekeeping flags back, and a locking read (SELECT ... FOR UPDATE) "
         "needs UPDATE on top of SELECT",
         _can_update),
    Need(("SELECT",), "users", "users",
         "housekeeping checks that a task's assignee is a real member of staff",
         _read),
]


# ---------------------------------------------------------------------------
# DSN
# ---------------------------------------------------------------------------
def parse_dsn(uri: str) -> dict:
    """`mysql+pymysql://user:pw@host:3306/db?charset=utf8` -> its parts.

    Credentials are percent-encoded by make_prod_env.py (a '@' in a password
    otherwise truncates the DSN), so they are decoded back here.
    """
    m = re.match(
        r"^mysql(?:\+\w+)?://(?P<user>[^:/@]*)(?::(?P<pw>[^@]*))?@"
        r"(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<db>[^?]+)",
        uri.strip())
    if not m:
        raise ValueError("not a MySQL DSN: {!r}...".format(uri[:40]))
    return {
        "user": unquote(m.group("user")),
        "password": unquote(m.group("pw") or ""),
        "host": m.group("host"),
        "port": int(m.group("port") or 3306),
        "db": m.group("db").strip(),
    }


def dsn_from_env_file(path: Path) -> str:
    if not path.exists():
        raise SystemExit(
            "ERROR: {} not found.\n"
            "Run this on the server, from the repository root, with the Hotel\n"
            "service's own .env in place -- or pass --service-uri.".format(path))
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("DB_URI="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ERROR: no DB_URI in {}".format(path))


def derive_schemas(hotel_db: str, md_override=None, users_override=None) -> dict:
    """The derivation the service itself performs (models/masterdata.py).

    Both must resolve to the schema the service will actually query, or this
    tool grants privileges on a database nothing reads.
    """
    prefix = hotel_db[: -len("_hotel")] if hotel_db.endswith("_hotel") else None
    md = md_override or os.getenv("MASTERDATA_DB_SCHEMA") or (
        prefix + "_masterdata" if prefix else "hotelerp_masterdata")
    us = users_override or os.getenv("USERS_DB_SCHEMA") or (
        prefix + "_users" if prefix else "hotelerp_users")
    return {"masterdata": md.strip(), "users": us.strip()}


def connect(host, port, user, password, db=None, timeout=10):
    return pymysql.connect(host=host, port=port, user=user, password=password,
                           database=db, connect_timeout=timeout,
                           autocommit=True, charset="utf8mb4")


def quote_account(user: str, host: str) -> str:
    for part in (user, host):
        if not SAFE_ACCOUNT_PART.match(part):
            raise SystemExit(
                "ERROR: refusing to build a GRANT for account part {!r}. "
                "Grant it by hand, or check the DSN was read correctly."
                .format(part))
    return "'{}'@'{}'".format(user, host)


# ---------------------------------------------------------------------------
# Capability probing -- ask the database what this account can do rather than
# parsing SHOW GRANTS. Privileges arrive through accounts, roles, wildcards and
# *.*; only the answer to "does this statement run" is the truth.
# ---------------------------------------------------------------------------
def probe(conn, schemas):
    out = []
    for need in NEEDS:
        sql = need.probe_sql(schemas)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.fetchall()
            out.append((need, True, ""))
        except Exception as exc:                               # noqa: BLE001
            out.append((need, False, str(exc.args[-1] if exc.args else exc)[:180]))
    return out


def classify(ok: bool, err: str) -> str:
    """What kind of failure this is -- which decides what to do about it.

    Only `missing` is answered with a GRANT. The distinction is the whole
    diagnosis: "denied" and "not there" look identical from the application
    (both are a 500 on the reservation list) and have nothing in common as
    fixes.
    """
    if ok:
        return "have"
    if DENIED.search(err):
        return "missing"
    if ABSENT.search(err):
        return "absent"
    return "unknown"


def report(results, schemas) -> bool:
    all_ok = True
    for need, ok, err in results:
        label = "{:<6} on {}".format(", ".join(need.privs), need.target(schemas))
        verdict = classify(ok, err)
        if verdict == "have":
            print("  HAVE     " + label)
            continue
        all_ok = False
        if verdict == "missing":
            print("  MISSING  " + label)
            print("           " + need.why)
        elif verdict == "absent":
            print("  ABSENT   " + label)
            print("           " + err)
        else:
            # A dead connection, a MySQL too old to EXPLAIN an UPDATE. Say
            # which, rather than prescribing a GRANT that will not help.
            print("  UNKNOWN  " + label)
            print("           " + err)
    return all_ok


def statements_for(results, schemas, account) -> list:
    """The GRANTs to run -- for privileges MySQL actually refused, and no others.

    A check that failed for another reason is reported, not answered with SQL.
    Handing an operator a statement that cannot work sends them looking in the
    wrong place a second time, and this class of bug is already one wrong lead
    too long.
    """
    return [need.grant(schemas, account)
            for need, ok, err in results if classify(ok, err) == "missing"]


def absent_targets(results, schemas) -> list:
    """What MySQL says is not there at all. No grant fixes this."""
    return [need.target(schemas)
            for need, ok, err in results if classify(ok, err) == "absent"]


def unresolved(results) -> list:
    """Checks that could not be answered either way."""
    return [need for need, ok, err in results if classify(ok, err) == "unknown"]


def main() -> int:
    p = argparse.ArgumentParser(
        description="Grant HotelServices the cross-schema privileges it needs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Report-only unless --confirm is passed. Nothing is ever "
               "written to an application table.")
    p.add_argument("--service-uri",
                   help="Hotel service DSN. Default: DB_URI from "
                        "Backend/Services/HotelServices/.env")
    p.add_argument("--admin-user",
                   help="MySQL account that may GRANT (e.g. root). Default: "
                        "the service's own user, which is right in dev and "
                        "wrong in production.")
    p.add_argument("--admin-password",
                   help="Use '-' to be prompted rather than leaving it in "
                        "shell history.")
    p.add_argument("--masterdata-schema", help="Override the derived name")
    p.add_argument("--users-schema", help="Override the derived name")
    p.add_argument("--confirm", action="store_true",
                   help="Actually run the GRANT statements")
    p.add_argument("--print-sql", action="store_true",
                   help="Print the SQL and exit -- for a DBA who will not hand "
                        "over an administrative account")
    p.add_argument("--verify", action="store_true",
                   help="Only check; exit 1 if anything is missing")
    args = p.parse_args()

    uri = args.service_uri or dsn_from_env_file(HOTEL_ENV)
    try:
        svc = parse_dsn(uri)
    except ValueError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 2
    schemas = derive_schemas(svc["db"], args.masterdata_schema, args.users_schema)

    print("server            : {}:{}".format(svc["host"], svc["port"]))
    print("hotel schema      : {}  (as {})".format(svc["db"], svc["user"]))
    print("masterdata schema : {}".format(schemas["masterdata"]))
    print("users schema      : {}".format(schemas["users"]))
    print()

    # 1. Connect as the service. This is the only way to learn which account
    #    MySQL matched -- and the whole reason the old advice ('...'@'%') was
    #    wrong on this deployment.
    try:
        svc_conn = connect(svc["host"], svc["port"], svc["user"],
                           svc["password"], svc["db"])
    except Exception as exc:                                   # noqa: BLE001
        print("ERROR: cannot connect as the service user: {}"
              .format(str(exc)[:200]), file=sys.stderr)
        print("That DSN is what the service itself uses; if it cannot connect, "
              "privileges are not the problem yet.", file=sys.stderr)
        return 2

    with svc_conn.cursor() as cur:
        cur.execute("SELECT CURRENT_USER()")
        current = cur.fetchone()[0]
        cur.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA")
        present = {r[0] for r in cur.fetchall()}

    user, _, host = current.rpartition("@")
    account = quote_account(user, host)
    print("MySQL matched this connection to {}".format(account))
    print("  (this, not the username in the DSN, is the account to grant to)")
    print()

    # 2. Note what this account can SEE -- but never gate on it.
    #
    # `SHOW DATABASES` and information_schema.SCHEMATA list only the schemas an
    # account already holds some privilege on. An account that is missing
    # exactly the privileges this tool grants therefore cannot see the schemas
    # at all -- which is the state this tool exists for. Reading invisibility
    # as "the schema is not on this server" inverts the diagnosis and sends an
    # operator hunting a second MySQL server that does not exist. Let the
    # probes below answer it instead: MySQL distinguishes "command denied"
    # from "unknown database", and those two are the whole question.
    invisible = [s for s in schemas.values() if s not in present]
    if invisible:
        print("not listed by SHOW DATABASES for this account: {}"
              .format(invisible))
        print("  Expected while the privileges are missing -- an account sees "
              "only what it")
        print("  holds a privilege on. Not evidence either way; the checks "
              "below decide.")
        print()

    # 3. What can it do today?
    print("=== what the Hotel service can do today ===")
    results = probe(svc_conn, schemas)
    have_all = report(results, schemas)
    print()

    statements = statements_for(results, schemas, account)
    absent = absent_targets(results, schemas)
    stuck = unresolved(results)

    if absent:
        # Now it can be said, because MySQL said it: not "invisible to this
        # account" but "not there". That is the split-deploy or wrong-name
        # case, and no GRANT touches it.
        print("FATAL: MySQL reports {} does not exist.".format(", ".join(absent)))
        print("  Either these schemas live on a different MySQL server or they")
        print("  are named differently. Both are fatal and neither is a")
        print("  privilege problem: a booking joins the hotel and masterdata")
        print("  schemas inside ONE transaction, so they must share a server.")
        print("  If the name is the issue, set MASTERDATA_DB_SCHEMA /")
        print("  USERS_DB_SCHEMA in the Hotel service's .env.")
        cand = sorted(s for s in present if "master" in s.lower())
        if cand:
            print("  Candidates visible on this server: {}".format(cand))
        return 1

    if stuck:
        print("Some checks could not be answered, and no GRANT is prescribed "
              "for them:")
        for need in stuck:
            print("  " + need.target(schemas))
        print()

    if args.print_sql:
        if not statements:
            print("-- no privilege was refused, so there is nothing to grant.")
            return 0 if have_all else 1
        print("-- Run as an account that may GRANT, on {}:".format(svc["host"]))
        for s in statements:
            print(s)
        print("-- No FLUSH PRIVILEGES needed: GRANT takes effect immediately.")
        print("-- Then restart HotelServices (see --confirm's closing note).")
        return 0

    if have_all:
        print("Nothing to do: HotelServices holds every cross-schema privilege "
              "it needs.")
        return 0

    if not statements:
        # Only unresolved checks. Granting is not the answer and guessing at
        # one would be worse than saying so.
        print("Nothing here is a privilege problem. Fix the checks above "
              "first, then re-run.")
        return 1

    if args.verify:
        print("VERIFY FAILED: the privileges above are missing. Re-run with "
              "--confirm to grant them.")
        return 1

    print("=== the grants that fix it ===")
    for s in statements:
        print("  " + s)
    print()

    if not args.confirm:
        print("DRY RUN -- nothing changed. Re-run with --confirm to apply, or")
        print("--print-sql to hand the statements to a DBA.")
        return 1

    # 4. Apply, as an account that may grant.
    admin_user = args.admin_user or svc["user"]
    if args.admin_password == "-":
        admin_pw = getpass.getpass("MySQL password for {}: ".format(admin_user))
    elif args.admin_password is not None:
        admin_pw = args.admin_password
    elif admin_user == svc["user"]:
        admin_pw = svc["password"]
    else:
        admin_pw = getpass.getpass("MySQL password for {}: ".format(admin_user))

    try:
        admin = connect(svc["host"], svc["port"], admin_user, admin_pw)
    except Exception as exc:                                   # noqa: BLE001
        print("ERROR: cannot connect as {!r}: {}"
              .format(admin_user, str(exc)[:200]), file=sys.stderr)
        return 2

    # The admin account can see every schema, so this is the one connection
    # that can answer what the service's own could not. Worth asking before
    # granting: a database-level GRANT on a database that does not exist
    # succeeds in MySQL, so without this the tool would report "applied",
    # re-check, fail, and blame the account.
    with admin.cursor() as cur:
        cur.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA")
        everything = {r[0] for r in cur.fetchall()}
    really_missing = [s for s in schemas.values() if s not in everything]
    if really_missing:
        print("FATAL: {} not on this server, confirmed as {}."
              .format(really_missing, admin_user), file=sys.stderr)
        print("  A GRANT would succeed and change nothing. These schemas must "
              "live on the", file=sys.stderr)
        print("  same MySQL server as the Hotel schema -- a booking joins them "
              "in one", file=sys.stderr)
        print("  transaction. Restore them here, or set MASTERDATA_DB_SCHEMA / "
              "USERS_DB_SCHEMA", file=sys.stderr)
        print("  if they are simply named differently.", file=sys.stderr)
        return 1

    print("applying as {}:".format(admin_user))
    for s in statements:
        try:
            with admin.cursor() as cur:
                cur.execute(s.rstrip(";"))
            print("  OK    " + s)
        except Exception as exc:                               # noqa: BLE001
            print("  FAIL  " + s, file=sys.stderr)
            print("        " + str(exc)[:200], file=sys.stderr)
            if "denied" in str(exc).lower():
                print("        {!r} may not grant this. Use an administrative "
                      "account: --admin-user root --admin-password -"
                      .format(admin_user), file=sys.stderr)
            return 1
    print()

    # 5. Prove it, on a fresh connection.
    print("=== re-checking ===")
    fresh = connect(svc["host"], svc["port"], svc["user"], svc["password"],
                    svc["db"])
    if not report(probe(fresh, schemas), schemas):
        print()
        print("Still missing something. The grants ran, so the account above is "
              "probably not the one the service connects as.")
        return 1

    print()
    print("Done. HotelServices can now read Master Data and keep room state in "
          "step.")
    print()
    print("RESTART THE SERVICE -- this is not optional and not superstition.")
    print("  MySQL applies a database-level privilege change at a connection's")
    print("  next USE, and the service holds a SQLAlchemy pool of connections")
    print("  opened before the grant. This tool verified on a NEW connection,")
    print("  so it reports success while the running process keeps answering")
    print("  500 until its pool turns over.")
    print()
    print("    sudo systemctl restart hotelerp-hotel   # whatever it is named")
    print("    curl -s localhost:8040/readyz           # expect \"ready\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

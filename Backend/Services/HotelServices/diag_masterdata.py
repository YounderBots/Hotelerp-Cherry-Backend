"""Why can't HotelServices read the Master Data schema?

Run ON THE SERVER from Backend/Services/HotelServices, with that service's own
.env in place. Works on any build -- it only uses configs + SQLAlchemy, so it
does not require the deployment-probe commit.

    cd Backend/Services/HotelServices && python diag_masterdata.py

This explains. `Backend/tools/grant_cross_schema.py` fixes: same diagnosis,
plus `--confirm` to apply the grants and re-verify them.
"""
import os
import re
import sys

from sqlalchemy import create_engine, text

sys.path.insert(0, ".")
from configs import Configuration  # noqa: E402

uri = str(Configuration.DB_URI)
own = uri.rsplit("/", 1)[-1].split("?", 1)[0]
# Same order the service itself resolves in (models/masterdata.py:_resolve_schema),
# so this reports on the schema the app will actually query.
override = (os.getenv("MASTERDATA_DB_SCHEMA") or "").strip()
if override:
    guess = override
elif own.endswith("_hotel"):
    guess = own[:-len("_hotel")] + "_masterdata"
else:
    guess = "hotelerp_masterdata"
if override:
    print("MASTERDATA_DB_SCHEMA is set -> overriding the derived name")

users_override = (os.getenv("USERS_DB_SCHEMA") or "").strip()
if users_override:
    users_guess = users_override
elif own.endswith("_hotel"):
    users_guess = own[:-len("_hotel")] + "_users"
else:
    users_guess = "hotelerp_users"

print("hotel schema      :", own)
print("masterdata expected:", guess)
print("users expected    :", users_guess)
print("server            :", re.sub(r"//[^@]*@", "//<user>:<pw>@", uri).rsplit("/", 1)[0])
print()

eng = create_engine(uri)
with eng.connect() as c:
    # The account MySQL matched this connection to -- NOT the username in the
    # DSN. They differ in the part that decides whether a GRANT does anything:
    # 'cherryhotel'@'localhost' is a different account from 'cherryhotel'@'%',
    # and granting to the wrong one reports "Query OK" and fixes nothing.
    account = c.execute(text("SELECT CURRENT_USER()")).scalar()
    print("this connection is MySQL account:", account)
    print("  (grant to exactly this -- not to the username with a different host)")
    print()

    have = {r[0] for r in c.execute(text("SHOW DATABASES"))}
    print("schemas this user can see:")
    for s in sorted(have):
        print("   ", s)
    if guess not in have:
        # NOT a verdict, and this used to be one -- which inverted the whole
        # diagnosis in the only case that matters. SHOW DATABASES lists the
        # schemas an account holds SOME privilege on, so an account missing
        # exactly the privileges this script is looking for cannot see the
        # schema either. Exiting here with "it is not on this server" sends an
        # operator hunting a second MySQL server that does not exist, past the
        # one-line grant that was the actual fix.
        print()
        print(f"({guess!r} is not in that list -- expected while the privileges")
        print(" are missing, since an account sees only what it can touch.")
        print(" MySQL answers the real question below.)")
    print()

    user, _, host = str(account).rpartition("@")
    acct_sql = f"'{user}'@'{host}'"
    missing = []

    def absent(reason: str) -> bool:
        """MySQL saying "not there", which no GRANT fixes."""
        return any(s in reason.lower()
                   for s in ("unknown database", "unknown table", "doesn't exist"))

    try:
        n = c.execute(text(f"SELECT COUNT(*) FROM `{guess}`.`room`")).scalar()
        print(f"read {guess}.room: OK ({n} rows)")
    except Exception as exc:
        reason = str(getattr(exc, "orig", exc))[:200]
        if absent(reason):
            # Only MySQL can tell this apart from a privilege refusal, and the
            # distinction is the entire diagnosis.
            print(f"VERDICT: {guess!r} does not exist on this server.")
            print("  ", reason)
            print("  -> Either the Master Data DB lives on a different MySQL")
            print("     server, or the schema has another name. Both are fatal,")
            print("     and neither is fixed by a grant: the booking path joins")
            print("     hotel and masterdata in ONE transaction, so they must")
            print("     share a server.")
            # Rank a schema sharing this service's own prefix first: on a shared
            # MySQL box "master" matches other products' databases too.
            prefix = own[:-len("_hotel")] if own.endswith("_hotel") else ""
            cand = sorted(
                (s for s in have if "master" in s.lower()),
                key=lambda s: (not (prefix and s.startswith(prefix)), s),
            )
            if cand:
                print(f"  -> Candidates visible here: {cand}")
                print(f"     If one is right, set MASTERDATA_DB_SCHEMA={cand[0]} "
                      "in this service's .env")
            raise SystemExit(1)
        print("cannot READ the Master Data schema.")
        print("  ", reason)
        missing.append(f"GRANT SELECT ON `{guess}`.* TO {acct_sql};")
        n = None

    # The half that gets missed, because the error in the log only ever names
    # SELECT. The reservation lifecycle writes the room's own occupancy and
    # housekeeping flags back, and lock_rooms() takes SELECT ... FOR UPDATE --
    # which MySQL refuses without UPDATE as well as SELECT. Grant SELECT alone
    # and the list works while no booking does.
    #
    # EXPLAIN runs the privilege check and touches nothing.
    try:
        c.execute(text(
            f"EXPLAIN UPDATE `{guess}`.`room` "
            "SET `Room_Booking_status` = `Room_Booking_status` WHERE `id` = 0"))
        print(f"write {guess}.room: OK")
    except Exception as exc:
        reason = str(getattr(exc, "orig", exc))[:200]
        if "denied" in reason.lower():
            print("cannot WRITE room state (bookings would still fail).")
            print("  ", reason)
            missing.append(f"GRANT UPDATE ON `{guess}`.`room` TO {acct_sql};")
        else:
            print("write check inconclusive:", reason)

    try:
        c.execute(text(f"SELECT 1 FROM `{users_guess}`.`users` LIMIT 1"))
        print(f"read {users_guess}.users: OK")
    except Exception as exc:
        reason = str(getattr(exc, "orig", exc))[:200]
        print("cannot read the Users schema (housekeeping assignment would 500).")
        print("  ", reason)
        if absent(reason):
            print(f"  -> {users_guess!r} is not here at all; a grant will not")
            print("     help. Set USERS_DB_SCHEMA if it is named differently.")
        else:
            missing.append(
                f"GRANT SELECT ON `{users_guess}`.`users` TO {acct_sql};")

print()
if missing:
    print("VERDICT: privileges are missing. Run as an account that may GRANT:")
    for s in missing:
        print("   ", s)
    print()
    print("  No FLUSH PRIVILEGES needed -- GRANT takes effect immediately.")
    print("  Then RESTART this service: MySQL applies a database-level grant at")
    print("  a connection's next USE, and the pool holds connections opened")
    print("  before it, so the running process keeps 500ing until it reconnects.")
    print()
    print("  Or let the tool do all of it:")
    print("     python Backend/tools/grant_cross_schema.py --confirm")
    raise SystemExit(1)

print(f"VERDICT: OK -- Master Data is readable and room state is writable.")

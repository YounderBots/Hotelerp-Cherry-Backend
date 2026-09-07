"""Why can't HotelServices read the Master Data schema?

Run ON THE SERVER from Backend/Services/HotelServices, with that service's own
.env in place. Works on any build -- it only uses configs + SQLAlchemy, so it
does not require the deployment-probe commit.

    cd Backend/Services/HotelServices && python diag_masterdata.py
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

print("hotel schema      :", own)
print("masterdata expected:", guess)
print("server            :", re.sub(r"//[^@]*@", "//<user>:<pw>@", uri).rsplit("/", 1)[0])
print()

eng = create_engine(uri)
with eng.connect() as c:
    have = {r[0] for r in c.execute(text("SHOW DATABASES"))}
    print("schemas this user can see:")
    for s in sorted(have):
        print("   ", s)
    print()

    if guess not in have:
        print(f"VERDICT: {guess!r} is NOT on this server (or this user cannot see it).")
        print("  -> Either the Master Data DB lives on a different MySQL server,")
        print("     or the schema has another name. Both are fatal: the booking")
        print("     path joins hotel and masterdata in ONE transaction, so they")
        print("     must share a server and this user needs SELECT on both.")
        # Rank a schema sharing this service's own prefix first: on a shared
        # MySQL box "master" matches other products' databases too.
        prefix = own[:-len("_hotel")] if own.endswith("_hotel") else ""
        cand = sorted(
            (s for s in have if "master" in s.lower()),
            key=lambda s: (not (prefix and s.startswith(prefix)), s),
        )
        if cand:
            print(f"  -> Candidates on this server: {cand}")
            print(f"     If one is right, set MASTERDATA_DB_SCHEMA={cand[0]} in this service's .env")
        raise SystemExit(1)

    try:
        n = c.execute(text(f"SELECT COUNT(*) FROM `{guess}`.`room`")).scalar()
    except Exception as exc:
        print("VERDICT: schema is visible but NOT readable.")
        print("  ", str(getattr(exc, "orig", exc))[:200])
        print(f"  -> GRANT SELECT ON `{guess}`.* TO '<hotel service db user>'@'%';")
        print("     FLUSH PRIVILEGES;")
        raise SystemExit(1)

print(f"VERDICT: OK -- read {n} rows from {guess}.room. Master Data is reachable.")

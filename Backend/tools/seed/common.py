"""Shared machinery for the seed: connections, truncation, inserts, dates.

EVERY TABLE IS EMPTIED EXCEPT `alembic_version`.
    That one row records which migration the schema is at. Truncating it would
    make Alembic believe the database is unmigrated and try to replay every
    revision against tables that already exist. The data goes; the schema
    version stays.
"""

from __future__ import annotations

import datetime as dt
import os
import random
import sys

import sqlalchemy as sa

COMPANY = "1"
ACTIVE = "ACTIVE"
SYSTEM = "1"          # created_by: the seed acts as user 1

# Everything the dataset describes is anchored to this date, so the story stays
# coherent however long after generation it is loaded: stays that should be
# finished are behind it, in-house guests span it, arrivals land on it.
TODAY = dt.date.today()

# Deterministic: the same run produces the same dataset, which makes the data
# reviewable and any difference between two runs a real change.
RNG = random.Random(20260901)

SCHEMAS = [
    "hotelerp_users",
    "hotelerp_masterdata",
    "hotelerp_hotel",
    "hotelerp_restaurant",
    "hotelerp_bar",
]

SERVICE_DIRS = {
    "hotelerp_users": "UserServices",
    "hotelerp_masterdata": "MasterDataServices",
    "hotelerp_hotel": "HotelServices",
    "hotelerp_restaurant": "RestaurantServices",
    "hotelerp_bar": "BarServices",
}

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SERVICES = os.path.join(ROOT, "Backend", "Services")


def base_uri() -> str:
    """Server URI, read from HotelServices' own .env — no credentials in code."""
    env = os.path.join(SERVICES, "HotelServices", ".env")
    uri = None
    with open(env, encoding="utf-8") as fh:
        for line in fh:
            if line.strip().startswith("DB_URI="):
                uri = line.split("=", 1)[1].strip()
                break
    if not uri:
        raise SystemExit("DB_URI not found in HotelServices/.env")
    return uri.rsplit("/", 1)[0]


def engine_for(schema: str):
    return sa.create_engine(f"{base_uri()}/{schema}", future=True)


def upload_dir(schema: str, *parts: str) -> str:
    """An absolute path inside a service's static upload tree."""
    return os.path.join(SERVICES, SERVICE_DIRS[schema], "templates", "static", *parts)


# ---------------------------------------------------------------------------
# Emptying
# ---------------------------------------------------------------------------

def wipe(conn, schema: str, keep=("alembic_version",)) -> list[str]:
    """TRUNCATE every table in `schema` except `keep`, ignoring FK order.

    TRUNCATE rather than DELETE so AUTO_INCREMENT restarts at 1 -- a freshly
    seeded database whose first reservation is id 43 looks used, and every id
    in this dataset is referenced by another table, so they have to be
    predictable.
    """
    insp = sa.inspect(conn.engine)
    tables = [t for t in insp.get_table_names() if t not in keep]
    conn.execute(sa.text("SET FOREIGN_KEY_CHECKS = 0"))
    for t in tables:
        conn.execute(sa.text(f"TRUNCATE TABLE `{t}`"))
    conn.execute(sa.text("SET FOREIGN_KEY_CHECKS = 1"))
    return tables


# ---------------------------------------------------------------------------
# Inserting
# ---------------------------------------------------------------------------

def insert(conn, table: str, rows: list[dict]) -> None:
    """Insert `rows` into `table`. Every row must share the same keys.

    The column names are checked against the live table BEFORE the insert, so a
    seed written against a remembered schema fails with the full list of what
    is wrong -- every unknown column, and every NOT NULL one left unset -- in a
    single message. Letting MySQL find them means one round trip per mistake.
    """
    if not rows:
        return
    cols = list(rows[0].keys())
    for r in rows:
        if list(r.keys()) != cols:
            raise ValueError(
                f"{table}: rows disagree on columns\n  {cols}\n  {list(r.keys())}"
            )

    actual = {c["name"]: c for c in sa.inspect(conn.engine).get_columns(table)}
    unknown = [c for c in cols if c not in actual]
    required = [
        name for name, c in actual.items()
        if not c["nullable"] and name not in cols
        and c.get("default") is None and not c.get("autoincrement")
    ]
    if unknown or required:
        problems = []
        if unknown:
            problems.append(f"  unknown column(s): {', '.join(unknown)}")
        if required:
            problems.append(f"  NOT NULL column(s) not supplied: {', '.join(required)}")
        problems.append(f"  table has: {', '.join(actual)}")
        raise ValueError(f"{table}: column mismatch\n" + "\n".join(problems))
    collist = ", ".join(f"`{c}`" for c in cols)
    values = ", ".join(f":{c}" for c in cols)
    conn.execute(sa.text(f"INSERT INTO `{table}` ({collist}) VALUES ({values})"), rows)


def audit(created: dt.datetime | None = None, **extra) -> dict:
    """The bookkeeping columns every table in this application carries."""
    row = {
        "status": ACTIVE,
        "created_by": SYSTEM,
        "created_at": created or dt.datetime.combine(TODAY, dt.time(9, 0)),
        "updated_at": None,
        "updated_by": None,
        "company_id": COMPANY,
    }
    row.update(extra)
    return row


def day(offset: int) -> dt.date:
    """A date `offset` days from the anchor. Negative is the past."""
    return TODAY + dt.timedelta(days=offset)


def at(d: dt.date, hour: int = 9, minute: int = 0) -> dt.datetime:
    return dt.datetime.combine(d, dt.time(hour, minute))


def money(v) -> float:
    """Two decimal places, the way the folio stores money."""
    return round(float(v) + 1e-9, 2)


def counts(conn) -> dict[str, int]:
    insp = sa.inspect(conn.engine)
    out = {}
    for t in sorted(insp.get_table_names()):
        out[t] = conn.execute(sa.text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
    return out


def report(title: str, table_counts: dict[str, int]) -> None:
    filled = {k: v for k, v in table_counts.items() if v}
    total = sum(filled.values())
    print(f"\n  {title}: {len(filled)} tables populated, {total} rows")
    for k, v in filled.items():
        print(f"      {k:<40} {v:>6}")

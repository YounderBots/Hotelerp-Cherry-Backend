#!/usr/bin/env python3
"""Replace the seeded shared password with a strong one per account.

    python Backend/tools/rotate_passwords.py --list
    python Backend/tools/rotate_passwords.py --confirm
    python Backend/tools/rotate_passwords.py --confirm --email admin@cherryhotel.com
    python Backend/tools/rotate_passwords.py --confirm --password 'S0me-Chosen-Pass'

WHY THIS EXISTS
    Every account `seed_demo_data.py` creates signs in with the same password,
    and that password is published -- in Backend/db/*/README.md, in the seed
    source, and in this repository's history. A property that deploys the
    release and does nothing else is running with credentials anyone who has
    seen the repo already knows. `Backend/tools/preflight.py` fails on exactly
    this, and will keep failing until the passwords are changed.

    Changing them by hand means ten bcrypt hashes typed into SQL, which is how
    a shared password survives a rotation. This does it once, correctly, and
    prints each new credential exactly once so it can be filed.

WHAT IT WRITES
    Only `users.Password`, and only for ACTIVE accounts. No other column, no
    other table. The hash is bcrypt with the same cost UserServices uses to
    verify, so an account is usable the moment this returns.

PRINTED ONCE
    The generated passwords are shown on stdout and stored nowhere. If the
    output is lost, run it again for the affected account -- there is no way to
    recover a password from its hash, which is the point.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import secrets
import string
import sys

import bcrypt
import sqlalchemy as sa
from dotenv import load_dotenv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
USER_SERVICE_ENV = os.path.join(ROOT, "Backend", "Services", "UserServices", ".env")

# Unambiguous: no O/0, l/1/I. A password read off a screen and typed at a front
# desk terminal must not turn on which glyph the font chose.
ALPHABET = (
    "".join(c for c in string.ascii_uppercase if c not in "OI")
    + "".join(c for c in string.ascii_lowercase if c not in "l")
    + "".join(c for c in string.digits if c not in "01")
    + "!@#$%^&*-_=+"
)
LENGTH = 20


def generate() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(LENGTH))


def db_url() -> str:
    """The same database UserServices reads, taken from its own .env."""
    if not os.path.isfile(USER_SERVICE_ENV):
        sys.exit(f"ERROR: {USER_SERVICE_ENV} not found. Start from the repo root.")
    load_dotenv(USER_SERVICE_ENV)
    uri = os.getenv("DB_URI")
    if not uri:
        sys.exit("ERROR: DB_URI is not set in UserServices/.env")
    return uri


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true",
                    help="actually write. Without it nothing is changed.")
    ap.add_argument("--list", action="store_true",
                    help="show the accounts that would be rotated, and exit.")
    ap.add_argument("--email", action="append", default=[],
                    help="rotate only this account. Repeatable.")
    ap.add_argument("--password",
                    help="set this password on every selected account instead of "
                         "generating one each. A shared password is weaker; the "
                         "default exists because it is the better option.")
    ap.add_argument("--out",
                    help="write the new credentials to this file instead of stdout, "
                         "so they do not land in a terminal scrollback or a CI log. "
                         "The path must be OUTSIDE the repository unless --force.")
    ap.add_argument("--force", action="store_true",
                    help="allow --out to point inside the repository (only if the "
                         "path is git-ignored).")
    args = ap.parse_args()

    engine = sa.create_engine(db_url(), pool_pre_ping=True)
    with engine.begin() as conn:
        where = "WHERE status = 'ACTIVE'"
        params: dict = {}
        if args.email:
            where += " AND LOWER(Company_Email) IN :emails"
            params["emails"] = tuple(e.strip().lower() for e in args.email)
        stmt = sa.text(
            f"SELECT id, Company_Email, First_Name, Last_Name, Role_ID FROM users {where} ORDER BY id"
        )
        if args.email:
            stmt = stmt.bindparams(sa.bindparam("emails", expanding=True))
        rows = conn.execute(stmt, params).mappings().all()

        if not rows:
            print("No matching active accounts.")
            return 1

        if args.list or not args.confirm:
            print(f"{len(rows)} account(s) would be rotated:\n")
            for r in rows:
                print(f"  {r['Company_Email']:<36} {r['First_Name']} {r['Last_Name']}")
            if not args.list:
                print("\nNothing written. Re-run with --confirm.")
            return 0

        if args.password and len(args.password) < 8:
            sys.exit("ERROR: a password shorter than 8 characters is refused "
                     "(UserServices enforces the same minimum).")

        target = None
        if args.out:
            # The guard runs BEFORE anything is written. Rotating first and
            # then refusing to save the output would change every password and
            # discard the only copy of them.
            target = os.path.abspath(args.out)
            try:
                inside_repo = os.path.commonpath([target, ROOT]) == ROOT
            except ValueError:
                inside_repo = False
            if inside_repo and not args.force:
                sys.exit(
                    f"REFUSED: {target} is inside the repository.\n"
                    "A plaintext credential file must live outside the working "
                    "tree, or be git-ignored. Choose a path elsewhere, or pass "
                    "--force if you have added it to .gitignore."
                )

        print("=" * 72)
        if target:
            print(f"NEW CREDENTIALS -> {target}")
        else:
            print("NEW CREDENTIALS -- shown once, stored nowhere. File them now.")
        print("=" * 72)

        # Collected first so the file is written even if a hash fails, and so
        # nothing reaches a log unless the caller asked for a file.
        issued = []
        for r in rows:
            password = args.password or generate()
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            conn.execute(
                sa.text("UPDATE users SET Password = :p WHERE id = :i"),
                {"p": hashed, "i": r["id"]},
            )
            issued.append((r["Company_Email"], password))
            if not target:
                print(f"  {r['Company_Email']:<36} {password}")

        if target:
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("# Cherry Hotel ERP - development credentials\n")
                fh.write(f"# generated {dt.datetime.now().isoformat(timespec='seconds')}\n")
                fh.write("# Local use only. Never commit, never paste into a ticket.\n")
                fh.write("# Rotate again with rotate_passwords.py if this is lost.\n")
                for email, pw in issued:
                    fh.write(f"{email}\t{pw}\n")
            try:
                os.chmod(target, 0o600)
            except OSError:
                pass  # best effort; Windows ACLs are not POSIX
            print(f"  wrote {len(issued)} credential(s) to {target}")

        print("=" * 72)
        print(f"{len(rows)} password(s) changed.")
        print("Verify with:  python Backend/tools/preflight.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

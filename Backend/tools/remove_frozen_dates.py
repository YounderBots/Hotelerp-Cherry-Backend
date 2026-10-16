#!/usr/bin/env python
"""Remove CommonWords' four frozen date constants from every service.

    python Backend/tools/remove_frozen_dates.py [--check]

WHY REMOVE RATHER THAN FIX
    They read

        CURRENTDATE = dt.datetime.today().strftime('%Y-%m-%d')
        Today_DateFormated = dt.datetime.today().strftime('%d %b %Y')
        CURRENTTIME = dt.datetime.today().strftime('%H:%M')
        CURRENTDATETIME = dt.datetime.today()

    in the CLASS BODY, so they are evaluated once when `configs.base_config` is
    imported and then frozen for the life of the process. A service running
    across midnight reports yesterday from `CommonWords.CURRENTDATE` until it is
    restarted -- and the failure would appear on exactly the night nobody
    restarts it.

    In a hotel system with a `business_date` and a night audit that closes on it,
    a date helper that silently stops being the date is a hazard.

    The alternative was converting them to @property, which keeps the attribute
    access working. That was written, and it is worse: four copies of an
    eight-line comment per class, for a value nobody reads. Converting dead code
    preserves the invitation to use it.

    So they are deleted, and what replaces them says plainly that there is
    deliberately no date constant here and why. Verified first: across the whole
    repository -- every service's resources/, routes/ and main.py, the tools,
    the tests, the templates and the frontend -- nothing reads any of the four.

    If someone genuinely wants one, the correct form is a function called at the
    point of use, not a value captured at import. The comment says so.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVICES_DIR = ROOT / "Backend" / "Services"
SERVICES = ["LoginServices", "UserServices", "MasterDataServices",
            "HotelServices", "RestaurantServices", "BarServices"]

NAMES = ["CURRENTDATE", "Today_DateFormated", "CURRENTTIME", "CURRENTDATETIME"]

COMMENT = '''    # DELIBERATELY NO DATE CONSTANT HERE.
    #
    # There used to be four on this class -- CURRENTDATE, Today_DateFormated,
    # CURRENTTIME, CURRENTDATETIME -- all written as `dt.datetime.today()...` in
    # the class body. A class-body expression is evaluated once, when this module
    # is imported, and then frozen for the life of the process: a service running
    # across midnight reported yesterday's date until it was restarted.
    #
    # Nothing read them, so nothing ever broke, which is precisely why they were
    # dangerous -- the failure mode was invisible until the one night the service
    # was not restarted. In a system with a `business_date` and a night audit
    # that closes on it, a date helper that silently stops being the date is not
    # worth keeping around.
    #
    # If you want the date, ask for it where you use it:
    #
    #     import datetime as dt
    #     today = dt.date.today()          # or dt.datetime.now()
    #
    # A value captured at import is the bug, whichever name it is filed under.
'''

# Either quoting style, either import alias the services use.
ASSIGN = re.compile(
    r"^[ \t]*(?P<name>" + "|".join(NAMES) + r")\s*=\s*dt\.datetime\.today\(\)"
    r"(?:\.strftime\((?P<fmt>'[^']*'|\"[^\"]*\")\))?[ \t]*\r?\n",
    re.M,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="actually rewrite the files. Without it the tool only "
                         "reports, so running it can never change source by "
                         "accident -- which is also why the suite can call it as "
                         "a regression check.")
    args = ap.parse_args()

    problems = 0
    for service in SERVICES:
        path = SERVICES_DIR / service / "configs" / "base_config.py"
        if not path.is_file():
            print(f"  MISSING {path}")
            problems += 1
            continue
        text = path.read_text(encoding="utf-8")
        found = [m.group("name") for m in ASSIGN.finditer(text)]

        if not found:
            print(f"  already clean  {service}")
            continue
        if not args.apply:
            print(f"  FROZEN   {service}: {', '.join(found)}")
            problems += 1
            continue

        # Replace the whole run of them, then drop one comment at the top of the
        # class. The anchor is the class statement itself, which every service
        # has -- anchoring on a member name meant Restaurant and BarServices were
        # silently skipped, because neither defines HouseKeeper_RoleID.
        text = ASSIGN.sub("", text)
        # Tidy the gaps left behind: at most one blank line between members.
        text = re.sub(r"\n{3,}", "\n\n", text)
        anchor = re.search(r"^class CommonWords\(\):[ \t]*$", text, re.M)
        if not anchor:
            print(f"  NO `class CommonWords` in {service} -- left alone")
            problems += 1
            continue
        head = text[:anchor.end()]
        indented = "\n".join(f"    {line}" if line else "" for line in COMMENT.rstrip().split("\n"))
        text = head + "\n" + indented + "\n" + text[anchor.end():].lstrip("\n")
        path.write_text(text, encoding="utf-8")
        print(f"  removed   {service}: {', '.join(found)}")

    # Verify.
    survivors = []
    for service in SERVICES:
        text = (SERVICES_DIR / service / "configs" / "base_config.py").read_text(encoding="utf-8")
        for m in ASSIGN.finditer(text):
            survivors.append(f"{service}/{m.group('name')}")

    print()
    if survivors:
        print(f"STILL PRESENT: {survivors}", file=sys.stderr)
        return 1
    if not args.apply and problems:
        print(f"{problems} service(s) still carry the frozen constants", file=sys.stderr)
        return 1
    print(f"all {len(SERVICES)} services carry no import-time date constant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
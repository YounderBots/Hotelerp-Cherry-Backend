"""Add the phonenumbers dependency to every requirements file that needs it.

    python Backend/tools/add_phonenumbers_dep.py --check
    python Backend/tools/add_phonenumbers_dep.py --apply

WHY THIS HAD TO BE DONE
    `resources/validation.py` imports `phonenumbers`, and it was added to four
    services' requirements only as a side effect of running `pip install` on this
    machine. Every one of those files is curated by hand -- they pin exact
    versions and carry the CVE reasoning behind the pins -- so an unrecorded
    dependency is invisible to review and fatal to a clean install: the service
    starts, `main.py` imports the controllers, the controllers import
    `validation`, and the process dies with `ModuleNotFoundError: phonenumbers`.
    It works on any machine where someone happened to run pip first, which is
    exactly the failure that never reproduces for the person who made the change.

    The same applies in the browser: `libphonenumber-js` is in
    `Frontend/package.json`, and that one was already recorded.

WHY THE VERSION IS PINNED AND NOT FLOATED
    These files pin everything, and a floating `phonenumbers` would break a
    reproducible install. 9.0.40 is what the 120-case matrix is pinned against;
    libphonenumber ships new numbering-plan metadata in every release, so an
    unpinned dependency would silently change which numbers the product accepts.
"""
from __future__ import annotations

import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
VERSION = "9.0.40"

# Only the services that actually own a copy of resources/validation.py.
TARGETS = [
    "Backend/requirements.txt",
    "Backend/Services/BarServices/requirements.txt",
    "Backend/Services/RestaurantServices/requirements.txt",
    "Backend/Services/UserServices/requirements.txt",
    "Backend/Services/HotelServices/requirements.txt",
]

BLOCK = f"""
# Country-aware phone validation. `resources/validation.py` normalises a phone
# number to E.164 and checks it against the real numbering plan for its country
# via libphonenumber, which is Google's maintained metadata for every plan
# (C-086). Pinned because libphonenumber ships new plan metadata in each release:
# floating this would silently change which numbers the product accepts, and the
# 120-case matrix in tests/test_phone_validation.py is pinned to this version.
# The browser half of the same rule is `libphonenumber-js` in
# Frontend/package.json, so both halves read the same plans.
phonenumbers=={VERSION}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report only (the default)")
    parser.add_argument("--apply", action="store_true", help="make the edits")
    args = parser.parse_args()

    pending = 0
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            print(f"MISSING  {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if "phonenumbers" in text:
            print(f"recorded {rel}")
            continue
        pending += 1
        if not args.apply:
            print(f"missing  {rel}")
            continue
        # Appended at the end rather than inserted by category: these files are
        # grouped by concern, and a new group reads better than a new line wedged
        # into an existing group it does not belong to.
        text = text.rstrip("\n") + "\n" + BLOCK
        path.write_text(text, encoding="utf-8", newline="")
        print(f"added    {rel}")

    print(f"\n{pending} file(s) {'updated' if args.apply else 'are missing the dependency'}")
    if args.apply:
        for rel in TARGETS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            assert f"phonenumbers=={VERSION}" in text, f"{rel} did not take the pin"
        print(f"verified phonenumbers=={VERSION} in all {len(TARGETS)} files")

    # The services that must NOT get it, so an over-broad edit is visible.
    for rel in ("Backend/Services/LoginServices/requirements.txt",
                "Backend/Services/MasterDataServices/requirements.txt"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "phonenumbers" in text:
            print(f"WARNING  {rel} has the dependency but owns no validation.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

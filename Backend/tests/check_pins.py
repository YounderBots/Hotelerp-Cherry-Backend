#!/usr/bin/env python3
"""Fail if the installed environment does not match Backend/requirements.txt.

This exists because of a specific incident. requirements.txt pinned
python-jose==3.4.0 to close CVE-2024-33663 and CVE-2024-33664, but the machines
actually running the services still had 3.3.0 installed, so the pin protected
nobody. Nothing compared the two, so the gap stayed open silently.

Run it anywhere the services run -- CI runs it on every push:

    python Backend/tests/check_pins.py
"""
import pathlib
import re
import sys

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover - Python < 3.8
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

REQUIREMENTS = pathlib.Path(__file__).resolve().parents[2] / "Backend" / "requirements.txt"

# `name[extra1,extra2]==1.2.3` -- extras are not part of the distribution name.
PIN = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*(?:\[[^\]]*\])?\s*==\s*([^\s;#]+)")


def parse_pins(path: pathlib.Path) -> list[tuple[str, str]]:
    pins = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = PIN.match(stripped)
        if match:
            pins.append((match.group(1), match.group(2)))
    return pins


def main() -> int:
    pins = parse_pins(REQUIREMENTS)
    if not pins:
        print(f"No pins found in {REQUIREMENTS} -- refusing to pass vacuously.")
        return 1

    drifted, missing = [], []
    for name, pinned in pins:
        try:
            installed = version(name)
        except PackageNotFoundError:
            missing.append((name, pinned))
            continue
        if installed != pinned:
            drifted.append((name, pinned, installed))

    for name, pinned, installed in drifted:
        print(f"DRIFT    {name}: pinned {pinned}, installed {installed}")
    for name, pinned in missing:
        print(f"MISSING  {name}: pinned {pinned}, not installed")

    if drifted or missing:
        print()
        print(
            f"{len(drifted) + len(missing)} of {len(pins)} pinned packages do not "
            f"match the running environment."
        )
        print("Fix with: python -m pip install -r Backend/requirements.txt --upgrade")
        return 1

    print(f"All {len(pins)} pinned packages match the running environment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

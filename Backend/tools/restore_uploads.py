#!/usr/bin/env python3
"""Copy a release's image files into the static trees the services serve from.

    python Backend/tools/restore_uploads.py --list      # what would be copied
    python Backend/tools/restore_uploads.py             # copy it
    python Backend/tools/restore_uploads.py --verify    # assert it is in place

WHY THIS EXISTS
    `Backend/db/<release>/README.md` restores a deployment in two steps: load
    the SQL, then copy the images into the services' static trees. The database
    stores *paths*, not image bytes, so the second step is not optional -- skip
    it and every room photograph, staff avatar, menu tile and identity proof
    answers 404 while the API itself looks perfectly healthy.

    It was written as five hand-typed `cp -r` lines, and on the deployment at
    168.231.103.18 those five lines were skipped. All 88 image paths the
    database served resolved to nothing. Nothing detected it: the rows were
    there, the endpoints answered 200, and the only symptom was missing
    pictures in a browser.

    So it is a command now, and `preflight.py` check 6 asks a running
    deployment whether the images actually serve.

WHAT IT WRITES
    Only files under `Backend/Services/<Service>/templates/static/`. It never
    deletes and never touches the database. Re-running is safe: a file already
    byte-identical to the release is left alone.

Exit code 0 on success, 1 if a file could not be placed (or, under --verify,
is missing or differs).
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_DIR = os.path.join(ROOT, "Backend", "db")
SERVICES = os.path.join(ROOT, "Backend", "Services")

# The five service directories a release ships images for. A release folder is
# laid out as uploads/<Service>/templates/static/..., i.e. already in the shape
# the destination expects, so the copy is a straight overlay.
SERVICE_DIRS = [
    "UserServices",
    "MasterDataServices",
    "HotelServices",
    "RestaurantServices",
    "BarServices",
]


def releases() -> list[str]:
    """Release folders under Backend/db, newest-looking last."""
    if not os.path.isdir(DB_DIR):
        return []
    found = [d for d in os.listdir(DB_DIR)
             if os.path.isdir(os.path.join(DB_DIR, d, "uploads"))]
    return sorted(found)


def pick_release(name: str | None) -> str:
    avail = releases()
    if not avail:
        sys.exit(f"no release with an uploads/ folder under {DB_DIR}")
    if name is None:
        # The last one sorted is the newest for the YYYY-style names in use;
        # if that ever stops being true, --release names it explicitly.
        return avail[-1]
    if name not in avail:
        sys.exit(f"unknown release {name!r}. Available: {', '.join(avail)}")
    return name


def plan(release: str) -> list[tuple[str, str, str]]:
    """Every file to place, as (service, source path, destination path)."""
    src_root = os.path.join(DB_DIR, release, "uploads")
    out: list[tuple[str, str, str]] = []
    for service in SERVICE_DIRS:
        src = os.path.join(src_root, service)
        if not os.path.isdir(src):
            continue
        for dirpath, _dirnames, filenames in os.walk(src):
            for fn in filenames:
                s = os.path.join(dirpath, fn)
                rel = os.path.relpath(s, src)
                out.append((service, s, os.path.join(SERVICES, service, rel)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--release", default=None,
                    help="release folder under Backend/db "
                         f"(default: newest of {', '.join(releases()) or 'none'})")
    ap.add_argument("--list", action="store_true",
                    help="show what would be copied and change nothing")
    ap.add_argument("--verify", action="store_true",
                    help="assert every release image is in place and identical; "
                         "write nothing")
    args = ap.parse_args()

    release = pick_release(args.release)
    items = plan(release)
    if not items:
        sys.exit(f"release {release!r} ships no image files")

    print(f"release {release}: {len(items)} image file(s)\n")

    placed = identical = replaced = missing = differs = 0
    failures: list[str] = []

    for service, src, dst in items:
        exists = os.path.exists(dst)
        same = exists and filecmp.cmp(src, dst, shallow=False)

        if args.verify:
            if not exists:
                missing += 1
                failures.append(os.path.relpath(dst, ROOT))
            elif not same:
                differs += 1
                failures.append(os.path.relpath(dst, ROOT) + " (differs)")
            continue

        if args.list:
            state = "identical" if same else ("replace" if exists else "add")
            print(f"  {state:9s} {os.path.relpath(dst, ROOT)}")
            continue

        if same:
            identical += 1
            continue
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        except OSError as exc:
            failures.append(f"{os.path.relpath(dst, ROOT)}: {exc}")
            continue
        if exists:
            replaced += 1
        else:
            placed += 1

    # -- report -----------------------------------------------------------
    if args.list:
        print(f"\n{len(items)} file(s) in release {release}. "
              "Run without --list to place them.")
        return 0

    if args.verify:
        by_service: dict[str, int] = {}
        for service, _s, _d in items:
            by_service[service] = by_service.get(service, 0) + 1
        for service, n in sorted(by_service.items()):
            print(f"  {n:4d}  {service}")
        if failures:
            print(f"\n  FAIL  {missing} missing, {differs} differing")
            for f in failures[:20]:
                print(f"        {f}")
            if len(failures) > 20:
                print(f"        ... and {len(failures) - 20} more")
            print("\nRun: python Backend/tools/restore_uploads.py")
            return 1
        print(f"\n  PASS  all {len(items)} image(s) in place and identical")
        return 0

    if failures:
        print(f"  {len(failures)} file(s) could NOT be placed:")
        for f in failures[:20]:
            print(f"    {f}")
        return 1

    print(f"  added     {placed}")
    print(f"  replaced  {replaced}")
    print(f"  identical {identical}")
    print(f"\nImages are in place for release {release}.")
    print("These paths are only correct for the database that shipped with "
          "this release -- a re-seed mints new filenames, so restore the SQL "
          "and the images from the SAME release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

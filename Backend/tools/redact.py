#!/usr/bin/env python
"""Redact a literal credential from files in the working tree.

    python Backend/tools/redact.py <literal> path [path ...]

Why a tool rather than a sed one-liner: this gets run again every time a
credential is rotated, and "find every occurrence, replace it, and prove none
is left" is exactly the kind of thing that should not be done by hand on a
value you are trying to stop publishing.

The literal is read from stdin or argv -- never hardcoded here, because a
redaction tool containing the thing it redacts is the same mistake one level
down. It refuses to write an empty replacement, because "replace the secret with
nothing" produces a document that no longer explains what it was doing.

After writing it re-reads every file and fails if the literal survives.
"""
from __future__ import annotations

import argparse
import pathlib
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("replacement", help="what to put in place of the literal")
    ap.add_argument("literal", help="the literal to remove; read from stdin if '-'")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()

    literal = sys.stdin.readline().rstrip("\n") if args.literal == "-" else args.literal
    if not literal:
        print("nothing to redact", file=sys.stderr)
        return 2
    if not args.replacement.strip():
        print("refusing to blank the value: the document would stop making sense",
              file=sys.stderr)
        return 2

    changed, hits = [], 0
    for raw in args.paths:
        path = pathlib.Path(raw)
        if not path.is_file():
            print(f"  skip     {raw} (not a file)")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        n = text.count(literal)
        if not n:
            print(f"  clean    {raw}")
            continue
        path.write_text(text.replace(literal, args.replacement), encoding="utf-8")
        changed.append(raw)
        hits += n
        print(f"  redacted {raw}  ({n} occurrence(s))")

    # Prove it, rather than trusting the replace.
    surviving = []
    for raw in args.paths:
        path = pathlib.Path(raw)
        if path.is_file() and literal in path.read_text(encoding="utf-8",
                                                        errors="replace"):
            surviving.append(raw)

    print()
    print(f"{hits} occurrence(s) replaced across {len(changed)} file(s)")
    if surviving:
        print(f"STILL PRESENT in: {surviving}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
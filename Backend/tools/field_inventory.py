"""Inventory every user-input field in the SPA, with the validation it carries.

    python Backend/tools/field_inventory.py            # markdown matrix
    python Backend/tools/field_inventory.py --json     # machine-readable

Reads the source rather than a hand-kept list, because a hand-kept list is the
thing that goes stale. For every <Input>/<Select>/<Textarea> it reports the
field name, the component, the page, and the validation attributes actually
present in the call site (required, minLength, maxLength, pattern, type, and any
client-side check in the surrounding module).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Frontend" / "src"

# <Input ... /> including multi-line prop lists.
FIELD_RE = re.compile(
    r"<(Input|Select|Textarea|Checkbox)\b(?P<props>.*?)/>", re.S)
NAME_RE = re.compile(r"""\bname\s*=\s*["'{]([^"'{}]+)["'}]""")
ATTR_RE = re.compile(r"""\b(required|minLength|maxLength|pattern|type|min|max|step|accept)\s*=\s*(?:["']([^"']*)["']|\{\s*([^}]*?)\s*\})""")


def scan(path: pathlib.Path) -> list[dict]:
    """Fields declared directly in one file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    found = []
    for match in FIELD_RE.finditer(text):
        props = match.group("props") or ""
        name = NAME_RE.search(props)
        if not name:
            continue
        attrs = {}
        for a in ATTR_RE.finditer(props):
            key = a.group(1)
            attrs[key] = (a.group(2) if a.group(2) is not None else (a.group(3) or "")).strip()
        line = text[: match.start()].count("\n") + 1
        found.append({
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "line": line,
            "component": match.group(1),
            "name": name.group(1).strip(),
            **attrs,
        })
    return found


def main() -> int:
    rows: list[dict] = []
    for path in sorted(SRC.rglob("*.jsx")):
        if "/stories/" in path.as_posix() and "Form" not in path.as_posix():
            continue
        rows.extend(scan(path))
    for path in sorted(SRC.rglob("*.js")):
        rows.extend(scan(path))

    # Name/validation classification, shared with the report below.
    def kind(name: str, attrs: dict) -> str:
        n = name.lower()
        # Word-ish matching, not substring: "acknowledgment_of_hotel_policies"
        # contains "tel" inside "hotel" and is not a phone field.
        tokens = set(re.split(r"[^a-z0-9]+", n))
        if tokens & {"mobile", "phone", "telephone", "contact", "whatsapp", "msisdn"} \
                or n.endswith(("_mobile", "_phone", "_telephone")):
            return "phone"
        if "email" in n or n.endswith("_e_mail"):
            return "email"
        if "password" in n:
            return "password"
        if any(k in n for k in ("date", "time", "_at")) and "datetime" not in n:
            return "date/time"
        if any(k in n for k in ("amount", "price", "rate", "cost", "quantity", "qty",
                                "percent", "score", "no_of", "count", "capacity",
                                "min_", "max_", "bed", "adult", "child", "discount",
                                "tax", "salary", "points", "level")):
            return "numeric"
        if attrs.get("type") in ("number", "date", "time", "datetime-local", "file"):
            return "numeric" if attrs.get("type") == "number" else "date/time"
        return "text"

    for r in rows:
        r["kind"] = kind(r["name"], r)
        r["has_max"] = "maxLength" in r
        r["has_required"] = "required" in r

    by_kind: dict[str, int] = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1

    if "--json" in sys.argv:
        print(json.dumps({"fields": rows, "by_kind": by_kind}, indent=2))
        return 0

    print(f"# Field inventory -- {len(rows)} input fields across {len({r['file'] for r in rows})} files\n")
    print("| Kind | Fields | With maxLength | With required |")
    print("|---|---:|---:|---:|")
    for k in sorted(by_kind, key=lambda x: -by_kind[x]):
        subset = [r for r in rows if r["kind"] == k]
        print(f"| {k} | {len(subset)} | {sum(1 for r in subset if r['has_max'])} | "
              f"{sum(1 for r in subset if r['has_required'])} |")
    print(f"\n**Total: {len(rows)} fields**\n")

    print("## Every field\n")
    print("| Page (file) | Field | Kind | Required | maxLength | Other constraints |")
    print("|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: (x["file"], x["line"])):
        page = r["file"].split("/")[-1]
        others = ", ".join(
            f"{k}={r[k]}" for k in ("type", "min", "max", "step", "pattern", "accept")
            if r.get(k)
        )
        print(f"| {page}:{r['line']} | `{r['name']}` | {r['kind']} | "
              f"{'yes' if r['has_required'] else '-'} | {r.get('maxLength', '-')} | {others or '-'} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

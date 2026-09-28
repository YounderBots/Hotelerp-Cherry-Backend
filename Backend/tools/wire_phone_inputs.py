"""Wire the country selector into the last four phone fields in the SPA.

    python Backend/tools/wire_phone_inputs.py --check
    python Backend/tools/wire_phone_inputs.py --apply

The four forms that still had a bare `<Input type="tel">` after the first pass.
They were not cosmetic omissions: with country-aware validation in the API, a
national number typed here is refused with "Select the country for this mobile",
while the same number on the guest, booking and employee forms gets a country
selector. Four screens, two different behaviours for the same field.

WHAT IT EDITS, AND WHY IT IS SAFE TO DO MECHANICALLY
    Every one of the four had the same shape, verified by reading each file:
    an `initialForm` object, a `formError` useState, an `Input` import, one
    `<Input type="tel" name=... value={formData.X} onChange={handleChange} />`,
    and one payload line `X: formData.X.trim()`. The script asserts every one of
    those five anchors before it writes, and refuses the file if any is missing
    -- because a plausible-looking wrong edit to a form is worse than an
    unwired one. It prints what it did so the diff can be read.
"""
from __future__ import annotations

import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Frontend" / "src"

# rel path -> (form state key, human label for the assertion failure)
TARGETS = {
    "Restaurant/Guest Management/GuestManagement.jsx": "mobile",
    "Bar/Order Management/Orders.jsx": "guest_mobile",
    "Restaurant/Order Management/Orders.jsx": "guest_mobile",
    "Restaurant/Table Reservation/TableReservation.jsx": "guest_mobile",
}

# A room's telephone is an internal extension, not somebody's number, so it is
# deliberately absent: forcing a numbering plan on it would reject every
# extension that is not eleven digits.
NOT_A_PERSON = {"room_telephone"}

def input_import_for(rel: str) -> str:
    """The `import Input` line this file already has, whatever its depth.

    A fixed `../stories/...` anchor is wrong for every file that is not
    directly under `src`, and a wrong-but-close anchor is how an edit lands in
    the wrong place. So the path is read from the file and reused verbatim.
    """
    m = re.search(r'^import Input from "([^"]+)";', (SRC / rel).read_text(encoding="utf-8"), re.M)
    return f'import Input from "{m.group(1)}";' if m else ""


def phone_import_for(rel: str) -> str:
    """The matching PhoneInput import, one level up the same way."""
    return input_import_for(rel).replace(
        'from "../stories/Form/Input"', 'from "../stories/Form/PhoneInput"'
    ).replace("Input;", "PhoneInput;").replace(
        'from "../../stories/Form/Input"', 'from "../../stories/Form/PhoneInput"'
    ).replace("import Input", "import PhoneInput")


def tel_inputs(text: str) -> list[dict]:
    """Every bare `<Input type="tel">` in the file, with its field name."""
    found = []
    for m in re.finditer(r"<Input\b(?P<props>.*?)/>", text, re.S):
        props = m.group("props")
        if 'type="tel"' not in props:
            continue
        name = re.search(r"""\bname\s*=\s*["']([^"']+)["']""", props)
        found.append({
            "name": name.group(1) if name else None,
            "start": m.start(),
            "end": m.end(),
            "props": props,
        })
    return found


def wire(text: str, key: str, rel: str) -> tuple[str, list[str]]:
    """Return the rewritten text and the list of assertions that failed."""
    problems: list[str] = []

    candidates = [f for f in tel_inputs(text) if f["name"] == key]
    if not candidates:
        return text, [f"no bare <Input type=\"tel\"> named {key!r}"]
    target = candidates[-1]

    label = re.search(r"""\blabel\s*=\s*["']([^"']+)["']""", target["props"])
    field_label = label.group(1) if label else "Phone"

    replacement = (
        '<PhoneInput\n'
        f'          label="{field_label}"\n'
        '          required\n'
        f'          name="{key}"\n'
        f'          value={{formData.{key}}}\n'
        '          region={formData.phone_region}\n'
        '          error={Boolean(phoneError)}\n'
        '          helperText={phoneError}\n'
        '          onChange={(e164, region, result) => {\n'
        f'            setFormData((p) => ({{ ...p, {key}: e164, phone_region: region }}));\n'
        '            setPhoneError(\n'
        '              result && result.ok === false && !result.incomplete ? result.message : null,\n'
        '            );\n'
        '          }}\n'
        '        />'
    )
    text = text[: target["start"]] + replacement + text[target["end"]:]

    # The country has to live somewhere, and it travels with the number because a
    # national number with no country is ambiguous and the API will not guess one.
    #
    # The check is on the FORM OBJECT, not the file. Asking "is phone_region in
    # the text?" after the JSX edit above has already written `formData.phone_region`
    # always answers yes, so the country was never declared in initialForm -- and a
    # field whose country comes from `undefined` shows the wrong selector on first
    # paint and sends `undefined` in the payload.
    form_object = re.search(r"const initialForm = \{(.*?)\n\};", text, re.S)
    if not form_object:
        problems.append("no `const initialForm = {` to add the country to")
    elif "phone_region" not in form_object.group(1):
        text = text.replace(
            "const initialForm = {\n",
            "const initialForm = {\n"
            "  // The country the number is typed in. It is sent with the number, not\n"
            "  // stored with it: a national number with no country code is ambiguous\n"
            "  // and the API refuses to guess one (C-086).\n"
            '  phone_region: "IN",\n',
            1,
        )

    if "const [phoneError, setPhoneError] = useState(null);" not in text:
        if "const [formError, setFormError] = useState(null);" not in text:
            problems.append("no formError state to sit the phone message beside")
        else:
            text = text.replace(
                "const [formError, setFormError] = useState(null);",
                "const [formError, setFormError] = useState(null);\n"
                "  // The phone field's own message, kept next to the field rather than\n"
                "  // only in the form-level banner.\n"
                "  const [phoneError, setPhoneError] = useState(null);",
                1,
            )

    if "Form/PhoneInput" not in text:
        anchor = input_import_for(rel)
        if not anchor:
            problems.append("no `import Input from .../Form/Input` to sit the PhoneInput import beside")
        elif anchor not in text:
            problems.append(f"the Input import moved since this tool last read it: {anchor!r}")
        else:
            text = text.replace(anchor, anchor + "\n" + phone_import_for(rel), 1)

    # The payload carries the region, so the server can read a national number.
    if not re.search(rf"phone_region:\s*formData\.phone_region", text):
        pattern = re.compile(rf"(\b{re.escape(key)}:\s*formData\.{re.escape(key)}\.trim\(\)[^,\n]*,)")
        text, n = pattern.subn(r"\1\n        phone_region: formData.phone_region,", text, count=1)
        if not n:
            problems.append(f"no payload line `{key}: formData.{key}.trim()` to add the region to")

    return text, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report only (the default)")
    parser.add_argument("--apply", action="store_true", help="make the edits")
    args = parser.parse_args()

    pending = 0
    written = 0
    for rel, key in TARGETS.items():
        path = SRC / rel
        if not path.exists():
            print(f"MISSING  {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        remaining = [f["name"] for f in tel_inputs(text) if f["name"] != "__none__"]
        if not remaining:
            print(f"wired    {rel}")
            continue
        pending += 1
        if not args.apply:
            print(f"to wire  {rel}: {remaining}")
            continue
        new_text, problems = wire(text, key, rel)
        if problems:
            # Refuse rather than half-write: a form that renders a field it does
            # not submit is worse than one that is honestly unwired.
            print(f"SKIPPED  {rel} -- {problems}")
            continue
        path.write_text(new_text, encoding="utf-8", newline="")
        written += 1
        print(f"wired    {rel}: {key!r}")

    if args.apply:
        print(f"\n{written} file(s) written"
              f"; {pending - written} refused because an anchor did not match")
    else:
        print(f"\n{pending} file(s) still need wiring")
    if not args.apply:
        print("\nEvery remaining bare <Input type=\"tel\"> in the SPA:")
        for path in sorted(SRC.rglob("*.jsx")):
            for f in tel_inputs(path.read_text(encoding="utf-8", errors="replace")):
                note = ""
                if f["name"] in NOT_A_PERSON:
                    note = "  <- internal extension, deliberately not country-aware"
                elif f["name"] is None:
                    note = "  <- not a person\'s number (filter or story)"
                print(f"  {path.relative_to(ROOT).as_posix()}  {f['name']}{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

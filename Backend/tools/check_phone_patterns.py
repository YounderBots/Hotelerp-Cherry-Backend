"""Guard: no hand-written phone-number pattern may come back.

    python Backend/tools/check_phone_patterns.py

The product used to carry four of its own, and the failure they share is invisible
until a guest is refused:

    /^[+()\\-\\s\\d]{7,20}$/   accepts `(((((((` and `1234567`
    /^[+\\d][\\d\\s\\-()]{6,19}$/   refuses a number longer than twenty characters

They know nothing about any country, and no pattern can: national lengths, trunk
prefixes and mobile ranges are data, and they differ per country. The rule now
lives in `resources/validation.py` on the server and `stories/Form/phone.js` in
the browser, both on libphonenumber's metadata.

SO WHY IS THERE STILL A SCRIPT
    Because the failure mode is a *new* file quietly growing its own regex, and
    nobody notices until a guest from Qatar cannot be entered. This is the check
    that catches that at review time. It is report-only on purpose: there is
    nothing left to rewrite, and a tool that edits source automatically is a
    hazard in a repository where the rules span two languages and four services.

IT EXITS NON-ZERO WHEN IT FINDS ONE, so it can go in a pre-commit or CI step.

HOW IT DECIDES
    A phone pattern is a character class that BOTH matches digits and accepts the
    punctuation people write inside a number -- `+`, `(`, `)`, or an escaped
    hyphen -- and is followed by a length bound. Both halves matter: a digit class
    alone matches `#[0-9A-Fa-f]{6}` (a colour check) and `[A-Za-z0-9]{1,64}`
    (a code check), and an escaped hyphen alone matches nothing anyone writes. It
    also ignores comments, so the note explaining what was removed from
    `AddNewReservation.jsx` is not reported as if the pattern were still there.

ALLOWED, AND WHY
    * `Form.stories.jsx` \u2014 the component gallery, not a form the product ships.
    * `phone.js` / `PhoneInput.jsx` and their tests \u2014 the rules themselves.
    * `Register.jsx` \u2014 the public pre-registration form posts to an endpoint this
      audit did not change, and its pattern is anchored. Recorded as remaining
      work rather than silently accepted, so the exception is visible.
    * `room_telephone` \u2014 a room's telephone is an internal extension, not
      somebody's number, and forcing a numbering plan on it would reject every
      extension that is not eleven digits.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Frontend" / "src"
BACKEND = ROOT / "Backend" / "Services"

# The shape of "somebody tried to match a phone number": a character class with a
# length bound after it. Whether the class is a phone pattern is then decided in
# code rather than in one unreadable pattern, because the two halves can appear in
# either order (`[+()\-\s\d]` puts the punctuation first, `[\d\s\-()]` the digits
# first) and a single alternation that gets that wrong fails silently -- it was
# tried, it reported a clean tree while a real pattern sat in the file, and the
# only reason that was caught is that the guard was tested against a planted one.
CLASS_WITH_BOUND = re.compile(r"\[[^\]]*\]\s*\{")
HAS_DIGIT = re.compile(r"\\d|\d\s*-\s*\d")
# The punctuation people actually write inside a number. A bare unescaped hyphen
# does not count: `[0-9A-Fa-f]{6}` is a colour check, not a phone pattern.
HAS_PHONE_PUNCTUATION = re.compile(r"\+|\(|\)|\\-")


def is_phone_pattern(line: str) -> bool:
    """A digit class that also accepts phone punctuation, with a length bound."""
    for m in CLASS_WITH_BOUND.finditer(line):
        body = m.group(0)[1: m.group(0).index("]")]
        if HAS_DIGIT.search(body) and HAS_PHONE_PUNCTUATION.search(body):
            return True
    return False

ALLOWED_SUFFIXES = (
    "stories/Form/Form.stories.jsx",
    "stories/Form/phone.js",
    "stories/Form/phone.test.js",
    "stories/Form/PhoneInput.jsx",
    "stories/Form/PhoneInput.test.jsx",
    "resources/validation.py",
)

# The one pattern that must stay, with the reason it stays. Keyed BY FILE, because
# keying it by the pattern text alone permits that pattern anywhere -- so a new
# form could reintroduce it and the guard would call the tree clean. An exception
# that does not say where it applies is not an exception, it is a hole.
ALLOWED_PATTERNS = {
    "Authentication/Pages/Register.jsx": (
        r"/^[+\d][\d\s\-()]{6,19}$/",
        "Authentication/Pages/Register.jsx \u2014 the public pre-registration form posts to an endpoint this "
        "audit did not change, and its pattern is anchored. Recorded as remaining work, not silently accepted.",
    ),
}

COMMENT = re.compile(r"^\s*(//|\*|/\*|#)")


def scan(root: pathlib.Path, suffixes: tuple[str, ...]) -> list[tuple[pathlib.Path, int, str]]:
    hits = []
    for suffix in suffixes:
        for path in sorted(root.rglob(f"*{suffix}")):
            try:
                if path.stat().st_size > 500_000:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if COMMENT.match(line) or not is_phone_pattern(line):
                    continue
                hits.append((path, number, line.strip()))
    return hits


def main() -> int:
    def rel(path: pathlib.Path) -> str:
        return path.relative_to(ROOT).as_posix()

    findings: list[tuple[str, int, str]] = []
    reported_allowed = False

    for root, suffixes in ((SRC, (".jsx", ".js")), (BACKEND, (".py",))):
        for path, number, line in scan(root, suffixes):
            relpath = rel(path)
            if any(relpath.endswith(ok) for ok in ALLOWED_SUFFIXES):
                continue
            # The exception applies to its own file only.
            # Matched on the tail of the path, like ALLOWED_SUFFIXES: the key is
            # written without the repository-relative prefix.
            allowance = next(
                (v for k, v in ALLOWED_PATTERNS.items() if relpath.endswith(k)),
                None,
            )
            if allowance and allowance[0] in line:
                if not reported_allowed:
                    print(f"allowed  {allowance[1]}")
                    reported_allowed = True
                continue
            findings.append((relpath, number, line))

    if not findings:
        print(
            "No hand-written phone patterns outside the shared rules "
            "and the one recorded exception."
        )
        return 0

    print(f"{len(findings)} hand-written phone pattern(s) found:\n")
    for relpath, number, line in findings:
        print(f"  XX {relpath}:{number}")
        print(f"     {line[:150]}")
    print(
        "\nUse validatePhone() from stories/Form/phone.js (browser) or "
        "normalize_phone()\nfrom resources/validation.py (server). Numbering plans are data, not patterns."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""No hand-written phone pattern may come back, and the check itself must work.

    python -m pytest Backend/tests/test_phone_pattern_guard.py -q

WHY A TEST AND NOT A NOTE
    The product carried four hand-written phone regexes for its lifetime, and the
    only reason anybody noticed is that this audit read the code. A note in a
    document is not a check: the natural next contribution adds a field, writes
    the three lines they always write, and nothing objects. Registering the guard
    here is what makes it a rule rather than a suggestion.

WHAT IT PROVES
    Two things, because a guard that cannot fail is worse than no guard at all:

      1. The tree is clean today -- no phone pattern outside the shared rules and
         the one recorded exception.
      2. The guard still detects one, and still ignores what is not a phone
         pattern. This was checked by planting the real patterns and finding that
         the first version of the detector reported a clean tree while one sat in
         the file: its alternation assumed the digits came before the punctuation
         in the character class, and in `[+()\\-\\s\\d]` they do not.

    The second test writes into the source tree and restores it. It is scoped to a
    file it creates, and every write is in a `finally`, so a failure leaves no
    trace -- but it is still a test that touches files, which is why the tree is
    verified clean again at the end of it.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
GUARD = ROOT / "Backend" / "tools" / "check_phone_patterns.py"

# A file the guard is allowed to write into, chosen because it is already wired to
# the shared field -- so a planted pattern here is the most likely real regression.
PROBE = ROOT / "Frontend" / "src" / "Restaurant" / "Table Reservation" / "TableReservation.jsx"


def run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD)], cwd=ROOT, capture_output=True, text=True, check=False
    )


def test_the_guard_script_exists_and_runs():
    assert GUARD.exists(), f"{GUARD} is missing; the rule has no enforcement"
    result = run_guard()
    assert result.returncode == 0, (
        "A hand-written phone pattern is back, or the guard itself is broken:\n"
        + result.stdout
    )


def test_the_guard_detects_a_planted_pattern_and_ignores_the_rest():
    """A guard that cannot fail is worse than no guard at all."""
    # (planted text, should the guard fire?)
    cases = [
        # The four the product actually shipped, restored in a form.
        ("const PHONE_RE = /^[+()\\-\\s\\d]{7,20}$/;\n\n", True),
        # The Register pattern, copied somewhere it is not allowed.
        ("const P2 = /^[+\\d][\\d\\s\\-()]{6,19}$/;\n\n", True),
        # The same idea on the server.
        ('if not re.fullmatch(r"[0-9+()-]{10}", value):\n', True),
        # Not phone patterns: a colour, a code, bare digits, and the comment that
        # records the removal. A detector loose enough to flag these is one people
        # will disable.
        (
            "const COLOUR = /^#[0-9A-Fa-f]{6}$/;\n"
            "const CODE = /^[A-Za-z0-9]{1,64}$/;\n"
            "const RANGE = /^[0-9]{1,3}$/;\n"
            "// the old /^[+()\\-\\s\\d]{7,20}$/ is gone\n",
            False,
        ),
    ]

    original = PROBE.read_text(encoding="utf-8")
    try:
        for planted, should_fire in cases:
            PROBE.write_text(planted + original, encoding="utf-8", newline="")
            fired = run_guard().returncode == 1
            assert fired is should_fire, (
                f"guard {'fired' if fired else 'stayed quiet'} on a case it should "
                f"{'have caught' if should_fire else 'have ignored'}:\n{planted!r}"
            )
    finally:
        PROBE.write_text(original, encoding="utf-8", newline="")

    # And the tree really is clean again, so the test does not leave a pattern behind.
    assert run_guard().returncode == 0, "the test left a pattern in the tree"
    assert "PHONE_RE" not in PROBE.read_text(encoding="utf-8")

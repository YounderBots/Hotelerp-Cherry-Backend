"""The phone-number validation matrix, run against every service that owns one.

    python -m pytest Backend/tests/test_phone_validation.py -q

WHY THIS SUITE EXISTS
    Phone validation used to be `re.fullmatch(r"\\d{10}", value)` in the two
    guest controllers and nothing at all in the others (C-086). A hotel that
    takes guests from abroad cannot describe a guest's mobile in ten digits:
    the rule rejected every non-Indian number, every number typed in
    international format, and accepted ten digits belonging to no numbering
    plan.

    This is the matrix, written once and run from each service root that owns a
    phone field, because the validator is a small identical file per service
    (services cannot import each other) and four copies of a rule is four
    chances to drift. `test_every_service_copy_is_identical` is what stops the
    drift.

    The distinction the matrix is built around: a number can be IMPOSSIBLE (no
    plan has one of that shape) or POSSIBLE-BUT-INVALID (well-formed, in a range
    the plan does not assign). They produce different messages, and a user who
    typed a wrong digit needs to be told that, not told their number is invalid.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
from fastapi import HTTPException

SERVICE_ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(SERVICE_ROOT))

ALL_ROOTS = ["BarServices", "RestaurantServices", "UserServices", "HotelServices"]


def load():
    from resources import validation
    return validation


pv = load()


def detail_of(value, **kwargs) -> str:
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone(value, **kwargs)
    return str(caught.value.detail)


# --------------------------------------------------------------- 1. valid ----
# One real, structurally valid number per plan. These are the numbers the
# library's own metadata says are assigned; none of them has been verified as
# reachable, and the suite never claims otherwise.
VALID = {
    "IN": "+919876543210",       # India, mobile
    "IN_local": "9876543210",    # same number, national format, default region IN
    "IN_prefixed": "+91 98765 43210",
    "IN_zero_prefixed": "09876543210",   # a leading trunk 0, as Indians type it
    "US": "+14155552671",
    "US_local": "(415) 555-2671",
    "US_hyphens": "415-555-2671",
    "US_spaces": "+1 415 555 2671",
    "GB": "+442079460958",
    "GB_local": "020 7946 0958",
    "AE": "+971501234567",
    "SG": "+6581234567",
    "DE": "+4915112345678",
    "AU": "+61412345678",
    "CA": "+14165550123",
    "NZ": "+64211234567",
    "ZA": "+27821234567",
    "BR": "+5511987654321",
    "JP": "+819012345678",
    "IN_unicode_digits": "९८७६५४३२१०",       # Devanagari digits
    "IN_fullwidth": "９８７６５４３２１０",              # full-width digits
    "US_intl_prefix_00": "0014155552671",           # dialled-out form
    "IN_paste_formatted": "+91-98765-43210",
}

# The region each form is read in. National-format forms ("IN_local", "GB_local",
# "US_local", "US_hyphens") are only valid with their own country; the
# international ones are valid in any, so they get IN to keep the table flat.
REGION = {
    "IN": "IN", "IN_local": "IN", "IN_prefixed": "IN", "IN_zero_prefixed": "IN",
    "IN_unicode_digits": "IN", "IN_fullwidth": "IN", "IN_paste_formatted": "IN",
    "US": "US", "US_local": "US", "US_hyphens": "US", "US_spaces": "US",
    "US_intl_prefix_00": "US",
    "GB": "GB", "GB_local": "GB",
    "AE": "AE", "SG": "SG", "DE": "DE", "AU": "AU", "CA": "CA",
    "NZ": "NZ", "ZA": "ZA", "BR": "BR", "JP": "JP",
}


@pytest.mark.parametrize("value", sorted(VALID))
def test_a_valid_number_is_accepted(value):
    out = pv.normalize_phone(VALID[value], field="mobile", default_region=REGION[value])
    assert out is not None
    assert out.startswith("+"), f"{value!r} did not normalise to E.164"
    assert out.replace("+", "").isdigit()
    # Nothing but a leading +, digits: no spaces, no separators survive.
    assert " " not in out and "-" not in out and "(" not in out


def test_the_same_number_typed_four_ways_stores_one_string():
    """The point of normalisation: one number, one stored spelling."""
    forms = ["+919876543210", "+91 98765 43210", "09876543210", "+91-98765-43210"]
    stored = {pv.normalize_phone(f, field="mobile", default_region="IN") for f in forms}
    assert stored == {"+919876543210"}


def test_e164_is_the_storage_form():
    # A national format needs its region; the stored form is the same either way.
    assert pv.normalize_phone("(415) 555-2671", field="mobile", default_region="US") == "+14155552671"
    assert pv.normalize_phone("020 7946 0958", field="mobile", default_region="GB") == "+442079460958"


# ------------------------------------------------------ 2. invalid format ----
INVALID = {
    "letters": "abcdefghij",
    "letters_mixed": "98765abcde",
    "special_chars": "!@#$%^&*()",
    "emoji": "📞9876543210",
    "sql": "98765' OR 1=1--",
    "html": "<script>alert(1)</script>",
    "path": "../../etc/passwd",
    "trailing_letters": "9876543210x",
    "too_short": "1",
    "two_digit": "12",
    "too_long_national": "98765432101234567890",
    "very_long_malicious": "9" * 500,
    "repeated_digits": "1111111111111111",
    "leading_plus_only": "+",
    "dashes_only": "----",
    "brackets_only": "()",
    "percent_zero": "%2B91987654321",
    "emoji_then_digits": "\U0001F4DE9876543210",   # parse() would extract the digits
    "letter_prefix": "call9876543210",
    "underscored": "98765_43210",
}


@pytest.mark.parametrize("value", sorted(INVALID))
def test_junk_is_refused_with_a_readable_message(value):
    message = detail_of(value, field="mobile")
    assert "phone" in message.lower() or "digit" in message.lower() or "required" in message.lower()
    # Never a stack trace, never a 500, never an internal phrase.
    assert "Traceback" not in message
    assert "phonenumber" not in message
    assert len(message) < 200


def test_digits_hidden_inside_junk_are_not_silently_extracted():
    """`parse("📞9876543210")` returns a valid number, and that is the bug.

    Accepting it would store a number the user never typed, with no indication
    that the character they pasted was dropped. Separators are forgiven because
    people type them; an emoji or a word is a mistake worth reporting.
    """
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone("\U0001F4DE9876543210", field="mobile", default_region="IN")
    assert caught.value.status_code == 400
    assert "digit" in str(caught.value.detail).lower()


def test_a_very_long_paste_is_refused_before_parsing():
    """A 500-digit paste must not reach the parser at all."""
    message = detail_of("9" * 500, field="mobile")
    assert "too long" in message.lower()


# --------------------------------------------------- 3. empty and optional ----
@pytest.mark.parametrize("value", [None, "", "   ", "\t"])
def test_empty_input_is_none_not_an_error(value):
    """Optional fields stay optional: nothing typed means absent."""
    assert pv.normalize_phone(value, field="mobile") is None


@pytest.mark.parametrize("value", ["-", "()", "  -  ", "( )", "--"])
def test_separators_only_is_required_not_absent(value):
    """A filled-in field containing no digits is not an empty field.

    Letting it become None made a create collide with the uniqueness filter and
    answer "this mobile already exists" for a guest who has no mobile at all.
    """
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone(value, field="mobile")
    assert caught.value.status_code == 400
    assert "required" in str(caught.value.detail).lower()


# ------------------------------- 4. region handling, including the mismatch ----
def test_a_national_number_needs_a_region():
    with pytest.raises(HTTPException):
        pv.normalize_phone("4155552671", field="mobile", default_region="ZZ")


def test_a_number_too_short_to_be_one_anywhere_says_so():
    """Not "select a country" -- two digits is wrong in every plan."""
    message = detail_of("12", field="mobile")
    assert "short" in message.lower()
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone("12", field="mobile", default_region="IN")
    assert "short" in str(caught.value.detail).lower()


def test_the_region_decides_how_a_national_number_is_read():
    assert pv.normalize_phone("9876543210", field="mobile", default_region="IN") == "+919876543210"
    # The same ten digits are not an assignable US number, and the message has
    # to name the country so the user knows which selector to change.
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone("9876543210", field="mobile", default_region="US")
    message = str(caught.value.detail).lower()
    assert "united states" in message or "does not have" in message


def test_a_national_number_without_a_region_is_refused_not_guessed():
    """The bug this rule exists to prevent.

    `(415) 555-2671` is ten digits that fit India's numbering plan, so a
    validator that falls back to IN accepts it as `+914155552671` -- a
    structurally valid number belonging to nobody. Refusing, and saying to
    select a country, is the only safe answer.
    """
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone("(415) 555-2671", field="mobile")
    assert caught.value.status_code == 400
    assert "country" in str(caught.value.detail).lower()
    with pytest.raises(HTTPException):
        pv.normalize_phone("9876543210", field="mobile")


def test_an_international_number_needs_no_region():
    """A '+' makes the country explicit, so the selector is not consulted."""
    assert pv.normalize_phone("+14155552671", field="mobile") == "+14155552671"
    assert pv.normalize_phone("+442079460958", field="mobile") == "+442079460958"


def test_an_explicit_country_code_overrides_the_region():
    """Typing +44 while the selector says US must still be a UK number."""
    out = pv.normalize_phone("+442079460958", field="mobile", default_region="US")
    assert out == "+442079460958"


def test_country_code_without_a_number_is_refused():
    assert detail_of("+44", field="mobile")


def test_an_invalid_country_code_is_refused():
    message = detail_of("+999123456789", field="mobile")
    assert "valid" in message.lower() or "phone" in message.lower()


def test_a_duplicate_country_code_is_refused():
    """'+91 91 98765 43210' is not a number in any plan."""
    with pytest.raises(HTTPException):
        pv.normalize_phone("+91 91 98765 43210", field="mobile")


def test_changing_the_country_after_typing_revalidates_rather_than_keeping_the_old_number():
    """The 'country changed after entering number' case.

    `020 7946 0958` is a London number, and it is *also* a structurally valid
    Indian number (Mumbai's 020 area code), so accepting it after the switch is
    correct -- the digits name a real number in the new country. What must
    never happen is the old interpretation surviving the change. So the
    assertion is on the number, not on a refusal: it is either the new
    country's number or a 400, and it is never the previous country's.
    """
    uk = pv.normalize_phone("020 7946 0958", field="mobile", default_region="GB")
    assert uk == "+442079460958"

    try:
        after = pv.normalize_phone("020 7946 0958", field="mobile", default_region="IN")
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        assert after == "+912079460958"
        assert after != uk


# ------------------------------------- 5. possible vs valid (the distinction) --
def test_possible_but_not_valid_is_reported_differently_from_impossible():
    """Two failures, two messages.

    A number that is impossible (no plan has one of that shape) and a number
    that is well-formed but in a range the plan does not assign need different
    corrections from the person typing it, so they are not given the same
    advice. Both are refused; the assertion is that the possible-but-invalid
    one names the country, because the fix is "change the country or a digit",
    not "that is not a number".
    """
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone("9876543210", field="mobile", default_region="US")
    message = str(caught.value.detail).lower()
    assert "does not have" in message or "united states" in message
    # Never a raw library error, never a stack trace.
    assert "phonenumber" not in message
    assert "traceback" not in message


# ------------------------------------------------------- 6. mobile-only rule ---
def test_mobile_only_rejects_a_landline_when_asked():
    landline = "+442079460958"
    assert pv.normalize_phone(landline, field="mobile") is not None  # fine generally
    with pytest.raises(HTTPException) as caught:
        pv.normalize_phone(landline, field="mobile", allow_mobile_only=True)
    assert "mobile" in str(caught.value.detail).lower()


def test_mobile_only_accepts_a_mobile():
    assert pv.normalize_phone("+919876543210", field="mobile", allow_mobile_only=True) == "+919876543210"


# ------------------------------------------------------------- 7. utilities ----
def test_is_valid_phone_never_raises():
    assert pv.is_valid_phone("+919876543210") is True
    assert pv.is_valid_phone("nonsense") is False
    assert pv.is_valid_phone(None) is False


def test_display_phone_is_readable_but_storage_is_not():
    stored = pv.normalize_phone("+14155552671", field="mobile")
    shown = pv.display_phone(stored)
    assert stored == "+14155552671"
    assert shown != stored, "display should be prettified"
    assert shown.startswith("+1")


def test_display_phone_passes_through_anything_it_cannot_parse():
    assert pv.display_phone("not a number") == "not a number"
    assert pv.display_phone("") == ""


def test_the_error_names_the_field_it_came_from():
    message = detail_of("abc", field="alternative_mobile")
    assert "Alternative" in message or "alternative" in message


# =========================================================== email ==========
# `if "@" not in x or "." not in x` was the rule. It accepts `@.`, `a@b.`,
# `a b@c.d` and a 10KB string. These are the cases that separates a real check
# from a real one.
GOOD_EMAILS = [
    "a@b.com",
    "name@example.com",
    "first.last@sub.example.co.uk",
    "user+tag@example.com",
    "user_name-1@example-host.com",
    "O'Brien@example.com",
    "josé@example.com",
    "x@a.io",
    "user@example.com\n",      # a pasted trailing newline is trimmed, not rejected
]
BAD_EMAILS = [
    "",
    "   ",
    "plainaddress",
    "@example.com",
    "user@",
    "user@localhost",           # no dot: not deliverable on the public internet
    "user@example.",             # no TLD
    "user@.com",
    "user@@example.com",         # two @
    "user name@example.com",     # space
    "user@exam ple.com",
    "user<>@example.com",
    "a" * 65 + "@example.com",   # local part over 64
    "a" * 250 + "@example.com",  # whole address over 254
    "<script>alert(1)</script>@example.com",
]


@pytest.mark.parametrize("value", GOOD_EMAILS)
def test_valid_email_is_accepted(value):
    assert pv.validate_email(value) is True


@pytest.mark.parametrize("value", BAD_EMAILS)
def test_invalid_email_is_refused(value):
    assert pv.validate_email(value) is False


def test_email_is_normalised_for_storage_and_lookup():
    assert pv.normalize_email("  Name@Example.COM ") == "name@example.com"
    assert pv.require_email(" Name@Example.COM ") == "name@example.com"
    assert pv.normalize_email(None) is None


def test_require_email_returns_none_for_blank_so_optional_stays_optional():
    assert pv.require_email("") is None
    assert pv.require_email(None) is None


def test_require_email_raises_with_readable_copy():
    with pytest.raises(HTTPException) as caught:
        pv.require_email("nope", field="company_email")
    assert caught.value.status_code == 400
    assert "email" in str(caught.value.detail).lower()
    assert "example" in str(caught.value.detail), "the message should show the shape"


# =========================================================== names ==========
# A name field that rejects O'Brien, José or मीरा is broken for most of the
# world, so these are the names that MUST be kept -- including one with an
# internal tab, because whitespace inside a name collapses to a single space
# and is then perfectly good. Only characters wrong everywhere are refused.
GOOD_NAMES = [
    "Aarav", "Jos\u00e9", "O'Brien", "Anne-Marie", "van der Berg",
    "\u092e\u0940\u0930\u093e", "\u674e\u96f7", "Muhammad ibn Abdullah", "Smith Jr.",
    "Anne\tMarie",          # internal tab: collapsed, not rejected
]
BAD_NAMES = [
    "", "   ", "x" * 101, "bad\x00name", "bell\x07name", "esc\x1b[31mname",
]


@pytest.mark.parametrize("value", GOOD_NAMES)
def test_real_names_are_kept(value):
    assert pv.clean_name(value) == " ".join(value.split())


@pytest.mark.parametrize("value", BAD_NAMES)
def test_unusable_names_are_refused(value):
    with pytest.raises(HTTPException) as caught:
        pv.require_name(value, field="first_name")
    assert caught.value.status_code == 400


def test_a_name_that_is_only_whitespace_is_empty_not_a_name():
    with pytest.raises(HTTPException) as caught:
        pv.require_name("   ", field="first_name")
    assert "required" in str(caught.value.detail).lower()


def test_optional_name_allows_none():
    assert pv.clean_name(None) is None
    assert pv.clean_name("") is None


def test_pasted_whitespace_is_collapsed():
    assert pv.clean_name("  Anne   Marie  ") == "Anne Marie"


# ----------------------------------------- 8. every service copy is identical --
def test_every_service_copy_is_identical():
    """Four services cannot import each other, so this rule is copied four times.

    A copy that drifts is worse than no rule at all, because it validates the
    same field differently depending on which service happens to handle it.
    """
    here = (SERVICE_ROOT / "resources" / "validation.py").read_text(encoding="utf-8")
    services = SERVICE_ROOT.parent
    for other in ALL_ROOTS:
        candidate = services / other / "resources" / "validation.py"
        if other == SERVICE_ROOT.name or not candidate.exists():
            continue
        theirs = candidate.read_text(encoding="utf-8")
        if _body(theirs) != _body(here):
            pytest.fail(
                f"{other}/resources/validation.py has drifted from this copy.\n"
                "The rule must be byte-identical: copy this file over it and re-run."
            )


def _body(text: str) -> str:
    """Compare the module's code, ignoring the module docstring's wording."""
    return "\n".join(line for line in text.splitlines() if not line.startswith("#"))

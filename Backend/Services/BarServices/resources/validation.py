"""Field validation this service enforces on every write.

    from resources.validation import normalize_phone, validate_email, clean_name

WHY THIS EXISTS
    Three separate mistakes, all found by auditing what the API actually accepted
    rather than what the form claimed:

    * Phone numbers were checked with `re.fullmatch(r"\\d{10}", value)` -- "ten
      digits" as a universal rule. That rejects every non-Indian guest, rejects
      anything typed in international format, and accepts ten digits belonging to
      no numbering plan. It also let the same number be stored three ways, so a
      uniqueness index and the guest lookup that joins on it could miss a match.
    * Email was checked with `"@" not in x or "." not in x`, which accepts
      `@.`, `a@b.`, `a b@c.d` and a 10KB string, and rejects nothing useful.
    * Names were length-checked only, so a name of control characters or a
      `<script>` payload passed.

    The rules are here, in one place, so a new endpoint inherits them by
    importing rather than by remembering.

WHAT VALIDATION PROVES, AND WHAT IT DOES NOT
    A phone number that passes is STRUCTURALLY valid for a real numbering plan
    and is stored canonically as E.164 (+14155552671). It is NOT proof that the
    number is assigned, reachable, or belongs to the person who typed it -- only
    an SMS/OTP verification can establish that, and this application has none.
    No error message here may imply otherwise.

SERVICES CANNOT IMPORT EACH OTHER
    This file is duplicated verbatim into every service that validates a field.
    `Backend/tests/test_phone_validation.py` asserts the copies are byte-identical,
    so "copied" cannot quietly become "diverged".
"""
from __future__ import annotations

import os
import re
import unicodedata

import phonenumbers
from fastapi import HTTPException
from phonenumbers import NumberParseException, PhoneNumberFormat, PhoneNumberType

# ===========================================================================
# Phone
# ===========================================================================
# The numbering plan used when a caller passes no region AND the property has
# deliberately configured one. Unset by default, so a national number is refused
# rather than guessed -- the safe answer for a hotel that takes guests from more
# than one country. Set DEFAULT_PHONE_REGION=IN in a service .env only for a
# property that is genuinely single-country.
DEFAULT_REGION = (os.getenv("DEFAULT_PHONE_REGION") or "").strip().upper() or None

# E.164 is at most 15 digits including the country code, and a national number
# needs at least 2. Anything longer is a paste accident or an attempt to make the
# parser work, and is refused before it sees a number.
MAX_INPUT_DIGITS = 20
MIN_NATIONAL_DIGITS = 2
# Below this many digits, no numbering plan has a number: too short is the
# answer whether or not a country was named.
MIN_PLAUSIBLE_DIGITS = 4

# Unicode decimal digits (full-width, Arabic-Indic, Devanagari, Tamil) are digits
# to a person typing them and noise to a parser. Fold them to ASCII first, so
# "९८७६५" is accepted the same as "98765".
_UNICODE_DIGITS = {d: str(i) for i, d in enumerate(range(0xFF10, 0xFF1A))}
_UNICODE_DIGITS.update({d: str(i) for i, d in enumerate(range(0x0660, 0x066A))})
_UNICODE_DIGITS.update({d: str(i) for i, d in enumerate(range(0x0966, 0x096F))})
_UNICODE_DIGITS.update({d: str(i) for i, d in enumerate(range(0x0BE6, 0x0BF0))})

# Separators a human legitimately types inside a number.
_SEPARATORS = re.compile(r"[\s\-()./  ]")


def _fold_digits(raw) -> str:
    """ASCII-fold Unicode digits and drop the separators people type."""
    text = unicodedata.normalize("NFKC", str(raw))
    text = "".join(_UNICODE_DIGITS.get(ch, ch) for ch in text)
    return _SEPARATORS.sub("", text)


def _fail(field: str, message: str, status: int = 400) -> HTTPException:
    """A 400 whose `detail` is written for the person filling the form in."""
    return HTTPException(status_code=status, detail=message)


def _pretty(field: str) -> str:
    return field.replace("_", " ").capitalize()


def normalize_phone(
    raw,
    *,
    field: str = "mobile",
    default_region: str | None = None,
    allow_mobile_only: bool = False,
) -> str | None:
    """Validate a phone number and return it in E.164 form.

    Returns ``None`` for empty input so optional fields stay optional. Raises
    HTTPException 400 with a specific, non-technical message otherwise.

    `allow_mobile_only` rejects landline-only ranges. A guest's or an employee's
    mobile should not accept a switchboard number; a venue's own contact field
    legitimately may, so it is a per-call decision rather than a global rule.
    """
    if raw is None:
        return None
    if not str(raw).strip():
        # Absent. A required field left empty is the caller's own check, and an
        # optional one stays optional.
        return None

    folded = _fold_digits(raw)
    region = (default_region or DEFAULT_REGION or "").strip().upper() or None

    if not folded:
        # Something WAS typed, and it was nothing but separators and spaces --
        # "-- --" or "( )". That is a filled-in field containing no number, which
        # is different from an empty one, and must not quietly become NULL: on
        # create, NULL then collides with the uniqueness filter and answers
        # "this mobile already exists" for a guest who has no mobile at all.
        raise _fail(field, f"{_pretty(field)} is required")

    # Separators are forgiven; anything else that is not a digit is not a typo
    # to absorb. `parse()` would extract the digits from "📞9876543210" and
    # store a number the user never typed, which is exactly the silent
    # correction a person cannot see. So the body of the number -- after the
    # "+" or the dialled-out "00" prefix -- must be digits and nothing else.
    body = folded
    if body.startswith("+"):
        body = body[1:]
    elif body.startswith("00"):
        body = body[2:]
    if not body.isdigit():
        raise _fail(
            field,
            f"{_pretty(field)} must contain digits only, for example +91 98765 43210",
        )

    digits = body
    if len(digits) > MAX_INPUT_DIGITS:
        raise _fail(field, f"{_pretty(field)} is too long to be a phone number")

    # Too few digits to be a number in ANY plan. Checked before the region and
    # before the parser, because the answer does not depend on either: telling
    # someone who has typed two digits to choose a country answers the wrong
    # question, and the parser would only produce a vaguer version of the same.
    if len(digits) < MIN_PLAUSIBLE_DIGITS:
        raise _fail(field, f"That {_pretty(field).lower()} is too short to be a phone number")

    # A leading 00 is the international access prefix as a phone dials it;
    # libphonenumber wants a '+'.
    if folded.startswith("00") and not folded.startswith("+"):
        folded = "+" + folded[2:]

    # A number with no country code is ambiguous, and guessing is worse than
    # refusing: with the region falling back to IN, "(415) 555-2671" parses as
    # +914155552671 -- ten digits that fit India's plan and belong to nobody.
    if not folded.startswith("+") and not region:
        raise _fail(
            field,
            f"Select the country for this {_pretty(field).lower()}, or enter the number "
            f"in international format such as +91 98765 43210",
        )

    try:
        parsed = phonenumbers.parse(folded, region)
    except NumberParseException:
        raise _fail(
            field,
            "Enter a valid phone number for the selected country, "
            "for example +91 98765 43210",
        ) from None

    if not phonenumbers.is_possible_number(parsed):
        national = phonenumbers.national_significant_number(parsed) or digits
        if len(national) < MIN_NATIONAL_DIGITS:
            raise _fail(field, f"That {_pretty(field).lower()} is too short")
        raise _fail(field, f"That {_pretty(field).lower()} is not a valid phone number")

    if not phonenumbers.is_valid_number(parsed):
        # Structurally fine, but the plan does not assign that range. The user
        # has a digit or a country wrong; a "format" message would not help.
        raise _fail(
            field,
            f"{_region_label(parsed, region)} does not have that phone number. Check the digits.",
        )

    if allow_mobile_only and phonenumbers.number_type(parsed) not in (
        PhoneNumberType.MOBILE,
        PhoneNumberType.FIXED_LINE_OR_MOBILE,
    ):
        raise _fail(field, f"{_pretty(field)} must be a mobile number")

    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)


def is_valid_phone(raw, *, default_region: str | None = None) -> bool:
    """Boolean form, for the places that filter rather than accept a write."""
    try:
        return normalize_phone(raw, default_region=default_region) is not None
    except HTTPException:
        return False


def display_phone(raw) -> str:
    """A readable rendering for a screen, from a stored E.164 value.

    Storage stays canonical; only the display is prettified, so one guest reads
    "+1 415-555-2671" at the bar and "+91 98765 43210" in the restaurant
    without the database ever holding a formatted string.
    """
    if not raw:
        return ""
    try:
        parsed = phonenumbers.parse(_fold_digits(raw), None)
    except NumberParseException:
        return str(raw)
    return phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)


def _region_label(parsed, fallback_region) -> str:
    """The country name for the number, so the message can name it."""
    code = phonenumbers.region_code_for_number(parsed) or fallback_region or ""
    try:
        return phonenumbers.geocoder.description_for_number(parsed, "en") or code
    except Exception:  # pragma: no cover - the geocoder is best-effort
        return code


# ===========================================================================
# Email
# ===========================================================================
# Deliberately not one clever regex. The rule is structural -- a local part, an
# @, a domain with at least one dot and a TLD of letters -- plus a length cap,
# which rejects the real mistakes (`a@b`, `@b.com`, `a b@c.com`, two @) and
# accepts what people actually type, including `user+tag@sub.example.co.uk` and
# internationalised addresses. Anything stricter starts refusing real addresses.
EMAIL_MAX = 254          # RFC 5321's practical limit for the whole address
EMAIL_LOCAL_MAX = 64     # and for the part before the @
EMAIL_MESSAGE = "Enter a valid email address, for example name@example.com"

_EMAIL_RE = re.compile(
    r"^[^\s@,;:<>()\[\]\\]+"          # local part: no whitespace or specials
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"  # dot-separated labels
    r"[A-Za-z]{2,63}$"                 # TLD, letters only
)


def validate_email(raw) -> bool:
    """Whether `raw` is a structurally valid, plausible email address."""
    if raw is None:
        return False
    value = unicodedata.normalize("NFKC", str(raw)).strip()
    if not value or len(value) > EMAIL_MAX:
        return False
    if value.count("@") != 1:          # missing, or more than one
        return False
    local, _, _domain = value.partition("@")
    if not local or len(local) > EMAIL_LOCAL_MAX:
        return False
    return bool(_EMAIL_RE.match(value))


def normalize_email(raw):
    """Trimmed and lower-cased for storage and comparison.

    Only the domain is case-insensitive by the standard, and the local part is
    case-sensitive in theory -- but every mainstream provider treats it
    case-insensitively, and a login that is case-sensitive for the domain half
    only produces support tickets. Case is folded on both halves so uniqueness
    and lookup behave the way users expect.
    """
    if raw is None:
        return None
    value = unicodedata.normalize("NFKC", str(raw)).strip().lower()
    return value or None


def require_email(raw, *, field: str = "email") -> str | None:
    """Validate and normalise, raising a 400 with readable copy."""
    if raw is None or not str(raw).strip():
        return None
    if not validate_email(raw):
        raise HTTPException(status_code=400, detail=EMAIL_MESSAGE)
    return normalize_email(raw)


# ===========================================================================
# Names
# ===========================================================================
NAME_MAX = 100
# Control characters that are never part of a name. Tab, newline and the Unicode
# line/paragraph separators are excluded on purpose: `clean_name` collapses
# whitespace before this check, so "Anne<tab>Marie" is already a well-formed name
# by the time it gets here, and rejecting it would refuse a paste rather than
# clean it. A name is not markup -- React escapes what it renders -- but a name
# is not the place to store a payload either, and a NUL byte in a MySQL string
# column is a truncation bug waiting to happen.
_CONTROL_CHARS = re.compile(
    "[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\u2028\u2029\ufeff\ufffe\uffff]"
)


def clean_name(raw, *, field: str = "name", required: bool = False) -> str | None:
    """Normalise a personal or business name.

    Accepts what people are actually called -- spaces, hyphens, apostrophes and
    non-Latin scripts -- because a name field that rejects "José", "O'Brien" or
    "मीरा" is broken for most of the world. Rejects only what is wrong
    everywhere: empty, too long, or carrying control characters.
    """
    if raw is None:
        if required:
            raise HTTPException(status_code=400, detail=f"{_pretty(field)} is required")
        return None
    # Collapse the whitespace a paste leaves behind, and strip the ends.
    value = unicodedata.normalize("NFC", str(raw))
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        if required:
            raise HTTPException(status_code=400, detail=f"{_pretty(field)} is required")
        return None
    if len(value) > NAME_MAX:
        raise HTTPException(
            status_code=400,
            detail=f"{_pretty(field)} must not exceed {NAME_MAX} characters",
        )
    if _CONTROL_CHARS.search(value):
        raise HTTPException(
            status_code=400,
            detail=f"{_pretty(field)} contains characters that cannot be stored",
        )
    return value


def require_name(raw, *, field: str = "name") -> str:
    """`clean_name` for a field the endpoint cannot do without."""
    value = clean_name(raw, field=field, required=True)
    return value  # type: ignore[return-value]

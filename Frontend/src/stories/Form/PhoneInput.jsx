/**
 * PhoneInput -- a country selector next to the number, validated by
 * libphonenumber, submitting E.164.
 *
 * WHY THIS EXISTS
 *   Every phone field in the product was a bare `<Input type="tel">` and the API
 *   checked "exactly ten digits". That combination rejects every non-Indian
 *   number, rejects anything typed in international format, and stores the same
 *   number differently depending on who typed it -- `+91 98765 43210`,
 *   `09876543210` and `098765 43210` are three rows to a uniqueness index that
 *   thinks they are four.
 *
 *   So: the user picks (or is shown) a country, types the number the way that
 *   country writes it, and the field hands the parent ONE canonical string --
 *   `+919876543210`. Display can be pretty; storage is not.
 *
 * WHY THE LIBRARY AND NOT A REGEX
 *   Numbering plans are data, not patterns: national lengths, trunk prefixes,
 *   mobile ranges and landline shapes all differ per country, and they change.
 *   libphonenumber is the maintained dataset, shared with the backend's
 *   `phonenumbers`, so the two agree on what is valid instead of drifting.
 *
 * WHAT IT DOES NOT DO
 *   It proves the number is structurally valid for a real plan. It does not
 *   prove the number is assigned, reachable, or the caller's -- only an SMS
 *   verification can, and this application has none. The helper text therefore
 *   never claims a number "works", and the error copy says what is wrong with
 *   the format rather than implying the line is dead.
 *
 * THE RULES LIVE IN ./phone
 *   `validatePhone`, `regionOf` and the rest are pure functions with no React in
 *   them, so four forms can validate without importing a component, and this
 *   file exports exactly one thing (which is also what keeps Fast Refresh
 *   working). See phone.js.
 *
 * USAGE
 *   <PhoneInput
 *     label="Mobile"
 *     required
 *     value={form.mobile}                 // canonical E.164, or ""
 *     region={form.phone_region}          // ISO-2, e.g. "IN"
 *     onChange={(e164, region, result) => ...}   // all three handed up
 *     error={Boolean(phoneError)}
 *     helperText={phoneError}   // omit it and the component shows the
 *                                // selected country's own example
 *   />
 *   The parent stores `e164` in the field the API expects and sends `region`
 *   alongside it, because a national number with no country is ambiguous and
 *   the API refuses to guess one.
 */
import React, { useEffect, useMemo, useRef, useState } from "react";
import { AsYouType } from "libphonenumber-js";
import { ChevronDown } from "lucide-react";
import {
  DEFAULT_REGION,
  PINNED,
  REST_OF_THE_WORLD,
  callingCode,
  countryLabel,
  nationalPlaceholder,
  storedExample,
  toNational,
  validatePhone,
} from "./phone";
import "./Input.css";
import "./PhoneInput.css";

const PhoneInput = ({
  label: fieldLabel = "Phone",
  required = false,
  value = "",
  region: regionProp,
  onChange,
  onRegionChange,
  disabled = false,
  error = false,
  helperText,
  className = "",
  name = "phone",
  id,
}) => {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef(null);
  const region = regionProp || DEFAULT_REGION;

  /**
   * The number is shown in national format for the selected country, so the
   * user types what their country writes. `value` is canonical E.164 from the
   * API; converting on the way in is what lets an existing guest's stored
   * `+14155552671` appear as `(415) 555-2671` instead of a raw string.
   */
  const national = useMemo(() => toNational(value), [value]);

  /**
   * WHAT IS TYPED IS LOCAL STATE, AND IT HAS TO BE.
   *
   * The parent holds the canonical value, and a half-typed number has no
   * canonical value -- so pushing "" up on every incomplete keystroke made this a
   * controlled input whose value came straight back as "", and the field wiped
   * itself as the user typed. That is not a cosmetic bug: the number could not
   * be entered at all.
   *
   * So: what the user sees belongs here, and the parent receives only the
   * canonical string ("" while incomplete, which is what a required check
   * wants). The parent's value is adopted only when it is something this
   * component did not just produce -- opening a record, or clearing the form.
   */
  const [digits, setDigits] = useState(national);
  const lastEmitted = useRef("");

  useEffect(() => {
    if (value !== lastEmitted.current) {
      setDigits(national);
    }
    // `national` is derived from `value` and re-runs on every emission, so
    // depending on it would fight the user halfway through a number.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const publish = (formatted, regionCode) => {
    const result = validatePhone(formatted, regionCode);
    const e164 = result.ok ? result.e164 || "" : "";
    lastEmitted.current = e164;
    if (onChange) onChange(e164, regionCode, result);
  };

  const emit = (typed) => {
    // AsYouType formats as the user types, which is the formatting feedback
    // that makes an unfamiliar numbering plan legible.
    const formatter = new AsYouType(region);
    const formatted = typed ? formatter.input(typed) : "";
    setDigits(formatted);
    publish(formatted, region);
  };

  const choose = (code) => {
    setOpen(false);
    if (onRegionChange) onRegionChange(code);
    // Re-format and re-validate under the new country rather than keeping the
    // old reading: the same digits can be a different number, or not a number
    // at all, once the country changes.
    if (digits) {
      const refilled = new AsYouType(code).input(digits);
      setDigits(refilled);
      publish(refilled, code);
    } else {
      lastEmitted.current = value;
    }
  };

  return (
    <div className={`phone-field ${className}`.trim()} ref={wrapRef}>
      <span className="phone-field__label" id={`${id || name}-label`}>
        {fieldLabel}
        {required ? <span aria-hidden="true" className="phone-field__req"> *</span> : null}
      </span>

      <div className={`phone-field__row ${error ? "is-error" : ""}`.trim()}>
        <div className="phone-field__country">
          <button
            type="button"
            className="phone-field__country-button"
            onClick={() => setOpen((v) => !v)}
            disabled={disabled}
            aria-haspopup="listbox"
            aria-expanded={open}
            aria-label={`Country: ${countryLabel(region)}. Change`}
          >
            <span className="phone-field__code">+{callingCode(region)}</span>
            <span className="phone-field__region">{region}</span>
            <ChevronDown size={14} aria-hidden="true" />
          </button>
          {open ? (
            <ul className="phone-field__list" role="listbox" aria-label="Choose a country">
              <li className="phone-field__list-head" aria-hidden="true">Common</li>
              {PINNED.map((code) => (
                <li key={`pin-${code}`}>
                  <button type="button" role="option" aria-selected={code === region}
                    onClick={() => choose(code)}>
                    {countryLabel(code)} <span className="phone-field__code">+{callingCode(code)}</span>
                  </button>
                </li>
              ))}
              {/* The rest of the countries, NOT the common ones again. The two
                  lists used to both render every pinned country, so the listbox
                  offered "United Kingdom" twice and a screen reader announced it
                  twice -- which also made the country ambiguous to pick from. */}
              <li className="phone-field__list-sep" aria-hidden="true">All other countries</li>
              {REST_OF_THE_WORLD.map((code) => (
                <li key={code}>
                  <button type="button" role="option" aria-selected={code === region}
                    onClick={() => choose(code)}>
                    {countryLabel(code)} <span className="phone-field__code">+{callingCode(code)}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>

        <input
          className="phone-field__input"
          type="tel"
          inputMode="tel"
          autoComplete="tel-national"
          name={name}
          value={digits}
          disabled={disabled}
          placeholder={nationalPlaceholder(region) || "Phone number"}
          aria-labelledby={`${id || name}-label`}
          aria-invalid={error || undefined}
          onChange={(e) => emit(e.target.value)}
          onPaste={(e) => {
            // Pasted text may be formatted or carry a country code. Hand it to
            // the same path as typing, so a paste cannot bypass validation.
            const text = (e.clipboardData || window.clipboardData).getData("text");
            if (text) {
              e.preventDefault();
              emit(text);
            }
          }}
        />
      </div>

      {/* The example follows the selected country, so the hint can never
          contradict the selector above it. A hint that says "+91 98765 43210"
          on a form set to United Kingdom reads as the expected format, and is
          a format the API would then refuse. */}
      <span className="phone-field__hint">
        {helperText || `Stored as ${storedExample(region)}`}
      </span>
    </div>
  );
};

export default PhoneInput;

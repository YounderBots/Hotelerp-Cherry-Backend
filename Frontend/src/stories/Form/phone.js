/**
 * The phone rules, as pure functions with no React in them.
 *
 * WHY THIS IS NOT IN PhoneInput.jsx
 *   Two reasons, and the second is the real one.
 *
 *   First, these are logic, not chrome: four screens validate with them and one
 *   renders with them, so a form that only needs the rule (a booking, an
 *   employee record) should not have to import a component to get it.
 *
 *   Second, the lint rule is right. A file that exports both a component and
 *   plain functions breaks Fast Refresh -- the rule exists so a hot update
 *   cannot leave the page running half-old code -- and a file whose exports are
 *   all values is not a component at all.
 *
 * IT AGREES WITH THE API
 *   `resources/validation.py` on the server is the same rule in Python, over the
 *   same libphonenumber metadata. Both are country-aware, both store E.164, and
 *   both refuse a national number with no country rather than guessing one. The
 *   browser is a convenience; the server is the rule.
 */
import { getCountries, getCountryCallingCode, parsePhoneNumberFromString } from "libphonenumber-js";

/** Every country libphonenumber knows (245), for the selector. */
export const ALL_COUNTRIES = getCountries();

/**
 * The countries a property is most likely to need, so the common case is one
 * click. The list is still every country; this only orders and previews them.
 */
export const PINNED = ["IN", "US", "GB", "AE", "SA", "QA", "KW", "BH", "OM", "SG", "MU"];

/**
 * Every country except the common ones.
 *
 * The selector shows a "Common" group and then the rest, and the two must not
 * overlap: rendering both lists in full offered "United Kingdom" twice, which
 * made the list ambiguous to a person and announced twice to a screen reader.
 */
export const REST_OF_THE_WORLD = ALL_COUNTRIES.filter((code) => !PINNED.includes(code));

const COUNTRY_NAMES = {
  IN: "India", US: "United States", GB: "United Kingdom", AE: "United Arab Emirates",
  SA: "Saudi Arabia", QA: "Qatar", KW: "Kuwait", BH: "Bahrain", OM: "Oman",
  SG: "Singapore", MU: "Mauritius",
};

export const DEFAULT_REGION = "IN";

/** A readable country name, falling back to the code for the long tail. */
export const countryLabel = (code) => COUNTRY_NAMES[code] || code;

export const callingCode = (region) => getCountryCallingCode(region || DEFAULT_REGION);

/**
 * The country a stored number belongs to, so an edit form can show it in the
 * selector instead of assuming the property's own country. Without this, a guest
 * from abroad opens their record and the field re-reads their number as local --
 * which is how a good record gets corrupted by being opened.
 */
export const regionOf = (value) => {
  if (!value) return null;
  const parsed = parsePhoneNumberFromString(String(value));
  return parsed ? parsed.country || null : null;
};

/**
 * The digits to show in the input for a stored canonical value.
 *
 * Kept here with the other rules because it is the same parse: the field holds
 * E.164 (one spelling, so uniqueness and lookup work) and shows national
 * (readable), and the two must not drift apart.
 */
export const toNational = (value) => {
  if (!value) return "";
  const text = String(value);
  if (!text.startsWith("+")) return text;
  const parsed = parsePhoneNumberFromString(text);
  return parsed ? parsed.nationalNumber : text;
};

/** A stored E.164 number as the country writes it, for display. */
export const displayAsNational = (value) => {
  if (!value) return "";
  const parsed = parsePhoneNumberFromString(String(value));
  return parsed ? parsed.formatNational() : String(value);
};

/**
 * @returns {{ ok: boolean, e164?: string, message?: string, possible?: boolean,
 *             incomplete?: boolean, empty?: boolean }}
 *
 *   { ok: true, empty }              nothing typed; an optional field is fine
 *   { ok: false, incomplete: true }  still typing -- do NOT paint an error yet
 *   { ok: false, possible: false }   cannot be a number of that length at all
 *   { ok: false, possible: true }    well-formed, but the plan does not assign
 *                                   it: a digit, or the country, is wrong
 *   { ok: true, e164 }               good, and this is what gets stored
 *
 * The four-way split is the point. A user halfway through a number needs no
 * red box; a user who has finished typing a number that no plan assigns needs to
 * be told WHICH country refused it, because the fix is a different digit or a
 * different country, and a generic "invalid" gives them nothing to act on.
 */
export const validatePhone = (value, region) => {
  const raw = String(value ?? "").trim();
  if (!raw) return { ok: true, empty: true };

  const parsed = parsePhoneNumberFromString(raw, region || DEFAULT_REGION);
  if (!parsed) {
    // Too few digits to be a number yet. Flagged `incomplete` so a form does not
    // paint an error under a field the user is still halfway through.
    return {
      ok: false,
      incomplete: true,
      possible: false,
      message: "That is not a complete phone number yet.",
    };
  }

  // Which country the number reads as. The parsed country wins when the number
  // carried its own code; otherwise it is the one the user selected.
  const country = parsed.country || region || DEFAULT_REGION;

  if (!parsed.isPossible()) {
    return {
      ok: false,
      possible: false,
      // No article before the country name: "a India" is wrong, and picking
      // between "a" and "an" per country is not worth a demonym table.
      message: `That is only ${parsed.nationalNumber.length} digits so far, not a complete ${countryLabel(country)} number.`,
    };
  }
  if (!parsed.isValid()) {
    return {
      ok: false,
      possible: true,
      message: `${countryLabel(country)} does not assign that number. Check the digits or choose another country.`,
    };
  }
  return { ok: true, e164: parsed.number };
};

/**
 * A stored-form example for a country, E.164, for the helper text.
 *
 * WHY NOT A FIXED ONE
 *   The hint used to read "e.g. +91 98765 43210" on every screen, including a
 *   form where the country selector said United Kingdom -- so the example
 *   contradicted the field it was explaining. An example that names the wrong
 *   country is worse than none, because a user reads it as the expected format.
 */
const STORED_EXAMPLES = {
  IN: "+91 98765 43210", US: "+1 415-555-2671", GB: "+44 20 7946 0958",
  AE: "+971 50 123 4567", SA: "+966 50 123 4567", QA: "+974 3312 3456",
  KW: "+965 5012 3456", BH: "+973 3600 1234", OM: "+968 9212 3456",
  SG: "+65 8123 4567", MU: "+230 5251 2345",
};

/** The example for this country, or a neutral one if it has none. */
export const storedExample = (region) =>
  STORED_EXAMPLES[region || DEFAULT_REGION] || "in international format, e.g. +44 20 7946 0958";

/** The digits a country writes locally, ready to be typed or pasted into. */
export const nationalPlaceholder = (region) => {
  const example = {
    IN: "98765 43210", US: "(415) 555-2671", GB: "020 7946 0958",
    AE: "50 123 4567", SG: "8123 4567", SA: "50 123 4567", QA: "3312 3456",
    KW: "5012 3456", BH: "3600 1234", OM: "9212 3456", MU: "5251 2345",
  }[region];
  return example || "";
};

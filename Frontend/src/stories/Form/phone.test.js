import { describe, expect, it } from "vitest";

import {
  displayAsNational,
  nationalPlaceholder,
  regionOf,
  storedExample,
  validatePhone,
} from "./phone";

// The rules the browser and the backend must agree on. The backend half of the
// same matrix is Backend/tests/test_phone_validation.py, and the two use the
// same libphonenumber metadata, so a case here and a case there answer alike.

describe("validatePhone", () => {
  it("accepts a national number for the selected country", () => {
    expect(validatePhone("9876543210", "IN")).toMatchObject({ ok: true, e164: "+919876543210" });
    expect(validatePhone("(415) 555-2671", "US")).toMatchObject({ ok: true, e164: "+14155552671" });
    expect(validatePhone("020 7946 0958", "GB")).toMatchObject({ ok: true, e164: "+442079460958" });
  });

  it("accepts the same number in any of the forms people type it", () => {
    const forms = ["9876543210", "+91 98765 43210", "09876543210", "+91-98765-43210"];
    for (const form of forms) {
      expect(validatePhone(form, "IN").e164).toBe("+919876543210");
    }
  });

  it("accepts an international number whatever the selector says", () => {
    expect(validatePhone("+971501234567", "IN").ok).toBe(true);
    expect(validatePhone("+442079460958", "US").e164).toBe("+442079460958");
  });

  it("marks a half-typed number as incomplete rather than invalid", () => {
    // A form must not paint an error under a field the user is still typing.
    const result = validatePhone("1", "IN");
    expect(result.ok).toBe(false);
    expect(result.incomplete).toBe(true);
    expect(result.possible).toBe(false);
  });

  it("rejects a number that is too short for its country", () => {
    const result = validatePhone("12", "IN");
    expect(result.ok).toBe(false);
    expect(result.possible).toBe(false);
  });

  it("distinguishes an impossible number from an unassigned one", () => {
    // Ten digits that fit no US range, but are the right length.
    const unassigned = validatePhone("9876543210", "US");
    expect(unassigned.ok).toBe(false);
    expect(unassigned.possible).toBe(true);
    expect(unassigned.incomplete).toBeUndefined();
    expect(unassigned.message).toMatch(/does not assign|choose another country/i);

    // Parsed, but the length is impossible for the plan.
    const impossible = validatePhone("+9198765", "IN");
    expect(impossible.ok).toBe(false);
    expect(impossible.possible).toBe(false);
  });

  it("names the country in the message so the user knows what to change", () => {
    expect(validatePhone("9876543210", "US").message).toMatch(/United States/i);
    expect(validatePhone("+4420796", "GB").message).toMatch(/United Kingdom/i);
  });

  it("treats empty input as empty, not invalid", () => {
    for (const value of ["", "   ", null, undefined]) {
      expect(validatePhone(value, "IN")).toMatchObject({ ok: true, empty: true });
    }
  });

  it("never returns a raw library message", () => {
    const bad = [validatePhone("abc", "IN"), validatePhone("+999123456789", "IN")];
    for (const result of bad) {
      expect(result.ok).toBe(false);
      expect(result.message).not.toMatch(/phonenumber|parse|NaN|undefined/i);
    }
  });

  it("does not silently accept a number pasted for a different country", () => {
    // A UK number typed while the selector says India must not be stored as the
    // Indian reading of those digits.
    const asIndia = validatePhone("02079460958", "IN");
    if (asIndia.ok) {
      expect(asIndia.e164).not.toBe("+442079460958");
    } else {
      expect(asIndia.message).toBeTruthy();
    }
  });

  it("strips formatting before checking, so pasted text is accepted", () => {
    expect(validatePhone("+1 (415) 555-2671", "US").e164).toBe("+14155552671");
    expect(validatePhone("  +44 20 7946 0958  ", "GB").e164).toBe("+442079460958");
  });
});

describe("regionOf", () => {
  it("reads the country off a stored E.164 number", () => {
    // This is what an edit form uses to show a guest's real country instead of
    // assuming the property's own.
    expect(regionOf("+14155552671")).toBe("US");
    expect(regionOf("+919876543210")).toBe("IN");
    expect(regionOf("+442079460958")).toBe("GB");
  });

  it("returns null for nothing usable rather than guessing", () => {
    expect(regionOf("")).toBeNull();
    expect(regionOf(null)).toBeNull();
    expect(regionOf("not a number")).toBeNull();
  });
});

describe("displayAsNational", () => {
  it("shows a stored number the way its country writes it", () => {
    expect(displayAsNational("+14155552671")).toBe("(415) 555-2671");
  });

  it("passes anything unparseable through untouched", () => {
    expect(displayAsNational("")).toBe("");
    expect(displayAsNational("legacy-10-digit")).toBe("legacy-10-digit");
  });
});

describe("storedExample", () => {
  it("gives an example in the selected country's own format", () => {
    // The hint used to read "+91 98765 43210" everywhere, including a form set
    // to the United Kingdom -- where a user would read it as the expected
    // format and be refused by the API.
    expect(storedExample("IN")).toMatch(/^\+91 /);
    expect(storedExample("GB")).toMatch(/^\+44 /);
    expect(storedExample("AE")).toMatch(/^\+971 /);
  });

  it("falls back to a real country's example rather than nothing", () => {
    // Never empty, and never an example the API would refuse. Zimbabwe has no
    // entry, so it takes the generic fallback.
    expect(storedExample("ZW")).toMatch(/in international format, e\.g\. \+\d/);
    for (const region of ["IN", "US", "GB", "AE", "SG", "ZW", undefined]) {
      const example = storedExample(region);
      expect(example).toBeTruthy();
      expect(example).toMatch(/\+\d/);
    }
  });
});

describe("nationalPlaceholder", () => {
  it("shows a number in the shape the country writes", () => {
    expect(nationalPlaceholder("US")).toBe("(415) 555-2671");
    expect(nationalPlaceholder("IN")).toBe("98765 43210");
  });

  it("returns an empty string for a country with no example", () => {
    expect(nationalPlaceholder("ZZ")).toBe("");
  });

  it("never offers a fiction-range number as the example", () => {
    // "+1 555 123 4567" was the placeholder on the booking form, and 555 is
    // reserved for fiction: anyone who copied it was refused by the API.
    for (const region of ["IN", "US", "GB", "AE", "SG"]) {
      const example = nationalPlaceholder(region);
      if (example) expect(example).not.toMatch(/555\s?123\s?4567/);
    }
  });
});

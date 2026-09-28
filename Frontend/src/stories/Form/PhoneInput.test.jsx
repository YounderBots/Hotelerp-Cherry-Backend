// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import React, { useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import PhoneInput from "./PhoneInput";

afterEach(() => cleanup());

// Component behaviour, not the rules -- phone.test.js covers those. Every test
// here exists because the pure function could not see it, and the first one
// exists because the bug it guards was invisible to a unit test: the field was
// clearing itself as the user typed, so the number could not be entered at all.

/**
 * A real parent, holding the canonical value and handing it back down. The
 * "wipe" bug only appears when the child is controlled by a value that is
 * briefly empty, so the harness has to be that parent rather than a mock.
 */
const Harness = ({ initial = "", initialRegion = "IN", onChange, ...rest }) => {
  const [value, setValue] = useState(initial);
  const [region, setRegion] = useState(initialRegion);
  return (
    <PhoneInput
      label="Mobile"
      name="mobile"
      value={value}
      region={region}
      onChange={(e164, nextRegion, result) => {
        setValue(e164);
        setRegion(nextRegion);
        onChange(e164, nextRegion, result);
      }}
      {...rest}
    />
  );
};

const setup = (props = {}) => {
  const onChange = vi.fn();
  const utils = render(<Harness onChange={onChange} {...props} />);
  return { ...utils, onChange, input: screen.getByRole("textbox") };
};

const countryButton = (name) => screen.getByRole("button", { name });
const pickCountry = (optionName) => {
  fireEvent.click(countryButton(/country:/i));
  fireEvent.click(screen.getByRole("option", { name: optionName }));
};

describe("PhoneInput", () => {
  it("keeps what the user typed, character by character", () => {
    // THE REGRESSION. The parent receives "" for a half-typed number -- it has
    // no canonical value yet -- and an input bound to that value cleared itself
    // on every keystroke, so the number could not be entered at all.
    //
    // The invariant is the DIGITS, not the exact string: the field also
    // formats as you type, which is the point of it, so "98765 4" after six
    // keystrokes is correct. Wiping to "" is not.
    const digitsIn = (text) => text.replace(/\D/g, "");
    const { input } = setup();
    for (const partial of ["9", "98", "987", "9876", "98765", "987654", "9876543"]) {
      fireEvent.change(input, { target: { value: partial } });
      expect(digitsIn(input.value)).toBe(partial);
      expect(input.value).not.toBe("");
    }
  });

  it("formats as the country types, and hands up E.164", () => {
    const { input, onChange } = setup();
    fireEvent.change(input, { target: { value: "9876543210" } });
    expect(input.value).toBe("98765 43210");
    expect(onChange).toHaveBeenLastCalledWith(
      "+919876543210",
      "IN",
      expect.objectContaining({ ok: true }),
    );
  });

  it("shows a stored number in its own country's format", () => {
    const { input } = setup({ initial: "+14155552671" });
    expect(input.value).toBe("4155552671");
  });

  it("re-validates the digits under the new country instead of keeping the old number", () => {
    // The number on screen is a US one, shown as US digits. Choosing the UK
    // does NOT turn it into a London number -- a London number has entirely
    // different digits -- so what must happen is that the digits stay visible
    // and are reported as not being a British number, rather than being
    // silently re-read, wiped, or submitted under the old country's identity.
    const { onChange, input } = setup({ initial: "+14155552671" });
    expect(input.value).toBe("4155552671");

    pickCountry(/United Kingdom/i);

    expect(onChange).toHaveBeenLastCalledWith(
      "",                                    // nothing canonical to store
      "GB",                                  // under the country now selected
      expect.objectContaining({ ok: false }),
    );
    // The typed digits are still there for the person to correct.
    expect(input.value.replace(/\D/g, "")).toBe("4155552671");
  });

  it("re-validates rather than keeping the old reading when the country changes", () => {
    // Valid as a UAE number; the same digits are not an Indian one, and the
    // field must report that instead of submitting the number it already had.
    const { onChange } = setup({ initial: "+971501234567" });
    expect(onChange).not.toHaveBeenCalled();

    pickCountry(/^India/i);
    expect(onChange).toHaveBeenLastCalledWith(
      "",
      "IN",
      expect.objectContaining({ ok: false }),
    );
  });

  it("does not paint an error under a field still being typed", () => {
    const { input } = setup();
    fireEvent.change(input, { target: { value: "9876" } });
    expect(screen.queryByText(/cannot be right|not a complete/i)).toBeNull();
  });

  it("shows the parent's message beside the field", () => {
    const message = "India does not assign that number. Check the digits.";
    setup({ helperText: message });
    expect(screen.getByText(message)).toBeTruthy();
  });

  it("names the country on the selector and offers every country", () => {
    setup();
    const button = countryButton(/country: india/i);
    expect(button.textContent).toContain("+91");

    fireEvent.click(button);
    const list = screen.getByRole("listbox", { name: /choose a country/i });
    // Every country libphonenumber knows, not a shortlist: a hotel's guests are
    // not all local, which is the whole reason this field exists.
    expect(within(list).getAllByRole("option").length).toBeGreaterThan(200);
  });

  it("accepts a pasted international number through the same rule", () => {
    // A paste must not bypass validation the way it would on a raw <input>.
    const { onChange } = setup();
    fireEvent.paste(screen.getByRole("textbox"), {
      clipboardData: { getData: () => "+1 (415) 555-2671" },
    });
    expect(onChange).toHaveBeenLastCalledWith(
      "+14155552671",
      "IN",
      expect.objectContaining({ ok: true }),
    );
  });

  it("adopts a value the parent sets from outside", () => {
    // Opening a record, or clicking a different row while the form stays open:
    // the parent supplies a stored E.164 number and the field shows it in that
    // country's national format. Without this, an edit form would show a raw
    // "+442079460958", or re-read a guest's number as the property's country --
    // which is how a good record gets corrupted by being opened.
    //
    // Driven straight from a prop, not through useState, because the question is
    // whether the field re-reads a value the PARENT changed.
    const { rerender } = render(<PhoneInput label="Mobile" name="mobile" value="+442079460958" region="GB" onChange={() => {}} />);
    expect(screen.getByRole("textbox").value).toBe("2079460958");

    rerender(<PhoneInput label="Mobile" name="mobile" value="+14155552671" region="US" onChange={() => {}} />);
    expect(screen.getByRole("textbox").value).toBe("4155552671");
  });
});

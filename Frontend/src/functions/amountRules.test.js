import { describe, expect, it } from "vitest";
import { amountError, parseAmount } from "./amountRules";

describe("parseAmount", () => {
  it("reads a real number", () => {
    expect(parseAmount("12.5")).toBe(12.5);
    expect(parseAmount(0)).toBe(0);
  });

  it("treats an empty field as absent, not as zero", () => {
    expect(parseAmount("")).toBeNull();
    expect(parseAmount("   ")).toBeNull();
    expect(parseAmount(null)).toBeNull();
    expect(parseAmount(undefined)).toBeNull();
  });

  it("reports text that is not a number as NaN rather than as absent", () => {
    expect(Number.isNaN(parseAmount("1,500"))).toBe(true);
    expect(Number.isNaN(parseAmount("abc"))).toBe(true);
  });
});

describe("amountError", () => {
  it("accepts zero and positive values", () => {
    expect(amountError("0", { label: "Price" })).toBeNull();
    expect(amountError("199.99", { label: "Price" })).toBeNull();
  });

  it("rejects a negative price, which is what a number input lets you type", () => {
    expect(amountError("-50", { label: "Price" })).toBe("Price cannot be negative.");
    expect(amountError("-18", { label: "Tax %", max: 100 })).toBe("Tax % cannot be negative.");
  });

  it("keeps a percentage inside its own range", () => {
    expect(amountError("18", { label: "Tax %", max: 100 })).toBeNull();
    expect(amountError("140", { label: "Tax %", max: 100 })).toBe("Tax % cannot be more than 100.");
  });

  it("says the field is required only when it is asked for", () => {
    expect(amountError("", { label: "Price", required: true })).toBe("Price is required.");
    expect(amountError("", { label: "Cost price" })).toBeNull();
  });

  it("distinguishes 'not a number' from 'empty'", () => {
    expect(amountError("1,500", { label: "Price", required: true })).toBe("Price must be a number.");
  });
});

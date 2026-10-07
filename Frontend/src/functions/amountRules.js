/**
 * Rules for the money and percentage fields on a form.
 *
 * WHY THIS EXISTS
 *   `<input type="number">` will happily take a leading minus, and a form that
 *   only checks "the field is not empty" will send `-50` as a price and `-18`
 *   as a tax rate. The menu screen did exactly that: `price: Number(price)` on
 *   submit, no floor anywhere, so a negative price reached the API and could
 *   end up printed on a bill.
 *
 *   The check is a pure function rather than JSX so every screen that has a
 *   price defines "a price a till can print" the same way, and so the rule can
 *   be tested without rendering a form. See amountRules.test.js.
 */

/**
 * Read a form field as a number without lying about what it holds.
 *
 * @param {string|number|null|undefined} raw the field's raw value
 * @returns {number|null} the number, `null` when the field is empty (so an
 *   optional field stays optional) and `NaN` when the text is not a number at
 *   all — kept distinct from "empty", because "1,500" is a mistake the user
 *   must be told about, not a field they forgot to fill in.
 */
export const parseAmount = (raw) => {
  if (raw === null || raw === undefined) return null;
  const text = String(raw).trim();
  if (text === "") return null;
  const value = Number(text);
  return Number.isFinite(value) ? value : NaN;
};

/**
 * The message to print under a field, or `null` when the value is acceptable.
 *
 * @param {string|number|null|undefined} raw the field's raw value
 * @param {object} spec
 * @param {string} spec.label      field name as the user reads it, e.g. "Price"
 * @param {number} [spec.min=0]    lowest accepted value
 * @param {number} [spec.max]      highest accepted value, when the field has one
 * @param {boolean} [spec.required=false] reject an empty value as well
 * @returns {string|null}
 */
export const amountError = (raw, { label, min = 0, max, required = false } = {}) => {
  const value = parseAmount(raw);
  if (value === null) return required ? `${label} is required.` : null;
  if (Number.isNaN(value)) return `${label} must be a number.`;
  if (value < min) {
    return min > 0 ? `${label} must be at least ${min}.` : `${label} cannot be negative.`;
  }
  if (max !== undefined && value > max) return `${label} cannot be more than ${max}.`;
  return null;
};

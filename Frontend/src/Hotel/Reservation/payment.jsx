import React from "react";

/**
 * Billing panel for a reservation.
 *
 * WHAT CHANGED, AND WHY IT MATTERS
 *   This component used to be the pricing engine. It held the rate card
 *   lookup, multiplied it out over the stay, applied tax and discount, and
 *   posted the resulting `overall_amount` to the API as a plain form field --
 *   which the API stored without checking. The total of a booking was
 *   therefore decided in the browser, and anything that could send a form
 *   could name its own price.
 *
 *   It also got the arithmetic wrong. Its rate map spelled bed & breakfast
 *   `bed_and_breakfast_rate`; the master-data API returns `bed_breakfast_rate`.
 *   Choosing that rate looked up a field that was never there, so the room
 *   priced at zero and the guest was quoted tax on nothing.
 *
 *   Both problems have the same fix: the server prices the stay
 *   (POST /hotel/room_reservation_quote) and this panel renders what came
 *   back. There is no second implementation left to disagree with the first.
 *
 * WHAT IS STILL AN INPUT
 *   Tax and discount selection, extra charges, extra beds, a negotiated room
 *   amount, and how much the guest is paying now. Those are the front desk's
 *   decisions. Every figure derived FROM them is read-only, because a
 *   read-only field is an honest description of something the browser does
 *   not get a vote on.
 */

const money = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(2) : "0.00";
};

/** A derived figure. Never editable — the server owns it. */
const DerivedField = ({ label, value, tone = "", hint = "" }) => (
  <div className={`pay-field pay-field--derived ${tone}`}>
    <label>{label}</label>
    <output className="pay-derived-value">{money(value)}</output>
    {hint && <span className="pay-field-hint">{hint}</span>}
  </div>
);

const Payment = ({
  taxTypes = [],
  discountTypes = [],
  paymentMethods = [],
  // The operator-controlled half of the quote request.
  inputs = {},
  onInputChange,
  // The server's answer.
  quote = null,
  quoteLoading = false,
  quoteError = null,
}) => {
  const set = (field) => (event) => onInputChange(field, event.target.value);

  const lines = quote?.lines || [];

  return (
    <div className="pay-wrapper">
      {quoteError && (
        <div className="rmv-alert" role="alert">
          <span>{quoteError}</span>
        </div>
      )}

      {/* The rate card behind the room amount. Without it the guest sees one
          number and has to take it on trust. */}
      {lines.length > 0 && (
        <div className="pay-breakdown">
          <p className="pay-title">Room Charges</p>
          <div className="pay-breakdown-scroll">
            <table className="pay-breakdown-table">
              <thead>
                <tr>
                  <th scope="col">Room</th>
                  <th scope="col">Type</th>
                  <th scope="col">Rate</th>
                  <th scope="col" className="num">Per unit</th>
                  <th scope="col" className="num">Units</th>
                  <th scope="col" className="num">Amount</th>
                </tr>
              </thead>
              <tbody>
                {lines.map((line) => (
                  <tr key={line.room_id}>
                    <td>{line.room_no}</td>
                    <td>{line.room_type_name}</td>
                    <td className="pay-rate-label">
                      {String(line.rate_type || "").replace(/_/g, " ")}
                    </td>
                    <td className="num">{money(line.unit_rate)}</td>
                    <td className="num">{line.units}</td>
                    <td className="num">{money(line.line_total)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <th scope="row" colSpan={5}>
                    {quote?.nights} night{quote?.nights === 1 ? "" : "s"}
                  </th>
                  <td className="num">{money(quote?.computed_room_amount)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}

      <p className="pay-title">
        Charges {quoteLoading && <span className="pay-title-note">recalculating…</span>}
      </p>

      <div className="pay-grid">
        <div className="pay-field">
          <label htmlFor="pay-tax-type">Tax Type</label>
          <select
            id="pay-tax-type"
            value={inputs.tax_type_id ?? ""}
            onChange={set("tax_type_id")}
          >
            <option value="">No tax</option>
            {taxTypes.map((tax) => (
              <option key={tax.id} value={tax.id}>
                {tax.tax_name || tax.name} ({tax.tax_percentage}%)
              </option>
            ))}
          </select>
        </div>

        <DerivedField
          label="Tax Percentage"
          value={quote?.tax_percentage}
          hint="From Master Data → Tax"
        />
        <DerivedField label="Tax Amount" value={quote?.tax_amount} />

        <div className="pay-field">
          <label htmlFor="pay-discount-type">Discount Type</label>
          <select
            id="pay-discount-type"
            value={inputs.discount_type_id ?? ""}
            onChange={set("discount_type_id")}
          >
            <option value="">No discount</option>
            {discountTypes.map((discount) => (
              <option key={discount.id} value={discount.id}>
                {discount.discount_name || discount.name} ({discount.discount_percentage}%)
              </option>
            ))}
          </select>
        </div>

        <DerivedField
          label="Discount Percentage"
          value={quote?.discount_percentage}
          hint="From Master Data → Discount"
        />
        <DerivedField label="Discount Amount" value={quote?.discount_amount} />

        <div className="pay-field">
          <label htmlFor="pay-room-amount">Room Amount</label>
          <input
            id="pay-room-amount"
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            placeholder={money(quote?.computed_room_amount)}
            value={inputs.room_amount ?? ""}
            onChange={set("room_amount")}
          />
          <span className="pay-field-hint">
            {quote?.room_amount_overridden
              ? `Negotiated rate — card rate is ${money(quote?.computed_room_amount)}`
              : "Leave blank to use the rate card"}
          </span>
        </div>

        <div className="pay-field">
          <label htmlFor="pay-extra-charges">Extra Charges</label>
          <input
            id="pay-extra-charges"
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            placeholder="0.00"
            value={inputs.extra_charges ?? ""}
            onChange={set("extra_charges")}
          />
        </div>

        <div className="pay-field">
          <label htmlFor="pay-extra-bed-count">Extra Bed Count</label>
          <input
            id="pay-extra-bed-count"
            type="number"
            min="0"
            step="1"
            inputMode="numeric"
            value={inputs.extra_bed_count ?? ""}
            onChange={set("extra_bed_count")}
          />
        </div>

        <DerivedField
          label="Extra Bed Cost (per bed, whole stay)"
          value={quote?.extra_bed_cost}
          hint="From the room type's bed cost"
        />

        <DerivedField label="Taxable Amount" value={quote?.taxable_amount} />
        <DerivedField
          label="Overall Amount"
          value={quote?.overall_amount}
          tone="pay-field--total"
        />
      </div>

      <p className="pay-title">Payment Details</p>
      <div className="pay-grid">
        <div className="pay-field">
          <label htmlFor="pay-method">
            Payment Method <span className="required">*</span>
          </label>
          <select
            id="pay-method"
            value={inputs.payment_method_id ?? ""}
            onChange={set("payment_method_id")}
            required
          >
            <option value="">Select Payment Method</option>
            {paymentMethods.map((method) => (
              <option key={method.id} value={method.id}>
                {method.payment_method || method.name}
              </option>
            ))}
          </select>
        </div>

        <div className="pay-field">
          <label htmlFor="pay-paying-amount">Paying Now</label>
          <input
            id="pay-paying-amount"
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            placeholder="0.00"
            value={inputs.paying_amount ?? ""}
            onChange={set("paying_amount")}
          />
        </div>

        <DerivedField label="Paid Amount" value={quote?.paid_amount} tone="pay-field--paid" />
        <DerivedField
          label="Balance Amount"
          value={quote?.balance_amount}
          tone="pay-field--balance"
        />
        <DerivedField
          label="Refundable (overpaid)"
          value={quote?.extra_amount}
          hint={Number(quote?.extra_amount) > 0 ? "Paying more than the total" : ""}
        />
      </div>
    </div>
  );
};

export default Payment;

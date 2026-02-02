import Button from "../../stories/Button";

const Payment = () => {
  return (
    <div className="pay-wrapper">

      <div className="pay-header">
        <h2>Billing Details</h2>
      </div>

      <div className="pay-grid">

        <div className="pay-field">
          <label>Tax Type</label>
          <select>
            <option>Deluxe Room Offer</option>
            <option>Suite Room Discount</option>
            <option>Family Room Special</option>
            <option>Executive Room Promo</option>
            <option>Standard Room Deal</option>
          </select>
        </div>

        <div className="pay-field">
          <label>Discount Type</label>
          <select>
            <option>Early Bird Offer</option>
            <option>Long Stay Discount</option>
            <option>Seasonal Promotion</option>
            <option>Corporate Discount</option>
            <option>Returning Guest Offer</option>
          </select>
        </div>

        <div className="pay-field">
          <label>Extra Charges</label>
          <input type="number" placeholder="Enter extra charges" />
        </div>

        <div className="pay-field">
          <label>Room Amount</label>
          <input type="number" placeholder="Enter room amount" />
        </div>

        <div className="pay-field">
          <label>Tax Amount</label>
          <input type="text" placeholder="Auto calculated tax" />
        </div>

        <div className="pay-field">
          <label>Discount Amount</label>
          <input type="text" placeholder="Auto calculated discount" />
        </div>

        <div className="pay-field">
          <label>Extra Charges Amount</label>
          <input type="text" placeholder="Final extra charges amount" />
        </div>

        <div className="pay-field">
          <label>Overall Amount</label>
          <input type="text" placeholder="Total bill amount" />
        </div>

      </div>
      <p className="pay-title">Payment Details</p>
      <div className="pay-grid">

        <div className="pay-field">
          <label>Payment Mode</label>
          <select>
            <option>Cash</option>
            <option>Credit Card</option>
            <option>Debit Card</option>
            <option>UPI / QR Payment</option>
            <option>Bank Transfer</option>
          </select>
        </div>

        <div className="pay-field">
          <label>Paying Amount</label>
          <input type="text" placeholder="Enter paying amount" />
        </div>

        <div className="pay-field">
          <label>Balance Amount</label>
          <input type="text" placeholder="Remaining balance amount" />
        </div>

        <div className="pay-field">
          <label>Extra Amount</label>
          <input type="text" placeholder="Extra paid amount" />
        </div>

      </div>

      <Button className="pay-submit-btn">Submit</Button>
    </div>
  );
};

export default Payment;

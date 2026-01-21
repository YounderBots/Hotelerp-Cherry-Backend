

const Payment = () => {


    return (
        <div className="reservation-container">
            <div className="reservation-header">
                <h2>Billing Details</h2>
            </div>
            <div className="payment-Screen">
                <div>
                    <label>Tax Type</label>
                    <select>
                        <option>Deluxe Room Offer</option>
                        <option>Suite Room Discount</option>
                        <option>Family Room Special</option>
                        <option>Excutive Room Promo</option>
                        <option>Standard Room Deal</option>
                    </select>

                </div>

                <div>
                    <label>Discount Type</label>
                    <select>
                        <option>Early Bird Offer</option>
                        <option>Long Stay Discount</option>
                        <option>Seasonal Promotion</option>
                        <option>Corprate Discount</option>
                        <option>Returning Guest Offer</option>
                    </select>
                </div>


                <div>
                    <label>Extra Charges</label>
                    <input type="number"></input>
                </div>
                <div>
                    <label>Room Amount</label>
                    <input type="number"></input>
                </div>
                <div>
                    <label>Tax Amount</label>
                    <input type="text"></input>
                </div>
                <div>
                    <label>Discount Amount</label>
                    <input type="text"></input>
                </div>
                <div>
                    <label>Extra Charges Amount</label>
                    <input type="text"></input>
                </div>
                <div>
                    <label>Overall Amount</label>
                    <input type="text"></input>
                </div>

                <label>Payment Details</label>
                
                    

                    <div>
                        <label>Payment Mode</label>
                        <select>
                            <option>Cash</option>
                            <option>Credit Card</option>
                            <option>Debit Card</option>
                            <option>UPI / QR Payment</option>
                            <option>Bank Transfer</option>
                        </select>
                    </div>

                    <div>
                        <label>Paying Amount</label>
                        <input type="text"></input>
                    </div>
                    <div>
                        <label>Balance Amount</label>
                        <input type="text"></input>
                    </div>
                    <div>
                        <label>Extra Amount</label>
                        <input type="text"></input>
                    </div>

                </div>
            </div>

       


    )
}


export default Payment;
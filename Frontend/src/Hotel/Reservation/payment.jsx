import React, { useState, useEffect } from "react";
import Button from "../../stories/Button";

// Maps each selectable rate type (Card.jsx / AddNewReservation.jsx) to the
// matching per-night (or per-week) rate column on the room_types master record.
const RATE_FIELD = {
  daily: "daily_rate",
  weekly: "weekly_rate",
  bed_only: "bed_only_rate",
  bed_breakfast: "bed_and_breakfast_rate",
  half_board: "half_board_rate",
  full_board: "full_board_rate",
};

const Payment = ({
  taxTypes,
  discountTypes,
  paymentMethods,
  selectedRooms,
  roomTypes,
  perRoom = {},
  totalNights = 1,
  setpaymentData
}) => {
  const [paymentData, setPaymentData] = useState({
    tax_type_id: "",
    discount_type_id: "",
    extra_charges: 0,
    room_amount: 0,
    tax_percentage: 0,
    tax_amount: 0,
    discount_percentage: 0,
    discount_amount: 0,
    overall_amount: 0,
    payment_method_id: "",
    paying_amount: 0,
    paid_amount: 0,
    balance_amount: 0,
    extra_amount: 0,
    extra_bed_count: 0,
    extra_bed_cost: 0,
    total_amount: 0
  });

  // Recompute the room amount whenever the selected rooms, their chosen rate
  // type, or the stay length changes — weekly rates bill per week block,
  // every other rate type bills per night. Also suggests the extra-bed cost
  // (per bed, for the whole stay) from the first selected room's type — staff
  // can still override it by hand for negotiated rates.
  useEffect(() => {
    let total = 0;
    selectedRooms.forEach(room => {
      const roomType = roomTypes.find(t => Number(t.id) === Number(room.room_type_id));
      if (!roomType) return;
      const rateType = perRoom?.[room.id]?.rateType || "daily";
      const rateField = RATE_FIELD[rateType] || RATE_FIELD.daily;
      const rate = parseFloat(roomType[rateField]) || 0;
      const nights = Math.max(1, totalNights || 1);
      const units = rateType === "weekly" ? Math.ceil(nights / 7) : nights;
      total += rate * units;
    });

    const firstRoomType = selectedRooms[0]
      ? roomTypes.find(t => Number(t.id) === Number(selectedRooms[0].room_type_id))
      : null;
    const bedCostPerNight = parseFloat(firstRoomType?.bed_cost) || 0;
    const extraBedCost = bedCostPerNight * Math.max(1, totalNights || 1);

    setPaymentData(prev => ({ ...prev, room_amount: total, extra_bed_cost: extraBedCost }));
     
  }, [selectedRooms, roomTypes, perRoom, totalNights]);

  useEffect(() => {
    const roomAmount = paymentData.room_amount || 0;
    const extraCharges = paymentData.extra_charges || 0;
    const extraBedTotal = (paymentData.extra_bed_count || 0) * (paymentData.extra_bed_cost || 0);
    const taxableAmount = roomAmount + extraCharges + extraBedTotal;

    const taxAmount = taxableAmount * (paymentData.tax_percentage || 0) / 100;
    const discountAmount = taxableAmount * (paymentData.discount_percentage || 0) / 100;

    const overallAmount = roomAmount + extraCharges + extraBedTotal + taxAmount - discountAmount;

    const balanceAmount = overallAmount - (paymentData.paying_amount || 0);
    const extraAmount = balanceAmount < 0 ? Math.abs(balanceAmount) : 0;
    const finalBalance = balanceAmount < 0 ? 0 : balanceAmount;

    setPaymentData(prev => ({
      ...prev,
      tax_amount: taxAmount,
      discount_amount: discountAmount,
      overall_amount: overallAmount,
      total_amount: overallAmount,
      balance_amount: finalBalance,
      extra_amount: extraAmount,
      paid_amount: paymentData.paying_amount
    }));
  }, [
    paymentData.room_amount,
    paymentData.extra_charges,
    paymentData.extra_bed_count,
    paymentData.extra_bed_cost,
    paymentData.tax_percentage,
    paymentData.discount_percentage,
    paymentData.paying_amount
  ]);

  const handlePaymentChange = (field, value) => {
    let numValue;

    if (value === "" || value === null || value === undefined) {
      numValue = 0;
    } else if (field.includes('percentage') || field.includes('amount') || field.includes('cost') || field.includes('charges') || field === 'paying_amount') {
      numValue = parseFloat(value) || 0;
    } else if (field === 'payment_method_id') {
      numValue = Number(value);
    }
    else {
      numValue = value;
    }

    setPaymentData(prev => {
      const updated = { ...prev, [field]: numValue };

      if (field === 'tax_type_id' && numValue) {
        const selectedTax = taxTypes.find(tax => tax.id == numValue);
        if (selectedTax) {
          updated.tax_percentage = selectedTax.tax_percentage || selectedTax.percentage || 0;
        }
      }

      if (field === 'discount_type_id' && numValue) {
        const selectedDiscount = discountTypes.find(discount => discount.id == numValue);
        if (selectedDiscount) {
          updated.discount_percentage = selectedDiscount.discount_percentage || selectedDiscount.percentage || 0;
        }
      }

      return updated;
    });
  };


  const formatInputValue = (value) => {
    if (value === 0) return "0";
    return value.toString();
  };

  useEffect(() => {
    setpaymentData(paymentData);
  }, [paymentData]);

  return (
    <div className="pay-wrapper">

      <div className="pay-grid">
        <div className="pay-field">
          <label>Tax Type</label>
          <select
            value={paymentData.tax_type_id}
            onChange={(e) => handlePaymentChange('tax_type_id', e.target.value)}
          >
            <option value="">Select Tax Type</option>
            {taxTypes.map((tax) => (
              <option key={tax.id} value={tax.id}>
                {tax.tax_name || tax.name}
              </option>
            ))}
          </select>
        </div>

        <div className="pay-field">
          <label>Tax Percentage</label>
          <input
            type="number"
            placeholder="Tax %"
            value={formatInputValue(paymentData.tax_percentage)}
            onChange={(e) => handlePaymentChange('tax_percentage', e.target.value)}
          />
        </div>

        <div className="pay-field">
          <label>Tax Amount</label>
          <input
            type="number"
            value={paymentData.tax_amount.toFixed(2)}
            readOnly
          />
        </div>

        <div className="pay-field">
          <label>Discount Type</label>
          <select
            value={paymentData.discount_type_id}
            onChange={(e) => handlePaymentChange('discount_type_id', e.target.value)}
          >
            <option value="">Select Discount Type</option>
            {discountTypes.map((discount) => (
              <option key={discount.id} value={discount.id}>
                {discount.discount_name || discount.name}
              </option>
            ))}
          </select>
        </div>

        <div className="pay-field">
          <label>Discount Percentage</label>
          <input
            type="number"
            placeholder="Discount %"
            value={formatInputValue(paymentData.discount_percentage)}
            onChange={(e) => handlePaymentChange('discount_percentage', e.target.value)}
          />
        </div>

        <div className="pay-field">
          <label>Discount Amount</label>
          <input
            type="number"
            value={paymentData.discount_amount.toFixed(2)}
            readOnly
          />
        </div>

        <div className="pay-field">
          <label>Room Amount</label>
          <input
            type="number"
            value={formatInputValue(paymentData.room_amount)}
            onChange={(e) => handlePaymentChange('room_amount', e.target.value)}
          />
        </div>

        <div className="pay-field">
          <label>Extra Charges</label>
          <input
            type="number"
            placeholder="Enter extra charges"
            value={formatInputValue(paymentData.extra_charges)}
            onChange={(e) => handlePaymentChange('extra_charges', e.target.value)}
          />
        </div>

        <div className="pay-field">
          <label>Extra Bed Count</label>
          <input
            type="number"
            value={formatInputValue(paymentData.extra_bed_count)}
            onChange={(e) => handlePaymentChange('extra_bed_count', e.target.value)}
            min="0"
          />
        </div>

        <div className="pay-field">
          <label>Extra Bed Cost</label>
          <input
            type="number"
            value={formatInputValue(paymentData.extra_bed_cost)}
            onChange={(e) => handlePaymentChange('extra_bed_cost', e.target.value)}
            step="0.01"
            min="0"
          />
        </div>

        <div className="pay-field">
          <label>Overall Amount</label>
          <input
            type="number"
            value={paymentData.overall_amount.toFixed(2)}
            readOnly
          />
        </div>

        <div className="pay-field">
          <label>Total Amount</label>
          <input
            type="number"
            value={paymentData.total_amount.toFixed(2)}
            readOnly
          />
        </div>
      </div>

      <p className="pay-title">Payment Details</p>
      <div className="pay-grid">
        <div className="pay-field">
          <label>Payment Method</label>
          <select
            value={paymentData.payment_method_id}
            onChange={(e) => handlePaymentChange('payment_method_id', e.target.value)}
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
          <label>Paying Amount</label>
          <input
            type="number"
            placeholder="Enter paying amount"
            value={formatInputValue(paymentData.paying_amount)}
            onChange={(e) => handlePaymentChange('paying_amount', e.target.value)}
            step="0.01"
            min="0"
          />
        </div>

        <div className="pay-field">
          <label>Paid Amount</label>
          <input
            type="number"
            value={paymentData.paid_amount.toFixed(2)}
            readOnly
          />
        </div>

        <div className="pay-field">
          <label>Balance Amount</label>
          <input
            type="number"
            value={paymentData.balance_amount.toFixed(2)}
            readOnly
          />
        </div>

        <div className="pay-field">
          <label>Extra Amount</label>
          <input
            type="number"
            value={paymentData.extra_amount.toFixed(2)}
            readOnly
          />
        </div>
      </div>
    </div>
  );
};

export default Payment;
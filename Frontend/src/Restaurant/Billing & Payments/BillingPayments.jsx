import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, CreditCard, Printer, X } from "lucide-react";

const BillingPayments = () => {
  const [showViewBillModal, setShowViewBillModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedBill, setSelectedBill] = useState(null);

  const billingData = [
    {
      id: 1,
      billNo: "BILL5021",
      orderId: "ORD1164",
      tableId: "T03",
      roomNo: "-",
      orderType: "Dine-In",
      billAmount: "₹850",
      discount: "₹50",
      tax: "₹80",
      paymentStatus: "Pending",
      cashier: "John",
      date: "22-Jan-2025",
      items: [
        { name: "Paneer Butter Masala", qty: 2, amount: "₹500" },
        { name: "Butter Naan", qty: 3, amount: "₹350" },
      ],
      summary: {
        subtotal: "₹850",
        discount: "₹50",
        tax: "₹80",
        total: "₹880",
      },
    },
    {
      id: 2,
      billNo: "BILL5022",
      orderId: "ORD1167",
      tableId: "-",
      roomNo: "R102",
      orderType: "Room Service",
      billAmount: "₹1,200",
      discount: "₹0",
      tax: "₹96",
      paymentStatus: "Paid",
      cashier: "Admin",
      date: "22-Jan-2025",
      items: [],
      summary: {},
    },
  ];

  const openViewBillModal = (row) => {
    setSelectedBill(row);
    setShowViewBillModal(true);
  };

  const openPaymentModal = (row) => {
    setSelectedBill(row);
    setShowPaymentModal(true);
  };

  const closeModals = () => {
    setSelectedBill(null);
    setShowViewBillModal(false);
    setShowPaymentModal(false);
  };

  return (
    <>
      {/* ================= BILLING TABLE ================= */}
      <TableTemplate
        title="Billing & Payments"
        searchable
        pagination
        columns={[
          { key: "billNo", title: "Bill No" },
          { key: "orderId", title: "Order ID" },
          { key: "tableId", title: "Table ID", align: "center" },
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "orderType", title: "Order Type" },
          { key: "billAmount", title: "Bill Amount", align: "right" },
          { key: "discount", title: "Discount", align: "right" },
          { key: "tax", title: "Tax", align: "right" },
          {
            key: "paymentStatus",
            title: "Payment Status",
            type: "badge",
            align: "center",
          },
          {
            key: "action",
            title: "Action",
            align: "center",
            width: "140px",
            type: "custom",
            render: (row) => (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: "6px",
                  whiteSpace: "nowrap",
                }}
              >
                <button
                  className="table-action-btn view"
                  onClick={() => openViewBillModal(row)}
                >
                  <Eye size={16} />
                </button>

                {row.paymentStatus !== "Paid" && (
                  <button
                    className="table-action-btn success"
                    onClick={() => openPaymentModal(row)}
                  >
                    <CreditCard size={16} />
                  </button>
                )}
              </div>
            ),
          },
        ]}
        data={billingData}
      />

      {/* ================= VIEW BILL MODAL ================= */}
      {showViewBillModal && selectedBill && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Bill Details – {selectedBill.billNo}</h3>
              <button onClick={closeModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <p className="small text-muted mb-3">
                Cashier: {selectedBill.cashier} | Date: {selectedBill.date}
              </p>

              <table className="table table-sm">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedBill.items.map((item, index) => (
                    <tr key={index}>
                      <td>{item.name}</td>
                      <td>{item.qty}</td>
                      <td>{item.amount}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <hr />

              <div className="d-flex justify-content-between">
                <span>Subtotal</span>
                <span>{selectedBill.summary.subtotal}</span>
              </div>
              <div className="d-flex justify-content-between">
                <span>Discount</span>
                <span>{selectedBill.summary.discount}</span>
              </div>
              <div className="d-flex justify-content-between">
                <span>Tax</span>
                <span>{selectedBill.summary.tax}</span>
              </div>
              <div className="d-flex justify-content-between fw-semibold">
                <span>Total Payable</span>
                <span>{selectedBill.summary.total}</span>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModals}>
                Close
              </button>
              <button className="btn outline">
                <Printer size={16} /> Print Bill
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= COLLECT PAYMENT MODAL (FIXED HEIGHT) ================= */}
      {showPaymentModal && selectedBill && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Collect Payment</h3>
              <button onClick={closeModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ paddingTop: "20px" }}>
              <div className="form-group mb-3">
                <label>Payment Mode</label>
                <select className="form-control">
                  <option>Cash</option>
                  <option>Card</option>
                  <option>UPI</option>
                  <option>Room Charge</option>
                  <option>Split Payment</option>
                </select>
              </div>

              <div className="form-group mb-3">
                <label>Amount Paid</label>
                <input type="number" className="form-control" />
              </div>

              <div className="form-group mb-3">
                <label>Reference Number</label>
                <input type="text" className="form-control" />
              </div>

              <div className="form-group mb-4">
                <label>Remarks</label>
                <textarea className="form-control" rows="3" />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModals}>
                Cancel
              </button>
              <button className="btn primary">
                Submit Payment
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BillingPayments;

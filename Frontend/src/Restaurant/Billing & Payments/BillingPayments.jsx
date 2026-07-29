import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, CreditCard, Printer, X, Receipt, Ban } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const BillingPayments = () => {
  const [bills, setBills] = useState([]);
  const [orders, setOrders] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showViewBillModal, setShowViewBillModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedBill, setSelectedBill] = useState(null);
  const [formError, setFormError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [cancelReason, setCancelReason] = useState("");

  const [genOrderId, setGenOrderId] = useState("");
  const [genForm, setGenForm] = useState({ cgst_percentage: 2.5, sgst_percentage: 2.5, service_charge_percentage: 5, discount_type: "", discount_value: 0 });
  const [genOrderItems, setGenOrderItems] = useState([]);
  const [genItemsLoading, setGenItemsLoading] = useState(false);
  const [genItemsError, setGenItemsError] = useState(null);

  const [payForm, setPayForm] = useState({ payment_method_id: "", paid_amount: "", payment_reference: "", remarks: "" });

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([
      APICall.getT("/restaurant/bill"),
      APICall.getT("/restaurant/order"),
      APICall.getT("/restaurant/payment_method"),
      APICall.getT("/restaurant/menu"),
    ]).then(([bRes, oRes, pRes, mRes]) => {
      setBills(bRes.status === "fulfilled" ? readList(bRes.value) : []);
      setOrders(oRes.status === "fulfilled" ? readList(oRes.value) : []);
      setPaymentMethods(pRes.status === "fulfilled" ? readList(pRes.value) : []);
      setMenuItems(mRes.status === "fulfilled" ? readList(mRes.value) : []);
      if (bRes.status === "rejected") setError(errMsg(bRes.reason, "Failed to load bills."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const billableOrders = orders.filter((o) => ["Served", "Ready", "In Progress"].includes(o.order_status) && o.payment_status !== "Paid");

  // Pull the selected order's line items so the Generate Bill modal can show
  // what's actually being billed, instead of only the order number + totals.
  useEffect(() => {
    if (!genOrderId) {
      setGenOrderItems([]);
      setGenItemsError(null);
      return;
    }
    let cancelled = false;
    setGenItemsLoading(true);
    setGenItemsError(null);
    APICall.getT(`/restaurant/order/${genOrderId}`)
      .then((res) => {
        if (cancelled) return;
        setGenOrderItems(res?.data?.items || []);
      })
      .catch((err) => {
        if (cancelled) return;
        setGenOrderItems([]);
        setGenItemsError(errMsg(err, "Failed to load order items."));
      })
      .finally(() => {
        if (!cancelled) setGenItemsLoading(false);
      });
    return () => { cancelled = true; };
  }, [genOrderId]);

  const menuName = (menuId) => menuItems.find((m) => m.id === menuId)?.item_name || `#${menuId}`;
  const genItemsSubtotal = genOrderItems.reduce((sum, it) => sum + (it.price || 0) * (it.quantity || 0), 0);

  const openViewBillModal = async (row) => {
    try {
      const res = await APICall.getT(`/restaurant/bill/${row.id}`);
      setSelectedBill(res?.data || row);
      setShowViewBillModal(true);
    } catch (err) {
      setError(errMsg(err, "Failed to load bill."));
    }
  };

  const openPaymentModal = (row) => {
    setSelectedBill(row);
    setPayForm({ payment_method_id: "", paid_amount: row.grand_total, payment_reference: "", remarks: "" });
    setFormError(null);
    setShowPaymentModal(true);
  };

  const closeModals = () => {
    if (saving) return;
    setSelectedBill(null);
    setShowViewBillModal(false);
    setShowPaymentModal(false);
    setShowGenerateModal(false);
    setShowCancelModal(false);
  };

  const openCancelModal = (row) => {
    setSelectedBill(row);
    setCancelReason("");
    setFormError(null);
    setShowCancelModal(true);
  };

  const submitCancelBill = async () => {
    if (!cancelReason.trim()) {
      setFormError("A reason is required to cancel a bill.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await APICall.putT(`/restaurant/bill/${selectedBill.id}/cancel`, { reason: cancelReason.trim() });
      setShowCancelModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to cancel bill."));
    } finally {
      setSaving(false);
    }
  };

  const openGenerateModal = () => {
    setGenOrderId("");
    setGenForm({ cgst_percentage: 2.5, sgst_percentage: 2.5, service_charge_percentage: 5, discount_type: "", discount_value: 0 });
    setFormError(null);
    setShowGenerateModal(true);
  };

  const generateBill = async () => {
    if (!genOrderId) {
      setFormError("Select an order to bill.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT(`/restaurant/bill/generate/${genOrderId}`, {
        cgst_percentage: Number(genForm.cgst_percentage) || 0,
        sgst_percentage: Number(genForm.sgst_percentage) || 0,
        service_charge_percentage: Number(genForm.service_charge_percentage) || 0,
        discount_type: genForm.discount_type || null,
        discount_value: Number(genForm.discount_value) || 0,
      });
      setShowGenerateModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to generate bill."));
    } finally {
      setSaving(false);
    }
  };

  const submitPayment = async () => {
    if (!payForm.payment_method_id || !payForm.paid_amount) {
      setFormError("Payment mode and amount are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT(`/restaurant/bill/${selectedBill.id}/payment`, {
        payment_method_id: Number(payForm.payment_method_id),
        paid_amount: Number(payForm.paid_amount),
        payment_reference: payForm.payment_reference || null,
        remarks: payForm.remarks || null,
      });
      setShowPaymentModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to record payment."));
    } finally {
      setSaving(false);
    }
  };

  const printBill = () => window.print();

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Billing & Payments"
        searchable
        pagination
        loading={loading}
        hasActionButton
        actionButton={{ label: "Generate Bill", onClick: openGenerateModal, size: "medium", variant: "primary" }}
        columns={[
          { key: "bill_number", title: "Bill No" },
          { key: "order_number", title: "Order No" },
          { key: "table_code", title: "Table", align: "center", type: "custom", render: (row) => row.table_code || row.room_no || "-" },
          { key: "sub_total", title: "Subtotal", align: "right" },
          { key: "discount_amount", title: "Discount", align: "right" },
          { key: "grand_total", title: "Grand Total", align: "right" },
          { key: "payment_status", title: "Payment Status", type: "badge", align: "center" },
          {
            key: "action",
            title: "Action",
            align: "center",
            width: "140px",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", justifyContent: "center", gap: "6px", whiteSpace: "nowrap" }}>
                <button className="table-action-btn view" onClick={() => openViewBillModal(row)}>
                  <Eye size={16} />
                </button>
                {row.payment_status !== "Paid" && row.bill_status !== "Cancelled" && (
                  <>
                    <button className="table-action-btn success" onClick={() => openPaymentModal(row)}>
                      <CreditCard size={16} />
                    </button>
                    <button className="table-action-btn delete" title="Cancel bill (lets you generate a fresh one for this order)" onClick={() => openCancelModal(row)}>
                      <Ban size={16} />
                    </button>
                  </>
                )}
              </div>
            ),
          },
        ]}
        data={bills}
      />

      {showGenerateModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3><Receipt size={16} /> Generate Bill</h3>
              <button onClick={closeModals}><X size={18} /></button>
            </div>
            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}
            <div className="modal-body single">
              <div className="form-group">
                <label>Order <span className="required">*</span></label>
                <select value={genOrderId} onChange={(e) => setGenOrderId(e.target.value)}>
                  <option value="">— select —</option>
                  {billableOrders.map((o) => (
                    <option key={o.id} value={o.id}>{o.order_number} — {o.table_code || o.room_no || o.order_type}</option>
                  ))}
                </select>
              </div>

              {genOrderId && (
                <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                  <label>Order Items</label>
                  {genItemsLoading && <p className="small text-muted">Loading items…</p>}
                  {genItemsError && <div className="rmv-alert" role="alert"><span>{genItemsError}</span></div>}
                  {!genItemsLoading && !genItemsError && (
                    <table className="table table-sm" style={{ width: "100%" }}>
                      <thead>
                        <tr><th style={{ textAlign: "left" }}>Item</th><th>Qty</th><th>Price</th><th>Amount</th></tr>
                      </thead>
                      <tbody>
                        {genOrderItems.map((it) => (
                          <tr key={it.id}>
                            <td>{menuName(it.menu_id)}</td>
                            <td style={{ textAlign: "center" }}>{it.quantity}</td>
                            <td style={{ textAlign: "center" }}>{it.price}</td>
                            <td style={{ textAlign: "center" }}>{(it.price || 0) * (it.quantity || 0)}</td>
                          </tr>
                        ))}
                        {genOrderItems.length === 0 && (
                          <tr><td colSpan={4} style={{ textAlign: "center", color: "#9ca3af" }}>No items on this order</td></tr>
                        )}
                      </tbody>
                      {genOrderItems.length > 0 && (
                        <tfoot>
                          <tr>
                            <td colSpan={3} style={{ textAlign: "right", fontWeight: 600 }}>Subtotal</td>
                            <td style={{ textAlign: "center", fontWeight: 600 }}>{genItemsSubtotal}</td>
                          </tr>
                        </tfoot>
                      )}
                    </table>
                  )}
                </div>
              )}

              <div className="form-group">
                <label>CGST %</label>
                <input type="number" value={genForm.cgst_percentage} onChange={(e) => setGenForm((p) => ({ ...p, cgst_percentage: e.target.value }))} />
              </div>
              <div className="form-group">
                <label>SGST %</label>
                <input type="number" value={genForm.sgst_percentage} onChange={(e) => setGenForm((p) => ({ ...p, sgst_percentage: e.target.value }))} />
              </div>
              <div className="form-group">
                <label>Service Charge %</label>
                <input type="number" value={genForm.service_charge_percentage} onChange={(e) => setGenForm((p) => ({ ...p, service_charge_percentage: e.target.value }))} />
              </div>
              <div className="form-group">
                <label>Discount Type</label>
                <select value={genForm.discount_type} onChange={(e) => setGenForm((p) => ({ ...p, discount_type: e.target.value }))}>
                  <option value="">None</option>
                  <option value="Percentage">Percentage</option>
                  <option value="Flat">Flat Amount</option>
                </select>
              </div>
              {genForm.discount_type && (
                <div className="form-group">
                  <label>Discount Value</label>
                  <input type="number" value={genForm.discount_value} onChange={(e) => setGenForm((p) => ({ ...p, discount_value: e.target.value }))} />
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModals} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={generateBill} disabled={saving}>{saving ? "Generating…" : "Generate"}</button>
            </div>
          </div>
        </div>
      )}

      {showCancelModal && selectedBill && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Cancel Bill — {selectedBill.bill_number}</h3>
              <button onClick={closeModals}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
              <p className="small text-muted mb-3">
                This cancels the bill only — the order (<strong>{selectedBill.order_number}</strong>) stays open, so you
                can add/change items if needed and use <strong>Generate Bill</strong> again for the same order.
              </p>
              <div className="form-group">
                <label>Reason <span className="required">*</span></label>
                <textarea rows="3" value={cancelReason} onChange={(e) => setCancelReason(e.target.value)} placeholder="e.g. wrong tax applied, items changed" />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModals} disabled={saving}>Close</button>
              <button className="btn primary" onClick={submitCancelBill} disabled={saving}>{saving ? "Cancelling…" : "Cancel Bill"}</button>
            </div>
          </div>
        </div>
      )}

      {showViewBillModal && selectedBill && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Bill Details – {selectedBill.bill_number}</h3>
              <button onClick={closeModals}><X size={18} /></button>
            </div>

            <div className="modal-body">
              <p className="small text-muted mb-3">Date: {selectedBill.bill_date} {selectedBill.bill_time}</p>

              <table className="table table-sm">
                <thead>
                  <tr><th>Item</th><th>Qty</th><th>Amount</th></tr>
                </thead>
                <tbody>
                  {(selectedBill.items || []).map((item) => (
                    <tr key={item.id}>
                      <td>{item.item_name}</td>
                      <td>{item.quantity}</td>
                      <td>{item.amount}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <hr />
              <div className="d-flex justify-content-between"><span>Subtotal</span><span>{selectedBill.sub_total}</span></div>
              <div className="d-flex justify-content-between"><span>CGST</span><span>{selectedBill.cgst_amount}</span></div>
              <div className="d-flex justify-content-between"><span>SGST</span><span>{selectedBill.sgst_amount}</span></div>
              <div className="d-flex justify-content-between"><span>Service Charge</span><span>{selectedBill.service_charge_amount}</span></div>
              <div className="d-flex justify-content-between"><span>Discount</span><span>{selectedBill.discount_amount}</span></div>
              <div className="d-flex justify-content-between fw-semibold"><span>Total Payable</span><span>{selectedBill.grand_total}</span></div>

              {selectedBill.payments && selectedBill.payments.length > 0 && (
                <>
                  <hr />
                  <p><strong>Payments</strong></p>
                  {selectedBill.payments.map((p) => (
                    <div className="d-flex justify-content-between" key={p.id}>
                      <span>{p.payment_reference || "Payment"} ({p.payment_status})</span>
                      <span>{p.paid_amount}</span>
                    </div>
                  ))}
                </>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModals}>Close</button>
              <button className="btn outline" onClick={printBill}><Printer size={16} /> Print Bill</button>
            </div>
          </div>
        </div>
      )}

      {showPaymentModal && selectedBill && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Collect Payment — {selectedBill.bill_number}</h3>
              <button onClick={closeModals}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body" style={{ paddingTop: "20px" }}>
              <div className="form-group mb-3">
                <label>Payment Mode</label>
                <select className="form-control" value={payForm.payment_method_id} onChange={(e) => setPayForm((p) => ({ ...p, payment_method_id: e.target.value }))}>
                  <option value="">— select —</option>
                  {paymentMethods.map((m) => (
                    <option key={m.id} value={m.id}>{m.method_name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group mb-3">
                <label>Amount Paid</label>
                <input type="number" className="form-control" value={payForm.paid_amount} onChange={(e) => setPayForm((p) => ({ ...p, paid_amount: e.target.value }))} />
              </div>

              <div className="form-group mb-3">
                <label>Reference Number</label>
                <input type="text" className="form-control" value={payForm.payment_reference} onChange={(e) => setPayForm((p) => ({ ...p, payment_reference: e.target.value }))} />
              </div>

              <div className="form-group mb-4">
                <label>Remarks</label>
                <textarea className="form-control" rows="3" value={payForm.remarks} onChange={(e) => setPayForm((p) => ({ ...p, remarks: e.target.value }))} />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModals} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={submitPayment} disabled={saving}>{saving ? "Submitting…" : "Submit Payment"}</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BillingPayments;

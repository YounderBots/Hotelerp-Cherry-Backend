import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, CreditCard, Printer, Ban } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const BarBillingPayments = () => {
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
      APICall.getT("/bar/bill"),
      APICall.getT("/bar/order"),
      APICall.getT("/bar/payment_method"),
      APICall.getT("/bar/menu"),
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

  useEffect(() => {
    if (!genOrderId) {
      setGenOrderItems([]);
      setGenItemsError(null);
      return;
    }
    let cancelled = false;
    setGenItemsLoading(true);
    setGenItemsError(null);
    APICall.getT(`/bar/order/${genOrderId}`)
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
      const res = await APICall.getT(`/bar/bill/${row.id}`);
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
      await APICall.putT(`/bar/bill/${selectedBill.id}/cancel`, { reason: cancelReason.trim() });
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
      await APICall.postT(`/bar/bill/generate/${genOrderId}`, {
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
      await APICall.postT(`/bar/bill/${selectedBill.id}/payment`, {
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
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Billing & Payments"
        searchable
        pagination
        loading={loading}
        hasActionButton
        actionButton={{ label: "Generate Bill", onClick: openGenerateModal, size: "medium", variant: "primary" }}
        columns={[
          { key: "bill_number", title: "Bill No" },
          { key: "order_number", title: "Order No" },
          { key: "table_code", title: "Table", align: "center", type: "custom", render: (row) => row.table_code || "-" },
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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openViewBillModal(row)} />
                {row.payment_status !== "Paid" && row.bill_status !== "Cancelled" && (
                  <>
                    <IconButton variant="success" size="small" icon={<CreditCard size={16} />} ariaLabel="Collect payment" onClick={() => openPaymentModal(row)} />
                    <IconButton
                      variant="danger-ghost"
                      size="small"
                      icon={<Ban size={16} />}
                      ariaLabel="Cancel bill"
                      title="Cancel bill (lets you generate a fresh one for this order)"
                      onClick={() => openCancelModal(row)}
                    />
                  </>
                )}
              </div>
            ),
          },
        ]}
        data={bills}
      />

      {showGenerateModal && (
        <Modal
          isOpen
          title="Generate Bill"
          onClose={closeModals}
          size="large"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeModals, disabled: saving },
            { label: saving ? "Generating…" : "Generate", variant: "primary", onClick: generateBill, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <Select
            label="Order"
            required
            value={genOrderId}
            onChange={(e) => setGenOrderId(e.target.value)}
            options={billableOrders.map((o) => ({ value: o.id, label: `${o.order_number} — ${o.table_code || o.order_type}` }))}
            placeholder="— select —"
          />

          {genOrderId && (
            <div>
              <label className="form-label">Order Items</label>
              {genItemsLoading && <p className="small text-muted">Loading items…</p>}
              <ErrorAlert message={genItemsError} />
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

          <Input label="CGST %" type="number" value={genForm.cgst_percentage} onChange={(e) => setGenForm((p) => ({ ...p, cgst_percentage: e.target.value }))} />
          <Input label="SGST %" type="number" value={genForm.sgst_percentage} onChange={(e) => setGenForm((p) => ({ ...p, sgst_percentage: e.target.value }))} />
          <Input label="Service Charge %" type="number" value={genForm.service_charge_percentage} onChange={(e) => setGenForm((p) => ({ ...p, service_charge_percentage: e.target.value }))} />
          <Select
            label="Discount Type"
            value={genForm.discount_type}
            onChange={(e) => setGenForm((p) => ({ ...p, discount_type: e.target.value }))}
            options={[{ value: "Percentage", label: "Percentage" }, { value: "Flat", label: "Flat Amount" }]}
            placeholder="None"
          />
          {genForm.discount_type && (
            <Input label="Discount Value" type="number" value={genForm.discount_value} onChange={(e) => setGenForm((p) => ({ ...p, discount_value: e.target.value }))} />
          )}
        </Modal>
      )}

      {showCancelModal && selectedBill && (
        <Modal
          isOpen
          title={`Cancel Bill — ${selectedBill.bill_number}`}
          onClose={closeModals}
          size="medium"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModals, disabled: saving },
            { label: saving ? "Cancelling…" : "Cancel Bill", variant: "primary", onClick: submitCancelBill, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <p className="small text-muted mb-3">
            This cancels the bill only — the order (<strong>{selectedBill.order_number}</strong>) stays open, so you
            can add/change items if needed and use <strong>Generate Bill</strong> again for the same order.
          </p>
          <div className="form-group">
            <label className="form-label">
              Reason <span className="required">*</span>
            </label>
            <textarea
              className="form-control"
              rows="3"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="e.g. wrong tax applied, items changed"
            />
          </div>
        </Modal>
      )}

      {showViewBillModal && selectedBill && (
        <Modal
          isOpen
          title={`Bill Details – ${selectedBill.bill_number}`}
          onClose={closeModals}
          size="large"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModals },
            { label: "Print Bill", icon: <Printer size={16} />, variant: "outline", onClick: printBill },
          ]}
        >
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
        </Modal>
      )}

      {showPaymentModal && selectedBill && (
        <Modal
          isOpen
          title={`Collect Payment — ${selectedBill.bill_number}`}
          onClose={closeModals}
          size="medium"
          bodyLayout="grid"
          showFooter
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeModals, disabled: saving },
            { label: saving ? "Submitting…" : "Submit Payment", variant: "primary", onClick: submitPayment, disabled: saving },
          ]}
        >
          <div style={{ gridColumn: "1 / -1" }}>
            <ErrorAlert message={formError} />
          </div>

          <Select
            label="Payment Mode"
            value={payForm.payment_method_id}
            onChange={(e) => setPayForm((p) => ({ ...p, payment_method_id: e.target.value }))}
            options={paymentMethods.map((m) => ({ value: m.id, label: m.method_name }))}
            placeholder="— select —"
          />
          <Input label="Amount Paid" type="number" value={payForm.paid_amount} onChange={(e) => setPayForm((p) => ({ ...p, paid_amount: e.target.value }))} />
          <Input label="Reference Number" value={payForm.payment_reference} onChange={(e) => setPayForm((p) => ({ ...p, payment_reference: e.target.value }))} />
          <div className="form-group" style={{ gridColumn: "1 / -1" }}>
            <label className="form-label">Remarks</label>
            <textarea className="form-control" rows="3" value={payForm.remarks} onChange={(e) => setPayForm((p) => ({ ...p, remarks: e.target.value }))} />
          </div>
        </Modal>
      )}
    </>
  );
};

export default BarBillingPayments;

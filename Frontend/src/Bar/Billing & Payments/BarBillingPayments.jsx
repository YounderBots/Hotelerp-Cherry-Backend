import React, { useState } from "react";
import { Ban, CreditCard, Printer } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import IconButton from "../../stories/IconButton";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatDate, formatPrecise, num } from "../../functions/formatters";
import { printDocument, printHeading, printRow } from "../../functions/printDocument";
import { useApiResource, useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import "../../stories/OrderDetail.css";

/**
 * Tax and service-charge defaults for a new bill.
 *
 * These are page defaults, not master data. BarServices does expose a
 * generic settings key/value store (GET /bar/settings), but it has no
 * seeded keys and no screen to manage them, so reading the rates from it today
 * would bill every order at 0%. Moving them there is a decision for the
 * property, not something to infer — see the note in the audit summary.
 */
const DEFAULT_CHARGES = {
  cgst_percentage: 2.5,
  sgst_percentage: 2.5,
  service_charge_percentage: 5,
  discount_type: "",
  discount_value: 0,
};

const DISCOUNT_TYPES = [
  { value: "Percentage", label: "Percentage" },
  { value: "Flat", label: "Flat Amount" },
];

const emptyPayForm = {
  payment_method_id: "",
  paid_amount: "",
  payment_reference: "",
  remarks: "",
};

const BarBillingPayments = () => {
  const perms = usePagePermissions("/bar_billing_payments");

  const {
    data: [bills, orders, paymentMethods, menuItems],
    loading,
    error,
    reload: load,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/bar/bill"),
      select: readList,
      fallback: "Failed to load bills.",
    },
    { fetch: () => APICall.getT("/bar/order"), select: readList },
    { fetch: () => APICall.getT("/bar/payment_method"), select: readList },
    { fetch: () => APICall.getT("/bar/menu"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [activeModal, setActiveModal] = useState(null); // view | payment | generate | cancel
  const [selectedBill, setSelectedBill] = useState(null);
  const [formError, setFormError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [cancelReason, setCancelReason] = useState("");

  const [genOrderId, setGenOrderId] = useState("");
  const [genForm, setGenForm] = useState(DEFAULT_CHARGES);
  const [payForm, setPayForm] = useState(emptyPayForm);

  // The selected order's line items, so the Generate Bill modal shows what is
  // actually being billed rather than only an order number. This was a
  // hand-rolled useEffect with its own cancelled flag, loading flag and error
  // state — the exact triple useApiResource exists to own, and the reason it
  // takes `deps` and `enabled`.
  const {
    data: genOrderItems,
    loading: genItemsLoading,
    error: genItemsError,
  } = useApiResource(() => APICall.getT(`/bar/order/${genOrderId}`), {
    select: (res) => res?.data?.items || [],
    fallback: "Failed to load order items.",
    enabled: !!genOrderId,
    deps: [genOrderId],
  });

  const billableOrders = orders.filter(
    (o) =>
      ["Served", "Ready", "In Progress"].includes(o.order_status) &&
      o.payment_status !== "Paid",
  );

  // get_order now returns item_name; the menu list is only a fallback for a
  // response that predates it.
  const menuName = (it) =>
    it.item_name || menuItems.find((m) => m.id === it.menu_id)?.item_name || "Unnamed item";

  const genItemsSubtotal = genOrderItems.reduce(
    (sum, it) => sum + num(it.price) * num(it.quantity),
    0,
  );

  /* ================= HANDLERS ================= */

  const closeModals = () => {
    if (saving) return;
    setSelectedBill(null);
    setActiveModal(null);
    setFormError(null);
  };

  const openViewBillModal = async (row) => {
    try {
      const res = await APICall.getT(`/bar/bill/${row.id}`);
      setSelectedBill(res?.data || row);
      setActiveModal("view");
    } catch (err) {
      showToast(errMsg(err, "Failed to load bill."), "error");
    }
  };

  const openPaymentModal = (row) => {
    setSelectedBill(row);
    // Defaults to what is still owed, not the whole bill: a partly-paid bill
    // was pre-filling the grand total, so confirming without editing tried to
    // collect the full amount a second time.
    const outstanding = num(row.grand_total) - num(row.paid_amount);
    setPayForm({
      ...emptyPayForm,
      paid_amount: outstanding > 0 ? outstanding.toFixed(2) : "",
    });
    setFormError(null);
    setActiveModal("payment");
  };

  const openCancelModal = (row) => {
    setSelectedBill(row);
    setCancelReason("");
    setFormError(null);
    setActiveModal("cancel");
  };

  const openGenerateModal = () => {
    setGenOrderId("");
    setGenForm(DEFAULT_CHARGES);
    setFormError(null);
    setActiveModal("generate");
  };

  const submitCancelBill = async () => {
    if (saving) return;
    if (!cancelReason.trim()) {
      setFormError("A reason is required to cancel a bill.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await APICall.putT(`/bar/bill/${selectedBill.id}/cancel`, {
        reason: cancelReason.trim(),
      });
      showToast("Bill cancelled", "delete");
      setActiveModal(null);
      setSelectedBill(null);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to cancel bill."));
    } finally {
      setSaving(false);
    }
  };

  const generateBill = async () => {
    if (saving) return;
    if (!genOrderId) {
      setFormError("Select an order to bill.");
      return;
    }
    if (genForm.discount_type && num(genForm.discount_value) <= 0) {
      setFormError("Enter a discount value, or clear the discount type.");
      return;
    }
    if (genForm.discount_type === "Percentage" && num(genForm.discount_value) > 100) {
      setFormError("A percentage discount cannot exceed 100%.");
      return;
    }

    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT(`/bar/bill/generate/${genOrderId}`, {
        cgst_percentage: num(genForm.cgst_percentage),
        sgst_percentage: num(genForm.sgst_percentage),
        service_charge_percentage: num(genForm.service_charge_percentage),
        discount_type: genForm.discount_type || null,
        discount_value: num(genForm.discount_value),
      });
      showToast("Bill generated successfully", "success");
      setActiveModal(null);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to generate bill."));
    } finally {
      setSaving(false);
    }
  };

  const submitPayment = async () => {
    if (saving) return;
    if (!payForm.payment_method_id || !payForm.paid_amount) {
      setFormError("Payment mode and amount are required.");
      return;
    }
    if (num(payForm.paid_amount) <= 0) {
      setFormError("Enter an amount greater than zero.");
      return;
    }

    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT(`/bar/bill/${selectedBill.id}/payment`, {
        payment_method_id: Number(payForm.payment_method_id),
        paid_amount: num(payForm.paid_amount),
        payment_reference: payForm.payment_reference.trim() || null,
        remarks: payForm.remarks.trim() || null,
      });
      showToast("Payment recorded successfully", "success");
      setActiveModal(null);
      setSelectedBill(null);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to record payment."));
    } finally {
      setSaving(false);
    }
  };

  // Was `window.print()`, which printed the whole application page — nav rail,
  // submenu and the list behind the modal — rather than the bill.
  const printBill = () => {
    const b = selectedBill;
    if (!b) return;

    const itemRows = (b.items || [])
      .map(
        (it) =>
          `<tr><td>${it.item_name || "Item"}</td>` +
          `<td class="num">${it.quantity ?? ""}</td>` +
          `<td class="num">${formatPrecise(it.rate)}</td>` +
          `<td class="num">${formatPrecise(it.amount)}</td></tr>`,
      )
      .join("");

    const paymentRows = (b.payments || [])
      .map((p) =>
        printRow(
          `${p.payment_reference || "Payment"} (${p.payment_status || ""})`.trim(),
          formatPrecise(p.paid_amount),
        ),
      )
      .join("");

    const ok = printDocument({
      title: `Bill ${b.bill_number}`,
      heading: "Bill",
      subtitle: `${b.bill_number} · ${formatDate(b.bill_date)} ${b.bill_time || ""}`.trim(),
      body:
        printHeading("Order") +
        printRow("Order number", b.order_number || "—") +
        printRow("Table", b.table_code || "—") +
        printHeading("Items") +
        `<table><thead><tr><th>Item</th><th class="num">Qty</th>` +
        `<th class="num">Rate</th><th class="num">Amount</th></tr></thead>` +
        `<tbody>${itemRows || '<tr><td colspan="4">No items</td></tr>'}</tbody></table>` +
        printHeading("Summary") +
        printRow("Subtotal", formatPrecise(b.sub_total)) +
        printRow("CGST", formatPrecise(b.cgst_amount)) +
        printRow("SGST", formatPrecise(b.sgst_amount)) +
        printRow("Service charge", formatPrecise(b.service_charge_amount)) +
        printRow("Discount", `-${formatPrecise(b.discount_amount)}`) +
        printRow("Total payable", formatPrecise(b.grand_total), { total: true }) +
        (paymentRows ? printHeading("Payments") + paymentRows : ""),
    });

    if (!ok) {
      showToast("The print window was blocked. Please allow pop-ups for this site.", "error");
    }
  };

  /* ================= UI ================= */

  const billItems = selectedBill?.items || [];
  const billPayments = selectedBill?.payments || [];

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Billing & Payments"
        loading={loading}
        emptyMessage="No bills yet. Generate one from a served order."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Generate Bill",
          onClick: openGenerateModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "bill_number", title: "Bill No", align: "left" },
          { key: "order_number", title: "Order No", align: "left" },
          { key: "table_code", title: "Table", align: "left" },
          {
            key: "sub_total",
            title: "Subtotal",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.sub_total),
            exportValue: (row) => formatPrecise(row.sub_total),
          },
          {
            key: "discount_amount",
            title: "Discount",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.discount_amount),
            exportValue: (row) => formatPrecise(row.discount_amount),
          },
          {
            key: "grand_total",
            title: "Grand Total",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.grand_total),
            exportValue: (row) => formatPrecise(row.grand_total),
          },
          { key: "bill_status", title: "Bill Status", align: "center", type: "badge" },
          { key: "payment_status", title: "Payment", align: "center", type: "badge" },
          {
            key: "action",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => {
              const settleable =
                row.payment_status !== "Paid" && row.bill_status !== "Cancelled";
              return (
                <RowActions
                  label={`bill ${row.bill_number || ""}`.trim()}
                  onView={() => openViewBillModal(row)}
                >
                  {settleable && perms.edit && (
                    <IconButton
                      variant="action-edit"
                      size="action"
                      icon={<CreditCard size={16} />}
                      onClick={() => openPaymentModal(row)}
                      title="Collect payment"
                      ariaLabel={`Collect payment for bill ${row.bill_number || ""}`}
                    />
                  )}
                  {settleable && perms.delete && (
                    <IconButton
                      variant="action-delete"
                      size="action"
                      icon={<Ban size={16} />}
                      onClick={() => openCancelModal(row)}
                      title="Cancel bill"
                      ariaLabel={`Cancel bill ${row.bill_number || ""}`}
                    />
                  )}
                </RowActions>
              );
            },
          },
        ]}
        data={bills}
      />

      {/* ================= GENERATE ================= */}
      <Modal
        isOpen={activeModal === "generate"}
        title="Generate Bill"
        onClose={closeModals}
        size="large"
        bodyLayout="custom"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModals, disabled: saving },
          {
            label: saving ? "Generating…" : "Generate",
            variant: "primary",
            onClick: generateBill,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} />

        <div className="field-grid">
          <Select
            label="Order"
            required
            value={genOrderId}
            onChange={(e) => setGenOrderId(e.target.value)}
            placeholder={billableOrders.length ? "— select —" : "No orders are ready to bill"}
            options={billableOrders.map((o) => ({
              value: o.id,
              label: `${o.order_number} — ${o.service_location || o.order_type}`,
            }))}
          />
          <Input
            label="CGST %"
            type="number"
            min="0"
            step="any"
            value={genForm.cgst_percentage}
            onChange={(e) => setGenForm((p) => ({ ...p, cgst_percentage: e.target.value }))}
          />
          <Input
            label="SGST %"
            type="number"
            min="0"
            step="any"
            value={genForm.sgst_percentage}
            onChange={(e) => setGenForm((p) => ({ ...p, sgst_percentage: e.target.value }))}
          />
          <Input
            label="Service Charge %"
            type="number"
            min="0"
            step="any"
            value={genForm.service_charge_percentage}
            onChange={(e) =>
              setGenForm((p) => ({ ...p, service_charge_percentage: e.target.value }))
            }
          />
          <Select
            label="Discount Type"
            value={genForm.discount_type}
            onChange={(e) => setGenForm((p) => ({ ...p, discount_type: e.target.value }))}
            placeholder="None"
            options={DISCOUNT_TYPES}
          />
          {genForm.discount_type && (
            <Input
              label={genForm.discount_type === "Percentage" ? "Discount %" : "Discount Amount"}
              type="number"
              min="0"
              step="any"
              value={genForm.discount_value}
              onChange={(e) => setGenForm((p) => ({ ...p, discount_value: e.target.value }))}
            />
          )}
        </div>

        {genOrderId && (
          <div className="modal-section">
            <h4 className="modal-section__title">Order Items</h4>
            <ErrorAlert message={genItemsError} />
            {/* Was a bare <table className="table table-sm"> — Bootstrap
                classes in a project with no Bootstrap, so it rendered
                unstyled with no loading or empty treatment. */}
            <TableTemplate
              loading={genItemsLoading}
              emptyMessage="No items on this order."
              searchable={false}
              pagination={false}
              exportable={false}
              columns={[
                {
                  key: "item_name",
                  title: "Item",
                  align: "left",
                  type: "custom",
                  render: menuName,
                },
                { key: "quantity", title: "Qty", align: "right" },
                {
                  key: "price",
                  title: "Price",
                  align: "right",
                  type: "custom",
                  render: (it) => formatPrecise(it.price),
                },
                {
                  key: "amount",
                  title: "Amount",
                  align: "right",
                  type: "custom",
                  render: (it) => formatPrecise(num(it.price) * num(it.quantity)),
                },
              ]}
              data={genOrderItems}
            />
            {genOrderItems.length > 0 && (
              <div className="order-detail__summary">
                <span>
                  <b>Subtotal</b>
                  {formatPrecise(genItemsSubtotal)}
                </span>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={activeModal === "view" && !!selectedBill}
        title={`Bill — ${selectedBill?.bill_number || ""}`}
        onClose={closeModals}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: closeModals },
          {
            label: "Print Bill",
            variant: "outline",
            icon: <Printer size={16} />,
            onClick: printBill,
          },
        ]}
      >
        <ViewSection title="Bill">
          <DetailList columns={3}>
            <DetailItem label="Bill Number" value={selectedBill?.bill_number} />
            <DetailItem label="Order Number" value={selectedBill?.order_number} />
            <DetailItem label="Table" value={selectedBill?.table_code} />
            <DetailItem label="Date" value={formatDate(selectedBill?.bill_date)} />
            <DetailItem label="Time" value={selectedBill?.bill_time} />
            <DetailItem label="Status" value={selectedBill?.bill_status} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Items">
          <TableTemplate
            searchable={false}
            pagination={false}
            exportable={false}
            emptyMessage="No items on this bill."
            columns={[
              { key: "item_name", title: "Item", align: "left" },
              { key: "quantity", title: "Qty", align: "right" },
              {
                key: "rate",
                title: "Rate",
                align: "right",
                type: "custom",
                render: (it) => formatPrecise(it.rate),
              },
              {
                key: "amount",
                title: "Amount",
                align: "right",
                type: "custom",
                render: (it) => formatPrecise(it.amount),
              },
            ]}
            data={billItems}
          />
        </ViewSection>

        <ViewSection title="Summary">
          {/* Was six `<div className="d-flex justify-content-between">` rows —
              Bootstrap classes that do nothing here, so every line rendered as
              a stacked block with the amount under the label. */}
          <DetailList columns={3}>
            <DetailItem label="Subtotal" value={formatPrecise(selectedBill?.sub_total)} />
            <DetailItem label="CGST" value={formatPrecise(selectedBill?.cgst_amount)} />
            <DetailItem label="SGST" value={formatPrecise(selectedBill?.sgst_amount)} />
            <DetailItem
              label="Service Charge"
              value={formatPrecise(selectedBill?.service_charge_amount)}
            />
            <DetailItem
              label="Discount"
              value={formatPrecise(selectedBill?.discount_amount)}
            />
            <DetailItem
              label="Total Payable"
              value={formatPrecise(selectedBill?.grand_total)}
            />
          </DetailList>
        </ViewSection>

        {billPayments.length > 0 && (
          <ViewSection title="Payments">
            <DetailList columns={2}>
              {billPayments.map((p) => (
                <DetailItem
                  key={p.id}
                  label={`${p.payment_reference || "Payment"} (${p.payment_status || "—"})`}
                  value={formatPrecise(p.paid_amount)}
                />
              ))}
            </DetailList>
          </ViewSection>
        )}
      </Modal>

      {/* ================= COLLECT PAYMENT ================= */}
      <Modal
        isOpen={activeModal === "payment" && !!selectedBill}
        title={`Collect Payment — ${selectedBill?.bill_number || ""}`}
        onClose={closeModals}
        size="medium"
        bodyLayout="grid"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModals, disabled: saving },
          {
            label: saving ? "Submitting…" : "Submit",
            variant: "primary",
            onClick: submitPayment,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} className="field-full" />

        <Select
          label="Payment Mode"
          required
          value={payForm.payment_method_id}
          onChange={(e) => setPayForm((p) => ({ ...p, payment_method_id: e.target.value }))}
          placeholder="— select —"
          options={paymentMethods.map((m) => ({ value: m.id, label: m.method_name }))}
        />
        <Input
          label="Amount Paid"
          required
          type="number"
          min="0"
          step="any"
          value={payForm.paid_amount}
          onChange={(e) => setPayForm((p) => ({ ...p, paid_amount: e.target.value }))}
        />
        <Input
          label="Reference Number"
          value={payForm.payment_reference}
          onChange={(e) => setPayForm((p) => ({ ...p, payment_reference: e.target.value }))}
        />
        <div className="field-full">
          <Textarea
            label="Remarks"
            rows={3}
            value={payForm.remarks}
            onChange={(e) => setPayForm((p) => ({ ...p, remarks: e.target.value }))}
          />
        </div>
      </Modal>

      {/* ================= CANCEL BILL ================= */}
      <Modal
        isOpen={activeModal === "cancel" && !!selectedBill}
        title={`Cancel Bill — ${selectedBill?.bill_number || ""}`}
        onClose={closeModals}
        size="medium"
        bodyLayout="single"
        variant="alert"
        showFooter
        actions={[
          { label: "Keep bill", variant: "secondary", onClick: closeModals, disabled: saving },
          {
            label: saving ? "Cancelling…" : "Cancel Bill",
            variant: "error",
            onClick: submitCancelBill,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} />

        <p className="modal-section__hint">
          {`This cancels the bill only — order ${selectedBill?.order_number || ""} stays open, so items can be changed and a fresh bill generated for it.`}
        </p>
        <Textarea
          label="Reason"
          required
          rows={3}
          value={cancelReason}
          onChange={(e) => setCancelReason(e.target.value)}
          placeholder="e.g. wrong tax applied, items changed"
        />
      </Modal>

      <Toast {...toast} />
    </>
  );
};

export default BarBillingPayments;

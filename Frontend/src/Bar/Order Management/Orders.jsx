import React, { useState } from "react";
import { Plus, Send, XCircle } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import IconButton from "../../stories/IconButton";
import Button from "../../stories/Button";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatPrecise } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import "../../stories/OrderDetail.css";

/** `bar_order_type_enum` as the column is declared. */
const ORDER_TYPES = ["At Table", "At Counter", "Takeaway"];

const initialForm = {
  order_type: "At Table",
  table_id: "",
  guest_name: "",
  guest_mobile: "",
  no_of_guests: "",
};

const emptyPick = { menuId: "", variantId: "", qty: 1, note: "" };

const Orders = () => {
  const perms = usePagePermissions("/bar_orders");

  const {
    data: [data, tables, menuItems],
    loading,
    error,
    reload: load,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/bar/order"),
      select: readList,
      fallback: "Failed to load orders.",
    },
    { fetch: () => APICall.getT("/bar/table"), select: readList },
    { fetch: () => APICall.getT("/bar/menu"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [showNewModal, setShowNewModal] = useState(false);
  const [detailOrder, setDetailOrder] = useState(null);
  const [cancelRow, setCancelRow] = useState(null);
  const [removeItemRow, setRemoveItemRow] = useState(null);
  const [saving, setSaving] = useState(false);
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState(null);
  const [formData, setFormData] = useState(initialForm);
  const [pick, setPick] = useState(emptyPick);

  /* ================= HANDLERS ================= */

  const openNewModal = () => {
    setFormData(initialForm);
    setFormError(null);
    setShowNewModal(true);
  };

  const closeNewModal = () => {
    if (saving) return;
    setShowNewModal(false);
    setFormData(initialForm);
    setFormError(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const openDetail = async (row) => {
    try {
      const res = await APICall.getT(`/bar/order/${row.id}`);
      setDetailOrder(res?.data || row);
      setPick(emptyPick);
      setFormError(null);
    } catch (err) {
      showToast(errMsg(err, "Failed to load order detail."), "error");
    }
  };

  const closeDetail = () => {
    setDetailOrder(null);
    setFormError(null);
    load();
  };

  const refreshDetail = async () => {
    const res = await APICall.getT(`/bar/order/${detailOrder.id}`);
    setDetailOrder(res?.data);
  };

  const createOrder = async () => {
    if (saving) return;
    if (formData.order_type === "At Table" && !formData.table_id) {
      setFormError("Select a table for an At Table order.");
      return;
    }

    setFormError(null);
    setSaving(true);
    try {
      const res = await APICall.postT("/bar/order", {
        order_type: formData.order_type,
        table_id: formData.table_id ? Number(formData.table_id) : null,
        guest_name: formData.guest_name.trim() || null,
        guest_mobile: formData.guest_mobile.trim() || null,
        no_of_guests: formData.no_of_guests ? Number(formData.no_of_guests) : null,
      });
      showToast("Order created successfully", "success");
      setShowNewModal(false);
      setFormData(initialForm);
      load();
      // Straight into the item picker: an order with no items is not useful.
      openDetail({ id: res?.data?.id });
    } catch (err) {
      setFormError(errMsg(err, "Failed to create order."));
    } finally {
      setSaving(false);
    }
  };

  const addItem = async () => {
    if (busy) return;
    if (!pick.menuId) {
      setFormError("Choose a menu item to add.");
      return;
    }
    if (!pick.qty || Number(pick.qty) < 1) {
      setFormError("Quantity must be at least one.");
      return;
    }

    setFormError(null);
    setBusy(true);
    try {
      await APICall.postT(`/bar/order/${detailOrder.id}/items`, {
        items: [
          {
            menu_id: Number(pick.menuId),
            variant_id: pick.variantId ? Number(pick.variantId) : null,
            quantity: Number(pick.qty),
            special_instructions: pick.note.trim() || null,
          },
        ],
      });
      showToast("Item added to order", "success");
      setPick(emptyPick);
      await refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to add item."));
    } finally {
      setBusy(false);
    }
  };

  const confirmRemoveItem = async () => {
    const item = removeItemRow;
    setRemoveItemRow(null);
    try {
      await APICall.deleteT(`/bar/order/item/${item.id}`);
      showToast("Item removed from order", "delete");
      await refreshDetail();
    } catch (err) {
      showToast(errMsg(err, "Failed to remove item."), "error");
    }
  };

  const sendToBar = async () => {
    if (busy) return;
    setFormError(null);
    setBusy(true);
    try {
      await APICall.postT(`/bar/order/${detailOrder.id}/confirm`, {});
      showToast("Order sent to the bar", "success");
      await refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to send order to the bar."));
    } finally {
      setBusy(false);
    }
  };

  const markServed = async () => {
    if (busy) return;
    setFormError(null);
    setBusy(true);
    try {
      await APICall.putT(`/bar/order/${detailOrder.id}/status`, {
        order_status: "Served",
      });
      showToast("Order marked as served", "update");
      await refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to mark order as served."));
    } finally {
      setBusy(false);
    }
  };

  // Cancelling used to happen on a single click of a red trash icon, with no
  // confirmation and no feedback — the row simply changed on the next reload.
  const confirmCancel = async () => {
    const row = cancelRow;
    setCancelRow(null);
    try {
      await APICall.putT(`/bar/order/${row.id}/status`, {
        order_status: "Cancelled",
      });
      showToast("Order cancelled", "delete");
      load();
    } catch (err) {
      showToast(errMsg(err, "Failed to cancel order."), "error");
    }
  };

  /* ================= DERIVED ================= */

  const items = detailOrder?.items || [];
  const pendingItemCount = items.filter((i) => i.item_status === "Pending").length;
  const allItemsReady =
    items.length > 0 &&
    items.every((i) => i.item_status === "Ready" || i.item_status === "Served");
  const canMarkServed =
    detailOrder &&
    ["In Progress", "Ready"].includes(detailOrder.order_status) &&
    pendingItemCount === 0 &&
    allItemsReady;
  const canEditItems =
    detailOrder &&
    !["Completed", "Cancelled"].includes(detailOrder.order_status) &&
    perms.edit;

  const pickedMenu = menuItems.find((m) => m.id === Number(pick.menuId));
  const variants = pickedMenu?.variants || [];

  const availableTables = tables
    .filter((t) => t.table_status === "Available")
    .map((t) => ({ value: t.id, label: `${t.table_name} (${t.table_code})` }));

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Orders"
        loading={loading}
        emptyMessage="No orders yet. Add one to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Order",
          onClick: openNewModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "order_number", title: "Order No", align: "left" },
          { key: "order_type", title: "Type", align: "left" },
          // service_location is resolved by the API. This was joined against a
          // separately-fetched table list, so a failed second request left "-"
          // on every at-table row.
          { key: "service_location", title: "Table", align: "left" },
          { key: "guest_name", title: "Guest Name", align: "left" },
          { key: "no_of_guests", title: "Guests", align: "right" },
          {
            key: "grand_total",
            title: "Total Amount",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.grand_total),
            exportValue: (row) => formatPrecise(row.grand_total),
          },
          { key: "order_status", title: "Order Status", align: "center", type: "badge" },
          { key: "payment_status", title: "Payment", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`order ${row.order_number || ""}`.trim()}
                onView={() => openDetail(row)}
              >
                {row.order_status === "New" && perms.delete && (
                  <IconButton
                    variant="action-delete"
                    size="action"
                    icon={<XCircle size={16} />}
                    onClick={() => setCancelRow(row)}
                    title="Cancel order"
                    ariaLabel={`Cancel order ${row.order_number || ""}`}
                  />
                )}
              </RowActions>
            ),
          },
        ]}
        data={data}
      />

      {/* ================= NEW ORDER ================= */}
      <Modal
        isOpen={showNewModal}
        title="Add Order"
        onClose={closeNewModal}
        size="large"
        bodyLayout="grid"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeNewModal, disabled: saving },
          {
            label: saving ? "Creating…" : "Create & Add Items",
            variant: "primary",
            onClick: createOrder,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} className="field-full" />

        <Select
          label="Order Type"
          name="order_type"
          value={formData.order_type}
          onChange={handleChange}
          options={ORDER_TYPES}
        />

        {formData.order_type === "At Table" && (
          <Select
            label="Table"
            required
            name="table_id"
            value={formData.table_id}
            onChange={handleChange}
            placeholder={
              availableTables.length ? "— select —" : "No tables are free right now"
            }
            options={availableTables}
          />
        )}

        <Input
          label="Guest Name"
          name="guest_name"
          value={formData.guest_name}
          onChange={handleChange}
        />
        <Input
          label="Guest Mobile"
          type="tel"
          name="guest_mobile"
          value={formData.guest_mobile}
          onChange={handleChange}
        />
        <Input
          label="No. of Guests"
          type="number"
          min="1"
          name="no_of_guests"
          value={formData.no_of_guests}
          onChange={handleChange}
        />
      </Modal>

      {/* ================= ORDER DETAIL ================= */}
      <Modal
        isOpen={!!detailOrder}
        title={`Order ${detailOrder?.order_number || ""}`}
        onClose={closeDetail}
        size="xlarge"
        bodyLayout="custom"
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: closeDetail },
          ...(pendingItemCount > 0 && canEditItems
            ? [
                {
                  label: `Send ${pendingItemCount} item${pendingItemCount === 1 ? "" : "s"} to Bar`,
                  variant: "primary",
                  icon: <Send size={14} />,
                  onClick: sendToBar,
                  disabled: busy,
                },
              ]
            : []),
          ...(canMarkServed
            ? [{ label: "Mark Served", variant: "primary", onClick: markServed, disabled: busy }]
            : []),
        ]}
      >
        <ErrorAlert message={formError} />

        <div className="order-detail__summary">
          <span>
            <b>Status</b>
            {detailOrder?.order_status}
          </span>
          <span>
            <b>Payment</b>
            {detailOrder?.payment_status}
          </span>
          <span>
            <b>Total</b>
            {formatPrecise(detailOrder?.grand_total)}
          </span>
        </div>

        {/* Was a hand-rolled <table> with per-cell inline styles and hardcoded
            hex colours. TableTemplate gives it the same header, alignment and
            empty state as every other list in the app. */}
        <TableTemplate
          searchable={false}
          pagination={false}
          exportable={false}
          emptyMessage="No items on this order yet."
          columns={[
            {
              key: "item_name",
              title: "Item",
              align: "left",
              type: "custom",
              render: (it) => (
                <>
                  {it.item_name || "Unnamed item"}
                  {it.variant_name ? ` — ${it.variant_name}` : ""}
                  {it.special_instructions && (
                    <span className="order-item__note">{it.special_instructions}</span>
                  )}
                </>
              ),
            },
            { key: "quantity", title: "Qty", align: "right" },
            {
              key: "price",
              title: "Price",
              align: "right",
              type: "custom",
              render: (it) => formatPrecise(it.price),
            },
            { key: "item_status", title: "Status", align: "center", type: "badge" },
            {
              key: "actions",
              title: "",
              align: "center",
              type: "custom",
              excludeFromExport: true,
              render: (it) =>
                it.item_status === "Pending" && canEditItems ? (
                  <RowActions
                    label={it.item_name || "item"}
                    onDelete={() => setRemoveItemRow(it)}
                  />
                ) : null,
            },
          ]}
          data={items}
        />

        {canEditItems && (
          <div className="modal-section">
            <h4 className="modal-section__title">Add an item</h4>
            <div className="order-add-item">
              <Select
                label="Menu Item"
                value={pick.menuId}
                onChange={(e) => setPick((p) => ({ ...p, menuId: e.target.value, variantId: "" }))}
                placeholder="— select —"
                options={menuItems
                  .filter((m) => m.availability_status === "Available")
                  .map((m) => ({
                    value: m.id,
                    label: `${m.item_name} — ${formatPrecise(m.price)}`,
                  }))}
              />
              {variants.length > 0 && (
                <Select
                  label="Variant"
                  value={pick.variantId}
                  onChange={(e) => setPick((p) => ({ ...p, variantId: e.target.value }))}
                  placeholder={`Standard — ${formatPrecise(pickedMenu?.price)}`}
                  options={variants.map((v) => ({
                    value: v.id,
                    label: `${v.variant_name} — ${formatPrecise(v.price)}`,
                  }))}
                />
              )}
              <Input
                label="Qty"
                type="number"
                min="1"
                value={pick.qty}
                onChange={(e) => setPick((p) => ({ ...p, qty: e.target.value }))}
              />
              <Input
                label="Note"
                value={pick.note}
                onChange={(e) => setPick((p) => ({ ...p, note: e.target.value }))}
                placeholder="Special instructions"
              />
              <Button variant="primary" onClick={addItem} disabled={busy}>
                <Plus size={14} aria-hidden="true" /> Add
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* ================= CANCEL ORDER ================= */}
      <ConfirmModal
        isOpen={!!cancelRow}
        onClose={() => setCancelRow(null)}
        onConfirm={confirmCancel}
        title="Cancel Order"
        confirmText="Cancel order"
        cancelText="Keep order"
        size="small"
        destructive
      >
        {`Cancel order ${cancelRow?.order_number || ""}? This cannot be undone.`}
      </ConfirmModal>

      {/* ================= REMOVE ITEM ================= */}
      <ConfirmModal
        isOpen={!!removeItemRow}
        onClose={() => setRemoveItemRow(null)}
        onConfirm={confirmRemoveItem}
        title="Remove Item"
        confirmText="Remove"
        size="small"
        destructive
      >
        {`Remove ${removeItemRow?.item_name || "this item"} from the order?`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Orders;

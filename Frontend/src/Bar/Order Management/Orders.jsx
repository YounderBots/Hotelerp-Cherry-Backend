import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Trash2, Plus, Send } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const ORDER_TYPES = ["At Table", "At Counter", "Takeaway"];

const Orders = () => {
  const [data, setData] = useState([]);
  const [tables, setTables] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showNewModal, setShowNewModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailOrder, setDetailOrder] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = {
    order_type: "At Table",
    table_id: "",
    guest_name: "",
    guest_mobile: "",
    no_of_guests: "",
  };
  const [formData, setFormData] = useState(initialForm);

  const [pickMenuId, setPickMenuId] = useState("");
  const [pickVariantId, setPickVariantId] = useState("");
  const [pickQty, setPickQty] = useState(1);
  const [pickNote, setPickNote] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([
      APICall.getT("/bar/order"),
      APICall.getT("/bar/table"),
      APICall.getT("/bar/menu"),
    ]).then(([oRes, tRes, mRes]) => {
      setData(oRes.status === "fulfilled" ? readList(oRes.value) : []);
      setTables(tRes.status === "fulfilled" ? readList(tRes.value) : []);
      setMenuItems(mRes.status === "fulfilled" ? readList(mRes.value) : []);
      if (oRes.status === "rejected") setError(errMsg(oRes.reason, "Failed to load orders."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const tableLabel = (id) => {
    const t = tables.find((x) => x.id === id);
    return t ? `${t.table_name} (${t.table_code})` : "-";
  };

  const openNewModal = () => {
    setFormData(initialForm);
    setFormError(null);
    setShowNewModal(true);
  };
  const closeNewModal = () => {
    if (saving) return;
    setShowNewModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const createOrder = async () => {
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
        guest_name: formData.guest_name || null,
        guest_mobile: formData.guest_mobile || null,
        no_of_guests: formData.no_of_guests ? Number(formData.no_of_guests) : null,
      });
      setShowNewModal(false);
      load();
      openDetail({ id: res?.data?.id, order_number: res?.data?.order_number, order_status: "New" });
    } catch (err) {
      setFormError(errMsg(err, "Failed to create order."));
    } finally {
      setSaving(false);
    }
  };

  const openDetail = async (row) => {
    setError(null);
    try {
      const res = await APICall.getT(`/bar/order/${row.id}`);
      setDetailOrder(res?.data || row);
      setPickMenuId("");
      setPickVariantId("");
      setPickQty(1);
      setPickNote("");
      setShowDetailModal(true);
    } catch (err) {
      setError(errMsg(err, "Failed to load order detail."));
    }
  };
  const closeDetail = () => {
    setShowDetailModal(false);
    setDetailOrder(null);
    load();
  };

  const refreshDetail = async () => {
    const res = await APICall.getT(`/bar/order/${detailOrder.id}`);
    setDetailOrder(res?.data);
  };

  const addItem = async () => {
    if (!pickMenuId || !pickQty) return;
    setFormError(null);
    try {
      await APICall.postT(`/bar/order/${detailOrder.id}/items`, {
        items: [
          {
            menu_id: Number(pickMenuId),
            variant_id: pickVariantId ? Number(pickVariantId) : null,
            quantity: Number(pickQty),
            special_instructions: pickNote || null,
          },
        ],
      });
      setPickMenuId("");
      setPickVariantId("");
      setPickQty(1);
      setPickNote("");
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to add item."));
    }
  };

  const removeItem = async (orderItemId) => {
    try {
      await APICall.deleteT(`/bar/order/item/${orderItemId}`);
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to remove item."));
    }
  };

  const sendToStation = async () => {
    setFormError(null);
    try {
      await APICall.postT(`/bar/order/${detailOrder.id}/confirm`, {});
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to send order to the bar."));
    }
  };

  const cancelOrder = async (row) => {
    try {
      await APICall.putT(`/bar/order/${row.id}/status`, { order_status: "Cancelled" });
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to cancel order."));
    }
  };

  const markServed = async () => {
    setFormError(null);
    try {
      await APICall.putT(`/bar/order/${detailOrder.id}/status`, { order_status: "Served" });
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to mark order as served."));
    }
  };

  const pendingItemCount = (detailOrder?.items || []).filter((i) => i.item_status === "Pending").length;
  const hasItems = (detailOrder?.items || []).length > 0;
  const allItemsReady = hasItems && (detailOrder.items || []).every((i) => i.item_status === "Ready" || i.item_status === "Served");
  const canMarkServed = detailOrder && ["In Progress", "Ready"].includes(detailOrder.order_status) && pendingItemCount === 0 && allItemsReady;

  const selectedPickMenu = menuItems.find((m) => m.id === Number(pickMenuId));

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Orders"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Order",
          onClick: openNewModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "order_number", title: "Order No", align: "center" },
          { key: "order_type", title: "Type", align: "center" },
          { key: "table_id", title: "Table", align: "center", type: "custom", render: (row) => (row.order_type === "Takeaway" ? "-" : tableLabel(row.table_id)) },
          { key: "guest_name", title: "Guest Name", align: "center" },
          { key: "no_of_guests", title: "Guests", align: "center" },
          { key: "grand_total", title: "Total Amount", align: "center" },
          { key: "order_status", title: "Order Status", align: "center", type: "badge" },
          { key: "payment_status", title: "Payment", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openDetail(row)} />
                {row.order_status === "New" && (
                  <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} ariaLabel="Cancel order" onClick={() => cancelOrder(row)} />
                )}
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showNewModal && (
        <Modal
          isOpen
          title="Add Order"
          onClose={closeNewModal}
          size="large"
          bodyLayout="grid"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeNewModal, disabled: saving },
            { label: saving ? "Creating…" : "Create & Add Items", variant: "primary", onClick: createOrder, disabled: saving },
          ]}
        >
          {formError && (
            <div style={{ gridColumn: "1 / -1" }}>
              <ErrorAlert message={formError} />
            </div>
          )}

          <Select
            label="Order Type"
            name="order_type"
            value={formData.order_type}
            onChange={handleChange}
            options={ORDER_TYPES.map((t) => ({ value: t, label: t }))}
          />

          {formData.order_type === "At Table" && (
            <Select
              label="Table"
              required
              name="table_id"
              value={formData.table_id}
              onChange={handleChange}
              options={tables.filter((t) => t.table_status === "Available").map((t) => ({ value: t.id, label: `${t.table_name} (${t.table_code})` }))}
              placeholder="— select —"
            />
          )}

          <Input label="Guest Name" name="guest_name" value={formData.guest_name} onChange={handleChange} />
          <Input label="Guest Mobile" name="guest_mobile" value={formData.guest_mobile} onChange={handleChange} />
          <Input label="No. of Guests" type="number" name="no_of_guests" value={formData.no_of_guests} onChange={handleChange} />
        </Modal>
      )}

      {showDetailModal && detailOrder && (
        <Modal
          isOpen
          title={`Order ${detailOrder.order_number}`}
          onClose={closeDetail}
          size="large"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeDetail },
            ...(pendingItemCount > 0 ? [{ label: `Send ${pendingItemCount} item(s) to Bar`, icon: <Send size={14} />, variant: "primary", onClick: sendToStation }] : []),
            ...(canMarkServed ? [{ label: "Mark Served", variant: "primary", onClick: markServed }] : []),
          ]}
        >
          <ErrorAlert message={formError} />

          <p><strong>Status:</strong> {detailOrder.order_status} &nbsp; <strong>Payment:</strong> {detailOrder.payment_status}</p>

          <table style={{ width: "100%", marginBottom: "16px" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>Item</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {(detailOrder.items || []).map((it) => {
                const menu = menuItems.find((m) => m.id === it.menu_id);
                return (
                  <tr key={it.id}>
                    <td>
                      {menu?.item_name || `#${it.menu_id}`}
                      {it.variant_name ? ` — ${it.variant_name}` : ""}
                      {it.special_instructions && (
                        <div style={{ fontSize: "12px", color: "#64748b" }}>{it.special_instructions}</div>
                      )}
                    </td>
                    <td style={{ textAlign: "center" }}>{it.quantity}</td>
                    <td style={{ textAlign: "center" }}>{it.price}</td>
                    <td style={{ textAlign: "center" }}>{it.item_status}</td>
                    <td style={{ textAlign: "center" }}>
                      {it.item_status === "Pending" && (
                        <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={14} />} ariaLabel="Remove item" onClick={() => removeItem(it.id)} />
                      )}
                    </td>
                  </tr>
                );
              })}
              {(!detailOrder.items || detailOrder.items.length === 0) && (
                <tr><td colSpan={5} style={{ textAlign: "center", color: "#9ca3af" }}>No items yet</td></tr>
              )}
            </tbody>
          </table>

          {detailOrder.order_status !== "Completed" && detailOrder.order_status !== "Cancelled" && (
            <div style={{ display: "flex", gap: "8px", alignItems: "flex-end", flexWrap: "wrap" }}>
              <div style={{ minWidth: "200px" }}>
                <Select
                  label="Menu Item"
                  value={pickMenuId}
                  onChange={(e) => {
                    setPickMenuId(e.target.value);
                    setPickVariantId("");
                  }}
                  options={menuItems.filter((m) => m.availability_status === "Available").map((m) => ({ value: m.id, label: `${m.item_name} — ${m.price}` }))}
                  placeholder="— select —"
                />
              </div>
              {(selectedPickMenu?.variants || []).length > 0 && (
                <div style={{ minWidth: "150px" }}>
                  <Select
                    label="Variant"
                    value={pickVariantId}
                    onChange={(e) => setPickVariantId(e.target.value)}
                    options={selectedPickMenu.variants.map((v) => ({ value: v.id, label: `${v.variant_name} — ${v.price}` }))}
                    placeholder={`Standard — ${selectedPickMenu?.price}`}
                  />
                </div>
              )}
              <div style={{ width: "90px" }}>
                <Input label="Qty" type="number" min="1" value={pickQty} onChange={(e) => setPickQty(e.target.value)} />
              </div>
              <div style={{ flex: 1, minWidth: "160px" }}>
                <Input label="Note" value={pickNote} onChange={(e) => setPickNote(e.target.value)} placeholder="Special instructions" />
              </div>
              <Button variant="primary" onClick={addItem}><Plus size={14} /> Add</Button>
            </div>
          )}
        </Modal>
      )}
    </>
  );
};

export default Orders;

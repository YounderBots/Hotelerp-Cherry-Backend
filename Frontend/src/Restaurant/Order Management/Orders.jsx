import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Trash2, X, Plus, Send } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const ORDER_TYPES = ["Dine-In", "Takeaway", "Delivery", "Room Service"];

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
    order_type: "Dine-In",
    table_id: "",
    room_no: "",
    guest_name: "",
    guest_mobile: "",
    no_of_guests: "",
  };
  const [formData, setFormData] = useState(initialForm);

  const [pickMenuId, setPickMenuId] = useState("");
  const [pickQty, setPickQty] = useState(1);
  const [pickNote, setPickNote] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([
      APICall.getT("/restaurant/order"),
      APICall.getT("/restaurant/table"),
      APICall.getT("/restaurant/menu"),
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
    if (formData.order_type === "Dine-In" && !formData.table_id) {
      setFormError("Select a table for a Dine-In order.");
      return;
    }
    if (formData.order_type === "Room Service" && !formData.room_no.trim()) {
      setFormError("Room number is required for Room Service.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      const res = await APICall.postT("/restaurant/order", {
        order_type: formData.order_type,
        table_id: formData.table_id ? Number(formData.table_id) : null,
        room_no: formData.room_no || null,
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
      const res = await APICall.getT(`/restaurant/order/${row.id}`);
      setDetailOrder(res?.data || row);
      setPickMenuId("");
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
    const res = await APICall.getT(`/restaurant/order/${detailOrder.id}`);
    setDetailOrder(res?.data);
  };

  const addItem = async () => {
    if (!pickMenuId || !pickQty) return;
    setFormError(null);
    try {
      await APICall.postT(`/restaurant/order/${detailOrder.id}/items`, {
        items: [{ menu_id: Number(pickMenuId), quantity: Number(pickQty), special_instructions: pickNote || null }],
      });
      setPickMenuId("");
      setPickQty(1);
      setPickNote("");
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to add item."));
    }
  };

  const removeItem = async (orderItemId) => {
    try {
      await APICall.deleteT(`/restaurant/order/item/${orderItemId}`);
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to remove item."));
    }
  };

  const sendToKitchen = async () => {
    setFormError(null);
    try {
      await APICall.postT(`/restaurant/order/${detailOrder.id}/confirm`, {});
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to send order to the kitchen."));
    }
  };

  const cancelOrder = async (row) => {
    try {
      await APICall.putT(`/restaurant/order/${row.id}/status`, { order_status: "Cancelled" });
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to cancel order."));
    }
  };

  const markServed = async () => {
    setFormError(null);
    try {
      await APICall.putT(`/restaurant/order/${detailOrder.id}/status`, { order_status: "Served" });
      refreshDetail();
    } catch (err) {
      setFormError(errMsg(err, "Failed to mark order as served."));
    }
  };

  const pendingItemCount = (detailOrder?.items || []).filter((i) => i.item_status === "Pending").length;
  const hasItems = (detailOrder?.items || []).length > 0;
  const allItemsReady = hasItems && (detailOrder.items || []).every((i) => i.item_status === "Ready" || i.item_status === "Served");
  const canMarkServed = detailOrder && ["In Progress", "Ready"].includes(detailOrder.order_status) && pendingItemCount === 0 && allItemsReady;

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Orders"
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
          { key: "table_id", title: "Table/Room", align: "center", type: "custom", render: (row) => (row.order_type === "Room Service" ? row.room_no : tableLabel(row.table_id)) },
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
                <button className="table-action-btn view" onClick={() => openDetail(row)}>
                  <Eye size={16} />
                </button>
                {row.order_status === "New" && (
                  <button className="table-action-btn delete" onClick={() => cancelOrder(row)}>
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showNewModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Add Order</h3>
              <button onClick={closeNewModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body grid">
              <div className="form-group">
                <label>Order Type</label>
                <select name="order_type" value={formData.order_type} onChange={handleChange}>
                  {ORDER_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              {formData.order_type === "Dine-In" && (
                <div className="form-group">
                  <label>Table <span className="required">*</span></label>
                  <select name="table_id" value={formData.table_id} onChange={handleChange}>
                    <option value="">— select —</option>
                    {tables.filter((t) => t.table_status === "Available").map((t) => (
                      <option key={t.id} value={t.id}>{t.table_name} ({t.table_code})</option>
                    ))}
                  </select>
                </div>
              )}

              {formData.order_type === "Room Service" && (
                <div className="form-group">
                  <label>Room No <span className="required">*</span></label>
                  <input name="room_no" value={formData.room_no} onChange={handleChange} />
                </div>
              )}

              <div className="form-group">
                <label>Guest Name</label>
                <input name="guest_name" value={formData.guest_name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Guest Mobile</label>
                <input name="guest_mobile" value={formData.guest_mobile} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>No. of Guests</label>
                <input type="number" name="no_of_guests" value={formData.no_of_guests} onChange={handleChange} />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeNewModal} disabled={saving}>Close</button>
              <button className="btn primary" onClick={createOrder} disabled={saving}>{saving ? "Creating…" : "Create & Add Items"}</button>
            </div>
          </div>
        </div>
      )}

      {showDetailModal && detailOrder && (
        <div className="modal-overlay">
          <div className="modal-card modal-lg">
            <div className="modal-header">
              <h3>Order {detailOrder.order_number}</h3>
              <button onClick={closeDetail}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
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
                        <td>{menu?.item_name || `#${it.menu_id}`}</td>
                        <td style={{ textAlign: "center" }}>{it.quantity}</td>
                        <td style={{ textAlign: "center" }}>{it.price}</td>
                        <td style={{ textAlign: "center" }}>{it.item_status}</td>
                        <td style={{ textAlign: "center" }}>
                          {it.item_status === "Pending" && (
                            <button className="table-action-btn delete" onClick={() => removeItem(it.id)}>
                              <Trash2 size={14} />
                            </button>
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
                  <div className="form-group" style={{ minWidth: "200px" }}>
                    <label>Menu Item</label>
                    <select value={pickMenuId} onChange={(e) => setPickMenuId(e.target.value)}>
                      <option value="">— select —</option>
                      {menuItems.filter((m) => m.availability_status === "Available").map((m) => (
                        <option key={m.id} value={m.id}>{m.item_name} — {m.price}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group" style={{ width: "90px" }}>
                    <label>Qty</label>
                    <input type="number" min="1" value={pickQty} onChange={(e) => setPickQty(e.target.value)} />
                  </div>
                  <div className="form-group" style={{ flex: 1, minWidth: "160px" }}>
                    <label>Note</label>
                    <input value={pickNote} onChange={(e) => setPickNote(e.target.value)} placeholder="Special instructions" />
                  </div>
                  <button className="btn primary" onClick={addItem}><Plus size={14} /> Add</button>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeDetail}>Close</button>
              {pendingItemCount > 0 && (
                <button className="btn primary" onClick={sendToKitchen}><Send size={14} /> Send {pendingItemCount} item(s) to Kitchen</button>
              )}
              {canMarkServed && (
                <button className="btn primary" onClick={markServed}>Mark Served</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Orders;

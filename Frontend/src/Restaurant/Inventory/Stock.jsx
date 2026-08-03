import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Pencil, Activity } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const Stock = () => {
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [activeModal, setActiveModal] = useState(null); // view | adjust | movement | add-item
  const [selectedItem, setSelectedItem] = useState(null);
  const [movements, setMovements] = useState([]);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const [adjustForm, setAdjustForm] = useState({ direction: "Add", quantity: "", transaction_type: "ADJUSTMENT", remarks: "" });
  const [newItemForm, setNewItemForm] = useState({ item_name: "", unit: "Kg", min_stock_level: "" });

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    APICall.getT("/restaurant/inventory_stock")
      .then((res) => setStockData(readList(res)))
      .catch((err) => setError(errMsg(err, "Failed to load stock.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openModal = async (type, row) => {
    setSelectedItem(row);
    setFormError(null);
    if (type === "adjust") setAdjustForm({ direction: "Add", quantity: "", transaction_type: "ADJUSTMENT", remarks: "" });
    if (type === "movement") {
      try {
        const res = await APICall.getT(`/restaurant/inventory_item/${row.inventory_item_id}/transactions`);
        setMovements(readList(res));
      } catch (err) {
        setError(errMsg(err, "Failed to load stock movements."));
        setMovements([]);
      }
    }
    setActiveModal(type);
  };

  const openAddItemModal = () => {
    setNewItemForm({ item_name: "", unit: "Kg", min_stock_level: "" });
    setFormError(null);
    setActiveModal("add-item");
  };

  const closeModal = () => {
    if (saving) return;
    setSelectedItem(null);
    setMovements([]);
    setActiveModal(null);
  };

  const saveNewItem = async () => {
    if (!newItemForm.item_name.trim()) {
      setFormError("Item name is required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await APICall.postT("/restaurant/inventory_item", {
        item_name: newItemForm.item_name.trim(),
        unit: newItemForm.unit,
        min_stock_level: newItemForm.min_stock_level ? Number(newItemForm.min_stock_level) : 0,
      });
      closeModal();
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to create item."));
    } finally {
      setSaving(false);
    }
  };

  const saveAdjustment = async () => {
    if (!adjustForm.quantity) {
      setFormError("Quantity is required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      const signed = adjustForm.direction === "Add" ? Number(adjustForm.quantity) : -Number(adjustForm.quantity);
      await APICall.postT("/restaurant/inventory_stock/adjust", {
        inventory_item_id: selectedItem.inventory_item_id,
        kitchen_id: selectedItem.kitchen_id || null,
        quantity: signed,
        transaction_type: adjustForm.transaction_type,
        remarks: adjustForm.remarks || null,
      });
      closeModal();
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to adjust stock."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ marginBottom: 4 }}>Stock Management</h3>
        <div style={{ fontSize: 13, color: "#64748b" }}>Restaurant → Inventory → Stock</div>
      </div>

      <ErrorAlert message={error} />

      <TableTemplate
        title="Stock List"
        searchable
        pagination
        loading={loading}
        hasActionButton
        actionButton={{ label: "Add Item", onClick: openAddItemModal, size: "medium", variant: "primary" }}
        columns={[
          { key: "item_name", title: "Item Name" },
          { key: "unit", title: "Unit", align: "center" },
          { key: "kitchen_id", title: "Store", align: "center", type: "custom", render: (row) => (row.kitchen_id ? `Kitchen #${row.kitchen_id}` : "Main Store") },
          { key: "available_quantity", title: "Available Qty", align: "center" },
          { key: "min_stock_level", title: "Minimum Stock", align: "center" },
          { key: "below_minimum", title: "Stock Status", align: "center", type: "custom", render: (row) => <span className="badge">{row.below_minimum ? "Low Stock" : "In Stock"}</span> },
          { key: "last_updated_date", title: "Last Updated" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", justifyContent: "center", gap: "8px", flexWrap: "nowrap" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openModal("view", row)} />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} ariaLabel="Adjust" onClick={() => openModal("adjust", row)} />
                <IconButton variant="danger-ghost" size="small" icon={<Activity size={16} />} ariaLabel="Movements" onClick={() => openModal("movement", row)} />
              </div>
            ),
          },
        ]}
        data={stockData}
      />

      {activeModal === "view" && selectedItem && (
        <Modal
          isOpen
          title={`Stock Details – ${selectedItem.item_name}`}
          onClose={closeModal}
          size="medium"
          bodyLayout="single"
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeModal }]}
        >
          <p><strong>Store:</strong> {selectedItem.kitchen_id ? `Kitchen #${selectedItem.kitchen_id}` : "Main Store"}</p>
          <p><strong>Available Qty:</strong> {selectedItem.available_quantity} {selectedItem.unit}</p>
          <p><strong>Minimum Stock:</strong> {selectedItem.min_stock_level}</p>
          <p><strong>Last Updated:</strong> {selectedItem.last_updated_date}</p>
        </Modal>
      )}

      {activeModal === "add-item" && (
        <Modal
          isOpen
          title="Add Inventory Item"
          onClose={closeModal}
          size="medium"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Save Item", variant: "primary", onClick: saveNewItem, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />
          <Input label="Item Name" value={newItemForm.item_name} onChange={(e) => setNewItemForm((p) => ({ ...p, item_name: e.target.value }))} />
          <Select
            label="Unit"
            value={newItemForm.unit}
            onChange={(e) => setNewItemForm((p) => ({ ...p, unit: e.target.value }))}
            options={["Kg", "Gram", "Litre", "ml", "Nos"]}
          />
          <Input label="Minimum Stock Level" type="number" value={newItemForm.min_stock_level} onChange={(e) => setNewItemForm((p) => ({ ...p, min_stock_level: e.target.value }))} />
        </Modal>
      )}

      {activeModal === "adjust" && selectedItem && (
        <Modal
          isOpen
          title={`Adjust Stock – ${selectedItem.item_name}`}
          onClose={closeModal}
          size="medium"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Save Adjustment", variant: "primary", onClick: saveAdjustment, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />
          <Select
            label="Adjustment Type"
            value={adjustForm.direction}
            onChange={(e) => setAdjustForm((p) => ({ ...p, direction: e.target.value }))}
            options={["Add", "Reduce"]}
          />
          <Input label="Quantity" type="number" value={adjustForm.quantity} onChange={(e) => setAdjustForm((p) => ({ ...p, quantity: e.target.value }))} />
          <Select
            label="Reason"
            value={adjustForm.transaction_type}
            onChange={(e) => setAdjustForm((p) => ({ ...p, transaction_type: e.target.value }))}
            options={[
              { value: "ADJUSTMENT", label: "Correction" },
              { value: "WASTE", label: "Wastage / Damage" },
            ]}
          />
          <div className="form-group">
            <label>Remarks</label>
            <textarea rows="2" value={adjustForm.remarks} onChange={(e) => setAdjustForm((p) => ({ ...p, remarks: e.target.value }))} />
          </div>
        </Modal>
      )}

      {activeModal === "movement" && selectedItem && (
        <Modal
          isOpen
          title={`Stock Movements – ${selectedItem.item_name}`}
          onClose={closeModal}
          size="xlarge"
          bodyLayout="single"
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeModal }]}
        >
          <table className="table table-hover">
            <thead>
              <tr>
                <th>Date & Time</th>
                <th>Type</th>
                <th>Qty</th>
                <th>Reference</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {movements.length === 0 ? (
                <tr><td colSpan="5" style={{ textAlign: "center" }}>No movements found</td></tr>
              ) : (
                movements.map((m) => (
                  <tr key={m.id}>
                    <td>{new Date(m.created_at).toLocaleString()}</td>
                    <td>{m.transaction_type}</td>
                    <td>{m.quantity}</td>
                    <td>{m.reference_type}{m.reference_id ? ` (${m.reference_id})` : ""}</td>
                    <td>{m.remarks || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Modal>
      )}
    </>
  );
};

export default Stock;

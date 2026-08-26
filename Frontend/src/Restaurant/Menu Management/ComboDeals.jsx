import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Input from "../../stories/Form/Input";
import ErrorAlert from "../../stories/ErrorAlert";
import { ChipGroup } from "../../stories/Chip";
import RepeatableRowEditor from "../../stories/RepeatableRowEditor";
import { Eye, Pencil, Trash2 } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";

const emptyItem = () => ({ menu_id: "", quantity: 1 });

const initialForm = {
  combo_name: "",
  description: "",
  combo_price: "",
  valid_from: "",
  valid_to: "",
};

const ComboDeals = () => {
  const {
    data: [combos, menuItems],
    loading,
    error,
    setError,
    reload: load,
  } = useApiResources([
    { fetch: () => APICall.getT("/restaurant/combo"), select: readList,
      fallback: "Failed to load combo deals." },
    { fetch: () => APICall.getT("/restaurant/menu"), select: readList },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const [formData, setFormData] = useState(initialForm);
  const [items, setItems] = useState([emptyItem()]);

  const menuItemName = (id) => menuItems.find((m) => m.id === id)?.item_name || `#${id}`;

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setItems([emptyItem()]);
    setFormError(null);
    setShowModal(true);
  };
  const openEditModal = (row) => {
    setEditId(row.id);
    setFormData({
      combo_name: row.combo_name || "",
      description: row.description || "",
      combo_price: row.combo_price ?? "",
      valid_from: row.valid_from ? row.valid_from.slice(0, 10) : "",
      valid_to: row.valid_to ? row.valid_to.slice(0, 10) : "",
    });
    setItems(
      (row.items || []).length
        ? row.items.map((it) => ({ menu_id: String(it.menu_id), quantity: it.quantity }))
        : [emptyItem()]
    );
    setFormError(null);
    setShowModal(true);
  };
  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
  };

  const handleDelete = async (row) => {
    try {
      await APICall.deleteT(`/restaurant/combo/${row.id}`);
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to delete combo deal."));
    }
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const addItemRow = () => setItems((rows) => [...rows, emptyItem()]);
  const updateItemRow = (idx, field, value) =>
    setItems((rows) => rows.map((row, i) => (i === idx ? { ...row, [field]: value } : row)));
  const removeItemRow = (idx) => setItems((rows) => rows.filter((_, i) => i !== idx));

  const handleSave = async () => {
    const cleanItems = items.filter((it) => it.menu_id);
    if (!formData.combo_name.trim() || !formData.combo_price) {
      setFormError("Combo name and price are required.");
      return;
    }
    if (cleanItems.length === 0) {
      setFormError("Add at least one menu item to the combo.");
      return;
    }
    setFormError(null);
    setSaving(true);
    const payload = {
      combo_name: formData.combo_name.trim(),
      description: formData.description || null,
      combo_price: Number(formData.combo_price),
      valid_from: formData.valid_from ? new Date(formData.valid_from).toISOString() : null,
      valid_to: formData.valid_to ? new Date(formData.valid_to).toISOString() : null,
      items: cleanItems.map((it) => ({ menu_id: Number(it.menu_id), quantity: Number(it.quantity) || 1 })),
    };
    try {
      if (editId) {
        await APICall.putT(`/restaurant/combo/${editId}`, payload);
      } else {
        await APICall.postT("/restaurant/combo", payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save combo deal."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Combo / Package Deals"
        hasActionButton
        searchable
        pagination
        loading={loading}
        actionButton={{ label: "Add Combo", onClick: openAddModal, size: "medium", variant: "primary" }}
        columns={[
          { key: "combo_code", title: "Combo Code", align: "center" },
          { key: "combo_name", title: "Combo Name" },
          { key: "combo_price", title: "Price", align: "center" },
          {
            key: "items",
            title: "Items",
            align: "center",
            type: "custom",
            render: (row) => (row.items?.length ? `${row.items.length} item${row.items.length > 1 ? "s" : ""}` : "—"),
          },
          {
            key: "valid_to",
            title: "Valid Until",
            align: "center",
            type: "custom",
            render: (row) => (row.valid_to ? new Date(row.valid_to).toLocaleDateString() : "No expiry"),
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openViewModal(row)} />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} ariaLabel="Edit" onClick={() => openEditModal(row)} />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} ariaLabel="Delete" onClick={() => handleDelete(row)} />
              </div>
            ),
          },
        ]}
        data={combos}
      />

      {!loading && combos.length === 0 && !error && (
        <p style={{ color: "#64748b", marginTop: "12px" }}>
          No combo deals yet. Use "Add Combo" to bundle two or more menu items at a package price.
        </p>
      )}

      {showViewModal && viewData && (
        <Modal
          isOpen
          title={viewData.combo_name}
          onClose={closeViewModal}
          size="small"
          bodyLayout="single"
          viewMode
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          <Input label="Combo Code" value={viewData.combo_code || "-"} disabled />
          <Input label="Description" value={viewData.description || "—"} disabled />
          <Input label="Combo Price" value={viewData.combo_price ?? "-"} disabled />
          <Input label="Valid From" value={viewData.valid_from ? new Date(viewData.valid_from).toLocaleDateString() : "—"} disabled />
          <Input label="Valid To" value={viewData.valid_to ? new Date(viewData.valid_to).toLocaleDateString() : "No expiry"} disabled />
          <div className="form-group">
            <label>Included Items</label>
            <ChipGroup
              items={(viewData.items || []).map((it) => ({
                key: it.id || `${it.menu_id}-${it.quantity}`,
                label: `${menuItemName(it.menu_id)} × ${it.quantity}`,
              }))}
            />
          </div>
        </Modal>
      )}

      {showModal && (
        <Modal
          isOpen
          title={editId ? "Edit Combo Deal" : "Add Combo Deal"}
          onClose={closeModal}
          size="large"
          bodyLayout="grid"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Submit", variant: "primary", onClick: handleSave, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <Input label="Combo Name" required name="combo_name" value={formData.combo_name} onChange={handleChange} />

          <Input label="Combo Price" required type="number" name="combo_price" value={formData.combo_price} onChange={handleChange} />

          <Input label="Valid From" type="date" name="valid_from" value={formData.valid_from} onChange={handleChange} />

          <Input label="Valid To" type="date" name="valid_to" value={formData.valid_to} onChange={handleChange} min={formData.valid_from || undefined} />

          <div style={{ gridColumn: "1 / -1" }}>
            <Input label="Description" name="description" value={formData.description} onChange={handleChange} />
          </div>

          <div className="form-group" style={{ gridColumn: "1 / -1" }}>
            <label>Included Items <span className="required">*</span></label>
            <RepeatableRowEditor
              rows={items}
              fields={[
                {
                  key: "menu_id",
                  placeholder: "— select menu item —",
                  type: "select",
                  options: menuItems.map((m) => ({ value: m.id, label: m.item_name })),
                },
                { key: "quantity", placeholder: "Qty", type: "number" },
              ]}
              onFieldChange={(index, key, value) => updateItemRow(index, key, value)}
              onAdd={addItemRow}
              onRemove={(index) => removeItemRow(index)}
              addLabel="+ Add Item"
              emptyLabel="No items added yet."
            />
          </div>
        </Modal>
      )}
    </>
  );
};

export default ComboDeals;

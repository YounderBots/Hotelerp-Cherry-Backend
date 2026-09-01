import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import Input from "../../stories/Form/Input";
import Textarea from "../../stories/Form/Textarea";
import DetailList, { DetailItem } from "../../stories/DetailList";
import Toast from "../../stories/Toast";
import ErrorAlert from "../../stories/ErrorAlert";
import { ChipGroup } from "../../stories/Chip";
import RepeatableRowEditor from "../../stories/RepeatableRowEditor";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatDate, formatPrecise } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

const emptyItem = () => ({ menu_id: "", quantity: 1 });

const initialForm = {
  combo_name: "",
  description: "",
  combo_price: "",
  valid_from: "",
  valid_to: "",
};

const ComboDeals = () => {
  const perms = usePagePermissions("/combo_deals");
  const { toast, showToast } = useToast();
  const [deleteRow, setDeleteRow] = useState(null);

  const {
    data: [combos, menuItems],
    loading,
    error,
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

  // An unknown id reads as "—" rather than "#42": a row number tells the
  // user nothing.
  const menuItemName = (id) => menuItems.find((m) => m.id === id)?.item_name || "—";

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

  // Was wired straight to the trash icon: one click deleted a combo with no
  // confirmation and no feedback.
  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    try {
      await APICall.deleteT(`/restaurant/combo/${row.id}`);
      showToast("Combo deal deleted successfully", "delete");
      load();
    } catch (err) {
      showToast(errMsg(err, "Failed to delete combo deal."), "error");
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
        emptyMessage='No combo deals yet. Use "Add Combo" to bundle two or more menu items at a package price.'
        hasActionButton={perms.add}
        exportable
        searchable
        pagination
        loading={loading}
        actionButton={{ label: "Add Combo", onClick: openAddModal, size: "medium", variant: "primary" }}
        columns={[
          { key: "combo_code", title: "Combo Code", align: "center" },
          { key: "combo_name", title: "Combo Name" },
          {
            key: "combo_price",
            title: "Price",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.combo_price),
            exportValue: (row) => formatPrecise(row.combo_price),
          },
          {
            key: "items",
            title: "Items",
            align: "right",
            type: "custom",
            render: (row) => row.items?.length || 0,
            exportValue: (row) => String(row.items?.length || 0),
          },
          {
            key: "valid_to",
            title: "Valid Until",
            align: "center",
            type: "custom",
            // `new Date(...)` on a plain calendar date shifts it a day west of
            // Greenwich; formatDate reads the string as the date it is.
            render: (row) => (row.valid_to ? formatDate(row.valid_to) : "No expiry"),
            exportValue: (row) => (row.valid_to ? formatDate(row.valid_to) : "No expiry"),
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <RowActions
                label={row.combo_name || "combo"}
                canEdit={perms.edit}
                canDelete={perms.delete}
                onView={() => openViewModal(row)}
                onEdit={() => openEditModal(row)}
                onDelete={() => setDeleteRow(row)}
              />
            ),
          },
        ]}
        data={combos}
      />

      {showViewModal && viewData && (
        <Modal
          isOpen
          title={viewData.combo_name}
          onClose={closeViewModal}
          size="medium"
          bodyLayout="single"
          viewMode
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          {/* Every field here used to be an `<Input ... disabled />` — a form
              control the user could tab into, with a "switched off" border. */}
          <DetailList columns={2}>
            <DetailItem label="Combo Code" value={viewData.combo_code} />
            <DetailItem label="Combo Price" value={formatPrecise(viewData.combo_price)} />
            <DetailItem label="Valid From" value={formatDate(viewData.valid_from)} />
            <DetailItem
              label="Valid To"
              value={viewData.valid_to ? formatDate(viewData.valid_to) : "No expiry"}
            />
            <DetailItem label="Description" value={viewData.description} span={2} />
            <DetailItem label="Included Items" span={2}>
              <ChipGroup
                items={(viewData.items || []).map((it) => ({
                  key: it.id || `${it.menu_id}-${it.quantity}`,
                  label: `${menuItemName(it.menu_id)} × ${it.quantity}`,
                }))}
              />
            </DetailItem>
          </DetailList>
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
          <ErrorAlert message={formError} className="field-full" />

          <Input label="Combo Name" required name="combo_name" value={formData.combo_name} onChange={handleChange} />

          <Input label="Combo Price" required type="number" name="combo_price" value={formData.combo_price} onChange={handleChange} />

          <Input label="Valid From" type="date" name="valid_from" value={formData.valid_from} onChange={handleChange} />

          <Input label="Valid To" type="date" name="valid_to" value={formData.valid_to} onChange={handleChange} min={formData.valid_from || undefined} />

          <div className="field-full">
            <Textarea
              label="Description"
              name="description"
              rows={3}
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="field-full">
            <label className="form-label form-label--required">Included Items</label>
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

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteRow}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Delete Combo Deal"
        confirmText="Delete"
        size="small"
        destructive
      >
        {`Delete ${deleteRow?.combo_name || "this combo"}? This cannot be undone.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default ComboDeals;

import React, { useState } from "react";
import { Activity } from "lucide-react";
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
import { formatDate, formatDateTime, formatPrecise } from "../../functions/formatters";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/**
 * Restaurant stock on hand.
 *
 * Units are the `inventory_unit_enum` the column is declared with, and the two
 * adjustment reasons are the two `transaction_type` values adjust_stock
 * accepts — both are database constraints, not master data.
 */
const UNITS = ["Kg", "Gram", "Litre", "ml", "Nos"];

const ADJUST_REASONS = [
  { value: "ADJUSTMENT", label: "Correction" },
  { value: "WASTE", label: "Wastage / Damage" },
];

const emptyAdjust = { direction: "Add", quantity: "", transaction_type: "ADJUSTMENT", remarks: "" };
const emptyItem = { item_name: "", unit: "Kg", min_stock_level: "" };

const Stock = () => {
  const perms = usePagePermissions("/stock");

  const {
    data: stockData,
    loading,
    error,
    reload: load,
  } = useApiResource(() => APICall.getT("/restaurant/inventory_stock"), {
    select: readList,
    fallback: "Failed to load stock.",
  });

  const { toast, showToast } = useToast();

  const [activeModal, setActiveModal] = useState(null); // view | adjust | movement | add-item
  const [selectedItem, setSelectedItem] = useState(null);
  const [movements, setMovements] = useState([]);
  const [movementsLoading, setMovementsLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const [adjustForm, setAdjustForm] = useState(emptyAdjust);
  const [newItemForm, setNewItemForm] = useState(emptyItem);

  /* ================= HANDLERS ================= */

  const openModal = async (type, row) => {
    setSelectedItem(row);
    setFormError(null);
    if (type === "adjust") setAdjustForm(emptyAdjust);
    setActiveModal(type);

    if (type === "movement") {
      setMovements([]);
      setMovementsLoading(true);
      try {
        const res = await APICall.getT(
          `/restaurant/inventory_item/${row.inventory_item_id}/transactions`,
        );
        setMovements(readList(res));
      } catch (err) {
        showToast(errMsg(err, "Failed to load stock movements."), "error");
      } finally {
        setMovementsLoading(false);
      }
    }
  };

  const openAddItemModal = () => {
    setNewItemForm(emptyItem);
    setFormError(null);
    setActiveModal("add-item");
  };

  const closeModal = () => {
    if (saving) return;
    setSelectedItem(null);
    setMovements([]);
    setActiveModal(null);
    setFormError(null);
  };

  const saveNewItem = async () => {
    if (saving) return;
    if (!newItemForm.item_name.trim()) {
      setFormError("Item name is required.");
      return;
    }
    const min = newItemForm.min_stock_level;
    if (min !== "" && (Number.isNaN(Number(min)) || Number(min) < 0)) {
      setFormError("Minimum stock level must be zero or more.");
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      await APICall.postT("/restaurant/inventory_item", {
        item_name: newItemForm.item_name.trim(),
        unit: newItemForm.unit,
        min_stock_level: min ? Number(min) : 0,
      });
      showToast("Inventory item added successfully", "success");
      closeModal();
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to create item."));
    } finally {
      setSaving(false);
    }
  };

  const saveAdjustment = async () => {
    if (saving) return;
    const qty = Number(adjustForm.quantity);
    // A blank or non-positive quantity used to be posted as-is. "Reduce 0" is
    // a no-op transaction in the ledger, and a negative typed into "Reduce"
    // silently became an increase once the sign was applied below.
    if (!adjustForm.quantity || Number.isNaN(qty) || qty <= 0) {
      setFormError("Enter a quantity greater than zero.");
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      const signed = adjustForm.direction === "Add" ? qty : -qty;
      await APICall.postT("/restaurant/inventory_stock/adjust", {
        inventory_item_id: selectedItem.inventory_item_id,
        kitchen_id: selectedItem.kitchen_id || null,
        quantity: signed,
        transaction_type: adjustForm.transaction_type,
        remarks: adjustForm.remarks.trim() || null,
      });
      showToast("Stock adjusted successfully", "update");
      closeModal();
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to adjust stock."));
    } finally {
      setSaving(false);
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Stock"
        loading={loading}
        emptyMessage="No stock recorded yet. Add an inventory item to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Item",
          onClick: openAddItemModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "item_name", title: "Item Name", align: "left" },
          { key: "unit", title: "Unit", align: "center" },
          // kitchen_name is resolved by the API. This column used to render
          // `Kitchen #${kitchen_id}` — a database row number shown to a
          // storekeeper who knows the place by its name.
          { key: "kitchen_name", title: "Store", align: "left" },
          {
            key: "available_quantity",
            title: "Available Qty",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.available_quantity),
            exportValue: (row) => formatPrecise(row.available_quantity),
          },
          {
            key: "min_stock_level",
            title: "Minimum Stock",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.min_stock_level),
            exportValue: (row) => formatPrecise(row.min_stock_level),
          },
          {
            key: "below_minimum",
            title: "Stock Status",
            align: "center",
            type: "badge",
            // A bare `<span className="badge">` rendered an unstyled chip that
            // was the same colour whether stock was fine or exhausted. Mapping
            // to the shared badge vocabulary makes low stock read as a warning.
            render: (row) => (row.below_minimum ? "Low Stock" : "In Stock"),
            exportValue: (row) => (row.below_minimum ? "Low Stock" : "In Stock"),
          },
          {
            key: "last_updated_date",
            title: "Last Updated",
            align: "left",
            type: "custom",
            render: (row) => formatDate(row.last_updated_date),
            exportValue: (row) => formatDate(row.last_updated_date),
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="stock item"
                canEdit={perms.edit}
                onView={() => openModal("view", row)}
                onEdit={() => openModal("adjust", row)}
              >
                {/* Movements is a read-only history. It used to be a
                    danger-ghost icon — the destructive red — beside a View
                    and an Edit drawn in two other styles. */}
                <IconButton
                  variant="action-edit"
                  size="action"
                  icon={<Activity size={16} />}
                  onClick={() => openModal("movement", row)}
                  title="Stock movements"
                  ariaLabel={`Stock movements for ${row.item_name || "item"}`}
                />
              </RowActions>
            ),
          },
        ]}
        data={stockData}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={activeModal === "view" && !!selectedItem}
        title={`Stock — ${selectedItem?.item_name || ""}`}
        onClose={closeModal}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: closeModal }]}
      >
        <ViewSection title="Item">
          <DetailList columns={2}>
            <DetailItem label="Item Name" value={selectedItem?.item_name} />
            <DetailItem label="Store" value={selectedItem?.kitchen_name} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Levels">
          <DetailList columns={3}>
            <DetailItem
              label="Available Quantity"
              value={
                selectedItem &&
                `${formatPrecise(selectedItem.available_quantity)} ${selectedItem.unit || ""}`.trim()
              }
            />
            <DetailItem
              label="Minimum Stock"
              value={
                selectedItem &&
                `${formatPrecise(selectedItem.min_stock_level)} ${selectedItem.unit || ""}`.trim()
              }
            />
            <DetailItem
              label="Status"
              value={selectedItem?.below_minimum ? "Low Stock" : "In Stock"}
            />
            <DetailItem
              label="Last Updated"
              value={selectedItem && formatDate(selectedItem.last_updated_date)}
            />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ================= ADD ITEM ================= */}
      <Modal
        isOpen={activeModal === "add-item"}
        title="Add Inventory Item"
        onClose={closeModal}
        size="medium"
        bodyLayout="grid"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: saveNewItem,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} className="field-full" />

        <Input
          label="Item Name"
          required
          name="item_name"
          placeholder="e.g. Basmati Rice"
          value={newItemForm.item_name}
          onChange={(e) => setNewItemForm((p) => ({ ...p, item_name: e.target.value }))}
        />
        <Select
          label="Unit"
          name="unit"
          value={newItemForm.unit}
          onChange={(e) => setNewItemForm((p) => ({ ...p, unit: e.target.value }))}
          options={UNITS}
        />
        <Input
          label="Minimum Stock Level"
          type="number"
          min="0"
          name="min_stock_level"
          placeholder="0"
          value={newItemForm.min_stock_level}
          onChange={(e) => setNewItemForm((p) => ({ ...p, min_stock_level: e.target.value }))}
        />
      </Modal>

      {/* ================= ADJUST ================= */}
      <Modal
        isOpen={activeModal === "adjust" && !!selectedItem}
        title={`Adjust Stock — ${selectedItem?.item_name || ""}`}
        onClose={closeModal}
        size="medium"
        bodyLayout="grid"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: saveAdjustment,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} className="field-full" />

        <Select
          label="Adjustment Type"
          name="direction"
          value={adjustForm.direction}
          onChange={(e) => setAdjustForm((p) => ({ ...p, direction: e.target.value }))}
          options={["Add", "Reduce"]}
        />
        <Input
          label={`Quantity${selectedItem?.unit ? ` (${selectedItem.unit})` : ""}`}
          required
          type="number"
          min="0"
          step="any"
          name="quantity"
          value={adjustForm.quantity}
          onChange={(e) => setAdjustForm((p) => ({ ...p, quantity: e.target.value }))}
        />
        <Select
          label="Reason"
          name="transaction_type"
          value={adjustForm.transaction_type}
          onChange={(e) => setAdjustForm((p) => ({ ...p, transaction_type: e.target.value }))}
          options={ADJUST_REASONS}
        />
        <div className="field-full">
          <Textarea
            label="Remarks"
            name="remarks"
            rows={2}
            placeholder="Why is this adjustment being made?"
            value={adjustForm.remarks}
            onChange={(e) => setAdjustForm((p) => ({ ...p, remarks: e.target.value }))}
          />
        </div>
      </Modal>

      {/* ================= MOVEMENTS ================= */}
      <Modal
        isOpen={activeModal === "movement" && !!selectedItem}
        title={`Stock Movements — ${selectedItem?.item_name || ""}`}
        onClose={closeModal}
        size="xlarge"
        bodyLayout="custom"
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: closeModal }]}
      >
        {/* Was a hand-rolled <table className="table table-hover"> with no
            loading state, no search and no export — the only raw table left on
            this screen. */}
        <TableTemplate
          loading={movementsLoading}
          emptyMessage="No movements recorded for this item."
          searchable
          pagination
          pageSize={8}
          exportable={false}
          columns={[
            {
              key: "created_at",
              title: "Date & Time",
              align: "left",
              type: "custom",
              render: (m) => formatDateTime(m.created_at),
            },
            { key: "transaction_type", title: "Type", align: "left" },
            {
              key: "quantity",
              title: "Qty",
              align: "right",
              type: "custom",
              render: (m) => formatPrecise(m.quantity),
            },
            {
              key: "reference_type",
              title: "Reference",
              align: "left",
              type: "custom",
              render: (m) =>
                `${m.reference_type || "—"}${m.reference_id ? ` (${m.reference_id})` : ""}`,
            },
            { key: "remarks", title: "Remarks", align: "left" },
          ]}
          data={movements}
        />
      </Modal>

      <Toast {...toast} />
    </>
  );
};

export default Stock;

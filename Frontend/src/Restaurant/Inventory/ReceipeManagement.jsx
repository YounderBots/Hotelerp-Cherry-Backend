import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import RepeatableRowEditor from "../../stories/RepeatableRowEditor";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatCount, formatPrecise } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/**
 * Which ingredients each menu item consumes.
 *
 * Saving a recipe replaces it wholesale (set_recipe deactivates the old rows
 * and inserts the new ones), so the editor always loads the current recipe
 * first and posts the complete list back.
 */
const emptyRow = { inventory_item_id: "", quantity_required: "", unit: "" };

const ReceipeManagement = () => {
  const perms = usePagePermissions("/recipe_management");

  const {
    data: [menuItems, inventoryItems, recipeCountRows, kitchens],
    loading,
    error,
    reload: load,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/restaurant/menu"),
      select: readList,
      fallback: "Failed to load menu items.",
    },
    { fetch: () => APICall.getT("/restaurant/inventory_item"), select: readList },
    // Returns an object keyed by menu id, not a list.
    { fetch: () => APICall.getT("/restaurant/menu_recipe_counts"), select: (res) => res?.data || {}, initial: {} },
    { fetch: () => APICall.getT("/restaurant/kitchen"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [activeModal, setActiveModal] = useState(null); // addEdit | view
  const [selectedMenu, setSelectedMenu] = useState(null);
  const [rows, setRows] = useState([]);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const recipeCounts = recipeCountRows || {};

  // An unknown kitchen reads as "—" rather than "#7": a row number tells the
  // chef nothing, and this list may simply not have loaded.
  const kitchenName = (id) => kitchens.find((k) => k.id === id)?.kitchen_name || "—";

  const itemOptions = inventoryItems.map((i) => ({ value: String(i.id), label: i.item_name }));

  /* ================= HANDLERS ================= */

  const openView = async (menu) => {
    try {
      const res = await APICall.getT(`/restaurant/menu/${menu.id}/recipe`);
      setSelectedMenu({ ...menu, ingredients: readList(res) });
      setActiveModal("view");
    } catch (err) {
      showToast(errMsg(err, "Failed to load recipe."), "error");
    }
  };

  const openEdit = async (menu) => {
    setFormError(null);
    try {
      const res = await APICall.getT(`/restaurant/menu/${menu.id}/recipe`);
      const existing = readList(res).map((r) => ({
        inventory_item_id: String(r.inventory_item_id),
        quantity_required: r.quantity_required,
        unit: r.unit,
      }));
      setRows(existing.length ? existing : [{ ...emptyRow }]);
      setSelectedMenu(menu);
      setActiveModal("addEdit");
    } catch (err) {
      showToast(errMsg(err, "Failed to load recipe."), "error");
    }
  };

  const closeModal = () => {
    if (saving) return;
    setSelectedMenu(null);
    setRows([]);
    setActiveModal(null);
    setFormError(null);
  };

  // Picking an ingredient fills in its unit, which is a property of the item
  // rather than something the recipe chooses.
  const updateRow = (idx, field, value) => {
    setRows((prev) => {
      const next = [...prev];
      next[idx] = { ...next[idx], [field]: value };
      if (field === "inventory_item_id") {
        next[idx].unit = inventoryItems.find((i) => String(i.id) === value)?.unit || "";
      }
      return next;
    });
  };

  const addRow = () => setRows((prev) => [...prev, { ...emptyRow }]);
  const removeRow = (idx) => setRows((prev) => prev.filter((_, i) => i !== idx));

  const saveRecipe = async () => {
    if (saving) return;
    const valid = rows.filter((r) => r.inventory_item_id && r.quantity_required);
    if (valid.length === 0) {
      setFormError("Add at least one ingredient with a quantity.");
      return;
    }
    if (valid.some((r) => Number(r.quantity_required) <= 0)) {
      setFormError("Every ingredient needs a quantity greater than zero.");
      return;
    }
    // Two rows for the same ingredient would both be inserted, and stock would
    // then be deducted twice for one item.
    const ids = valid.map((r) => r.inventory_item_id);
    if (new Set(ids).size !== ids.length) {
      setFormError("Each ingredient can only appear once. Combine the duplicates.");
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      await APICall.postT(`/restaurant/menu/${selectedMenu.id}/recipe`, {
        ingredients: valid.map((r) => ({
          inventory_item_id: Number(r.inventory_item_id),
          quantity_required: Number(r.quantity_required),
          unit: r.unit || "Nos",
        })),
      });
      showToast("Recipe saved successfully", "update");
      closeModal();
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save recipe."));
    } finally {
      setSaving(false);
    }
  };

  /* ================= UI ================= */

  const ingredients = selectedMenu?.ingredients || [];

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Recipes"
        loading={loading}
        emptyMessage="No menu items yet. Add one under Menu Management to give it a recipe."
        searchable
        pagination
        exportable
        columns={[
          { key: "item_code", title: "Item Code", align: "left" },
          { key: "item_name", title: "Menu Item", align: "left" },
          {
            key: "kitchen_id",
            title: "Kitchen",
            align: "left",
            type: "custom",
            render: (row) => kitchenName(row.kitchen_id),
            exportValue: (row) => kitchenName(row.kitchen_id),
          },
          {
            key: "id",
            title: "Ingredients",
            align: "right",
            type: "custom",
            render: (row) => formatCount(recipeCounts[row.id] ?? 0),
            exportValue: (row) => String(recipeCounts[row.id] ?? 0),
          },
          { key: "availability_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`recipe for ${row.item_name || ""}`.trim()}
                canEdit={perms.edit}
                onView={() => openView(row)}
                onEdit={() => openEdit(row)}
              />
            ),
          },
        ]}
        data={menuItems}
      />

      {/* ================= EDIT RECIPE ================= */}
      <Modal
        isOpen={activeModal === "addEdit" && !!selectedMenu}
        title={`Recipe — ${selectedMenu?.item_name || ""}`}
        onClose={closeModal}
        size="large"
        bodyLayout="single"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: saveRecipe,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} />

        <div className="modal-section">
          <h4 className="modal-section__title">Ingredients</h4>
          <p className="modal-section__hint">
            Stock for these ingredients is deducted automatically whenever a KOT for
            this item is marked ready.
          </p>
          {/* Was a hand-rolled <table className="table table-sm table-bordered">
              of bare <select>/<input> elements — Bootstrap classes in a project
              that has no Bootstrap, so the table was unstyled. */}
          <RepeatableRowEditor
            rows={rows}
            addLabel="+ Add Ingredient"
            emptyLabel="No ingredients yet."
            onAdd={addRow}
            onRemove={removeRow}
            onFieldChange={updateRow}
            fields={[
              {
                key: "inventory_item_id",
                type: "select",
                placeholder: "— select ingredient —",
                options: itemOptions,
              },
              { key: "quantity_required", type: "number", placeholder: "Qty" },
              { key: "unit", type: "text", placeholder: "Unit" },
            ]}
          />
        </div>
      </Modal>

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={activeModal === "view" && !!selectedMenu}
        title={`Recipe — ${selectedMenu?.item_name || ""}`}
        onClose={closeModal}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: closeModal }]}
      >
        <ViewSection title="Menu Item">
          <DetailList columns={2}>
            <DetailItem label="Item Code" value={selectedMenu?.item_code} />
            <DetailItem label="Item Name" value={selectedMenu?.item_name} />
            <DetailItem label="Kitchen" value={kitchenName(selectedMenu?.kitchen_id)} />
            <DetailItem label="Status" value={selectedMenu?.availability_status} />
          </DetailList>
        </ViewSection>

        <ViewSection title={`Ingredients (${formatCount(ingredients.length)})`}>
          {ingredients.length === 0 ? (
            <p className="view-section__empty">No recipe set for this item yet.</p>
          ) : (
            <DetailList columns={2}>
              {ingredients.map((i) => (
                <DetailItem
                  key={i.id}
                  label={i.item_name || "Unnamed ingredient"}
                  value={`${formatPrecise(i.quantity_required)} ${i.unit || ""}`.trim()}
                />
              ))}
            </DetailList>
          )}
        </ViewSection>
      </Modal>

      <Toast {...toast} />
    </>
  );
};

export default ReceipeManagement;

import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Pencil, Plus, Trash2 } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const BarReceipeManagement = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [inventoryItems, setInventoryItems] = useState([]);
  const [stations, setStations] = useState([]);
  const [recipeCounts, setRecipeCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [activeModal, setActiveModal] = useState(null); // addEdit | view
  const [selectedMenu, setSelectedMenu] = useState(null);
  const [rows, setRows] = useState([]);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([
      APICall.getT("/bar/menu"),
      APICall.getT("/bar/inventory_item"),
      APICall.getT("/bar/menu_recipe_counts"),
      APICall.getT("/bar/station"),
    ]).then(([mRes, iRes, cRes, sRes]) => {
      setMenuItems(mRes.status === "fulfilled" ? readList(mRes.value) : []);
      setInventoryItems(iRes.status === "fulfilled" ? readList(iRes.value) : []);
      setRecipeCounts(cRes.status === "fulfilled" ? cRes.value?.data || {} : {});
      setStations(sRes.status === "fulfilled" ? readList(sRes.value) : []);
      if (mRes.status === "rejected") setError(errMsg(mRes.reason, "Failed to load menu items."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const stationName = (id) => stations.find((s) => s.id === id)?.station_name || (id ? `#${id}` : "—");

  const openView = async (menu) => {
    try {
      const res = await APICall.getT(`/bar/menu/${menu.id}/recipe`);
      setSelectedMenu({ ...menu, ingredients: readList(res) });
      setActiveModal("view");
    } catch (err) {
      setError(errMsg(err, "Failed to load recipe."));
    }
  };

  const openEdit = async (menu) => {
    setFormError(null);
    try {
      const res = await APICall.getT(`/bar/menu/${menu.id}/recipe`);
      const existing = readList(res).map((r) => ({ inventory_item_id: String(r.inventory_item_id), quantity_required: r.quantity_required, unit: r.unit }));
      setRows(existing.length ? existing : [{ inventory_item_id: "", quantity_required: "", unit: "" }]);
      setSelectedMenu(menu);
      setActiveModal("addEdit");
    } catch (err) {
      setError(errMsg(err, "Failed to load recipe."));
    }
  };

  const closeModal = () => {
    if (saving) return;
    setSelectedMenu(null);
    setRows([]);
    setActiveModal(null);
  };

  const updateRow = (idx, field, value) => {
    setRows((prev) => {
      const next = [...prev];
      next[idx] = { ...next[idx], [field]: value };
      if (field === "inventory_item_id") {
        const item = inventoryItems.find((i) => String(i.id) === value);
        next[idx].unit = item?.unit || "";
      }
      return next;
    });
  };

  const addRow = () => setRows((prev) => [...prev, { inventory_item_id: "", quantity_required: "", unit: "" }]);
  const removeRow = (idx) => setRows((prev) => prev.filter((_, i) => i !== idx));

  const saveRecipe = async () => {
    const valid = rows.filter((r) => r.inventory_item_id && r.quantity_required);
    if (valid.length === 0) {
      setFormError("Add at least one ingredient with a quantity.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await APICall.postT(`/bar/menu/${selectedMenu.id}/recipe`, {
        ingredients: valid.map((r) => ({
          inventory_item_id: Number(r.inventory_item_id),
          quantity_required: Number(r.quantity_required),
          unit: r.unit || "ml",
        })),
      });
      closeModal();
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save recipe."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Recipes"
        searchable
        pagination
        loading={loading}
        columns={[
          { key: "item_code", title: "Item Code" },
          { key: "item_name", title: "Menu Item" },
          { key: "station_id", title: "Station", type: "custom", render: (row) => stationName(row.station_id) },
          { key: "id", title: "Ingredients", align: "center", type: "custom", render: (row) => `${recipeCounts[row.id] ?? 0} ingredient(s)` },
          { key: "availability_status", title: "Status", type: "badge", align: "center" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", justifyContent: "center", gap: 8, flexWrap: "nowrap" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openView(row)} />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} ariaLabel="Edit" onClick={() => openEdit(row)} />
              </div>
            ),
          },
        ]}
        data={menuItems}
      />

      {activeModal === "addEdit" && selectedMenu && (
        <Modal
          isOpen
          title={`Recipe — ${selectedMenu.item_name}`}
          onClose={closeModal}
          size="large"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Save Recipe", variant: "primary", onClick: saveRecipe, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <h6 className="fw-semibold mb-2">Ingredients Mapping</h6>
          <table className="table table-sm table-bordered">
            <thead>
              <tr>
                <th>Ingredient</th>
                <th>Qty Required</th>
                <th>Unit</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, idx) => (
                <tr key={idx}>
                  <td>
                    <select value={r.inventory_item_id} onChange={(e) => updateRow(idx, "inventory_item_id", e.target.value)}>
                      <option value="">— select —</option>
                      {inventoryItems.map((i) => (
                        <option key={i.id} value={i.id}>{i.item_name}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input type="number" value={r.quantity_required} onChange={(e) => updateRow(idx, "quantity_required", e.target.value)} />
                  </td>
                  <td>{r.unit || "-"}</td>
                  <td style={{ textAlign: "center" }}>
                    <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={14} />} ariaLabel="Remove ingredient" onClick={() => removeRow(idx)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <Button variant="secondary" className="mb-3" onClick={addRow}>
            <Plus size={14} /> Add Ingredient
          </Button>
          <p style={{ fontSize: 13, color: "#64748b" }}>
            Stock for these ingredients is deducted automatically whenever a BOT for this item is marked ready.
          </p>
        </Modal>
      )}

      {activeModal === "view" && selectedMenu && (
        <Modal
          isOpen
          title={`Recipe Details – ${selectedMenu.item_name}`}
          onClose={closeModal}
          size="medium"
          bodyLayout="single"
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeModal }]}
        >
          <p><strong>Station:</strong> {stationName(selectedMenu.station_id)}</p>
          <table className="table table-sm mt-3">
            <thead>
              <tr><th>Ingredient</th><th>Qty</th><th>Unit</th></tr>
            </thead>
            <tbody>
              {selectedMenu.ingredients.length === 0 ? (
                <tr><td colSpan={3} style={{ textAlign: "center", color: "#9ca3af" }}>No recipe set</td></tr>
              ) : (
                selectedMenu.ingredients.map((i) => (
                  <tr key={i.id}>
                    <td>{i.item_name || `#${i.inventory_item_id}`}</td>
                    <td>{i.quantity_required}</td>
                    <td>{i.unit}</td>
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

export default BarReceipeManagement;

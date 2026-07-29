import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Plus, X, Trash2 } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "../../MasterData/MasterData.css";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const ReceipeManagement = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [inventoryItems, setInventoryItems] = useState([]);
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
    Promise.allSettled([APICall.getT("/restaurant/menu"), APICall.getT("/restaurant/inventory_item")]).then(async ([mRes, iRes]) => {
      const menus = mRes.status === "fulfilled" ? readList(mRes.value) : [];
      setMenuItems(menus);
      setInventoryItems(iRes.status === "fulfilled" ? readList(iRes.value) : []);
      if (mRes.status === "rejected") setError(errMsg(mRes.reason, "Failed to load menu items."));

      const counts = {};
      await Promise.all(
        menus.map(async (m) => {
          try {
            const res = await APICall.getT(`/restaurant/menu/${m.id}/recipe`);
            counts[m.id] = readList(res).length;
          } catch {
            counts[m.id] = 0;
          }
        })
      );
      setRecipeCounts(counts);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openView = async (menu) => {
    try {
      const res = await APICall.getT(`/restaurant/menu/${menu.id}/recipe`);
      setSelectedMenu({ ...menu, ingredients: readList(res) });
      setActiveModal("view");
    } catch (err) {
      setError(errMsg(err, "Failed to load recipe."));
    }
  };

  const openEdit = async (menu) => {
    setFormError(null);
    try {
      const res = await APICall.getT(`/restaurant/menu/${menu.id}/recipe`);
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
      await APICall.postT(`/restaurant/menu/${selectedMenu.id}/recipe`, {
        ingredients: valid.map((r) => ({
          inventory_item_id: Number(r.inventory_item_id),
          quantity_required: Number(r.quantity_required),
          unit: r.unit || "Nos",
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
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Recipes"
        searchable
        pagination
        loading={loading}
        columns={[
          { key: "item_code", title: "Item Code" },
          { key: "item_name", title: "Menu Item" },
          { key: "kitchen_section", title: "Kitchen" },
          { key: "id", title: "Ingredients", align: "center", type: "custom", render: (row) => `${recipeCounts[row.id] ?? 0} ingredient(s)` },
          { key: "availability_status", title: "Status", type: "badge", align: "center" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", justifyContent: "center", gap: 8, flexWrap: "nowrap" }}>
                <button className="table-action-btn view" title="View" onClick={() => openView(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" title="Edit" onClick={() => openEdit(row)}>
                  <Pencil size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={menuItems}
      />

      {activeModal === "addEdit" && selectedMenu && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 1000 }}>
            <div className="modal-header">
              <h3>Recipe — {selectedMenu.item_name}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body">
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
                        <button className="btn icon" onClick={() => removeRow(idx)}>
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <button className="btn secondary mb-3" onClick={addRow}>
                <Plus size={14} /> Add Ingredient
              </button>
              <p style={{ fontSize: 13, color: "#64748b" }}>
                Stock for these ingredients is deducted automatically whenever a KOT for this item is marked ready.
              </p>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={saveRecipe} disabled={saving}>{saving ? "Saving…" : "Save Recipe"}</button>
            </div>
          </div>
        </div>
      )}

      {activeModal === "view" && selectedMenu && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 600 }}>
            <div className="modal-header">
              <h3>Recipe Details – {selectedMenu.item_name}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>
            <div className="modal-body single">
              <p><strong>Kitchen:</strong> {selectedMenu.kitchen_section}</p>
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
            </div>
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ReceipeManagement;

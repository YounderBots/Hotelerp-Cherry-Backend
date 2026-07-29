import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const KITCHEN_SECTIONS = ["Main", "Grill", "Dessert", "Bar"];

const MenuManagement = () => {
  const [data, setData] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);
  const [newCategoryName, setNewCategoryName] = useState("");

  const initialForm = {
    item_name: "",
    description: "",
    category_id: "",
    kitchen_section: "Main",
    preparation_time: "",
    price: "",
    tax_percentage: "",
    is_veg: "Yes",
    availability_status: "Available",
    item_image: "",
  };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/restaurant/menu"), APICall.getT("/restaurant/menu_category")]).then(([mRes, cRes]) => {
      setData(mRes.status === "fulfilled" ? readList(mRes.value) : []);
      setCategories(cRes.status === "fulfilled" ? readList(cRes.value) : []);
      if (mRes.status === "rejected") setError(errMsg(mRes.reason, "Failed to load menu items."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const categoryName = (id) => categories.find((c) => c.id === id)?.category_name || id;

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setNewCategoryName("");
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData({ ...row, category: categoryName(row.category_id) });
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    if (saving) return;
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleImageChange = (file) => {
    if (!file) return;
    setFormData((p) => ({ ...p, item_image: URL.createObjectURL(file) }));
  };

  const resolveCategoryId = async () => {
    if (formData.category_id) return Number(formData.category_id);
    if (!newCategoryName.trim()) return null;
    const res = await APICall.postT("/restaurant/menu_category", {
      category_name: newCategoryName.trim(),
      kitchen_section: formData.kitchen_section,
    });
    return res?.data?.id;
  };

  const handleSave = async () => {
    if (!formData.item_name.trim() || !formData.price || (!formData.category_id && !newCategoryName.trim())) {
      setFormError("Item name, price and category are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      const categoryId = await resolveCategoryId();
      if (!categoryId) {
        setFormError("Could not resolve a category for this item.");
        setSaving(false);
        return;
      }
      const payload = {
        item_name: formData.item_name.trim(),
        description: formData.description || null,
        category_id: categoryId,
        kitchen_section: formData.kitchen_section,
        preparation_time: formData.preparation_time ? Number(formData.preparation_time) : null,
        price: Number(formData.price),
        tax_percentage: formData.tax_percentage ? Number(formData.tax_percentage) : null,
        is_veg: formData.is_veg,
        availability_status: formData.availability_status,
        item_image: formData.item_image || null,
      };
      if (editId) {
        await APICall.putT(`/restaurant/menu/${editId}`, payload);
      } else {
        await APICall.postT("/restaurant/menu", payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save menu item."));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setNewCategoryName("");
    setFormError(null);
    setFormData({
      item_name: row.item_name || "",
      description: row.description || "",
      category_id: row.category_id ?? "",
      kitchen_section: row.kitchen_section || "Main",
      preparation_time: row.preparation_time ?? "",
      price: row.price ?? "",
      tax_percentage: row.tax_percentage ?? "",
      is_veg: row.is_veg || "Yes",
      availability_status: row.availability_status || "Available",
      item_image: row.item_image || "",
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    try {
      await APICall.deleteT(`/restaurant/menu/${id}`);
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to deactivate menu item."));
    }
  };

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Menu Management"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Item",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "item_code", title: "Item Code", align: "center" },
          {
            key: "item_image",
            title: "Item",
            align: "center",
            type: "custom",
            render: (row) =>
              row.item_image ? (
                <img src={row.item_image} alt="item" style={{ width: "40px", height: "40px", objectFit: "cover", borderRadius: "6px" }} />
              ) : (
                <span style={{ color: "#9ca3af" }}>—</span>
              ),
          },
          { key: "item_name", title: "Item Name" },
          { key: "category_id", title: "Category", type: "custom", render: (row) => categoryName(row.category_id) },
          { key: "kitchen_section", title: "Kitchen" },
          { key: "preparation_time", title: "Prep Time (min)", align: "center" },
          { key: "price", title: "Price", align: "center" },
          { key: "availability_status", title: "Availability", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => openViewModal(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => handleEdit(row)}>
                  <Pencil size={16} />
                </button>
                <button className="table-action-btn delete" onClick={() => handleDelete(row.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showViewModal && viewData && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Menu Item</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>
            <div className="modal-body single view">
              {Object.entries(viewData).map(([key, value]) => (
                <div className="form-group" key={key}>
                  <label>{key.replace(/_/g, " ")}</label>
                  {key === "item_image" && value ? (
                    <img src={value} alt="item" style={{ width: "100%", height: "140px", objectFit: "cover", borderRadius: "8px" }} />
                  ) : (
                    <input value={value ?? "-"} disabled />
                  )}
                </div>
              ))}
            </div>
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>Close</button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{editId ? "Edit Menu Item" : "Add Menu Item"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body grid">
              <div className="form-group">
                <label>Item Name <span className="required">*</span></label>
                <input name="item_name" value={formData.item_name} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Category <span className="required">*</span></label>
                <select name="category_id" value={formData.category_id} onChange={handleChange}>
                  <option value="">— select or type new below —</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.category_name}</option>
                  ))}
                </select>
                {!formData.category_id && (
                  <input
                    style={{ marginTop: "8px" }}
                    placeholder="New category name"
                    value={newCategoryName}
                    onChange={(e) => setNewCategoryName(e.target.value)}
                  />
                )}
              </div>

              <div className="form-group">
                <label>Kitchen Section</label>
                <select name="kitchen_section" value={formData.kitchen_section} onChange={handleChange}>
                  {KITCHEN_SECTIONS.map((k) => (
                    <option key={k} value={k}>{k}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Preparation Time (min)</label>
                <input type="number" name="preparation_time" value={formData.preparation_time} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Price <span className="required">*</span></label>
                <input type="number" name="price" value={formData.price} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Tax %</label>
                <input type="number" name="tax_percentage" value={formData.tax_percentage} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Veg / Non-Veg</label>
                <select name="is_veg" value={formData.is_veg} onChange={handleChange}>
                  <option value="Yes">Veg</option>
                  <option value="No">Non-Veg</option>
                </select>
              </div>

              <div className="form-group">
                <label>Availability</label>
                <select name="availability_status" value={formData.availability_status} onChange={handleChange}>
                  <option>Available</option>
                  <option>Out of Stock</option>
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Description</label>
                <input name="description" value={formData.description} onChange={handleChange} />
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Item Image</label>
                {formData.item_image && (
                  <img src={formData.item_image} alt="preview" style={{ width: "120px", height: "120px", objectFit: "cover", borderRadius: "8px", marginBottom: "8px" }} />
                )}
                <input type="file" accept="image/*" onChange={(e) => handleImageChange(e.target.files[0])} />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal} disabled={saving}>Close</button>
              <button className="btn primary" onClick={handleSave} disabled={saving}>{saving ? "Saving…" : "Submit"}</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MenuManagement;

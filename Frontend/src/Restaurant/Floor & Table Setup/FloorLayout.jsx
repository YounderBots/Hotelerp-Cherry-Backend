import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X, ToggleLeft, ToggleRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./FloorTable.css";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const FloorTable = () => {
  const navigate = useNavigate();

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = {
    floor_name: "",
    floor_number: "",
    floor_type: "Restaurant",
    description: "",
    total_tables: "",
    total_capacity: "",
    is_open: "Yes",
  };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    APICall.getT("/restaurant/floor")
      .then((res) => setData(readList(res)))
      .catch((err) => setError(errMsg(err, "Failed to load floors.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const viewPage = (row) => navigate("/view", { state: row });

  const closeModal = () => {
    if (saving) return;
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = async () => {
    if (!formData.floor_name.trim() || !formData.floor_number) {
      setFormError("Floor name and floor number are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    const payload = {
      floor_name: formData.floor_name.trim(),
      floor_number: Number(formData.floor_number),
      floor_type: formData.floor_type,
      description: formData.description || null,
      total_tables: formData.total_tables ? Number(formData.total_tables) : null,
      total_capacity: formData.total_capacity ? Number(formData.total_capacity) : null,
      is_open: formData.is_open,
    };
    try {
      if (editId) {
        await APICall.putT(`/restaurant/floor/${editId}`, payload);
      } else {
        await APICall.postT("/restaurant/floor", payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save floor."));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormError(null);
    setFormData({
      floor_name: row.floor_name || "",
      floor_number: row.floor_number ?? "",
      floor_type: row.floor_type || "Restaurant",
      description: row.description || "",
      total_tables: row.total_tables ?? "",
      total_capacity: row.total_capacity ?? "",
      is_open: row.is_open || "Yes",
    });
    setShowModal(true);
  };

  const toggleOpen = async (row) => {
    try {
      await APICall.putT(`/restaurant/floor/${row.id}`, { is_open: row.is_open === "Yes" ? "No" : "Yes" });
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to update floor status."));
    }
  };

  const handleDelete = async (id) => {
    try {
      await APICall.deleteT(`/restaurant/floor/${id}`);
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to deactivate floor."));
    }
  };

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Floor Layout"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Floor",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "floor_number", title: "Floor No", align: "center" },
          { key: "floor_name", title: "Floor Name", align: "center" },
          { key: "floor_type", title: "Type", align: "center" },
          { key: "total_tables", title: "Total Tables", align: "center" },
          { key: "total_capacity", title: "Capacity", align: "center" },
          { key: "is_open", title: "Open", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => viewPage(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => handleEdit(row)}>
                  <Pencil size={16} />
                </button>
                <button className="table-action-btn delete" onClick={() => handleDelete(row.id)}>
                  <Trash2 size={16} />
                </button>
                <button className="table-action-btn status" title="Toggle open/closed" onClick={() => toggleOpen(row)}>
                  {row.is_open === "Yes" ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>{editId ? "Edit Floor" : "Add Floor"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
              <div className="form-group">
                <label>Floor Number <span className="required">*</span></label>
                <input type="number" name="floor_number" value={formData.floor_number} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Floor Name <span className="required">*</span></label>
                <input name="floor_name" value={formData.floor_name} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Floor Type</label>
                <select name="floor_type" value={formData.floor_type} onChange={handleChange}>
                  <option value="Restaurant">Restaurant</option>
                  <option value="Bar">Bar</option>
                  <option value="Banquet">Banquet</option>
                  <option value="Outdoor">Outdoor</option>
                </select>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Enter floor description"
                  style={{ resize: "vertical", minHeight: "90px" }}
                />
              </div>

              <div className="form-group">
                <label>Total Tables</label>
                <input type="number" name="total_tables" value={formData.total_tables} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Total Capacity</label>
                <input type="number" name="total_capacity" value={formData.total_capacity} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Open for service</label>
                <select name="is_open" value={formData.is_open} onChange={handleChange}>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
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

export default FloorTable;

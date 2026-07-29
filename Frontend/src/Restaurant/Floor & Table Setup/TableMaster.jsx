import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const TableMaster = () => {
  const [data, setData] = useState([]);
  const [floors, setFloors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = {
    table_name: "",
    table_number: "",
    floor_id: "",
    seating_capacity: "",
    table_type: "Standard",
    section: "",
    server_name: "",
    table_status: "Available",
    is_mergeable: "No",
  };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/restaurant/table"), APICall.getT("/restaurant/floor")]).then(([tRes, fRes]) => {
      setData(tRes.status === "fulfilled" ? readList(tRes.value) : []);
      setFloors(fRes.status === "fulfilled" ? readList(fRes.value) : []);
      if (tRes.status === "rejected") setError(errMsg(tRes.reason, "Failed to load tables."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const floorName = (floorId) => floors.find((f) => f.id === floorId)?.floor_name || floorId;

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData({ ...row, floor: floorName(row.floor_id) });
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

  const handleSave = async () => {
    if (!formData.table_name.trim() || !formData.table_number || !formData.floor_id || !formData.seating_capacity) {
      setFormError("Table name, table number, floor and seating capacity are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    const payload = {
      table_name: formData.table_name.trim(),
      table_number: Number(formData.table_number),
      floor_id: Number(formData.floor_id),
      seating_capacity: Number(formData.seating_capacity),
      table_type: formData.table_type,
      section: formData.section || null,
      table_status: formData.table_status,
      is_mergeable: formData.is_mergeable,
    };
    try {
      if (editId) {
        await APICall.putT(`/restaurant/table/${editId}`, { ...payload, server_name: formData.server_name || null });
      } else {
        await APICall.postT("/restaurant/table", payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save table."));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormError(null);
    setFormData({
      table_name: row.table_name || "",
      table_number: row.table_number ?? "",
      floor_id: row.floor_id ?? "",
      seating_capacity: row.seating_capacity ?? "",
      table_type: row.table_type || "Standard",
      section: row.section || "",
      server_name: row.server_name || "",
      table_status: row.table_status || "Available",
      is_mergeable: row.is_mergeable || "No",
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    try {
      await APICall.deleteT(`/restaurant/table/${id}`);
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to deactivate table."));
    }
  };

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Table Master"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Table",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "table_code", title: "Table Code", align: "center" },
          { key: "table_name", title: "Table Name", align: "center" },
          { key: "floor_id", title: "Floor", align: "center", type: "custom", render: (row) => floorName(row.floor_id) },
          { key: "seating_capacity", title: "Capacity", align: "center" },
          { key: "table_type", title: "Table Type", align: "center" },
          { key: "server_name", title: "Assigned Server", align: "center" },
          { key: "current_order_id", title: "Current Order", align: "center" },
          { key: "table_status", title: "Status", align: "center", type: "badge" },
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
              <h3>View Table</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>
            <div className="modal-body single view">
              {Object.entries(viewData).map(([key, value]) => (
                <div className="form-group" key={key}>
                  <label>{key.replace(/_/g, " ")}</label>
                  <input value={value ?? "-"} disabled />
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
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>{editId ? "Edit Table" : "Add Table"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
              <div className="form-group">
                <label>Table Number <span className="required">*</span></label>
                <input type="number" name="table_number" value={formData.table_number} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Table Name <span className="required">*</span></label>
                <input name="table_name" value={formData.table_name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Floor <span className="required">*</span></label>
                <select name="floor_id" value={formData.floor_id} onChange={handleChange}>
                  <option value="">— select —</option>
                  {floors.map((f) => (
                    <option key={f.id} value={f.id}>{f.floor_name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Seating Capacity <span className="required">*</span></label>
                <input type="number" name="seating_capacity" value={formData.seating_capacity} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Section</label>
                <input name="section" value={formData.section} onChange={handleChange} placeholder="Restaurant / Bar / Outdoor" />
              </div>
              {editId && (
                <div className="form-group">
                  <label>Assigned Server</label>
                  <input name="server_name" value={formData.server_name} onChange={handleChange} />
                </div>
              )}

              <div className="form-group">
                <label>Table Type</label>
                <select name="table_type" value={formData.table_type} onChange={handleChange}>
                  <option>Standard</option>
                  <option>VIP</option>
                  <option>Private</option>
                  <option>Bar Counter</option>
                </select>
              </div>

              <div className="form-group">
                <label>Status</label>
                <select name="table_status" value={formData.table_status} onChange={handleChange}>
                  <option>Available</option>
                  <option>Occupied</option>
                  <option>Reserved</option>
                  <option>Cleaning</option>
                  <option>Blocked</option>
                </select>
              </div>

              <div className="form-group">
                <label>Mergeable</label>
                <select name="is_mergeable" value={formData.is_mergeable} onChange={handleChange}>
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
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

export default TableMaster;

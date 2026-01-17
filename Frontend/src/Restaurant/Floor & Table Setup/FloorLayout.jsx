import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const FloorTable = () => {
  const [data, setData] = useState([
    {
      id: 1,
      floorId: "F01",
      floorName: "Indoor Floor",
      description: "Main dining indoor area",
      totalTables: 24,
      seatingCapacity: 75,
      assignedServers: 10,
      currentOrders: 21,
      status: "Active",
    },
    {
      id: 2,
      floorId: "F02",
      floorName: "Outdoor Floor",
      description: "Open air dining",
      totalTables: 30,
      seatingCapacity: 50,
      assignedServers: 20,
      currentOrders: 20,
      status: "Active",
    },
    {
      id: 3,
      floorId: "F03",
      floorName: "Bar",
      description: "Bar & lounge area",
      totalTables: 15,
      seatingCapacity: 60,
      assignedServers: 0,
      currentOrders: 0,
      status: "Inactive",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    floorId: "",
    floorName: "",
    description: "",
    status: "Active",
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.floorId || !formData.floorName) return;

    const payload = {
      ...(editId
        ? data.find((i) => i.id === editId)
        : {
          totalTables: 0,
          seatingCapacity: 0,
          assignedServers: 0,
          currentOrders: 0,
        }),
      ...formData,
      id: editId || Date.now(),
    };

    if (editId) {
      setData((prev) =>
        prev.map((item) => (item.id === editId ? payload : item))
      );
    } else {
      setData((prev) => [...prev, payload]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      floorId: row.floorId,
      floorName: row.floorName,
      description: row.description || "",
      status: row.status,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Floor Layout"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Floor",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "floorId", title: "Floor ID", align: "center" },
          { key: "floorName", title: "Floor Name", align: "center" },
          { key: "totalTables", title: "Total Tables", align: "center" },
          { key: "seatingCapacity", title: "Seating Capacity", align: "center" },
          { key: "assignedServers", title: "Assigned Servers", align: "center" },
          { key: "currentOrders", title: "Current Orders", align: "center" },
          { key: "status", title: "Status", align: "center", type: "badge" },
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

      {/* ================= VIEW MODAL ================= */}
      {showViewModal && viewData && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Floor</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body single view">
              {[
                ["Floor ID", viewData.floorId],
                ["Floor Name", viewData.floorName],
                ["Description", viewData.description],
                ["Status", viewData.status],
              ].map(([label, value]) => (
                <div className="form-group" key={label}>
                  <label>{label}</label>
                  <input value={value || "-"} disabled />
                </div>
              ))}
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>{editId ? "Edit Floor" : "Add Floor"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Floor ID</label>
                <input name="floorId" value={formData.floorId} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Floor Name</label>
                <input name="floorName" value={formData.floorName} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Enter floor description"
                  style={{
                    resize: "vertical",
                    minHeight: "90px",
                  }}
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select name="status" value={formData.status} onChange={handleChange}>
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>Close</button>
              <button className="btn primary" onClick={handleSave}>Submit</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloorTable;

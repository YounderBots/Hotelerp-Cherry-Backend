import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const TableMaster = () => {
  const [data, setData] = useState([
    {
      id: 1,
      tableId: "T01",
      tableName: "Window Table 1",
      floor: "Indoor Floor",
      capacity: 4,
      tableType: "Standard",
      assignedServer: "Ravi",
      currentOrderId: "ORD-1021",
      status: "Occupied",
      isActive: "Yes",
    },
    {
      id: 2,
      tableId: "T02",
      tableName: "Poolside Table A",
      floor: "Outdoor Floor",
      capacity: 6,
      tableType: "VIP",
      assignedServer: "Suresh",
      currentOrderId: "",
      status: "Available",
      isActive: "Yes",
    },
    {
      id: 3,
      tableId: "T03",
      tableName: "Bar Counter 1",
      floor: "Bar",
      capacity: 2,
      tableType: "Bar Counter",
      assignedServer: "",
      currentOrderId: "",
      status: "Cleaning",
      isActive: "No",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    tableId: "",
    tableName: "",
    floor: "",
    capacity: "",
    tableType: "Standard",
    assignedServer: "",
    status: "Available",
    isActive: "Yes",
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
    if (!formData.tableId || !formData.tableName) return;

    const payload = {
      ...(editId
        ? data.find((i) => i.id === editId)
        : { currentOrderId: "" }),
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
      tableId: row.tableId,
      tableName: row.tableName,
      floor: row.floor,
      capacity: row.capacity,
      tableType: row.tableType,
      assignedServer: row.assignedServer,
      status: row.status,
      isActive: row.isActive,
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
        title="Table Master"
        hasActionButton
        searchable
        pagination
        pageSize={2}
        exportable
        actionButton={{
          label: "Add Table",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "tableId", title: "Table ID", align: "center" },
          { key: "tableName", title: "Table Name", align: "center" },
          { key: "floor", title: "Floor", align: "center" },
          { key: "capacity", title: "Capacity", align: "center" },
          { key: "tableType", title: "Table Type", align: "center" },
          { key: "assignedServer", title: "Assigned Server", align: "center" },
          { key: "currentOrderId", title: "Current Order ID", align: "center" },
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
              <h3>View Table</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(([key, value]) => (
                <div className="form-group" key={key}>
                  <label>{key.replace(/([A-Z])/g, " $1")}</label>
                  <input value={value || "-"} disabled />
                </div>
              ))}
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>{editId ? "Edit Table" : "Add Table"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body single">
              {[
                ["Table ID", "tableId"],
                ["Table Name", "tableName"],
                ["Floor", "floor"],
                ["Seating Capacity", "capacity"],
                ["Assigned Server", "assignedServer"],
              ].map(([label, name]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input name={name} value={formData[name]} onChange={handleChange} />
                </div>
              ))}

              <div className="form-group">
                <label>Table Type</label>
                <select name="tableType" value={formData.tableType} onChange={handleChange}>
                  <option>Standard</option>
                  <option>VIP</option>
                  <option>Private Dining</option>
                  <option>Bar Counter</option>
                </select>
              </div>

              <div className="form-group">
                <label>Status</label>
                <select name="status" value={formData.status} onChange={handleChange}>
                  <option>Available</option>
                  <option>Occupied</option>
                  <option>Reserved</option>
                  <option>Cleaning</option>
                </select>
              </div>

              <div className="form-group">
                <label>Is Active</label>
                <select name="isActive" value={formData.isActive} onChange={handleChange}>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
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

export default TableMaster;

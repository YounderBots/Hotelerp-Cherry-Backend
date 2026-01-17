import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X, UserPlus } from "lucide-react";
import "../../MasterData/MasterData.css";

const RoomIncidentLog = () => {
  const [data, setData] = useState([
    {
      id: 1,
      roomNo: "101",
      incidentDate: "2026-01-05",
      incidentTime: "14:30",
      witness: "Guest",
      reportedBy: "Front Office",
      reportDate: "2026-01-05",
    },
    {
      id: 2,
      roomNo: "205",
      incidentDate: "2026-01-04",
      incidentTime: "18:00",
      witness: "Housekeeping",
      reportedBy: "Supervisor",
      reportDate: "2026-01-04",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    roomNo: "",
    incidentDate: "",
    incidentTime: "",
    incidentDescription: "",
    housekeepingStaff: "",
    severity: "",
    witnesses: "",
    actionsTaken: "",
    reportedBy: "",
    reportDate: "",
    attachments: null,
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
    const { name, value, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files ? files : value,
    }));
  };

  const handleSave = () => {
    if (!formData.roomNo || !formData.incidentDate) return;

    const payload = {
      id: editId || Date.now(),
      roomNo: formData.roomNo,
      incidentDate: formData.incidentDate,
      incidentTime: formData.incidentTime,
      witness: formData.witnesses,
      reportedBy: formData.reportedBy,
      reportDate: formData.reportDate,
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
      ...initialForm,
      roomNo: row.roomNo,
      incidentDate: row.incidentDate,
      incidentTime: row.incidentTime,
      witnesses: row.witness,
      reportedBy: row.reportedBy,
      reportDate: row.reportDate,
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
        title="Room Incident Log"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Incident",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "incidentDate", title: "Incident Date", align: "center" },
          { key: "incidentTime", title: "Incident Time", align: "center" },
          { key: "witness", title: "Witness", align: "center" },
          { key: "reportedBy", title: "Reported By", align: "center" },
          { key: "reportDate", title: "Date of Report", align: "center" },
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
              <h3>View Incident</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(([key, value]) => (
                <div className="form-group" key={key}>
                  <label>{key.replace(/([A-Z])/g, " $1")}</label>
                  <input value={value} disabled />
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
          <div className="modal-card">
            <div className="modal-header">
              <h3>{editId ? "Edit Incident" : "Add Incident"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid">
              {[
                ["Room No", "roomNo"],
                ["Date of Incident", "incidentDate", "date"],
                ["Time of Incident", "incidentTime", "time"],
                ["Incident Description", "incidentDescription"],
                ["Housekeeping Staff Involved", "housekeepingStaff"],
                ["Severity of Incident", "severity"],
                ["Witnesses", "witnesses"],
                ["Actions Taken", "actionsTaken"],
                ["Reported By", "reportedBy"],
                ["Date of Report", "reportDate", "date"],
              ].map(([label, name, type]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input
                    type={type || "text"}
                    name={name}
                    value={formData[name]}
                    onChange={handleChange}
                  />
                </div>
              ))}

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Attachments</label>
                <input
                  type="file"
                  name="attachments"
                  multiple
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Close
              </button>
              <button className="btn primary" onClick={handleSave}>
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RoomIncidentLog;

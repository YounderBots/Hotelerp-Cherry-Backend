import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const GuestEnquiry = () => {
  const [data, setData] = useState([
    {
      id: 1,
      inquiryMode: "Phone",
      guestName: "Anand M",
      responseDate: "2026-01-05",
      followUpDate: "2026-01-07",
      incidents: "Room availability",
      status: "Open",
    },
    {
      id: 2,
      inquiryMode: "Email",
      guestName: "Madhu M",
      responseDate: "2026-01-04",
      followUpDate: "2026-01-06",
      incidents: "Pricing enquiry",
      status: "In Progress",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    inquiryMode: "",
    guestName: "",
    responseDate: "",
    followUpDate: "",
    incidents: "",
    status: "Open",
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
    if (!formData.inquiryMode || !formData.guestName) return;

    if (editId) {
      setData((prev) =>
        prev.map((item) =>
          item.id === editId ? { ...item, ...formData } : item
        )
      );
    } else {
      setData((prev) => [...prev, { id: Date.now(), ...formData }]);
    }
    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData(row);
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Guest Enquiry"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add New Enquiry",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "inquiryMode", title: "Inquiry Mode", align: "center" },
          { key: "guestName", title: "Guest Name", align: "center" },
          {
            key: "responseDate",
            title: "Response",
            align: "center",
          },
          {
            key: "followUpDate",
            title: "Follow Up",
            align: "center",
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button
                  className="table-action-btn view"
                  onClick={() => openViewModal(row)}
                >
                  <Eye size={16} />
                </button>
                <button
                  className="table-action-btn edit"
                  onClick={() => handleEdit(row)}
                >
                  <Pencil size={16} />
                </button>
                <button
                  className="table-action-btn delete"
                  onClick={() => handleDelete(row.id)}
                >
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
              <h3>View Guest Enquiry</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
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
              <h3>{editId ? "Edit Enquiry" : "Add Enquiry"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Inquiry Mode</label>
                <input
                  name="inquiryMode"
                  value={formData.inquiryMode}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Guest Name</label>
                <input
                  name="guestName"
                  value={formData.guestName}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Response Date</label>
                <input
                  type="date"
                  name="responseDate"
                  value={formData.responseDate}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Follow-up Date</label>
                <input
                  type="date"
                  name="followUpDate"
                  value={formData.followUpDate}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Incidents Inquiry</label>
                <input
                  name="incidents"
                  value={formData.incidents}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Resolved">Resolved</option>
                  <option value="Pending">Pending</option>
                </select>
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

export default GuestEnquiry;

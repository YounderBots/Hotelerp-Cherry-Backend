import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";
import APICall from "../../APICalls/APICalls";

const GuestEnquiry = () => {
  const [data, setData] = useState([]);

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

  const getGuestEnquiry = async () => {
    const AllEnquiry = await APICall.getT("/hotel/inquiry");
    setData(AllEnquiry.data);
  }

  const createGuestEnquiry = async () => {
    try {
      await APICall.postT("/hotel/inquiry", {
        inquiry_mode: formData.inquiryMode,
        guest_name: formData.guestName,
        inquiry_status: formData.status,
        response: formData.responseDate,
        follow_up: formData.followUpDate,
        incidents: formData.incidents,

      });
      getGuestEnquiry();
    }
    catch (error) {
      return error;
    }
  }

  const updateGuestEnquiry = async () => {
    try {
      await APICall.putT("/hotel/inquiry", {
        id: editId,
        inquiry_mode: formData.inquiryMode,
        guest_name: formData.guestName,
        inquiry_status: formData.status,
        response: formData.responseDate,
        follow_up: formData.followUpDate,
        incidents: formData.incidents,


      });
      getGuestEnquiry();
    }
    catch (error) {
      return error;
    }
  }

  const deleteguestEnquiry = async (id) => {
    try {
      await APICall.deleteT(`/hotel/inquiry/${id}`)
    }
    catch (error) {
      return error
    }
  }


  useEffect(() => {
    getGuestEnquiry();
  }, [])


  const handleSave = () => {
    if (!formData.inquiryMode || !formData.guestName) return;

    if (editId) {
      updateGuestEnquiry();

    } else {
      createGuestEnquiry();
    }
    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      inquiryMode: row.inquiry_mode,
      guestName: row.guest_name,
      status: row.inquiry_status,
      responseDate: row.response,
      followUpDate: row.follow_up,
      incidents: row.incidents
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deleteguestEnquiry(id);
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
          { key: "inquiry_mode", title: "Inquiry Mode", align: "center" },
          { key: "guest_name", title: "Guest Name", align: "center" },
          {
            key: "response",
            title: "Response",
            align: "center",
          },
          {
            key: "follow_up",
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

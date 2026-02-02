import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X, UserPlus } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const RoomIncidentLog = () => {
  const [data, setData] = useState([

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

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "application/pdf",
    ];

    if (!allowedTypes.includes(file.type)) {
      alert("Only JPG, PNG, or PDF files are allowed!");
      e.target.value = "";
      return;
    }

    setFormData((prev) => ({
      ...prev,
      attachment_file: file,
    }));
  };


  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files ? files[0] : value,
    }));
  };


  const getRoomIncidentLog = async () => {
    const AllRoomIncidentLog = await APICall.getT("/hotel/roomincident_log");
    setData(AllRoomIncidentLog.data);
  }

  const createRoomIncidentLog = async () => {
    try {
      await APICall.postT("/hotel/roomincident_log", {
        room_no: formData.roomNo,
        incident_date: formData.incidentDate,
        incident_time: formData.incidentTime,
        incident_description: formData.incidentDescription,
        involved_staff: formData.housekeepingStaff,
        severity: formData.severity,
        witness: formData.witnesses,
        actions_taken: formData.actionsTaken,
        reported_by: formData.reportedBy,
        report_date: formData.reportDate,
        attachment_file: formData.attachments

      });
      getRoomIncidentLog();
    }
    catch (error) {
      return error;
    }
  }


  useEffect(() => {
    getRoomIncidentLog();
  }, [])



  const handleSave = () => {
    // Basic validation
    if (!formData.roomNo || !formData.incidentDate) {
      alert("Room No and Incident Date are required");
      return;
    }

    if (editId) {
      // 🔁 local edit logic (if you really need it)
      setData((prev) =>
        prev.map((item) =>
          item.id === editId
            ? { ...item, ...formData }
            : item
        )
      );
    } else {
      // ✅ backend create
      createRoomIncidentLog();
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
          { key: "room_no", title: "Room No", align: "center" },
          { key: "incident_date", title: "Incident Date", align: "center" },
          { key: "incident_time", title: "Incident Time", align: "center" },
          { key: "witnesses", title: "Witness", align: "center" },
          { key: "reported_by", title: "Reported By", align: "center" },
          { key: "report_date", title: "Date of Report", align: "center" },
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
                <label>Attachment</label>
                <input
                  type="file"
                  name="attachment_file"
                  onChange={handleFileChange}
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

import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const RoomIncidentLog = () => {
  const [data, setData] = useState([]);
  const [rooms, setRooms] = useState([]);

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

  /* ================= API CALLS ================= */

  const getRoomIncidentLog = async () => {
    try {
      const res = await APICall.getT("/hotel/roomincident_log");
      setData(res.data.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getAllRooms = async () => {
    try {
      const res = await APICall.getT("/masterdata/room");
      setRooms(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const createRoomIncidentLog = async () => {
    try {
      const form = new FormData();

      form.append("room_id", formData.roomNo);
      form.append("incident_date", formData.incidentDate);
      form.append("incident_time", formData.incidentTime);
      form.append("incident_description", formData.incidentDescription);

      form.append("involved_staff", formData.housekeepingStaff || "");
      form.append("severity", formData.severity || "");
      form.append("witnesses", formData.witnesses || "");
      form.append("actions_taken", formData.actionsTaken || "");
      form.append("reported_by", formData.reportedBy || "");
      form.append("report_date", formData.reportDate || "");

      if (formData.attachments) {
        form.append("attachment_file", formData.attachments);
      }

      await APICall.postT("/hotel/roomincident_log", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      getRoomIncidentLog();
    } catch (err) {
      console.error(err);
    }
  };

  /* ================= HANDLERS ================= */

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowed = ["image/jpeg", "image/png", "application/pdf"];
    if (!allowed.includes(file.type)) {
      alert("Only JPG, PNG, or PDF allowed");
      e.target.value = "";
      return;
    }

    setFormData((prev) => ({ ...prev, attachments: file }));
  };

  const handleSave = () => {
    if (!formData.roomNo || !formData.incidentDate) {
      alert("Room No & Incident Date required");
      return;
    }

    createRoomIncidentLog();
    setShowModal(false);
    setFormData(initialForm);
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      ...initialForm,
      roomNo: row.room_id,
      incidentDate: row.incident_date,
      incidentTime: row.incident_time,
      incidentDescription: row.incident_description,
      housekeepingStaff: row.involved_staff,
      severity: row.severity,
      witnesses: row.witnesses,
      actionsTaken: row.actions_taken,
      reportedBy: row.reported_by,
      reportDate: row.report_date,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
  };

  /* ================= EFFECT ================= */

  useEffect(() => {
    getRoomIncidentLog();
    getAllRooms();
  }, []);

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
          onClick: () => setShowModal(true),
        }}
        columns={[
          { key: "room_id", title: "Room No", align: "center" },

          {
            key: "incident_date",
            title: "Incident Date",
            align: "center",
            render: (row) =>
              new Date(row.incident_date).toLocaleDateString(),
          },

          {
            key: "incident_time",
            title: "Incident Time",
            align: "center",
            render: (row) => row.incident_time?.slice(0, 5),
          },

          { key: "witnesses", title: "Witnesses", align: "center" },
          { key: "reported_by", title: "Reported By", align: "center" },

          {
            key: "report_date",
            title: "Report Date",
            align: "center",
            render: (row) =>
              new Date(row.report_date).toLocaleDateString(),
          },

          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={() => setViewData(row)}>
                  <Eye size={16} />
                </button>
                <button onClick={() => handleEdit(row)}>
                  <Pencil size={16} />
                </button>
                <button onClick={() => handleDelete(row.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />


      {/* ================= VIEW MODAL ================= */}
      {viewData && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Incident</h3>
              <button onClick={() => setViewData(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(([k, v]) => (
                <div className="form-group" key={k}>
                  <label>{k.replace(/_/g, " ")}</label>
                  <input value={v || ""} disabled />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= ADD MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Add Incident</h3>
              <button onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid">
              <div className="form-group">
                <label>Room Number</label>
                <select name="roomNo" value={formData.roomNo} onChange={handleChange}>
                  <option value="">Select Room</option>
                  {rooms.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.room_no}
                    </option>
                  ))}
                </select>
              </div>

              {[
                ["Incident Date", "incidentDate", "date"],
                ["Incident Time", "incidentTime", "time"],
                ["Description", "incidentDescription"],
                ["Housekeeping Staff", "housekeepingStaff"],
                ["Witnesses", "witnesses"],
                ["Actions Taken", "actionsTaken"],
                ["Reported By", "reportedBy"],
                ["Report Date", "reportDate", "date"],
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

              <div className="form-group">
                <label>Severity</label>
                <select name="severity" value={formData.severity} onChange={handleChange}>
                  <option value="">Select</option>
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                  <option>Critical</option>
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1/-1" }}>
                <label>Attachment</label>
                <input type="file" onChange={handleFileChange} />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={() => setShowModal(false)}>
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

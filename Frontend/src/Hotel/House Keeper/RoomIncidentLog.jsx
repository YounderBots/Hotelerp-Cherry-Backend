import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import { Eye, Pencil, Trash2 } from "lucide-react";
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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} onClick={() => setViewData(row)} ariaLabel="View" />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} onClick={() => handleEdit(row)} ariaLabel="Edit" />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} onClick={() => handleDelete(row.id)} ariaLabel="Delete" />
              </div>
            ),
          },
        ]}
        data={data}
      />


      {/* ================= VIEW MODAL ================= */}
      {viewData && (
        <Modal
          isOpen={!!viewData}
          title="View Incident"
          onClose={() => setViewData(null)}
          size="large"
          bodyLayout="grid"
          viewMode
        >
          {Object.entries(viewData).map(([k, v]) => (
            <Input key={k} label={k.replace(/_/g, " ")} value={v || ""} disabled />
          ))}
        </Modal>
      )}

      {/* ================= ADD MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title="Add Incident"
          onClose={() => setShowModal(false)}
          showFooter
          size="xlarge"
          bodyLayout="grid"
          actions={[
            { label: "Close", variant: "secondary", onClick: () => setShowModal(false) },
            { label: "Submit", variant: "primary", onClick: handleSave },
          ]}
        >
          <Select
            label="Room Number"
            name="roomNo"
            value={formData.roomNo}
            onChange={handleChange}
            placeholder="Select Room"
            options={rooms.map((r) => ({ value: r.id, label: r.room_no }))}
          />

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
            <Input
              key={name}
              label={label}
              type={type || "text"}
              name={name}
              value={formData[name]}
              onChange={handleChange}
            />
          ))}

          <Select
            label="Severity"
            name="severity"
            value={formData.severity}
            onChange={handleChange}
            placeholder="Select"
            options={[
              { value: "Low", label: "Low" },
              { value: "Medium", label: "Medium" },
              { value: "High", label: "High" },
              { value: "Critical", label: "Critical" },
            ]}
          />

          <div style={{ gridColumn: "1/-1" }}>
            <Input label="Attachment" type="file" onChange={handleFileChange} />
          </div>
        </Modal>
      )}
    </>
  );
};

export default RoomIncidentLog;

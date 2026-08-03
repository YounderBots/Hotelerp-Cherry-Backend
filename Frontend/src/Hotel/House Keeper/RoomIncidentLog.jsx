import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import { Eye, Pencil, Trash2 } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

// Bookkeeping columns the API returns on every row. They are meaningless to a
// user and were previously dumped into the View dialog alongside the real data.
const INTERNAL_FIELDS = new Set([
  "company_id", "created_by", "created_at", "updated_at", "updated_by", "status",
]);

const RoomIncidentLog = () => {
  const [data, setData] = useState([]);
  const [rooms, setRooms] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [pendingDelete, setPendingDelete] = useState(null);

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

  // Errors were swallowed into console.error, so a failed load left an empty
  // table that looked like "no incidents" rather than "this did not load".
  const errMsg = (err, fallback) =>
    (err instanceof ApiError && err.message) ? err.message : fallback;

  const getRoomIncidentLog = useCallback(async () => {
    setLoading(true);
    try {
      const res = await APICall.getT("/hotel/roomincident_log");
      setData(Array.isArray(res?.data?.data) ? res.data.data : []);
      setError("");
    } catch (err) {
      setData([]);
      setError(errMsg(err, "Failed to load incident logs."));
    } finally {
      setLoading(false);
    }
  }, []);

  const getAllRooms = useCallback(async () => {
    try {
      const res = await APICall.getT("/masterdata/room");
      setRooms(Array.isArray(res?.data) ? res.data : []);
    } catch (err) {
      // Non-fatal: the table still renders, the room picker is just empty.
      setError((prev) => prev || errMsg(err, "Could not load the room list."));
    }
  }, []);

  const createRoomIncidentLog = async () => {
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

    await APICall.postT("/hotel/roomincident_log", form);
  };

  // The update path never existed on this page: handleSave always POSTed, so
  // editing an incident silently created a duplicate. PUT /roomincident_log
  // takes JSON and requires numeric ids.
  const updateRoomIncidentLog = async () => {
    await APICall.putT("/hotel/roomincident_log", {
      id: Number(editId),
      room_id: Number(formData.roomNo),
      incident_date: formData.incidentDate,
      incident_time: formData.incidentTime,
      incident_description: formData.incidentDescription,
      involved_staff: formData.housekeepingStaff || "",
      severity: formData.severity || "",
      witnesses: formData.witnesses || "",
      actions_taken: formData.actionsTaken || "",
      reported_by: formData.reportedBy || "",
      report_date: formData.reportDate || "",
    });
  };

  /* ================= HANDLERS ================= */

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Surfaced in the dialog rather than through alert(), which blocks the
    // page and does not match how the rest of the app reports problems.
    const allowed = ["image/jpeg", "image/png", "application/pdf"];
    if (!allowed.includes(file.type)) {
      setFormError("Attachments must be a JPG, PNG or PDF.");
      e.target.value = "";
      return;
    }
    const MAX_BYTES = 5 * 1024 * 1024; // matches UPLOAD_MAX_BYTES on the server
    if (file.size > MAX_BYTES) {
      setFormError("Attachments must be 5 MB or smaller.");
      e.target.value = "";
      return;
    }

    setFormError("");
    setFormData((prev) => ({ ...prev, attachments: file }));
  };

  const handleSave = async () => {
    if (!formData.roomNo || !formData.incidentDate) {
      setFormError("Room number and incident date are required.");
      return;
    }
    if (!formData.incidentDescription?.trim()) {
      setFormError("Please describe the incident.");
      return;
    }
    setFormError("");
    setSaving(true);
    try {
      // Branch on editId. This used to call create unconditionally, so every
      // save from the Edit dialog appended a second copy of the record.
      if (editId) {
        await updateRoomIncidentLog();
      } else {
        await createRoomIncidentLog();
      }
      closeModal();
      await getRoomIncidentLog();
    } catch (err) {
      setFormError(errMsg(err, editId ? "Could not update the incident." : "Could not save the incident."));
    } finally {
      setSaving(false);
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setFormData(initialForm);
    setEditId(null);
    setFormError("");
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

  // This used to filter the row out of local state and never call the API, so
  // a "deleted" incident came straight back on the next refresh.
  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setSaving(true);
    try {
      await APICall.deleteT(`/hotel/roomincident_log/${pendingDelete.id}`);
      setPendingDelete(null);
      await getRoomIncidentLog();
    } catch (err) {
      setError(errMsg(err, "Could not delete the incident."));
      setPendingDelete(null);
    } finally {
      setSaving(false);
    }
  };

  /* ================= EFFECT ================= */

  useEffect(() => {
    getRoomIncidentLog();
    getAllRooms();
  }, [getRoomIncidentLog, getAllRooms]);

  /* ================= UI ================= */

  return (
    <>
      {/* A failed load previously left an empty table, which reads as "there are
          no incidents" rather than "this did not load". */}
      {error && (
        <div role="alert" style={{ marginBottom: 12, color: "var(--error-color)" }}>
          {error}{" "}
          <button type="button" onClick={getRoomIncidentLog} style={{ textDecoration: "underline" }}>
            Retry
          </button>
        </div>
      )}

      <TableTemplate
        title="Room Incident Log"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        emptyMessage="No incidents have been logged yet."
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
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} onClick={() => setPendingDelete(row)} ariaLabel="Delete" />
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
          {Object.entries(viewData)
            .filter(([k]) => !INTERNAL_FIELDS.has(k))
            .map(([k, v]) => (
              <Input key={k} label={k.replace(/_/g, " ")} value={v ?? ""} disabled />
            ))}
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          // The title said "Add Incident" even when editing an existing one.
          title={editId ? "Edit Incident" : "Add Incident"}
          onClose={closeModal}
          showFooter
          size="xlarge"
          bodyLayout="grid"
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModal, disabled: saving },
            {
              label: saving ? "Saving…" : (editId ? "Update" : "Submit"),
              variant: "primary",
              onClick: handleSave,
              disabled: saving,
            },
          ]}
        >
          {formError && (
            <div role="alert" style={{ gridColumn: "1 / -1", color: "var(--error-color)" }}>
              {formError}
            </div>
          )}
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

      {/* ================= DELETE CONFIRMATION ================= */}
      {/* Deleting used to happen immediately and only in local state. It now
          asks first, because it is irreversible, and then calls the API. */}
      {pendingDelete && (
        <Modal
          isOpen={Boolean(pendingDelete)}
          title="Delete incident"
          onClose={() => setPendingDelete(null)}
          showFooter
          size="small"
          actions={[
            { label: "Cancel", variant: "secondary", onClick: () => setPendingDelete(null), disabled: saving },
            { label: saving ? "Deleting…" : "Delete", variant: "danger", onClick: confirmDelete, disabled: saving },
          ]}
        >
          <p>
            Delete the incident logged for room{" "}
            <strong>{pendingDelete.room_id}</strong>? This cannot be undone.
          </p>
        </Modal>
      )}
    </>
  );
};

export default RoomIncidentLog;

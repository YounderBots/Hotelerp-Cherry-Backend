import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";

/** "22:00" + "06:00" reads as an overnight shift, not a negative duration. */
const shiftLength = (start, end) => {
  if (!start || !end) return null;
  const [sh, sm] = start.split(":").map(Number);
  const [eh, em] = end.split(":").map(Number);
  if ([sh, sm, eh, em].some((n) => Number.isNaN(n))) return null;
  let mins = eh * 60 + em - (sh * 60 + sm);
  if (mins <= 0) mins += 24 * 60; // crosses midnight
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
};

const Shift = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/user/shifts"),
    { select: readList, fallback: "Failed to load shifts." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { shift_name: "", start_time: "", end_time: "" };
  const [formData, setFormData] = useState(initialForm);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  const payload = () => ({
    shift_name: formData.shift_name.trim(),
    start_time: formData.start_time,
    end_time: formData.end_time,
  });

  const createShift = async () => {
    await APICall.postT("/user/shifts", payload());
    showToast("Shift created", "success");
    reload();
  };

  const updateShift = async () => {
    await APICall.putT("/user/shifts", { id: editId, ...payload() });
    showToast("Shift updated", "update");
    reload();
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({
      shift_name: row.shift_name ?? "",
      start_time: row.start_time ?? "",
      end_time: row.end_time ?? "",
    });
    setEditId(row.id);
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setEditId(null);
    setFormData(initialForm);
  };

  const handleSave = async () => {
    // Guard AND disabled Submit — the label alone used to change on `saving`,
    // so a double click created a duplicate shift.
    if (saving) return;
    const name = formData.shift_name.trim();
    if (!name) {
      showToast("Shift name is required", "error");
      return;
    }
    if (name.length > 100) {
      showToast("Shift name must be under 100 characters", "error");
      return;
    }
    if (!formData.start_time) {
      showToast("Start time is required", "error");
      return;
    }
    if (!formData.end_time) {
      showToast("End time is required", "error");
      return;
    }
    if (formData.start_time === formData.end_time) {
      showToast("Start time and end time cannot be identical", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateShift();
      } else {
        await createShift();
      }
      closeModal();
    } catch (err) {
      showToast(err?.message || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    const id = deleteId;
    setDeleteId(null);
    try {
      await APICall.deleteT(`/user/shifts/${id}`);
      showToast("Shift deleted", "delete");
      reload();
    } catch (err) {
      showToast(err?.message || "Delete failed", "error");
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Shifts"
        loading={loading}
        emptyMessage="No shifts yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Shift",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "shift_name", title: "Shift Name", align: "left" },
          { key: "start_time", title: "Start Time", align: "center" },
          { key: "end_time", title: "End Time", align: "center" },
          {
            key: "duration",
            title: "Duration",
            align: "center",
            type: "custom",
            exportValue: (row) => shiftLength(row.start_time, row.end_time) || "",
            render: (row) => shiftLength(row.start_time, row.end_time) || "—",
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="shift"
                onView={() => setViewData(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteId(row.id)}
              />
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Shift Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={2}>
          <DetailItem label="Shift Name" value={viewData?.shift_name} />
          <DetailItem
            label="Duration"
            value={viewData && shiftLength(viewData.start_time, viewData.end_time)}
          />
          <DetailItem label="Start Time" value={viewData?.start_time} />
          <DetailItem label="End Time" value={viewData?.end_time} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Shift" : "Add Shift"}
        onClose={closeModal}
        showFooter
        size="medium"
        bodyLayout="grid"
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: handleSave,
            disabled: saving,
          },
        ]}
      >
        <Input
          label="Shift Name"
          required
          type="text"
          name="shift_name"
          placeholder="e.g. Morning"
          maxLength={100}
          value={formData.shift_name}
          onChange={handleChange}
          disabled={saving}
        />
        <Input
          label="Start Time"
          required
          type="time"
          name="start_time"
          value={formData.start_time}
          onChange={handleChange}
          disabled={saving}
        />
        <Input
          label="End Time"
          required
          type="time"
          name="end_time"
          value={formData.end_time}
          onChange={handleChange}
          disabled={saving}
          helperText="An end time earlier than the start time is treated as an overnight shift."
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Shift"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this shift? Employees assigned to it will
        need to be reassigned. This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Shift;

import React, { useState } from "react";
import TableTemplate, { ColorSwatchCell } from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import RowActions from "../stories/RowActions";
import DetailList, { DetailItem } from "../stories/DetailList";
import ErrorAlert from "../stories/ErrorAlert";
import Toast from "../stories/Toast";
import APICall from "../APICalls/APICalls";
import { readList } from "../functions/apiHelpers";
import { useApiResource } from "../hooks/useApiResource";
import { useToast } from "../hooks/useToast";

const DEFAULT_COLOR = "#22c55e";

const HskTaskType = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/masterdata/task_type"),
    { select: readList, fallback: "Failed to load task types." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { name: "", color: DEFAULT_COLOR };
  const [formData, setFormData] = useState(initialForm);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  const createHskTaskType = async () => {
    await APICall.postT("/masterdata/task_type", {
      task_name: formData.name.trim(),
      color: formData.color,
    });
    showToast("Task Type added successfully", "success");
    reload();
  };

  const updateHskTaskType = async () => {
    await APICall.putT("/masterdata/task_type", {
      id: editId,
      task_name: formData.name.trim(),
      color: formData.color,
    });
    showToast("Task Type updated successfully", "update");
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
      name: row.task_name ?? "",
      color: row.color || DEFAULT_COLOR,
    });
    setEditId(row.id);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditId(null);
    setFormData(initialForm);
  };

  const handleSave = async () => {
    if (saving) return;
    if (!formData.name.trim()) {
      showToast("Task Type is required", "error");
      return;
    }

    setSaving(true);
    try {
      // Both branches are awaited and the list is reloaded once, inside the
      // create/update helpers. This screen used to fire an extra unawaited
      // reload straight after dispatching the save, which raced the write and
      // could repaint the row with its pre-save values.
      if (editId) {
        await updateHskTaskType();
      } else {
        await createHskTaskType();
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
      await APICall.deleteT(`/masterdata/task_type/${id}`);
      showToast("Task Type deleted successfully", "delete");
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
        title="Housekeeping Task Types"
        loading={loading}
        emptyMessage="No task types yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Task Type",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "task_name", title: "Task Type", align: "left" },
          {
            key: "color",
            title: "Colour",
            align: "left",
            type: "custom",
            exportValue: (row) => row.color || "",
            render: (row) => <ColorSwatchCell color={row.color} />,
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="task type"
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
        title="Task Type Details"
        onClose={() => setViewData(null)}
        size="small"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Task Type" value={viewData?.task_name} />
          <DetailItem label="Colour">
            <ColorSwatchCell color={viewData?.color} />
          </DetailItem>
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Task Type" : "Add Task Type"}
        onClose={closeModal}
        showFooter
        size="medium"
        bodyLayout="grid"
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: handleSave,
            disabled: saving,
          },
        ]}
      >
        <Input
          label="Task Type"
          required
          name="name"
          placeholder="e.g. Deep Clean"
          value={formData.name}
          onChange={handleChange}
        />
        {/* The colour swatch sizing lives in FormField.css
            (.form-control[type='color']), so this field shares the exact
            height of the text input beside it instead of carrying its own
            inline height. */}
        <Input
          label="Colour"
          type="color"
          name="color"
          value={formData.color}
          onChange={handleChange}
          helperText="Used to tag this task type across the app."
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Task Type"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this task type? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default HskTaskType;

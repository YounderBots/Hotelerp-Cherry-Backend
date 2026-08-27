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

const Designation = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/user/designations"),
    { select: readList, fallback: "Failed to load designations." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { name: "" };
  const [formData, setFormData] = useState(initialForm);

  /* ================= API ================= */

  const createDesignation = async () => {
    await APICall.postT("/user/designations", { designation_name: formData.name.trim() });
    showToast("Designation created", "success");
    reload();
  };

  const updateDesignation = async () => {
    await APICall.putT("/user/designations", { id: editId, designation_name: formData.name.trim() });
    showToast("Designation updated", "update");
    reload();
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({ name: row.designation_name ?? "" });
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
    // The guard AND the disabled Submit are both needed. This screen used to
    // swap only the button LABEL on `saving` and leave it enabled, so a double
    // click posted twice and created a duplicate designation.
    if (saving) return;
    const name = formData.name.trim();
    if (!name) {
      showToast("Designation Name is required", "error");
      return;
    }
    if (name.length > 100) {
      showToast("Designation Name must be under 100 characters", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateDesignation();
      } else {
        await createDesignation();
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
      await APICall.deleteT(`/user/designations/${id}`);
      showToast("Designation deleted", "delete");
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
        title="Designations"
        loading={loading}
        emptyMessage="No designations yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Designation",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "designation_name", title: "Designation Name", align: "left" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="designation"
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
        title="Designation Details"
        onClose={() => setViewData(null)}
        size="small"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Designation Name" value={viewData?.designation_name} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Designation" : "Add Designation"}
        onClose={closeModal}
        showFooter
        size="small"
        bodyLayout="single"
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
          label="Designation Name"
          required
          type="text"
          name="name"
          placeholder="e.g. Front Desk Executive"
          maxLength={100}
          value={formData.name}
          onChange={(e) => setFormData({ name: e.target.value })}
          disabled={saving}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Designation"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this designation? Employees
        assigned to it will need to be reassigned. This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Designation;

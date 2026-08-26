import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import Textarea from "../stories/Form/Textarea";
import RowActions from "../stories/RowActions";
import DetailList, { DetailItem } from "../stories/DetailList";
import ErrorAlert from "../stories/ErrorAlert";
import Toast from "../stories/Toast";
import APICall from "../APICalls/APICalls";
import { readList } from "../functions/apiHelpers";
import { useApiResource } from "../hooks/useApiResource";
import { useToast } from "../hooks/useToast";

// The backend spells this resource "complementry"; the UI spells it correctly.
// Keep the two apart rather than propagating the typo into user-facing copy.
const ENDPOINT = "/masterdata/complementry";

const Complementary = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT(ENDPOINT),
    { select: readList, fallback: "Failed to load complementary items." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { name: "", description: "" };
  const [formData, setFormData] = useState(initialForm);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  const payload = () => ({
    complementry_name: formData.name.trim(),
    description: formData.description.trim(),
  });

  const createComplementary = async () => {
    await APICall.postT(ENDPOINT, payload());
    showToast("Complementary item added successfully", "success");
    reload();
  };

  const updateComplementary = async () => {
    await APICall.putT(ENDPOINT, { id: editId, ...payload() });
    showToast("Complementary item updated successfully", "update");
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
      name: row.complementry_name ?? "",
      description: row.description ?? "",
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
      showToast("Complementary name is required", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateComplementary();
      } else {
        await createComplementary();
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
      await APICall.deleteT(`${ENDPOINT}/${id}`);
      showToast("Complementary item deleted successfully", "delete");
      // This reload was missing: the row stayed on screen after a successful
      // delete until the page was reloaded by hand.
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
        title="Complementary Items"
        loading={loading}
        emptyMessage="No complementary items yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Complementary",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "complementry_name", title: "Complementary Name", align: "left" },
          {
            key: "description",
            title: "Description",
            align: "left",
            type: "custom",
            exportValue: (row) => row.description || "",
            // Clamped to two lines so one long description cannot set the
            // height of every row in the table.
            render: (row) => (
              <span className="table-cell-clamp" title={row.description || ""}>
                {row.description || "—"}
              </span>
            ),
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="complementary item"
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
        title="Complementary Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Complementary Name" value={viewData?.complementry_name} />
          <DetailItem label="Description" value={viewData?.description} span={1} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Complementary" : "Add Complementary"}
        onClose={closeModal}
        showFooter
        size="medium"
        bodyLayout="single"
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
          label="Complementary Name"
          required
          name="name"
          placeholder="e.g. Welcome Drink"
          value={formData.name}
          onChange={handleChange}
        />
        <Textarea
          label="Description"
          name="description"
          rows={4}
          placeholder="What this complementary item includes"
          value={formData.description}
          onChange={handleChange}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Complementary"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this complementary item? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Complementary;

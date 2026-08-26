import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
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

const Facilities = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/masterdata/facilities"),
    { select: readList, fallback: "Failed to load facilities." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { facility_name: "" };
  const [formData, setFormData] = useState(initialForm);

  /* ================= API ================= */

  const createFacility = async () => {
    await APICall.postT("/masterdata/facilities", {
      facility_name: formData.facility_name.trim(),
    });
    showToast("Facility added successfully", "success");
    reload();
  };

  const updateFacility = async () => {
    await APICall.putT("/masterdata/facilities", {
      id: editId,
      facility_name: formData.facility_name.trim(),
    });
    showToast("Facility updated successfully", "update");
    reload();
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({ facility_name: row.facility_name ?? "" });
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
    if (!formData.facility_name.trim()) {
      showToast("Facility name is required", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateFacility();
      } else {
        await createFacility();
      }
      closeModal();
    } catch (err) {
      // Kept open on failure so the typed value is not thrown away.
      showToast(err?.message || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    const id = deleteId;
    setDeleteId(null);
    try {
      await APICall.deleteT(`/masterdata/facilities/${id}`);
      showToast("Facility deleted successfully", "delete");
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
        title="Facilities"
        loading={loading}
        emptyMessage="No facilities yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Facility",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "facility_name", title: "Facility Name", align: "left" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="facility"
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
        title="Facility Details"
        onClose={() => setViewData(null)}
        size="small"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Facility Name" value={viewData?.facility_name} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Facility" : "Add Facility"}
        onClose={closeModal}
        showFooter
        size="small"
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
          label="Facility Name"
          required
          type="text"
          name="facility_name"
          placeholder="e.g. Swimming Pool"
          value={formData.facility_name}
          onChange={(e) => setFormData({ facility_name: e.target.value })}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Facility"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this facility? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Facilities;

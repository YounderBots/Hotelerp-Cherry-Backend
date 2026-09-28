import React, { useRef, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import RowActions from "../stories/RowActions";
import DetailList, { DetailItem } from "../stories/DetailList";
import ErrorAlert from "../stories/ErrorAlert";
import Toast from "../stories/Toast";
import APICall from "../APICalls/APICalls";
import { readNestedList } from "../functions/apiHelpers";
import { useApiResource } from "../hooks/useApiResource";
import { useToast } from "../hooks/useToast";
import { usePagePermissions } from "../hooks/usePagePermissions";

const IdentificationProof = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/masterdata/identity_proof"),
    { select: readNestedList, fallback: "Failed to load identification proofs." },
  );

  const permissions = usePagePermissions("/identification_proof");
  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const savingRef = useRef(false);
  const deletingRef = useRef(false);
  const [deleting, setDeleting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { name: "" };
  const [formData, setFormData] = useState(initialForm);

  /* ================= API ================= */

  const createIdentificationProof = async () => {
    await APICall.postT("/masterdata/identity_proof", { proof_name: formData.name.trim() });
    showToast("Identification Proof added successfully", "success");
    await reload();
  };

  const updateIdentificationProof = async () => {
    await APICall.putT("/masterdata/identity_proof", {
      id: editId,
      proof_name: formData.name.trim(),
    });
    showToast("Identification Proof updated successfully", "update");
    await reload();
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({ name: row.proof_name ?? "" });
    setEditId(row.id);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditId(null);
    setFormData(initialForm);
  };

  const handleSave = async () => {
    // Guard plus the disabled Submit below: without both, a double click
    // posted twice and created a duplicate row.
    if (saving || savingRef.current) return;
    if (!formData.name.trim()) {
      showToast("Identification Proof Name is required", "error");
      return;
    }

    savingRef.current = true;
    setSaving(true);
    try {
      // Awaited, so a failed save leaves the modal open with the typed value
      // intact rather than closing over a request that never landed.
      if (editId) {
        await updateIdentificationProof();
      } else {
        await createIdentificationProof();
      }
      closeModal();
    } catch (err) {
      showToast(err?.message || "Save failed", "error");
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteId || deleting || deletingRef.current) return;
    deletingRef.current = true;
    setDeleting(true);
    try {
      await APICall.deleteT(`/masterdata/identity_proof/${deleteId}`);
      showToast("Identification Proof deleted successfully", "delete");
      await reload();
      setDeleteId(null);
    } catch (err) {
      showToast(err?.message || "Delete failed", "error");
    } finally {
      deletingRef.current = false;
      setDeleting(false);
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Identification Proofs"
        loading={loading}
        emptyMessage="No identification proofs yet. Add the first one to get started."
        hasActionButton={permissions.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Identification Proof",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "proof_name", title: "Identification Proof Name", align: "left" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="identification proof"
                onView={() => setViewData(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteId(row.id)}
                canEdit={permissions.edit}
                canDelete={permissions.delete}
              />
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Identification Proof Details"
        onClose={() => setViewData(null)}
        size="small"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Identification Proof Name" value={viewData?.proof_name} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Identification Proof" : "Add Identification Proof"}
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
          label="Identification Proof Name"
          required
          type="text"
          name="name"
          placeholder="e.g. Passport"
          value={formData.name}
          onChange={(e) => setFormData({ name: e.target.value })}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => (deleting ? null : setDeleteId(null))}
        onConfirm={confirmDelete}
        title="Delete Identification Proof"
        confirmText={deleting ? "Deleting…" : "Delete"}
        size="small"
        destructive
      >
        Are you sure you want to delete this identification proof? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default IdentificationProof;

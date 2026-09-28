import React, { useRef, useState } from "react";
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
import { usePagePermissions } from "../hooks/usePagePermissions";

const PaymentMethods = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/masterdata/payment_methods"),
    { select: readList, fallback: "Failed to load payment methods." },
  );

  const permissions = usePagePermissions("/payment_methods");
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

  const createPaymentMethods = async () => {
    await APICall.postT("/masterdata/payment_methods", { payment_method: formData.name.trim() });
    showToast("Payment Method added successfully", "success");
    await reload();
  };

  const updatePaymentMethods = async () => {
    await APICall.putT("/masterdata/payment_methods", {
      id: editId,
      payment_method: formData.name.trim(),
    });
    showToast("Payment Method updated successfully", "update");
    await reload();
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({ name: row.payment_method ?? "" });
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
      showToast("Payment Method Name is required", "error");
      return;
    }

    savingRef.current = true;
    setSaving(true);
    try {
      // Awaited, so a failed save leaves the modal open with the typed value
      // intact rather than closing over a request that never landed.
      if (editId) {
        await updatePaymentMethods();
      } else {
        await createPaymentMethods();
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
      await APICall.deleteT(`/masterdata/payment_methods/${deleteId}`);
      showToast("Payment Method deleted successfully", "delete");
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
        title="Payment Methods"
        loading={loading}
        emptyMessage="No payment methods yet. Add the first one to get started."
        hasActionButton={permissions.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Payment Method",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "payment_method", title: "Payment Method Name", align: "left" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="payment method"
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
        title="Payment Method Details"
        onClose={() => setViewData(null)}
        size="small"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Payment Method Name" value={viewData?.payment_method} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Payment Method" : "Add Payment Method"}
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
          label="Payment Method Name"
          required
          type="text"
          name="name"
          placeholder="e.g. Credit Card"
          value={formData.name}
          onChange={(e) => setFormData({ name: e.target.value })}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => (deleting ? null : setDeleteId(null))}
        onConfirm={confirmDelete}
        title="Delete Payment Method"
        confirmText={deleting ? "Deleting…" : "Delete"}
        size="small"
        destructive
      >
        Are you sure you want to delete this payment method? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default PaymentMethods;

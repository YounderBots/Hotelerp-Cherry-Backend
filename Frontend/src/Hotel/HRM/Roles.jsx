import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Textarea from "../../stories/Form/Textarea";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";

const Roles = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/user/roles"),
    { select: readList, fallback: "Failed to load roles." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { roleName: "", description: "" };
  const [formData, setFormData] = useState(initialForm);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  const payload = () => ({
    role_name: formData.roleName.trim(),
    description: formData.description.trim() || null,
  });

  const createRole = async () => {
    await APICall.postT("/user/roles", payload());
    showToast("Role created", "success");
    reload();
  };

  const updateRole = async () => {
    await APICall.putT("/user/roles", { id: editId, ...payload() });
    showToast("Role updated", "update");
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
      roleName: row.role_name ?? "",
      description: row.description ?? "",
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
    // Guard AND disabled Submit. This screen used to change only the button
    // label on `saving`, leaving it clickable — a double click created a
    // duplicate role.
    if (saving) return;
    const name = formData.roleName.trim();
    if (!name) {
      showToast("Role name is required", "error");
      return;
    }
    if (name.length > 100) {
      showToast("Role name must be under 100 characters", "error");
      return;
    }
    if (formData.description.length > 500) {
      showToast("Description must be under 500 characters", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateRole();
      } else {
        await createRole();
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
      await APICall.deleteT(`/user/roles/${id}`);
      showToast("Role deleted", "delete");
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
        title="Roles"
        loading={loading}
        emptyMessage="No roles yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Role",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "role_name", title: "Role Name", align: "left" },
          {
            key: "description",
            title: "Description",
            align: "left",
            type: "custom",
            exportValue: (row) => row.description || "",
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
                label="role"
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
        title="Role Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Role Name" value={viewData?.role_name} />
          <DetailItem label="Description" value={viewData?.description} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Role" : "Add Role"}
        onClose={closeModal}
        showFooter
        size="medium"
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
          label="Role Name"
          required
          type="text"
          name="roleName"
          placeholder="e.g. Front Office Manager"
          maxLength={100}
          value={formData.roleName}
          onChange={handleChange}
          disabled={saving}
        />
        <Textarea
          label="Description"
          name="description"
          rows={3}
          maxLength={500}
          placeholder="What this role is responsible for"
          value={formData.description}
          onChange={handleChange}
          disabled={saving}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Role"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this role? Users assigned to it will lose
        their permissions, and its entries in Role Permissions will no longer
        apply. This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Roles;

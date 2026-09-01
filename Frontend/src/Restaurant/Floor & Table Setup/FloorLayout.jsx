import React, { useState } from "react";
import { ToggleLeft, ToggleRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import IconButton from "../../stories/IconButton";
import DetailList, { DetailItem } from "../../stories/DetailList";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import Switch from "../../stories/Form/Switch";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/** `floor_type_enum` as the column is declared. */
const FLOOR_TYPES = ["Restaurant", "Banquet", "Outdoor"];

const initialForm = {
  floor_name: "",
  floor_number: "",
  floor_type: "Restaurant",
  description: "",
  total_tables: "",
  total_capacity: "",
  is_open: true,
};

const FloorTable = () => {
  const navigate = useNavigate();
  const perms = usePagePermissions("/floor_layout");

  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT("/restaurant/floor"),
    { select: readList, fallback: "Failed to load floors." },
  );

  const { toast, showToast } = useToast();

  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteRow, setDeleteRow] = useState(null);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [formError, setFormError] = useState(null);
  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormError(null);
    setFormData({
      floor_name: row.floor_name || "",
      floor_number: row.floor_number ?? "",
      floor_type: row.floor_type || "Restaurant",
      description: row.description || "",
      total_tables: row.total_tables ?? "",
      total_capacity: row.total_capacity ?? "",
      is_open: row.is_open ?? true,
    });
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setEditId(null);
    setShowModal(false);
    setFormData(initialForm);
    setFormError(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = async () => {
    if (saving) return;
    if (!formData.floor_name.trim() || formData.floor_number === "") {
      setFormError("Floor name and floor number are required.");
      return;
    }

    setFormError(null);
    setSaving(true);
    const payload = {
      floor_name: formData.floor_name.trim(),
      floor_number: Number(formData.floor_number),
      floor_type: formData.floor_type,
      description: formData.description.trim() || null,
      total_tables: formData.total_tables ? Number(formData.total_tables) : null,
      total_capacity: formData.total_capacity ? Number(formData.total_capacity) : null,
      is_open: formData.is_open,
    };

    try {
      if (editId) {
        await APICall.putT(`/restaurant/floor/${editId}`, payload);
        showToast("Floor updated successfully", "update");
      } else {
        await APICall.postT("/restaurant/floor", payload);
        showToast("Floor added successfully", "success");
      }
      setShowModal(false);
      setEditId(null);
      setFormData(initialForm);
      reload();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save floor."));
    } finally {
      setSaving(false);
    }
  };

  // Opening and closing a floor for service is a one-click toggle rather than
  // a trip through the edit form, so it is guarded by `busyId` instead: a
  // double click used to fire two PUTs that raced to opposite values.
  const toggleOpen = async (row) => {
    if (busyId) return;
    setBusyId(row.id);
    try {
      await APICall.putT(`/restaurant/floor/${row.id}`, { is_open: !row.is_open });
      showToast(row.is_open ? "Floor closed for service" : "Floor opened for service", "update");
      reload();
    } catch (err) {
      showToast(errMsg(err, "Failed to update floor status."), "error");
    } finally {
      setBusyId(null);
    }
  };

  // Was wired straight to the trash icon with no confirmation, so one stray
  // click removed a floor — and every table on it — from service silently.
  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    try {
      await APICall.deleteT(`/restaurant/floor/${row.id}`);
      showToast("Floor deactivated successfully", "delete");
      reload();
    } catch (err) {
      showToast(errMsg(err, "Failed to deactivate floor."), "error");
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Floor Layout"
        loading={loading}
        emptyMessage="No floors yet. Add the first one to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Floor",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "floor_number", title: "Floor No", align: "right" },
          { key: "floor_name", title: "Floor Name", align: "left" },
          { key: "floor_type", title: "Type", align: "left" },
          { key: "total_tables", title: "Total Tables", align: "right" },
          { key: "total_capacity", title: "Capacity", align: "right" },
          {
            key: "is_open",
            title: "Service",
            align: "center",
            type: "badge",
            // Was plain "Yes"/"No" text in a column headed "Open" — the only
            // state column in the app that was not a badge.
            render: (row) => (row.is_open ? "Open" : "Closed"),
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`floor ${row.floor_name || ""}`.trim()}
                canEdit={perms.edit}
                canDelete={perms.delete}
                onView={() => setViewData(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteRow(row)}
              >
                {perms.edit && (
                  <IconButton
                    variant="action-edit"
                    size="action"
                    icon={
                      row.is_open ? <ToggleRight size={16} /> : <ToggleLeft size={16} />
                    }
                    onClick={() => toggleOpen(row)}
                    disabled={busyId === row.id}
                    title={row.is_open ? "Close for service" : "Open for service"}
                    ariaLabel={`${row.is_open ? "Close" : "Open"} ${row.floor_name || "floor"} for service`}
                  />
                )}
              </RowActions>
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Floor Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
          {
            label: "Open floor plan",
            variant: "primary",
            onClick: () => navigate("/view", { state: viewData }),
          },
        ]}
      >
        <DetailList columns={2}>
          <DetailItem label="Floor Number" value={viewData?.floor_number} />
          <DetailItem label="Floor Name" value={viewData?.floor_name} />
          <DetailItem label="Floor Code" value={viewData?.floor_code} />
          <DetailItem label="Type" value={viewData?.floor_type} />
          <DetailItem label="Total Tables" value={viewData?.total_tables} />
          <DetailItem label="Capacity" value={viewData?.total_capacity} />
          <DetailItem label="Service" value={viewData?.is_open ? "Open" : "Closed"} />
          <DetailItem label="Description" value={viewData?.description} span={2} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Floor" : "Add Floor"}
        onClose={closeModal}
        size="large"
        bodyLayout="grid"
        showFooter
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
        <ErrorAlert message={formError} className="field-full" />

        <Input
          label="Floor Number"
          required
          type="number"
          name="floor_number"
          value={formData.floor_number}
          onChange={handleChange}
        />
        <Input
          label="Floor Name"
          required
          name="floor_name"
          placeholder="e.g. Ground Floor"
          value={formData.floor_name}
          onChange={handleChange}
        />
        <Select
          label="Floor Type"
          name="floor_type"
          value={formData.floor_type}
          onChange={handleChange}
          options={FLOOR_TYPES}
        />
        <Input
          label="Total Tables"
          type="number"
          min="0"
          name="total_tables"
          value={formData.total_tables}
          onChange={handleChange}
        />
        <Input
          label="Total Capacity"
          type="number"
          min="0"
          name="total_capacity"
          value={formData.total_capacity}
          onChange={handleChange}
        />
        <Switch
          label="Open for service"
          checked={formData.is_open}
          onChange={(e) => setFormData((p) => ({ ...p, is_open: e.target.checked }))}
        />
        <div className="field-full">
          {/* Was a bare <textarea> in a .form-group with an unlabelled <label>
              and an inline resize style. */}
          <Textarea
            label="Description"
            name="description"
            rows={3}
            placeholder="Anything worth knowing about this floor."
            value={formData.description}
            onChange={handleChange}
          />
        </div>
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteRow}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Deactivate Floor"
        confirmText="Deactivate"
        size="small"
        destructive
      >
        {`Deactivate ${deleteRow?.floor_name || "this floor"}? Its tables will no longer be reachable from the floor plan.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default FloorTable;

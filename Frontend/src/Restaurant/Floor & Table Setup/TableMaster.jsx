import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Switch from "../../stories/Form/Switch";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/**
 * Restaurant table master.
 *
 * Table type, section and status are the three SQL enums the columns are
 * declared with (`table_type_enum`, `table_section_enum`, `table_status_enum`),
 * so they are listed here rather than fetched: the database rejects anything
 * else, and a second source would only be able to disagree with it.
 */
const TABLE_TYPES = ["Standard", "VIP", "Private"];
const SECTIONS = ["Restaurant", "Outdoor", "Banquet"];
const TABLE_STATUSES = ["Available", "Occupied", "Reserved", "Cleaning", "Blocked"];

const initialForm = {
  table_name: "",
  table_number: "",
  floor_id: "",
  seating_capacity: "",
  table_type: "Standard",
  section: "",
  server_name: "",
  table_status: "Available",
  is_mergeable: false,
};

const TableMaster = () => {
  const perms = usePagePermissions("/table_master");

  const {
    data: [data, floors],
    loading,
    error,
    reload: load,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/restaurant/table"),
      select: readList,
      fallback: "Failed to load tables.",
    },
    { fetch: () => APICall.getT("/restaurant/floor"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteRow, setDeleteRow] = useState(null);
  const [saving, setSaving] = useState(false);
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
      table_name: row.table_name || "",
      table_number: row.table_number ?? "",
      floor_id: row.floor_id ?? "",
      seating_capacity: row.seating_capacity ?? "",
      table_type: row.table_type || "Standard",
      section: row.section || "",
      server_name: row.server_name || "",
      table_status: row.table_status || "Available",
      is_mergeable: row.is_mergeable ?? false,
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
    if (
      !formData.table_name.trim() ||
      !formData.table_number ||
      !formData.floor_id ||
      !formData.seating_capacity
    ) {
      setFormError("Table name, table number, floor and seating capacity are required.");
      return;
    }
    if (Number(formData.seating_capacity) < 1) {
      setFormError("Seating capacity must be at least one.");
      return;
    }

    setFormError(null);
    setSaving(true);
    const payload = {
      table_name: formData.table_name.trim(),
      table_number: Number(formData.table_number),
      floor_id: Number(formData.floor_id),
      seating_capacity: Number(formData.seating_capacity),
      table_type: formData.table_type,
      section: formData.section || null,
      table_status: formData.table_status,
      is_mergeable: !!formData.is_mergeable,
    };

    try {
      if (editId) {
        await APICall.putT(`/restaurant/table/${editId}`, {
          ...payload,
          server_name: formData.server_name.trim() || null,
        });
        showToast("Table updated successfully", "update");
      } else {
        await APICall.postT("/restaurant/table", payload);
        showToast("Table added successfully", "success");
      }
      setShowModal(false);
      setEditId(null);
      setFormData(initialForm);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save table."));
    } finally {
      setSaving(false);
    }
  };

  // Was wired straight to the trash icon with no confirmation: one stray click
  // took a table out of service, and nothing said it had happened.
  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    try {
      await APICall.deleteT(`/restaurant/table/${row.id}`);
      showToast("Table deactivated successfully", "delete");
      load();
    } catch (err) {
      showToast(errMsg(err, "Failed to deactivate table."), "error");
    }
  };

  /* ================= UI ================= */

  const floorOptions = floors.map((f) => ({ value: f.id, label: f.floor_name }));

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Table Master"
        loading={loading}
        emptyMessage="No tables yet. Add the first one to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Table",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "table_code", title: "Table Code", align: "left" },
          { key: "table_name", title: "Table Name", align: "left" },
          // floor_name and current_order_number are resolved by the API. The
          // floor used to be joined in the browser against a list that may not
          // have loaded, and the order was the raw restaurant_order.id.
          { key: "floor_name", title: "Floor", align: "left" },
          { key: "seating_capacity", title: "Capacity", align: "right" },
          { key: "table_type", title: "Table Type", align: "left" },
          { key: "server_name", title: "Assigned Server", align: "left" },
          { key: "current_order_number", title: "Current Order", align: "left" },
          { key: "table_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`table ${row.table_name || ""}`.trim()}
                canEdit={perms.edit}
                canDelete={perms.delete}
                onView={() => setViewData(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteRow(row)}
              />
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Table Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewData(null) }]}
      >
        {/* Was `Object.entries(viewData).map(...)` into disabled <Input>s,
            which printed every column on the row — id, company_id, branch_id,
            status, created_by, created_at — as a greyed-out form field. */}
        <ViewSection title="Table">
          <DetailList columns={2}>
            <DetailItem label="Table Code" value={viewData?.table_code} />
            <DetailItem label="Table Name" value={viewData?.table_name} />
            <DetailItem label="Table Number" value={viewData?.table_number} />
            <DetailItem label="Floor" value={viewData?.floor_name} />
            <DetailItem label="Section" value={viewData?.section} />
            <DetailItem label="Table Type" value={viewData?.table_type} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Service">
          <DetailList columns={2}>
            <DetailItem label="Seating Capacity" value={viewData?.seating_capacity} />
            <DetailItem label="Status" value={viewData?.table_status} />
            <DetailItem label="Assigned Server" value={viewData?.server_name} />
            <DetailItem label="Current Order" value={viewData?.current_order_number} />
            <DetailItem label="Mergeable" value={viewData?.is_mergeable ? "Yes" : "No"} />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Table" : "Add Table"}
        onClose={closeModal}
        // Nine fields. In a small, single-column modal this was a form the
        // user had to scroll to reach its own Submit button.
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
          label="Table Number"
          required
          type="number"
          min="1"
          name="table_number"
          value={formData.table_number}
          onChange={handleChange}
        />
        <Input
          label="Table Name"
          required
          name="table_name"
          placeholder="e.g. Window 2"
          value={formData.table_name}
          onChange={handleChange}
        />
        <Select
          label="Floor"
          required
          name="floor_id"
          value={formData.floor_id}
          onChange={handleChange}
          placeholder="— select —"
          options={floorOptions}
        />
        <Input
          label="Seating Capacity"
          required
          type="number"
          min="1"
          name="seating_capacity"
          value={formData.seating_capacity}
          onChange={handleChange}
        />
        <Select
          label="Section"
          name="section"
          value={formData.section}
          onChange={handleChange}
          placeholder="— none —"
          options={SECTIONS}
        />
        <Select
          label="Table Type"
          name="table_type"
          value={formData.table_type}
          onChange={handleChange}
          options={TABLE_TYPES}
        />
        <Select
          label="Status"
          name="table_status"
          value={formData.table_status}
          onChange={handleChange}
          options={TABLE_STATUSES}
        />
        {/* create_table has no server_name field; only the update endpoint
            accepts one, so it is offered only when editing. */}
        {editId && (
          <Input
            label="Assigned Server"
            name="server_name"
            value={formData.server_name}
            onChange={handleChange}
          />
        )}
        <Switch
          label="Mergeable"
          checked={formData.is_mergeable}
          onChange={(e) => setFormData((p) => ({ ...p, is_mergeable: e.target.checked }))}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteRow}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Deactivate Table"
        confirmText="Deactivate"
        size="small"
        destructive
      >
        {`Deactivate table ${deleteRow?.table_name || ""}? It will no longer be available for orders or reservations.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default TableMaster;

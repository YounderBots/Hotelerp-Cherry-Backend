import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Pencil, Trash2 } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";

const TableMaster = () => {
  const {
    data: [data, floors],
    loading,
    error,
    setError,
    reload: load,
  } = useApiResources([
    { fetch: () => APICall.getT("/restaurant/table"), select: readList,
      fallback: "Failed to load tables." },
    { fetch: () => APICall.getT("/restaurant/floor"), select: readList },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

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
  const [formData, setFormData] = useState(initialForm);

  const floorName = (floorId) => floors.find((f) => f.id === floorId)?.floor_name || floorId;

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData({ ...row, floor: floorName(row.floor_id) });
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    if (saving) return;
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleBoolChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value === "true" }));
  };

  const handleSave = async () => {
    if (!formData.table_name.trim() || !formData.table_number || !formData.floor_id || !formData.seating_capacity) {
      setFormError("Table name, table number, floor and seating capacity are required.");
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
        await APICall.putT(`/restaurant/table/${editId}`, { ...payload, server_name: formData.server_name || null });
      } else {
        await APICall.postT("/restaurant/table", payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save table."));
    } finally {
      setSaving(false);
    }
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

  const handleDelete = async (id) => {
    try {
      await APICall.deleteT(`/restaurant/table/${id}`);
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to deactivate table."));
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Table Master"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Table",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "table_code", title: "Table Code", align: "center" },
          { key: "table_name", title: "Table Name", align: "center" },
          { key: "floor_id", title: "Floor", align: "center", type: "custom", render: (row) => floorName(row.floor_id) },
          { key: "seating_capacity", title: "Capacity", align: "center" },
          { key: "table_type", title: "Table Type", align: "center" },
          { key: "server_name", title: "Assigned Server", align: "center" },
          { key: "current_order_id", title: "Current Order", align: "center" },
          { key: "table_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openViewModal(row)} />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} ariaLabel="Edit" onClick={() => handleEdit(row)} />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} ariaLabel="Delete" onClick={() => handleDelete(row.id)} />
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          title="View Table"
          onClose={closeViewModal}
          size="medium"
          bodyLayout="grid"
          viewMode
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          {Object.entries(viewData).map(([key, value]) => (
            <Input key={key} label={key.replace(/_/g, " ")} value={value ?? "-"} disabled />
          ))}
        </Modal>
      )}

      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Table" : "Add Table"}
          onClose={closeModal}
          size="small"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Submit", variant: "primary", onClick: handleSave, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <Input label="Table Number" required type="number" name="table_number" value={formData.table_number} onChange={handleChange} />
          <Input label="Table Name" required name="table_name" value={formData.table_name} onChange={handleChange} />
          <Select
            label="Floor"
            required
            name="floor_id"
            value={formData.floor_id}
            onChange={handleChange}
            placeholder="— select —"
            options={floors.map((f) => ({ value: f.id, label: f.floor_name }))}
          />
          <Input label="Seating Capacity" required type="number" name="seating_capacity" value={formData.seating_capacity} onChange={handleChange} />
          <Select
            label="Section"
            name="section"
            value={formData.section}
            onChange={handleChange}
            placeholder="— none —"
            options={[
              { value: "Restaurant", label: "Restaurant" },
              { value: "Outdoor", label: "Outdoor" },
              { value: "Banquet", label: "Banquet" },
            ]}
          />
          {editId && (
            <Input label="Assigned Server" name="server_name" value={formData.server_name} onChange={handleChange} />
          )}

          <Select
            label="Table Type"
            name="table_type"
            value={formData.table_type}
            onChange={handleChange}
            options={["Standard", "VIP", "Private"]}
          />

          <Select
            label="Status"
            name="table_status"
            value={formData.table_status}
            onChange={handleChange}
            options={["Available", "Occupied", "Reserved", "Cleaning", "Blocked"]}
          />

          <Select
            label="Mergeable"
            name="is_mergeable"
            value={String(formData.is_mergeable)}
            onChange={handleBoolChange}
            options={[
              { value: "false", label: "No" },
              { value: "true", label: "Yes" },
            ]}
          />
        </Modal>
      )}
    </>
  );
};

export default TableMaster;

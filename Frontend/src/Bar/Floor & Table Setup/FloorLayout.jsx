import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import ErrorAlert from "../../stories/ErrorAlert";
import { Pencil, Trash2, ToggleLeft, ToggleRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const FloorLayout = () => {
  const navigate = useNavigate();

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = {
    floor_name: "",
    floor_number: "",
    description: "",
    total_tables: "",
    total_capacity: "",
    is_open: true,
  };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    APICall.getT("/bar/floor")
      .then((res) => setData(readList(res)))
      .catch((err) => setError(errMsg(err, "Failed to load floors.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
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
    if (!formData.floor_name.trim() || !formData.floor_number) {
      setFormError("Floor name and floor number are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    const payload = {
      floor_name: formData.floor_name.trim(),
      floor_number: Number(formData.floor_number),
      description: formData.description || null,
      total_tables: formData.total_tables ? Number(formData.total_tables) : null,
      total_capacity: formData.total_capacity ? Number(formData.total_capacity) : null,
      is_open: formData.is_open,
    };
    try {
      if (editId) {
        await APICall.putT(`/bar/floor/${editId}`, payload);
      } else {
        await APICall.postT("/bar/floor", payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save floor."));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormError(null);
    setFormData({
      floor_name: row.floor_name || "",
      floor_number: row.floor_number ?? "",
      description: row.description || "",
      total_tables: row.total_tables ?? "",
      total_capacity: row.total_capacity ?? "",
      is_open: row.is_open ?? true,
    });
    setShowModal(true);
  };

  const toggleOpen = async (row) => {
    try {
      await APICall.putT(`/bar/floor/${row.id}`, { is_open: !row.is_open });
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to update floor status."));
    }
  };

  const handleDelete = async (id) => {
    try {
      await APICall.deleteT(`/bar/floor/${id}`);
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to deactivate floor."));
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Floor Layout"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Floor",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "floor_number", title: "Floor No", align: "center" },
          { key: "floor_name", title: "Floor Name", align: "center" },
          { key: "total_tables", title: "Total Tables", align: "center" },
          { key: "total_capacity", title: "Capacity", align: "center" },
          { key: "is_open", title: "Open", align: "center", type: "custom", render: (row) => (row.is_open ? "Yes" : "No") },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} ariaLabel="Edit" onClick={() => handleEdit(row)} />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} ariaLabel="Delete" onClick={() => handleDelete(row.id)} />
                <IconButton
                  variant="ghost"
                  size="small"
                  icon={row.is_open ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                  ariaLabel="Toggle open/closed"
                  title="Toggle open/closed"
                  onClick={() => toggleOpen(row)}
                />
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showModal && (
        <Modal
          isOpen
          title={editId ? "Edit Floor" : "Add Floor"}
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

          <Input label="Floor Number" required type="number" name="floor_number" value={formData.floor_number} onChange={handleChange} />
          <Input label="Floor Name" required name="floor_name" value={formData.floor_name} onChange={handleChange} />

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-control"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={4}
              placeholder="Enter floor description"
              style={{ resize: "vertical", minHeight: "90px" }}
            />
          </div>

          <Input label="Total Tables" type="number" name="total_tables" value={formData.total_tables} onChange={handleChange} />
          <Input label="Total Capacity" type="number" name="total_capacity" value={formData.total_capacity} onChange={handleChange} />
          <Select
            label="Open for service"
            name="is_open"
            value={String(formData.is_open)}
            onChange={handleBoolChange}
            options={[{ value: "true", label: "Yes" }, { value: "false", label: "No" }]}
          />
        </Modal>
      )}
    </>
  );
};

export default FloorLayout;

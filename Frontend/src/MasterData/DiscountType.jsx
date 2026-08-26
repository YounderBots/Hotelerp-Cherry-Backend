import React, { useMemo, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import Select from "../stories/Form/Select";
import RowActions from "../stories/RowActions";
import DetailList, { DetailItem } from "../stories/DetailList";
import ErrorAlert from "../stories/ErrorAlert";
import Toast from "../stories/Toast";
import APICall from "../APICalls/APICalls";
import { readList } from "../functions/apiHelpers";
import { useApiResources } from "../hooks/useApiResource";
import { useToast } from "../hooks/useToast";

const DiscountType = () => {
  // Both lookups in one parallel load. The countries list only feeds the
  // picker, so it declares no fallback: if it fails the picker is empty but
  // the table still renders its rows.
  const {
    data: [rows, countries],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT("/masterdata/discount"), select: readList, fallback: "Failed to load discount types." },
    { fetch: () => APICall.getT("/masterdata/country_currency"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { countryId: "", name: "", percentage: "" };
  const [formData, setFormData] = useState(initialForm);

  const countryName = useMemo(() => {
    const map = new Map(countries.map((c) => [String(c.id), c.country_name]));
    return (id) => map.get(String(id)) || "—";
  }, [countries]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  const payload = () => ({
    country_id: Number(formData.countryId),
    discount_name: formData.name.trim(),
    discount_percentage: Number(formData.percentage),
  });

  const createDiscountType = async () => {
    await APICall.postT("/masterdata/discount", payload());
    showToast("Discount Type added successfully", "success");
    reload();
  };

  const updateDiscountType = async () => {
    await APICall.putT("/masterdata/discount", { id: editId, ...payload() });
    showToast("Discount Type updated successfully", "update");
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
      countryId: row.country_id ?? "",
      name: row.discount_name ?? "",
      percentage: row.discount_percentage ?? "",
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

    // Each check names the field it failed on. This screen used to `return`
    // silently on an incomplete form, so pressing Submit simply did nothing
    // and gave the user no idea which field was at fault.
    if (!formData.countryId) {
      showToast("Country is required", "error");
      return;
    }
    if (!formData.name.trim()) {
      showToast("Discount Name is required", "error");
      return;
    }
    const pct = Number(formData.percentage);
    if (formData.percentage === "" || Number.isNaN(pct) || pct <= 0 || pct > 100) {
      // Mirrors the server rule (0 < pct <= 100) so an out-of-range value is
      // caught here rather than coming back as a 400.
      showToast("Discount Percentage must be a number between 1 and 100", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateDiscountType();
      } else {
        await createDiscountType();
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
      await APICall.deleteT(`/masterdata/discount/${id}`);
      showToast("Discount Type deleted successfully", "delete");
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
        title="Discount Types"
        loading={loading}
        emptyMessage="No discount types yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Discount Type",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "country_id",
            title: "Country",
            align: "left",
            type: "custom",
            // Without exportValue the CSV/PDF carried the raw foreign key.
            exportValue: (row) => countryName(row.country_id),
            render: (row) => countryName(row.country_id),
          },
          { key: "discount_name", title: "Discount Name", align: "left" },
          {
            key: "discount_percentage",
            title: "Discount Percentage (%)",
            align: "right",
            type: "custom",
            exportValue: (row) => row.discount_percentage,
            render: (row) =>
              row.discount_percentage === null || row.discount_percentage === undefined || row.discount_percentage === ""
                ? "—"
                : `${row.discount_percentage}%`,
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="discount type"
                onView={() => setViewData(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteId(row.id)}
              />
            ),
          },
        ]}
        data={rows}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Discount Type Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={2}>
          <DetailItem label="Country" value={viewData && countryName(viewData.country_id)} />
          <DetailItem label="Discount Name" value={viewData?.discount_name} />
          <DetailItem
            label="Discount Percentage"
            value={
              viewData?.discount_percentage === null || viewData?.discount_percentage === undefined || viewData?.discount_percentage === ""
                ? null
                : `${viewData.discount_percentage}%`
            }
          />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Discount Type" : "Add Discount Type"}
        onClose={closeModal}
        showFooter
        size="medium"
        bodyLayout="grid"
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
        <Select
          label="Country"
          required
          name="countryId"
          value={formData.countryId}
          onChange={handleChange}
          placeholder="Select country"
          options={countries.map((c) => ({ value: c.id, label: c.country_name }))}
        />
        <Input
          label="Discount Name"
          required
          name="name"
          placeholder="e.g. Corporate Rate"
          value={formData.name}
          onChange={handleChange}
        />
        <Input
          label="Discount Percentage"
          required
          type="number"
          inputMode="decimal"
          min="0.01"
          max="100"
          step="0.01"
          name="percentage"
          placeholder="0.00"
          value={formData.percentage}
          onChange={handleChange}
          helperText="Between 1 and 100."
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Discount Type"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this discount type? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default DiscountType;

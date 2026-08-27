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

const ENDPOINT = "/masterdata/country_currency";

const CurrencyCountry = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT(ENDPOINT),
    { select: readList, fallback: "Failed to load countries and currencies." },
  );

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = { countryName: "", currencySymbol: "", currencyName: "" };
  const [formData, setFormData] = useState(initialForm);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  // One payload builder for both create and update. They used to be written
  // out separately, and the update copy sent `currency_name: countryName` —
  // so editing any row silently overwrote the currency name with the country
  // name ("India" instead of "Rupee").
  const payload = () => ({
    country_name: formData.countryName.trim(),
    symbol: formData.currencySymbol.trim(),
    currency_name: formData.currencyName.trim(),
  });

  const createCurrency = async () => {
    await APICall.postT("/masterdata/country_currency", payload());
    showToast("Country / currency added successfully", "success");
    reload();
  };

  const updateCurrency = async () => {
    await APICall.putT("/masterdata/country_currency", { id: editId, ...payload() });
    showToast("Country / currency updated successfully", "update");
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
      countryName: row.country_name ?? "",
      currencySymbol: row.symbol ?? "",
      currencyName: row.currency_name ?? "",
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
    if (!formData.countryName.trim()) {
      showToast("Country name is required", "error");
      return;
    }
    if (!formData.currencySymbol.trim()) {
      showToast("Currency symbol is required", "error");
      return;
    }
    if (!formData.currencyName.trim()) {
      showToast("Currency name is required", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateCurrency();
      } else {
        await createCurrency();
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
      // Literal, not `${ENDPOINT}`: build_rbac_map.py reads these call
      // sites to derive the gateway permission map, and cannot resolve a
      // variable — this row had dropped out of it.
      await APICall.deleteT(`/masterdata/country_currency/${id}`);
      showToast("Country / currency deleted successfully", "delete");
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
        title="Countries & Currencies"
        loading={loading}
        emptyMessage="No countries yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Country",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "country_name", title: "Country", align: "left" },
          { key: "currency_name", title: "Currency", align: "left" },
          { key: "symbol", title: "Symbol", align: "center" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="country"
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
        title="Country & Currency Details"
        onClose={() => setViewData(null)}
        size="medium"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={2}>
          <DetailItem label="Country" value={viewData?.country_name} />
          <DetailItem label="Currency" value={viewData?.currency_name} />
          <DetailItem label="Symbol" value={viewData?.symbol} />
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Country & Currency" : "Add Country & Currency"}
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
        <Input
          label="Country Name"
          required
          name="countryName"
          placeholder="e.g. India"
          value={formData.countryName}
          onChange={handleChange}
        />
        <Input
          label="Currency Name"
          required
          name="currencyName"
          placeholder="e.g. Rupee"
          value={formData.currencyName}
          onChange={handleChange}
        />
        <Input
          label="Currency Symbol"
          required
          name="currencySymbol"
          placeholder="e.g. ₹"
          maxLength={8}
          value={formData.currencySymbol}
          onChange={handleChange}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Country & Currency"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this country and currency? Discounts and
        taxes that reference it may be affected. This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default CurrencyCountry;

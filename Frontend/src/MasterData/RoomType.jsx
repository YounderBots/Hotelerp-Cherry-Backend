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
import { readList, readNestedList } from "../functions/apiHelpers";
import { useApiResources } from "../hooks/useApiResource";
import { useToast } from "../hooks/useToast";

const ENDPOINT = "/masterdata/room_types";

// Declared once and used for the form, the payload and the View modal, so a
// rate can never appear in one of the three and be missing from another.
const RATE_FIELDS = [
  { name: "roomCost", api: "room_cost", label: "Room Cost" },
  { name: "extraBedCost", api: "bed_cost", label: "Extra Bed Cost" },
  { name: "dailyRate", api: "daily_rate", label: "Daily Rate" },
  { name: "weeklyRate", api: "weekly_rate", label: "Weekly Rate" },
  { name: "bedOnlyRate", api: "bed_only_rate", label: "Bed Only Rate" },
  { name: "bedBreakfastRate", api: "bed_breakfast_rate", label: "Bed & Breakfast Rate" },
  { name: "halfBoardRate", api: "half_board_rate", label: "Half Board Rate" },
  { name: "fullBoardRate", api: "full_board_rate", label: "Full Board Rate" },
];

// An empty numeric field means "not set" (null), not zero.
const numOrNull = (v) => (v === "" || v === null || v === undefined ? null : Number(v));

const showNum = (v) => (v === null || v === undefined || v === "" ? "—" : v);

const RoomType = () => {
  const {
    data: [rows, complementary],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT(ENDPOINT), select: readNestedList, fallback: "Failed to load room types." },
    { fetch: () => APICall.getT("/masterdata/complementry"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = useMemo(
    () => ({
      roomType: "",
      complementary: "",
      ...Object.fromEntries(RATE_FIELDS.map((f) => [f.name, ""])),
    }),
    [],
  );

  const [formData, setFormData] = useState(initialForm);

  // `complementry` on a row is a foreign key. The table used to render it with
  // type:"badge", which printed the raw id in a blue pill.
  const complementaryName = useMemo(() => {
    const map = new Map(complementary.map((c) => [String(c.id), c.complementry_name]));
    return (id) => map.get(String(id)) || "—";
  }, [complementary]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    // Numeric fields keep their raw string while editing, so clearing one
    // shows "" rather than snapping back to 0. numOrNull() converts at submit.
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ================= API ================= */

  const payload = () => ({
    type_name: formData.roomType.trim(),
    complementry: formData.complementary,
    ...Object.fromEntries(RATE_FIELDS.map((f) => [f.api, numOrNull(formData[f.name])])),
  });

  const createRoomType = async () => {
    await APICall.postT(ENDPOINT, payload());
    showToast("Room type added successfully", "success");
    reload();
  };

  const updateRoomType = async () => {
    await APICall.putT(ENDPOINT, { id: editId, ...payload() });
    showToast("Room type updated successfully", "update");
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
      roomType: row.room_type_name ?? "",
      complementary: row.complementry ?? "",
      ...Object.fromEntries(RATE_FIELDS.map((f) => [f.name, row[f.api] ?? ""])),
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
    if (!formData.roomType.trim()) {
      showToast("Room type is required", "error");
      return;
    }

    const negative = RATE_FIELDS.find((f) => {
      const n = numOrNull(formData[f.name]);
      return n !== null && (Number.isNaN(n) || n < 0);
    });
    if (negative) {
      showToast(`${negative.label} must be zero or more`, "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateRoomType();
      } else {
        await createRoomType();
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
      await APICall.deleteT(`${ENDPOINT}/${id}`);
      showToast("Room type deleted successfully", "delete");
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
        title="Room Types"
        loading={loading}
        emptyMessage="No room types yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Room Type",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "room_type_name", title: "Room Type", align: "left" },
          {
            key: "complementry",
            title: "Complementary",
            align: "left",
            type: "custom",
            exportValue: (row) => complementaryName(row.complementry),
            render: (row) => complementaryName(row.complementry),
          },
          {
            key: "room_cost",
            title: "Room Cost",
            align: "right",
            type: "custom",
            exportValue: (row) => row.room_cost,
            render: (row) => showNum(row.room_cost),
          },
          {
            key: "bed_cost",
            title: "Extra Bed Cost",
            align: "right",
            type: "custom",
            exportValue: (row) => row.bed_cost,
            render: (row) => showNum(row.bed_cost),
          },
          {
            key: "daily_rate",
            title: "Daily Rate",
            align: "right",
            type: "custom",
            exportValue: (row) => row.daily_rate,
            render: (row) => showNum(row.daily_rate),
          },
          {
            key: "weekly_rate",
            title: "Weekly Rate",
            align: "right",
            type: "custom",
            exportValue: (row) => row.weekly_rate,
            render: (row) => showNum(row.weekly_rate),
          },
          { key: "status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="room type"
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
        title="Room Type Details"
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <DetailList columns={3}>
          <DetailItem label="Room Type" value={viewData?.room_type_name} />
          <DetailItem
            label="Complementary"
            value={viewData && complementaryName(viewData.complementry)}
          />
          <DetailItem label="Status" value={viewData?.status} />
          {RATE_FIELDS.map((f) => (
            <DetailItem key={f.api} label={f.label} value={viewData?.[f.api]} />
          ))}
        </DetailList>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Room Type" : "Add Room Type"}
        onClose={closeModal}
        showFooter
        size="large"
        // The grid comes from the modal body rather than an inline style, so
        // it collapses to one column at the same breakpoint as every other
        // form in the app.
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
          label="Room Type"
          required
          name="roomType"
          placeholder="e.g. Deluxe Double"
          value={formData.roomType}
          onChange={handleChange}
        />
        <Select
          label="Complementary"
          name="complementary"
          value={formData.complementary}
          onChange={handleChange}
          placeholder="Select complementary"
          options={complementary.map((c) => ({ value: c.id, label: c.complementry_name }))}
        />
        {RATE_FIELDS.map((f) => (
          <Input
            key={f.name}
            label={f.label}
            type="number"
            inputMode="decimal"
            min="0"
            step="0.01"
            name={f.name}
            placeholder="0.00"
            value={formData[f.name] ?? ""}
            onChange={handleChange}
          />
        ))}
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Room Type"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this room type? Rooms assigned to it may
        be affected. This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default RoomType;

import React, { useMemo, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import Select from "../stories/Form/Select";
import ImagePicker from "../stories/Form/ImagePicker";
import RowActions from "../stories/RowActions";
import DetailList, { DetailItem } from "../stories/DetailList";
import ViewSection from "../stories/ViewSection";
import ErrorAlert from "../stories/ErrorAlert";
import Toast from "../stories/Toast";
import APICall from "../APICalls/APICalls";
import { readList } from "../functions/apiHelpers";
import { useApiResources } from "../hooks/useApiResource";
import { useToast } from "../hooks/useToast";

const ENDPOINT = "/masterdata/room";

const IMAGE_SLOTS = [0, 1, 2, 3];

const Rooms = () => {
  const {
    data: [rows, roomTypes, bedTypes],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT(ENDPOINT), select: readList, fallback: "Failed to load rooms." },
    { fetch: () => APICall.getT("/masterdata/room_types"), select: readList },
    { fetch: () => APICall.getT("/masterdata/bed_types"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = {
    room_no: "",
    room_name: "",
    room_type_id: "",
    bed_type_id: "",
    room_telephone: "",
    max_adult: "",
    max_child: "",
    // Round-tripped on update only; never edited here. See the form body.
    room_status: "",
    images: [null, null, null, null],
  };

  const [formData, setFormData] = useState(initialForm);

  const roomTypeName = useMemo(() => {
    const map = new Map(roomTypes.map((r) => [String(r.id), r.room_type_name]));
    return (id) => map.get(String(id)) || "—";
  }, [roomTypes]);

  const bedTypeName = useMemo(() => {
    const map = new Map(bedTypes.map((b) => [String(b.id), b.bed_type_name]));
    return (id) => map.get(String(id)) || "—";
  }, [bedTypes]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const setImage = (index, file) => {
    setFormData((prev) => {
      const images = [...prev.images];
      images[index] = file;
      return { ...prev, images };
    });
  };

  /* ================= API ================= */

  const buildForm = (isEdit) => {
    const form = new FormData();

    if (isEdit) form.append("room_id", editId);
    form.append("room_no", formData.room_no.trim());
    form.append("room_name", formData.room_name.trim());
    form.append("room_type_id", formData.room_type_id);
    form.append("bed_type_id", formData.bed_type_id);
    form.append("max_adult", formData.max_adult);
    form.append("max_child", formData.max_child);

    // The two endpoints spell the telephone differently: POST takes
    // `room_telephone`, PUT takes `tele_no`. Sending the POST spelling on an
    // update left the number unchanged on every edit.
    form.append(isEdit ? "tele_no" : "room_telephone", formData.room_telephone.trim());

    // room_condition is a required Form field on PUT, so the row's existing
    // value is sent straight back. POST does not take it at all.
    if (isEdit) form.append("room_condition", formData.room_status);

    // Images are optional on both endpoints. Only newly picked Files are
    // sent — an untouched slot keeps whatever the server already has.
    formData.images.forEach((img, i) => {
      if (img instanceof File) form.append(`image_${i + 1}`, img);
    });

    return form;
  };

  const createRoom = async () => {
    await APICall.postT("/masterdata/room", buildForm(false));
    showToast("Room added successfully", "success");
    reload();
  };

  const updateRoom = async () => {
    await APICall.putT("/masterdata/room", buildForm(true));
    showToast("Room updated successfully", "update");
    reload();
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    // GET /masterdata/room keys each row as `id`, not `room_id`; using
    // row.room_id here left editId undefined and the PUT failed with a 422.
    setEditId(row.id);
    setFormData({
      room_no: row.room_no ?? "",
      room_name: row.room_name ?? "",
      room_type_id: row.room_type_id ?? "",
      bed_type_id: row.bed_type_id ?? "",
      room_telephone: row.room_telephone ?? "",
      max_adult: row.max_adult ?? "",
      max_child: row.max_child ?? "",
      room_status: row.room_status || "",
      // Stored paths are kept as the API returns them ("/templates/static/
      // ..."). ImagePicker fetches them through the gateway with the session
      // token (authPrefix below); they used to be rewritten to an absolute URL
      // and handed to a plain <img src>, which carries no Authorization header
      // and was therefore answered 401 — every room photo rendered as an empty
      // slot.
      images: [
        row.images?.image_1 || null,
        row.images?.image_2 || null,
        row.images?.image_3 || null,
        row.images?.image_4 || null,
      ],
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditId(null);
    setFormData(initialForm);
  };

  const handleSave = async () => {
    if (saving) return;

    // These mirror the server's required Form(...) fields exactly. The screen
    // used to additionally demand all four images before it would submit —
    // they are optional server-side, and on edit the check made it impossible
    // to save any room that had fewer than four images stored.
    const required = [
      [formData.room_no.trim(), "Room number is required"],
      [formData.room_name.trim(), "Room name is required"],
      [formData.room_type_id, "Room type is required"],
      [formData.bed_type_id, "Bed type is required"],
      [String(formData.max_adult), "Max adults is required"],
      [String(formData.max_child), "Max children is required"],
    ];
    const missing = required.find(([v]) => !v);
    if (missing) {
      showToast(missing[1], "error");
      return;
    }

    if (Number(formData.max_adult) < 0 || Number(formData.max_child) < 0) {
      showToast("Occupancy cannot be negative", "error");
      return;
    }

    setSaving(true);
    try {
      // Awaited, and the modal only closes on success — this used to fire the
      // request and close immediately, so a rejected save looked like it had
      // worked until the list failed to change.
      if (editId) {
        await updateRoom();
      } else {
        await createRoom();
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
      await APICall.deleteT(`/masterdata/room/${id}`);
      showToast("Room deleted successfully", "delete");
      reload();
    } catch (err) {
      showToast(err?.message || "Delete failed", "error");
    }
  };

  const viewImages = viewData
    ? [
        viewData.images?.image_1,
        viewData.images?.image_2,
        viewData.images?.image_3,
        viewData.images?.image_4,
      ].filter(Boolean)
    : [];

  /* ================= UI ================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Rooms"
        loading={loading}
        emptyMessage="No rooms yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Room",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "room_no", title: "Room No", align: "left" },
          { key: "room_name", title: "Room Name", align: "left" },
          {
            key: "room_type_id",
            title: "Room Type",
            align: "left",
            type: "custom",
            exportValue: (row) => roomTypeName(row.room_type_id),
            render: (row) => roomTypeName(row.room_type_id),
          },
          {
            key: "bed_type_id",
            title: "Bed Type",
            align: "left",
            type: "custom",
            exportValue: (row) => bedTypeName(row.bed_type_id),
            render: (row) => bedTypeName(row.bed_type_id),
          },
          { key: "booking_status", title: "Booking", align: "center", type: "badge" },
          { key: "working_status", title: "Housekeeping", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="room"
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
        title={viewData ? `Room ${viewData.room_no}` : "Room Details"}
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
<ViewSection title="Room">
          <DetailList columns={3}>
            <DetailItem label="Room No" value={viewData?.room_no} />
            <DetailItem label="Room Name" value={viewData?.room_name} />
            <DetailItem label="Room Type" value={viewData && roomTypeName(viewData.room_type_id)} />
            <DetailItem label="Bed Type" value={viewData && bedTypeName(viewData.bed_type_id)} />
            <DetailItem label="Telephone" value={viewData?.room_telephone} />
            <DetailItem label="Occupancy" value={
              viewData ? `${viewData.max_adult ?? 0} adults · ${viewData.max_child ?? 0} children` : null
            } />
          </DetailList>
        </ViewSection>

        {/* All three statuses are set by operations elsewhere (reservations,
            housekeeping), never on this screen — read-only by design. */}
        <ViewSection title="Status">
          <DetailList columns={3}>
            <DetailItem label="Room" value={viewData?.room_status} />
            <DetailItem label="Booking" value={viewData?.booking_status} />
            <DetailItem label="Housekeeping" value={viewData?.working_status} />
          </DetailList>
        </ViewSection>

        {viewImages.length > 0 && (
          <ViewSection title="Images">
            <div className="image-picker-grid">
              {viewImages.map((img, i) => (
                <ImagePicker
                  key={img}
                  label={`Image ${i + 1}`}
                  value={img}
                  authPrefix="/masterdata"
                  readOnly
                />
              ))}
            </div>
          </ViewSection>
        )}
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Room" : "Add Room"}
        onClose={closeModal}
        showFooter
        size="large"
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
        <div className="field-grid">
          <Input
            label="Room No"
            required
            name="room_no"
            placeholder="e.g. 101"
            value={formData.room_no}
            onChange={handleChange}
          />
          <Input
            label="Room Name"
            required
            name="room_name"
            placeholder="e.g. Garden View"
            value={formData.room_name}
            onChange={handleChange}
          />
          <Select
            label="Room Type"
            required
            name="room_type_id"
            value={formData.room_type_id}
            onChange={handleChange}
            placeholder="Select room type"
            options={roomTypes.map((r) => ({ value: r.id, label: r.room_type_name }))}
          />
          <Select
            label="Bed Type"
            required
            name="bed_type_id"
            value={formData.bed_type_id}
            onChange={handleChange}
            placeholder="Select bed type"
            options={bedTypes.map((b) => ({ value: b.id, label: b.bed_type_name }))}
          />
          <Input
            label="Telephone"
            type="tel"
            name="room_telephone"
            placeholder="Extension or direct line"
            value={formData.room_telephone}
            onChange={handleChange}
          />
          <Input
            label="Max Adults"
            required
            type="number"
            inputMode="numeric"
            min="0"
            name="max_adult"
            placeholder="0"
            value={formData.max_adult}
            onChange={handleChange}
          />
          <Input
            label="Max Children"
            required
            type="number"
            inputMode="numeric"
            min="0"
            name="max_child"
            placeholder="0"
            value={formData.max_child}
            onChange={handleChange}
          />
          {/* No status control here, deliberately.
              - POST does not accept booking/working/room status at all; it
                sets them from server-side defaults. The old Add form showed
                "Room Status" and "Working Status" pickers whose values
                FastAPI discarded as unknown form fields.
              - PUT accepts only room_condition, and the values the old picker
                offered (Available / Occupied / Maintenance) are not the
                vocabulary the column actually holds (ACTIVE / UnBlocking,
                with CommonWords.Room_Condition = "UnBlocking" as the create
                default). Writing them would have corrupted the column.
              The stored value is round-tripped unchanged on update, and all
              three statuses are shown read-only in the View modal. */}
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Room Images</h4>
          <p className="modal-section__hint">
            Optional. {editId ? "Pick a file to replace an existing image." : "Up to four images."}
          </p>
          <div className="image-picker-grid">
            {IMAGE_SLOTS.map((i) => (
              <ImagePicker
                key={i}
                label={`Image ${i + 1}`}
                value={formData.images[i]}
                authPrefix="/masterdata"
                onChange={(file) => setImage(i, file)}
                onClear={() => setImage(i, null)}
                disabled={saving}
              />
            ))}
          </div>
        </div>
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Room"
        confirmText="Delete"
        size="small"
        destructive
      >
        Are you sure you want to delete this room? This action cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Rooms;

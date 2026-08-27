import React, { useMemo, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import TableFilters, { FilterDate, FilterSelect } from "../../stories/TableFilters";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { useApiResource } from "../../hooks/useApiResource";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import { useToast } from "../../hooks/useToast";

/**
 * Guest Enquiry — the front-office log of someone asking about the hotel
 * before they are a guest.
 *
 * WHAT A ROW MEANS
 * Who asked (guest_name), how the request reached us (inquiry_mode), what they
 * were told (response), what we owe them next (follow_up), anything that went
 * wrong while handling it (incidents), and whether the conversation is still
 * open (inquiry_status). It closes by being marked Completed, or is withdrawn
 * by a soft delete. There is no room, rate or booking link on this record —
 * `hotel.inquiry` has no foreign keys, and an enquiry that turns into a stay is
 * recorded by creating a reservation, not by mutating the enquiry.
 *
 * VOCABULARY IS NOT INVENTED HERE
 * MODES and STATUSES below are the values documented on models.Inquiry, held by
 * every row in the database, and now validated by the API. The previous version
 * of this screen shipped two lists it had made up — six modes ("Phone",
 * "Email", "Walk-in"...) and five statuses ("Open", "Resolved"...) — none of
 * which the backend recognised. Because it also *validated* against them, every
 * stored record failed the check and Edit could not be saved at all.
 *
 * These are true static constants, not master data: two closed sets of two
 * values each, with no table, endpoint or admin screen behind them anywhere in
 * the system. Reservation Status (Confirmed / Checked-In / ...) is master data
 * and is deliberately NOT reused — it describes a booking's lifecycle, which is
 * a different thing from whether a phone enquiry has been dealt with.
 */

const ENDPOINT = "/hotel/inquiry";
const PAGE_PATH = "/guest_enquiry";

// hotel.inquiry.inquiry_mode — how the enquiry reached the front office.
const MODES = ["Online", "Offline"];
// hotel.inquiry.inquiry_status — the enquiry's lifecycle.
const STATUSES = ["In Progress", "Completed"];

// varchar column widths from models.Inquiry, mirrored so the user is stopped at
// the field rather than by a 400 after pressing Submit.
const MAX_GUEST_NAME = 255;
const MAX_NOTE = 255;

const EMPTY_FORM = {
  guest_name: "",
  inquiry_mode: "",
  inquiry_status: "In Progress",
  response: "",
  follow_up: "",
  incidents: "",
};

const EMPTY_FILTERS = { status: "", mode: "", from: "", to: "" };

/** "2026-07-31T12:30:55" -> "2026-07-31", for comparing against a date input. */
const dayOf = (value) => String(value ?? "").slice(0, 10);

const formatDate = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

const formatDateTime = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

/** Two-line free-text cell; the full value is on the tooltip and in View. */
const NoteCell = ({ value }) =>
  value ? (
    <span className="table-cell-clamp" title={value}>
      {value}
    </span>
  ) : (
    "—"
  );

const GuestEnquiry = () => {
  const { data, loading, error, reload } = useApiResource(
    () => APICall.getT(ENDPOINT),
    { select: readList, fallback: "Failed to load guest enquiries." },
  );

  const permissions = usePagePermissions(PAGE_PATH);
  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const [formData, setFormData] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});

  const [filters, setFilters] = useState(EMPTY_FILTERS);

  /* ================= FILTERING ================= */

  const filtersActive =
    Boolean(filters.status) || Boolean(filters.mode) || Boolean(filters.from) || Boolean(filters.to);

  // Applied here rather than by the API: every list endpoint in this app
  // returns the company's full set and the screens narrow it, which is also how
  // TableTemplate's own search works. Splitting the two — server-side filters,
  // client-side search — would make the record count in the toolbar disagree
  // with the table under one of them.
  const rows = useMemo(() => {
    if (!filtersActive) return data;
    return data.filter((row) => {
      if (filters.status && row.inquiry_status !== filters.status) return false;
      if (filters.mode && row.inquiry_mode !== filters.mode) return false;
      const received = dayOf(row.created_at);
      if (filters.from && (!received || received < filters.from)) return false;
      if (filters.to && (!received || received > filters.to)) return false;
      return true;
    });
  }, [data, filters, filtersActive]);

  const setFilter = (key) => (event) =>
    setFilters((prev) => ({ ...prev, [key]: event.target.value }));

  /* ================= FORM ================= */

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear the field's error as soon as it is touched, so a message never
    // outlives the problem it describes.
    setErrors((prev) => (prev[name] ? { ...prev, [name]: undefined } : prev));
  };

  const validate = () => {
    const next = {};

    const guestName = formData.guest_name.trim();
    if (!guestName) next.guest_name = "Guest name is required.";
    else if (guestName.length > MAX_GUEST_NAME)
      next.guest_name = `Use ${MAX_GUEST_NAME} characters or fewer.`;

    if (!formData.inquiry_mode) next.inquiry_mode = "Enquiry mode is required.";
    else if (!MODES.includes(formData.inquiry_mode))
      next.inquiry_mode = `Choose one of: ${MODES.join(", ")}.`;

    if (!formData.inquiry_status) next.inquiry_status = "Status is required.";
    else if (!STATUSES.includes(formData.inquiry_status))
      next.inquiry_status = `Choose one of: ${STATUSES.join(", ")}.`;

    [
      ["response", "Response"],
      ["follow_up", "Follow-up"],
      ["incidents", "Incident notes"],
    ].forEach(([key, label]) => {
      if (formData[key].trim().length > MAX_NOTE)
        next[key] = `${label} must be ${MAX_NOTE} characters or fewer.`;
    });

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  /** Blank optional notes are sent as null so the column is cleared rather than
   *  storing an empty string that reads as "answered with nothing". */
  const buildPayload = () => ({
    inquiry_mode: formData.inquiry_mode,
    guest_name: formData.guest_name.trim(),
    inquiry_status: formData.inquiry_status,
    response: formData.response.trim() || null,
    follow_up: formData.follow_up.trim() || null,
    incidents: formData.incidents.trim() || null,
  });

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(EMPTY_FORM);
    setErrors({});
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({
      guest_name: row.guest_name ?? "",
      inquiry_mode: row.inquiry_mode ?? "",
      inquiry_status: row.inquiry_status ?? "",
      // The stored values are free text. The previous screen bound them to
      // <input type="date">, so it rendered "Sent rate card for Deluxe
      // rooms..." into a date field (blank on screen) and would have written
      // back the first ten characters.
      response: row.response ?? "",
      follow_up: row.follow_up ?? "",
      incidents: row.incidents ?? "",
    });
    setErrors({});
    setEditId(row.id);
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setEditId(null);
    setFormData(EMPTY_FORM);
    setErrors({});
  };

  const handleSave = async () => {
    if (saving) return;
    if (!validate()) {
      showToast("Please correct the highlighted fields", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await APICall.putT(ENDPOINT, { id: editId, ...buildPayload() });
        showToast("Enquiry updated successfully", "update");
      } else {
        await APICall.postT(ENDPOINT, buildPayload());
        showToast("Enquiry added successfully", "success");
      }
      // Awaited before closing: the list must not be repainted from a request
      // that is still in flight.
      await reload();
      setShowModal(false);
      setEditId(null);
      setFormData(EMPTY_FORM);
      setErrors({});
    } catch (err) {
      showToast(err?.message || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget || deleting) return;
    setDeleting(true);
    try {
      // Spelled out rather than built from ENDPOINT: Backend/tools/
      // build_rbac_map.py reads the SPA to decide which endpoints this page
      // may call, and it can only resolve a path literal. Written as
      // `${ENDPOINT}/${id}` the DELETE row drops out of ROUTE_PERMISSIONS
      // into UNCALLED_ENDPOINTS, and the gateway then denies it to every
      // role once RBAC_GATEWAY_MODE is `enforce`.
      await APICall.deleteT(`/hotel/inquiry/${deleteTarget.id}`);
      showToast("Enquiry deleted successfully", "delete");
      await reload();
      setDeleteTarget(null);
    } catch (err) {
      showToast(err?.message || "Delete failed", "error");
    } finally {
      setDeleting(false);
    }
  };

  /* ================= UI ================= */

  const emptyMessage = filtersActive
    ? "No enquiries match the selected filters."
    : "No guest enquiries yet. Add the first one to get started.";

  const columns = [
    { key: "guest_name", title: "Guest Name", align: "left" },
    { key: "inquiry_mode", title: "Mode", align: "left" },
    {
      key: "response",
      title: "Response",
      align: "left",
      type: "custom",
      exportValue: (row) => row.response || "",
      render: (row) => <NoteCell value={row.response} />,
    },
    {
      key: "follow_up",
      title: "Follow-up",
      align: "left",
      type: "custom",
      exportValue: (row) => row.follow_up || "",
      render: (row) => <NoteCell value={row.follow_up} />,
    },
    { key: "inquiry_status", title: "Status", align: "left", type: "badge" },
    {
      key: "created_at",
      title: "Received",
      align: "left",
      type: "custom",
      // Without this the toolbar search would match the raw ISO string while
      // the cell shows "31 Jul 2026", so typing what is on screen found nothing.
      exportValue: (row) => formatDate(row.created_at),
      render: (row) => formatDate(row.created_at),
    },
    {
      key: "actions",
      title: "Actions",
      align: "center",
      type: "custom",
      excludeFromExport: true,
      render: (row) => (
        <RowActions
          label={`enquiry from ${row.guest_name || "guest"}`}
          onView={() => setViewData(row)}
          onEdit={() => handleEdit(row)}
          onDelete={() => setDeleteTarget(row)}
          canEdit={permissions.edit}
          canDelete={permissions.delete}
        />
      ),
    },
  ];

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Guest Enquiry"
        loading={loading}
        emptyMessage={emptyMessage}
        searchable
        pagination
        exportable
        hasActionButton={permissions.add}
        actionButton={{
          label: "Add Enquiry",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        filters={
          <TableFilters
            onClear={() => setFilters(EMPTY_FILTERS)}
            isActive={filtersActive}
          >
            <FilterSelect
              id="ge-filter-status"
              label="Status"
              value={filters.status}
              onChange={setFilter("status")}
              options={STATUSES}
            />
            <FilterSelect
              id="ge-filter-mode"
              label="Mode"
              value={filters.mode}
              onChange={setFilter("mode")}
              options={MODES}
            />
            <FilterDate
              id="ge-filter-from"
              label="Received from"
              value={filters.from}
              onChange={setFilter("from")}
              max={filters.to}
            />
            <FilterDate
              id="ge-filter-to"
              label="Received to"
              value={filters.to}
              onChange={setFilter("to")}
              min={filters.from}
            />
          </TableFilters>
        }
        columns={columns}
        data={rows}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Guest Enquiry Details"
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <ViewSection title="Enquiry">
          <DetailList columns={3}>
            <DetailItem label="Guest Name" value={viewData?.guest_name} />
            <DetailItem label="Mode" value={viewData?.inquiry_mode} />
            <DetailItem label="Status" value={viewData?.inquiry_status} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Handling">
          <DetailList columns={1}>
            <DetailItem label="Response" value={viewData?.response} span={1} />
            <DetailItem label="Follow-up" value={viewData?.follow_up} span={1} />
            <DetailItem label="Incident Notes" value={viewData?.incidents} span={1} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Record">
          <DetailList columns={2}>
            <DetailItem label="Received" value={formatDateTime(viewData?.created_at)} />
            <DetailItem
              label="Last Updated"
              value={viewData?.updated_at ? formatDateTime(viewData.updated_at) : null}
            />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Enquiry" : "Add Enquiry"}
        onClose={closeModal}
        showFooter
        size="large"
        // "single" stacks the body with a gap and zeroes each field's own
        // margin; the three short fields get their own row through .field-grid
        // so the notes below can run full width.
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
        <div className="field-grid">
          <Input
            label="Guest Name"
            required
            name="guest_name"
            placeholder="e.g. Sameer Bhatia"
            value={formData.guest_name}
            onChange={handleChange}
            disabled={saving}
            maxLength={MAX_GUEST_NAME}
            autoComplete="off"
            error={!!errors.guest_name}
            helperText={errors.guest_name}
          />
          <Select
            label="Enquiry Mode"
            required
            name="inquiry_mode"
            placeholder="Select mode"
            value={formData.inquiry_mode}
            onChange={handleChange}
            disabled={saving}
            options={MODES}
            error={!!errors.inquiry_mode}
            helperText={errors.inquiry_mode || "How the enquiry reached the front office."}
          />
          <Select
            label="Status"
            required
            name="inquiry_status"
            placeholder="Select status"
            value={formData.inquiry_status}
            onChange={handleChange}
            disabled={saving}
            options={STATUSES}
            error={!!errors.inquiry_status}
            helperText={errors.inquiry_status}
          />
        </div>

        <Textarea
          label="Response"
          name="response"
          rows={3}
          placeholder="What the guest was told — e.g. Sent rate card for Deluxe rooms, awaiting confirmation"
          value={formData.response}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_NOTE}
          error={!!errors.response}
          helperText={errors.response}
        />

        <Textarea
          label="Follow-up"
          name="follow_up"
          rows={2}
          placeholder="What is owed next — e.g. Call back within 24 hours"
          value={formData.follow_up}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_NOTE}
          error={!!errors.follow_up}
          helperText={errors.follow_up}
        />

        <Textarea
          label="Incident Notes"
          name="incidents"
          rows={2}
          placeholder="Anything that went wrong while handling this enquiry"
          value={formData.incidents}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_NOTE}
          error={!!errors.incidents}
          helperText={errors.incidents}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => (deleting ? null : setDeleteTarget(null))}
        onConfirm={confirmDelete}
        title="Delete Enquiry"
        confirmText={deleting ? "Deleting…" : "Delete"}
        size="small"
        destructive
      >
        {`Delete the enquiry from ${deleteTarget?.guest_name || "this guest"}? This action cannot be undone.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default GuestEnquiry;

import React, { useMemo, useState } from "react";
import { Paperclip } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import TableFilters, { FilterDate, FilterSelect } from "../../stories/TableFilters";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import AttachmentPreview from "../../stories/AttachmentPreview";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import { useToast } from "../../hooks/useToast";

/**
 * Room Incident Log — what went wrong in a room and what was done about it.
 *
 * WHAT A ROW MEANS
 * A dated, timed record against one room: what happened, how bad it was, who
 * was involved, who saw it, what action was taken, who reported it and when,
 * plus an optional photo or scanned report. It is a log, not a workflow —
 * there is no assignee and no open/closed state on `hsk_room_incident`, and an
 * incident that needs cleaning or repair is recorded as a Task Assign row, not
 * by mutating this one.
 *
 * THE LIST WAS ALWAYS EMPTY
 * The loader read `res.data.data`. `APICall.getT` already returns the parsed
 * body, so the rows are at `res.data` and that expression was `undefined` on
 * every response — the table rendered "No incidents have been logged yet."
 * however many incidents the database held. This is the readList the rest of
 * the app uses.
 *
 * DROPDOWN SOURCES
 *   Room         /masterdata/room   value = room.id (the column holds the id)
 *   Reported By  /user/users        value = user.id
 * "Reported By" was a free-text box while both stored rows hold a user id, so
 * the column was already a reference in practice and the form let anyone type
 * over it. A value that does not match a known user still renders as-is, so
 * anything typed in before keeps displaying.
 *
 * SEVERITY is a true static constant — a four-value scale with no table,
 * endpoint or admin screen behind it anywhere in the system, now validated by
 * the API against the same list.
 *
 * ATTACHMENTS
 * Uploads are served by the authenticated gateway proxy, so a plain <img src>
 * at one gets a 401. `AttachmentPreview` fetches the bytes with the session
 * token and renders them from an object URL, which is what makes a stored file
 * viewable at all — before this it could be uploaded and never seen again.
 */

const PAGE_PATH = "/room_incident_log";

/*
 * ENDPOINT LITERALS, NOT A CONSTANT
 * The endpoint is spelled out at each call site rather than held in a shared
 * `const`. Backend/tools/build_rbac_map.py derives the gateway's permission map
 * from these literals; a call whose argument it cannot resolve is treated as
 * "this file issues POST dynamically", and it then pairs that verb with EVERY
 * endpoint literal in the file. With a const, that handed this page create and
 * edit rights over /masterdata/room and /user/users — both of which it only
 * reads.
 */


/** hsk_room_incident.severity — how serious the incident was. */
const SEVERITIES = ["Low", "Medium", "High", "Critical"];

// varchar width from models.HousekeeperRoomIncident, mirrored so the user is
// stopped at the field rather than by a 400 after pressing Submit.
const MAX_TEXT = 255;

// Mirrors the server's allow-list (BaseConfig.UPLOAD_ALLOWED_EXTENSIONS plus
// PDF) so the user is stopped at the field rather than by a 400 after Submit.
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"];
const ACCEPT_ATTR = ".jpg,.jpeg,.png,.gif,.webp,.pdf";
const MAX_UPLOAD_BYTES = 5 * 1024 * 1024; // BaseConfig.UPLOAD_MAX_BYTES

const EMPTY_FORM = {
  room_id: "",
  incident_date: "",
  incident_time: "",
  incident_description: "",
  involved_staff: "",
  severity: "",
  witnesses: "",
  actions_taken: "",
  reported_by: "",
  report_date: "",
  attachment: null,
};

const EMPTY_FILTERS = { severity: "", from: "", to: "" };

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

const formatTime = (value) => (value ? String(value).slice(0, 5) : "—");

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

const NoteCell = ({ value }) =>
  value ? (
    <span className="table-cell-clamp" title={value}>
      {value}
    </span>
  ) : (
    "—"
  );

const RoomIncidentLog = () => {
  const {
    data: [rows, rooms, users],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT("/hotel/roomincident_log"), select: readList, fallback: "Failed to load incident logs." },
    { fetch: () => APICall.getT("/masterdata/room"), select: readList },
    { fetch: () => APICall.getT("/user/users"), select: readList },
  ]);

  const permissions = usePagePermissions(PAGE_PATH);
  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editingRow, setEditingRow] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const [formData, setFormData] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  // Bumped to remount the file input, which is the only way to clear a
  // <input type="file"> without reaching for a ref.
  const [fileKey, setFileKey] = useState(0);

  /* ================= LOOKUPS ================= */

  const roomLabel = useMemo(() => {
    const byId = new Map(rooms.map((room) => [String(room.id), room]));
    return (id) => {
      const room = byId.get(String(id));
      if (!room) return id ? `Room #${id}` : "—";
      return room.room_name ? `${room.room_no} · ${room.room_name}` : String(room.room_no);
    };
  }, [rooms]);

  const roomNumber = useMemo(() => {
    const byId = new Map(rooms.map((room) => [String(room.id), room.room_no]));
    // An unresolved id reads as "—" rather than "#42": a database row
    // number is not a name, and a miss usually just means the reference
    // list has not loaded yet.
    return (id) => byId.get(String(id)) || "—";
  }, [rooms]);

  const fullName = (user) =>
    [user?.first_name, user?.last_name].filter(Boolean).join(" ").trim() ||
    user?.username ||
    "";

  /** A user id resolves to a name; anything else is shown as stored. */
  const reporterName = useMemo(() => {
    const byId = new Map(users.map((user) => [String(user.id), user]));
    return (value) => {
      if (!value) return "—";
      const user = byId.get(String(value));
      return user ? fullName(user) : String(value);
    };
  }, [users]);

  const roomOptions = useMemo(
    () =>
      rooms.map((room) => ({
        value: String(room.id),
        label: room.room_name ? `${room.room_no} · ${room.room_name}` : String(room.room_no),
      })),
    [rooms],
  );

  const userOptions = useMemo(
    () =>
      users.map((user) => ({
        value: String(user.id),
        label: user.user_code ? `${fullName(user)} (${user.user_code})` : fullName(user),
      })),
    [users],
  );

  /* ================= FILTERING ================= */

  const filtersActive =
    Boolean(filters.severity) || Boolean(filters.from) || Boolean(filters.to);

  const visibleRows = useMemo(() => {
    if (!filtersActive) return rows;
    return rows.filter((row) => {
      if (filters.severity && row.severity !== filters.severity) return false;
      const day = dayOf(row.incident_date);
      if (filters.from && (!day || day < filters.from)) return false;
      if (filters.to && (!day || day > filters.to)) return false;
      return true;
    });
  }, [rows, filters, filtersActive]);

  const setFilter = (key) => (event) =>
    setFilters((prev) => ({ ...prev, [key]: event.target.value }));

  /* ================= FORM ================= */

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => (prev[name] ? { ...prev, [name]: undefined } : prev));
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      setFormData((prev) => ({ ...prev, attachment: null }));
      return;
    }

    // Reported through the field's own helper text rather than alert(), which
    // blocks the page and matches nothing else in the app.
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setErrors((prev) => ({ ...prev, attachment: "Attach a JPG, PNG, GIF, WEBP or PDF." }));
      setFormData((prev) => ({ ...prev, attachment: null }));
      setFileKey((n) => n + 1);
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setErrors((prev) => ({ ...prev, attachment: "The attachment must be 5 MB or smaller." }));
      setFormData((prev) => ({ ...prev, attachment: null }));
      setFileKey((n) => n + 1);
      return;
    }

    setErrors((prev) => ({ ...prev, attachment: undefined }));
    setFormData((prev) => ({ ...prev, attachment: file }));
  };

  const validate = () => {
    const next = {};

    if (!formData.room_id) next.room_id = "Room is required.";
    if (!formData.incident_date) next.incident_date = "Incident date is required.";
    if (!formData.incident_time) next.incident_time = "Incident time is required.";

    const description = formData.incident_description.trim();
    if (!description) next.incident_description = "Describe what happened.";
    else if (description.length > MAX_TEXT)
      next.incident_description = `Use ${MAX_TEXT} characters or fewer.`;

    if (formData.severity && !SEVERITIES.includes(formData.severity))
      next.severity = `Choose one of: ${SEVERITIES.join(", ")}.`;

    // A report cannot be filed before the thing it reports happened.
    if (formData.report_date && formData.incident_date && formData.report_date < formData.incident_date)
      next.report_date = "The report date cannot be before the incident date.";

    [
      ["involved_staff", "Involved staff"],
      ["witnesses", "Witnesses"],
      ["actions_taken", "Actions taken"],
    ].forEach(([key, label]) => {
      if (formData[key].trim().length > MAX_TEXT)
        next[key] = `${label} must be ${MAX_TEXT} characters or fewer.`;
    });

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  /** Both create and update are multipart, so the attachment can be set on the
   *  way in and replaced later. An untouched file field sends nothing and the
   *  server keeps whatever it already had. */
  const buildForm = () => {
    const form = new FormData();
    if (editId) form.append("id", String(editId));
    form.append("room_id", formData.room_id);
    form.append("incident_date", formData.incident_date);
    form.append("incident_time", formData.incident_time);
    form.append("incident_description", formData.incident_description.trim());
    form.append("involved_staff", formData.involved_staff.trim());
    form.append("severity", formData.severity);
    form.append("witnesses", formData.witnesses.trim());
    form.append("actions_taken", formData.actions_taken.trim());
    form.append("reported_by", formData.reported_by);
    form.append("report_date", formData.report_date);
    if (formData.attachment instanceof File) {
      form.append("attachment_file", formData.attachment);
    }
    return form;
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(EMPTY_FORM);
    setErrors({});
    setEditId(null);
    setEditingRow(null);
    setFileKey((n) => n + 1);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({
      room_id: row.room_id != null ? String(row.room_id) : "",
      incident_date: dayOf(row.incident_date),
      incident_time: String(row.incident_time ?? "").slice(0, 5),
      incident_description: row.incident_description ?? "",
      involved_staff: row.involved_staff ?? "",
      severity: row.severity ?? "",
      witnesses: row.witnesses ?? "",
      actions_taken: row.actions_taken ?? "",
      reported_by: row.reported_by != null ? String(row.reported_by) : "",
      report_date: dayOf(row.report_date),
      attachment: null,
    });
    setErrors({});
    setEditId(row.id);
    setEditingRow(row);
    setFileKey((n) => n + 1);
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setEditId(null);
    setEditingRow(null);
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
      // Branch on editId. This used to call create unconditionally, so every
      // save from the Edit dialog appended a second copy of the record.
      if (editId) {
        await APICall.putT("/hotel/roomincident_log", buildForm());
        showToast("Incident updated successfully", "update");
      } else {
        await APICall.postT("/hotel/roomincident_log", buildForm());
        showToast("Incident logged successfully", "success");
      }
      await reload();
      setShowModal(false);
      setEditId(null);
      setEditingRow(null);
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
      await APICall.deleteT(`/hotel/roomincident_log/${deleteTarget.id}`);
      showToast("Incident deleted successfully", "delete");
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
    ? "No incidents match the selected filters."
    : "No incidents have been logged yet.";

  const columns = [
    {
      key: "room_id",
      title: "Room",
      align: "left",
      type: "custom",
      exportValue: (row) => roomNumber(row.room_id),
      render: (row) => roomNumber(row.room_id),
    },
    {
      key: "incident_date",
      title: "Occurred",
      align: "left",
      type: "custom",
      exportValue: (row) => `${formatDate(row.incident_date)} ${formatTime(row.incident_time)}`,
      render: (row) => (
        <span className="table-cell-nowrap">
          {`${formatDate(row.incident_date)} · ${formatTime(row.incident_time)}`}
        </span>
      ),
    },
    { key: "severity", title: "Severity", align: "center", type: "badge", badgeType: "priority" },
    {
      key: "incident_description",
      title: "Description",
      align: "left",
      type: "custom",
      exportValue: (row) => row.incident_description || "",
      render: (row) => <NoteCell value={row.incident_description} />,
    },
    {
      key: "reported_by",
      title: "Reported By",
      align: "left",
      type: "custom",
      exportValue: (row) => reporterName(row.reported_by),
      render: (row) => reporterName(row.reported_by),
    },
    {
      key: "attachment_file",
      title: "File",
      align: "center",
      type: "custom",
      exportValue: (row) => (row.attachment_file ? "Yes" : "No"),
      render: (row) =>
        row.attachment_file ? (
          <Paperclip size={15} aria-label="Has an attachment" className="attachment-flag" />
        ) : (
          "—"
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
          label={`incident in room ${roomNumber(row.room_id)}`}
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
        title="Room Incident Log"
        loading={loading}
        emptyMessage={emptyMessage}
        searchable
        pagination
        exportable
        hasActionButton={permissions.add}
        actionButton={{
          label: "Add Incident",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        filters={
          <TableFilters onClear={() => setFilters(EMPTY_FILTERS)} isActive={filtersActive}>
            <FilterSelect
              id="ril-filter-severity"
              label="Severity"
              value={filters.severity}
              onChange={setFilter("severity")}
              options={SEVERITIES}
            />
            <FilterDate
              id="ril-filter-from"
              label="Occurred from"
              value={filters.from}
              onChange={setFilter("from")}
              max={filters.to}
            />
            <FilterDate
              id="ril-filter-to"
              label="Occurred to"
              value={filters.to}
              onChange={setFilter("to")}
              min={filters.from}
            />
          </TableFilters>
        }
        columns={columns}
        data={visibleRows}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title={viewData ? `Incident · Room ${roomNumber(viewData.room_id)}` : "Incident Details"}
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <ViewSection title="Incident">
          {/* One DetailList per section, like every other View in the app.
              `span` widens the description rather than starting a second list
              just to get a full-width row. */}
          <DetailList columns={3}>
            <DetailItem label="Room" value={viewData && roomLabel(viewData.room_id)} />
            <DetailItem label="Date" value={formatDate(viewData?.incident_date)} />
            <DetailItem label="Time" value={formatTime(viewData?.incident_time)} />
            <DetailItem label="Severity" value={viewData?.severity} />
            <DetailItem
              label="What Happened"
              value={viewData?.incident_description}
              span={3}
            />
          </DetailList>
        </ViewSection>

        <ViewSection title="People">
          <DetailList columns={2}>
            <DetailItem label="Involved Staff" value={viewData?.involved_staff} />
            <DetailItem label="Witnesses" value={viewData?.witnesses} />
            <DetailItem label="Reported By" value={viewData && reporterName(viewData.reported_by)} />
            <DetailItem label="Report Date" value={formatDate(viewData?.report_date)} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Resolution">
          <DetailList columns={1}>
            <DetailItem label="Actions Taken" value={viewData?.actions_taken} />
          </DetailList>
        </ViewSection>

        {viewData?.attachment_file && (
          <ViewSection title="Attachment">
            <AttachmentPreview
              path={viewData.attachment_file}
              prefix="/hotel"
              alt={`Attachment for the incident in room ${roomNumber(viewData.room_id)}`}
            />
          </ViewSection>
        )}

        <ViewSection title="Record">
          <DetailList columns={2}>
            <DetailItem label="Logged" value={formatDateTime(viewData?.created_at)} />
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
        // The title said "Add Incident" even when editing an existing one.
        title={editId ? "Edit Incident" : "Add Incident"}
        onClose={closeModal}
        showFooter
        size="large"
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
          <Select
            label="Room"
            required
            name="room_id"
            placeholder="Select room"
            value={formData.room_id}
            onChange={handleChange}
            disabled={saving}
            options={roomOptions}
            error={!!errors.room_id}
            helperText={errors.room_id}
          />
          <Input
            label="Incident Date"
            required
            type="date"
            name="incident_date"
            value={formData.incident_date}
            onChange={handleChange}
            disabled={saving}
            error={!!errors.incident_date}
            helperText={errors.incident_date}
          />
          <Input
            label="Incident Time"
            required
            type="time"
            name="incident_time"
            value={formData.incident_time}
            onChange={handleChange}
            disabled={saving}
            error={!!errors.incident_time}
            helperText={errors.incident_time}
          />
          <Select
            label="Severity"
            name="severity"
            placeholder="Select severity"
            value={formData.severity}
            onChange={handleChange}
            disabled={saving}
            options={SEVERITIES}
            error={!!errors.severity}
            helperText={errors.severity}
          />
          <Select
            label="Reported By"
            name="reported_by"
            placeholder="Select staff"
            value={formData.reported_by}
            onChange={handleChange}
            disabled={saving}
            options={userOptions}
            error={!!errors.reported_by}
            helperText={errors.reported_by}
          />
          <Input
            label="Report Date"
            type="date"
            name="report_date"
            value={formData.report_date}
            onChange={handleChange}
            disabled={saving}
            min={formData.incident_date || undefined}
            error={!!errors.report_date}
            helperText={errors.report_date}
          />
        </div>

        <Textarea
          label="What Happened"
          required
          name="incident_description"
          rows={3}
          placeholder="e.g. Minor water leak reported near the bathroom sink"
          value={formData.incident_description}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_TEXT}
          error={!!errors.incident_description}
          helperText={errors.incident_description}
        />

        <div className="field-grid">
          <Input
            label="Involved Staff"
            name="involved_staff"
            placeholder="e.g. Housekeeping — Floor 2"
            value={formData.involved_staff}
            onChange={handleChange}
            disabled={saving}
            maxLength={MAX_TEXT}
            autoComplete="off"
            error={!!errors.involved_staff}
            helperText={errors.involved_staff || "The team or people handling it."}
          />
          <Input
            label="Witnesses"
            name="witnesses"
            placeholder="e.g. Guest in 204"
            value={formData.witnesses}
            onChange={handleChange}
            disabled={saving}
            maxLength={MAX_TEXT}
            autoComplete="off"
            error={!!errors.witnesses}
            helperText={errors.witnesses}
          />
        </div>

        <Textarea
          label="Actions Taken"
          name="actions_taken"
          rows={2}
          placeholder="e.g. Maintenance notified, plumber dispatched"
          value={formData.actions_taken}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_TEXT}
          error={!!errors.actions_taken}
          helperText={errors.actions_taken}
        />

        <div className="modal-section">
          <h4 className="modal-section__title">Attachment</h4>
          <p className="modal-section__hint">
            Optional — a photo of the damage or a scanned report. JPG, PNG, GIF, WEBP or
            PDF, up to 5 MB.
            {editId && editingRow?.attachment_file
              ? " Picking a file replaces the one already attached."
              : ""}
          </p>

          {editId && editingRow?.attachment_file && !formData.attachment && (
            <div className="modal-section__preview">
              <AttachmentPreview
                path={editingRow.attachment_file}
                prefix="/hotel"
                alt="The attachment currently on this incident"
              />
            </div>
          )}

          <Input
            key={fileKey}
            label={formData.attachment ? formData.attachment.name : "Choose a file"}
            type="file"
            accept={ACCEPT_ATTR}
            onChange={handleFileChange}
            disabled={saving}
            error={!!errors.attachment}
            helperText={errors.attachment}
          />
        </div>
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => (deleting ? null : setDeleteTarget(null))}
        onConfirm={confirmDelete}
        title="Delete Incident"
        confirmText={deleting ? "Deleting…" : "Delete"}
        size="small"
        destructive
      >
        {`Delete the incident logged for room ${
          deleteTarget ? roomNumber(deleteTarget.room_id) : ""
        }? This action cannot be undone.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default RoomIncidentLog;

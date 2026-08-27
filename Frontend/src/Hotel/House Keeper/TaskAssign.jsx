import React, { useMemo, useState } from "react";
import TableTemplate, { ColorSwatchCell } from "../../stories/TableTemplate";
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
import { useApiResources } from "../../hooks/useApiResource";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import { useToast } from "../../hooks/useToast";

/**
 * Task Assign — the housekeeping work list.
 *
 * WHAT A ROW MEANS
 * One piece of housekeeping work: a room, a task type, the staff member it is
 * assigned to, when it is scheduled, how far along it is, and whether the room
 * is held out of service while it happens. Lost property found during the job
 * and any instruction for the housekeeper ride along on the same record.
 *
 * IT IS NOT A LIST OF HOUSEKEEPERS. The screen is named after the department,
 * but the entity is the assignment. Staff themselves are HRM's Employee /
 * User screens; this only points at one.
 *
 * WHY ONE STAFF PICKER FILLS FOUR COLUMNS
 * `housekeeper_task` carries employee_id, first_name, last_name AND
 * assign_staff, all NOT NULL, and every row in the database has employee_id
 * and assign_staff set to the same user id. The two name columns are that
 * user's name denormalised onto the row — the dashboard and the night-audit
 * screen read the name from here rather than joining across to UserServices,
 * so they cannot be dropped. The old form offered a dead "Employee ID" picker
 * (rendered with no name/value/onChange, so it could not be used at all), two
 * free-text name boxes that were never checked against the person selected,
 * and a separate "Assigned Staff" picker over the same user list. One picker
 * now writes all four, which is the only combination that cannot contradict
 * itself.
 *
 * DROPDOWN SOURCES — ALL SERVER-SIDE, NONE INVENTED HERE
 *   Room       /masterdata/room       value = room.id (the column holds the id)
 *   Task Type  /masterdata/task_type  value = task_name (see below)
 *   Staff      /user/users            value = user.id
 * Task Type was a free-text box, so every housekeeper could coin a new task
 * name while Master Data > HSK Task Type sat there as the authoritative list.
 * The NAME is stored rather than the id because that is what all five existing
 * rows hold and what the dashboard and the night-audit CSV render directly;
 * storing ids instead would need a migration of live data and would show a bare
 * number on two other screens.
 *
 * TASK STATUS / ROOM STATUS are true static constants: the vocabularies
 * documented on models.HousekeeperTask, held by every stored row and now
 * validated by the API. There is no master table behind either. The previous
 * form offered "Assigned" and "In Progress", neither of which the column has
 * ever held — it stores Pending and In-Progress.
 *
 * ROOM STATUS REACHES THE ROOM. Setting a task to Blocking marks the room out
 * of order in Master Data, and the reservation availability rules refuse to
 * sell a blocked room. Completing or deleting the task releases it. That
 * happens server-side in the housekeeping controller so it holds however the
 * record is changed.
 */

const PAGE_PATH = "/task_assign";

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


// models.HousekeeperTask.task_status — the work's lifecycle.
const TASK_STATUSES = ["Pending", "In-Progress", "Completed"];
// models.HousekeeperTask.room_status — whether the room is held out of service.
const ROOM_STATUSES = ["Blocking", "Unblocking"];

// varchar widths from models.HousekeeperTask, mirrored so the user is stopped
// at the field rather than by a 400 after pressing Submit.
const MAX_NOTE = 255;

const EMPTY_FORM = {
  employee_id: "",
  first_name: "",
  last_name: "",
  room_no: "",
  task_type: "",
  schedule_date: "",
  schedule_time: "",
  task_status: "Pending",
  room_status: "Unblocking",
  lost_found: "",
  special_instructions: "",
};

const EMPTY_FILTERS = { task_status: "", room_status: "", from: "", to: "" };

/** "2026-07-31T12:30:55" / "2026-07-31" -> "2026-07-31", for date comparisons. */
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

/** "10:00:00" -> "10:00". The seconds are always zero and only add noise. */
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

/** Two-line free-text cell; the full value is on the tooltip and in View. */
const NoteCell = ({ value }) =>
  value ? (
    <span className="table-cell-clamp" title={value}>
      {value}
    </span>
  ) : (
    "—"
  );

const TaskAssign = () => {
  const {
    data: [rows, rooms, taskTypes, users],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT("/hotel/housekeeper_tasks"), select: readList, fallback: "Failed to load housekeeping tasks." },
    { fetch: () => APICall.getT("/masterdata/room"), select: readList },
    { fetch: () => APICall.getT("/masterdata/task_type"), select: readList },
    { fetch: () => APICall.getT("/user/users"), select: readList },
  ]);

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

  /* ================= LOOKUPS ================= */

  // The table used to print `room_no` and `assign_staff` straight out of the
  // row, which meant a column headed "Room No" showed 22 (the room's primary
  // key) instead of 202, and "Assigned Staff" showed 2 instead of a name.
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
    return (id) => byId.get(String(id)) || (id ? `#${id}` : "—");
  }, [rooms]);

  /** The colour Master Data assigns this task type, so the tag reads the same
   *  here as it does on the HSK Task Type screen. */
  const taskTypeColor = useMemo(() => {
    const byName = new Map(taskTypes.map((type) => [type.task_name, type.color]));
    return (name) => byName.get(name) || null;
  }, [taskTypes]);

  const userById = useMemo(
    () => new Map(users.map((user) => [String(user.id), user])),
    [users],
  );

  const fullName = (user) =>
    [user?.first_name, user?.last_name].filter(Boolean).join(" ").trim() ||
    user?.username ||
    "";

  /** The name on the record, falling back to the user record it points at. */
  const staffName = (row) => {
    const stored = [row?.first_name, row?.last_name].filter(Boolean).join(" ").trim();
    if (stored) return stored;
    return fullName(userById.get(String(row?.employee_id))) || "—";
  };

  const staffOptions = useMemo(
    () =>
      users.map((user) => ({
        value: String(user.id),
        label: user.user_code ? `${fullName(user)} (${user.user_code})` : fullName(user),
      })),
    [users],
  );

  const roomOptions = useMemo(
    () =>
      rooms.map((room) => ({
        value: String(room.id),
        label: room.room_name ? `${room.room_no} · ${room.room_name}` : String(room.room_no),
      })),
    [rooms],
  );

  // Only the task types Master Data still has active — the endpoint already
  // filters INACTIVE rows out, so a retired task type cannot be picked while
  // tasks that already reference it keep rendering their stored name.
  const taskTypeOptions = useMemo(
    () => taskTypes.map((type) => ({ value: type.task_name, label: type.task_name })),
    [taskTypes],
  );

  /* ================= FILTERING ================= */

  const filtersActive =
    Boolean(filters.task_status) ||
    Boolean(filters.room_status) ||
    Boolean(filters.from) ||
    Boolean(filters.to);

  // Applied here rather than by the API: the list endpoint returns the
  // company's full set and the screen narrows it, which is also how
  // TableTemplate's own search and record count work.
  const visibleRows = useMemo(() => {
    if (!filtersActive) return rows;
    return rows.filter((row) => {
      if (filters.task_status && row.task_status !== filters.task_status) return false;
      if (filters.room_status && row.room_status !== filters.room_status) return false;
      const day = dayOf(row.schedule_date);
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

  /** Picking a staff member fills the two denormalised name columns with it. */
  const handleStaffChange = (event) => {
    const value = event.target.value;
    const user = userById.get(String(value));
    setFormData((prev) => ({
      ...prev,
      employee_id: value,
      // Keep whatever the record already held when the id points at a user who
      // is no longer in the list, so editing an old task cannot blank its name.
      first_name: user ? user.first_name || user.username || "" : prev.first_name,
      last_name: user ? user.last_name || "" : prev.last_name,
    }));
    setErrors((prev) => (prev.employee_id ? { ...prev, employee_id: undefined } : prev));
  };

  const validate = () => {
    const next = {};

    if (!formData.employee_id) next.employee_id = "Assigned staff is required.";
    else if (!formData.first_name.trim())
      next.employee_id = "The selected staff member has no name on record.";

    if (!formData.room_no) next.room_no = "Room is required.";
    if (!formData.task_type) next.task_type = "Task type is required.";
    if (!formData.schedule_date) next.schedule_date = "Schedule date is required.";
    if (!formData.schedule_time) next.schedule_time = "Schedule time is required.";

    if (!TASK_STATUSES.includes(formData.task_status))
      next.task_status = `Choose one of: ${TASK_STATUSES.join(", ")}.`;
    if (!ROOM_STATUSES.includes(formData.room_status))
      next.room_status = `Choose one of: ${ROOM_STATUSES.join(", ")}.`;

    [
      ["lost_found", "Lost & found"],
      ["special_instructions", "Special instructions"],
    ].forEach(([key, label]) => {
      if (formData[key].trim().length > MAX_NOTE)
        next[key] = `${label} must be ${MAX_NOTE} characters or fewer.`;
    });

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  /** Blank optional notes are sent as null so the column is cleared rather
   *  than storing an empty string. */
  const buildPayload = () => ({
    employee_id: formData.employee_id,
    // Both id columns describe the same person; see the header comment.
    assign_staff: formData.employee_id,
    first_name: formData.first_name.trim(),
    last_name: formData.last_name.trim(),
    room_no: formData.room_no,
    task_type: formData.task_type,
    schedule_date: formData.schedule_date,
    schedule_time: formData.schedule_time,
    task_status: formData.task_status,
    room_status: formData.room_status,
    lost_found: formData.lost_found.trim() || null,
    special_instructions: formData.special_instructions.trim() || null,
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
      employee_id: row.employee_id != null ? String(row.employee_id) : "",
      first_name: row.first_name ?? "",
      last_name: row.last_name ?? "",
      room_no: row.room_no != null ? String(row.room_no) : "",
      task_type: row.task_type ?? "",
      schedule_date: dayOf(row.schedule_date),
      // <input type="time"> wants HH:MM; the row carries HH:MM:SS.
      schedule_time: String(row.schedule_time ?? "").slice(0, 5),
      task_status: row.task_status ?? TASK_STATUSES[0],
      room_status: row.room_status ?? ROOM_STATUSES[1],
      lost_found: row.lost_found ?? "",
      special_instructions: row.special_instructions ?? "",
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
        await APICall.putT("/hotel/housekeeper_tasks", { id: editId, ...buildPayload() });
        showToast("Task updated successfully", "update");
      } else {
        await APICall.postT("/hotel/housekeeper_tasks", buildPayload());
        showToast("Task assigned successfully", "success");
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
      await APICall.deleteT(`/hotel/housekeeper_tasks/${deleteTarget.id}`);
      showToast("Task deleted successfully", "delete");
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
    ? "No tasks match the selected filters."
    : "No housekeeping tasks yet. Assign the first one to get started.";

  const columns = [
    {
      key: "first_name",
      title: "Assigned To",
      align: "left",
      type: "custom",
      exportValue: (row) => staffName(row),
      render: (row) => staffName(row),
    },
    {
      key: "room_no",
      title: "Room",
      align: "left",
      type: "custom",
      exportValue: (row) => roomNumber(row.room_no),
      render: (row) => roomNumber(row.room_no),
    },
    {
      key: "task_type",
      title: "Task Type",
      align: "left",
      type: "custom",
      exportValue: (row) => row.task_type || "",
      render: (row) =>
        row.task_type ? (
          <ColorSwatchCell color={taskTypeColor(row.task_type)} label={row.task_type} />
        ) : (
          "—"
        ),
    },
    {
      key: "schedule_date",
      title: "Scheduled",
      align: "left",
      type: "custom",
      // Without this the toolbar search would match the raw ISO string while
      // the cell shows "31 Jul 2026", so typing what is on screen found nothing.
      exportValue: (row) => `${formatDate(row.schedule_date)} ${formatTime(row.schedule_time)}`,
      render: (row) => (
        <span className="table-cell-nowrap">
          {`${formatDate(row.schedule_date)} · ${formatTime(row.schedule_time)}`}
        </span>
      ),
    },
    // Headed "Room Status", not "Room": the column beside it is the room
    // number, and two columns headed "Room" is not a table anyone can read.
    { key: "room_status", title: "Room Status", align: "center", type: "badge" },
    { key: "task_status", title: "Task Status", align: "center", type: "badge" },
    {
      key: "actions",
      title: "Actions",
      align: "center",
      type: "custom",
      excludeFromExport: true,
      render: (row) => (
        <RowActions
          label={`task for room ${roomNumber(row.room_no)}`}
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
        title="Task Assign"
        loading={loading}
        emptyMessage={emptyMessage}
        searchable
        pagination
        exportable
        hasActionButton={permissions.add}
        actionButton={{
          label: "Assign Task",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        filters={
          <TableFilters onClear={() => setFilters(EMPTY_FILTERS)} isActive={filtersActive}>
            <FilterSelect
              id="ta-filter-task-status"
              label="Task Status"
              value={filters.task_status}
              onChange={setFilter("task_status")}
              options={TASK_STATUSES}
            />
            <FilterSelect
              id="ta-filter-room-status"
              label="Room Status"
              value={filters.room_status}
              onChange={setFilter("room_status")}
              options={ROOM_STATUSES}
            />
            <FilterDate
              id="ta-filter-from"
              label="Scheduled from"
              value={filters.from}
              onChange={setFilter("from")}
              max={filters.to}
            />
            <FilterDate
              id="ta-filter-to"
              label="Scheduled to"
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
        title={viewData ? `Task · Room ${roomNumber(viewData.room_no)}` : "Task Details"}
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        <ViewSection title="Assignment">
          <DetailList columns={3}>
            <DetailItem label="Assigned To" value={viewData && staffName(viewData)} />
            <DetailItem
              label="Staff Code"
              value={userById.get(String(viewData?.employee_id))?.user_code}
            />
            <DetailItem label="Room" value={viewData && roomLabel(viewData.room_no)} />
            <DetailItem label="Task Type" value={viewData?.task_type} />
            <DetailItem label="Schedule Date" value={formatDate(viewData?.schedule_date)} />
            <DetailItem label="Schedule Time" value={formatTime(viewData?.schedule_time)} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Status">
          <DetailList columns={2}>
            <DetailItem label="Task Status" value={viewData?.task_status} />
            <DetailItem
              label="Room Status"
              value={viewData?.room_status}
              // The consequence of the value is not obvious from the word
              // alone, and this is the screen that causes it.
            />
          </DetailList>
        </ViewSection>

        <ViewSection title="Notes">
          <DetailList columns={1}>
            <DetailItem label="Lost & Found" value={viewData?.lost_found} />
            <DetailItem label="Special Instructions" value={viewData?.special_instructions} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Record">
          <DetailList columns={2}>
            <DetailItem label="Created" value={formatDateTime(viewData?.created_at)} />
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
        title={editId ? "Edit Task" : "Assign Task"}
        onClose={closeModal}
        showFooter
        size="large"
        // "single" stacks the body with a gap and zeroes each field's own
        // margin; the short fields get their own rows through .field-grid so
        // the notes below can run full width.
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
            label="Assigned To"
            required
            name="employee_id"
            placeholder="Select staff"
            value={formData.employee_id}
            onChange={handleStaffChange}
            disabled={saving}
            options={staffOptions}
            error={!!errors.employee_id}
            helperText={errors.employee_id || "The housekeeper who will do the work."}
          />
          <Select
            label="Room"
            required
            name="room_no"
            placeholder="Select room"
            value={formData.room_no}
            onChange={handleChange}
            disabled={saving}
            options={roomOptions}
            error={!!errors.room_no}
            helperText={errors.room_no}
          />
          <Select
            label="Task Type"
            required
            name="task_type"
            placeholder="Select task type"
            value={formData.task_type}
            onChange={handleChange}
            disabled={saving}
            options={taskTypeOptions}
            error={!!errors.task_type}
            helperText={errors.task_type || "Managed in Master Data › HSK Task Type."}
          />
        </div>

        <div className="field-grid">
          <Input
            label="Schedule Date"
            required
            type="date"
            name="schedule_date"
            value={formData.schedule_date}
            onChange={handleChange}
            disabled={saving}
            error={!!errors.schedule_date}
            helperText={errors.schedule_date}
          />
          <Input
            label="Schedule Time"
            required
            type="time"
            name="schedule_time"
            value={formData.schedule_time}
            onChange={handleChange}
            disabled={saving}
            error={!!errors.schedule_time}
            helperText={errors.schedule_time}
          />
          <Select
            label="Task Status"
            required
            name="task_status"
            placeholder="Select status"
            value={formData.task_status}
            onChange={handleChange}
            disabled={saving}
            options={TASK_STATUSES}
            error={!!errors.task_status}
            helperText={errors.task_status}
          />
          <Select
            label="Room Status"
            required
            name="room_status"
            placeholder="Select room status"
            value={formData.room_status}
            onChange={handleChange}
            disabled={saving}
            options={ROOM_STATUSES}
            error={!!errors.room_status}
            helperText={
              errors.room_status ||
              (formData.room_status === "Blocking"
                ? "Holds the room out of service — it cannot be booked until the task is done."
                : "The room stays available for booking.")
            }
          />
        </div>

        <Textarea
          label="Lost & Found"
          name="lost_found"
          rows={2}
          placeholder="Anything left behind in the room — e.g. Blue scarf, handed to reception"
          value={formData.lost_found}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_NOTE}
          error={!!errors.lost_found}
          helperText={errors.lost_found}
        />

        <Textarea
          label="Special Instructions"
          name="special_instructions"
          rows={2}
          placeholder="Anything the housekeeper needs to know — e.g. Guest allergic to strong detergent"
          value={formData.special_instructions}
          onChange={handleChange}
          disabled={saving}
          maxLength={MAX_NOTE}
          error={!!errors.special_instructions}
          helperText={errors.special_instructions}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => (deleting ? null : setDeleteTarget(null))}
        onConfirm={confirmDelete}
        title="Delete Task"
        confirmText={deleting ? "Deleting…" : "Delete"}
        size="small"
        destructive
      >
        {`Delete the ${deleteTarget?.task_type || "housekeeping"} task for room ${
          deleteTarget ? roomNumber(deleteTarget.room_no) : ""
        }? This action cannot be undone.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default TaskAssign;

import React, { useMemo, useState } from "react";
import TableTemplate from "../../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../../stories/Modal";
import Input from "../../../stories/Form/Input";
import Select from "../../../stories/Form/Select";
import RowActions from "../../../stories/RowActions";
import IconButton from "../../../stories/IconButton";
import DetailList, { DetailItem } from "../../../stories/DetailList";
import ViewSection from "../../../stories/ViewSection";
import ErrorAlert from "../../../stories/ErrorAlert";
import Toast from "../../../stories/Toast";
import { LogIn, LogOut } from "lucide-react";
import { useApiResources } from "../../../hooks/useApiResource";
import { useToast } from "../../../hooks/useToast";
import { todayIso } from "../../../functions/formatters";

/**
 * Shift scheduling + clock in/out, shared by the Restaurant and Bar screens.
 *
 * The Restaurant and Bar versions were two 300-line files differing only in
 * endpoint, role vocabulary and whether the venue has a `section` column. They
 * are one component now, configured per venue.
 *
 * The API calls stay in the per-venue wrapper on purpose: the gateway's RBAC
 * map (Backend/tools/build_rbac_map.py) attributes an endpoint to a page by
 * finding `APICall.<verb>("/literal")` in the routed file and the components it
 * imports. Putting both venues' literals in this shared file would grant the
 * Restaurant page the Bar endpoints and vice versa.
 */

/** "2026-08-06" -> "06 Aug 2026". The raw ISO string wrapped onto three lines
 *  in the Date column and read as machine output rather than a date. */
const formatDay = (iso) => {
  if (!iso) return "—";
  const d = new Date(`${String(iso).slice(0, 10)}T00:00:00`);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
};

/** "09:00:00" -> "09:00". Seconds are never meaningful on a roster. */
const formatTime = (t) => (t ? String(t).slice(0, 5) : null);

const StaffShiftPlanning = ({
  /** "Restaurant" | "Bar" — used for copy only. */
  venueLabel,
  /** The venue's DB role enum. Must match the SAEnum in its models.py. */
  roleOptions,
  /** Venue has a free `section` column alongside floor_id (Restaurant only). */
  hasSection = false,
  api,
}) => {
  const {
    data: [shifts, employees, floors],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: api.listShifts, select: api.readList, fallback: `Failed to load ${venueLabel.toLowerCase()} shifts.` },
    { fetch: api.listEmployees, select: api.readList },
    { fetch: api.listFloors, select: api.readList },
  ]);

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [clock, setClock] = useState(null); // { row, direction }
  const [clockAmount, setClockAmount] = useState("");

  const initialForm = {
    employee_id: "",
    role: roleOptions[0],
    shift_date: todayIso(),
    shift_start: "09:00",
    shift_end: "17:00",
    floor_id: "",
    section: "",
    sales_target: "",
  };
  const [formData, setFormData] = useState(initialForm);

  const floorName = (id) => floors.find((f) => String(f.id) === String(id))?.floor_name || "—";

  const employeeName = (row) =>
    row.employee_name ||
    (() => {
      const e = employees.find((x) => String(x.id) === String(row.employee_id));
      return e ? `${e.first_name || ""} ${e.last_name || ""}`.trim() : "—";
    })();

  /**
   * Section options come from the floors configured for this venue, not a
   * hardcoded list. `restaurant_floor.floor_type` and `restaurant_table.section`
   * share one vocabulary (Restaurant / Outdoor / Banquet); this field used to be
   * free text with a "Restaurant / Bar / Outdoor" placeholder, and the stored
   * data drifted to Bar, Hotel, Main Dining Hall and Outdoor Patio — only one
   * of five values matched anything.
   *
   * Any value already saved on a row is kept as an option so editing an old
   * record cannot silently rewrite its section.
   */
  const sectionOptions = useMemo(() => {
    if (!hasSection) return [];
    const canonical = [...new Set(floors.map((f) => f.floor_type).filter(Boolean))];
    const existing = [...new Set(shifts.map((s) => s.section).filter(Boolean))];
    const legacy = existing.filter((v) => !canonical.includes(v));
    return [
      ...canonical.map((v) => ({ value: v, label: v })),
      ...legacy.map((v) => ({ value: v, label: `${v} (legacy)` })),
    ];
  }, [hasSection, floors, shifts]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({
      employee_id: row.employee_id ?? "",
      role: row.role || roleOptions[0],
      shift_date: row.shift_date ?? todayIso(),
      shift_start: row.shift_start ?? "",
      shift_end: row.shift_end ?? "",
      floor_id: row.floor_id ?? "",
      section: row.section ?? "",
      sales_target: row.sales_target ?? "",
    });
    setEditId(row.id);
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setEditId(null);
    setFormData(initialForm);
  };

  const handleSave = async () => {
    if (saving) return;
    if (!formData.employee_id) {
      showToast("Employee is required", "error");
      return;
    }
    if (!formData.shift_date) {
      showToast("Shift date is required", "error");
      return;
    }
    if (!formData.shift_start) {
      showToast("Start time is required", "error");
      return;
    }
    const target = formData.sales_target === "" ? null : Number(formData.sales_target);
    if (target !== null && (Number.isNaN(target) || target < 0)) {
      showToast("Sales target must be zero or more", "error");
      return;
    }

    setSaving(true);
    try {
      // PUT accepts only the mutable subset — employee and date are fixed once
      // scheduled, which is why both are disabled in edit mode.
      const common = {
        role: formData.role,
        shift_start: formData.shift_start,
        shift_end: formData.shift_end || null,
        floor_id: formData.floor_id ? Number(formData.floor_id) : null,
        sales_target: target,
        ...(hasSection ? { section: formData.section || null } : {}),
      };

      if (editId) {
        await api.updateShift(editId, common);
        showToast("Shift updated", "update");
      } else {
        const employee = employees.find((e) => String(e.id) === String(formData.employee_id));
        await api.createShift({
          employee_id: Number(formData.employee_id),
          employee_name: employee
            ? `${employee.first_name || ""} ${employee.last_name || ""}`.trim()
            : null,
          shift_date: formData.shift_date,
          ...common,
        });
        showToast("Shift scheduled", "success");
      }
      reload();
      closeModal();
    } catch (err) {
      showToast(err?.message || "Failed to save shift", "error");
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    const id = deleteId;
    setDeleteId(null);
    try {
      await api.cancelShift(id);
      showToast("Shift cancelled", "delete");
      reload();
    } catch (err) {
      showToast(err?.message || "Failed to cancel shift", "error");
    }
  };

  const submitClock = async () => {
    if (saving) return;
    setSaving(true);
    try {
      const amount = clockAmount === "" ? null : Number(clockAmount);
      if (clock.direction === "in") {
        await api.clockIn(clock.row.id, { opening_cash_float: amount });
        showToast("Clocked in", "success");
      } else {
        await api.clockOut(clock.row.id, { closing_cash_amount: amount });
        showToast("Clocked out", "success");
      }
      setClock(null);
      reload();
    } catch (err) {
      showToast(err?.message || "Failed to record clock time", "error");
    } finally {
      setSaving(false);
    }
  };

  /* ================= UI ================= */

  const columns = [
    {
      key: "shift_date",
      title: "Date",
      align: "left",
      type: "custom",
      exportValue: (row) => row.shift_date || "",
      render: (row) => <span className="nowrap">{formatDay(row.shift_date)}</span>,
    },
    {
      key: "employee_name",
      title: "Staff",
      align: "left",
      type: "custom",
      exportValue: employeeName,
      render: employeeName,
    },
    { key: "role", title: "Role", align: "left" },
    // Restaurant has both a floor and a section; Bar has only a floor. Showing
    // both for Restaurant made nine data columns, which pushed the Status badge
    // underneath the pinned Actions column at 1440px. Section is the finer of
    // the two, so it wins where it exists — and the View modal shows both.
    ...(hasSection
      ? [{ key: "section", title: "Section", align: "left" }]
      : [
          {
            key: "floor_id",
            title: "Floor",
            align: "left",
            type: "custom",
            exportValue: (row) => floorName(row.floor_id),
            render: (row) => floorName(row.floor_id),
          },
        ]),
    {
      // Start and End were separate columns. With date, staff, role, floor,
      // section, status and a four-button action cluster that was one column
      // too many at 1440px, and the Status badge rendered behind the pinned
      // Actions column.
      key: "shift_start",
      title: "Shift",
      align: "left",
      type: "custom",
      exportValue: (row) => `${formatTime(row.shift_start) || ""} - ${formatTime(row.shift_end) || ""}`,
      render: (row) => (
        <span className="nowrap">
          {formatTime(row.shift_start) || "—"} – {formatTime(row.shift_end) || "open"}
        </span>
      ),
    },
    { key: "shift_status", title: "Status", align: "center", type: "badge" },
    {
      key: "actions",
      title: "Actions",
      align: "center",
      type: "custom",
      excludeFromExport: true,
      render: (row) => (
        <RowActions
          label="shift"
          onView={() => setViewData(row)}
          onEdit={() => handleEdit(row)}
          onDelete={() => setDeleteId(row.id)}
        >
          {/* Clock in/out is a state transition on the row, not a CRUD verb, so
              it sits after the standard trio rather than replacing one. */}
          {!row.clock_in_at && (
            <IconButton
              variant="action-edit"
              size="action"
              icon={<LogIn size={16} />}
              onClick={() => {
                setClock({ row, direction: "in" });
                setClockAmount("");
              }}
              title="Clock in"
              ariaLabel={`Clock in ${employeeName(row)}`}
            />
          )}
          {row.clock_in_at && !row.clock_out_at && (
            <IconButton
              variant="action-edit"
              size="action"
              icon={<LogOut size={16} />}
              onClick={() => {
                setClock({ row, direction: "out" });
                setClockAmount("");
              }}
              title="Clock out"
              ariaLabel={`Clock out ${employeeName(row)}`}
            />
          )}
        </RowActions>
      ),
    },
  ];

  const clockingIn = clock?.direction === "in";

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title={`${venueLabel} Shift Planning`}
        loading={loading}
        emptyMessage={`No ${venueLabel.toLowerCase()} shifts scheduled yet.`}
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Shift",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={columns}
        data={shifts}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Shift Details"
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewData(null) }]}
      >
        <ViewSection title="Assignment">
          <DetailList columns={3}>
            <DetailItem label="Staff" value={viewData && employeeName(viewData)} />
            <DetailItem label="Role" value={viewData?.role} />
            <DetailItem label="Date" value={viewData && formatDay(viewData.shift_date)} />
            <DetailItem label="Floor" value={viewData && floorName(viewData.floor_id)} />
            {hasSection && <DetailItem label="Section" value={viewData?.section} />}
            <DetailItem
              label="Scheduled"
              value={viewData && `${formatTime(viewData.shift_start)} – ${formatTime(viewData.shift_end) || "open"}`}
            />
          </DetailList>
        </ViewSection>

        <ViewSection title="Attendance">
          <DetailList columns={3}>
            <DetailItem label="Status" value={viewData?.shift_status} />
            <DetailItem
              label="Clocked In"
              value={viewData?.clock_in_at ? new Date(viewData.clock_in_at).toLocaleString() : null}
            />
            <DetailItem
              label="Clocked Out"
              value={viewData?.clock_out_at ? new Date(viewData.clock_out_at).toLocaleString() : null}
            />
          </DetailList>
        </ViewSection>

        <ViewSection title="Cash & Sales">
          <DetailList columns={3}>
            <DetailItem label="Sales Target" value={viewData?.sales_target} />
            <DetailItem label="Actual Sales" value={viewData?.actual_sales} />
            <DetailItem label="Opening Float" value={viewData?.opening_cash_float} />
            <DetailItem label="Closing Cash" value={viewData?.closing_cash_amount} />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Shift" : "Add Shift"}
        onClose={closeModal}
        showFooter
        size="large"
        bodyLayout="grid"
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
        <Select
          label="Employee"
          required
          name="employee_id"
          value={formData.employee_id}
          onChange={handleChange}
          placeholder="Select employee"
          // The update endpoint does not accept employee_id or shift_date;
          // changing either means cancelling and re-scheduling.
          disabled={!!editId || saving}
          options={employees.map((e) => ({
            value: e.id,
            label: `${e.first_name || ""} ${e.last_name || ""}`.trim() || e.username,
          }))}
        />
        <Input
          label="Shift Date"
          required
          type="date"
          name="shift_date"
          value={formData.shift_date}
          onChange={handleChange}
          disabled={!!editId || saving}
        />
        <Select
          label="Role"
          required
          name="role"
          value={formData.role}
          onChange={handleChange}
          disabled={saving}
          options={roleOptions.map((r) => ({ value: r, label: r }))}
        />
        <Input
          label="Start Time"
          required
          type="time"
          name="shift_start"
          value={formData.shift_start}
          onChange={handleChange}
          disabled={saving}
        />
        <Input
          label="End Time"
          type="time"
          name="shift_end"
          value={formData.shift_end}
          onChange={handleChange}
          disabled={saving}
        />
        <Select
          label="Floor"
          name="floor_id"
          value={formData.floor_id}
          onChange={handleChange}
          placeholder="Select floor"
          disabled={saving}
          options={floors.map((f) => ({ value: f.id, label: f.floor_name }))}
        />
        {hasSection && (
          <Select
            label="Section"
            name="section"
            value={formData.section}
            onChange={handleChange}
            placeholder="Select section"
            disabled={saving}
            options={sectionOptions}
          />
        )}
        <Input
          label="Sales Target"
          type="number"
          inputMode="decimal"
          min="0"
          step="0.01"
          name="sales_target"
          placeholder="0.00"
          value={formData.sales_target}
          onChange={handleChange}
          disabled={saving}
        />
      </Modal>

      {/* ================= CLOCK IN / OUT ================= */}
      <Modal
        isOpen={!!clock}
        title={clockingIn ? "Clock In" : "Clock Out"}
        onClose={() => !saving && setClock(null)}
        showFooter
        size="small"
        bodyLayout="single"
        actions={[
          {
            label: "Cancel",
            variant: "secondary",
            onClick: () => setClock(null),
            disabled: saving,
          },
          {
            label: saving ? "Saving…" : "Confirm",
            variant: "primary",
            onClick: submitClock,
            disabled: saving,
          },
        ]}
      >
        <DetailList columns={1}>
          <DetailItem label="Staff" value={clock && employeeName(clock.row)} />
        </DetailList>
        <Input
          label={clockingIn ? "Opening Cash Float" : "Closing Cash Amount"}
          type="number"
          inputMode="decimal"
          min="0"
          step="0.01"
          placeholder="0.00"
          value={clockAmount}
          onChange={(e) => setClockAmount(e.target.value)}
          disabled={saving}
          helperText="Optional."
        />
      </Modal>

      {/* ================= CANCEL SHIFT ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Cancel Shift"
        confirmText="Cancel Shift"
        cancelText="Keep Shift"
        size="small"
        destructive
      >
        Are you sure you want to cancel this shift? It will be removed from the
        roster. Recorded clock-in and clock-out times are kept.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default StaffShiftPlanning;

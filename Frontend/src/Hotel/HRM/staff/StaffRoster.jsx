import React, { useState } from "react";
import TableTemplate from "../../../stories/TableTemplate";
import Modal from "../../../stories/Modal";
import Input from "../../../stories/Form/Input";
import Select from "../../../stories/Form/Select";
import RowActions from "../../../stories/RowActions";
import DetailList, { DetailItem } from "../../../stories/DetailList";
import ErrorAlert from "../../../stories/ErrorAlert";
import Toast from "../../../stories/Toast";
import { useApiResources } from "../../../hooks/useApiResource";
import { useToast } from "../../../hooks/useToast";

/**
 * Today's floor roster, shared by the Restaurant and Bar screens.
 *
 * Cross-references the HRM employee directory with today's shift assignments
 * for the venue, so an unscheduled employee still appears (as Not Scheduled)
 * rather than vanishing from the roster.
 *
 * API literals live in the per-venue wrapper — see the note in
 * StaffShiftPlanning.jsx for why.
 */
const todayIso = () => new Date().toISOString().slice(0, 10);

const StaffRoster = ({ venueLabel, roleOptions, hasSection = false, api }) => {
  const {
    data: [employees, shifts, floors],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: api.listEmployees, select: api.readList, fallback: "Failed to load the staff directory." },
    { fetch: api.listShifts, select: api.readList },
    { fetch: api.listFloors, select: api.readList },
  ]);

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [viewRow, setViewRow] = useState(null);

  const initialForm = {
    employee_id: "",
    role: roleOptions[0],
    shift_start: "09:00",
    shift_end: "17:00",
    floor_id: "",
    section: "",
  };
  const [formData, setFormData] = useState(initialForm);

  const floorName = (id) => floors.find((f) => String(f.id) === String(id))?.floor_name || null;

  // Canonical section vocabulary, derived from the venue's configured floors
  // rather than hardcoded. See StaffShiftPlanning for the full rationale.
  const sectionOptions = hasSection
    ? [...new Set(floors.map((f) => f.floor_type).filter(Boolean))].map((v) => ({
        value: v,
        label: v,
      }))
    : [];

  const rows = employees.map((e) => {
    const shift = shifts.find((s) => String(s.employee_id) === String(e.id));
    return {
      id: e.id,
      user_code: e.user_code,
      name: `${e.first_name || ""} ${e.last_name || ""}`.trim() || e.username,
      phone: e.mobile,
      role: shift?.role || null,
      floor: shift ? floorName(shift.floor_id) : null,
      section: shift?.section || null,
      shift_time: shift
        ? `${String(shift.shift_start).slice(0, 5)} – ${shift.shift_end ? String(shift.shift_end).slice(0, 5) : "open"}`
        : null,
      shift_status: shift?.shift_status || "Not Scheduled",
      scheduled: Boolean(shift),
    };
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const openAssign = (row) => {
    setFormData({ ...initialForm, employee_id: row ? row.id : "" });
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setFormData(initialForm);
  };

  const saveAssignment = async () => {
    if (saving) return;
    if (!formData.employee_id) {
      showToast("Employee is required", "error");
      return;
    }
    if (!formData.shift_start) {
      showToast("Start time is required", "error");
      return;
    }

    setSaving(true);
    try {
      const employee = employees.find((e) => String(e.id) === String(formData.employee_id));
      await api.createShift({
        employee_id: Number(formData.employee_id),
        employee_name: employee
          ? `${employee.first_name || ""} ${employee.last_name || ""}`.trim()
          : null,
        role: formData.role,
        shift_date: todayIso(),
        shift_start: formData.shift_start,
        shift_end: formData.shift_end || null,
        floor_id: formData.floor_id ? Number(formData.floor_id) : null,
        ...(hasSection ? { section: formData.section || null } : {}),
      });
      showToast("Staff assigned for today", "success");
      reload();
      closeModal();
    } catch (err) {
      showToast(err?.message || "Failed to assign staff", "error");
    } finally {
      setSaving(false);
    }
  };

  const dash = (v) => v || "—";

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title={`${venueLabel} Roster — Today`}
        loading={loading}
        emptyMessage="No employees in the directory yet."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Assign Staff",
          onClick: () => openAssign(null),
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "user_code", title: "Employee ID", align: "left" },
          { key: "name", title: "Staff Name", align: "left" },
          {
            key: "phone",
            title: "Contact",
            align: "left",
            type: "custom",
            exportValue: (r) => r.phone || "",
            render: (r) => dash(r.phone),
          },
          {
            key: "role",
            title: "Role",
            align: "left",
            type: "custom",
            exportValue: (r) => r.role || "",
            render: (r) => dash(r.role),
          },
          {
            key: "floor",
            title: "Floor",
            align: "left",
            type: "custom",
            exportValue: (r) => r.floor || "",
            render: (r) => dash(r.floor),
          },
          {
            key: "shift_time",
            title: "Shift",
            align: "left",
            type: "custom",
            exportValue: (r) => r.shift_time || "",
            render: (r) => dash(r.shift_time),
          },
          { key: "shift_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions label="roster entry" onView={() => setViewRow(row)} />
            ),
          },
        ]}
        data={rows}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewRow}
        title={viewRow ? viewRow.name : "Roster Entry"}
        onClose={() => setViewRow(null)}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewRow(null) }]}
      >
        <DetailList columns={2}>
          <DetailItem label="Employee ID" value={viewRow?.user_code} />
          <DetailItem label="Staff Name" value={viewRow?.name} />
          <DetailItem label="Contact" value={viewRow?.phone} />
          <DetailItem label="Status" value={viewRow?.shift_status} />
          <DetailItem label="Role" value={viewRow?.role} />
          <DetailItem label="Floor" value={viewRow?.floor} />
          {hasSection && <DetailItem label="Section" value={viewRow?.section} />}
          <DetailItem label="Shift" value={viewRow?.shift_time} />
        </DetailList>
      </Modal>

      {/* ================= ASSIGN ================= */}
      <Modal
        isOpen={showModal}
        title="Assign Staff for Today"
        onClose={closeModal}
        showFooter
        size="large"
        bodyLayout="grid"
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Assign",
            variant: "primary",
            onClick: saveAssignment,
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
          disabled={saving}
          options={employees.map((e) => ({
            value: e.id,
            label: `${e.first_name || ""} ${e.last_name || ""}`.trim() || e.username,
          }))}
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
      </Modal>

      <Toast {...toast} />
    </>
  );
};

export default StaffRoster;

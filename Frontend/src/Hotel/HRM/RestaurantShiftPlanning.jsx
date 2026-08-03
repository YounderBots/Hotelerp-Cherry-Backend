import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Pencil, LogIn, LogOut } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);
const todayIso = () => new Date().toISOString().slice(0, 10);

// Restaurant shift scheduling + clock in/out — lives under HRM (not
// Restaurant) since staffing is an HR concern; the restaurant module only
// contributes the day-to-day shift/section/cash-float data via
// /restaurant/staff_assignment.
const RestaurantShiftPlanning = () => {
  const [shifts, setShifts] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showShiftModal, setShowShiftModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showClockModal, setShowClockModal] = useState(null); // "in" | "out" | null
  const [editId, setEditId] = useState(null);
  const [selectedShift, setSelectedShift] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);
  const [clockAmount, setClockAmount] = useState("");

  const initialForm = { employee_id: "", role: "Waiter", shift_date: todayIso(), shift_start: "09:00", shift_end: "17:00", section: "" };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/restaurant/staff_assignment"), APICall.getT("/user/users")]).then(([sRes, eRes]) => {
      setShifts(sRes.status === "fulfilled" ? readList(sRes.value) : []);
      setEmployees(eRes.status === "fulfilled" ? readList(eRes.value) : []);
      if (sRes.status === "rejected") setError(errMsg(sRes.reason, "Failed to load shifts."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowShiftModal(true);
  };
  const openEditModal = (row) => {
    setEditId(row.id);
    setFormError(null);
    setFormData({
      employee_id: row.employee_id,
      role: row.role,
      shift_date: row.shift_date,
      shift_start: row.shift_start,
      shift_end: row.shift_end || "",
      section: row.section || "",
    });
    setShowShiftModal(true);
  };
  const closeShiftModal = () => {
    if (saving) return;
    setShowShiftModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const saveShift = async () => {
    if (!formData.employee_id || !formData.shift_date || !formData.shift_start) {
      setFormError("Employee, date and start time are required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      if (editId) {
        await APICall.putT(`/restaurant/staff_assignment/${editId}`, {
          role: formData.role,
          shift_start: formData.shift_start,
          shift_end: formData.shift_end || null,
          section: formData.section || null,
        });
      } else {
        const employee = employees.find((e) => String(e.id) === String(formData.employee_id));
        await APICall.postT("/restaurant/staff_assignment", {
          employee_id: Number(formData.employee_id),
          employee_name: employee ? `${employee.first_name || ""} ${employee.last_name || ""}`.trim() : null,
          role: formData.role,
          shift_date: formData.shift_date,
          shift_start: formData.shift_start,
          shift_end: formData.shift_end || null,
          section: formData.section || null,
        });
      }
      setShowShiftModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save shift."));
    } finally {
      setSaving(false);
    }
  };

  const openViewModal = (row) => {
    setSelectedShift(row);
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setSelectedShift(null);
    setShowViewModal(false);
  };

  const openClockModal = (row, direction) => {
    setSelectedShift(row);
    setClockAmount("");
    setFormError(null);
    setShowClockModal(direction);
  };
  const closeClockModal = () => {
    if (saving) return;
    setShowClockModal(null);
    setSelectedShift(null);
  };

  const submitClock = async () => {
    setSaving(true);
    setFormError(null);
    try {
      if (showClockModal === "in") {
        await APICall.postT(`/restaurant/staff_assignment/${selectedShift.id}/clock_in`, {
          opening_cash_float: clockAmount ? Number(clockAmount) : null,
        });
      } else {
        await APICall.postT(`/restaurant/staff_assignment/${selectedShift.id}/clock_out`, {
          closing_cash_amount: clockAmount ? Number(clockAmount) : null,
        });
      }
      setShowClockModal(null);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to record clock time."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Restaurant Shift Planning"
        hasActionButton
        searchable
        pagination
        loading={loading}
        actionButton={{ label: "Add Shift", variant: "primary", onClick: openAddModal }}
        columns={[
          { key: "shift_date", title: "Shift Date" },
          { key: "employee_name", title: "Staff Name" },
          { key: "role", title: "Role" },
          { key: "section", title: "Section" },
          { key: "shift_start", title: "Start Time" },
          { key: "shift_end", title: "End Time" },
          { key: "shift_status", title: "Shift Status", type: "badge", align: "center" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} onClick={() => openViewModal(row)} ariaLabel="View" />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} onClick={() => openEditModal(row)} ariaLabel="Edit" />
                {!row.clock_in_at && (
                  <IconButton variant="subtle" size="small" icon={<LogIn size={16} />} onClick={() => openClockModal(row, "in")} ariaLabel="Clock In" />
                )}
                {row.clock_in_at && !row.clock_out_at && (
                  <IconButton variant="subtle" size="small" icon={<LogOut size={16} />} onClick={() => openClockModal(row, "out")} ariaLabel="Clock Out" />
                )}
              </div>
            ),
          },
        ]}
        data={shifts}
      />

      {showShiftModal && (
        <Modal
          isOpen={showShiftModal}
          title={editId ? "Edit Shift" : "Add Shift"}
          onClose={closeShiftModal}
          showFooter
          size="xlarge"
          bodyLayout="grid"
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeShiftModal, disabled: saving },
            { label: saving ? "Saving…" : "Save Shift", variant: "primary", onClick: saveShift, disabled: saving },
          ]}
        >
          <div style={{ gridColumn: "1 / -1" }}>
            <ErrorAlert message={formError} />
          </div>

          <Select
            label="Employee"
            name="employee_id"
            value={formData.employee_id}
            onChange={handleChange}
            placeholder="— select —"
            disabled={!!editId}
            options={employees.map((e) => ({ value: e.id, label: `${e.first_name} ${e.last_name}` }))}
          />

          <Input label="Shift Date" type="date" name="shift_date" value={formData.shift_date} onChange={handleChange} disabled={!!editId} />

          <Input label="Start Time" type="time" name="shift_start" value={formData.shift_start} onChange={handleChange} />

          <Input label="End Time" type="time" name="shift_end" value={formData.shift_end} onChange={handleChange} />

          <Select
            label="Role"
            name="role"
            value={formData.role}
            onChange={handleChange}
            options={[
              { value: "Waiter", label: "Waiter" },
              { value: "Chef", label: "Chef" },
              { value: "Cashier", label: "Cashier" },
              { value: "Manager", label: "Manager" },
            ]}
          />

          <Input label="Section" name="section" value={formData.section} onChange={handleChange} />
        </Modal>
      )}

      {showClockModal && selectedShift && (
        <Modal
          isOpen={!!showClockModal}
          title={`${showClockModal === "in" ? "Clock In" : "Clock Out"} — ${selectedShift.employee_name}`}
          onClose={closeClockModal}
          showFooter
          size="small"
          bodyLayout="single"
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeClockModal, disabled: saving },
            { label: saving ? "Saving…" : "Confirm", variant: "primary", onClick: submitClock, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />
          <Input
            label={showClockModal === "in" ? "Opening Cash Float" : "Closing Cash Amount"}
            type="number"
            value={clockAmount}
            onChange={(e) => setClockAmount(e.target.value)}
          />
        </Modal>
      )}

      {showViewModal && selectedShift && (
        <Modal
          isOpen={showViewModal}
          title="Shift Details"
          onClose={closeViewModal}
          showFooter
          size="medium"
          bodyLayout="single"
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          <p>
            <strong>Staff:</strong> {selectedShift.employee_name}
          </p>
          <p>
            <strong>Date:</strong> {selectedShift.shift_date}
          </p>
          <p>
            <strong>Role:</strong> {selectedShift.role}
          </p>
          <p>
            <strong>Time:</strong> {selectedShift.shift_start} – {selectedShift.shift_end || "-"}
          </p>
          <p>
            <strong>Status:</strong> {selectedShift.shift_status}
          </p>
          <p>
            <strong>Clock In:</strong> {selectedShift.clock_in_at ? new Date(selectedShift.clock_in_at).toLocaleTimeString() : "-"}
          </p>
          <p>
            <strong>Clock Out:</strong> {selectedShift.clock_out_at ? new Date(selectedShift.clock_out_at).toLocaleTimeString() : "-"}
          </p>
          <p>
            <strong>Opening Float:</strong> {selectedShift.opening_cash_float ?? "-"}
          </p>
          <p>
            <strong>Closing Cash:</strong> {selectedShift.closing_cash_amount ?? "-"}
          </p>
        </Modal>
      )}
    </>
  );
};

export default RestaurantShiftPlanning;

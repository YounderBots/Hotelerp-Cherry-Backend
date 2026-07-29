import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, LogIn, LogOut, X } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);
const todayIso = () => new Date().toISOString().slice(0, 10);

const StaffPlanning = () => {
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
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Shift Planning"
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
                <button className="table-action-btn view" onClick={() => openViewModal(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => openEditModal(row)}>
                  <Pencil size={16} />
                </button>
                {!row.clock_in_at && (
                  <button className="table-action-btn" title="Clock In" onClick={() => openClockModal(row, "in")}>
                    <LogIn size={16} />
                  </button>
                )}
                {row.clock_in_at && !row.clock_out_at && (
                  <button className="table-action-btn" title="Clock Out" onClick={() => openClockModal(row, "out")}>
                    <LogOut size={16} />
                  </button>
                )}
              </div>
            ),
          },
        ]}
        data={shifts}
      />

      {showShiftModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>{editId ? "Edit Shift" : "Add Shift"}</h3>
              <button onClick={closeShiftModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
              <div className="grid-4">
                <div className="form-group">
                  <label>Employee</label>
                  <select name="employee_id" value={formData.employee_id} onChange={handleChange} disabled={!!editId}>
                    <option value="">— select —</option>
                    {employees.map((e) => (
                      <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Shift Date</label>
                  <input type="date" name="shift_date" value={formData.shift_date} onChange={handleChange} disabled={!!editId} />
                </div>

                <div className="form-group">
                  <label>Start Time</label>
                  <input type="time" name="shift_start" value={formData.shift_start} onChange={handleChange} />
                </div>

                <div className="form-group">
                  <label>End Time</label>
                  <input type="time" name="shift_end" value={formData.shift_end} onChange={handleChange} />
                </div>

                <div className="form-group">
                  <label>Role</label>
                  <select name="role" value={formData.role} onChange={handleChange}>
                    <option>Waiter</option>
                    <option>Bartender</option>
                    <option>Chef</option>
                    <option>Cashier</option>
                    <option>Manager</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Section</label>
                  <input name="section" value={formData.section} onChange={handleChange} />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeShiftModal} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={saveShift} disabled={saving}>{saving ? "Saving…" : "Save Shift"}</button>
            </div>
          </div>
        </div>
      )}

      {showClockModal && selectedShift && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "480px", width: "95%" }}>
            <div className="modal-header">
              <h3>{showClockModal === "in" ? "Clock In" : "Clock Out"} — {selectedShift.employee_name}</h3>
              <button onClick={closeClockModal}><X size={18} /></button>
            </div>
            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}
            <div className="modal-body single">
              <div className="form-group">
                <label>{showClockModal === "in" ? "Opening Cash Float" : "Closing Cash Amount"}</label>
                <input type="number" value={clockAmount} onChange={(e) => setClockAmount(e.target.value)} />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeClockModal} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={submitClock} disabled={saving}>{saving ? "Saving…" : "Confirm"}</button>
            </div>
          </div>
        </div>
      )}

      {showViewModal && selectedShift && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "500px", width: "95%" }}>
            <div className="modal-header">
              <h3>Shift Details</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>
            <div className="modal-body single">
              <p><strong>Staff:</strong> {selectedShift.employee_name}</p>
              <p><strong>Date:</strong> {selectedShift.shift_date}</p>
              <p><strong>Role:</strong> {selectedShift.role}</p>
              <p><strong>Time:</strong> {selectedShift.shift_start} – {selectedShift.shift_end || "-"}</p>
              <p><strong>Status:</strong> {selectedShift.shift_status}</p>
              <p><strong>Clock In:</strong> {selectedShift.clock_in_at ? new Date(selectedShift.clock_in_at).toLocaleTimeString() : "-"}</p>
              <p><strong>Clock Out:</strong> {selectedShift.clock_out_at ? new Date(selectedShift.clock_out_at).toLocaleTimeString() : "-"}</p>
              <p><strong>Opening Float:</strong> {selectedShift.opening_cash_float ?? "-"}</p>
              <p><strong>Closing Cash:</strong> {selectedShift.closing_cash_amount ?? "-"}</p>
            </div>
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default StaffPlanning;

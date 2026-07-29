import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, X } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);
const todayIso = () => new Date().toISOString().slice(0, 10);

const StaffMaster = () => {
  const [employees, setEmployees] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showStaffModal, setShowStaffModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedRow, setSelectedRow] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = { employee_id: "", role: "Waiter", shift_date: todayIso(), shift_start: "09:00", section: "" };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/user/users"), APICall.getT("/restaurant/staff_assignment", { shift_date: todayIso() })]).then(([eRes, sRes]) => {
      setEmployees(eRes.status === "fulfilled" ? readList(eRes.value) : []);
      setShifts(sRes.status === "fulfilled" ? readList(sRes.value) : []);
      if (eRes.status === "rejected") setError(errMsg(eRes.reason, "Failed to load staff directory."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const shiftFor = (employeeId) => shifts.find((s) => s.employee_id === employeeId);

  const rows = employees.map((e) => {
    const shift = shiftFor(e.id);
    return {
      id: e.id,
      name: `${e.first_name || ""} ${e.last_name || ""}`.trim(),
      phone: e.mobile,
      role: shift?.role || "—",
      section: shift?.section || "—",
      shift_status: shift?.shift_status || "Not Scheduled",
      shift_id: shift?.id,
    };
  });

  const openAddModal = () => {
    setFormData(initialForm);
    setFormError(null);
    setShowStaffModal(true);
  };
  const closeAddModal = () => {
    if (saving) return;
    setShowStaffModal(false);
  };

  const openViewModal = (row) => {
    setSelectedRow(row);
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setSelectedRow(null);
    setShowViewModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const saveStaff = async () => {
    if (!formData.employee_id) {
      setFormError("Select an employee.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      const employee = employees.find((e) => String(e.id) === String(formData.employee_id));
      await APICall.postT("/restaurant/staff_assignment", {
        employee_id: Number(formData.employee_id),
        employee_name: employee ? `${employee.first_name || ""} ${employee.last_name || ""}`.trim() : null,
        role: formData.role,
        shift_date: formData.shift_date,
        shift_start: formData.shift_start,
        section: formData.section || null,
      });
      setShowStaffModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save staff assignment."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Staff List (Today's Roster)"
        searchable
        pagination
        loading={loading}
        actionButton={{ label: "Assign Staff Today", variant: "primary", onClick: openAddModal }}
        columns={[
          { key: "id", title: "Employee ID" },
          { key: "name", title: "Staff Name" },
          { key: "phone", title: "Contact No" },
          { key: "role", title: "Role" },
          { key: "section", title: "Section" },
          { key: "shift_status", title: "Status", type: "badge", align: "center" },
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
              </div>
            ),
          },
        ]}
        data={rows}
      />

      {showStaffModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>Assign Staff for Today</h3>
              <button onClick={closeAddModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
              <div className="grid-3">
                <div className="form-group">
                  <label>Employee</label>
                  <select name="employee_id" value={formData.employee_id} onChange={handleChange}>
                    <option value="">— select —</option>
                    {employees.map((e) => (
                      <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>
                    ))}
                  </select>
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
                  <input name="section" value={formData.section} onChange={handleChange} placeholder="Restaurant / Bar / Outdoor" />
                </div>

                <div className="form-group">
                  <label>Shift Date</label>
                  <input type="date" name="shift_date" value={formData.shift_date} onChange={handleChange} />
                </div>

                <div className="form-group">
                  <label>Shift Start</label>
                  <input type="time" name="shift_start" value={formData.shift_start} onChange={handleChange} />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeAddModal} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={saveStaff} disabled={saving}>{saving ? "Saving…" : "Save Staff"}</button>
            </div>
          </div>
        </div>
      )}

      {showViewModal && selectedRow && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "500px", width: "95%" }}>
            <div className="modal-header">
              <h3>Staff Details</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>
            <div className="modal-body single">
              <p><strong>Name:</strong> {selectedRow.name}</p>
              <p><strong>Contact:</strong> {selectedRow.phone}</p>
              <p><strong>Role:</strong> {selectedRow.role}</p>
              <p><strong>Section:</strong> {selectedRow.section}</p>
              <p><strong>Status:</strong> {selectedRow.shift_status}</p>
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

export default StaffMaster;

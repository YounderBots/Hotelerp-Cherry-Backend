import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";
const todayIso = () => new Date().toISOString().slice(0, 10);

// Today's restaurant floor roster — cross-references the shared HRM employee
// directory (/user/users) with today's restaurant shift assignments. Lives
// under HRM (not Restaurant) since staffing is an HR concern; the restaurant
// module only contributes the day-to-day shift/section data.
const RestaurantRoster = () => {
  const {
    data: [employees, shifts],
    loading,
    error,
    reload: load,
  } = useApiResources([
    { fetch: () => APICall.getT("/user/users"), select: readList,
      fallback: "Failed to load staff directory." },
    { fetch: () => APICall.getT("/restaurant/staff_assignment", { shift_date: todayIso() }), select: readList },
  ]);

  const [showStaffModal, setShowStaffModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedRow, setSelectedRow] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = { employee_id: "", role: "Waiter", shift_date: todayIso(), shift_start: "09:00", section: "" };
  const [formData, setFormData] = useState(initialForm);

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
      <ErrorAlert message={error} />

      <TableTemplate
        title="Restaurant Roster (Today)"
        hasActionButton
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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} onClick={() => openViewModal(row)} ariaLabel="View" />
              </div>
            ),
          },
        ]}
        data={rows}
      />

      {showStaffModal && (
        <Modal
          isOpen={showStaffModal}
          title="Assign Staff for Today"
          onClose={closeAddModal}
          showFooter
          size="xlarge"
          bodyLayout="grid"
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeAddModal, disabled: saving },
            { label: saving ? "Saving…" : "Save Staff", variant: "primary", onClick: saveStaff, disabled: saving },
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
            options={employees.map((e) => ({ value: e.id, label: `${e.first_name} ${e.last_name}` }))}
          />

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

          <Input label="Section" name="section" value={formData.section} onChange={handleChange} placeholder="Restaurant / Bar / Outdoor" />

          <Input label="Shift Date" type="date" name="shift_date" value={formData.shift_date} onChange={handleChange} />

          <Input label="Shift Start" type="time" name="shift_start" value={formData.shift_start} onChange={handleChange} />
        </Modal>
      )}

      {showViewModal && selectedRow && (
        <Modal
          isOpen={showViewModal}
          title="Staff Details"
          onClose={closeViewModal}
          showFooter
          size="medium"
          bodyLayout="single"
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          <p>
            <strong>Name:</strong> {selectedRow.name}
          </p>
          <p>
            <strong>Contact:</strong> {selectedRow.phone}
          </p>
          <p>
            <strong>Role:</strong> {selectedRow.role}
          </p>
          <p>
            <strong>Section:</strong> {selectedRow.section}
          </p>
          <p>
            <strong>Status:</strong> {selectedRow.shift_status}
          </p>
        </Modal>
      )}
    </>
  );
};

export default RestaurantRoster;

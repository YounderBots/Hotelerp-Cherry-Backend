import React, { useMemo, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import Checkbox from "../../stories/Form/Checkbox";
import ImagePicker from "../../stories/Form/ImagePicker";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";

// Gender and marital status have no master-data table in this system, and
// they are not business reference data an operator maintains — they stay
// in-code. Contrast with country below, which does have a canonical source.
const GENDERS = ["Male", "Female", "Other", "Prefer not to say"];
const MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed", "Prefer not to say"];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+()\-\s\d]{7,20}$/;
const MAX_PHOTO_MB = 3;

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

const initialForm = {
  username: "",
  first_name: "",
  last_name: "",
  personal_email: "",
  company_email: "",
  password: "",
  mobile: "",
  alternative_mobile: "",
  dob: "",
  gender: "",
  marital_status: "",
  address: "",
  city: "",
  state: "",
  postal_code: "",
  country: "",
  department_id: "",
  designation_id: "",
  role_id: "",
  shift_id: "",
  date_of_joining: "",
  experience: "",
  salary_details: "",
  register_code: "",
  emergency_name: "",
  emergency_contact: "",
  emergency_relationship: "",
  acknowledgment_of_hotel_policies: false,
  photo: null,
};

// Every one of these is `Form(...)` on POST /user/users and NOT NULL in the
// users table. The old form validated only 7 of them and appended "" for the
// rest, and an empty string satisfies `str = Form(...)` — so employees were
// being created with a blank department, role and shift, which is what made
// them show up unassigned on the roster screens.
const REQUIRED_ON_CREATE = [
  ["username", "Username"],
  ["first_name", "First name"],
  ["last_name", "Last name"],
  ["personal_email", "Personal email"],
  ["company_email", "Company email"],
  ["mobile", "Mobile"],
  ["dob", "Date of birth"],
  ["gender", "Gender"],
  ["marital_status", "Marital status"],
  ["address", "Address"],
  ["city", "City"],
  ["state", "State"],
  ["postal_code", "Postal code"],
  ["country", "Country"],
  ["department_id", "Department"],
  ["designation_id", "Designation"],
  ["role_id", "Role"],
  ["shift_id", "Shift"],
  ["date_of_joining", "Date of joining"],
  ["experience", "Experience"],
  ["salary_details", "Salary details"],
  ["register_code", "Register code"],
  ["emergency_name", "Emergency contact name"],
  ["emergency_contact", "Emergency contact number"],
  ["emergency_relationship", "Emergency contact relationship"],
];

const Employee = () => {
  const {
    data: [employees, departments, designations, roles, shifts, countries],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT("/user/users"), select: readList, fallback: "Failed to load employees." },
    { fetch: () => APICall.getT("/user/departments"), select: readList },
    { fetch: () => APICall.getT("/user/designations"), select: readList },
    { fetch: () => APICall.getT("/user/roles"), select: readList },
    { fetch: () => APICall.getT("/user/shifts"), select: readList },
    // Country is a canonical master-data list, not free text — same source the
    // Tax and Discount screens use.
    { fetch: () => APICall.getT("/masterdata/country_currency"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteRow, setDeleteRow] = useState(null);
  const [formData, setFormData] = useState(initialForm);

  const lookup = (list, idKey, nameKey) => {
    const map = new Map(list.map((x) => [String(x[idKey]), x[nameKey]]));
    return (id) => map.get(String(id)) || null;
  };

  const departmentName = useMemo(() => lookup(departments, "id", "department_name"), [departments]);
  const designationName = useMemo(() => lookup(designations, "id", "designation_name"), [designations]);
  const roleName = useMemo(() => lookup(roles, "id", "role_name"), [roles]);
  const shiftName = useMemo(() => lookup(shifts, "id", "shift_name"), [shifts]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  /* ================= API ================= */

  const buildCreateForm = () => {
    const fd = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (key === "photo") {
        if (value instanceof File) fd.append("photo", value);
        return;
      }
      if (key === "acknowledgment_of_hotel_policies") {
        fd.append(key, value ? "true" : "false");
        return;
      }
      if (key === "company_email" || key === "personal_email") {
        fd.append(key, String(value || "").trim().toLowerCase());
        return;
      }
      fd.append(key, typeof value === "string" ? value.trim() : value ?? "");
    });
    return fd;
  };

  const buildUpdatePayload = () => {
    // PUT /user/users takes JSON and does not accept a photo — see the note on
    // the photo field in the form below.
    const { photo, password, ...rest } = formData;
    const payload = { ...rest, id: editId };
    payload.company_email = String(payload.company_email || "").trim().toLowerCase();
    payload.personal_email = String(payload.personal_email || "").trim().toLowerCase();
    // Only send a password when one was actually typed, or the backend would
    // re-hash an empty string and lock the employee out.
    if (password) payload.password = password;
    return payload;
  };

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleEdit = (row) => {
    setFormData({
      ...initialForm,
      username: row.username ?? "",
      first_name: row.first_name ?? "",
      last_name: row.last_name ?? "",
      personal_email: row.personal_email ?? "",
      company_email: row.company_email ?? "",
      password: "",
      mobile: row.mobile ?? "",
      alternative_mobile: row.alternative_mobile ?? "",
      dob: isoDay(row.dob),
      gender: row.gender ?? "",
      marital_status: row.marital_status ?? "",
      address: row.address ?? "",
      city: row.city ?? "",
      state: row.state ?? "",
      postal_code: row.postal_code ?? "",
      country: row.country ?? "",
      department_id: row.department_id ?? "",
      designation_id: row.designation_id ?? "",
      role_id: row.role_id ?? "",
      shift_id: row.shift_id ?? "",
      date_of_joining: isoDay(row.date_of_joining),
      experience: row.experience ?? "",
      salary_details: row.salary_details ?? "",
      register_code: row.register_code ?? "",
      emergency_name: row.emergency_name ?? "",
      emergency_contact: row.emergency_contact ?? "",
      emergency_relationship: row.emergency_relationship ?? "",
      acknowledgment_of_hotel_policies: Boolean(row.acknowledgment_of_hotel_policies),
      photo: row.photo || null,
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

  const validate = () => {
    for (const [key, label] of REQUIRED_ON_CREATE) {
      if (!String(formData[key] ?? "").trim()) return `${label} is required`;
    }
    if (!EMAIL_RE.test(formData.company_email.trim())) return "Enter a valid company email";
    if (!EMAIL_RE.test(formData.personal_email.trim())) return "Enter a valid personal email";
    if (!PHONE_RE.test(formData.mobile.trim())) return "Enter a valid mobile number";
    if (formData.alternative_mobile && !PHONE_RE.test(formData.alternative_mobile.trim())) {
      return "Alternative mobile is not a valid number";
    }
    if (!PHONE_RE.test(formData.emergency_contact.trim())) {
      return "Enter a valid emergency contact number";
    }
    if (!editId && !formData.password) return "Password is required for a new employee";
    if (formData.password && formData.password.length < 6) {
      return "Password must be at least 6 characters";
    }
    if (isoDay(formData.dob) > isoDay(new Date().toISOString())) {
      return "Date of birth cannot be in the future";
    }
    if (isoDay(formData.date_of_joining) < isoDay(formData.dob)) {
      return "Date of joining cannot precede date of birth";
    }
    return null;
  };

  const handleSave = async () => {
    if (saving) return;
    const problem = validate();
    if (problem) {
      showToast(problem, "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await APICall.putT("/user/users", buildUpdatePayload());
        showToast("Employee updated", "update");
      } else {
        await APICall.postT("/user/users", buildCreateForm());
        showToast("Employee added", "success");
      }
      reload();
      closeModal();
    } catch (err) {
      showToast(err?.message || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    try {
      await APICall.deleteT(`/user/users/${row.id}`);
      showToast("Employee deleted", "delete");
      reload();
    } catch (err) {
      showToast(err?.message || "Delete failed", "error");
    }
  };

  const fullName = (row) =>
    [row.first_name, row.last_name].filter(Boolean).join(" ") || row.username || "—";

  /* ================= UI ================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Employees"
        loading={loading}
        emptyMessage="No employees yet. Add the first one to get started."
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Employee",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "user_code", title: "Employee ID", align: "left" },
          {
            key: "first_name",
            title: "Name",
            align: "left",
            type: "custom",
            exportValue: fullName,
            render: fullName,
          },
          // Company email is long and, with department, designation and role,
          // pushed the table past 1440px — the Designation header clipped to
          // "DESIC" and Role disappeared behind the pinned Actions column.
          // It is shown in full in the View modal.
          { key: "mobile", title: "Mobile", align: "left" },
          {
            key: "department_id",
            title: "Department",
            align: "left",
            type: "custom",
            exportValue: (row) => departmentName(row.department_id) || "",
            render: (row) => departmentName(row.department_id) || "—",
          },
          {
            key: "designation_id",
            title: "Designation",
            align: "left",
            type: "custom",
            exportValue: (row) => designationName(row.designation_id) || "",
            render: (row) => designationName(row.designation_id) || "—",
          },
          {
            key: "role_id",
            title: "Role",
            align: "left",
            type: "custom",
            exportValue: (row) => roleName(row.role_id) || "",
            render: (row) => roleName(row.role_id) || "—",
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="employee"
                onView={() => setViewData(row)}
                onEdit={() => handleEdit(row)}
                onDelete={() => setDeleteRow(row)}
              />
            ),
          },
        ]}
        data={employees}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title={viewData ? fullName(viewData) : "Employee"}
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewData(null) }]}
      >
        <ViewSection title="Identity">
          <DetailList columns={3}>
            <DetailItem label="Employee ID" value={viewData?.user_code} />
            <DetailItem label="Username" value={viewData?.username} />
            <DetailItem label="Full Name" value={viewData && fullName(viewData)} />
          </DetailList>
          {viewData?.photo && (
            <div className="image-picker-slot--single">
              <ImagePicker
                label="Photo"
                value={viewData.photo}
                authPrefix="/user"
                readOnly
              />
            </div>
          )}
        </ViewSection>

        <ViewSection title="Contact">
          <DetailList columns={3}>
            <DetailItem label="Company Email" value={viewData?.company_email} />
            <DetailItem label="Personal Email" value={viewData?.personal_email} />
            <DetailItem label="Mobile" value={viewData?.mobile} />
            <DetailItem label="Alternative Mobile" value={viewData?.alternative_mobile} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Personal">
          <DetailList columns={3}>
            <DetailItem label="Date of Birth" value={viewData?.dob} />
            <DetailItem label="Gender" value={viewData?.gender} />
            <DetailItem label="Marital Status" value={viewData?.marital_status} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Address">
          <DetailList columns={3}>
            <DetailItem label="Address" value={viewData?.address} span={3} />
            <DetailItem label="City" value={viewData?.city} />
            <DetailItem label="State" value={viewData?.state} />
            <DetailItem label="Postal Code" value={viewData?.postal_code} />
            <DetailItem label="Country" value={viewData?.country} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Organisation">
          <DetailList columns={3}>
            <DetailItem label="Department" value={viewData && departmentName(viewData.department_id)} />
            <DetailItem label="Designation" value={viewData && designationName(viewData.designation_id)} />
            <DetailItem label="Role" value={viewData && roleName(viewData.role_id)} />
            <DetailItem label="Shift" value={viewData && shiftName(viewData.shift_id)} />
            <DetailItem label="Date of Joining" value={viewData?.date_of_joining} />
            <DetailItem label="Experience" value={viewData?.experience} />
            <DetailItem label="Salary Details" value={viewData?.salary_details} />
            <DetailItem label="Register Code" value={viewData?.register_code} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Emergency Contact">
          <DetailList columns={3}>
            <DetailItem label="Name" value={viewData?.emergency_name} />
            <DetailItem label="Contact" value={viewData?.emergency_contact} />
            <DetailItem label="Relationship" value={viewData?.emergency_relationship} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Policy">
          <DetailList columns={1}>
            <DetailItem
              label="Hotel Policies Acknowledged"
              value={viewData?.acknowledgment_of_hotel_policies ? "Yes" : "No"}
            />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showModal}
        title={editId ? "Edit Employee" : "Add Employee"}
        onClose={closeModal}
        showFooter
        size="xlarge"
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
          <Input label="Username" required name="username" value={formData.username} onChange={handleChange} disabled={saving} maxLength={100} />
          <Input label="First Name" required name="first_name" value={formData.first_name} onChange={handleChange} disabled={saving} maxLength={100} />
          <Input label="Last Name" required name="last_name" value={formData.last_name} onChange={handleChange} disabled={saving} maxLength={100} />
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Contact & Access</h4>
          <div className="field-grid">
            <Input label="Company Email" required type="email" name="company_email" value={formData.company_email} onChange={handleChange} disabled={saving} />
            <Input label="Personal Email" required type="email" name="personal_email" value={formData.personal_email} onChange={handleChange} disabled={saving} />
            <Input
              label={editId ? "New Password" : "Password"}
              required={!editId}
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              disabled={saving}
              helperText={editId ? "Leave blank to keep the current password." : "At least 6 characters."}
            />
            <Input label="Mobile" required type="tel" name="mobile" value={formData.mobile} onChange={handleChange} disabled={saving} />
            <Input label="Alternative Mobile" type="tel" name="alternative_mobile" value={formData.alternative_mobile} onChange={handleChange} disabled={saving} />
          </div>
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Personal</h4>
          <div className="field-grid">
            <Input label="Date of Birth" required type="date" name="dob" value={formData.dob} onChange={handleChange} disabled={saving} />
            <Select label="Gender" required name="gender" value={formData.gender} onChange={handleChange} placeholder="Select gender" disabled={saving} options={GENDERS.map((g) => ({ value: g, label: g }))} />
            <Select label="Marital Status" required name="marital_status" value={formData.marital_status} onChange={handleChange} placeholder="Select marital status" disabled={saving} options={MARITAL_STATUSES.map((m) => ({ value: m, label: m }))} />
          </div>
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Address</h4>
          <div className="field-grid">
            <Textarea label="Address" required name="address" rows={2} value={formData.address} onChange={handleChange} disabled={saving} />
            <Input label="City" required name="city" value={formData.city} onChange={handleChange} disabled={saving} />
            <Input label="State" required name="state" value={formData.state} onChange={handleChange} disabled={saving} />
            <Input label="Postal Code" required name="postal_code" value={formData.postal_code} onChange={handleChange} disabled={saving} />
            {/* Was a free-text input. /masterdata/country_currency is the
                canonical country list — the same source Tax Types and Discount
                Types read. A value already stored that is not in the list is
                kept as an option so editing cannot silently rewrite it. */}
            <Select
              label="Country"
              required
              name="country"
              value={formData.country}
              onChange={handleChange}
              placeholder="Select country"
              disabled={saving}
              options={(() => {
                const names = countries.map((c) => c.country_name).filter(Boolean);
                const opts = names.map((n) => ({ value: n, label: n }));
                if (formData.country && !names.includes(formData.country)) {
                  opts.unshift({ value: formData.country, label: `${formData.country} (not in master data)` });
                }
                return opts;
              })()}
            />
          </div>
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Organisation</h4>
          <div className="field-grid">
            <Select label="Department" required name="department_id" value={formData.department_id} onChange={handleChange} placeholder="Select department" disabled={saving} options={departments.map((d) => ({ value: d.id, label: d.department_name }))} />
            <Select label="Designation" required name="designation_id" value={formData.designation_id} onChange={handleChange} placeholder="Select designation" disabled={saving} options={designations.map((d) => ({ value: d.id, label: d.designation_name }))} />
            <Select label="Role" required name="role_id" value={formData.role_id} onChange={handleChange} placeholder="Select role" disabled={saving} options={roles.map((r) => ({ value: r.id, label: r.role_name }))} />
            <Select label="Shift" required name="shift_id" value={formData.shift_id} onChange={handleChange} placeholder="Select shift" disabled={saving} options={shifts.map((s) => ({ value: s.id, label: s.shift_name }))} />
            <Input label="Date of Joining" required type="date" name="date_of_joining" value={formData.date_of_joining} onChange={handleChange} disabled={saving} />
            <Input label="Experience" required name="experience" placeholder="e.g. 3 years" value={formData.experience} onChange={handleChange} disabled={saving} />
            <Input label="Salary Details" required name="salary_details" value={formData.salary_details} onChange={handleChange} disabled={saving} />
            <Input label="Register Code" required name="register_code" value={formData.register_code} onChange={handleChange} disabled={saving} />
          </div>
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Emergency Contact</h4>
          <div className="field-grid">
            <Input label="Name" required name="emergency_name" value={formData.emergency_name} onChange={handleChange} disabled={saving} />
            <Input label="Contact Number" required type="tel" name="emergency_contact" value={formData.emergency_contact} onChange={handleChange} disabled={saving} />
            <Input label="Relationship" required name="emergency_relationship" placeholder="e.g. Spouse" value={formData.emergency_relationship} onChange={handleChange} disabled={saving} />
          </div>
        </div>

        <div className="modal-section">
          <h4 className="modal-section__title">Photo</h4>
          <p className="modal-section__hint">
            {editId
              ? "The update endpoint does not accept a photo, so this can only be set when the employee is created."
              : `Optional. JPG or PNG, up to ${MAX_PHOTO_MB} MB.`}
          </p>
          <div className="image-picker-slot--single">
            <ImagePicker
              label="Employee Photo"
              value={formData.photo}
              authPrefix="/user"
              readOnly={!!editId}
              disabled={saving}
              accept="image/jpeg,image/png"
              onChange={(file) => {
                if (file.size / (1024 * 1024) > MAX_PHOTO_MB) {
                  showToast(`Photo must be ${MAX_PHOTO_MB} MB or smaller`, "error");
                  return;
                }
                setFormData((p) => ({ ...p, photo: file }));
              }}
              onClear={() => setFormData((p) => ({ ...p, photo: null }))}
            />
          </div>
        </div>

        <div className="modal-section">
          <Checkbox
            label="Employee has acknowledged the hotel policies"
            name="acknowledgment_of_hotel_policies"
            checked={formData.acknowledgment_of_hotel_policies}
            disabled={saving}
            onChange={(e) =>
              setFormData((p) => ({
                ...p,
                acknowledgment_of_hotel_policies: e.target.checked,
              }))
            }
          />
        </div>
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteRow}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Delete Employee"
        confirmText="Delete"
        size="small"
        destructive
      >
        {deleteRow
          ? `Delete ${fullName(deleteRow)}? They will lose access to the system and be removed from all rosters. This action cannot be undone.`
          : ""}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Employee;

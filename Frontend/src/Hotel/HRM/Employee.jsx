import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import {
  ArrowLeft,
  RefreshCw,
  Eye,
  Pencil,
  Trash2,
  X,
  Download,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import APICall, { ApiError, baseURL } from "../../APICalls/APICalls";
import "../../MasterData/MasterData.css";
import "../Reservation/Reservation.css";

// -------------------------------------------------------------------------
// Constants
// -------------------------------------------------------------------------
const GENDERS = ["Male", "Female", "Other", "Prefer not to say"];
const MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed", "Prefer not to say"];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+()\-\s\d]{7,20}$/;

const MAX_PHOTO_MB = 3;
const ALLOWED_PHOTO_EXT = ["jpg", "jpeg", "png"];

// -------------------------------------------------------------------------
// Helpers (shared conventions from Pages 7-17)
// -------------------------------------------------------------------------
const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");
const isPlainDate = (v) => /^\d{4}-\d{2}-\d{2}(T|$)/.test(String(v || ""));

const formatDate = (v) => {
  if (!v) return "—";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
};

const humaniseKey = (k) =>
  String(k || "")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());

// HR-sensitive allowlist: system columns + secrets never displayed in view modal
const isSensitive = (k) => {
  const key = String(k || "").toLowerCase();
  return (
    key === "id" ||
    key === "token" ||
    key === "company_id" ||
    key === "created_by" ||
    key === "updated_by" ||
    key === "created_at" ||
    key === "updated_at" ||
    key === "status" ||
    key === "password"
  );
};

const displayValue = (v) => {
  if (v === null || v === undefined || v === "") return "—";
  if (Array.isArray(v)) return v.length > 0 ? v.join(", ") : "—";
  if (typeof v === "object") {
    try { return JSON.stringify(v); } catch { return "—"; }
  }
  if (isPlainDate(v)) return formatDate(v);
  return String(v);
};

const resolveImage = (path) => {
  if (!path || typeof path !== "string") return null;
  if (/^https?:\/\//i.test(path)) return path;
  return `${baseURL}${path.startsWith("/") ? "" : "/"}${path}`;
};

// -------------------------------------------------------------------------
// Toast + ConfirmDialog (same pattern as Pages 7, 11, 14-17)
// -------------------------------------------------------------------------
const Toast = ({ toast, onClose }) => {
  if (!toast) return null;
  const Icon = toast.kind === "success" ? CheckCircle : AlertCircle;
  return (
    <div
      className={`reservation-toast ${toast.kind}`}
      role={toast.kind === "success" ? "status" : "alert"}
      aria-live={toast.kind === "success" ? "polite" : "assertive"}
    >
      <Icon size={18} aria-hidden="true" />
      <span>{toast.text}</span>
      <button
        type="button"
        className="reservation-toast-close"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        <X size={14} aria-hidden="true" />
      </button>
    </div>
  );
};

const ConfirmDialog = ({
  open,
  title,
  body,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
  loading = false,
}) => {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => { if (e.key === "Escape" && !loading) onCancel(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onCancel, loading]);

  if (!open) return null;
  return (
    <div
      className="modal-container"
      role="dialog"
      aria-modal="true"
      aria-labelledby="emp-confirm-title"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel(); }}
    >
      <div className="modal-content confirm-modal">
        <div className="modal-header">
          <h2 className="modal-title" id="emp-confirm-title">{title}</h2>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onCancel}
            aria-label="Close confirmation"
            disabled={loading}
          >
            <X size={22} />
          </button>
        </div>
        <div className="modal-body"><p>{body}</p></div>
        <div className="modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            className="btn btn-danger"
            onClick={onConfirm}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? "Working…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

// -------------------------------------------------------------------------
// Initial form
// -------------------------------------------------------------------------
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

// -------------------------------------------------------------------------
// Page
// -------------------------------------------------------------------------
const Employee = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [data, setData] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  const [departments, setDepartments] = useState([]);
  const [designations, setDesignations] = useState([]);
  const [roles, setRoles] = useState([]);
  const [shifts, setShifts] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [formData, setFormData] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [toast, setToast] = useState(null);
  const showToast = useCallback((kind, text) => setToast({ kind, text, at: Date.now() }), []);

  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  // --------------------------------------------------------------------
  // Load users + all four masterdata dropdowns in parallel
  // --------------------------------------------------------------------
  const load = useCallback(() => {
    setData(null);
    setError(null);
    Promise.allSettled([
      APICall.getT("/user/users"),
      APICall.getT("/user/departments"),
      APICall.getT("/user/designations"),
      APICall.getT("/user/roles"),
      APICall.getT("/user/shifts"),
    ]).then(([rUsers, rDept, rDesig, rRole, rShift]) => {
      if (!mounted.current) return;
      if (rUsers.status === "fulfilled") {
        setData(Array.isArray(rUsers.value?.data) ? rUsers.value.data : readList(rUsers.value));
        setError(null);
      } else {
        setData([]);
        setError(errMsg(rUsers.reason, "Failed to load employees."));
      }
      setDepartments(rDept.status === "fulfilled" ? readList(rDept.value) : []);
      setDesignations(rDesig.status === "fulfilled" ? readList(rDesig.value) : []);
      setRoles(rRole.status === "fulfilled" ? readList(rRole.value) : []);
      setShifts(rShift.status === "fulfilled" ? readList(rShift.value) : []);
    });
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load, refreshTick]);

  // Body scroll lock while any dialog is open
  useEffect(() => {
    const anyOpen = showModal || showViewModal || Boolean(pendingDelete);
    if (!anyOpen) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [showModal, showViewModal, pendingDelete]);

  // --------------------------------------------------------------------
  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    if (saving) return;
    setEditId(null);
    setFormError(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((p) => ({
      ...p,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const ext = (file.name.split(".").pop() || "").toLowerCase();
    if (!ALLOWED_PHOTO_EXT.includes(ext)) {
      const msg = `Photo must be one of: ${ALLOWED_PHOTO_EXT.join(", ")}.`;
      showToast("error", msg);
      e.target.value = "";
      return;
    }
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > MAX_PHOTO_MB) {
      const msg = `Photo must be ${MAX_PHOTO_MB} MB or smaller.`;
      showToast("error", msg);
      e.target.value = "";
      return;
    }
    setFormData((p) => ({ ...p, photo: file }));
  };

  const validate = () => {
    if (!formData.username?.trim()) return "Username is required.";
    if (!formData.first_name?.trim()) return "First name is required.";
    if (!formData.last_name?.trim()) return "Last name is required.";
    if (!formData.company_email?.trim()) return "Company email is required.";
    if (!EMAIL_RE.test(formData.company_email.trim())) return "Enter a valid company email.";
    if (formData.personal_email && !EMAIL_RE.test(formData.personal_email.trim())) {
      return "Personal email is not a valid address.";
    }
    if (!editId && !formData.password) return "Password is required for a new employee.";
    if (formData.password && formData.password.length < 6) return "Password must be at least 6 characters.";
    if (!formData.mobile?.trim()) return "Mobile is required.";
    if (!PHONE_RE.test(formData.mobile.trim())) return "Enter a valid mobile number.";
    if (formData.alternative_mobile && !PHONE_RE.test(formData.alternative_mobile.trim())) {
      return "Alternative mobile is not a valid number.";
    }
    if (formData.dob && isoDay(formData.dob) > isoDay(new Date().toISOString())) {
      return "Date of birth cannot be in the future.";
    }
    if (formData.date_of_joining && formData.dob && isoDay(formData.date_of_joining) < isoDay(formData.dob)) {
      return "Date of joining cannot precede date of birth.";
    }
    return null;
  };

  const buildFormData = (includeId) => {
    const fd = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (key === "photo") {
        if (value) fd.append("photo", value);
        return;
      }
      if (key === "acknowledgment_of_hotel_policies") {
        fd.append(key, value ? "true" : "false");
        return;
      }
      // company_email / personal_email trimmed + lowered.
      if (key === "company_email" || key === "personal_email") {
        fd.append(key, String(value || "").trim().toLowerCase());
        return;
      }
      if (typeof value === "string") {
        fd.append(key, value.trim());
        return;
      }
      fd.append(key, value ?? "");
    });
    if (includeId && editId) fd.set("id", String(editId));
    return fd;
  };

  const handleSave = async () => {
    const v = validate();
    if (v) {
      setFormError(v);
      showToast("error", v);
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      if (editId) {
        // Update payload — backend PUT expects JSON per userController.py update endpoint.
        const payload = { ...formData, id: editId };
        // Never resend the file object as JSON.
        if (payload.photo instanceof File) delete payload.photo;
        // Trim + lowercase emails.
        payload.company_email = String(payload.company_email || "").trim().toLowerCase();
        payload.personal_email = String(payload.personal_email || "").trim().toLowerCase();
        await APICall.putT("/user/users", payload);
        showToast("success", "Employee updated.");
      } else {
        await APICall.postT("/user/users", buildFormData(false));
        showToast("success", "Employee added.");
      }
      setShowModal(false);
      setEditId(null);
      setFormData(initialForm);
      load();
    } catch (err) {
      const m = errMsg(err, editId ? "Failed to update employee." : "Failed to add employee.");
      setFormError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      ...initialForm,
      ...row,
      password: "", // never rehydrate any password (backend doesn't return it, but be defensive)
      photo: null, // File input can't be pre-populated; leave null so user can re-upload if desired
      dob: isoDay(row.dob),
      date_of_joining: isoDay(row.date_of_joining),
      acknowledgment_of_hotel_policies: Boolean(row.acknowledgment_of_hotel_policies),
    });
    setFormError(null);
    setShowModal(true);
  };

  const handleDeleteClick = (row) => setPendingDelete(row);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleteLoading(true);
    try {
      await APICall.deleteT(`/user/users/${pendingDelete.id}`);
      showToast("success", "Employee deleted.");
      setPendingDelete(null);
      load();
    } catch (err) {
      showToast("error", errMsg(err, "Failed to delete employee."));
    } finally {
      if (mounted.current) setDeleteLoading(false);
    }
  };

  const getDepartmentName = (id) => {
    const dept = departments.find((d) => String(d.id) === String(id));
    return dept ? dept.department_name : "—";
  };

  const handleBack = () => navigate("/dashboard");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const handleExportCsv = () => {
    const list = Array.isArray(data) ? data : [];
    if (list.length === 0) {
      showToast("error", "No employees to export.");
      return;
    }
    const header = ["Username", "First Name", "Last Name", "Company Email", "Mobile", "Gender", "Department", "Role"];
    const rows = list.map((r) => [
      r.username ?? "",
      r.first_name ?? "",
      r.last_name ?? "",
      r.company_email ?? "",
      r.mobile ?? "",
      r.gender ?? "",
      getDepartmentName(r.department_id),
      roles.find((ro) => String(ro.id) === String(r.role_id))?.role_name || "",
    ]);
    const csv = [header, ...rows]
      .map((row) => row.map((cell) => {
        const s = String(cell ?? "");
        return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
      }).join(","))
      .join("\r\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `employees-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isLoading = data === null;
  const tableData = Array.isArray(data) ? data : [];

  const columns = [
    {
      key: "photo",
      title: "Photo",
      align: "center",
      type: "custom",
      render: (row) => {
        const src = resolveImage(row.photo);
        return src ? (
          <img
            src={src}
            alt=""
            style={{ width: 45, height: 45, borderRadius: "50%", objectFit: "cover" }}
            loading="lazy"
            onError={(e) => { e.currentTarget.style.display = "none"; }}
          />
        ) : (
          <span aria-hidden="true">—</span>
        );
      },
    },
    { key: "username", title: "Username", align: "center" },
    {
      key: "first_name",
      title: "Name",
      render: (row) => [row.first_name, row.last_name].filter(Boolean).join(" ") || "—",
    },
    { key: "company_email", title: "Company Email", align: "center" },
    { key: "mobile", title: "Mobile", align: "center" },
    { key: "gender", title: "Gender", align: "center" },
    {
      key: "department_id",
      title: "Department",
      align: "center",
      type: "custom",
      render: (row) => getDepartmentName(row.department_id),
    },
    {
      key: "actions",
      title: "Actions",
      align: "center",
      type: "custom",
      render: (row) => (
        <div className="table-actions">
          <button
            type="button"
            className="table-action-btn view"
            title="View"
            aria-label={`View employee ${row.username || row.id}`}
            onClick={() => openViewModal(row)}
          >
            <Eye size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            className="table-action-btn edit"
            title="Edit"
            aria-label={`Edit employee ${row.username || row.id}`}
            onClick={() => handleEdit(row)}
          >
            <Pencil size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            className="table-action-btn delete"
            title="Delete"
            aria-label={`Delete employee ${row.username || row.id}`}
            onClick={() => handleDeleteClick(row)}
          >
            <Trash2 size={16} aria-hidden="true" />
          </button>
        </div>
      ),
    },
  ];

  const viewEntries = viewData
    ? Object.entries(viewData).filter(([k]) => !isSensitive(k))
    : [];

  return (
    <div className="emp-page">
      <div className="emp-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to dashboard"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="emp-header">
          <span className="rmv-eyebrow">HRM</span>
          <h1 className="rmv-title">Employee</h1>
        </div>
        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleRefresh}
            aria-label="Refresh"
            disabled={isLoading}
          >
            <RefreshCw size={16} aria-hidden="true" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="reservation-alert" role="alert">
          <span>{error}</span>
          <button
            type="button"
            className="reservation-alert-action"
            onClick={handleRefresh}
          >
            Retry
          </button>
        </div>
      )}

      {isLoading && (
        <div className="reservation-loading" role="status" aria-live="polite">
          Loading employees…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Employee"
          variant="striped"
          pagination
          pageSize={10}
          searchable
          exportable
          hasActionButton
          actionButton={{
            icon: <Download size={18} />,
            label: "Add Employee",
            onClick: openAddModal,
            size: "medium",
            variant: "primary",
          }}
          columns={columns}
          data={tableData}
        />
      )}

      {!isLoading && !error && tableData.length === 0 && (
        <div className="reservation-empty">
          No employees yet. Use "Add Employee" to create the first one.
        </div>
      )}

      {!isLoading && tableData.length > 0 && (
        <div className="emp-export-bar">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleExportCsv}
            aria-label="Export employees as CSV"
          >
            <Download size={16} aria-hidden="true" />
            <span>Export CSV</span>
          </button>
        </div>
      )}

      {/* ================= VIEW MODAL ================= */}
      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          title={`View Employee — ${viewData.username || `#${viewData.id}`}`}
          onClose={closeViewModal}
          size="large"
        >
          <div className="modal-body grid view">
            {viewEntries.map(([key, value]) => {
              if (key === "photo") {
                const src = resolveImage(value);
                return (
                  <div className="form-group" key={key}>
                    <label>Photo</label>
                    {src ? (
                      <img
                        src={src}
                        alt={`Employee ${viewData.username || ""}`}
                        style={{
                          width: 120, height: 120, borderRadius: 10,
                          objectFit: "cover", border: "1px solid #ccc",
                        }}
                        onError={(e) => { e.currentTarget.style.display = "none"; }}
                      />
                    ) : (
                      <p>No image</p>
                    )}
                  </div>
                );
              }
              const label = humaniseKey(key);
              return (
                <div className="form-group" key={key}>
                  <label htmlFor={`emp-view-${key}`}>{label}</label>
                  <input
                    id={`emp-view-${key}`}
                    value={displayValue(value)}
                    readOnly
                    aria-readonly="true"
                  />
                </div>
              );
            })}
          </div>
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Employee" : "Add Employee"}
          onClose={closeModal}
          showFooter
          size="large"
          bodyLayout="single"
          actions={[
            {
              label: "Close",
              variant: "secondary",
              onClick: closeModal,
            },
            {
              label: saving ? "Saving…" : "Submit",
              variant: "primary",
              onClick: handleSave,
              autoFocus: true,
            },
          ]}
        >
          {formError && (
            <div className="reservation-alert inline" role="alert" style={{ marginBottom: 12 }}>
              {formError}
            </div>
          )}

          <div className="modal-body grid">
            <div className="form-group">
              <label htmlFor="emp-photo">Photo (JPG/PNG, ≤ {MAX_PHOTO_MB} MB)</label>
              <input
                id="emp-photo"
                type="file"
                name="photo"
                accept=".jpg,.jpeg,.png"
                onChange={handlePhotoChange}
                disabled={saving}
              />
              {formData.photo && (
                <p className="emp-hint">Selected: {formData.photo.name}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="emp-username">Username <span className="required">*</span></label>
              <input
                id="emp-username"
                type="text" name="username" autoComplete="username"
                value={formData.username} onChange={handleChange}
                disabled={saving} maxLength={64} required
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-first">First Name <span className="required">*</span></label>
              <input
                id="emp-first"
                type="text" name="first_name" autoComplete="given-name"
                value={formData.first_name} onChange={handleChange}
                disabled={saving} maxLength={100} required
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-last">Last Name <span className="required">*</span></label>
              <input
                id="emp-last"
                type="text" name="last_name" autoComplete="family-name"
                value={formData.last_name} onChange={handleChange}
                disabled={saving} maxLength={100} required
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-personal-email">Personal Email</label>
              <input
                id="emp-personal-email"
                type="email" inputMode="email" name="personal_email"
                autoComplete="email"
                value={formData.personal_email} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-company-email">Company Email <span className="required">*</span></label>
              <input
                id="emp-company-email"
                type="email" inputMode="email" name="company_email"
                autoComplete="email"
                value={formData.company_email} onChange={handleChange}
                disabled={saving} maxLength={100} required
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-password">
                Password {editId ? "" : <span className="required">*</span>}
                {editId && <em style={{ fontWeight: 400, marginLeft: 6, fontSize: 12 }}>(leave blank to keep current)</em>}
              </label>
              <input
                id="emp-password"
                type="password" name="password"
                autoComplete={editId ? "new-password" : "new-password"}
                value={formData.password} onChange={handleChange}
                disabled={saving} minLength={6} maxLength={255}
                required={!editId}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-mobile">Mobile <span className="required">*</span></label>
              <input
                id="emp-mobile"
                type="tel" inputMode="tel" name="mobile"
                autoComplete="tel"
                value={formData.mobile} onChange={handleChange}
                disabled={saving} maxLength={20} required
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-alt-mobile">Alternative Mobile</label>
              <input
                id="emp-alt-mobile"
                type="tel" inputMode="tel" name="alternative_mobile"
                value={formData.alternative_mobile} onChange={handleChange}
                disabled={saving} maxLength={20}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-dob">Date of Birth</label>
              <input
                id="emp-dob"
                type="date" name="dob"
                value={isoDay(formData.dob)} onChange={handleChange}
                disabled={saving}
                max={isoDay(new Date().toISOString())}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-gender">Gender</label>
              <select
                id="emp-gender"
                name="gender" value={formData.gender} onChange={handleChange}
                disabled={saving}
              >
                <option value="">Select gender</option>
                {GENDERS.map((g) => (<option key={g} value={g}>{g}</option>))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="emp-marital">Marital Status</label>
              <select
                id="emp-marital"
                name="marital_status" value={formData.marital_status} onChange={handleChange}
                disabled={saving}
              >
                <option value="">Select marital status</option>
                {MARITAL_STATUSES.map((m) => (<option key={m} value={m}>{m}</option>))}
              </select>
            </div>

            <div className="form-group" style={{ gridColumn: "1 / -1" }}>
              <label htmlFor="emp-address">Address</label>
              <textarea
                id="emp-address"
                name="address" rows={2} maxLength={500}
                value={formData.address} onChange={handleChange}
                disabled={saving}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-city">City</label>
              <input
                id="emp-city" type="text" name="city" autoComplete="address-level2"
                value={formData.city} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-state">State</label>
              <input
                id="emp-state" type="text" name="state" autoComplete="address-level1"
                value={formData.state} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-postal">Postal Code</label>
              <input
                id="emp-postal" type="text" name="postal_code" autoComplete="postal-code"
                value={formData.postal_code} onChange={handleChange}
                disabled={saving} maxLength={20}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-country">Country</label>
              <input
                id="emp-country" type="text" name="country" autoComplete="country-name"
                value={formData.country} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group" style={{ gridColumn: "1 / -1" }}>
              <label htmlFor="emp-department">Department</label>
              <select
                id="emp-department" name="department_id"
                value={formData.department_id} onChange={handleChange}
                disabled={saving}
              >
                <option value="">Select a department</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>{d.department_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ gridColumn: "1 / -1" }}>
              <label htmlFor="emp-designation">Designation</label>
              <select
                id="emp-designation" name="designation_id"
                value={formData.designation_id} onChange={handleChange}
                disabled={saving}
              >
                <option value="">Select a designation</option>
                {designations.map((d) => (
                  <option key={d.id} value={d.id}>{d.designation_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ gridColumn: "1 / -1" }}>
              <label htmlFor="emp-role">Role</label>
              <select
                id="emp-role" name="role_id"
                value={formData.role_id} onChange={handleChange}
                disabled={saving}
              >
                <option value="">Select a role</option>
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>{r.role_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ gridColumn: "1 / -1" }}>
              <label htmlFor="emp-shift">Shift</label>
              <select
                id="emp-shift" name="shift_id"
                value={formData.shift_id} onChange={handleChange}
                disabled={saving}
              >
                <option value="">Select a shift</option>
                {shifts.map((s) => (
                  <option key={s.id} value={s.id}>{s.shift_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="emp-joining">Date of Joining</label>
              <input
                id="emp-joining" type="date" name="date_of_joining"
                value={isoDay(formData.date_of_joining)} onChange={handleChange}
                disabled={saving}
                min={isoDay(formData.dob) || undefined}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-experience">Experience</label>
              <input
                id="emp-experience" type="text" name="experience"
                value={formData.experience} onChange={handleChange}
                disabled={saving} maxLength={100}
                placeholder="e.g. 3 years"
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-salary">Salary Details</label>
              <input
                id="emp-salary" type="text" name="salary_details"
                value={formData.salary_details} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-register-code">Register Code</label>
              <input
                id="emp-register-code" type="text" name="register_code"
                value={formData.register_code} onChange={handleChange}
                disabled={saving} maxLength={64}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-emerg-name">Emergency Contact Name</label>
              <input
                id="emp-emerg-name" type="text" name="emergency_name"
                value={formData.emergency_name} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-emerg-contact">Emergency Contact Number</label>
              <input
                id="emp-emerg-contact" type="tel" inputMode="tel" name="emergency_contact"
                value={formData.emergency_contact} onChange={handleChange}
                disabled={saving} maxLength={20}
              />
            </div>

            <div className="form-group">
              <label htmlFor="emp-emerg-rel">Emergency Contact Relationship</label>
              <input
                id="emp-emerg-rel" type="text" name="emergency_relationship"
                value={formData.emergency_relationship} onChange={handleChange}
                disabled={saving} maxLength={100}
              />
            </div>

            <div className="form-group" style={{ gridColumn: "1 / -1" }}>
              <label htmlFor="emp-ack" className="emp-ack-label">
                <input
                  id="emp-ack"
                  type="checkbox"
                  name="acknowledgment_of_hotel_policies"
                  checked={formData.acknowledgment_of_hotel_policies}
                  onChange={handleChange}
                  disabled={saving}
                />
                <span>I acknowledge that I have read, understood, and agree to comply with the hotel's policies.</span>
              </label>
            </div>
          </div>
        </Modal>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete employee"
        body={
          pendingDelete
            ? `Delete employee ${pendingDelete.username || pendingDelete.id}? This action cannot be undone.`
            : ""
        }
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
        loading={deleteLoading}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default Employee;

import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
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
import APICall, { ApiError } from "../../APICalls/APICalls";
import "../Reservation/Reservation.css";

// -------------------------------------------------------------------------
// Constants
// -------------------------------------------------------------------------
const INQUIRY_MODES = ["Phone", "Email", "Walk-in", "Web", "Referral", "Other"];
const INQUIRY_STATUSES = ["Open", "In Progress", "Resolved", "Pending", "Closed"];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  

// -------------------------------------------------------------------------
// Helpers (shared conventions from Pages 7-16)
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
    .replace(/([A-Z])/g, " $1")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());

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
    key === "status"
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

const inquiryStatusClass = (status) => {
  const s = String(status || "").toLowerCase();
  if (s === "open") return "status-confirmed";      // blue
  if (s === "in progress") return "status-pending"; // amber
  if (s === "resolved") return "status-checked-in"; // green
  if (s === "pending") return "status-pending";     // amber
  if (s === "closed") return "status-checked-out";  // pink/muted
  return "status-pending";
};

// -------------------------------------------------------------------------
// Toast
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

// -------------------------------------------------------------------------
// Confirm dialog
// -------------------------------------------------------------------------
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
      aria-labelledby="ge-confirm-title"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel(); }}
    >
      <div className="modal-content confirm-modal">
        <div className="modal-header">
          <h2 className="modal-title" id="ge-confirm-title">{title}</h2>
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
// View modal
// -------------------------------------------------------------------------
const DetailsModal = ({ open, title, entity, onClose }) => {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [open]);

  if (!open || !entity) return null;

  const entries = Object.entries(entity).filter(([k]) => !isSensitive(k));

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="ge-view-title"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="modal-card modal-sm">
        <div className="modal-header">
          <h3 id="ge-view-title">{title}</h3>
          <button
            type="button"
            onClick={onClose}
            aria-label={`Close ${title}`}
          >
            <X size={18} aria-hidden="true" />
          </button>
        </div>

        <div className="modal-body single view">
          {entries.map(([key, value]) => (
            <div className="form-group" key={key}>
              <label htmlFor={`ge-detail-${key}`}>{humaniseKey(key)}</label>
              <input
                id={`ge-detail-${key}`}
                value={displayValue(value)}
                readOnly
                aria-readonly="true"
              />
            </div>
          ))}
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="btn secondary"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

// -------------------------------------------------------------------------
// Add / Edit modal
// -------------------------------------------------------------------------
const initialForm = {
  inquiryMode: "",
  guestName: "",
  responseDate: "",
  followUpDate: "",
  incidents: "",
  status: "Open",
};

// -------------------------------------------------------------------------
// Page
// -------------------------------------------------------------------------
const GuestEnquiry = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [data, setData] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

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

  const load = useCallback(() => {
    setData(null);
    setError(null);
    APICall.getT("/hotel/inquiry")
      .then((res) => {
        if (!mounted.current) return;
        setData(Array.isArray(res?.data) ? res.data : readList(res));
      })
      .catch((err) => {
        if (!mounted.current) return;
        setData([]);
        setError(errMsg(err, "Failed to load enquiries."));
      });
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load, refreshTick]);

  // Escape / body-scroll-lock for the CRUD modal
  useEffect(() => {
    if (!showModal) return undefined;
    const onKey = (e) => { if (e.key === "Escape" && !saving) closeModal(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
     
  }, [showModal, saving]);

  useEffect(() => {
    const anyOpen = showModal || showViewModal || Boolean(pendingDelete);
    if (!anyOpen) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [showModal, showViewModal, pendingDelete]);

  // ---------------------------------------------------------------
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
    setEditId(null);
    setFormError(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      inquiryMode: row.inquiry_mode || "",
      guestName: row.guest_name || "",
      status: row.inquiry_status || "Open",
      responseDate: isoDay(row.response),
      followUpDate: isoDay(row.follow_up),
      incidents: row.incidents || "",
    });
    setFormError(null);
    setShowModal(true);
  };

  const validate = () => {
    if (!formData.inquiryMode.trim()) return "Inquiry mode is required.";
    if (!INQUIRY_MODES.includes(formData.inquiryMode)) return `Inquiry mode must be one of: ${INQUIRY_MODES.join(", ")}`;
    if (!formData.guestName.trim()) return "Guest name is required.";
    if (!INQUIRY_STATUSES.includes(formData.status)) return `Status must be one of: ${INQUIRY_STATUSES.join(", ")}`;
    if (formData.responseDate && formData.followUpDate && isoDay(formData.followUpDate) < isoDay(formData.responseDate)) {
      return "Follow-up date cannot be before the response date.";
    }
    return null;
  };

  const buildPayload = (includeId = false) => {
    const payload = {
      inquiry_mode: formData.inquiryMode,
      guest_name: formData.guestName.trim(),
      inquiry_status: formData.status,
      response: formData.responseDate || null,
      follow_up: formData.followUpDate || null,
      incidents: formData.incidents || null,
    };
    if (includeId && editId) payload.id = editId;
    return payload;
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
        await APICall.putT("/hotel/inquiry", buildPayload(true));
        showToast("success", "Enquiry updated.");
      } else {
        await APICall.postT("/hotel/inquiry", buildPayload(false));
        showToast("success", "Enquiry created.");
      }
      closeModal();
      load();
    } catch (err) {
      const m = errMsg(err, editId ? "Failed to update enquiry." : "Failed to create enquiry.");
      setFormError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  const handleDeleteClick = (row) => setPendingDelete(row);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleteLoading(true);
    try {
      await APICall.deleteT(`/hotel/inquiry/${pendingDelete.id}`);
      showToast("success", "Enquiry deleted.");
      setPendingDelete(null);
      load();
    } catch (err) {
      showToast("error", errMsg(err, "Failed to delete enquiry."));
    } finally {
      if (mounted.current) setDeleteLoading(false);
    }
  };

  const handleBack = () => navigate("/dashboard");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const handleExportCsv = () => {
    const list = Array.isArray(data) ? data : [];
    if (list.length === 0) {
      showToast("error", "No enquiries to export.");
      return;
    }
    const header = ["Inquiry Mode", "Guest Name", "Response", "Follow Up", "Status", "Incidents"];
    const rows = list.map((r) => [
      r.inquiry_mode ?? "",
      r.guest_name ?? "",
      r.response ?? "",
      r.follow_up ?? "",
      r.inquiry_status ?? "",
      r.incidents ?? "",
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
    a.download = `guest-enquiries-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isLoading = data === null;
  const tableData = Array.isArray(data) ? data : [];

  const columns = [
    { key: "inquiry_mode", title: "Inquiry Mode", align: "center" },
    { key: "guest_name", title: "Guest Name", align: "center" },
    {
      key: "response",
      title: "Response",
      align: "center",
      render: (row) => formatDate(row.response),
    },
    {
      key: "follow_up",
      title: "Follow Up",
      align: "center",
      render: (row) => formatDate(row.follow_up),
    },
    {
      key: "inquiry_status",
      title: "Status",
      align: "center",
      type: "custom",
      render: (row) => (
        <span className={`rmv-status-badge ${inquiryStatusClass(row.inquiry_status)}`}>
          {row.inquiry_status || "—"}
        </span>
      ),
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
            aria-label={`View enquiry for ${row.guest_name || "guest"}`}
            onClick={() => openViewModal(row)}
          >
            <Eye size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            className="table-action-btn edit"
            title="Edit"
            aria-label={`Edit enquiry for ${row.guest_name || "guest"}`}
            onClick={() => handleEdit(row)}
          >
            <Pencil size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            className="table-action-btn delete"
            title="Delete"
            aria-label={`Delete enquiry for ${row.guest_name || "guest"}`}
            onClick={() => handleDeleteClick(row)}
          >
            <Trash2 size={16} aria-hidden="true" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="ge-page">
      <div className="ge-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to dashboard"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="ge-header">
          <span className="rmv-eyebrow">Front Office</span>
          <h1 className="rmv-title">Guest Enquiry</h1>
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
          Loading enquiries…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Guest Enquiry"
          variant="striped"
          pagination
          pageSize={10}
          searchable
          exportable
          hasActionButton
          actionButton={{
            label: "Add New Enquiry",
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
          No enquiries yet. Use "Add New Enquiry" to create the first one.
        </div>
      )}

      {!isLoading && tableData.length > 0 && (
        <div className="ge-export-bar">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleExportCsv}
            aria-label="Export enquiries as CSV"
          >
            <Download size={16} aria-hidden="true" />
            <span>Export CSV</span>
          </button>
        </div>
      )}

      {/* Add / Edit modal */}
      {showModal && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="ge-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget && !saving) closeModal(); }}
        >
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3 id="ge-modal-title">{editId ? "Edit Enquiry" : "Add Enquiry"}</h3>
              <button
                type="button"
                onClick={closeModal}
                aria-label="Close enquiry dialog"
                disabled={saving}
              >
                <X size={18} aria-hidden="true" />
              </button>
            </div>

            {formError && (
              <div className="reservation-alert inline" role="alert">
                {formError}
              </div>
            )}

            <div className="modal-body single">
              <div className="ge-form-grid">
              <div className="form-group">
                <label htmlFor="ge-mode">Inquiry Mode <span className="required">*</span></label>
                <select
                  id="ge-mode"
                  name="inquiryMode"
                  value={formData.inquiryMode}
                  onChange={handleChange}
                  disabled={saving}
                  required
                >
                  <option value="">— select —</option>
                  {INQUIRY_MODES.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="ge-name">Guest Name <span className="required">*</span></label>
                <input
                  id="ge-name"
                  type="text"
                  name="guestName"
                  value={formData.guestName}
                  onChange={handleChange}
                  disabled={saving}
                  maxLength={100}
                  autoComplete="name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="ge-response">Response Date</label>
                <input
                  id="ge-response"
                  type="date"
                  name="responseDate"
                  value={formData.responseDate}
                  onChange={handleChange}
                  disabled={saving}
                />
              </div>

              <div className="form-group">
                <label htmlFor="ge-followup">Follow-up Date</label>
                <input
                  id="ge-followup"
                  type="date"
                  name="followUpDate"
                  value={formData.followUpDate}
                  onChange={handleChange}
                  disabled={saving}
                  min={formData.responseDate || undefined}
                />
              </div>

              <div className="form-group">
                <label htmlFor="ge-status">Status <span className="required">*</span></label>
                <select
                  id="ge-status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  disabled={saving}
                  required
                >
                  {INQUIRY_STATUSES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div className="form-group ge-field-full">
                <label htmlFor="ge-incidents">Incident Notes</label>
                <textarea
                  id="ge-incidents"
                  name="incidents"
                  value={formData.incidents}
                  onChange={handleChange}
                  disabled={saving}
                  maxLength={1000}
                  rows={4}
                />
              </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn secondary"
                onClick={closeModal}
                disabled={saving}
              >
                Close
              </button>
              <button
                type="button"
                className="btn primary"
                onClick={handleSave}
                disabled={saving}
                aria-busy={saving}
              >
                {saving ? "Saving…" : "Submit"}
              </button>
            </div>
          </div>
        </div>
      )}

      <DetailsModal
        open={showViewModal}
        title="View Guest Enquiry"
        entity={viewData}
        onClose={closeViewModal}
      />

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete enquiry"
        body={
          pendingDelete
            ? `Delete enquiry from ${pendingDelete.guest_name || "guest"}? This action cannot be undone.`
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

export default GuestEnquiry;

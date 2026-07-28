import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
import {
  ArrowLeft,
  RefreshCw,
  X,
  Pencil,
  Trash2,
  Eye,
  Download,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "../../MasterData/MasterData.css";
import "../Reservation/Reservation.css";

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

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
      aria-labelledby="shift-confirm-title"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel(); }}
    >
      <div className="modal-content confirm-modal">
        <div className="modal-header">
          <h2 className="modal-title" id="shift-confirm-title">{title}</h2>
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
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={loading}>
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

const initialForm = { shift_name: "", start_time: "", end_time: "" };

const Shift = () => {
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
    APICall.getT("/user/shifts")
      .then((res) => {
        if (!mounted.current) return;
        setData(Array.isArray(res?.data) ? res.data : readList(res));
      })
      .catch((err) => {
        if (!mounted.current) return;
        setData([]);
        setError(errMsg(err, "Failed to load shifts."));
      });
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load, refreshTick]);

  useEffect(() => {
    if (!showModal && !showViewModal) return undefined;
    const onKey = (e) => {
      if (e.key !== "Escape") return;
      if (showModal && !saving) closeModal();
      else if (showViewModal) closeViewModal();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showModal, showViewModal, saving]);

  useEffect(() => {
    const anyOpen = showModal || showViewModal || Boolean(pendingDelete);
    if (!anyOpen) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [showModal, showViewModal, pendingDelete]);

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

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
  };

  const closeViewModal = () => {
    setShowViewModal(false);
    setViewData(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validate = () => {
    if (!formData.shift_name?.trim()) return "Shift name is required.";
    if (formData.shift_name.trim().length > 100) return "Shift name must be under 100 characters.";
    if (!formData.start_time) return "Start time is required.";
    if (!formData.end_time) return "End time is required.";
    // start/end are HH:MM strings; overnight shifts (end < start) are legit — allow.
    if (formData.start_time === formData.end_time) return "Start time and end time cannot be identical.";
    return null;
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
        await APICall.putT("/user/shifts", {
          id: editId,
          shift_name: formData.shift_name.trim(),
          start_time: formData.start_time,
          end_time: formData.end_time,
        });
        showToast("success", "Shift updated.");
      } else {
        await APICall.postT("/user/shifts", {
          shift_name: formData.shift_name.trim(),
          start_time: formData.start_time,
          end_time: formData.end_time,
        });
        showToast("success", "Shift created.");
      }
      closeModal();
      load();
    } catch (err) {
      const m = errMsg(err, editId ? "Failed to update shift." : "Failed to create shift.");
      setFormError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      shift_name: row.shift_name || "",
      start_time: row.start_time || "",
      end_time: row.end_time || "",
    });
    setFormError(null);
    setShowModal(true);
  };

  const handleDeleteClick = (row) => setPendingDelete(row);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleteLoading(true);
    try {
      await APICall.deleteT(`/user/shifts/${pendingDelete.id}`);
      showToast("success", "Shift deleted.");
      setPendingDelete(null);
      load();
    } catch (err) {
      showToast("error", errMsg(err, "Failed to delete shift."));
    } finally {
      if (mounted.current) setDeleteLoading(false);
    }
  };

  const handleBack = () => navigate("/dashboard");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const handleExportCsv = () => {
    const list = Array.isArray(data) ? data : [];
    if (list.length === 0) {
      showToast("error", "No shifts to export.");
      return;
    }
    const header = ["Shift Name", "Start Time", "End Time"];
    const rows = list.map((r) => [r.shift_name ?? "", r.start_time ?? "", r.end_time ?? ""]);
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
    a.download = `shifts-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isLoading = data === null;
  const tableData = Array.isArray(data) ? data : [];

  const columns = [
    { key: "shift_name", title: "Shift Name", align: "center" },
    { key: "start_time", title: "Start Time", align: "center" },
    { key: "end_time", title: "End Time", align: "center" },
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
            aria-label={`View shift ${row.shift_name || row.id}`}
            onClick={() => openViewModal(row)}
          >
            <Eye size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            className="table-action-btn edit"
            title="Edit"
            aria-label={`Edit shift ${row.shift_name || row.id}`}
            onClick={() => handleEdit(row)}
          >
            <Pencil size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            className="table-action-btn delete"
            title="Delete"
            aria-label={`Delete shift ${row.shift_name || row.id}`}
            onClick={() => handleDeleteClick(row)}
          >
            <Trash2 size={16} aria-hidden="true" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="shift-page">
      <div className="shift-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to dashboard"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="shift-header">
          <span className="rmv-eyebrow">HRM</span>
          <h1 className="rmv-title">Shifts</h1>
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
          Loading shifts…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Shift List"
          variant="striped"
          pagination
          pageSize={10}
          searchable
          exportable
          hasActionButton
          actionButton={{
            icon: <Download size={18} />,
            label: "Add Shift",
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
          No shifts yet. Use "Add Shift" to create the first one.
        </div>
      )}

      {!isLoading && tableData.length > 0 && (
        <div className="shift-export-bar">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleExportCsv}
            aria-label="Export shifts as CSV"
          >
            <Download size={16} aria-hidden="true" />
            <span>Export CSV</span>
          </button>
        </div>
      )}

      {/* View modal */}
      {showViewModal && viewData && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="shift-view-title"
          onClick={(e) => { if (e.target === e.currentTarget) closeViewModal(); }}
        >
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3 id="shift-view-title">View Shift — {viewData.shift_name || `#${viewData.id}`}</h3>
              <button
                type="button"
                onClick={closeViewModal}
                aria-label="Close view shift"
              >
                <X size={18} aria-hidden="true" />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label htmlFor="shift-view-name">Shift Name</label>
                <input
                  id="shift-view-name"
                  value={viewData.shift_name || "—"}
                  readOnly
                  aria-readonly="true"
                />
              </div>
              <div className="form-group">
                <label htmlFor="shift-view-start">Start Time</label>
                <input
                  id="shift-view-start"
                  value={viewData.start_time || "—"}
                  readOnly
                  aria-readonly="true"
                />
              </div>
              <div className="form-group">
                <label htmlFor="shift-view-end">End Time</label>
                <input
                  id="shift-view-end"
                  value={viewData.end_time || "—"}
                  readOnly
                  aria-readonly="true"
                />
              </div>
            </div>

            <div className="modal-footer">
              <button type="button" className="btn secondary" onClick={closeViewModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add / Edit modal */}
      {showModal && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="shift-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget && !saving) closeModal(); }}
        >
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3 id="shift-modal-title">{editId ? "Edit Shift" : "Add Shift"}</h3>
              <button
                type="button"
                onClick={closeModal}
                aria-label="Close shift dialog"
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
              <div className="form-group">
                <label htmlFor="shift-name">Shift Name <span className="required">*</span></label>
                <input
                  id="shift-name"
                  type="text"
                  name="shift_name"
                  value={formData.shift_name}
                  onChange={handleChange}
                  disabled={saving}
                  maxLength={100}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="shift-start">Start Time <span className="required">*</span></label>
                <input
                  id="shift-start"
                  type="time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleChange}
                  disabled={saving}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="shift-end">End Time <span className="required">*</span></label>
                <input
                  id="shift-end"
                  type="time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleChange}
                  disabled={saving}
                  required
                />
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

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete shift"
        body={
          pendingDelete
            ? `Delete shift "${pendingDelete.shift_name || pendingDelete.id}"? Employees assigned to this shift will need to be reassigned. This action cannot be undone.`
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

export default Shift;

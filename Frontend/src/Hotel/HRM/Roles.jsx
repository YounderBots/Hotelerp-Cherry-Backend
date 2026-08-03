import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Textarea from "../../stories/Form/Textarea";
import IconButton from "../../stories/IconButton";
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
import "../Reservation/Reservation.css";
import "./HRM.css";

// -------------------------------------------------------------------------
// Helpers (shared conventions)
// -------------------------------------------------------------------------
const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

// -------------------------------------------------------------------------
// Toast + ConfirmDialog (shared inline pattern)
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
      aria-labelledby="rl-confirm-title"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel(); }}
    >
      <div className="modal-content confirm-modal">
        <div className="modal-header">
          <h2 className="modal-title" id="rl-confirm-title">{title}</h2>
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
// Page
// -------------------------------------------------------------------------
const initialForm = { roleName: "", description: "" };

const Role = () => {
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
    APICall.getT("/user/roles")
      .then((res) => {
        if (!mounted.current) return;
        setData(Array.isArray(res?.data) ? res.data : readList(res));
      })
      .catch((err) => {
        if (!mounted.current) return;
        setData([]);
        setError(errMsg(err, "Failed to load roles."));
      });
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load, refreshTick]);

  useEffect(() => {
    const anyOpen = showModal || showViewModal || Boolean(pendingDelete);
    if (!anyOpen) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [showModal, showViewModal, pendingDelete]);

  // -------------------------
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
    if (!formData.roleName.trim()) return "Role name is required.";
    if (formData.roleName.trim().length > 100) return "Role name must be under 100 characters.";
    if (formData.description && formData.description.length > 500) return "Description must be under 500 characters.";
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
        await APICall.putT("/user/roles", {
          id: editId,
          role_name: formData.roleName.trim(),
          description: formData.description || null,
        });
        showToast("success", "Role updated.");
      } else {
        await APICall.postT("/user/roles", {
          role_name: formData.roleName.trim(),
          description: formData.description || null,
        });
        showToast("success", "Role created.");
      }
      closeModal();
      load();
    } catch (err) {
      const m = errMsg(err, editId ? "Failed to update role." : "Failed to create role.");
      setFormError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      roleName: row.role_name || "",
      description: row.description || "",
    });
    setFormError(null);
    setShowModal(true);
  };

  const handleDeleteClick = (row) => setPendingDelete(row);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleteLoading(true);
    try {
      await APICall.deleteT(`/user/roles/${pendingDelete.id}`);
      showToast("success", "Role deleted.");
      setPendingDelete(null);
      load();
    } catch (err) {
      showToast("error", errMsg(err, "Failed to delete role."));
    } finally {
      if (mounted.current) setDeleteLoading(false);
    }
  };

  const handleBack = () => navigate("/dashboard");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const handleExportCsv = () => {
    const list = Array.isArray(data) ? data : [];
    if (list.length === 0) {
      showToast("error", "No roles to export.");
      return;
    }
    const header = ["Role Name", "Description"];
    const rows = list.map((r) => [r.role_name ?? "", r.description ?? ""]);
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
    a.download = `roles-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isLoading = data === null;
  const tableData = Array.isArray(data) ? data : [];

  const columns = [
    { key: "role_name", title: "Role Name", align: "center" },
    { key: "description", title: "Description", align: "center" },
    {
      key: "actions",
      title: "Actions",
      align: "center",
      type: "custom",
      render: (row) => (
        <div className="table-actions">
          <IconButton
            variant="ghost"
            size="small"
            icon={<Eye size={16} />}
            onClick={() => openViewModal(row)}
            ariaLabel={`View role ${row.role_name || row.id}`}
          />
          <IconButton
            variant="subtle"
            size="small"
            icon={<Pencil size={16} />}
            onClick={() => handleEdit(row)}
            ariaLabel={`Edit role ${row.role_name || row.id}`}
          />
          <IconButton
            variant="danger-ghost"
            size="small"
            icon={<Trash2 size={16} />}
            onClick={() => handleDeleteClick(row)}
            ariaLabel={`Delete role ${row.role_name || row.id}`}
          />
        </div>
      ),
    },
  ];

  return (
    <div className="rol-page">
      <div className="rol-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to dashboard"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="rol-header">
          <span className="rmv-eyebrow">HRM</span>
          <h1 className="rmv-title">Roles</h1>
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
          Loading roles…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Role List"
          variant="striped"
          pagination
          pageSize={10}
          searchable
          exportable
          hasActionButton
          actionButton={{
            label: "Add Role",
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
          No roles yet. Use "Add Role" to create the first one.
        </div>
      )}

      {!isLoading && tableData.length > 0 && (
        <div className="rol-export-bar">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleExportCsv}
            aria-label="Export roles as CSV"
          >
            <Download size={16} aria-hidden="true" />
            <span>Export CSV</span>
          </button>
        </div>
      )}

      {/* View modal */}
      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          title={`View Role — ${viewData.role_name || `#${viewData.id}`}`}
          onClose={closeViewModal}
          size="medium"
          bodyLayout="single"
          viewMode
        >
          <Input label="Role Name" value={viewData.role_name || "—"} readOnly disabled />
          <Textarea label="Description" value={viewData.description || ""} readOnly disabled rows={4} />
        </Modal>
      )}

      {/* Add / Edit modal */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Role" : "Add Role"}
          onClose={closeModal}
          showFooter
          size="medium"
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

          <Input
            label="Role Name"
            required
            type="text"
            name="roleName"
            value={formData.roleName}
            onChange={handleChange}
            disabled={saving}
            maxLength={100}
          />

          <Textarea
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            disabled={saving}
            maxLength={500}
            rows={4}
          />
        </Modal>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete role"
        body={
          pendingDelete
            ? `Delete role "${pendingDelete.role_name || pendingDelete.id}"? Users currently assigned to this role may lose access. This action cannot be undone.`
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

export default Role;

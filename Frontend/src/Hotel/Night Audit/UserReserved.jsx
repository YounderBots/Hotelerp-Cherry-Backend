import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Tabs, { Tab } from "../../stories/Tabs";
import TableTemplate from "../../stories/TableTemplate";
import {
  Download,
  Eye,
  X,
  ArrowLeft,
  RefreshCw,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import "./NightAudit.css";
import "../Reservation/Reservation.css";
import APICall, { ApiError } from "../../APICalls/APICalls";

// -------------------------------------------------------------------------
// Helpers
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
    key === "status" ||
    key === "proof_document"
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

const guestFullName = (r) =>
  [r?.salutation, r?.first_name, r?.last_name].filter(Boolean).join(" ").trim() || "—";

// Backend reservation_status class map (mirrors Page 7/8/13).
const statusClass = (status) => {
  const s = String(status || "").toLowerCase();
  if (s === "pending") return "status-pending";
  if (s === "confirmed") return "status-confirmed";
  if (s === "arrived" || s === "checked-in") return "status-checked-in";
  if (s === "departures" || s === "checked-out") return "status-checked-out";
  if (s === "cancelled" || s === "canceled") return "status-cancelled";
  return "status-pending";
};

const taskStatusClass = (status) => {
  const s = String(status || "").toLowerCase();
  if (s === "completed" || s === "done") return "status-checked-in";
  if (s === "in progress" || s === "in_progress" || s === "in service") return "status-confirmed";
  if (s === "pending" || s === "assigned") return "status-pending";
  if (s === "cancelled" || s === "canceled") return "status-cancelled";
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
// View modal — renders a whitelisted key/value grid
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
      aria-labelledby="ur-details-title"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="modal-card large">
        <div className="modal-header">
          <h3 id="ur-details-title">{title}</h3>
          <button
            type="button"
            onClick={onClose}
            aria-label={`Close ${title}`}
          >
            <X size={18} aria-hidden="true" />
          </button>
        </div>

        <div className="modal-body grid view">
          {entries.map(([key, value]) => (
            <div className="form-group" key={key}>
              <label htmlFor={`ur-detail-${key}`}>{humaniseKey(key)}</label>
              <input
                id={`ur-detail-${key}`}
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
// CSV export helper (RFC-4180 + BOM for Excel)
// -------------------------------------------------------------------------
const downloadCsv = (filename, header, rows) => {
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
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// -------------------------------------------------------------------------
// Page
// -------------------------------------------------------------------------
const UserReserved = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [reservations, setReservations] = useState(null); // null = loading
  const [tasks, setTasks] = useState(null);
  const [resError, setResError] = useState(null);
  const [taskError, setTaskError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  const [viewReservation, setViewReservation] = useState(null);
  const [viewKeeper, setViewKeeper] = useState(null);

  const [toast, setToast] = useState(null);
  const showToast = useCallback((kind, text) => setToast({ kind, text, at: Date.now() }), []);

  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    mounted.current = true;
    setReservations(null);
    setTasks(null);
    setResError(null);
    setTaskError(null);

    Promise.allSettled([
      APICall.getT("/hotel/room_reservation"),
      APICall.getT("/hotel/housekeeper_tasks"),
    ]).then(([rRes, rTask]) => {
      if (!mounted.current) return;
      if (rRes.status === "fulfilled") {
        setReservations(Array.isArray(rRes.value?.data) ? rRes.value.data : readList(rRes.value));
      } else {
        setReservations([]);
        setResError(errMsg(rRes.reason, "Failed to load reservations."));
      }
      if (rTask.status === "fulfilled") {
        setTasks(readList(rTask.value));
      } else {
        setTasks([]);
        setTaskError(errMsg(rTask.reason, "Failed to load housekeeper tasks."));
      }
    });

    return () => { mounted.current = false; };
  }, [refreshTick]);

  const handleBack = () => navigate("/reservation");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const handleExportReservations = () => {
    const list = Array.isArray(reservations) ? reservations : [];
    if (list.length === 0) {
      showToast("error", "No reservations to export.");
      return;
    }
    downloadCsv(
      `user-activity-${isoDay(new Date().toISOString())}.csv`,
      ["Reservation ID", "Guest", "Phone", "Email", "Arrival", "Departure", "Nights", "Status"],
      list.map((r) => [
        r.room_reservation_id ?? r.id,
        guestFullName(r),
        r.phone_number ?? "",
        r.email ?? "",
        r.arrival_date ?? "",
        r.departure_date ?? "",
        r.no_of_nights ?? "",
        r.reservation_status ?? "",
      ]),
    );
  };

  const handleExportTasks = () => {
    const list = Array.isArray(tasks) ? tasks : [];
    if (list.length === 0) {
      showToast("error", "No housekeeper tasks to export.");
      return;
    }
    downloadCsv(
      `housekeeper-tasks-${isoDay(new Date().toISOString())}.csv`,
      ["Employee ID", "Name", "Schedule Date", "Schedule Time", "Room", "Task Type", "Assigned Staff", "Task Status", "Room Status"],
      list.map((t) => [
        t.employee_id ?? "",
        [t.first_name, t.last_name].filter(Boolean).join(" "),
        t.schedule_date ?? "",
        t.schedule_time ?? "",
        t.room_no ?? "",
        t.task_type ?? "",
        t.assign_staff ?? "",
        t.task_status ?? "",
        t.room_status ?? "",
      ]),
    );
  };

  const reservationsLoading = reservations === null;
  const tasksLoading = tasks === null;
  const reservationsList = Array.isArray(reservations) ? reservations : [];
  const tasksList = Array.isArray(tasks) ? tasks : [];

  // ---------------------------------------------------------------
  // Columns
  // ---------------------------------------------------------------
  const reservationColumns = [
    { key: "room_reservation_id", title: "Reservation ID", align: "center", width: "160px" },
    {
      key: "first_name",
      title: "Guest",
      render: (row) => guestFullName(row),
    },
    { key: "phone_number", title: "Phone", align: "center" },
    {
      key: "arrival_date",
      title: "Arrival",
      align: "center",
      render: (row) => formatDate(row.arrival_date),
    },
    {
      key: "departure_date",
      title: "Departure",
      align: "center",
      render: (row) => formatDate(row.departure_date),
    },
    {
      key: "reservation_status",
      title: "Status",
      align: "center",
      type: "custom",
      render: (row) => (
        <span className={`rvw-status-chip ${statusClass(row.reservation_status)}`}>
          {row.reservation_status || "—"}
        </span>
      ),
    },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => (
        <button
          type="button"
          className="table-action-btn view"
          onClick={() => setViewReservation(row)}
          aria-label={`View reservation ${row.room_reservation_id || row.id}`}
        >
          <Eye size={16} aria-hidden="true" />
        </button>
      ),
    },
  ];

  const houseKeeperColumns = [
    { key: "employee_id", title: "Employee ID", align: "center" },
    {
      key: "first_name",
      title: "Name",
      render: (row) => [row.first_name, row.last_name].filter(Boolean).join(" ") || "—",
    },
    {
      key: "schedule_date",
      title: "Schedule Date",
      align: "center",
      render: (row) => formatDate(row.schedule_date),
    },
    { key: "schedule_time", title: "Schedule Time", align: "center" },
    { key: "room_no", title: "Room", align: "center" },
    { key: "task_type", title: "Task Type", align: "center" },
    { key: "assign_staff", title: "Assigned Staff", align: "center" },
    {
      key: "task_status",
      title: "Task Status",
      align: "center",
      type: "custom",
      render: (row) => (
        <span className={`rvw-status-chip ${taskStatusClass(row.task_status)}`}>
          {row.task_status || "—"}
        </span>
      ),
    },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => (
        <button
          type="button"
          className="table-action-btn view"
          onClick={() => setViewKeeper(row)}
          aria-label={`View task for ${row.first_name || "employee"} in room ${row.room_no || "?"}`}
        >
          <Eye size={16} aria-hidden="true" />
        </button>
      ),
    },
  ];

  return (
    <div className="userreserved-wrapper">
      <div className="ur-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to reservations"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="ur-header">
          <span className="rmv-eyebrow">Night Audit</span>
          <h1 className="rmv-title">User Activity & Housekeeping</h1>
        </div>
        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleRefresh}
            aria-label="Refresh"
            disabled={reservationsLoading || tasksLoading}
          >
            <RefreshCw size={16} aria-hidden="true" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <Tabs variant="default">
        <Tab label="User Activity Logs">
          {resError && (
            <div className="rmv-alert" role="alert">
              <span>{resError}</span>
              <button type="button" className="rmv-alert-action" onClick={handleRefresh}>Retry</button>
            </div>
          )}

          {reservationsLoading && (
            <div className="rmv-loading" role="status" aria-live="polite">
              Loading reservations…
            </div>
          )}

          {!reservationsLoading && (
            <TableTemplate
              variant="striped"
              pagination
              pageSize={5}
              searchable
              exportable
              hasActionButton
              actionButton={{
                icon: <Download size={18} />,
                label: "Export CSV",
                onClick: handleExportReservations,
                size: "small",
                variant: "outline",
              }}
              columns={reservationColumns}
              data={reservationsList}
            />
          )}

          {!reservationsLoading && !resError && reservationsList.length === 0 && (
            <div className="rmv-empty">No user activity yet.</div>
          )}
        </Tab>

        <Tab label="House Keeper Details">
          {taskError && (
            <div className="rmv-alert" role="alert">
              <span>{taskError}</span>
              <button type="button" className="rmv-alert-action" onClick={handleRefresh}>Retry</button>
            </div>
          )}

          {tasksLoading && (
            <div className="rmv-loading" role="status" aria-live="polite">
              Loading housekeeper tasks…
            </div>
          )}

          {!tasksLoading && (
            <TableTemplate
              title="House Keeper Task"
              variant="striped"
              pagination
              pageSize={4}
              searchable
              exportable
              hasActionButton
              actionButton={{
                icon: <Download size={18} />,
                label: "Export CSV",
                onClick: handleExportTasks,
                size: "small",
                variant: "outline",
              }}
              columns={houseKeeperColumns}
              data={tasksList}
            />
          )}

          {!tasksLoading && !taskError && tasksList.length === 0 && (
            <div className="rmv-empty">No housekeeping tasks yet.</div>
          )}
        </Tab>
      </Tabs>

      <DetailsModal
        open={Boolean(viewReservation)}
        title="Reservation Details"
        entity={viewReservation}
        onClose={() => setViewReservation(null)}
      />

      <DetailsModal
        open={Boolean(viewKeeper)}
        title="House Keeper Task Details"
        entity={viewKeeper}
        onClose={() => setViewKeeper(null)}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default UserReserved;

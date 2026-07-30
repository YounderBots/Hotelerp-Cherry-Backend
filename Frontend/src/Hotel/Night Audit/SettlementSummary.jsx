import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
import {
  ArrowLeft,
  Download,
  Eye,
  RefreshCw,
  X,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./NightAudit.css";
import "../Reservation/Reservation.css";

// -------------------------------------------------------------------------
// Helpers
// -------------------------------------------------------------------------
const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");
const isPlainDate = (v) => /^\d{4}-\d{2}-\d{2}(T|$)/.test(String(v || ""));

const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

const numberFmt = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
const formatAmount = (v) => numberFmt.format(num(v));

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

// Derive settlement status from balance (client-side).
// A settlement row is "Settled" when overall_amount was fully paid, "Outstanding"
// when the guest still owes money, and "Overpaid" when we owe them a refund.
const settlementBucket = (row) => {
  const balance = num(row?.balance_amount);
  if (balance > 0.005) return "outstanding";
  if (balance < -0.005) return "overpaid";
  return "settled";
};

const SETTLEMENT_LABEL = {
  settled: "Settled",
  outstanding: "Outstanding",
  overpaid: "Overpaid",
};

const SETTLEMENT_CLASS = {
  settled: "status-checked-in",     // green
  outstanding: "status-cancelled",  // red
  overpaid: "status-confirmed",     // blue
};

// -------------------------------------------------------------------------
// Toast + Details modal (shared pattern)
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
      aria-labelledby="ss-details-title"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="modal-card large">
        <div className="modal-header">
          <h3 id="ss-details-title">{title}</h3>
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
              <label htmlFor={`ss-detail-${key}`}>{humaniseKey(key)}</label>
              <input
                id={`ss-detail-${key}`}
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
// Page
// -------------------------------------------------------------------------
const SettlementSummary = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [data, setData] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);
  const [viewSettlement, setViewSettlement] = useState(null);
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
    APICall.getT("/hotel/room_reservation")
      .then((res) => {
        if (!mounted.current) return;
        setData(Array.isArray(res?.data) ? res.data : readList(res));
      })
      .catch((err) => {
        if (!mounted.current) return;
        setData([]);
        setError(errMsg(err, "Failed to load settlement data."));
      });
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load, refreshTick]);

  const handleBack = () => navigate("/reservation");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const tableData = Array.isArray(data) ? data : [];
  const isLoading = data === null;

  const totals = useMemo(() => {
    const t = { total: 0, paid: 0, balance: 0, settled: 0, outstanding: 0, overpaid: 0 };
    for (const r of tableData) {
      t.total += num(r.overall_amount ?? r.total_amount);
      t.paid += num(r.paid_amount);
      t.balance += num(r.balance_amount);
      const b = settlementBucket(r);
      t[b] += 1;
    }
    return t;
  }, [tableData]);

  const handleExportCsv = () => {
    if (tableData.length === 0) {
      showToast("error", "No settlement data to export.");
      return;
    }
    const header = ["Reservation ID", "Guest", "Phone", "Arrival", "Departure", "Total", "Paid", "Balance", "Settlement Status"];
    const rows = tableData.map((r) => [
      r.room_reservation_id ?? r.id,
      guestFullName(r),
      r.phone_number ?? "",
      r.arrival_date ?? "",
      r.departure_date ?? "",
      num(r.overall_amount ?? r.total_amount).toFixed(2),
      num(r.paid_amount).toFixed(2),
      num(r.balance_amount).toFixed(2),
      SETTLEMENT_LABEL[settlementBucket(r)],
    ]);
    // Totals row
    rows.push([
      "",
      "TOTAL",
      "",
      "",
      "",
      totals.total.toFixed(2),
      totals.paid.toFixed(2),
      totals.balance.toFixed(2),
      `Settled: ${totals.settled} · Outstanding: ${totals.outstanding} · Overpaid: ${totals.overpaid}`,
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
    a.download = `settlement-summary-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const columns = [
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
      key: "overall_amount",
      title: "Total",
      align: "right",
      render: (row) => formatAmount(row.overall_amount ?? row.total_amount),
    },
    {
      key: "paid_amount",
      title: "Paid",
      align: "right",
      render: (row) => formatAmount(row.paid_amount),
    },
    {
      key: "balance_amount",
      title: "Balance",
      align: "right",
      type: "custom",
      render: (row) => {
        const bucket = settlementBucket(row);
        const cls =
          bucket === "outstanding" ? "ss-balance-outstanding"
          : bucket === "overpaid" ? "ss-balance-overpaid"
          : "ss-balance-settled";
        return <span className={cls}>{formatAmount(row.balance_amount)}</span>;
      },
    },
    {
      key: "settlement_status",
      title: "Settlement Status",
      align: "center",
      type: "custom",
      render: (row) => {
        const bucket = settlementBucket(row);
        return (
          <span className={`rmv-status-badge ${SETTLEMENT_CLASS[bucket]}`}>
            {SETTLEMENT_LABEL[bucket]}
          </span>
        );
      },
    },
    {
      key: "actions",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => (
        <button
          type="button"
          className="table-action-btn view"
          title="View settlement"
          aria-label={`View settlement for ${row.room_reservation_id || row.id}`}
          onClick={() => setViewSettlement(row)}
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
          <h1 className="rmv-title">Settlement Summary</h1>
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
        <div className="rmv-alert" role="alert">
          <span>{error}</span>
          <button type="button" className="rmv-alert-action" onClick={handleRefresh}>Retry</button>
        </div>
      )}

      {!isLoading && !error && tableData.length > 0 && (
        <div className="ss-totals" role="status" aria-live="polite">
          <div>
            <span>Bookings</span>
            <b>{tableData.length}</b>
          </div>
          <div>
            <span>Total billed</span>
            <b>{formatAmount(totals.total)}</b>
          </div>
          <div>
            <span>Total paid</span>
            <b>{formatAmount(totals.paid)}</b>
          </div>
          <div>
            <span>Outstanding</span>
            <b className={totals.balance > 0.005 ? "ss-balance-outstanding" : ""}>
              {formatAmount(totals.balance)}
            </b>
          </div>
          <div>
            <span>Settled / Outstanding / Overpaid</span>
            <b>{totals.settled} / {totals.outstanding} / {totals.overpaid}</b>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="rmv-loading" role="status" aria-live="polite">
          Loading settlement data…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Settlement Summary"
          variant="striped"
          pagination
          pageSize={10}
          searchable
          exportable
          hasActionButton
          actionButton={{
            icon: <Download size={18} />,
            label: "Export CSV",
            onClick: handleExportCsv,
            size: "small",
            variant: "outline",
          }}
          columns={columns}
          data={tableData}
        />
      )}

      {!isLoading && !error && tableData.length === 0 && (
        <div className="rmv-empty">No settlement data yet.</div>
      )}

      <DetailsModal
        open={Boolean(viewSettlement)}
        title="Settlement Details"
        entity={viewSettlement}
        onClose={() => setViewSettlement(null)}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default SettlementSummary;

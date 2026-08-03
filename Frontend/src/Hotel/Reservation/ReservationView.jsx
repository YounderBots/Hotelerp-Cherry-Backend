import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./Reservation.css";

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const numberFmt = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
const formatAmount = (v) => (Number.isFinite(Number(v)) ? numberFmt.format(Number(v)) : "—");

const formatDate = (v) => {
  if (!v) return "—";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
};

const guestName = (r) =>
  [r?.salutation, r?.first_name, r?.last_name].filter(Boolean).join(" ").trim() || "Guest";

// Bucket by the real reservation_status master data vocabulary
// (Booked / Checked-In / Checked-Out / Cancelled / No Show).
// Also tolerates the legacy Confirmed/Arrived/Departures/Pending labels.
const bucketOf = (r) => {
  const s = String(r?.reservation_status || "").toLowerCase();
  if (s === "checked-in" || s === "arrived") return "checked_in";
  if (s === "checked-out" || s === "departures") return "checked_out";
  if (s === "cancelled" || s === "canceled") return "cancelled";
  if (s === "no show" || s === "no-show") return "no_show";
  if (s === "booked" || s === "confirmed" || s === "pending") return "booked";
  return "booked";
};

const BUCKET_LABEL = {
  booked: "Booked",
  checked_in: "Checked-In",
  checked_out: "Checked-Out",
  cancelled: "Cancelled",
  no_show: "No Show",
};

const BUCKET_CLASS = {
  booked: "status-pending",
  checked_in: "status-checked-in",
  checked_out: "status-checked-out",
  cancelled: "status-cancelled",
  no_show: "status-cancelled",
};

const ReservationView = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [reservations, setReservations] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);
  const [activeTab, setActiveTab] = useState("all");

  const load = useCallback(() => {
    setReservations(null);
    setError(null);
    APICall.getT("/hotel/room_reservation")
      .then((res) => {
        if (!mounted.current) return;
        setReservations(Array.isArray(res?.data) ? res.data : readList(res));
      })
      .catch((err) => {
        if (!mounted.current) return;
        setReservations([]);
        setError(errMsg(err, "Failed to load reservations."));
      });
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load, refreshTick]);

  const counts = useMemo(() => {
    const list = reservations || [];
    const c = { all: list.length, booked: 0, checked_in: 0, checked_out: 0, cancelled: 0, no_show: 0 };
    for (const r of list) {
      const b = bucketOf(r);
      c[b] = (c[b] || 0) + 1;
    }
    return c;
  }, [reservations]);

  const filtered = useMemo(() => {
    const list = reservations || [];
    if (activeTab === "all") return list;
    return list.filter((r) => bucketOf(r) === activeTab);
  }, [reservations, activeTab]);

  const isLoading = reservations === null;

  const handleBack = () => navigate("/reservation");
  const handleRefresh = () => setRefreshTick((n) => n + 1);
  const handleCardOpen = (r) =>
    navigate("/ReservationView", { state: { reservationId: r.id } });

  return (
    <div className="rvv-page">
      <div className="rvv-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to reservations"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="rvv-header">
          <span className="rmv-eyebrow">Reservations</span>
          <h1 className="rmv-title">Reservation View</h1>
        </div>
        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleRefresh}
            aria-label="Refresh reservations"
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

      <div className="rvw-tabs" role="tablist" aria-label="Filter reservations by status">
        {[
          { key: "all", label: "All" },
          { key: "booked", label: "Booked" },
          { key: "checked_in", label: "Checked-In" },
          { key: "checked_out", label: "Checked-Out" },
          { key: "cancelled", label: "Cancelled" },
          { key: "no_show", label: "No Show" },
        ].map((tab) => {
          const active = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              type="button"
              role="tab"
              aria-selected={active}
              className={`rvw-tab ${active ? "active" : ""}`}
              onClick={() => setActiveTab(tab.key)}
            >
              <span>{tab.label}</span>
              <span className="rvw-tab-count">{counts[tab.key] ?? 0}</span>
            </button>
          );
        })}
      </div>

      {isLoading && (
        <div className="rmv-loading" role="status" aria-live="polite">
          Loading reservations…
        </div>
      )}

      {!isLoading && (reservations || []).length === 0 && !error && (
        <div className="rmv-empty">
          No reservations yet.
        </div>
      )}

      {!isLoading && filtered.length === 0 && (reservations || []).length > 0 && (
        <div className="rmv-empty inline">
          No reservations in this category.
        </div>
      )}

      {!isLoading && filtered.length > 0 && (
        <div className="rvv-grid">
          {filtered.map((r) => {
            const bucket = bucketOf(r);
            return (
              <button
                type="button"
                key={r.id}
                className="rvv-card"
                onClick={() => handleCardOpen(r)}
                aria-label={`Open reservation ${r.room_reservation_id || r.id} for ${guestName(r)}`}
              >
                <div className="rvv-card-top">
                  <div className="rvv-card-guest">
                    <h4>{guestName(r)}</h4>
                    <span className="rvv-card-id">#{r.room_reservation_id || r.id}</span>
                  </div>
                  <span className={`rmv-status-badge ${BUCKET_CLASS[bucket]}`}>
                    {BUCKET_LABEL[bucket]}
                  </span>
                </div>

                <div className="rvv-card-dates">
                  <div>
                    <p>{formatDate(r.arrival_date)}</p>
                    <label>Check In</label>
                  </div>
                  <div>
                    <p>{formatDate(r.departure_date)}</p>
                    <label>Check Out</label>
                  </div>
                  <div>
                    <p>{r.no_of_nights ?? "—"}</p>
                    <label>Nights</label>
                  </div>
                </div>

                <div className="rvv-card-amounts">
                  <div>
                    <span>Total</span>
                    <b>{formatAmount(r.overall_amount ?? r.total_amount)}</b>
                  </div>
                  <div>
                    <span>Paid</span>
                    <b>{formatAmount(r.paid_amount)}</b>
                  </div>
                  <div className="rvv-balance">
                    <span>Balance</span>
                    <b>{formatAmount(r.balance_amount)}</b>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ReservationView;

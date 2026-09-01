import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { useApiResource } from "../../hooks/useApiResource";
import "./Reservation.css";

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

// Bucket by the property's real status vocabulary, which is Master Data:
// Confirmed / Checked-In / Checked-Out / Cancelled / No-Show / Pending /
// On Hold. The previous version bucketed on "Booked", a label this system has
// never stored, and labelled the upcoming-arrivals tab with it.
//
// Comparison folds case, spaces and hyphens so a property that retypes
// "No Show" or "NO-SHOW" still lands in the right bucket -- the label is free
// text an operator can edit under Master Data.
const fold = (v) => String(v || "").toLowerCase().replace(/[^a-z]/g, "");

const bucketOf = (r) => {
  const s = fold(r?.reservation_status);
  if (s === "checkedin" || s === "arrived") return "checked_in";
  if (s === "checkedout" || s === "departures") return "checked_out";
  if (s === "cancelled" || s === "canceled") return "cancelled";
  if (s === "noshow") return "no_show";
  // Everything still ahead of arrival -- Confirmed, Pending, On Hold -- is an
  // upcoming stay, which is what this tab is for.
  return "upcoming";
};

const BUCKET_LABEL = {
  upcoming: "Upcoming",
  checked_in: "Checked-In",
  checked_out: "Checked-Out",
  cancelled: "Cancelled",
  no_show: "No-Show",
};

const BUCKET_CLASS = {
  upcoming: "status-pending",
  checked_in: "status-checked-in",
  checked_out: "status-checked-out",
  cancelled: "status-cancelled",
  no_show: "status-cancelled",
};

const ReservationView = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("all");

  // `useApiResource` replaces a hand-written load/refresh pair that carried its
  // own `mounted` ref, its own error mapping and a refresh counter. The hook
  // owns all three, and its deferred start is what keeps this screen free of
  // the extra render pass `react-hooks/set-state-in-effect` warns about.
  const {
    data: reservations,
    loading,
    error,
    reload,
  } = useApiResource(() => APICall.getT("/hotel/room_reservation"), {
    select: readList,
    fallback: "Failed to load reservations.",
  });

  const counts = useMemo(() => {
    const list = reservations || [];
    const c = { all: list.length, upcoming: 0, checked_in: 0, checked_out: 0, cancelled: 0, no_show: 0 };
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

  const isLoading = loading;

  const handleBack = () => navigate("/reservation");
  const handleRefresh = () => reload();
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
          { key: "upcoming", label: "Upcoming" },
          { key: "checked_in", label: "Checked-In" },
          { key: "checked_out", label: "Checked-Out" },
          { key: "cancelled", label: "Cancelled" },
          { key: "no_show", label: "No-Show" },
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

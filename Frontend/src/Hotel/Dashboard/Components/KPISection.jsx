import React from "react";
import KPICard from "./KPICard";
import { Plus, RefreshCw } from "lucide-react";

const numberFmt = new Intl.NumberFormat(undefined);

const formatCount = (n) => (Number.isFinite(n) ? numberFmt.format(n) : "—");

const formatCurrency = (n) => {
  if (!Number.isFinite(n)) return "—";
  return numberFmt.format(Math.round(n));
};

const KPISection = ({
  displayName = "back",
  kpis = {},
  loading = false,
  error = null,
  onAddBooking,
  onRefresh,
}) => {
  const {
    newBookingsToday = 0,
    arrivingToday = 0,
    departingToday = 0,
    availableRooms = 0,
    totalRevenue = 0,
  } = kpis;

  const cards = [
    { title: "New Bookings (today)", value: loading ? "…" : formatCount(newBookingsToday), type: "bookings" },
    { title: "Check-In (today)", value: loading ? "…" : formatCount(arrivingToday), type: "checkin" },
    { title: "Check-Out (today)", value: loading ? "…" : formatCount(departingToday), type: "checkout" },
    { title: "Rooms Available", value: loading ? "…" : formatCount(availableRooms), type: "available" },
    { title: "Total Revenue", value: loading ? "…" : formatCurrency(totalRevenue), type: "revenue", note: "Sum of overall_amount across live reservations" },
  ];

  return (
    <div className="kpi-section">
      <div className="dashboard-header dashboard-header-inline">
        <div>
          <h2 className="dashboard-hello">Welcome back, {displayName}</h2>
          <p className="dashboard-subtitle">Hotel operations overview</p>
        </div>

        <div className="dashboard-actions">
          <button
            type="button"
            className="btn-outline"
            onClick={onRefresh}
            aria-label="Refresh dashboard"
            disabled={loading}
          >
            <RefreshCw size={16} aria-hidden="true" />
            <span>Refresh</span>
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={onAddBooking}
            aria-label="Create a new reservation"
          >
            <Plus size={16} aria-hidden="true" />
            <span>Add Booking</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="dashboard-alert" role="alert">
          <span>Some dashboard data could not be loaded: {error}</span>
          <button
            type="button"
            className="dashboard-alert-action"
            onClick={onRefresh}
          >
            Retry
          </button>
        </div>
      )}

      <div className="kpi-grid">
        {cards.map((card, index) => (
          <KPICard
            key={card.type}
            title={card.title}
            value={card.value}
            note={card.note}
            type={card.type}
            loading={loading}
            index={index}
          />
        ))}
      </div>
    </div>
  );
};

export default KPISection;

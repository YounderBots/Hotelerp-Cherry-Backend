import React from "react";
import {
  Calendar,
  LogIn,
  LogOut,
  BedDouble,
  DollarSign,
} from "lucide-react";

const iconMap = {
  bookings: Calendar,
  checkin: LogIn,
  checkout: LogOut,
  available: BedDouble,
  revenue: DollarSign,
};

const KPICard = ({ title, value, note, type, loading = false }) => {
  const Icon = iconMap[type] || Calendar;

  return (
    <div
      className={`kpi-card ${loading ? "loading" : ""}`}
      role="group"
      aria-label={`${title}: ${loading ? "loading" : value}`}
    >
      <div className="kpi-top">
        <span className="kpi-title">{title}</span>
        <div className="kpi-icon" aria-hidden="true">
          <Icon size={18} />
        </div>
      </div>

      <div className="kpi-value" aria-live="polite">
        {loading ? <span className="kpi-skeleton" aria-hidden="true" /> : value}
      </div>

      {note && !loading && (
        <div className="kpi-note" title={note}>
          {note}
        </div>
      )}
    </div>
  );
};

export default KPICard;

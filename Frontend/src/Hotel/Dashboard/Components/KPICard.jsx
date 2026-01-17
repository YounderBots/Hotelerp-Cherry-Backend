// KPICard.jsx
import React from "react";
import {
  Calendar,
  LogIn,
  LogOut,
  BedDouble,
  DollarSign,
  TrendingUp,
  TrendingDown,
} from "lucide-react";

const iconMap = {
  bookings: Calendar,
  checkin: LogIn,
  checkout: LogOut,
  available: BedDouble,
  revenue: DollarSign,
};

const KPICard = ({
  title,
  value,
  change,
  type,
  negative,
  active,
  onClick,
}) => {
  const Icon = iconMap[type];
  const TrendIcon = negative ? TrendingDown : TrendingUp;

  return (
    <div
      className={`kpi-card ${active ? "active" : ""}`}
      onClick={onClick}
    >
      <div className="kpi-top">
        <span className="kpi-title">{title}</span>
        <div className="kpi-icon">
          <Icon size={18} />
        </div>
      </div>

      <div className="kpi-value">{value}</div>

      <div className={`kpi-badge ${negative ? "down" : "up"}`}>
        <TrendIcon size={14} />
        <span>{change}</span>
        <small>from last week</small>
      </div>
    </div>
  );
};

export default KPICard;

import React from "react";
import {
  Calendar,
  LogIn,
  LogOut,
  BedDouble,
  DollarSign,
  Wallet,
  ShoppingBag,
  Receipt,
  Calculator,
  XCircle,
  Users,
} from "lucide-react";

const iconMap = {
  bookings: Calendar,
  checkin: LogIn,
  checkout: LogOut,
  available: BedDouble,
  revenue: DollarSign,
  sales: Wallet,
  orders: ShoppingBag,
  bills: Receipt,
  avgcheck: Calculator,
  cancelled: XCircle,
  staff: Users,
};

const HERO_TYPES = new Set(["revenue", "sales"]);

const KPICard = ({ title, value, note, type, loading = false, index = 0 }) => {
  const Icon = iconMap[type] || Calendar;
  const isHero = HERO_TYPES.has(type);

  return (
    <div
      className={`kpi-card kpi-card--${type} ${isHero ? "kpi-card--hero" : ""} ${loading ? "loading" : ""}`}
      role="group"
      aria-label={`${title}: ${loading ? "loading" : value}`}
      style={{ "--kpi-delay": `${index * 60}ms` }}
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

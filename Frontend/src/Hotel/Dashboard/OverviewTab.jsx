import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, CalendarPlus, Hotel, Utensils, Wine } from "lucide-react";

import APICall, { ApiError } from "../../APICalls/APICalls";
import KPICard from "./Components/KPICard";
import DonutChart from "./Components/DonutChart";
import RoomAvailability from "./Components/RoomAvailability";
import MiniTableCard from "./Components/MiniTableCard";

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");
const today = isoDay(new Date().toISOString());
const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);

const numberFmt = new Intl.NumberFormat(undefined);
const formatCount = (n) => (Number.isFinite(n) ? numberFmt.format(n) : "—");
const formatCurrency = (n) => (Number.isFinite(n) ? numberFmt.format(Math.round(n)) : "—");

// One validated medium-tone accent per department, reused consistently across
// the Revenue Split donut, module cards, and Quick Actions.
const DEPT_ACCENT = { hotel: "#e0294a", restaurant: "#c8860b", bar: "#9366cc" };
const DEPT_TINT = { hotel: "var(--primary-lightest)", restaurant: "#faf1dc", bar: "#f1eaf8" };

const STATUS_VARIANT = {
  "checked-in": "success",
  "checked-out": "muted",
  confirmed: "info",
  cancelled: "error",
  pending: "warning",
};
const statusVariant = (status) => STATUS_VARIANT[String(status || "").toLowerCase()] || "muted";

const guestColumns = [
  { key: "name", title: "Guest" },
  { key: "type", title: "Type", align: "center" },
  {
    key: "status",
    title: "Status",
    align: "center",
    render: (row) => <span className={`status-pill status-pill--${statusVariant(row.status)}`}>{row.status}</span>,
  },
];

const OverviewTab = ({ onNavigate }) => {
  const navigate = useNavigate();
  const mounted = useRef(true);
  const [hotel, setHotel] = useState(null);
  const [restaurant, setRestaurant] = useState(null);
  const [bar, setBar] = useState(null);
  const [todayGuests, setTodayGuests] = useState(null);
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    mounted.current = true;
    setHotel(null);
    setRestaurant(null);
    setBar(null);
    setTodayGuests(null);
    setError(null);

    Promise.allSettled([
      APICall.getT("/hotel/room_reservation"),
      APICall.getT("/masterdata/room"),
      APICall.getT("/restaurant/reports/daily_sales", { report_date: today }),
      APICall.getT("/bar/reports/daily_sales", { report_date: today }),
    ]).then(([rRes, rRoom, rRestaurant, rBar]) => {
      if (!mounted.current) return;

      const reservations = rRes.status === "fulfilled" && Array.isArray(rRes.value?.data) ? rRes.value.data : [];
      const rooms = rRoom.status === "fulfilled" && Array.isArray(rRoom.value?.data) ? rRoom.value.data : [];

      const statusCounts = { Occupied: 0, Reserved: 0, Available: 0, "Not Ready": 0 };
      for (const r of rooms) {
        const bs = String(r?.booking_status || "").toLowerCase();
        const ws = String(r?.working_status || "").toLowerCase();
        if (ws === "maintenance" || ws === "out of order" || ws === "dirty" || ws === "not ready") {
          statusCounts["Not Ready"] += 1;
        } else if (bs === "occupied" || bs === "checked-in" || bs === "checkedin") {
          statusCounts.Occupied += 1;
        } else if (bs === "reserved" || bs === "booked" || bs === "pending") {
          statusCounts.Reserved += 1;
        } else {
          statusCounts.Available += 1;
        }
      }

      const arrivingToday = reservations.filter((r) => isoDay(r?.arrival_date) === today).length;
      const departingToday = reservations.filter((r) => isoDay(r?.departure_date) === today).length;
      const hotelRevenue = reservations.reduce((sum, r) => {
        const v = Number(r?.overall_amount);
        return Number.isFinite(v) ? sum + v : sum;
      }, 0);

      setHotel({
        revenue: hotelRevenue,
        occupancyPct: rooms.length > 0 ? (statusCounts.Occupied / rooms.length) * 100 : 0,
        occupiedRooms: statusCounts.Occupied,
        totalRooms: rooms.length,
        arrivingToday,
        departingToday,
        statusCounts,
      });

      const guestName = (r) => `${r?.first_name || ""} ${r?.last_name || ""}`.trim() || "Guest";
      const arrivals = reservations
        .filter((r) => isoDay(r?.arrival_date) === today)
        .map((r) => ({ key: `arr-${r.id}`, name: guestName(r), type: "Arrival", status: r?.reservation_status || "—" }));
      const departures = reservations
        .filter((r) => isoDay(r?.departure_date) === today)
        .map((r) => ({ key: `dep-${r.id}`, name: guestName(r), type: "Departure", status: r?.reservation_status || "—" }));
      setTodayGuests([...arrivals, ...departures]);

      setRestaurant(
        rRestaurant.status === "fulfilled"
          ? {
              revenue: Number(rRestaurant.value?.data?.grand_total) || 0,
              orders: Number(rRestaurant.value?.data?.total_orders) || 0,
              bills: Number(rRestaurant.value?.data?.total_bills) || 0,
            }
          : null,
      );

      setBar(
        rBar.status === "fulfilled"
          ? {
              revenue: Number(rBar.value?.data?.grand_total) || 0,
              orders: Number(rBar.value?.data?.total_orders) || 0,
              bills: Number(rBar.value?.data?.total_bills) || 0,
            }
          : null,
      );

      const failures = [rRes, rRoom, rRestaurant, rBar].filter((r) => r.status === "rejected");
      setError(failures.length > 0 ? errMsg(failures[0].reason, "Some overview data could not be loaded.") : null);
    });

    return () => { mounted.current = false; };
  }, [refreshTick]);

  const loading = hotel === null && restaurant === null && bar === null;

  const combinedRevenue = useMemo(() => {
    if (loading) return null;
    return (hotel?.revenue || 0) + (restaurant?.revenue || 0) + (bar?.revenue || 0);
  }, [loading, hotel, restaurant, bar]);

  const combinedBills = useMemo(() => {
    if (loading) return null;
    return (restaurant?.bills || 0) + (bar?.bills || 0);
  }, [loading, restaurant, bar]);

  const kpis = [
    { title: "Combined Revenue Today", value: loading ? "…" : formatCurrency(combinedRevenue), type: "revenue", note: "Hotel + Restaurant + Bar" },
    { title: "Hotel Occupancy", value: loading || !hotel ? "…" : `${Math.round(hotel.occupancyPct)}%`, type: "available", note: hotel ? `${hotel.occupiedRooms} of ${hotel.totalRooms} rooms` : undefined },
    { title: "Restaurant Orders Today", value: loading ? "…" : formatCount(restaurant?.orders), type: "orders" },
    { title: "Bar Orders Today", value: loading ? "…" : formatCount(bar?.orders), type: "orders" },
    { title: "Total Bills Today", value: loading ? "…" : formatCount(combinedBills), type: "bills", note: "Restaurant + Bar" },
  ];

  const modules = [
    {
      key: "hotel",
      tabIndex: 1,
      label: "Hotel",
      icon: Hotel,
      stats: hotel
        ? [
            { label: "Revenue Today", value: formatCurrency(hotel.revenue) },
            { label: "Arrivals Today", value: formatCount(hotel.arrivingToday) },
            { label: "Departures Today", value: formatCount(hotel.departingToday) },
          ]
        : [],
    },
    {
      key: "restaurant",
      tabIndex: 2,
      label: "Restaurant",
      icon: Utensils,
      stats: restaurant
        ? [
            { label: "Revenue Today", value: formatCurrency(restaurant.revenue) },
            { label: "Orders Today", value: formatCount(restaurant.orders) },
            { label: "Bills Today", value: formatCount(restaurant.bills) },
          ]
        : [],
    },
    {
      key: "bar",
      tabIndex: 3,
      label: "Bar",
      icon: Wine,
      stats: bar
        ? [
            { label: "Revenue Today", value: formatCurrency(bar.revenue) },
            { label: "Orders Today", value: formatCount(bar.orders) },
            { label: "Bills Today", value: formatCount(bar.bills) },
          ]
        : [],
    },
  ];

  return (
    <div className="dashboard-wrapper">
      {error && (
        <div className="dashboard-alert" role="alert">
          <span>{error}</span>
          <button type="button" className="dashboard-alert-action" onClick={() => setRefreshTick((n) => n + 1)}>
            Retry
          </button>
        </div>
      )}

      <div className="kpi-grid">
        {kpis.map((card, index) => (
          <KPICard key={card.title} title={card.title} value={card.value} note={card.note} type={card.type} loading={loading} index={index} />
        ))}
      </div>

      <div className="dashboard-row">
        {modules.map((mod) => {
          const Icon = mod.icon;
          return (
            <div key={mod.key} className="dashboard-col dashboard-col-4">
              <div className="card module-summary-card" style={{ "--dept-accent": DEPT_ACCENT[mod.key] }}>
                <div className="card-header-inline">
                  <h4>
                    <Icon size={16} className="module-summary-icon" aria-hidden="true" /> {mod.label}
                  </h4>
                </div>

                {loading ? (
                  <div className="dashboard-empty" role="status" aria-live="polite">Loading…</div>
                ) : (
                  <>
                    <dl className="module-summary-stats">
                      {mod.stats.map((s) => (
                        <div key={s.label}>
                          <dt>{s.label}</dt>
                          <dd>{s.value}</dd>
                        </div>
                      ))}
                    </dl>
                    <button type="button" className="btn-link module-summary-link" onClick={() => onNavigate?.(mod.tabIndex)}>
                      View {mod.label} <ArrowRight size={14} aria-hidden="true" />
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-6">
          <DonutChart
            title="Revenue Split"
            loading={loading}
            emptyMessage="No revenue recorded for today."
            valueFormatter={formatCurrency}
            centerValue={loading ? "…" : formatCurrency(combinedRevenue)}
            centerCaption="Total Today"
            data={[
              { label: "Hotel", value: hotel?.revenue || 0, color: DEPT_ACCENT.hotel },
              { label: "Restaurant", value: restaurant?.revenue || 0, color: DEPT_ACCENT.restaurant },
              { label: "Bar", value: bar?.revenue || 0, color: DEPT_ACCENT.bar },
            ]}
          />
        </div>
        <div className="dashboard-col dashboard-col-6">
          <RoomAvailability
            counts={hotel?.statusCounts}
            total={hotel?.totalRooms || 0}
            loading={loading}
          />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-8">
          <MiniTableCard
            title="Today's Arrivals & Departures"
            columns={guestColumns}
            rows={todayGuests || []}
            loading={loading}
            emptyMessage="No arrivals or departures scheduled for today."
            rowKey="key"
          />
        </div>
        <div className="dashboard-col dashboard-col-4">
          <div className="card quick-actions-card">
            <div className="card-header-inline">
              <h4>Quick Actions</h4>
            </div>
            <div className="quick-actions-list">
              {[
                { key: "hotel", label: "New Reservation", icon: CalendarPlus, path: "/add_new_reservation" },
                { key: "restaurant", label: "New Restaurant Order", icon: Utensils, path: "/orders" },
                { key: "bar", label: "New Bar Order", icon: Wine, path: "/bar_orders" },
              ].map((action) => {
                const Icon = action.icon;
                return (
                  <button
                    key={action.key}
                    type="button"
                    className="quick-action-btn"
                    style={{ "--qa-accent": DEPT_ACCENT[action.key], "--qa-tint": DEPT_TINT[action.key] }}
                    onClick={() => navigate(action.path)}
                  >
                    <span className="quick-action-icon">
                      <Icon size={16} aria-hidden="true" />
                    </span>
                    <span className="quick-action-label">{action.label}</span>
                    <ArrowRight size={14} className="quick-action-arrow" aria-hidden="true" />
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;

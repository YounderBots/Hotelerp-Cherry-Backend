import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  CalendarPlus,
  Hotel,
  Utensils,
  Wine,
  DollarSign,
  BedDouble,
  ShoppingBag,
  Receipt,
} from "lucide-react";

import APICall, { ApiError } from "../../APICalls/APICalls";
import DonutChart from "./Components/DonutChart";
import RoomAvailability from "./Components/RoomAvailability";
import MiniTableCard from "./Components/MiniTableCard";
import "./OverviewTab.css";

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
      // A SUMMARY, not the whole book -- see the note in HotelDashboardTab.
      // This screen shows two counts and a list of today's arrivals and
      // departures by NAME. Fetching every reservation to derive that also
      // delivered every guest's phone number and email to a page that renders
      // neither.
      APICall.getT("/hotel/reports/reservation_summary", { report_date: today }),
      APICall.getT("/masterdata/room"),
      APICall.getT("/restaurant/reports/daily_sales", { report_date: today }),
      APICall.getT("/bar/reports/daily_sales", { report_date: today }),
      // Hotel revenue comes from a DATED report, like the other two
      // departments. It used to be summed from the reservation list below,
      // which made the "today" in this card's headline untrue -- see the note
      // on hotelRevenue.
      APICall.getT("/hotel/reports/daily_sales", { report_date: today }),
    ]).then(([rRes, rRoom, rRestaurant, rBar, rHotelSales]) => {
      if (!mounted.current) return;

      const summary = rRes.status === "fulfilled" ? rRes.value?.data || null : null;
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

      // Counted by the server over the whole book.
      const arrivingToday = Number(summary?.arrivals_today) || 0;
      const departingToday = Number(summary?.departures_today) || 0;
      // WHAT THIS REPLACES
      //   `reservations.reduce((sum, r) => sum + r.overall_amount, 0)` -- the
      //   total of EVERY reservation ever booked, added to two figures that
      //   really were today's and displayed as "Revenue Today". It counted
      //   past and future stays alike, counted a whole stay against a single
      //   day, and counted cancelled bookings as earned. On this property it
      //   read 508,550 for a day whose arrivals were worth nothing, 11,760 of
      //   it from a booking that had been cancelled.
      const hotelRevenue =
        rHotelSales.status === "fulfilled"
          ? Number(rHotelSales.value?.data?.grand_total) || 0
          : 0;

      setHotel({
        revenue: hotelRevenue,
        occupancyPct: rooms.length > 0 ? (statusCounts.Occupied / rooms.length) * 100 : 0,
        occupiedRooms: statusCounts.Occupied,
        totalRooms: rooms.length,
        arrivingToday,
        departingToday,
        statusCounts,
      });

      // The server already selected today's arrivals and departures and
      // resolved each guest's display name, so there is nothing to filter here.
      const arrivals = (summary?.arrivals || []).map((r) => ({
        key: `arr-${r.id}`,
        name: r.guest_name || "Guest",
        type: "Arrival",
        status: r.reservation_status || "—",
      }));
      const departures = (summary?.departures || []).map((r) => ({
        key: `dep-${r.id}`,
        name: r.guest_name || "Guest",
        type: "Departure",
        status: r.reservation_status || "—",
      }));
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

  const tiles = [
    {
      key: "occupancy",
      label: "Hotel Occupancy",
      value: loading || !hotel ? null : `${Math.round(hotel.occupancyPct)}%`,
      note: hotel ? `${hotel.occupiedRooms} of ${hotel.totalRooms} rooms` : undefined,
      icon: BedDouble,
      accent: DEPT_ACCENT.hotel,
      tint: DEPT_TINT.hotel,
    },
    {
      key: "restaurant-orders",
      label: "Restaurant Orders",
      value: loading ? null : formatCount(restaurant?.orders),
      note: "Today",
      icon: ShoppingBag,
      accent: DEPT_ACCENT.restaurant,
      tint: DEPT_TINT.restaurant,
    },
    {
      key: "bar-orders",
      label: "Bar Orders",
      value: loading ? null : formatCount(bar?.orders),
      note: "Today",
      icon: Wine,
      accent: DEPT_ACCENT.bar,
      tint: DEPT_TINT.bar,
    },
    {
      key: "bills",
      label: "Total Bills",
      value: loading ? null : formatCount(combinedBills),
      note: "Restaurant + Bar",
      icon: Receipt,
      accent: "var(--warning-color)",
      tint: "var(--warning-light)",
    },
  ];

  const heroBreakdown = [
    { key: "hotel", label: "Hotel", value: hotel?.revenue || 0, dot: DEPT_ACCENT.hotel },
    { key: "restaurant", label: "Rest.", value: restaurant?.revenue || 0, dot: DEPT_ACCENT.restaurant },
    { key: "bar", label: "Bar", value: bar?.revenue || 0, dot: DEPT_ACCENT.bar },
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
    <div className="ov">
      {error && (
        <div className="ov-alert" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => setRefreshTick((n) => n + 1)}>
            Retry
          </button>
        </div>
      )}

      {/* KPI band — revenue hero + secondary tiles */}
      <div className="ov-kpis">
        <section className="ov-hero" role="group" aria-label={`Combined revenue today: ${loading ? "loading" : formatCurrency(combinedRevenue)}`}>
          <div className="ov-hero-top">
            <span className="ov-hero-label">Combined Revenue · Today</span>
            <span className="ov-hero-badge" aria-hidden="true"><DollarSign size={19} /></span>
          </div>
          <div>
            <div className="ov-hero-value" aria-live="polite">
              {loading ? (
                <span className="ov-skel" aria-hidden="true" />
              ) : (
                <><span className="ov-cur">₹</span>{formatCurrency(combinedRevenue)}</>
              )}
            </div>
            <dl className="ov-hero-breakdown">
              {heroBreakdown.map((seg) => (
                <div className="ov-hero-seg" key={seg.key} style={{ "--seg-dot": seg.dot }}>
                  <dt>{seg.label}</dt>
                  <dd>{loading ? "…" : `₹${formatCurrency(seg.value)}`}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {tiles.map((tile) => {
          const Icon = tile.icon;
          return (
            <div
              className="ov-tile"
              key={tile.key}
              role="group"
              aria-label={`${tile.label}: ${loading ? "loading" : tile.value}`}
              style={{ "--tile-accent": tile.accent, "--tile-tint": tile.tint }}
            >
              <div className="ov-tile-top">
                <span className="ov-tile-label">{tile.label}</span>
                <span className="ov-tile-icon" aria-hidden="true"><Icon size={18} /></span>
              </div>
              <div className="ov-tile-value" aria-live="polite">
                {loading ? <span className="ov-skel" aria-hidden="true" /> : tile.value}
              </div>
              {tile.note && !loading && <div className="ov-tile-note">{tile.note}</div>}
            </div>
          );
        })}
      </div>

      {/* Module summaries */}
      <div className="ov-grid">
        {modules.map((mod) => {
          const Icon = mod.icon;
          return (
            <div
              key={mod.key}
              className="card ov-module ov-span-2"
              style={{ "--mod-accent": DEPT_ACCENT[mod.key], "--mod-tint": DEPT_TINT[mod.key] }}
            >
              <div className="card-header-inline">
                <h4>
                  <span className="ov-module-icon" aria-hidden="true"><Icon size={16} /></span>
                  {mod.label}
                </h4>
              </div>
              {loading ? (
                <div className="dashboard-empty" role="status" aria-live="polite">Loading…</div>
              ) : (
                <>
                  <dl className="ov-module-stats">
                    {mod.stats.map((s) => (
                      <div key={s.label}>
                        <dt>{s.label}</dt>
                        <dd>{s.value}</dd>
                      </div>
                    ))}
                  </dl>
                  <button type="button" className="ov-module-link" onClick={() => onNavigate?.(mod.tabIndex)}>
                    View {mod.label} <ArrowRight size={14} aria-hidden="true" />
                  </button>
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* Revenue split + room availability */}
      <div className="ov-grid">
        <div className="ov-span-3">
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
        <div className="ov-span-3">
          <RoomAvailability
            counts={hotel?.statusCounts}
            total={hotel?.totalRooms || 0}
            loading={loading}
          />
        </div>
      </div>

      {/* Arrivals/departures + quick actions */}
      <div className="ov-grid">
        <div className="ov-span-4">
          <MiniTableCard
            title="Today's Arrivals & Departures"
            columns={guestColumns}
            rows={todayGuests || []}
            loading={loading}
            emptyMessage="No arrivals or departures scheduled for today."
            rowKey="key"
          />
        </div>
        <div className="card ov-span-2">
          <div className="card-header-inline">
            <h4>Quick Actions</h4>
          </div>
          <div className="ov-actions">
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
                  className="ov-action"
                  style={{ "--qa-accent": DEPT_ACCENT[action.key], "--qa-tint": DEPT_TINT[action.key] }}
                  onClick={() => navigate(action.path)}
                >
                  <span className="ov-action-icon" aria-hidden="true"><Icon size={16} /></span>
                  <span className="ov-action-label">{action.label}</span>
                  <ArrowRight size={14} className="ov-action-arrow" aria-hidden="true" />
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;

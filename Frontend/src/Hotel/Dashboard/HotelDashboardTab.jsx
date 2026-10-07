import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../Context/AuthContext";
import APICall from "../../APICalls/APICalls";
import { todayIso } from "../../functions/formatters";

import KPISection from "./Components/KPISection";
import BookingPlatform from "./Components/BookingPlatform";
import RoomAvailability from "./Components/RoomAvailability";
import TaskList from "./Components/TaskList";
import BookingTable from "./Components/BookingTable";
import RecentActivity from "./Components/RecentActivity";

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

const HotelDashboardTab = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [summary, setSummary] = useState(null); // null = loading
  const [rooms, setRooms] = useState(null);
  const [dailyRevenue, setDailyRevenue] = useState(0);
  const [activity, setActivity] = useState(null);
  // The signed-in staff member's housekeeping tasks — null until the call
  // settles, so the card can tell "still loading" from "there are none".
  const [tasks, setTasks] = useState(null);
  const [errors, setErrors] = useState({ reservations: null, rooms: null, activity: null, sales: null, tasks: null });
  const [refreshTick, setRefreshTick] = useState(0);

  // One value for "today", used by both dated report calls below. Use the
  // viewer's local calendar day; toISOString() can report yesterday during the
  // evening hours east of Greenwich.
  const today = todayIso();

  useEffect(() => {
    mounted.current = true;
    setSummary(null);
    setRooms(null);
    setActivity(null);
    setTasks(null);
    setErrors({ reservations: null, rooms: null, activity: null, sales: null, tasks: null });

    // No company_id is sent, and none is checked for.
    //
    // `user_activity_log` takes only from_date/to_date and reads company_id
    // from the verified token (nightauditController: "company_id now comes
    // from the verified token"). The parameter was therefore always ignored,
    // and the guard around it was worse than useless: rejecting the call when
    // the session's user object had no company_id turned a perfectly readable
    // log into a permanent "Failed to load activity" for that session.
    const activityCall = APICall.getT("/hotel/user_activity_log");

    Promise.allSettled([
      // A SUMMARY, not the whole book.
      //
      // This used to be `getT("/hotel/room_reservation")` -- every reservation
      // ever made, downloaded to derive three counts and a five-row panel. That
      // also handed this screen every guest's phone number and email, neither of
      // which it renders, so opening the Dashboard meant receiving a complete
      // guest contact list. The summary returns the counts and the rows this
      // page actually draws, and carries no contact details at all.
      APICall.getT("/hotel/reports/reservation_summary", { report_date: today }),
      APICall.getT("/masterdata/room"),
      activityCall,
      // Same correction as OverviewTab: revenue for a DAY, from the dated
      // report, rather than the sum of every reservation in the book.
      APICall.getT("/hotel/reports/daily_sales", { report_date: today }),
      // "My Tasks" is the signed-in staff member's own housekeeping rows.
      // The gateway maps this GET to /task_assign and /user_reserved_details
      // (rbac_map), so a role holding only the Dashboard is refused with a
      // 403 — that refusal is passed to the card to display, never swallowed
      // into an empty list that would read as "you have no work".
      APICall.getT("/hotel/housekeeper_tasks"),
    ]).then(([rRes, rRoom, rAct, rSales, rTasks]) => {
      if (!mounted.current) return;

      setSummary(rRes.status === "fulfilled" ? rRes.value?.data || null : null);
      setRooms(rRoom.status === "fulfilled" ? Array.isArray(rRoom.value?.data) ? rRoom.value.data : [] : []);
      setActivity(rAct.status === "fulfilled" ? rAct.value?.data || { room_activity: [], housekeeping_activity: [] } : { room_activity: [], housekeeping_activity: [] });
      setDailyRevenue(rSales.status === "fulfilled" ? Number(rSales.value?.data?.grand_total) || 0 : 0);
      setTasks(rTasks.status === "fulfilled" ? (Array.isArray(rTasks.value?.data) ? rTasks.value.data : []) : []);

      setErrors({
        reservations: rRes.status === "rejected" ? (rRes.reason?.message || "Failed to load bookings.") : null,
        rooms: rRoom.status === "rejected" ? (rRoom.reason?.message || "Failed to load rooms.") : null,
        activity: rAct.status === "rejected" ? (rAct.reason?.message || "Failed to load activity.") : null,
        sales: rSales.status === "rejected" ? (rSales.reason?.message || "Failed to load today's sales.") : null,
        tasks: rTasks.status === "rejected" ? (rTasks.reason?.message || "Failed to load your tasks.") : null,
      });
    });

    return () => { mounted.current = false; };
  }, [refreshTick, today]);


  const kpis = useMemo(() => {
    const roomList = rooms || [];

    // "Available" must mean sellable now, not merely unbooked. A room whose
    // housekeeping state is dirty/maintenance is shown as Not Ready in the
    // room-availability card and must not be counted as available here.
    const availableRooms = roomList.filter((r) => {
      const bs = String(r?.booking_status || "").toLowerCase();
      const ws = String(r?.working_status || "").toLowerCase();
      const notReady = ws === "maintenance" || ws === "out of order" || ws === "dirty" || ws === "not ready";
      return !notReady && (bs === "available" || bs === "");
    }).length;

    // Counted by the server across the whole book, not by filtering whatever
    // rows happened to be downloaded.
    const arrivingToday = Number(summary?.arrivals_today) || 0;
    const departingToday = Number(summary?.departures_today) || 0;
    const newBookingsToday = Number(summary?.new_bookings_today) || 0;
    // Revenue for TODAY, from the dated report -- not the sum of every
    // reservation in the book, which is what this used to be.
    const totalRevenue = dailyRevenue;

    return { availableRooms, arrivingToday, departingToday, newBookingsToday, totalRevenue };
  }, [summary, rooms, dailyRevenue]);

  const roomsByStatus = useMemo(() => {
    const roomList = rooms || [];
    const counts = { Occupied: 0, Reserved: 0, Available: 0, "Not Ready": 0 };
    for (const r of roomList) {
      const bs = String(r?.booking_status || "").toLowerCase();
      const ws = String(r?.working_status || "").toLowerCase();
      if (ws === "maintenance" || ws === "out of order" || ws === "dirty" || ws === "not ready") {
        counts["Not Ready"] += 1;
      } else if (bs === "occupied" || bs === "checked-in" || bs === "checkedin") {
        counts.Occupied += 1;
      } else if (bs === "reserved" || bs === "booked" || bs === "pending") {
        counts.Reserved += 1;
      } else {
        counts.Available += 1;
      }
    }
    return counts;
  }, [rooms]);

  const recentBookings = useMemo(
    () => summary?.recent_bookings || [],
    [summary],
  );

  const recentActivityItems = useMemo(() => {
    if (!activity) return [];
    const roomActs = (activity.room_activity || []).map((r) => ({
      key: `res-${r.id}`,
      title: `${r.first_name || ""} ${r.last_name || ""}`.trim() || "Guest",
      desc: `Room ${r.room_no || "—"} · ${r.booking_status || "Reservation"}`,
      time: isoDay(r.arrival_date) || "",
      kind: "primary",
    }));
    const keeperActs = (activity.housekeeping_activity || []).map((k) => ({
      key: `hsk-${k.id}`,
      title: `${k.task_type || "Housekeeping task"}`,
      desc: `${k.employee_name || "Staff"} · Room ${k.room_no || "—"} · ${k.task_status || ""}`.replace(/\s·\s$/, ""),
      time: "",
      kind: "success",
    }));
    return [...roomActs, ...keeperActs].slice(0, 8);
  }, [activity]);

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(" ");
  const displayName = (
    fullName ||
    user?.name ||
    user?.username ||
    user?.role_name ||
    "User"
  );

  const handleRefresh = () => setRefreshTick((n) => n + 1);
  const handleAddBooking = () => navigate("/add_new_reservation");

  const anyLoading = summary === null || rooms === null || activity === null || tasks === null;

  return (
    <div className="dashboard-wrapper container-fluid" aria-busy={anyLoading}>
      <div className="row mb-4">
        <div className="col-12">
          <KPISection
            displayName={displayName}
            kpis={kpis}
            loading={summary === null || rooms === null}
            error={errors.reservations || errors.rooms || errors.sales}
            onAddBooking={handleAddBooking}
            onRefresh={handleRefresh}
          />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-4">
          <BookingPlatform />
        </div>
        <div className="dashboard-col dashboard-col-4">
          <RoomAvailability
            counts={roomsByStatus}
            total={(rooms || []).length}
            loading={rooms === null}
            error={errors.rooms}
          />
        </div>
        <div className="dashboard-col dashboard-col-4">
          <TaskList
            tasks={tasks || []}
            userId={user?.id}
            loading={tasks === null}
            error={errors.tasks}
          />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-8">
          <div className="booking-list-wrap full-height">
            <BookingTable
              bookings={recentBookings}
              loading={summary === null}
              error={errors.reservations}
              onViewAll={() => navigate("/reservation")}
              onRowClick={(booking) =>
                navigate(`/ReservationView?reservationId=${encodeURIComponent(booking.id)}`, {
                  state: { reservationId: booking.id },
                })
              }
            />
          </div>
        </div>
        <div className="dashboard-col dashboard-col-4">
          <div className="recent-activity-wrap full-height">
            <RecentActivity
              items={recentActivityItems}
              loading={activity === null}
              error={errors.activity}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default HotelDashboardTab;

import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

import { useAuth } from "../../Context/AuthContext";
import APICall, { ApiError } from "../../APICalls/APICalls";

import KPISection from "./Components/KPISection";
import BookingPlatform from "./Components/BookingPlatform";
import RoomAvailability from "./Components/RoomAvailability";
import TaskList from "./Components/TaskList";
import BookingTable from "./Components/BookingTable";
import RecentActivity from "./Components/RecentActivity";

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

const AdminDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [reservations, setReservations] = useState(null); // null = loading
  const [rooms, setRooms] = useState(null);
  const [activity, setActivity] = useState(null);
  const [errors, setErrors] = useState({ reservations: null, rooms: null, activity: null });
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    mounted.current = true;
    setReservations(null);
    setRooms(null);
    setActivity(null);
    setErrors({ reservations: null, rooms: null, activity: null });

    const companyId = user?.company_id;
    const activityCall = companyId
      ? APICall.getT("/hotel/user_activity_log", { company_id: companyId })
      : Promise.reject(new ApiError("Company context unavailable.", { status: 0, code: "no_company" }));

    Promise.allSettled([
      APICall.getT("/hotel/room_reservation"),
      APICall.getT("/masterdata/room"),
      activityCall,
    ]).then(([rRes, rRoom, rAct]) => {
      if (!mounted.current) return;

      setReservations(rRes.status === "fulfilled" ? Array.isArray(rRes.value?.data) ? rRes.value.data : [] : []);
      setRooms(rRoom.status === "fulfilled" ? Array.isArray(rRoom.value?.data) ? rRoom.value.data : [] : []);
      setActivity(rAct.status === "fulfilled" ? rAct.value?.data || { room_activity: [], housekeeping_activity: [] } : { room_activity: [], housekeeping_activity: [] });

      setErrors({
        reservations: rRes.status === "rejected" ? (rRes.reason?.message || "Failed to load bookings.") : null,
        rooms: rRoom.status === "rejected" ? (rRoom.reason?.message || "Failed to load rooms.") : null,
        activity: rAct.status === "rejected" ? (rAct.reason?.message || "Failed to load activity.") : null,
      });
    });

    return () => { mounted.current = false; };
  }, [user?.company_id, refreshTick]);

  const today = isoDay(new Date().toISOString());

  const kpis = useMemo(() => {
    const rList = reservations || [];
    const roomList = rooms || [];

    const availableRooms = roomList.filter((r) => {
      const bs = String(r?.booking_status || "").toLowerCase();
      return bs === "available" || bs === "";
    }).length;

    const arrivingToday = rList.filter((r) => isoDay(r?.arrival_date) === today).length;
    const departingToday = rList.filter((r) => isoDay(r?.departure_date) === today).length;
    const newBookingsToday = rList.filter((r) => isoDay(r?.created_at) === today).length;
    const totalRevenue = rList.reduce((sum, r) => {
      const v = Number(r?.overall_amount);
      return Number.isFinite(v) ? sum + v : sum;
    }, 0);

    return { availableRooms, arrivingToday, departingToday, newBookingsToday, totalRevenue };
  }, [reservations, rooms, today]);

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
    () => (reservations || []).slice(0, 5),
    [reservations],
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

  const displayName = (
    user?.name ||
    user?.username ||
    user?.first_name ||
    user?.email ||
    user?.company_email ||
    "back"
  );

  const handleRefresh = () => setRefreshTick((n) => n + 1);
  const handleAddBooking = () => navigate("/add_new_reservation");

  const anyLoading = reservations === null || rooms === null || activity === null;

  return (
    <div className="dashboard-wrapper container-fluid" aria-busy={anyLoading}>
      <div className="row mb-4">
        <div className="col-12">
          <KPISection
            displayName={displayName}
            kpis={kpis}
            loading={reservations === null || rooms === null}
            error={errors.reservations || errors.rooms}
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
          <TaskList />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-8">
          <div className="booking-list-wrap full-height">
            <BookingTable
              bookings={recentBookings}
              loading={reservations === null}
              error={errors.reservations}
              onViewAll={() => navigate("/reservation")}
              onRowClick={(booking) =>
                navigate("/ReservationView", { state: { reservationId: booking.id } })
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

export default AdminDashboard;

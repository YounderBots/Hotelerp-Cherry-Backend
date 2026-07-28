import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Building2,
  X,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import APICall, { ApiError, baseURL } from "../../APICalls/APICalls";
import "./Reservation.css";

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

// Normalise the room's booking + working status into a canonical bucket.
// Aligns with Page 6's Room Availability heuristic (Occupied / Reserved / Available / Not Ready).
const bucketOf = (room) => {
  const bs = String(room?.booking_status || "").toLowerCase();
  const ws = String(room?.working_status || "").toLowerCase();
  if (ws === "maintenance" || ws === "out of order" || ws === "dirty" || ws === "not ready") return "not_ready";
  if (bs === "occupied" || bs === "checked-in" || bs === "checkedin" || bs === "arrived") return "occupied";
  if (bs === "reserved" || bs === "booked" || bs === "pending" || bs === "confirmed") return "reserved";
  return "available";
};

const BUCKET_LABEL = {
  available: "Available",
  reserved: "Reserved",
  occupied: "Occupied",
  not_ready: "Not Ready",
};

const BUCKET_CLASS = {
  available: "status-available",
  reserved: "status-reserved",
  occupied: "status-occupied",
  not_ready: "status-not-ready",
};

// Image path resolver — backend stores as "/templates/static/upload_image/xxx.jpg".
// If it's already an absolute URL, use as-is; otherwise prefix with the API baseURL.
const resolveImage = (path) => {
  if (!path || typeof path !== "string") return null;
  if (/^https?:\/\//i.test(path)) return path;
  return `${baseURL}${path.startsWith("/") ? "" : "/"}${path}`;
};

const RoomView = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [rooms, setRooms] = useState(null); // null = loading
  const [roomTypes, setRoomTypes] = useState([]);
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  const [activeTab, setActiveTab] = useState("all");
  const [activeRoom, setActiveRoom] = useState(null);

  useEffect(() => {
    mounted.current = true;
    setRooms(null);
    setError(null);

    Promise.allSettled([
      APICall.getT("/masterdata/room"),
      APICall.getT("/masterdata/room_types"),
    ]).then(([rRoom, rRT]) => {
      if (!mounted.current) return;
      setRooms(rRoom.status === "fulfilled" ? readList(rRoom.value) : []);
      setRoomTypes(rRT.status === "fulfilled" ? readList(rRT.value) : []);
      const errs = [];
      if (rRoom.status === "rejected") errs.push(errMsg(rRoom.reason, "rooms"));
      if (rRT.status === "rejected") errs.push(errMsg(rRT.reason, "room types"));
      setError(errs.length ? `Failed to load: ${errs.join(", ")}` : null);
    });

    return () => { mounted.current = false; };
  }, [refreshTick]);

  // Close modal on Escape
  useEffect(() => {
    if (!activeRoom) return undefined;
    const onKey = (e) => { if (e.key === "Escape") setActiveRoom(null); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [activeRoom]);

  // Body scroll lock while modal is open
  useEffect(() => {
    if (!activeRoom) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [activeRoom]);

  const roomTypeName = useCallback(
    (id) => roomTypes.find((rt) => rt.id === Number(id))?.room_type_name || "—",
    [roomTypes],
  );

  const counts = useMemo(() => {
    const list = rooms || [];
    const c = { all: list.length, available: 0, reserved: 0, occupied: 0, not_ready: 0 };
    for (const r of list) {
      const b = bucketOf(r);
      c[b] = (c[b] || 0) + 1;
    }
    return c;
  }, [rooms]);

  const filteredRooms = useMemo(() => {
    const list = rooms || [];
    if (activeTab === "all") return list;
    return list.filter((r) => bucketOf(r) === activeTab);
  }, [rooms, activeTab]);

  const isLoading = rooms === null;

  const handleBack = () => navigate("/reservation");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const activeRoomImage = activeRoom
    ? resolveImage(activeRoom.images?.image_1 || activeRoom.images?.image_2 || activeRoom.images?.image_3 || activeRoom.images?.image_4)
    : null;
  const activeRoomBucket = activeRoom ? bucketOf(activeRoom) : null;

  return (
    <div className="rvw-page">
      <div className="rvw-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to reservations"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="rvw-header">
          <span className="rmv-eyebrow">Room</span>
          <h1 className="rmv-title">Room View</h1>
        </div>
        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleRefresh}
            aria-label="Refresh rooms"
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

      {/* Status tab filters */}
      <div className="rvw-tabs" role="tablist" aria-label="Filter rooms by status">
        {[
          { key: "all", label: "All" },
          { key: "available", label: "Available" },
          { key: "reserved", label: "Reserved" },
          { key: "occupied", label: "Occupied" },
          { key: "not_ready", label: "Not Ready" },
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
          Loading rooms…
        </div>
      )}

      {!isLoading && (rooms || []).length === 0 && !error && (
        <div className="rmv-empty">
          No rooms configured. Add rooms under <b>Master Data → Rooms</b>.
        </div>
      )}

      {!isLoading && filteredRooms.length === 0 && (rooms || []).length > 0 && (
        <div className="rmv-empty inline">
          No rooms in this category.
        </div>
      )}

      {!isLoading && filteredRooms.length > 0 && (
        <div className="rvw-grid">
          {filteredRooms.map((room) => {
            const bucket = bucketOf(room);
            const img = resolveImage(room.images?.image_1);
            return (
              <button
                type="button"
                key={room.id}
                className="rvw-card"
                onClick={() => setActiveRoom(room)}
                aria-label={`Room ${room.room_no} — ${BUCKET_LABEL[bucket]}`}
              >
                <div className={`rvw-status-chip ${BUCKET_CLASS[bucket]}`}>
                  {BUCKET_LABEL[bucket]}
                </div>

                <div className="rvw-thumb" aria-hidden="true">
                  {img ? (
                    <img
                      src={img}
                      alt=""
                      loading="lazy"
                      onError={(e) => { e.currentTarget.style.display = "none"; }}
                    />
                  ) : (
                    <Building2 size={40} aria-hidden="true" />
                  )}
                </div>

                <div className="rvw-body">
                  <div className="rvw-body-row">
                    <h4 className="rvw-room-name">{room.room_name || "Room"}</h4>
                    <span className="rvw-room-no">#{room.room_no}</span>
                  </div>
                  <div className="rvw-room-type">
                    {roomTypeName(room.room_type_id)}
                  </div>
                  <div className="rvw-capacity">
                    Max {room.max_adult ?? 0} adults · {room.max_child ?? 0} children
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {activeRoom && (
        <div
          className="room-image-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="rvw-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget) setActiveRoom(null); }}
        >
          <div className="room-image-modal">
            <button
              type="button"
              className="room-image-close"
              onClick={() => setActiveRoom(null)}
              aria-label="Close room details"
            >
              <X size={18} aria-hidden="true" />
            </button>

            <div className="rvw-modal-thumb">
              {activeRoomImage ? (
                <img
                  src={activeRoomImage}
                  alt={`Room ${activeRoom.room_no}`}
                  onError={(e) => { e.currentTarget.style.display = "none"; }}
                />
              ) : (
                <Building2 size={80} aria-hidden="true" />
              )}
            </div>

            <div className="room-image-info">
              <h4 id="rvw-modal-title">{activeRoom.room_name || "Room"}</h4>
              <p>Room No: <b>#{activeRoom.room_no}</b></p>
              <span className="rvw-modal-type">{roomTypeName(activeRoom.room_type_id)}</span>
              <div className={`rvw-status-chip ${BUCKET_CLASS[activeRoomBucket]}`} style={{ marginTop: "0.5rem" }}>
                {BUCKET_LABEL[activeRoomBucket]}
              </div>
              <ul className="rvw-modal-meta">
                <li><span>Max adults</span><b>{activeRoom.max_adult ?? 0}</b></li>
                <li><span>Max children</span><b>{activeRoom.max_child ?? 0}</b></li>
                {activeRoom.room_telephone && (
                  <li><span>Room phone</span><b>{activeRoom.room_telephone}</b></li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoomView;

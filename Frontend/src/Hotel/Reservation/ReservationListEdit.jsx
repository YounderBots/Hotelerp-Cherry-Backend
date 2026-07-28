import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Save, Trash2, AlertCircle, CheckCircle, X } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import Tabs, { Tab } from "../../stories/Tabs";
import RoomCard from "./Pages/Card";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./Reservation.css";

// Backend reservation_status vocabulary (shared with Reservation.jsx).
const RESERVATION_STATUSES = ["Pending", "Confirmed", "Arrived", "Departures", "Cancelled"];
const LOCKED_STATUSES = new Set(["Arrived", "Departures", "Cancelled"]);

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");
const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

const parseArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v === null || v === undefined || v === "") return [];
  try {
    const p = JSON.parse(v);
    return Array.isArray(p) ? p : [];
  } catch {
    return [];
  }
};

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const readOne = (res) =>
  res?.data && !Array.isArray(res.data) && typeof res.data === "object" ? res.data : null;

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const roomTypeLabel = (t) => t?.room_type_name || t?.room_type || `#${t?.id}`;

const Toast = ({ toast, onClose }) => {
  if (!toast) return null;
  const Icon = toast.kind === "success" ? CheckCircle : AlertCircle;
  return (
    <div
      className={`reservation-toast ${toast.kind}`}
      role={toast.kind === "success" ? "status" : "alert"}
      aria-live={toast.kind === "success" ? "polite" : "assertive"}
    >
      <Icon size={18} aria-hidden="true" />
      <span>{toast.text}</span>
      <button
        type="button"
        className="reservation-toast-close"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        <X size={14} aria-hidden="true" />
      </button>
    </div>
  );
};

const ReservationListEdit = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const mounted = useRef(true);

  const bootstrapReservation = location.state?.reservation || null;
  const reservationId = bootstrapReservation?.id || location.state?.reservationId || null;

  const [reservation, setReservation] = useState(bootstrapReservation);
  const [reservationError, setReservationError] = useState(null);
  const [reservationLoading, setReservationLoading] = useState(!bootstrapReservation && Boolean(reservationId));

  const [roomTypes, setRoomTypes] = useState([]);
  const [roomsData, setRoomsData] = useState([]);
  const [masterError, setMasterError] = useState(null);

  const [selectedRoomIds, setSelectedRoomIds] = useState([]); // ordered ints
  const [perRoom, setPerRoom] = useState({}); // { [roomId]: { adults, children, complementary, extraBed, extraBedCost, rateType } }

  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [toast, setToast] = useState(null);

  const [dates, setDates] = useState({
    arrival_date: "",
    departure_date: "",
    reservation_status: "",
  });

  const showToast = useCallback((kind, text) => setToast({ kind, text, at: Date.now() }), []);

  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  // --------------------------------------------------------------------
  // Load masterdata
  // --------------------------------------------------------------------
  useEffect(() => {
    mounted.current = true;
    Promise.allSettled([
      APICall.getT("/masterdata/room_types"),
      APICall.getT("/masterdata/room"),
    ]).then(([rRT, rRoom]) => {
      if (!mounted.current) return;
      if (rRT.status === "fulfilled") setRoomTypes(readList(rRT.value));
      if (rRoom.status === "fulfilled") setRoomsData(readList(rRoom.value));
      const errs = [];
      if (rRT.status === "rejected") errs.push(errMsg(rRT.reason, "room types"));
      if (rRoom.status === "rejected") errs.push(errMsg(rRoom.reason, "rooms"));
      setMasterError(errs.length ? `Failed to load: ${errs.join(", ")}` : null);
    });
    return () => { mounted.current = false; };
  }, []);

  // --------------------------------------------------------------------
  // Load reservation if we only got an id from the caller (or via URL).
  // --------------------------------------------------------------------
  useEffect(() => {
    if (!reservationId || bootstrapReservation) return undefined;
    setReservationLoading(true);
    setReservationError(null);
    APICall.getT(`/hotel/room_reservation/${encodeURIComponent(reservationId)}`)
      .then((res) => {
        if (!mounted.current) return;
        const one = readOne(res);
        if (!one) {
          setReservationError("Reservation response was malformed.");
          setReservation(null);
        } else {
          setReservation(one);
        }
      })
      .catch((err) => {
        if (!mounted.current) return;
        setReservationError(errMsg(err, "Failed to load reservation."));
      })
      .finally(() => {
        if (mounted.current) setReservationLoading(false);
      });
  }, [reservationId, bootstrapReservation]);

  // --------------------------------------------------------------------
  // Hydrate local editable state once the reservation is available.
  // --------------------------------------------------------------------
  useEffect(() => {
    if (!reservation) return;
    setDates({
      arrival_date: isoDay(reservation.arrival_date),
      departure_date: isoDay(reservation.departure_date),
      reservation_status: reservation.reservation_status || "",
    });
    const seedIds = parseArr(reservation.room_ids).map((v) => Number(v)).filter(Number.isFinite);
    const seedRates = parseArr(reservation.rate_type);
    setSelectedRoomIds(seedIds);
    const seeded = {};
    seedIds.forEach((rid, i) => {
      seeded[rid] = {
        adults: num(reservation.no_of_adults) || 1,
        children: num(reservation.no_of_children),
        complementary: reservation.room_complementary || "",
        extraBed: 0,
        extraBedCost: 0,
        rateType: seedRates[i] || "daily",
      };
    });
    setPerRoom(seeded);
  }, [reservation]);

  const totalNights = useMemo(() => {
    if (!dates.arrival_date || !dates.departure_date) return 0;
    const a = new Date(dates.arrival_date);
    const d = new Date(dates.departure_date);
    if (Number.isNaN(a.getTime()) || Number.isNaN(d.getTime())) return 0;
    const ms = d.getTime() - a.getTime();
    if (ms <= 0) return 0;
    return Math.round(ms / (1000 * 60 * 60 * 24));
  }, [dates.arrival_date, dates.departure_date]);

  // --------------------------------------------------------------------
  // Room selection
  // --------------------------------------------------------------------
  const handleRoomSelect = (room) => {
    if (!room?.id) return;
    setSelectedRoomIds((prev) => {
      const exists = prev.includes(room.id);
      if (exists) {
        return prev.filter((id) => id !== room.id);
      }
      // Seed default per-room settings for a newly selected room.
      setPerRoom((prevMap) => ({
        ...prevMap,
        [room.id]: prevMap[room.id] || {
          adults: 1,
          children: 0,
          complementary: "",
          extraBed: 0,
          extraBedCost: 0,
          rateType: "daily",
        },
      }));
      return [...prev, room.id];
    });
  };

  const handleRemoveSelectedRoom = (roomId) => {
    setSelectedRoomIds((prev) => prev.filter((id) => id !== roomId));
    setPerRoom((prevMap) => {
      const next = { ...prevMap };
      delete next[roomId];
      return next;
    });
  };

  const isRoomSelected = (room) => selectedRoomIds.includes(room.id);

  const updateRoomField = (roomId, field, value) => {
    setPerRoom((prev) => ({
      ...prev,
      [roomId]: { ...(prev[roomId] || {}), [field]: value },
    }));
  };

  // --------------------------------------------------------------------
  // Save (PUT /hotel/room_reservation as FormData)
  // --------------------------------------------------------------------
  const validate = () => {
    if (!reservation?.id) return "Missing reservation reference.";
    if (!dates.arrival_date || !dates.departure_date) return "Arrival and departure dates are required.";
    if (isoDay(dates.arrival_date) > isoDay(dates.departure_date)) return "Departure must be on or after arrival.";
    if (!RESERVATION_STATUSES.includes(dates.reservation_status)) {
      return `Reservation status must be one of: ${RESERVATION_STATUSES.join(", ")}`;
    }
    if (selectedRoomIds.length === 0) return "Select at least one room.";
    for (const id of selectedRoomIds) {
      const p = perRoom[id] || {};
      if (num(p.adults) < 1) return `Adults must be at least 1 for room ${roomsData.find((r) => r.id === id)?.room_no || id}.`;
      if (num(p.children) < 0) return "Children count cannot be negative.";
      if (num(p.extraBed) < 0) return "Extra bed count cannot be negative.";
      if (num(p.extraBedCost) < 0) return "Extra bed cost cannot be negative.";
    }
    return null;
  };

  const handleSave = async () => {
    const v = validate();
    if (v) { setSaveError(v); showToast("error", v); return; }
    setSaveError(null);
    setSaving(true);
    try {
      const roomTypeIds = selectedRoomIds
        .map((rid) => Number(roomsData.find((r) => r.id === rid)?.room_type_id))
        .filter(Number.isFinite);
      const rateTypes = selectedRoomIds.map((rid) => perRoom[rid]?.rateType || "daily");
      const totalAdults = selectedRoomIds.reduce((s, rid) => s + num(perRoom[rid]?.adults), 0);
      const totalChildren = selectedRoomIds.reduce((s, rid) => s + num(perRoom[rid]?.children), 0);
      const totalExtraBed = selectedRoomIds.reduce((s, rid) => s + num(perRoom[rid]?.extraBed), 0);
      const totalExtraBedCost = selectedRoomIds.reduce(
        (s, rid) => s + num(perRoom[rid]?.extraBed) * num(perRoom[rid]?.extraBedCost),
        0,
      );

      const fd = new FormData();
      const setField = (k, val) => {
        if (val === undefined || val === null) return;
        fd.append(k, typeof val === "object" ? JSON.stringify(val) : String(val));
      };

      // Preserve every existing scalar we're not editing (backend expects a full form).
      Object.entries(reservation).forEach(([k, v2]) => {
        if (v2 === undefined || v2 === null) return;
        setField(k, v2);
      });

      // Overwrite the fields this page controls.
      fd.set("id", String(reservation.id));
      fd.set("arrival_date", dates.arrival_date);
      fd.set("departure_date", dates.departure_date);
      fd.set("no_of_nights", String(totalNights || num(reservation.no_of_nights)));
      fd.set("reservation_status", dates.reservation_status);
      fd.set("room_ids", JSON.stringify(selectedRoomIds));
      fd.set("room_type_ids", JSON.stringify(roomTypeIds));
      fd.set("rate_type", JSON.stringify(rateTypes));
      fd.set("no_of_rooms", String(selectedRoomIds.length || 1));
      fd.set("no_of_adults", String(totalAdults || 1));
      fd.set("no_of_children", String(totalChildren));
      fd.set("extra_bed_count", String(totalExtraBed));
      fd.set("extra_bed_cost", String(totalExtraBedCost));

      await APICall.putT("/hotel/room_reservation", fd);
      showToast("success", "Reservation updated.");
    } catch (err) {
      const m = errMsg(err, "Failed to update reservation.");
      setSaveError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  // --------------------------------------------------------------------
  // Derived table rows
  // --------------------------------------------------------------------
  const selectedRoomsRows = useMemo(() => {
    return selectedRoomIds.map((rid) => {
      const room = roomsData.find((r) => r.id === rid);
      const type = roomTypes.find((rt) => rt.id === Number(room?.room_type_id));
      const p = perRoom[rid] || {};
      return {
        id: rid,
        roomCategory: roomTypeLabel(type),
        roomNo: room?.room_no || `#${rid}`,
        adults: p.adults ?? 1,
        children: p.children ?? 0,
        complementary: p.complementary || "",
        extraBed: p.extraBed ?? 0,
        extraBedCost: p.extraBedCost ?? 0,
        amount: num(p.extraBed) * num(p.extraBedCost),
      };
    });
  }, [selectedRoomIds, perRoom, roomsData, roomTypes]);

  const isLocked = reservation && LOCKED_STATUSES.has(reservation.reservation_status);

  // --------------------------------------------------------------------
  // Render
  // --------------------------------------------------------------------
  if (!reservationId && !bootstrapReservation) {
    return (
      <div className="rle-page">
        <div className="rle-toolbar">
          <button
            type="button"
            className="rmv-back-btn"
            onClick={() => navigate("/reservation")}
            aria-label="Back to reservations"
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>Back to reservations</span>
          </button>
        </div>
        <div className="rmv-empty" role="alert">
          <AlertCircle size={18} aria-hidden="true" />
          <span>No reservation was selected. Open a reservation from the list.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="rle-page">
      <div className="rle-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={() => navigate("/reservation")}
          aria-label="Back to reservations"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>

        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn primary"
            onClick={handleSave}
            disabled={saving || reservationLoading || isLocked}
            aria-busy={saving}
            aria-label="Save reservation"
          >
            <Save size={16} aria-hidden="true" />
            <span>{saving ? "Saving…" : "Save changes"}</span>
          </button>
        </div>
      </div>

      {reservationError && (
        <div className="rmv-alert" role="alert">
          <span>{reservationError}</span>
        </div>
      )}
      {masterError && (
        <div className="rmv-alert" role="alert">
          <span>{masterError}</span>
        </div>
      )}
      {saveError && (
        <div className="rmv-alert" role="alert">
          <span>{saveError}</span>
        </div>
      )}
      {isLocked && (
        <div className="rmv-empty" role="alert">
          This reservation is <b>{reservation.reservation_status}</b> and can no longer be edited here.
        </div>
      )}

      {reservationLoading && (
        <div className="rmv-loading" role="status" aria-live="polite">
          Loading reservation…
        </div>
      )}

      {reservation && (
        <div className="rle-header">
          <div>
            <span className="rmv-eyebrow">Editing</span>
            <h1 className="rmv-title">
              Reservation #{reservation.room_reservation_id}
            </h1>
          </div>
        </div>
      )}

      <div className="split-container rle-split">
        <div className="left">
          {roomTypes.length === 0 ? (
            <div className="rmv-loading" role="status" aria-live="polite">
              Loading room types…
            </div>
          ) : (
            <Tabs variant="default">
              {roomTypes.map((type) => {
                const filteredRooms = roomsData.filter(
                  (room) => Number(room.room_type_id) === type.id,
                );
                return (
                  <Tab key={type.id} label={roomTypeLabel(type)}>
                    <h3 className="rle-tab-title">{roomTypeLabel(type)} Rooms</h3>
                    {filteredRooms.length === 0 ? (
                      <p className="rle-empty-cat">No rooms available in this category.</p>
                    ) : (
                      <div className="rle-room-grid">
                        {filteredRooms.map((room) => (
                          <RoomCard
                            key={room.id}
                            room={room}
                            isSelected={isRoomSelected(room)}
                            onSelect={handleRoomSelect}
                          />
                        ))}
                      </div>
                    )}
                  </Tab>
                );
              })}
            </Tabs>
          )}
        </div>

        <div className="right">
          <div className="top-div">
            <div className="field">
              <label htmlFor="rle-arrival">Arrival Date</label>
              <input
                id="rle-arrival"
                type="date"
                value={dates.arrival_date}
                onChange={(e) => setDates((d) => ({ ...d, arrival_date: e.target.value }))}
                disabled={isLocked}
              />
            </div>

            <div className="field">
              <label htmlFor="rle-departure">Departure Date</label>
              <input
                id="rle-departure"
                type="date"
                value={dates.departure_date}
                onChange={(e) => setDates((d) => ({ ...d, departure_date: e.target.value }))}
                min={dates.arrival_date || undefined}
                disabled={isLocked}
              />
            </div>

            <div className="field">
              <label htmlFor="rle-nights">Total nights</label>
              <input
                id="rle-nights"
                type="number"
                value={totalNights}
                readOnly
                aria-readonly="true"
              />
            </div>

            <div className="field">
              <label htmlFor="rle-status">Status</label>
              <select
                id="rle-status"
                value={dates.reservation_status}
                onChange={(e) => setDates((d) => ({ ...d, reservation_status: e.target.value }))}
                disabled={isLocked}
              >
                <option value="">— select —</option>
                {RESERVATION_STATUSES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <TableTemplate
            title="Selected rooms"
            columns={[
              { key: "roomCategory", title: "Room Category", align: "center" },
              { key: "roomNo", title: "Room No", align: "center" },
              {
                key: "adults",
                title: "Adults",
                align: "center",
                render: (row) => (
                  <input
                    type="number"
                    min="1"
                    value={row.adults}
                    onChange={(e) => updateRoomField(row.id, "adults", e.target.value)}
                    className="rle-inline-input"
                    aria-label={`Adults in room ${row.roomNo}`}
                    disabled={isLocked}
                  />
                ),
              },
              {
                key: "children",
                title: "Children",
                align: "center",
                render: (row) => (
                  <input
                    type="number"
                    min="0"
                    value={row.children}
                    onChange={(e) => updateRoomField(row.id, "children", e.target.value)}
                    className="rle-inline-input"
                    aria-label={`Children in room ${row.roomNo}`}
                    disabled={isLocked}
                  />
                ),
              },
              {
                key: "complementary",
                title: "Complementary",
                align: "center",
                render: (row) => (
                  <input
                    type="text"
                    value={row.complementary}
                    onChange={(e) => updateRoomField(row.id, "complementary", e.target.value)}
                    className="rle-inline-input wider"
                    aria-label={`Complementary for room ${row.roomNo}`}
                    maxLength={100}
                    disabled={isLocked}
                  />
                ),
              },
              {
                key: "extraBed",
                title: "Extra Bed",
                align: "center",
                render: (row) => (
                  <input
                    type="number"
                    min="0"
                    value={row.extraBed}
                    onChange={(e) => updateRoomField(row.id, "extraBed", e.target.value)}
                    className="rle-inline-input"
                    aria-label={`Extra bed count for room ${row.roomNo}`}
                    disabled={isLocked}
                  />
                ),
              },
              {
                key: "extraBedCost",
                title: "Bed Cost",
                align: "center",
                render: (row) => (
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={row.extraBedCost}
                    onChange={(e) => updateRoomField(row.id, "extraBedCost", e.target.value)}
                    className="rle-inline-input"
                    aria-label={`Extra bed cost for room ${row.roomNo}`}
                    disabled={isLocked}
                  />
                ),
              },
              {
                key: "amount",
                title: "Amount",
                align: "center",
                render: (row) => row.amount.toFixed(2),
              },
              {
                key: "action",
                title: "Action",
                align: "center",
                type: "custom",
                render: (row) => (
                  <button
                    type="button"
                    className="table-action-btn delete"
                    onClick={() => handleRemoveSelectedRoom(row.id)}
                    aria-label={`Remove room ${row.roomNo}`}
                    disabled={isLocked}
                  >
                    <Trash2 size={16} aria-hidden="true" />
                  </button>
                ),
              },
            ]}
            data={selectedRoomsRows}
          />

          {selectedRoomsRows.length === 0 && (
            <div className="rmv-empty inline">
              No rooms selected. Pick one or more rooms from the left panel.
            </div>
          )}
        </div>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default ReservationListEdit;

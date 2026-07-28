import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, AlertCircle, CheckCircle, X } from "lucide-react";
import Tabs, { Tab } from "../../stories/Tabs";
import Modal from "../../stories/Modal";
import Button from "../../stories/Button";
import RoomCard from "./Pages/Card";
import Payment from "./payment";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./Reservation.css";

const SALUTATIONS = ["Mr.", "Mrs.", "Ms.", "Mx.", "Dr.", "Prof."];
const RATE_TYPES = [
  { value: "daily", label: "Daily Rate" },
  { value: "weekly", label: "Weekly Rate" },
  { value: "bed_only", label: "Bed Only" },
  { value: "bed_breakfast", label: "Bed & Breakfast" },
  { value: "half_board", label: "Half Board" },
  { value: "full_board", label: "Full Board" },
];
const ROOM_COMPLEMENTARY_OPTIONS = [
  "",
  "Breakfast",
  "Welcome Drink",
  "Lunch",
  "Dinner",
];
const COMMON_COMPLEMENTARY_OPTIONS = [
  "",
  "Welcome Drink",
  "Airport Pickup",
  "Late Checkout",
  "Spa Voucher",
];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+()\-\s\d]{7,20}$/;
const MAX_FILE_MB = 5;
const ALLOWED_FILE_EXT = ["pdf", "jpg", "jpeg", "png"];

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");
const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const roomTypeLabel = (t) => t?.room_type_name || t?.room_type || `#${t?.id}`;

const nightsBetween = (start, end) => {
  if (!start || !end) return 0;
  const a = new Date(start);
  const d = new Date(end);
  if (Number.isNaN(a.getTime()) || Number.isNaN(d.getTime())) return 0;
  const ms = d.getTime() - a.getTime();
  if (ms <= 0) return 0;
  return Math.round(ms / (1000 * 60 * 60 * 24));
};

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

const RoomGrid = ({ rooms, isSelected, onSelect }) => (
  <div className="anr-room-grid">
    {rooms.length === 0 ? (
      <p className="anr-empty-cat">No rooms available in this category.</p>
    ) : (
      rooms.map((room) => (
        <RoomCard
          key={room.id}
          room={room}
          isSelected={isSelected(room)}
          onSelect={onSelect}
        />
      ))
    )}
  </div>
);

const AddNewReservation = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [modalView, setModalView] = useState(false);
  const [paymentModal, setPaymentModal] = useState(false);

  const [identityTypes, setIdentityTypes] = useState([]);
  const [roomsData, setRoomsData] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [taxTypes, setTaxTypes] = useState([]);
  const [discountTypes, setDiscountTypes] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [reservationStatusTypes, setReservationStatusTypes] = useState([]);
  const [masterError, setMasterError] = useState(null);

  // Room selection state
  const [selectedRoomIds, setSelectedRoomIds] = useState([]); // ordered ints
  const [perRoom, setPerRoom] = useState({}); // { [roomId]: { adults, children, rateType, complementary } }

  // Reservation form
  const [formData, setFormData] = useState({
    salutation: "Mr.",
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    arrival_date: "",
    departure_date: "",
    booking_status_id: "",
    identity_type_id: "",
    common_complementary: "",
    proof_document: null, // File
  });

  // Payment data comes from the Payment child via setPaymentData
  const [paymentdata, setPaymentdata] = useState({
    payment_method_id: "",
    extra_bed_count: 0,
    extra_bed_cost: 0,
    total_amount: 0,
    tax_percentage: 0,
    tax_amount: 0,
    discount_percentage: 0,
    discount_amount: 0,
    extra_charges: 0,
    overall_amount: 0,
    paid_amount: 0,
    balance_amount: 0,
    extra_amount: 0,
  });

  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = useCallback((kind, text) => setToast({ kind, text, at: Date.now() }), []);

  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  // ----------------------------------------------------------------
  // Load masterdata
  // ----------------------------------------------------------------
  useEffect(() => {
    mounted.current = true;
    Promise.allSettled([
      APICall.getT("/masterdata/identity_proof"),
      APICall.getT("/masterdata/room"),
      APICall.getT("/masterdata/room_types"),
      APICall.getT("/masterdata/tax"),
      APICall.getT("/masterdata/discount"),
      APICall.getT("/masterdata/payment_methods"),
      APICall.getT("/masterdata/reservation_status"),
    ]).then((results) => {
      if (!mounted.current) return;
      const [rIdent, rRoom, rRT, rTax, rDisc, rPM, rRes] = results;
      setIdentityTypes(rIdent.status === "fulfilled" ? readList(rIdent.value) : []);
      setRoomsData(rRoom.status === "fulfilled" ? readList(rRoom.value) : []);
      setRoomTypes(rRT.status === "fulfilled" ? readList(rRT.value) : []);
      setTaxTypes(rTax.status === "fulfilled" ? readList(rTax.value) : []);
      setDiscountTypes(rDisc.status === "fulfilled" ? readList(rDisc.value) : []);
      setPaymentMethods(rPM.status === "fulfilled" ? readList(rPM.value) : []);
      setReservationStatusTypes(rRes.status === "fulfilled" ? readList(rRes.value) : []);
      const errs = results
        .map((r, i) => (r.status === "rejected" ? ["identity", "rooms", "room types", "taxes", "discounts", "payment methods", "reservation statuses"][i] : null))
        .filter(Boolean);
      setMasterError(errs.length ? `Failed to load: ${errs.join(", ")}` : null);
    });
    return () => { mounted.current = false; };
  }, []);

  // ----------------------------------------------------------------
  // Room selection — track per-room state by id (not by index)
  // ----------------------------------------------------------------
  const handleSelectRoom = (room) => {
    if (!room?.id) return;
    setSelectedRoomIds((prev) => {
      const exists = prev.includes(room.id);
      if (exists) {
        return prev.filter((id) => id !== room.id);
      }
      setPerRoom((prevMap) => ({
        ...prevMap,
        [room.id]: prevMap[room.id] || {
          adults: 1,
          children: 0,
          rateType: "daily",
          complementary: "",
        },
      }));
      return [...prev, room.id];
    });
  };

  const isRoomSelected = (room) => selectedRoomIds.includes(room.id);

  const updateRoomField = (roomId, field, value) => {
    setPerRoom((prev) => ({
      ...prev,
      [roomId]: { ...(prev[roomId] || {}), [field]: value },
    }));
  };

  const selectedRooms = useMemo(
    () => selectedRoomIds.map((id) => roomsData.find((r) => r.id === id)).filter(Boolean),
    [selectedRoomIds, roomsData],
  );

  const totalAdults = useMemo(
    () => selectedRoomIds.reduce((s, id) => s + num(perRoom[id]?.adults), 0),
    [selectedRoomIds, perRoom],
  );
  const totalChildren = useMemo(
    () => selectedRoomIds.reduce((s, id) => s + num(perRoom[id]?.children), 0),
    [selectedRoomIds, perRoom],
  );

  const totalNights = useMemo(
    () => nightsBetween(formData.arrival_date, formData.departure_date),
    [formData.arrival_date, formData.departure_date],
  );

  // ----------------------------------------------------------------
  // Validation
  // ----------------------------------------------------------------
  const validateGuestForm = () => {
    if (!formData.first_name.trim()) return "First name is required.";
    if (!formData.last_name.trim()) return "Last name is required.";
    if (!formData.email.trim()) return "Email is required.";
    if (!EMAIL_RE.test(formData.email.trim())) return "Enter a valid email address.";
    if (!formData.phone_number.trim()) return "Phone number is required.";
    if (!PHONE_RE.test(formData.phone_number.trim())) return "Enter a valid phone number (digits, +, spaces, - and () only).";
    if (!formData.arrival_date) return "Arrival date is required.";
    if (!formData.departure_date) return "Departure date is required.";
    if (isoDay(formData.arrival_date) >= isoDay(formData.departure_date)) return "Departure date must be after arrival date.";
    if (totalNights < 1) return "The stay must be at least one night.";
    if (!formData.booking_status_id) return "Reservation status is required.";
    if (!formData.identity_type_id) return "Identity type is required.";

    if (!formData.proof_document) return "Please upload the identity proof document.";
    const file = formData.proof_document;
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > MAX_FILE_MB) return `Identity file must be ${MAX_FILE_MB} MB or smaller.`;
    const ext = (file.name.split(".").pop() || "").toLowerCase();
    if (!ALLOWED_FILE_EXT.includes(ext)) {
      return `Identity file type must be one of: ${ALLOWED_FILE_EXT.join(", ")}.`;
    }

    if (selectedRooms.length === 0) return "Select at least one room.";

    for (const room of selectedRooms) {
      const p = perRoom[room.id] || {};
      const maxA = num(room.max_adult);
      const maxC = num(room.max_child);
      if (num(p.adults) < 1) return `Adults must be at least 1 for room ${room.room_no}.`;
      if (maxA > 0 && num(p.adults) > maxA) return `Room ${room.room_no} allows at most ${maxA} adults.`;
      if (num(p.children) < 0) return `Children cannot be negative for room ${room.room_no}.`;
      if (maxC > 0 && num(p.children) > maxC) return `Room ${room.room_no} allows at most ${maxC} children.`;
    }
    return null;
  };

  // ----------------------------------------------------------------
  // Actions
  // ----------------------------------------------------------------
  const handleValidateGuest = () => {
    const v = validateGuestForm();
    if (v) {
      setFormError(v);
      showToast("error", v);
      return;
    }
    setFormError(null);
    setModalView(false);
    setPaymentModal(true);
  };

  const buildFormData = () => {
    const fd = new FormData();
    // Room reservation id — client-generated because backend requires it as a Form(...) param.
    // Prefixed with a stable string so old rows are still distinguishable; UUID-ish suffix minimises collision risk.
    const dtStamp = new Date().toISOString().replace(/[^0-9]/g, "").slice(0, 14);
    const rand = Math.random().toString(36).slice(2, 8).toUpperCase();
    fd.append("room_reservation_id", `RES-${dtStamp}-${rand}`);

    fd.append("salutation", formData.salutation);
    fd.append("first_name", formData.first_name.trim());
    fd.append("last_name", formData.last_name.trim());
    fd.append("phone_number", formData.phone_number.trim());
    fd.append("email", formData.email.trim().toLowerCase());

    fd.append("arrival_date", formData.arrival_date);
    fd.append("departure_date", formData.departure_date);
    fd.append("no_of_nights", String(totalNights));

    const roomTypeIds = selectedRoomIds
      .map((id) => Number(roomsData.find((r) => r.id === id)?.room_type_id))
      .filter(Number.isFinite);
    const rateTypes = selectedRoomIds.map((id) => perRoom[id]?.rateType || "daily");

    fd.append("room_type_ids", JSON.stringify(roomTypeIds));
    fd.append("room_ids", JSON.stringify(selectedRoomIds));
    fd.append("rate_type", JSON.stringify(rateTypes));

    fd.append("no_of_rooms", String(selectedRoomIds.length));
    fd.append("no_of_adults", String(totalAdults || 1));
    fd.append("no_of_children", String(totalChildren));

    fd.append("payment_method_id", String(num(paymentdata.payment_method_id)));
    fd.append("extra_bed_count", String(num(paymentdata.extra_bed_count)));
    fd.append("extra_bed_cost", String(num(paymentdata.extra_bed_cost)));
    fd.append("total_amount", String(num(paymentdata.total_amount)));
    fd.append("tax_percentage", String(num(paymentdata.tax_percentage)));
    fd.append("tax_amount", String(num(paymentdata.tax_amount)));
    fd.append("discount_percentage", String(num(paymentdata.discount_percentage)));
    fd.append("discount_amount", String(num(paymentdata.discount_amount)));
    fd.append("extra_charges", String(num(paymentdata.extra_charges)));
    fd.append("overall_amount", String(num(paymentdata.overall_amount)));
    fd.append("paid_amount", String(num(paymentdata.paid_amount)));
    fd.append("balance_amount", String(num(paymentdata.balance_amount)));
    fd.append("extra_amount", String(num(paymentdata.extra_amount)));

    fd.append("booking_status_id", String(Number(formData.booking_status_id)));

    const selectedStatus = reservationStatusTypes.find(
      (s) => s.id === Number(formData.booking_status_id),
    );
    fd.append("reservation_status", selectedStatus?.reservation_status || "Pending");

    // Aggregate the first-room's complementary as the "room_complementary" field to match backend shape.
    const firstComplementary = selectedRoomIds
      .map((id) => perRoom[id]?.complementary)
      .find((c) => c) || "";
    fd.append("room_complementary", firstComplementary);
    fd.append("common_complementary", formData.common_complementary || "");

    fd.append("identity_type_id", String(Number(formData.identity_type_id)));
    fd.append("identity_file", formData.proof_document);

    return fd;
  };

  const handleSubmitReservation = async () => {
    if (!paymentdata?.payment_method_id) {
      const msg = "Please select a payment method.";
      setFormError(msg);
      showToast("error", msg);
      return;
    }
    if (num(paymentdata.overall_amount) < 0) {
      const msg = "Overall amount cannot be negative.";
      setFormError(msg);
      showToast("error", msg);
      return;
    }
    if (num(paymentdata.paid_amount) < 0) {
      const msg = "Paid amount cannot be negative.";
      setFormError(msg);
      showToast("error", msg);
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      await APICall.postT("/hotel/room_reservation", buildFormData());
      showToast("success", "Reservation created.");
      setPaymentModal(false);
      // Small delay so the toast is visible before navigation.
      setTimeout(() => {
        if (mounted.current) navigate("/reservation");
      }, 900);
    } catch (err) {
      const m = errMsg(err, "Failed to create reservation.");
      setFormError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  const handleBack = () => navigate("/reservation");

  // ----------------------------------------------------------------
  // Render
  // ----------------------------------------------------------------
  return (
    <div className="anr-page">
      <div className="anr-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to reservations"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="anr-header">
          <span className="rmv-eyebrow">New</span>
          <h1 className="rmv-title">Add Reservation</h1>
        </div>
      </div>

      {masterError && (
        <div className="rmv-alert" role="alert">
          <span>{masterError}</span>
        </div>
      )}
      {formError && (
        <div className="rmv-alert" role="alert">
          <span>{formError}</span>
        </div>
      )}

      {roomTypes.length === 0 && !masterError ? (
        <div className="rmv-loading" role="status" aria-live="polite">
          Loading room types…
        </div>
      ) : roomTypes.length > 0 ? (
        <Tabs variant="default">
          {roomTypes.map((type) => (
            <Tab key={type.id} label={roomTypeLabel(type)}>
              <h3 className="rle-tab-title">{roomTypeLabel(type)} Rooms</h3>
              <RoomGrid
                rooms={roomsData.filter(
                  (room) => Number(room.room_type_id) === type.id,
                )}
                isSelected={isRoomSelected}
                onSelect={handleSelectRoom}
              />
            </Tab>
          ))}
        </Tabs>
      ) : null}

      <div className="anr-selection-bar">
        <div>
          <strong>Rooms:</strong>{" "}
          {selectedRooms.length === 0
            ? "Pick one or more rooms above."
            : selectedRooms.map((r) => `Room ${r.room_no}`).join(", ")}
        </div>
        <div>
          {selectedRooms.length > 0 && (
            <Button className="nxt-btn" onClick={() => setModalView(true)}>
              Next
            </Button>
          )}
        </div>
      </div>

      {/* Payment modal (final step) */}
      <Modal
        isOpen={paymentModal}
        title="Billing Details"
        onClose={() => (saving ? null : setPaymentModal(false))}
        showFooter
        size="large"
        bodyLayout="single"
        actions={[
          {
            label: "Back",
            variant: "secondary",
            onClick: () => {
              if (saving) return;
              setPaymentModal(false);
              setModalView(true);
            },
          },
          {
            label: saving ? "Submitting…" : "Submit",
            variant: "primary",
            onClick: handleSubmitReservation,
          },
        ]}
      >
        <Payment
          taxTypes={taxTypes}
          discountTypes={discountTypes}
          paymentMethods={paymentMethods}
          selectedRooms={selectedRooms}
          roomTypes={roomTypes}
          setpaymentData={setPaymentdata}
        />
      </Modal>

      {/* Reservation details modal (before payment) */}
      <Modal
        isOpen={modalView}
        title="Reservation Details"
        onClose={() => setModalView(false)}
        showFooter
        size="large"
        bodyLayout="single"
        actions={[
          {
            label: "Close",
            variant: "secondary",
            onClick: () => setModalView(false),
          },
          {
            label: "Continue to billing",
            variant: "primary",
            onClick: handleValidateGuest,
            autoFocus: true,
          },
        ]}
      >
        <div className="form-card">
          <h3 className="section-title">Guest Information</h3>

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="anr-first-name">First Name <span className="required">*</span></label>
              <div className="title-input">
                <select
                  aria-label="Salutation"
                  value={formData.salutation}
                  className="title-select"
                  onChange={(e) => setFormData((f) => ({ ...f, salutation: e.target.value }))}
                >
                  {SALUTATIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
                <input
                  id="anr-first-name"
                  type="text"
                  placeholder="First Name"
                  style={{ height: "40px" }}
                  value={formData.first_name}
                  onChange={(e) => setFormData((f) => ({ ...f, first_name: e.target.value }))}
                  required
                  maxLength={100}
                  autoComplete="given-name"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="anr-last-name">Last Name <span className="required">*</span></label>
              <input
                id="anr-last-name"
                type="text"
                placeholder="Last Name"
                value={formData.last_name}
                onChange={(e) => setFormData((f) => ({ ...f, last_name: e.target.value }))}
                required
                maxLength={100}
                autoComplete="family-name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-email">Email <span className="required">*</span></label>
              <input
                id="anr-email"
                type="email"
                inputMode="email"
                placeholder="guest@example.com"
                value={formData.email}
                onChange={(e) => setFormData((f) => ({ ...f, email: e.target.value }))}
                required
                maxLength={100}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-phone">Phone Number <span className="required">*</span></label>
              <input
                id="anr-phone"
                type="tel"
                inputMode="tel"
                placeholder="+1 555 123 4567"
                value={formData.phone_number}
                onChange={(e) => setFormData((f) => ({ ...f, phone_number: e.target.value }))}
                required
                maxLength={20}
                autoComplete="tel"
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-arrival">Arrival Date <span className="required">*</span></label>
              <input
                id="anr-arrival"
                type="date"
                value={formData.arrival_date}
                min={isoDay(new Date().toISOString())}
                onChange={(e) => setFormData((f) => ({ ...f, arrival_date: e.target.value }))}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-departure">Departure Date <span className="required">*</span></label>
              <input
                id="anr-departure"
                type="date"
                value={formData.departure_date}
                min={formData.arrival_date || undefined}
                onChange={(e) => setFormData((f) => ({ ...f, departure_date: e.target.value }))}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-nights">Number of Nights <span className="required">*</span></label>
              <input
                id="anr-nights"
                type="number"
                value={totalNights}
                readOnly
                aria-readonly="true"
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-rooms">Number of Rooms</label>
              <input
                id="anr-rooms"
                type="number"
                value={selectedRoomIds.length}
                readOnly
                aria-readonly="true"
                className="readonly-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="anr-status">Reservation Status <span className="required">*</span></label>
              <select
                id="anr-status"
                style={{ height: "40px" }}
                value={formData.booking_status_id}
                onChange={(e) => setFormData((f) => ({ ...f, booking_status_id: e.target.value }))}
                required
              >
                <option value="">— select —</option>
                {reservationStatusTypes.map((status) => (
                  <option key={status.id} value={status.id}>
                    {status.reservation_status}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="anr-identity-type">Identity Type <span className="required">*</span></label>
              <select
                id="anr-identity-type"
                style={{ height: "40px" }}
                value={formData.identity_type_id}
                onChange={(e) => setFormData((f) => ({ ...f, identity_type_id: e.target.value }))}
                required
              >
                <option value="">— select —</option>
                {identityTypes.map((identity) => (
                  <option key={identity.id} value={identity.id}>
                    {identity.proof_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="anr-identity-file">Identity Proof <span className="required">*</span></label>
              <div className="file-upload">
                <input
                  type="file"
                  id="anr-identity-file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setFormData((f) => ({ ...f, proof_document: e.target.files[0] || null }))}
                  required
                />
                <label htmlFor="anr-identity-file" className="file-label">
                  Choose File
                </label>
                <span className="file-name" aria-live="polite">
                  {formData.proof_document ? formData.proof_document.name : "No file chosen"}
                </span>
              </div>
              <p className="anr-hint">Max {MAX_FILE_MB} MB · {ALLOWED_FILE_EXT.join(", ")}</p>
            </div>
          </div>

          <div className="selected-rooms-section">
            <h3 className="section-title">Selected Rooms</h3>
            {selectedRooms.length === 0 && (
              <div className="rmv-empty inline">
                No rooms selected. Close this dialog and pick one or more rooms above.
              </div>
            )}
            {selectedRooms.map((room) => {
              const roomTypeObj = roomTypes.find((t) => Number(t.id) === Number(room.room_type_id));
              const maxAdults = num(room.max_adult);
              const maxChildren = num(room.max_child);
              const p = perRoom[room.id] || {};
              return (
                <div key={room.id} className="selected-room-card">
                  <div className="room-info">
                    <div className="room-block">
                      <label>Room Type</label>
                      <div>{roomTypeObj ? roomTypeLabel(roomTypeObj) : "Unknown"}</div>
                    </div>
                    <div className="room-block">
                      <label>Room No</label>
                      <div>{room.room_no}</div>
                    </div>
                    <div className="room-block">
                      <label>Max Capacity</label>
                      <div>{maxAdults} adults, {maxChildren} children</div>
                    </div>
                    <div>
                      <label htmlFor={`anr-rate-${room.id}`}>Rate Type</label>
                      <select
                        id={`anr-rate-${room.id}`}
                        className="rate-select"
                        value={p.rateType || "daily"}
                        onChange={(e) => updateRoomField(room.id, "rateType", e.target.value)}
                      >
                        {RATE_TYPES.map((rt) => (
                          <option key={rt.value} value={rt.value}>{rt.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor={`anr-adults-${room.id}`}>Total Adult</label>
                      <input
                        id={`anr-adults-${room.id}`}
                        type="number"
                        value={p.adults ?? 1}
                        className="small-input"
                        onChange={(e) => updateRoomField(room.id, "adults", num(e.target.value))}
                        min="1"
                        max={maxAdults > 0 ? maxAdults : undefined}
                      />
                    </div>
                    <div>
                      <label htmlFor={`anr-children-${room.id}`}>Total Child</label>
                      <input
                        id={`anr-children-${room.id}`}
                        type="number"
                        value={p.children ?? 0}
                        className="small-input"
                        onChange={(e) => updateRoomField(room.id, "children", num(e.target.value))}
                        min="0"
                        max={maxChildren > 0 ? maxChildren : undefined}
                      />
                    </div>
                    <div className="complementary-toggle">
                      <label htmlFor={`anr-comp-${room.id}`}>Complementary</label>
                      <select
                        id={`anr-comp-${room.id}`}
                        value={p.complementary || ""}
                        onChange={(e) => updateRoomField(room.id, "complementary", e.target.value)}
                        style={{ height: "40px", marginLeft: "10px" }}
                      >
                        {ROOM_COMPLEMENTARY_OPTIONS.map((opt) => (
                          <option key={opt} value={opt}>{opt || "No Complementary"}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              );
            })}
            <div className="anr-totals" role="status" aria-live="polite">
              <strong>Total Adults: {totalAdults}</strong> | <strong>Total Children: {totalChildren}</strong>
            </div>
          </div>

          <div className="form-group" style={{ marginTop: "20px" }}>
            <label htmlFor="anr-common-comp">Common Complementary</label>
            <select
              id="anr-common-comp"
              value={formData.common_complementary}
              onChange={(e) => setFormData((f) => ({ ...f, common_complementary: e.target.value }))}
              style={{ height: "40px", width: "100%" }}
            >
              {COMMON_COMPLEMENTARY_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt || "No Complementary"}</option>
              ))}
            </select>
          </div>
        </div>
      </Modal>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default AddNewReservation;

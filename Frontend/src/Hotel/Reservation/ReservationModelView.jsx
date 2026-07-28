import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Printer, Pencil, AlertCircle, RefreshCw } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./Reservation.css";

const LOCKED_STATUSES = new Set(["Arrived", "Departures", "Cancelled"]);

const escapeHtml = (v) =>
  String(v ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

const parseArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v === null || v === undefined || v === "") return [];
  try {
    const parsed = JSON.parse(v);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const readOne = (res) =>
  (res?.data && !Array.isArray(res.data) && typeof res.data === "object") ? res.data : null;

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const formatDate = (v) => {
  if (!v) return "—";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
};

const numberFmt = new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const formatAmount = (v) => numberFmt.format(num(v));

const getStatusBadgeClass = (status) => {
  const s = String(status || "").toLowerCase();
  if (s === "pending") return "status-pending";
  if (s === "confirmed") return "status-confirmed";
  if (s === "arrived" || s === "checked-in") return "status-checked-in";
  if (s === "departures" || s === "checked-out") return "status-checked-out";
  if (s === "cancelled" || s === "canceled") return "status-cancelled";
  return "status-pending";
};

const ReservationModelView = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const mounted = useRef(true);

  const reservationId = state?.reservationId;

  const [reservation, setReservation] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  const [roomTypes, setRoomTypes] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [taxTypes, setTaxTypes] = useState([]);
  const [discountTypes, setDiscountTypes] = useState([]);
  const [identityTypes, setIdentityTypes] = useState([]);

  useEffect(() => {
    mounted.current = true;
    if (!reservationId) return undefined;

    setReservation(null);
    setError(null);

    APICall.getT(`/hotel/room_reservation/${encodeURIComponent(reservationId)}`)
      .then((res) => {
        if (!mounted.current) return;
        const one = readOne(res);
        if (!one) {
          setError("Reservation response was malformed.");
          setReservation(null);
        } else {
          setReservation(one);
        }
      })
      .catch((err) => {
        if (!mounted.current) return;
        setError(errMsg(err, "Failed to load reservation."));
        setReservation(null);
      });

    Promise.allSettled([
      APICall.getT("/masterdata/room_types"),
      APICall.getT("/masterdata/room"),
      APICall.getT("/masterdata/payment_methods"),
      APICall.getT("/masterdata/tax"),
      APICall.getT("/masterdata/discount"),
      APICall.getT("/masterdata/identity_proof"),
    ]).then((results) => {
      if (!mounted.current) return;
      const [rRT, rRoom, rPM, rTax, rDisc, rIdent] = results;
      setRoomTypes(rRT.status === "fulfilled" ? readList(rRT.value) : []);
      setRooms(rRoom.status === "fulfilled" ? readList(rRoom.value) : []);
      setPaymentMethods(rPM.status === "fulfilled" ? readList(rPM.value) : []);
      setTaxTypes(rTax.status === "fulfilled" ? readList(rTax.value) : []);
      setDiscountTypes(rDisc.status === "fulfilled" ? readList(rDisc.value) : []);
      setIdentityTypes(rIdent.status === "fulfilled" ? readList(rIdent.value) : []);
    });

    return () => { mounted.current = false; };
  }, [reservationId, refreshTick]);

  // Derived: rooms in this reservation with human labels.
  const roomRows = useMemo(() => {
    if (!reservation) return [];
    const typeIds = parseArr(reservation.room_type_ids);
    const roomIds = parseArr(reservation.room_ids);
    const rateTypes = parseArr(reservation.rate_type);
    const len = Math.max(typeIds.length, roomIds.length, rateTypes.length, 0);
    if (len === 0) return [];

    const perRoomTotal = num(reservation.total_amount) && (num(reservation.no_of_rooms) || len)
      ? num(reservation.total_amount) / (num(reservation.no_of_rooms) || len)
      : 0;

    const list = [];
    for (let i = 0; i < len; i += 1) {
      const roomTypeId = typeIds[i];
      const roomId = roomIds[i];
      const rateType = rateTypes[i];
      list.push({
        sno: i + 1,
        roomType: roomTypes.find((rt) => rt.id === roomTypeId)?.room_type_name || (roomTypeId ? `#${roomTypeId}` : "—"),
        roomNo: rooms.find((r) => r.id === roomId)?.room_no || (roomId ? `#${roomId}` : "—"),
        rateType: rateType || "—",
        checkIn: formatDate(reservation.arrival_date),
        checkOut: formatDate(reservation.departure_date),
        price: perRoomTotal,
      });
    }
    return list;
  }, [reservation, roomTypes, rooms]);

  const paymentMethodLabel = useMemo(() => {
    if (!reservation) return "—";
    const pm = paymentMethods.find((p) => p.id === reservation.payment_method_id);
    return pm?.payment_method || reservation.payment_method_id || "—";
  }, [reservation, paymentMethods]);

  const identityTypeLabel = useMemo(() => {
    if (!reservation) return "—";
    return identityTypes.find((i) => i.id === reservation.identity_type_id)?.proof_name || "—";
  }, [reservation, identityTypes]);

  const taxTypeLabel = useMemo(() => {
    if (!reservation) return "—";
    return taxTypes.find((t) => t.id === reservation.tax_type_id)?.tax_name || "—";
  }, [reservation, taxTypes]);

  const discountTypeLabel = useMemo(() => {
    if (!reservation) return "—";
    return (
      discountTypes.find((d) => d.id === reservation.discount_type_id)?.discount_name ||
      discountTypes.find((d) => d.id === reservation.discount_type_id)?.name ||
      "—"
    );
  }, [reservation, discountTypes]);

  const guestName = reservation
    ? [reservation.salutation, reservation.first_name, reservation.last_name].filter(Boolean).join(" ").trim() || "—"
    : "—";

  const isLoading = Boolean(reservationId) && reservation === null && !error;
  const isLocked = reservation && LOCKED_STATUSES.has(reservation.reservation_status);

  const handleBack = () => navigate("/reservation");
  const handleRefresh = () => setRefreshTick((n) => n + 1);
  const handleEdit = () => {
    // Reservation.jsx opens the edit modal via row action, not a route.
    // Sending the user back to the list is the correct hand-off today.
    navigate("/reservation");
  };

  const handlePrint = () => {
    if (!reservation) return;
    const printWindow = window.open("", "_blank", "noopener,noreferrer");
    if (!printWindow) return;
    const roomRowsHtml = roomRows.map((r) => `
      <tr>
        <td>${escapeHtml(r.sno)}</td>
        <td>${escapeHtml(r.roomType)}</td>
        <td>${escapeHtml(r.roomNo)}</td>
        <td>${escapeHtml(r.rateType)}</td>
        <td>${escapeHtml(r.checkIn)}</td>
        <td>${escapeHtml(r.checkOut)}</td>
        <td>${escapeHtml(formatAmount(r.price))}</td>
      </tr>
    `).join("");
    const content = `<!doctype html><html><head>
      <meta charset="utf-8" />
      <title>Reservation ${escapeHtml(reservation.room_reservation_id)}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #111827; }
        h1 { margin: 0 0 8px 0; }
        h3 { border-bottom: 1px solid #000; padding-bottom: 4px; margin-top: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; font-size: 12px; }
        th { background: #f5f5f5; }
        .row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 24px; }
        .label { font-weight: 700; color: #555; font-size: 12px; }
        .value { font-size: 13px; }
        .summary { margin-top: 12px; }
        .summary div { display: flex; justify-content: space-between; padding: 4px 0; }
        .summary .total { font-weight: 700; border-top: 1px solid #000; padding-top: 8px; }
      </style>
      </head><body>
        <h1>Reservation Receipt</h1>
        <p>ID: ${escapeHtml(reservation.room_reservation_id)}</p>
        <p>Printed: ${escapeHtml(new Date().toLocaleString())}</p>

        <h3>Guest</h3>
        <div class="row">
          <div><span class="label">Name:</span> <span class="value">${escapeHtml(guestName)}</span></div>
          <div><span class="label">Phone:</span> <span class="value">${escapeHtml(reservation.phone_number || "—")}</span></div>
          <div><span class="label">Email:</span> <span class="value">${escapeHtml(reservation.email || "—")}</span></div>
          <div><span class="label">Status:</span> <span class="value">${escapeHtml(reservation.reservation_status || "—")}</span></div>
        </div>

        <h3>Stay</h3>
        <div class="row">
          <div><span class="label">Arrival:</span> <span class="value">${escapeHtml(formatDate(reservation.arrival_date))}</span></div>
          <div><span class="label">Departure:</span> <span class="value">${escapeHtml(formatDate(reservation.departure_date))}</span></div>
          <div><span class="label">Nights:</span> <span class="value">${escapeHtml(reservation.no_of_nights ?? "—")}</span></div>
          <div><span class="label">Rooms:</span> <span class="value">${escapeHtml(reservation.no_of_rooms ?? "—")}</span></div>
        </div>

        <h3>Rooms</h3>
        <table>
          <thead><tr>
            <th>S.No</th><th>Type</th><th>Room</th><th>Rate</th><th>Check-in</th><th>Check-out</th><th>Amount</th>
          </tr></thead>
          <tbody>${roomRowsHtml}</tbody>
        </table>

        <h3>Summary</h3>
        <div class="summary">
          <div><span>Total</span><span>${escapeHtml(formatAmount(reservation.total_amount))}</span></div>
          <div><span>Tax</span><span>${escapeHtml(formatAmount(reservation.tax_amount))}</span></div>
          <div><span>Discount</span><span>-${escapeHtml(formatAmount(reservation.discount_amount))}</span></div>
          <div><span>Extra charges</span><span>${escapeHtml(formatAmount(reservation.extra_charges))}</span></div>
          <div class="total"><span>Overall</span><span>${escapeHtml(formatAmount(reservation.overall_amount))}</span></div>
          <div><span>Paid</span><span>${escapeHtml(formatAmount(reservation.paid_amount))}</span></div>
          <div><span>Balance</span><span>${escapeHtml(formatAmount(reservation.balance_amount))}</span></div>
        </div>

        <script>window.addEventListener("load", function(){ window.print(); });<\/script>
      </body></html>`;
    printWindow.document.write(content);
    printWindow.document.close();
  };

  // -----------------------------------------------------------------------
  // No reservation id in navigation state — direct URL access.
  // -----------------------------------------------------------------------
  if (!reservationId) {
    return (
      <div className="rmv-page">
        <div className="rmv-toolbar">
          <button type="button" className="rmv-back-btn" onClick={handleBack} aria-label="Back to reservations">
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
    <div className="rmv-page">
      <div className="rmv-toolbar">
        <button type="button" className="rmv-back-btn" onClick={handleBack} aria-label="Back to reservations">
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>

        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleRefresh}
            aria-label="Refresh reservation"
            disabled={isLoading}
          >
            <RefreshCw size={16} aria-hidden="true" />
            <span>Refresh</span>
          </button>
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handlePrint}
            disabled={!reservation}
            aria-label="Print reservation receipt"
          >
            <Printer size={16} aria-hidden="true" />
            <span>Print</span>
          </button>
          {reservation && !isLocked && (
            <button
              type="button"
              className="rmv-toolbar-btn primary"
              onClick={handleEdit}
              aria-label="Edit reservation"
            >
              <Pencil size={16} aria-hidden="true" />
              <span>Edit</span>
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="rmv-alert" role="alert">
          <span>{error}</span>
          <button type="button" className="rmv-alert-action" onClick={handleRefresh}>Retry</button>
        </div>
      )}

      {isLoading && (
        <div className="rmv-loading" role="status" aria-live="polite">
          Loading reservation…
        </div>
      )}

      {reservation && (
        <>
          <div className="rmv-header">
            <div>
              <span className="rmv-eyebrow">Reservation</span>
              <h1 className="rmv-title">
                #{reservation.room_reservation_id}
                <span className={`rmv-status-badge ${getStatusBadgeClass(reservation.reservation_status)}`}>
                  {reservation.reservation_status || "—"}
                </span>
              </h1>
            </div>
            {reservation.confirmation_code && (
              <div className="rmv-confirmation">
                <span className="rmv-confirmation-label">Confirmation</span>
                <code className="rmv-confirmation-code">{reservation.confirmation_code}</code>
              </div>
            )}
          </div>

          <div className="Reservation-form-card">
            <section aria-labelledby="rmv-guest-heading">
              <h2 id="rmv-guest-heading" className="rmv-section-heading">Guest & Stay</h2>
              <div className="Reservation-form">
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-guest">Guest Name</label>
                  <input id="rmv-guest" type="text" value={guestName} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-email">Email</label>
                  <input id="rmv-email" type="text" value={reservation.email || ""} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-phone">Phone Number</label>
                  <input id="rmv-phone" type="text" value={reservation.phone_number || ""} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-arrival">Arrival Date</label>
                  <input id="rmv-arrival" type="text" value={formatDate(reservation.arrival_date)} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-departure">Departure Date</label>
                  <input id="rmv-departure" type="text" value={formatDate(reservation.departure_date)} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-nights">Number of Nights</label>
                  <input id="rmv-nights" type="text" value={reservation.no_of_nights ?? ""} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-rooms">Number of Rooms</label>
                  <input id="rmv-rooms" type="text" value={reservation.no_of_rooms ?? ""} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-adults">Adults / Children</label>
                  <input
                    id="rmv-adults"
                    type="text"
                    value={`${reservation.no_of_adults ?? 0} adult(s), ${reservation.no_of_children ?? 0} child(ren)`}
                    readOnly
                  />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-type">Reservation Type</label>
                  <input id="rmv-type" type="text" value={reservation.reservation_type || ""} readOnly />
                </div>
                <div className="Reservation-form-group">
                  <label htmlFor="rmv-identity">Identity Type</label>
                  <input id="rmv-identity" type="text" value={identityTypeLabel} readOnly />
                </div>
              </div>
            </section>

            <section aria-labelledby="rmv-invoice-heading" className="invoice-card">
              <h2 id="rmv-invoice-heading" className="rmv-section-heading">Rooms & Charges</h2>

              {roomRows.length > 0 ? (
                <table className="room-table">
                  <caption className="rmv-sr-only">Room breakdown for this reservation</caption>
                  <thead>
                    <tr>
                      <th scope="col">S.No.</th>
                      <th scope="col">Room Type</th>
                      <th scope="col">Room No</th>
                      <th scope="col">Rate</th>
                      <th scope="col">Check In</th>
                      <th scope="col">Check Out</th>
                      <th scope="col">Room Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {roomRows.map((room) => (
                      <tr key={room.sno}>
                        <td>{room.sno}</td>
                        <td>{room.roomType}</td>
                        <td>{room.roomNo}</td>
                        <td>{room.rateType}</td>
                        <td>{room.checkIn}</td>
                        <td>{room.checkOut}</td>
                        <td>{formatAmount(room.price)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="rmv-empty inline">
                  No room detail on this reservation yet.
                </div>
              )}

              <div className="summary-wrapper">
                <div className="summary">
                  <div>
                    <span>Total Amount</span>
                    <span>{formatAmount(reservation.total_amount)}</span>
                  </div>
                  <div>
                    <span>Tax ({num(reservation.tax_percentage)}% · {taxTypeLabel})</span>
                    <span>{formatAmount(reservation.tax_amount)}</span>
                  </div>
                  <div>
                    <span>Discount ({num(reservation.discount_percentage)}% · {discountTypeLabel})</span>
                    <span>-{formatAmount(reservation.discount_amount)}</span>
                  </div>
                  <div>
                    <span>Extra Charges</span>
                    <span>{formatAmount(reservation.extra_charges)}</span>
                  </div>
                  <div className="total">
                    <span>Overall Amount</span>
                    <span>{formatAmount(reservation.overall_amount)}</span>
                  </div>
                </div>
              </div>

              <h3 className="paid-title">Payment Summary</h3>
              <table className="paid-table">
                <caption className="rmv-sr-only">Payment summary and balance</caption>
                <thead>
                  <tr>
                    <th scope="col">Item</th>
                    <th scope="col">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Payment Method</td>
                    <td>{paymentMethodLabel}</td>
                  </tr>
                  <tr>
                    <td>Paid Amount</td>
                    <td>{formatAmount(reservation.paid_amount)}</td>
                  </tr>
                  <tr>
                    <td>Balance Amount</td>
                    <td>{formatAmount(reservation.balance_amount)}</td>
                  </tr>
                  <tr>
                    <td>Extra Amount</td>
                    <td>{formatAmount(reservation.extra_amount)}</td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>
        </>
      )}
    </div>
  );
};

export default ReservationModelView;

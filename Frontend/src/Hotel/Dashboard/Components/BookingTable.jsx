import React from "react";
// Calendar dates, formatted without a timezone round trip -- `new Date("2026-08-01")`
// parses as midnight UTC and renders as 31 July west of Greenwich.
import { formatDate } from "../../../functions/formatters";

const statusToBadge = (raw) => {
  const s = String(raw || "").toLowerCase();
  if (s.includes("check") && s.includes("in")) return "success";
  if (s === "confirmed" || s === "reserved") return "info";
  if (s === "pending" || s === "hold") return "warning";
  if (s === "cancelled" || s === "canceled") return "danger";
  return "";
};



// The dashboard summary sends one resolved `guest_name`; the reservation
// payload sends the parts. Accept either.
const fullName = (b) =>
  [b?.salutation, b?.first_name, b?.last_name].filter(Boolean).join(" ").trim() ||
  b?.guest_name ||
  "—";

const rowRoomLabel = (b) => {
  // Room NUMBERS where we have them -- "Room 207" means something to the desk,
  // "Room 15" (an internal id) does not.
  const nos = Array.isArray(b?.room_nos) ? b.room_nos.filter(Boolean) : [];
  if (nos.length === 1) return `Room ${nos[0]}`;
  if (nos.length > 1) return `${nos.length} rooms`;
  const ids = Array.isArray(b?.room_ids) ? b.room_ids : [];
  if (ids.length === 0) return b?.no_of_rooms ? `${b.no_of_rooms} room(s)` : "—";
  if (ids.length === 1) return `Room ${ids[0]}`;
  return `${ids.length} rooms`;
};

const BookingTable = ({
  bookings = [],
  loading = false,
  error = null,
  onViewAll,
  onRowClick,
}) => {
  const hasData = Array.isArray(bookings) && bookings.length > 0;

  return (
    <div className="card table-card">
      <div className="card-header-inline">
        <h4>Recent Bookings</h4>
        <button
          type="button"
          className="btn-link"
          onClick={onViewAll}
          aria-label="View all reservations"
        >
          View all
        </button>
      </div>

      {loading && (
        <div className="dashboard-empty" role="status" aria-live="polite">
          Loading bookings…
        </div>
      )}

      {!loading && error && (
        <div className="dashboard-alert inline" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && !hasData && (
        <div className="dashboard-empty">
          No reservations yet. Use “Add Booking” to create the first one.
        </div>
      )}

      {!loading && !error && hasData && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Recent room reservations</caption>
            <thead>
              <tr>
                <th scope="col">Booking ID</th>
                <th scope="col">Guest</th>
                <th scope="col">Room</th>
                <th scope="col">Nights</th>
                <th scope="col">Arrival → Departure</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => {
                const badge = statusToBadge(b?.reservation_status || b?.booking_status_id);
                const status = b?.reservation_status || "—";
                return (
                  <tr
                    key={b?.id ?? b?.room_reservation_id}
                    className={onRowClick ? "clickable" : ""}
                    tabIndex={onRowClick ? 0 : -1}
                    onClick={() => onRowClick && onRowClick(b)}
                    onKeyDown={(e) => {
                      if (!onRowClick) return;
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onRowClick(b);
                      }
                    }}
                    aria-label={onRowClick ? `Open reservation ${b?.room_reservation_id || b?.id}` : undefined}
                  >
                    <td>{b?.room_reservation_id || b?.id || "—"}</td>
                    <td><strong>{fullName(b)}</strong></td>
                    <td>{rowRoomLabel(b)}</td>
                    <td>{Number.isFinite(Number(b?.no_of_nights)) ? b.no_of_nights : "—"}</td>
                    <td>
                      <div className="date-stack">
                        <span>{formatDate(b?.arrival_date)}</span>
                        <span className="date-sub">→ {formatDate(b?.departure_date)}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${badge}`}>{status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default BookingTable;

import React, { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Printer, Pencil, AlertCircle, RefreshCw } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { printDocument, printHeading, printRow } from "../../functions/printDocument";
import { useApiResource } from "../../hooks/useApiResource";
import ViewSection from "../../stories/ViewSection";
import DetailList, { DetailItem } from "../../stories/DetailList";
import {
  escapeHtml,
  formatAmount,
  formatDate,
  formatDateTime,
  guestName as buildGuestName,
  isTerminal,
  num,
  parseArr,
  readOne,
  statusBadgeClass,
} from "./reservationShared";
import "./Reservation.css";

const ReservationModelView = () => {
  const [printBlocked, setPrintBlocked] = useState(false);
  const { state } = useLocation();
  const navigate = useNavigate();

  const reservationId = state?.reservationId;

  // WHAT THIS REPLACES
  //   Seven useState hooks, two hand-written effects and a `mounted` ref
  //   guarding against setState-after-unmount -- the exact shape
  //   useApiResource exists to absorb, and which every other screen in the
  //   module now uses.
  //
  //   It also replaces six /masterdata calls (room_types, room, payment_methods,
  //   tax, discount, identity_proof) that existed only to turn ids into names.
  //   The rewritten detail endpoint resolves every one of those itself and
  //   returns `room_nos`, `room_type_names`, `payment_method`, `tax_name`,
  //   `discount_name`, `identity_type` and a per-room `rate_breakdown`. Looking
  //   them up again here meant six extra round trips to reach an answer the
  //   server had already sent, and two chances to disagree with it.
  const {
    data: reservation,
    loading,
    error,
    reload,
  } = useApiResource(
    () => APICall.getT(`/hotel/room_reservation/${encodeURIComponent(reservationId)}`),
    {
      select: readOne,
      initial: null,
      fallback: "Failed to load reservation.",
      deps: [reservationId],
      enabled: Boolean(reservationId),
    },
  );

  // History is best-effort: the page is still correct without it.
  const { data: paymentHistory } = useApiResource(
    () =>
      APICall.getT(
        `/hotel/room_reservation_payments/${encodeURIComponent(reservation?.token)}`,
      ),
    {
      select: readList,
      initial: [],
      deps: [reservation?.token],
      enabled: Boolean(reservation?.token),
    },
  );

  /**
   * One row per room on the booking.
   *
   * `rate_breakdown` is the server's own per-room list and is preferred. The
   * zip below is the fallback for a response that predates it.
   *
   * NEITHER CARRIES A PER-ROOM AMOUNT, AND THIS DELIBERATELY NO LONGER SHOWS ONE.
   * The previous version printed `total_amount / no_of_rooms` in a "Room Amount"
   * column. That is only ever right when every room on the booking is the same
   * type at the same rate; for a mixed booking it invented a number and put it
   * on a receipt. Per-room amounts are not persisted -- only the aggregate
   * `room_amount` is -- so there is nothing to show here that would be true.
   * The real money is in the summary below, where it comes from stored columns.
   */
  const roomRows = useMemo(() => {
    if (!reservation) return [];

    const breakdown = parseArr(reservation.rate_breakdown);
    if (breakdown.length) {
      return breakdown.map((line, i) => ({
        key: `${line.room_id ?? i}`,
        sno: i + 1,
        roomType: line.room_type_name || "—",
        roomNo: line.room_no || "—",
        rateType: line.rate_type || "—",
        nights: line.units ?? reservation.no_of_nights ?? "—",
      }));
    }

    const roomNos = parseArr(reservation.room_nos);
    const typeNames = parseArr(reservation.room_type_names);
    const rateTypes = parseArr(reservation.rate_type);
    const len = Math.max(roomNos.length, typeNames.length, rateTypes.length);
    return Array.from({ length: len }, (_, i) => ({
      key: `fallback-${i}`,
      sno: i + 1,
      roomType: typeNames[i] || "—",
      roomNo: roomNos[i] || "—",
      rateType: rateTypes[i] || "—",
      nights: reservation.no_of_nights ?? "—",
    }));
  }, [reservation]);

  const guestName = reservation ? buildGuestName(reservation) : "—";
  const isLocked = isTerminal(reservation);

  const handleBack = () => navigate("/reservation");
  const handleEdit = () => {
    // The list owns editing -- it opens a modal from a row action rather than
    // routing to a screen. Handing the user back to it is the correct hand-off.
    navigate("/reservation");
  };

  const handlePrint = () => {
    if (!reservation) return;

    // Was a hand-written document with its own inline stylesheet — the third
    // near-identical copy in the app — and a bare `if (!printWindow) return;`,
    // so a blocked pop-up meant the Print button simply did nothing with no
    // explanation. printDocument owns the boilerplate and reports the block.
    const roomRowsHtml = roomRows
      .map(
        (r) =>
          `<tr><td>${escapeHtml(r.sno)}</td><td>${escapeHtml(r.roomType)}</td>` +
          `<td>${escapeHtml(r.roomNo)}</td><td>${escapeHtml(r.rateType)}</td>` +
          `<td class="num">${escapeHtml(r.nights)}</td></tr>`,
      )
      .join("");

    const ok = printDocument({
      title: `Reservation ${reservation.room_reservation_id}`,
      heading: "Reservation Receipt",
      subtitle: `${reservation.room_reservation_id} · ${new Date().toLocaleString()}`,
      body:
        printHeading("Guest") +
        printRow("Name", guestName) +
        printRow("Phone", reservation.phone_number || "—") +
        printRow("Email", reservation.email || "—") +
        printRow("Status", reservation.reservation_status || "—") +
        printHeading("Stay") +
        printRow("Arrival", formatDate(reservation.arrival_date)) +
        printRow("Departure", formatDate(reservation.departure_date)) +
        printRow("Nights", reservation.no_of_nights ?? "—") +
        printRow("Rooms", reservation.no_of_rooms ?? "—") +
        printHeading("Rooms") +
        `<table><thead><tr><th>S.No</th><th>Type</th><th>Room</th>` +
        `<th>Rate</th><th class="num">Nights</th></tr></thead>` +
        `<tbody>${roomRowsHtml || '<tr><td colspan="5">No rooms</td></tr>'}</tbody></table>` +
        printHeading("Summary") +
        printRow("Room amount", formatAmount(reservation.room_amount)) +
        printRow("Tax", formatAmount(reservation.tax_amount)) +
        printRow(
          "Discount",
          num(reservation.discount_amount)
            ? `-${formatAmount(reservation.discount_amount)}`
            : formatAmount(0),
        ) +
        printRow("Extra charges", formatAmount(reservation.extra_charges)) +
        printRow("Overall", formatAmount(reservation.overall_amount), { total: true }) +
        printRow("Paid", formatAmount(reservation.paid_amount)) +
        printRow("Balance", formatAmount(reservation.balance_amount)),
    });

    if (!ok) setPrintBlocked(true);
  };

  // -----------------------------------------------------------------------
  // No reservation id in navigation state — direct URL access.
  // -----------------------------------------------------------------------
  if (!reservationId) {
    return (
      <div className="rmv-page">
        <div className="rmv-toolbar">
          <button
            type="button"
            className="rmv-back-btn"
            onClick={handleBack}
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
    <div className="rmv-page">
      <div className="rmv-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to reservations"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>

        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={reload}
            aria-label="Refresh reservation"
            disabled={loading}
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
          <button type="button" className="rmv-alert-action" onClick={reload}>
            Retry
          </button>
        </div>
      )}

      {/* A blocked pop-up used to make Print do nothing at all, with no clue
          as to why. */}
      {printBlocked && (
        <div className="rmv-alert" role="alert">
          <span>The print window was blocked. Please allow pop-ups for this site.</span>
          <button
            type="button"
            className="rmv-alert-action"
            onClick={() => setPrintBlocked(false)}
          >
            Dismiss
          </button>
        </div>
      )}

      {loading && (
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
                <span
                  className={`rmv-status-badge ${statusBadgeClass(reservation.reservation_status)}`}
                >
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

          {/*
            Rendered as label/value pairs, not `<input readOnly>`.
            This screen used to lay its data out as ten read-only inputs: tab
            stops the keyboard had to walk through, values clipped to one line,
            and the whole record reading as a form somebody had switched off.
            DetailList is what the rest of the app's View surfaces use.
          */}
          <ViewSection title="Guest">
            <DetailList columns={3}>
              <DetailItem label="Guest Name" value={guestName} />
              <DetailItem label="Phone Number" value={reservation.phone_number} />
              <DetailItem label="Email" value={reservation.email} span={2} />
              <DetailItem label="Identity Type" value={reservation.identity_type} />
              <DetailItem label="Reservation Type" value={reservation.reservation_type} />
            </DetailList>
          </ViewSection>

          <ViewSection title="Stay">
            <DetailList columns={3}>
              <DetailItem label="Arrival Date" value={formatDate(reservation.arrival_date)} />
              <DetailItem label="Departure Date" value={formatDate(reservation.departure_date)} />
              <DetailItem label="Nights" value={reservation.no_of_nights} />
              <DetailItem label="Rooms" value={reservation.no_of_rooms} />
              <DetailItem
                label="Occupancy"
                value={`${reservation.no_of_adults ?? 0} adult(s), ${reservation.no_of_children ?? 0} child(ren)`}
              />
              <DetailItem label="Booked On" value={formatDateTime(reservation.created_at)} />
              {reservation.room_complementary && (
                <DetailItem
                  label="Room Complementary"
                  value={reservation.room_complementary}
                  span={3}
                />
              )}
              {reservation.common_complementary && (
                <DetailItem
                  label="Common Complementary"
                  value={reservation.common_complementary}
                  span={3}
                />
              )}
            </DetailList>
          </ViewSection>

          {reservation.cancellation_reason && (
            <ViewSection title="Cancellation">
              <DetailList columns={3}>
                <DetailItem label="Reason" value={reservation.cancellation_reason} span={2} />
                <DetailItem label="Cancelled At" value={formatDateTime(reservation.cancelled_at)} />
                <DetailItem label="Cancelled By" value={reservation.cancelled_by} />
              </DetailList>
            </ViewSection>
          )}

          <ViewSection title="Rooms">
            {roomRows.length > 0 ? (
              <div className="rmv-table-scroll">
                <table className="room-table">
                  <caption className="rmv-sr-only">Rooms on this reservation</caption>
                  <thead>
                    <tr>
                      <th scope="col">S.No.</th>
                      <th scope="col">Room Type</th>
                      <th scope="col">Room No</th>
                      <th scope="col">Rate Type</th>
                      <th scope="col">Nights</th>
                    </tr>
                  </thead>
                  <tbody>
                    {roomRows.map((room) => (
                      <tr key={room.key}>
                        <td>{room.sno}</td>
                        <td>{room.roomType}</td>
                        <td>{room.roomNo}</td>
                        <td>{room.rateType}</td>
                        <td>{room.nights}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="rmv-empty inline">No room detail on this reservation yet.</div>
            )}
          </ViewSection>

          <ViewSection title="Charges">
            <DetailList columns={3}>
              <DetailItem label="Room Amount" value={formatAmount(reservation.room_amount)} />
              <DetailItem
                label={`Tax${reservation.tax_name ? ` · ${reservation.tax_name}` : ""} (${num(reservation.tax_percentage)}%)`}
                value={formatAmount(reservation.tax_amount)}
              />
              <DetailItem
                label={`Discount${reservation.discount_name ? ` · ${reservation.discount_name}` : ""} (${num(reservation.discount_percentage)}%)`}
                value={
                  num(reservation.discount_amount)
                    ? `-${formatAmount(reservation.discount_amount)}`
                    : formatAmount(0)
                }
              />
              <DetailItem label="Extra Charges" value={formatAmount(reservation.extra_charges)} />
              {num(reservation.extra_bed_count) > 0 && (
                <DetailItem
                  label={`Extra Beds (${num(reservation.extra_bed_count)})`}
                  value={formatAmount(reservation.extra_bed_cost)}
                />
              )}
              <DetailItem label="Overall Amount" value={formatAmount(reservation.overall_amount)} />
            </DetailList>
          </ViewSection>

          <ViewSection title="Payment">
            <DetailList columns={3}>
              <DetailItem label="Payment Method" value={reservation.payment_method} />
              <DetailItem label="Payment State" value={reservation.payment_state} />
              <DetailItem label="Paid Amount" value={formatAmount(reservation.paid_amount)} />
              <DetailItem label="Balance Amount" value={formatAmount(reservation.balance_amount)} />
              <DetailItem label="Extra Amount" value={formatAmount(reservation.extra_amount)} />
            </DetailList>

            <h3 className="paid-title">Payment History</h3>
            {paymentHistory.length === 0 ? (
              <div className="rmv-empty inline">No payments recorded yet.</div>
            ) : (
              <div className="rmv-table-scroll">
                <table className="paid-table">
                  <caption className="rmv-sr-only">
                    Individual payments recorded against this reservation
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Method</th>
                      <th scope="col">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paymentHistory.map((p) => (
                      <tr key={p.id}>
                        <td>{formatDate(p.paid_date)}</td>
                        <td>{p.payment_method || "—"}</td>
                        <td>{formatAmount(p.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </ViewSection>
        </>
      )}
    </div>
  );
};

export default ReservationModelView;

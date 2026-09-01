// Shared helpers for the Reservation screens.
//
// The five screens in this folder read the same API and render the same
// vocabulary, but each had grown a private copy of the same handful of
// functions: `num` in four of them, `escapeHtml` and `parseArr` in two each,
// and `formatDate`/`formatAmount` in two. Copies drift -- the two `formatDate`
// copies both went through `new Date(...)` and shifted a calendar date a day
// west of Greenwich, a bug the Night Audit copy had already been fixed for.
//
// Generic formatting lives one level up in functions/formatters.js, shared with
// Night Audit. What stays here is the vocabulary that is specific to
// reservations: status classes, what counts as terminal, and the shapes the
// reservation payload uses.

import { formatPrecise } from "../../functions/formatters.js";

export {
  num,
  formatDate,
  formatDateTime,
  isoDay,
} from "../../functions/formatters.js";

/** Money on these screens is shown to the paisa, matching the folio. */
export const formatAmount = formatPrecise;

/**
 * `room_ids`, `room_type_ids` and `rate_type` come back as real arrays from the
 * rewritten API, but older rows -- and the multipart edit round trip -- can
 * still carry them as a JSON string. Accept both rather than rendering "[25]".
 */
export const parseArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v === null || v === undefined || v === "") return [];
  try {
    const parsed = JSON.parse(v);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

/** For the print window, which builds HTML as text. */
export const escapeHtml = (v) =>
  String(v ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

/**
 * Fold a status for comparison: case, spaces and hyphens all ignored.
 *
 * Needed because the vocabulary is spelled differently in different places --
 * a set written as "No Show" never matched the "No-Show" Master Data stores, so
 * no-show reservations stayed editable when they should have been locked.
 */
export const foldStatus = (v) => String(v || "").toLowerCase().replace(/[^a-z]/g, "");

const TERMINAL_STATUSES = new Set(["checkedout", "cancelled", "noshow"]);

/**
 * Whether a reservation can no longer be amended.
 *
 * The API reports this per row as `is_terminal`, computed from the same
 * transition table it enforces, so that is the answer whenever it is present.
 * The local set is only a fallback for a response that predates the field.
 */
export const isTerminal = (reservation) =>
  Boolean(reservation) &&
  (reservation.is_terminal === true ||
    TERMINAL_STATUSES.has(foldStatus(reservation.reservation_status)));

/** Status badge class, matching the colours TableTemplate uses in the list. */
export const statusBadgeClass = (status) => {
  switch (foldStatus(status)) {
    case "confirmed":
      return "status-confirmed";
    case "checkedin":
    case "arrived":
      return "status-checked-in";
    case "checkedout":
    case "departures":
      return "status-checked-out";
    case "cancelled":
    case "canceled":
    case "noshow":
      return "status-cancelled";
    default:
      return "status-pending";
  }
};

/** "Mr. Rohan Mehta" from the parts, falling back to the API's own label. */
export const guestName = (r) =>
  [r?.salutation, r?.first_name, r?.last_name].filter(Boolean).join(" ").trim() ||
  r?.guest_name ||
  "Guest";

/** A single-object response body, or null if the shape is wrong. */
export const readOne = (res) =>
  res?.data && !Array.isArray(res.data) && typeof res.data === "object" ? res.data : null;

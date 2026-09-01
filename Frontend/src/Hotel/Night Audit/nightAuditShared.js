// Shared helpers for the four Night Audit screens.
//
// These four screens all read the same API and render the same vocabulary, so
// the formatters live here rather than being copied into each file. The
// previous versions of these screens each carried their own private copy of
// `formatDate`, `readList`, `errMsg`, a `statusClass` map and a CSV writer --
// four drifting copies of the same six functions, which is how the settlement
// screen ended up with a different balance rounding rule from the table beside
// it.

// The formatters these screens use now live in functions/formatters.js, so the
// Reservation screens share ONE implementation with Night Audit rather than
// keeping their own drifting copies -- two of which formatted calendar dates
// through `new Date(...)` and shifted them a day west of Greenwich.
//
// Re-exported rather than re-pointed at every import site: this file is the
// Night Audit vocabulary, and `import { formatCurrency } from "./nightAuditShared"`
// stays the right thing for these screens to say.
export {
    num,
    formatCurrency,
    formatPrecise,
    formatCount,
    formatPercent,
    formatDate,
    formatDateTime,
    isoDay,
} from "../../functions/formatters.js";

/**
 * The reservation_status vocabulary, straight from the `reservation_status`
 * master table. Mapped to TableTemplate's badge classes so a status renders the
 * same colour in Night Audit as it does in Reservation.
 */
export const RESERVATION_STATUSES = [
    "Confirmed",
    "Checked-In",
    "Checked-Out",
    "Cancelled",
    "No-Show",
    "Pending",
    "On Hold",
];

/** Run states of a night_audit row. */
export const AUDIT_STATUSES = ["Completed", "Failed", "Running"];

export const AUDIT_STATUS_CLASS = {
    Completed: "na-badge--success",
    Failed: "na-badge--error",
    Running: "na-badge--info",
};

/**
 * Which of the audit's reservation lists a screen is showing.
 *
 * Keyed by the exact key the API returns under `lists`, so adding a list to the
 * backend is the only change needed to surface it.
 */
export const AUDIT_LISTS = [
    {
        key: "in_house",
        label: "In House",
        emptyMessage: "No guests were in house on this night.",
        description: "Guests checked in and occupying a room on this night.",
    },
    {
        key: "arrivals_expected",
        label: "Arrivals Due",
        emptyMessage: "No arrivals were due on this night.",
        description: "Reservations booked to arrive on this date.",
    },
    {
        key: "no_show_candidates",
        label: "Not Checked In",
        emptyMessage: "Every arrival due was checked in.",
        description:
            "Due to arrive but never checked in. These become No-Show if you choose that option when running the audit.",
    },
    {
        key: "departures_expected",
        label: "Departures Due",
        emptyMessage: "No departures were due on this night.",
        description: "Reservations booked to depart on this date.",
    },
    {
        key: "overdue_departures",
        label: "Overdue",
        emptyMessage: "No guests are past their departure date.",
        description:
            "Still checked in after their departure date. Check them out or extend the stay.",
    },
    {
        key: "unsettled_folios",
        label: "Unsettled",
        emptyMessage: "Every arrived reservation is settled.",
        description:
            "Guests who have arrived and still owe money. The audit records the balance; it does not clear it.",
    },
];

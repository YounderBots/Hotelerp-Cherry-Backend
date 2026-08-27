// Shared helpers for the four Night Audit screens.
//
// These four screens all read the same API and render the same vocabulary, so
// the formatters live here rather than being copied into each file. The
// previous versions of these screens each carried their own private copy of
// `formatDate`, `readList`, `errMsg`, a `statusClass` map and a CSV writer --
// four drifting copies of the same six functions, which is how the settlement
// screen ended up with a different balance rounding rule from the table beside
// it.

/** Amount as the app formats money everywhere else: grouped, no decimals. */
const currencyFmt = new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
});

/** Amount with cents, for anything that has to reconcile to the paisa. */
const preciseFmt = new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
});

const countFmt = new Intl.NumberFormat(undefined);

export const num = (v) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
};

export const formatCurrency = (v) =>
    v === null || v === undefined ? "—" : currencyFmt.format(Math.round(num(v)));

export const formatPrecise = (v) =>
    v === null || v === undefined ? "—" : preciseFmt.format(num(v));

export const formatCount = (v) =>
    v === null || v === undefined ? "—" : countFmt.format(num(v));

export const formatPercent = (v) =>
    v === null || v === undefined ? "—" : `${preciseFmt.format(num(v))}%`;

/**
 * A business date as text.
 *
 * Takes the 'YYYY-MM-DD' the API sends and formats it WITHOUT going through
 * `new Date(...)`. That matters: `new Date("2026-08-01")` parses as midnight
 * UTC, so west of Greenwich it renders as 31 July. A business date is a plain
 * calendar label, not an instant, and must never shift with the viewer's
 * timezone -- an audit for the 1st has to read as the 1st in every office.
 */
export const formatDate = (value) => {
    if (!value) return "—";
    const text = String(value).slice(0, 10);
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
    if (!match) return String(value);
    const [, y, m, d] = match;
    const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${Number(d)} ${MONTHS[Number(m) - 1]} ${y}`;
};

/** A date-time stamp (started_at / completed_at). These ARE instants. */
export const formatDateTime = (value) => {
    if (!value) return "—";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return `${formatDate(value)} · ${d.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit",
    })}`;
};

/** 'YYYY-MM-DD' for a date input, without a timezone round trip. */
export const isoDay = (value) => (value ? String(value).slice(0, 10) : "");

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

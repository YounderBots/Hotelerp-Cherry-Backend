// App-wide value formatting.
//
// WHY THIS EXISTS
// `formatDate`, `formatAmount` and a `num` coercion had been written three
// times: once in nightAuditShared.js and once each in ReservationView.jsx and
// ReservationModelView.jsx. The Night Audit copy was the correct one. The two
// Reservation copies both went through `new Date(value)`, which is wrong for a
// calendar date -- see `formatDate` below -- so an arrival stored as 1 Aug
// rendered as 31 Jul for any user west of Greenwich, on the two screens a guest
// is most likely to be shown at the desk.
//
// One implementation, so a fix lands everywhere rather than in whichever copy
// somebody happened to open.

const currencyFmt = new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
});

/** Money that has to reconcile to the paisa. */
const preciseFmt = new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
});

const countFmt = new Intl.NumberFormat(undefined);

const MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

/** Anything to a finite number, defaulting to 0. */
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
 * A calendar date as text.
 *
 * Formats the 'YYYY-MM-DD' the API sends WITHOUT going through `new Date(...)`.
 * That matters: `new Date("2026-08-01")` parses as midnight UTC, so west of
 * Greenwich it renders as 31 July. An arrival date is a plain calendar label,
 * not an instant, and must never shift with the viewer's timezone -- a guest
 * arriving on the 1st has to read as the 1st in every office.
 */
export const formatDate = (value) => {
    if (!value) return "—";
    const text = String(value).slice(0, 10);
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
    if (!match) return String(value);
    const [, y, m, d] = match;
    return `${Number(d)} ${MONTHS[Number(m) - 1]} ${y}`;
};

/** A timestamp (created_at, paid_date). These ARE instants, so Date is right. */
export const formatDateTime = (value) => {
    if (!value) return "—";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return `${formatDate(value)} · ${d.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit",
    })}`;
};

/**
 * Today, as the 'YYYY-MM-DD' a date input wants — in the VIEWER'S timezone.
 *
 * Ten screens had written this as `new Date().toISOString().slice(0, 10)`,
 * which is the UTC date, not the local one. East of Greenwich that is the
 * PREVIOUS day for part of every evening: at 01:00 in Chennai the UTC date is
 * still yesterday, so the reports, rosters and dashboards that use this as
 * their default all opened on the wrong day for anyone working a night shift —
 * and the report simply looked empty.
 */
export const todayIso = () => {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

/** 'YYYY-MM-DD' for a date input, without a timezone round trip. */
export const isoDay = (value) => (value ? String(value).slice(0, 10) : "");

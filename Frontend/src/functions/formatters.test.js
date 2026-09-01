import { describe, expect, it, vi, afterEach } from "vitest";

import {
    formatCount,
    formatCurrency,
    formatDate,
    formatDateTime,
    formatPercent,
    formatPrecise,
    isoDay,
    num,
    todayIso,
} from "./formatters.js";

// These helpers are shared by every screen that shows a date or an amount, so
// the two mistakes they exist to prevent are pinned down here: a calendar date
// must not move with the viewer's timezone, and "today" must be the viewer's
// today rather than UTC's.

afterEach(() => vi.useRealTimers());

describe("num", () => {
    it("coerces anything to a finite number, defaulting to 0", () => {
        expect(num("12.5")).toBe(12.5);
        expect(num(7)).toBe(7);
        expect(num(null)).toBe(0);
        expect(num(undefined)).toBe(0);
        expect(num("not a number")).toBe(0);
        expect(num(Infinity)).toBe(0);
    });
});

describe("formatDate", () => {
    // The bug this guards: `new Date("2026-08-01")` parses as midnight UTC, so
    // anywhere west of Greenwich it renders as 31 July. An arrival date is a
    // calendar label, not an instant.
    it("reads the API's YYYY-MM-DD without a timezone round trip", () => {
        expect(formatDate("2026-08-01")).toBe("1 Aug 2026");
        expect(formatDate("2026-12-31")).toBe("31 Dec 2026");
    });

    it("ignores a time component rather than shifting the day", () => {
        expect(formatDate("2026-08-01T23:30:00Z")).toBe("1 Aug 2026");
    });

    it("renders an em dash for nothing, and passes an unrecognised value through", () => {
        expect(formatDate(null)).toBe("—");
        expect(formatDate("")).toBe("—");
        expect(formatDate("not a date")).toBe("not a date");
    });
});

describe("formatDateTime", () => {
    it("renders a timestamp as a date plus a time", () => {
        const out = formatDateTime("2026-08-01T10:30:00");
        expect(out).toContain("1 Aug 2026");
        expect(out).toContain("·");
    });

    it("renders an em dash for nothing", () => {
        expect(formatDateTime(null)).toBe("—");
    });
});

describe("todayIso", () => {
    // The bug this guards: ten screens had written this as
    // `new Date().toISOString().slice(0, 10)`, which is the UTC date. East of
    // Greenwich that is the PREVIOUS day for part of every evening, so reports
    // and rosters opened on the wrong day for anyone on a night shift.
    it("returns the LOCAL calendar date, not the UTC one", () => {
        // 01:00 on 2 Sep in a UTC+5:30 zone is still 19:30 on 1 Sep in UTC.
        // The real Date here is constructed from an explicit local wall time,
        // so the assertion holds whatever zone the test host is in.
        vi.useFakeTimers();
        vi.setSystemTime(new Date(2026, 8, 2, 1, 0, 0));
        expect(todayIso()).toBe("2026-09-02");
    });

    it("zero-pads month and day", () => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date(2026, 0, 5, 12, 0, 0));
        expect(todayIso()).toBe("2026-01-05");
    });

    it("agrees with the local date at the very end of a day", () => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date(2026, 11, 31, 23, 59, 59));
        expect(todayIso()).toBe("2026-12-31");
    });
});

describe("isoDay", () => {
    it("truncates a timestamp to its date part for a date input", () => {
        expect(isoDay("2026-08-01T10:30:00Z")).toBe("2026-08-01");
        expect(isoDay("2026-08-01")).toBe("2026-08-01");
        expect(isoDay(null)).toBe("");
    });
});

describe("amount formatting", () => {
    it("renders an em dash for null and undefined, but not for zero", () => {
        expect(formatPrecise(null)).toBe("—");
        expect(formatPrecise(undefined)).toBe("—");
        expect(formatPrecise(0)).toBe("0.00");
        expect(formatCurrency(null)).toBe("—");
        expect(formatCount(null)).toBe("—");
        expect(formatPercent(null)).toBe("—");
    });

    it("keeps two decimals on a precise amount and none on a rounded one", () => {
        expect(formatPrecise(1234.5)).toBe("1,234.50");
        expect(formatCurrency(1234.5)).toBe("1,235");
    });

    it("treats a non-numeric amount as zero rather than NaN", () => {
        expect(formatPrecise("oops")).toBe("0.00");
    });

    it("suffixes a percentage", () => {
        expect(formatPercent(62.5)).toBe("62.50%");
    });
});

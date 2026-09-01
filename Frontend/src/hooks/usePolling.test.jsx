// @vitest-environment jsdom
import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { usePolling } from "./usePolling.js";

// The kitchen and bar station screens are wall displays that nobody reloads by
// hand, so what this hook guarantees matters: one timer per delay, the latest
// callback on every tick, and no timer at all when paused.

afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
});

describe("usePolling", () => {
    it("calls the callback once per interval", () => {
        vi.useFakeTimers();
        const fn = vi.fn();
        renderHook(() => usePolling(fn, 1000));

        expect(fn).not.toHaveBeenCalled();
        vi.advanceTimersByTime(1000);
        expect(fn).toHaveBeenCalledTimes(1);
        vi.advanceTimersByTime(2000);
        expect(fn).toHaveBeenCalledTimes(3);
    });

    it("does nothing when the delay is null", () => {
        vi.useFakeTimers();
        const fn = vi.fn();
        renderHook(() => usePolling(fn, null));
        vi.advanceTimersByTime(60000);
        expect(fn).not.toHaveBeenCalled();
    });

    it("does nothing when the delay is undefined", () => {
        vi.useFakeTimers();
        const fn = vi.fn();
        renderHook(() => usePolling(fn, undefined));
        vi.advanceTimersByTime(60000);
        expect(fn).not.toHaveBeenCalled();
    });

    it("stops when the delay becomes null", () => {
        vi.useFakeTimers();
        const fn = vi.fn();
        const { rerender } = renderHook(({ delay }) => usePolling(fn, delay), {
            initialProps: { delay: 1000 },
        });
        vi.advanceTimersByTime(1000);
        expect(fn).toHaveBeenCalledTimes(1);

        rerender({ delay: null });
        vi.advanceTimersByTime(5000);
        expect(fn).toHaveBeenCalledTimes(1);
    });

    it("clears its timer on unmount", () => {
        vi.useFakeTimers();
        const fn = vi.fn();
        const { unmount } = renderHook(() => usePolling(fn, 1000));
        unmount();
        vi.advanceTimersByTime(5000);
        expect(fn).not.toHaveBeenCalled();
    });

    // The reason the callback is held in a ref: a caller passing an inline
    // arrow (which every caller does) would otherwise restart the interval on
    // every render, and a page that re-renders faster than its own period
    // would never tick at all.
    it("does not restart the interval when only the callback changes", () => {
        vi.useFakeTimers();
        const first = vi.fn();
        const second = vi.fn();
        const { rerender } = renderHook(({ cb }) => usePolling(cb, 1000), {
            initialProps: { cb: first },
        });

        vi.advanceTimersByTime(600);
        rerender({ cb: second });
        // 400ms of the original period is left; the timer was not restarted.
        vi.advanceTimersByTime(400);

        expect(first).not.toHaveBeenCalled();
        expect(second).toHaveBeenCalledTimes(1);
    });
});

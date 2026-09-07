// @vitest-environment jsdom
import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useIdleTimeout, IDLE_TIMEOUT_MINUTES } from "./useIdleTimeout.js";

// A front-desk terminal is shared and left unattended, so what this hook
// guarantees is a security property: the session ends after a fixed period of
// no interaction, and any interaction genuinely restarts that clock.

const MINUTE = 60 * 1000;
const IDLE_MS = IDLE_TIMEOUT_MINUTES * MINUTE;

afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
});

describe("useIdleTimeout", () => {
    it("waits an hour by default", () => {
        expect(IDLE_TIMEOUT_MINUTES).toBe(60);
    });

    it("does not fire before the window elapses", () => {
        vi.useFakeTimers();
        const onIdle = vi.fn();
        renderHook(() => useIdleTimeout(onIdle));

        vi.advanceTimersByTime(IDLE_MS - 1);
        expect(onIdle).not.toHaveBeenCalled();
    });

    it("signs out once the window elapses", () => {
        vi.useFakeTimers();
        const onIdle = vi.fn();
        renderHook(() => useIdleTimeout(onIdle));

        vi.advanceTimersByTime(IDLE_MS);
        expect(onIdle).toHaveBeenCalledTimes(1);
    });

    it("fires once, not repeatedly, while the tab is left open", () => {
        vi.useFakeTimers();
        const onIdle = vi.fn();
        renderHook(() => useIdleTimeout(onIdle));

        vi.advanceTimersByTime(IDLE_MS * 3);
        expect(onIdle).toHaveBeenCalledTimes(1);
    });

    it("restarts the clock on activity", () => {
        vi.useFakeTimers();
        const onIdle = vi.fn();
        renderHook(() => useIdleTimeout(onIdle));

        // Most of the way there, then a keypress.
        vi.advanceTimersByTime(IDLE_MS - MINUTE);
        window.dispatchEvent(new Event("keydown"));

        // The original deadline passes without firing...
        vi.advanceTimersByTime(2 * MINUTE);
        expect(onIdle).not.toHaveBeenCalled();

        // ...and the full window from the keypress is what counts.
        vi.advanceTimersByTime(IDLE_MS);
        expect(onIdle).toHaveBeenCalledTimes(1);
    });

    it("ignores a second activity event within the throttle window", () => {
        // The reset is throttled to once a second so a mousemove storm does no
        // work. The risk is that the throttle drops a reset and shortens the
        // session, so pin that it does not: bursts still leave a full window.
        vi.useFakeTimers();
        const onIdle = vi.fn();
        renderHook(() => useIdleTimeout(onIdle));

        window.dispatchEvent(new Event("pointerdown"));
        window.dispatchEvent(new Event("wheel"));
        window.dispatchEvent(new Event("scroll"));

        vi.advanceTimersByTime(IDLE_MS - 1);
        expect(onIdle).not.toHaveBeenCalled();
        vi.advanceTimersByTime(1);
        expect(onIdle).toHaveBeenCalledTimes(1);
    });

    it("runs no timer while signed out", () => {
        vi.useFakeTimers();
        const onIdle = vi.fn();
        renderHook(() => useIdleTimeout(onIdle, false));

        vi.advanceTimersByTime(IDLE_MS * 2);
        expect(onIdle).not.toHaveBeenCalled();
    });

    it("uses the latest callback, not the one from first render", () => {
        vi.useFakeTimers();
        const first = vi.fn();
        const second = vi.fn();
        const { rerender } = renderHook(({ fn }) => useIdleTimeout(fn), {
            initialProps: { fn: first },
        });

        rerender({ fn: second });
        vi.advanceTimersByTime(IDLE_MS);

        expect(first).not.toHaveBeenCalled();
        expect(second).toHaveBeenCalledTimes(1);
    });

    it("stops listening once unmounted", () => {
        vi.useFakeTimers();
        const onIdle = vi.fn();
        const { unmount } = renderHook(() => useIdleTimeout(onIdle));

        unmount();
        vi.advanceTimersByTime(IDLE_MS * 2);
        expect(onIdle).not.toHaveBeenCalled();
    });
});

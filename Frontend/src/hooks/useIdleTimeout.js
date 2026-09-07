import { useEffect, useRef } from "react";

/**
 * Sign an idle session out.
 *
 * WHAT COUNTS AS ACTIVITY
 * Pointer, keyboard, scroll and touch. The timer is reset on a trailing edge
 * rather than on every event: a user moving the mouse fires hundreds of
 * mousemove events a second, and resetting a timeout on each one is pure
 * overhead. Listeners are passive and on the capture phase so a stopPropagation
 * inside the app cannot make the session look idle.
 *
 * THE INTERVAL
 * VITE_IDLE_TIMEOUT_MINUTES, defaulting to 60. Set it to 0 to switch the
 * timeout off entirely — worth doing for a screen that is deliberately left
 * displaying something, such as a kitchen station.
 *
 * VITE_IDLE_LOCK_MINUTES is still read as a fallback: it is the name this
 * setting had while idling sent the user to the lock screen instead of signing
 * them out, so a deployment that already sets it keeps working.
 *
 * NOTE ON THE CEILING
 * The access token is issued for ACCESS_TOKEN_EXPIRE_MINUTES (60) from LOGIN,
 * and there is no refresh endpoint, so a session cannot outlive that however
 * active the user is. An idle window at or above 60 minutes will therefore
 * rarely be what ends the session — token expiry gets there first. Raise the
 * token TTL if this window is meant to be the thing that governs.
 *
 * @param {() => void} onIdle  called once when the idle period elapses
 * @param {boolean}    active  false while signed out, so no timer runs
 */
const ACTIVITY_EVENTS = ["pointerdown", "keydown", "wheel", "touchstart", "scroll"];

const DEFAULT_IDLE_MINUTES = 60;

export const IDLE_TIMEOUT_MINUTES = (() => {
    const env = import.meta.env ?? {};
    const raw = Number(
        env.VITE_IDLE_TIMEOUT_MINUTES ?? env.VITE_IDLE_LOCK_MINUTES ?? DEFAULT_IDLE_MINUTES,
    );
    return Number.isFinite(raw) && raw >= 0 ? raw : DEFAULT_IDLE_MINUTES;
})();

export function useIdleTimeout(onIdle, active = true) {
    const onIdleRef = useRef(onIdle);
    useEffect(() => {
        onIdleRef.current = onIdle;
    }, [onIdle]);

    useEffect(() => {
        if (!active || IDLE_TIMEOUT_MINUTES <= 0) return undefined;

        const limitMs = IDLE_TIMEOUT_MINUTES * 60 * 1000;
        let timer = null;
        // Throttle the resets: one per second is plenty for a minutes-long
        // timeout and keeps a mousemove storm from doing any real work.
        let lastReset = 0;

        const arm = () => {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => onIdleRef.current?.(), limitMs);
        };

        const onActivity = () => {
            const now = performance.now();
            if (now - lastReset < 1000) return;
            lastReset = now;
            arm();
        };

        arm();
        for (const evt of ACTIVITY_EVENTS) {
            window.addEventListener(evt, onActivity, { passive: true, capture: true });
        }

        return () => {
            if (timer) clearTimeout(timer);
            for (const evt of ACTIVITY_EVENTS) {
                window.removeEventListener(evt, onActivity, { capture: true });
            }
        };
    }, [active]);
}

export default useIdleTimeout;

import { useEffect, useRef } from "react";

/**
 * Send an idle session to the lock screen.
 *
 * WHY THIS EXISTS
 * Authentication/Pages/LockScreen.jsx was written, styled and wired to
 * re-authenticate against /login_post with the signed-in user's stored email —
 * and then nothing ever navigated to it. The RBAC map generator had been
 * reporting /authentication/lockscreen as an unreachable route for that
 * reason. A terminal left open at a front desk stayed signed in until the JWT
 * expired an hour later, with every screen the role can reach one click away.
 *
 * WHAT COUNTS AS ACTIVITY
 * Pointer, keyboard, scroll and touch. The timer is reset on a trailing edge
 * rather than on every event: a user moving the mouse fires hundreds of
 * mousemove events a second, and resetting a timeout on each one is pure
 * overhead. Listeners are passive and on the capture phase so a stopPropagation
 * inside the app cannot make the session look idle.
 *
 * THE INTERVAL
 * VITE_IDLE_LOCK_MINUTES, defaulting to 5. Set it to 0 to switch the lock off
 * entirely — worth doing for a screen that is deliberately left displaying
 * something, such as a kitchen station.
 *
 * @param {() => void} onIdle  called once when the idle period elapses
 * @param {boolean}    active  false while signed out, so no timer runs
 */
const ACTIVITY_EVENTS = ["pointerdown", "keydown", "wheel", "touchstart", "scroll"];

export const IDLE_LOCK_MINUTES = (() => {
    const raw = Number(import.meta.env?.VITE_IDLE_LOCK_MINUTES ?? 5);
    return Number.isFinite(raw) && raw >= 0 ? raw : 5;
})();

export function useIdleLock(onIdle, active = true) {
    const onIdleRef = useRef(onIdle);
    useEffect(() => {
        onIdleRef.current = onIdle;
    }, [onIdle]);

    useEffect(() => {
        if (!active || IDLE_LOCK_MINUTES <= 0) return undefined;

        const limitMs = IDLE_LOCK_MINUTES * 60 * 1000;
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

export default useIdleLock;

import { useEffect, useRef } from "react";

/**
 * Call a function on an interval, without restarting the interval every time
 * the caller re-renders.
 *
 * WHY THIS EXISTS
 * The kitchen and bar station displays are wall screens: nobody stands at them
 * clicking reload. They loaded once on mount and never again, so a ticket sent
 * from the floor only appeared if a chef navigated away and back.
 *
 * The naive fix — `useEffect(() => setInterval(fn, ms), [fn])` — restarts the
 * timer on every render, because `fn` is a new closure each time, so the
 * interval can end up never firing on a page that re-renders faster than its
 * own period. Holding the callback in a ref keeps one timer for the lifetime
 * of the delay.
 *
 * Pass `delay = null` to stop polling; that is how the screens' auto-refresh
 * switch turns it off, and it also means a hidden or disabled poller holds no
 * timer at all.
 *
 * @param {Function} callback  what to run on each tick
 * @param {number|null} delay  milliseconds between ticks, or null to pause
 */
export function usePolling(callback, delay) {
    const savedCallback = useRef(callback);

    useEffect(() => {
        savedCallback.current = callback;
    }, [callback]);

    useEffect(() => {
        if (delay === null || delay === undefined) return undefined;
        const id = setInterval(() => savedCallback.current?.(), delay);
        return () => clearInterval(id);
    }, [delay]);
}

export default usePolling;

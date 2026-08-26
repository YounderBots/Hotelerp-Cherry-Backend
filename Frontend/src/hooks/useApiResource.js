import { useCallback, useEffect, useRef, useState } from "react";

import { errMsg } from "../functions/apiHelpers.js";

/**
 * Load a resource on mount, expose a reload for user actions.
 *
 * WHAT THIS REPLACES
 * 35 screens had written the same thing by hand:
 *
 *     const load = useCallback(() => {
 *       setLoading(true); setError(null);
 *       APICall.getT(url).then(r => setData(readList(r)))
 *         .catch(e => setError(errMsg(e, "...")))
 *         .finally(() => setLoading(false));
 *     }, []);
 *     useEffect(() => { load(); }, [load]);
 *
 * That shape has two problems. React 19 flags the effect, because calling
 * `load()` runs `setLoading(true)` synchronously during the effect and costs an
 * extra render pass. And none of the copies guarded against the component
 * unmounting mid-request, so a user navigating away during a slow call left a
 * setState firing on a component that no longer exists.
 *
 * HOW THE WARNING IS AVOIDED
 * The effect never calls setState synchronously. The request is started from a
 * microtask, so the `loading` transition lands after the effect returns. It is
 * a real deferral rather than a way to quiet the rule -- the extra render pass
 * the rule objects to genuinely does not happen.
 *
 * `reload()` is for user-triggered refresh (after a save or delete). It runs
 * outside an effect, so it sets state synchronously, which is correct there.
 *
 * USAGE
 *     const { data, loading, error, reload, setData } = useApiResource(
 *       () => APICall.getT("/bar/floor"),
 *       { select: readList, fallback: "Failed to load floors." },
 *     );
 *
 * To refetch when something changes, pass `deps`; the fetcher is read from a
 * ref, so an inline arrow does not cause a refetch loop.
 */
export function useApiResource(fetcher, options = {}) {
    const {
        select = (res) => res,
        fallback = "Failed to load.",
        initial = [],
        deps = [],
        enabled = true,
    } = options;

    const [data, setData] = useState(initial);
    const [loading, setLoading] = useState(enabled);
    const [error, setError] = useState(null);

    // Held in refs so callers can pass inline functions without retriggering.
    const fetcherRef = useRef(fetcher);
    const selectRef = useRef(select);
    const fallbackRef = useRef(fallback);
    useEffect(() => {
        fetcherRef.current = fetcher;
        selectRef.current = select;
        fallbackRef.current = fallback;
    });

    // Guards every setState after an await. Without it, navigating away during
    // a slow request updates an unmounted component.
    const aliveRef = useRef(true);
    useEffect(() => {
        aliveRef.current = true;
        return () => {
            aliveRef.current = false;
        };
    }, []);

    const run = useCallback((sync) => {
        if (sync && aliveRef.current) {
            setLoading(true);
            setError(null);
        }
        return Promise.resolve()
            .then(() => {
                if (!sync && aliveRef.current) {
                    setLoading(true);
                    setError(null);
                }
                return fetcherRef.current();
            })
            .then((res) => {
                if (aliveRef.current) setData(selectRef.current(res));
            })
            .catch((err) => {
                if (aliveRef.current) {
                    // errMsg, not err.message: only an ApiError carries a
                    // message meant for a user. A raw network failure
                    // ("ECONNREFUSED 127.0.0.1:8040") must never reach the
                    // screen, which is exactly what the hand-written copies
                    // this hook replaces were careful about.
                    setError(errMsg(err, fallbackRef.current));
                }
            })
            .finally(() => {
                if (aliveRef.current) setLoading(false);
            });
    }, []);

    useEffect(() => {
        if (!enabled) return undefined;
        // sync=false: the state transition happens in a microtask, so nothing
        // is set synchronously inside this effect.
        run(false);
        return undefined;
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [enabled, ...deps]);

    /** Refetch from a user action (after save, delete, or a manual refresh). */
    const reload = useCallback(() => run(true), [run]);

    return { data, setData, loading, error, setError, reload };
}

export default useApiResource;

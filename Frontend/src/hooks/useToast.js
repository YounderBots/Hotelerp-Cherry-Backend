import { useCallback, useEffect, useRef, useState } from "react";

/**
 * The app's transient success/error banner.
 *
 * WHAT THIS REPLACES
 * Every Master Data screen carried a byte-identical copy of this:
 *
 *     const [alerts, setAlerts] = useState({ show:false, message:"", type:"success", exiting:false });
 *     const showAlert = (message, type = "success") => {
 *       setAlerts({ show:true, message, type, exiting:false });
 *       setTimeout(() => setAlerts(p => ({ ...p, exiting:true })), 1800);
 *       setTimeout(() => setAlerts({ show:false, message:"", type:"success", exiting:false }), 2200);
 *     };
 *
 * Thirteen copies of the same two magic timeouts, none of which cleared its
 * timers. Firing a toast and navigating away inside 2.2s left both setStates
 * pointing at an unmounted component; firing two toasts in quick succession
 * left the first one's timers running, so the second could be cut short by
 * the first one's cleanup.
 *
 * USAGE
 *     const { toast, showToast } = useToast();
 *     showToast("Saved successfully");            // type defaults to "success"
 *     showToast("Delete failed", "error");
 *     <Toast {...toast} />
 *
 * `type` is one of the keys Toast understands: success | update | delete | error.
 */
const VISIBLE_MS = 1800;
const EXIT_MS = 400;

const HIDDEN = { show: false, message: "", type: "success", exiting: false };

export function useToast() {
    const [toast, setToast] = useState(HIDDEN);

    // One timer pair, replaced on every call, cleared on unmount.
    const timers = useRef([]);
    const clearTimers = () => {
        timers.current.forEach(clearTimeout);
        timers.current = [];
    };
    useEffect(() => clearTimers, []);

    const showToast = useCallback((message, type = "success") => {
        clearTimers();
        setToast({ show: true, message, type, exiting: false });
        timers.current = [
            setTimeout(() => setToast((prev) => ({ ...prev, exiting: true })), VISIBLE_MS),
            setTimeout(() => setToast(HIDDEN), VISIBLE_MS + EXIT_MS),
        ];
    }, []);

    const hideToast = useCallback(() => {
        clearTimers();
        setToast(HIDDEN);
    }, []);

    return { toast, showToast, hideToast };
}

export default useToast;

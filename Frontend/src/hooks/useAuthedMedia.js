import { useEffect, useState } from "react";

import APICall from "../APICalls/APICalls";

/**
 * A stored upload, fetched with the session token and handed back as an
 * object URL that an <img src> can use.
 *
 * WHY THIS IS NEEDED
 * Uploads are served by the same authenticated gateway proxy as the JSON API
 * (`/masterdata/templates/static/upload_image/...`, `/user/templates/static/
 * users/...`), and a browser sends no Authorization header on a plain
 * subresource request. So `<img src={mediaUrl(path)}>` is answered with a 401
 * and renders as nothing — which is why every room photo and every employee
 * photo the app had ever saved appeared as an empty slot.
 *
 * AttachmentPreview already solved this for incident attachments by fetching
 * the bytes itself. This is the same fetch, extracted so a plain image slot
 * (ImagePicker in readOnly mode) can use it too, rather than each screen
 * growing its own copy.
 *
 * The object URL is revoked when the path changes or the caller unmounts, so
 * a modal opened and closed repeatedly does not leak one blob per open.
 *
 * ONE FETCH PER FILE, NOT ONE PER CALLER
 * The bytes are cached by (prefix, path) and shared. The Room View grid is why:
 * twenty-five room cards draw four distinct photographs between them, and every
 * card fetched its own copy -- twenty-seven requests to render six images, with
 * the same file pulled down as many as seven times. Callers that mount together
 * now share one in-flight request, and a later mount reuses the bytes.
 *
 * The BLOB is shared, never the object URL: each caller still creates and
 * revokes its own, so one component unmounting cannot invalidate another's src.
 * A failed fetch is dropped from the cache rather than remembered, so a 403
 * during a token refresh does not poison the entry for the rest of the session.
 *
 * @param {string|File|null} path  stored path ("/templates/static/..."), or a
 *                                 File/blob URL/data URL, which are passed
 *                                 through untouched — a freshly picked file
 *                                 needs no fetch.
 * @param {string} prefix          gateway service prefix fronting the static
 *                                 mount, e.g. "/masterdata", "/user", "/hotel".
 * @returns {{url: string|null, status: 'idle'|'loading'|'ready'|'error'}}
 */
// Bounded so a long shift does not retain every image the operator has seen.
// Insertion-ordered, so dropping the oldest key is a plain shift().
const MAX_CACHED = 60;
const cache = new Map();

function fetchOnce(url) {
    const hit = cache.get(url);
    if (hit) return hit;

    const pending = APICall.getBlobT(url).catch((err) => {
        // Never remember a failure: the next mount should try again.
        cache.delete(url);
        throw err;
    });

    cache.set(url, pending);
    while (cache.size > MAX_CACHED) cache.delete(cache.keys().next().value);
    return pending;
}

/** Drop everything cached. For tests, and for a sign-out that changes identity. */
export function clearAuthedMediaCache() {
    cache.clear();
}

export function useAuthedMedia(path, prefix = "") {
    const passthrough =
        path instanceof File ||
        (typeof path === "string" && /^(blob:|data:|https?:)/i.test(path));

    const [state, setState] = useState({ url: null, status: "idle" });

    useEffect(() => {
        if (!path || passthrough) return undefined;

        let alive = true;
        let objectUrl = null;

        // Deferred to a microtask so nothing is set synchronously inside the
        // effect — the same reason useApiResource does it, and what keeps
        // React from charging an extra render pass here.
        Promise.resolve()
            .then(() => {
                if (!alive) return null;
                setState({ url: null, status: "loading" });
                const suffix = String(path).startsWith("/") ? path : `/${path}`;
                return fetchOnce(`${prefix}${suffix}`);
            })
            .then((blob) => {
                if (!alive || !blob) return;
                objectUrl = URL.createObjectURL(blob);
                setState({ url: objectUrl, status: "ready" });
            })
            .catch(() => {
                if (!alive) return;
                setState({ url: null, status: "error" });
            });

        return () => {
            alive = false;
            if (objectUrl) URL.revokeObjectURL(objectUrl);
        };
    }, [path, prefix, passthrough]);

    if (!path) return { url: null, status: "idle" };
    if (passthrough) return { url: path, status: "ready" };
    return state;
}

export default useAuthedMedia;

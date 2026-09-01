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
 * @param {string|File|null} path  stored path ("/templates/static/..."), or a
 *                                 File/blob URL/data URL, which are passed
 *                                 through untouched — a freshly picked file
 *                                 needs no fetch.
 * @param {string} prefix          gateway service prefix fronting the static
 *                                 mount, e.g. "/masterdata", "/user", "/hotel".
 * @returns {{url: string|null, status: 'idle'|'loading'|'ready'|'error'}}
 */
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
                return APICall.getBlobT(`${prefix}${suffix}`);
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

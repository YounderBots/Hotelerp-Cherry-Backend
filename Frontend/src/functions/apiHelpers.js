/**
 * Response and error helpers shared by the data-loading screens.
 *
 * These were copy-pasted into 42 (readList) and 48 (errMsg) components. Beyond
 * the duplication, that made the loading pattern impossible to fix in one
 * place, which is why the same React warning appeared 35 times.
 *
 * Two list readers are exported on purpose. The components had drifted into two
 * different behaviours, and collapsing them into one would silently change what
 * ~30 screens render:
 *
 *   readList        {data: [...]}                     -> the array, else []
 *   readNestedList  {data: [...]} or {data:{data:[]}}  -> the array, else []
 *
 * A screen using `readList` against a nested payload renders nothing today.
 * Switching it to `readNestedList` would start rendering rows that never
 * appeared before -- probably a fix, but a visible change that belongs to
 * whoever audits that screen, not to a refactor. Migrate each call site to the
 * reader it already had.
 */

import { ApiError } from "../APICalls/APICalls";

/** Message from an ApiError, else the caller's fallback. */
export const errMsg = (err, fallback) =>
    err instanceof ApiError && err.message ? err.message : fallback;

/** Array at `res.data`, else an empty array. */
export const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

/** Array at `res.data`, else at `res.data.data`, else an empty array. */
export const readNestedList = (res) => {
    if (Array.isArray(res?.data)) return res.data;
    if (Array.isArray(res?.data?.data)) return res.data.data;
    return [];
};

/*
 * `mediaUrl()` used to live here: it rewrote a stored upload path
 * ("/templates/static/...") to an absolute URL on the API origin, for use as an
 * <img src>. That could never work. Uploads sit behind the same authenticated
 * gateway proxy as the JSON API, and a browser sends no Authorization header on
 * a plain subresource request, so every room photo and employee photo it
 * produced was answered 401 and rendered as an empty slot.
 *
 * The working approach is to fetch the bytes with the session token and show
 * them from an object URL — hooks/useAuthedMedia.js, used by ImagePicker's
 * `authPrefix` prop and by stories/AttachmentPreview.jsx.
 */

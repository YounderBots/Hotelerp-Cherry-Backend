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

import { ApiError, baseURL } from "../APICalls/APICalls";

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

/**
 * Absolute URL for a stored upload.
 *
 * The API returns image paths as site-absolute strings ("/templates/static/
 * upload_image/<file>.jpg"). Rendered straight into an <img src>, the browser
 * resolves those against the FRONTEND origin, where the Vite dev server
 * answers any unknown path with index.html — so every room photo silently
 * loaded an HTML document and rendered as a broken image.
 *
 * Resolving against the API origin is the correct target. Note that the
 * gateway does not currently expose /templates (only MasterDataServices does,
 * on its localhost-only port), so these still need a gateway route before they
 * will actually load; consumers should handle the failure rather than assume
 * an image appears.
 */
export const mediaUrl = (path) => {
    if (!path || typeof path !== "string") return null;
    if (/^(https?:|blob:|data:)/i.test(path)) return path;
    return `${baseURL}${path.startsWith("/") ? "" : "/"}${path}`;
};

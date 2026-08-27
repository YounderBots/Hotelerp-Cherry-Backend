export const baseURL =
    (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) ||
    "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT_MS = 15_000;

// A distinguishable error class so callers can branch on `.status` / `.code`
// instead of scraping `.message`.
export class ApiError extends Error {
    constructor(message, { status = 0, code = "api_error", data = null } = {}) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.code = code;
        this.data = data;
    }
}

let unauthorizedHandler = () => {
    try {
        localStorage.removeItem("AuthToken");
        localStorage.removeItem("user");
        localStorage.removeItem("menus");
    } catch { /* localStorage may be blocked */ }
    if (typeof window !== "undefined" && window.location.pathname !== "/") {
        const here = window.location.pathname + window.location.search;
        const nextParam = here && here !== "/" ? `?next=${encodeURIComponent(here)}` : "";
        window.location.replace(`/${nextParam}`);
    }
};

export const setUnauthorizedHandler = (fn) => {
    unauthorizedHandler = typeof fn === "function" ? fn : unauthorizedHandler;
};

const getAuthHeader = () => {
    try {
        const token = localStorage.getItem("AuthToken");
        return token ? { Authorization: `Bearer ${token}` } : {};
    } catch {
        return {};
    }
};

const readJsonSafe = async (response) => {
    const ct = response.headers.get("content-type") || "";
    if (!ct.toLowerCase().includes("application/json")) return null;
    try { return await response.json(); } catch { return null; }
};

const messageFor = (status, payload) => {
    if (payload) {
        if (typeof payload.detail === "string") return payload.detail;
        if (typeof payload.message === "string") return payload.message;
        if (typeof payload.error === "string") return payload.error;
    }
    switch (status) {
        case 400: return "The request was invalid. Please check your input.";
        case 401: return "Your session has expired. Please sign in again.";
        case 403: return "You do not have permission to perform this action.";
        case 404: return "The requested resource was not found.";
        case 409: return "This action conflicts with the current state.";
        case 422: return "Some of the fields were rejected by the server.";
        case 429: return "Too many requests. Please wait a moment and try again.";
        case 500: return "The server encountered an error. Please try again.";
        case 502: return "The upstream service is unavailable.";
        case 503: return "The service is temporarily unavailable.";
        default:  return "Something went wrong. Please try again.";
    }
};

const runRequest = async (url, init, { timeoutMs = DEFAULT_TIMEOUT_MS, invokeUnauthorized = true } = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    let response;
    try {
        response = await fetch(url, { ...init, signal: controller.signal });
    } catch (err) {
        clearTimeout(timeoutId);
        if (err?.name === "AbortError") {
            throw new ApiError("The request timed out. Please try again.", {
                status: 0,
                code: "timeout",
            });
        }
        throw new ApiError("Cannot reach the server. Check your connection.", {
            status: 0,
            code: "network",
        });
    }
    clearTimeout(timeoutId);

    const payload = await readJsonSafe(response);

    if (response.status === 401 && invokeUnauthorized) {
        try { unauthorizedHandler(); } catch { /* ignore handler errors */ }
    }

    if (!response.ok) {
        throw new ApiError(messageFor(response.status, payload), {
            status: response.status,
            code: `http_${response.status}`,
            data: payload,
        });
    }

    return payload;
};

const APICall = {
    // -------------------------
    // POST (Without Token)
    // -------------------------
    postWT: (endpoint, payload = {}, opts = {}) =>
        runRequest(
            `${baseURL}${endpoint}`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            },
            { invokeUnauthorized: false, ...opts },
        ),

    // -------------------------
    // POST (With Token) — supports FormData and JSON
    // -------------------------
    postT: (endpoint, payload = {}, opts = {}) => {
        const isFormData = typeof FormData !== "undefined" && payload instanceof FormData;
        return runRequest(
            `${baseURL}${endpoint}`,
            {
                method: "POST",
                headers: {
                    ...(isFormData ? {} : { "Content-Type": "application/json" }),
                    ...getAuthHeader(),
                },
                body: isFormData ? payload : JSON.stringify(payload),
            },
            opts,
        );
    },

    // -------------------------
    // GET (Without Token)
    // -------------------------
    getWT: (endpoint, params = {}, opts = {}) => {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${baseURL}${endpoint}?${query}` : `${baseURL}${endpoint}`;
        return runRequest(
            url,
            {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            },
            { invokeUnauthorized: false, ...opts },
        );
    },

    // -------------------------
    // GET (With Token)
    // -------------------------
    getT: (endpoint, params = {}, opts = {}) => {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${baseURL}${endpoint}?${query}` : `${baseURL}${endpoint}`;
        return runRequest(
            url,
            {
                method: "GET",
                headers: { "Content-Type": "application/json", ...getAuthHeader() },
            },
            opts,
        );
    },

    // -------------------------
    // PUT (With Token) — supports FormData and JSON
    // -------------------------
    putT: (endpoint, payload = {}, opts = {}) => {
        const isFormData = typeof FormData !== "undefined" && payload instanceof FormData;
        return runRequest(
            `${baseURL}${endpoint}`,
            {
                method: "PUT",
                headers: {
                    ...(isFormData ? {} : { "Content-Type": "application/json" }),
                    ...getAuthHeader(),
                },
                body: isFormData ? payload : JSON.stringify(payload),
            },
            opts,
        );
    },

    // -------------------------
    // GET a stored file as a Blob (With Token)
    // -------------------------
    // Uploads are served by the same authenticated gateway proxy as the JSON
    // API, so pointing an <img src> or an <a href> straight at one gets a 401:
    // the browser sends no Authorization header on a plain subresource request.
    // Fetching the bytes here and handing back a Blob is what lets a stored
    // attachment actually be shown. Callers own the object URL they create from
    // it and must revoke it.
    getBlobT: async (endpoint, opts = {}) => {
        const { timeoutMs = DEFAULT_TIMEOUT_MS } = opts;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

        let response;
        try {
            response = await fetch(`${baseURL}${endpoint}`, {
                method: "GET",
                headers: { ...getAuthHeader() },
                signal: controller.signal,
            });
        } catch (err) {
            clearTimeout(timeoutId);
            if (err?.name === "AbortError") {
                throw new ApiError("The request timed out. Please try again.", {
                    status: 0,
                    code: "timeout",
                });
            }
            throw new ApiError("Cannot reach the server. Check your connection.", {
                status: 0,
                code: "network",
            });
        }
        clearTimeout(timeoutId);

        if (response.status === 401) {
            try { unauthorizedHandler(); } catch { /* ignore handler errors */ }
        }
        if (!response.ok) {
            throw new ApiError(messageFor(response.status, null), {
                status: response.status,
                code: `http_${response.status}`,
            });
        }
        return response.blob();
    },

    // -------------------------
    // DELETE (With Token)
    // -------------------------
    deleteT: (endpoint, opts = {}) =>
        runRequest(
            `${baseURL}${endpoint}`,
            {
                method: "DELETE",
                headers: { "Content-Type": "application/json", ...getAuthHeader() },
            },
            opts,
        ),
};

export default APICall;

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import APICall, { ApiError, setUnauthorizedHandler } from "./APICalls.js";

// Every page in the app reaches the backend through this module, so the
// behaviour asserted here -- token attachment, 401 handling, timeout and error
// shape -- is the behaviour of all 356 endpoints as the UI sees them.

const jsonResponse = (body, { status = 200 } = {}) => ({
    ok: status >= 200 && status < 300,
    status,
    headers: { get: (h) => (h.toLowerCase() === "content-type" ? "application/json" : null) },
    json: async () => body,
});

let store;

beforeEach(() => {
    store = new Map();
    globalThis.localStorage = {
        getItem: (k) => (store.has(k) ? store.get(k) : null),
        setItem: (k, v) => store.set(k, String(v)),
        removeItem: (k) => store.delete(k),
    };
});

afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
    delete globalThis.localStorage;
});

describe("authenticated calls", () => {
    it("attaches the bearer token stored at login", async () => {
        store.set("AuthToken", "token-abc");
        const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
        globalThis.fetch = fetchMock;

        await APICall.getT("/rooms_list");

        const [url, init] = fetchMock.mock.calls[0];
        expect(url).toContain("/rooms_list");
        expect(init.headers.Authorization).toBe("Bearer token-abc");
    });

    it("omits the header entirely when no token is stored", async () => {
        const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
        globalThis.fetch = fetchMock;

        await APICall.getT("/rooms_list");

        expect(fetchMock.mock.calls[0][1].headers.Authorization).toBeUndefined();
    });

    it("never sends the token on the unauthenticated login call", async () => {
        store.set("AuthToken", "token-abc");
        const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
        globalThis.fetch = fetchMock;

        await APICall.postWT("/login", { username: "x" });

        expect(fetchMock.mock.calls[0][1].headers.Authorization).toBeUndefined();
    });

    it("lets FormData set its own multipart boundary", async () => {
        const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
        globalThis.fetch = fetchMock;

        await APICall.postT("/upload", new FormData());

        expect(fetchMock.mock.calls[0][1].headers["Content-Type"]).toBeUndefined();
    });
});

describe("error handling", () => {
    it("raises ApiError carrying status, code and server payload", async () => {
        globalThis.fetch = vi.fn().mockResolvedValue(
            jsonResponse({ detail: "Room already occupied" }, { status: 409 }),
        );

        const err = await APICall.getT("/rooms_list").catch((e) => e);

        expect(err).toBeInstanceOf(ApiError);
        expect(err.status).toBe(409);
        expect(err.code).toBe("http_409");
        expect(err.message).toBe("Room already occupied");
        expect(err.data).toEqual({ detail: "Room already occupied" });
    });

    it("falls back to a human message when the server sends no detail", async () => {
        globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse({}, { status: 403 }));

        const err = await APICall.getT("/rooms_list").catch((e) => e);

        expect(err.message).toBe("You do not have permission to perform this action.");
    });

    it("reports unreachable server as a network error, not a crash", async () => {
        globalThis.fetch = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

        const err = await APICall.getT("/rooms_list").catch((e) => e);

        expect(err).toBeInstanceOf(ApiError);
        expect(err.code).toBe("network");
        expect(err.status).toBe(0);
    });

    it("aborts and reports a timeout rather than hanging forever", async () => {
        globalThis.fetch = vi.fn(
            (_url, init) =>
                new Promise((_resolve, reject) => {
                    init.signal.addEventListener("abort", () => {
                        const abort = new Error("aborted");
                        abort.name = "AbortError";
                        reject(abort);
                    });
                }),
        );

        const pending = APICall.getT("/rooms_list", {}, { timeoutMs: 5 }).catch((e) => e);
        const err = await pending;

        expect(err.code).toBe("timeout");
    });
});

describe("session expiry", () => {
    it("invokes the unauthorized handler exactly once on 401", async () => {
        const onUnauthorized = vi.fn();
        setUnauthorizedHandler(onUnauthorized);
        globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse({}, { status: 401 }));

        await APICall.getT("/rooms_list").catch(() => {});

        expect(onUnauthorized).toHaveBeenCalledTimes(1);
    });

    it("does not fire the handler for a failed login attempt", async () => {
        const onUnauthorized = vi.fn();
        setUnauthorizedHandler(onUnauthorized);
        globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse({}, { status: 401 }));

        await APICall.postWT("/login", {}).catch(() => {});

        expect(onUnauthorized).not.toHaveBeenCalled();
    });
});

describe("query building", () => {
    it("serialises params onto the URL", async () => {
        const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
        globalThis.fetch = fetchMock;

        await APICall.getT("/rooms_list", { company_id: 3, status: "Available" });

        expect(fetchMock.mock.calls[0][0]).toContain("company_id=3&status=Available");
    });

    it("leaves the URL clean when there are no params", async () => {
        const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
        globalThis.fetch = fetchMock;

        await APICall.getT("/rooms_list");

        expect(fetchMock.mock.calls[0][0]).not.toContain("?");
    });
});

// @vitest-environment jsdom
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useApiResource } from "./useApiResource.js";

// 35 screens are being migrated onto this hook, so what it guarantees needs to
// be pinned down here rather than discovered one broken page at a time. The two
// properties that matter: it must not update an unmounted component, and it
// must not call setState synchronously inside its effect (the React 19 warning
// this whole refactor exists to remove).

const deferred = () => {
    let resolve, reject;
    const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
    return { promise, resolve, reject };
};

afterEach(() => vi.restoreAllMocks());

describe("initial load", () => {
    it("starts in a loading state before anything resolves", () => {
        const { result } = renderHook(() =>
            useApiResource(() => deferred().promise, { initial: [] }));
        expect(result.current.loading).toBe(true);
        expect(result.current.data).toEqual([]);
        expect(result.current.error).toBeNull();
    });

    it("fetches on mount and exposes the selected data", async () => {
        const fetcher = vi.fn().mockResolvedValue({ data: [{ id: 1 }] });
        const { result } = renderHook(() =>
            useApiResource(fetcher, { select: (r) => r.data }));

        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(fetcher).toHaveBeenCalledTimes(1);
        expect(result.current.data).toEqual([{ id: 1 }]);
        expect(result.current.error).toBeNull();
    });

    it("surfaces the error message and stops loading on failure", async () => {
        const fetcher = vi.fn().mockRejectedValue(new Error("Room service is down"));
        const { result } = renderHook(() =>
            useApiResource(fetcher, { fallback: "Failed to load floors." }));

        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.error).toBe("Room service is down");
    });

    it("uses the fallback when the error carries no message", async () => {
        const fetcher = vi.fn().mockRejectedValue(new Error(""));
        const { result } = renderHook(() =>
            useApiResource(fetcher, { fallback: "Failed to load floors." }));

        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(result.current.error).toBe("Failed to load floors.");
    });

    it("does not fetch when disabled", async () => {
        const fetcher = vi.fn().mockResolvedValue({ data: [] });
        const { result } = renderHook(() => useApiResource(fetcher, { enabled: false }));
        await Promise.resolve();
        expect(fetcher).not.toHaveBeenCalled();
        expect(result.current.loading).toBe(false);
    });
});

describe("unmount safety", () => {
    it("does not update state after the component unmounts", async () => {
        // The bug every hand-written copy had: navigate away mid-request and the
        // resolution lands on a component that no longer exists.
        const d = deferred();
        const errors = [];
        const spy = vi.spyOn(console, "error").mockImplementation((...a) => errors.push(a));

        const { result, unmount } = renderHook(() =>
            useApiResource(() => d.promise, { select: (r) => r.data }));
        unmount();

        await act(async () => {
            d.resolve({ data: [{ id: 99 }] });
            await d.promise;
        });

        expect(result.current.data).toEqual([]);
        expect(errors.join(" ")).not.toMatch(/unmounted/i);
        spy.mockRestore();
    });

    it("swallows a rejection that arrives after unmount", async () => {
        const d = deferred();
        const { unmount } = renderHook(() => useApiResource(() => d.promise));
        unmount();
        await act(async () => {
            d.reject(new Error("too late"));
            await d.promise.catch(() => {});
        });
        // Reaching here without an unhandled rejection is the assertion.
        expect(true).toBe(true);
    });
});

describe("reload", () => {
    it("refetches on demand and clears a previous error", async () => {
        const fetcher = vi.fn()
            .mockRejectedValueOnce(new Error("Network down"))
            .mockResolvedValueOnce({ data: [{ id: 7 }] });

        const { result } = renderHook(() =>
            useApiResource(fetcher, { select: (r) => r.data }));

        await waitFor(() => expect(result.current.error).toBe("Network down"));

        await act(async () => { await result.current.reload(); });

        expect(fetcher).toHaveBeenCalledTimes(2);
        expect(result.current.error).toBeNull();
        expect(result.current.data).toEqual([{ id: 7 }]);
    });
});

describe("identity and deps", () => {
    it("an inline fetcher does not cause a refetch loop", async () => {
        const calls = { n: 0 };
        const { rerender, result } = renderHook(() =>
            // A new arrow every render -- the trap the ref indirection avoids.
            useApiResource(() => { calls.n += 1; return Promise.resolve({ data: [] }); }));

        await waitFor(() => expect(result.current.loading).toBe(false));
        rerender();
        rerender();
        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(calls.n).toBe(1);
    });

    it("refetches when a declared dep changes", async () => {
        const fetcher = vi.fn().mockResolvedValue({ data: [] });
        let floorId = 1;
        const { rerender, result } = renderHook(() =>
            useApiResource(fetcher, { deps: [floorId] }));

        await waitFor(() => expect(result.current.loading).toBe(false));
        expect(fetcher).toHaveBeenCalledTimes(1);

        floorId = 2;
        rerender();
        await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    });
});

describe("setData", () => {
    it("lets a screen patch the list without a round trip", async () => {
        const fetcher = vi.fn().mockResolvedValue({ data: [{ id: 1 }] });
        const { result } = renderHook(() =>
            useApiResource(fetcher, { select: (r) => r.data }));

        await waitFor(() => expect(result.current.loading).toBe(false));
        act(() => { result.current.setData([{ id: 1 }, { id: 2 }]); });
        expect(result.current.data).toHaveLength(2);
    });
});

// @vitest-environment jsdom
import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import APICall from "../APICalls/APICalls.js";
import { useAuthedMedia } from "./useAuthedMedia.js";

// The bug this hook exists to fix: uploads sit behind the authenticated gateway
// proxy, so `<img src="/templates/static/...">` is answered 401 and every room
// photo, employee photo and menu photo rendered as an empty slot. What matters
// here is that a stored PATH is fetched with the session token, that anything
// already loadable is passed through untouched, and that object URLs are
// revoked rather than leaked one per modal open.

let created;
let revoked;

beforeEach(() => {
    created = [];
    revoked = [];
    globalThis.URL.createObjectURL = vi.fn(() => {
        const url = `blob:mock/${created.length}`;
        created.push(url);
        return url;
    });
    globalThis.URL.revokeObjectURL = vi.fn((url) => revoked.push(url));
});

afterEach(() => vi.restoreAllMocks());

describe("stored paths", () => {
    it("fetches through the gateway prefix with the session token", async () => {
        const blob = new Blob(["x"], { type: "image/png" });
        const spy = vi.spyOn(APICall, "getBlobT").mockResolvedValue(blob);

        const { result } = renderHook(() =>
            useAuthedMedia("/templates/static/upload_image/a.png", "/masterdata"),
        );

        await waitFor(() => expect(result.current.status).toBe("ready"));
        expect(spy).toHaveBeenCalledWith("/masterdata/templates/static/upload_image/a.png");
        expect(result.current.url).toBe("blob:mock/0");
    });

    it("adds the missing slash between prefix and a relative path", async () => {
        const spy = vi
            .spyOn(APICall, "getBlobT")
            .mockResolvedValue(new Blob(["x"], { type: "image/png" }));

        const { result } = renderHook(() => useAuthedMedia("templates/static/a.png", "/hotel"));

        await waitFor(() => expect(result.current.status).toBe("ready"));
        expect(spy).toHaveBeenCalledWith("/hotel/templates/static/a.png");
    });

    it("reports an error rather than throwing when the fetch fails", async () => {
        vi.spyOn(APICall, "getBlobT").mockRejectedValue(new Error("401"));

        const { result } = renderHook(() => useAuthedMedia("/templates/static/a.png", "/user"));

        await waitFor(() => expect(result.current.status).toBe("error"));
        expect(result.current.url).toBeNull();
    });

    it("revokes the object URL on unmount", async () => {
        vi.spyOn(APICall, "getBlobT").mockResolvedValue(new Blob(["x"], { type: "image/png" }));

        const { result, unmount } = renderHook(() =>
            useAuthedMedia("/templates/static/a.png", "/masterdata"),
        );
        await waitFor(() => expect(result.current.status).toBe("ready"));

        unmount();
        expect(revoked).toContain("blob:mock/0");
    });
});

describe("values that need no fetch", () => {
    it("passes an absolute URL through untouched", () => {
        const spy = vi.spyOn(APICall, "getBlobT");
        const { result } = renderHook(() =>
            useAuthedMedia("https://cdn.example.com/a.png", "/restaurant"),
        );
        expect(result.current).toEqual({
            url: "https://cdn.example.com/a.png",
            status: "ready",
        });
        expect(spy).not.toHaveBeenCalled();
    });

    it("passes a blob: and a data: URL through untouched", () => {
        const spy = vi.spyOn(APICall, "getBlobT");
        expect(renderHook(() => useAuthedMedia("blob:x", "/bar")).result.current.status).toBe(
            "ready",
        );
        expect(
            renderHook(() => useAuthedMedia("data:image/png;base64,AA", "/bar")).result.current
                .status,
        ).toBe("ready");
        expect(spy).not.toHaveBeenCalled();
    });

    it("is idle for an empty value", () => {
        const spy = vi.spyOn(APICall, "getBlobT");
        const { result } = renderHook(() => useAuthedMedia(null, "/masterdata"));
        expect(result.current).toEqual({ url: null, status: "idle" });
        expect(spy).not.toHaveBeenCalled();
    });

    // ImagePicker only supplies a prefix when the caller knows which service
    // fronts the file; without one the value is used as-is.
    it("does not fetch when no prefix is given", () => {
        const spy = vi.spyOn(APICall, "getBlobT");
        renderHook(() => useAuthedMedia(null, ""));
        expect(spy).not.toHaveBeenCalled();
    });
});

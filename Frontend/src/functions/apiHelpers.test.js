import { describe, expect, it } from "vitest";

import { ApiError } from "../APICalls/APICalls.js";
import { errMsg, readList, readNestedList } from "./apiHelpers.js";

// These helpers were copy-pasted into 42-48 components. Consolidating them is
// only safe if the shared versions behave exactly as the copies did, so the
// difference between the two list readers is pinned down here rather than left
// to whoever migrates the next screen.

describe("errMsg", () => {
    it("uses the ApiError message when there is one", () => {
        expect(errMsg(new ApiError("Room is already booked"), "fallback"))
            .toBe("Room is already booked");
    });

    it("falls back when the ApiError carries no message", () => {
        expect(errMsg(new ApiError(""), "Failed to load floors."))
            .toBe("Failed to load floors.");
    });

    it("falls back for a plain Error, so backend internals never reach the UI", () => {
        expect(errMsg(new Error("ECONNREFUSED 127.0.0.1:8040"), "Failed to load."))
            .toBe("Failed to load.");
    });

    it("falls back for null and undefined", () => {
        expect(errMsg(null, "fallback")).toBe("fallback");
        expect(errMsg(undefined, "fallback")).toBe("fallback");
    });
});

describe("readList", () => {
    it("returns the array at res.data", () => {
        expect(readList({ data: [1, 2] })).toEqual([1, 2]);
    });

    it("returns [] for a nested payload -- the behaviour its call sites have today", () => {
        expect(readList({ data: { data: [1, 2] } })).toEqual([]);
    });

    it("returns [] for missing, null and non-array payloads", () => {
        expect(readList(undefined)).toEqual([]);
        expect(readList(null)).toEqual([]);
        expect(readList({})).toEqual([]);
        expect(readList({ data: "not an array" })).toEqual([]);
    });
});

describe("readNestedList", () => {
    it("returns the array at res.data", () => {
        expect(readNestedList({ data: [1, 2] })).toEqual([1, 2]);
    });

    it("also unwraps res.data.data -- the one real difference from readList", () => {
        expect(readNestedList({ data: { data: [1, 2] } })).toEqual([1, 2]);
    });

    it("returns [] when neither level holds an array", () => {
        expect(readNestedList({ data: { data: "nope" } })).toEqual([]);
        expect(readNestedList(undefined)).toEqual([]);
    });
});

describe("the two readers differ only on nested payloads", () => {
    it.each([
        [{ data: [1] }],
        [undefined],
        [null],
        [{}],
        [{ data: "x" }],
    ])("agree on %o", (input) => {
        expect(readList(input)).toEqual(readNestedList(input));
    });

    it("disagree on {data:{data:[...]}} -- why call sites must keep their own reader", () => {
        const nested = { data: { data: [1] } };
        expect(readList(nested)).toEqual([]);
        expect(readNestedList(nested)).toEqual([1]);
    });
});

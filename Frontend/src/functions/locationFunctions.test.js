import { describe, expect, it } from "vitest";

import findMenuByPath from "./locationFunctions.js";

// The router matches routes case-insensitively, so a hand-typed or bookmarked
// URL can differ from the canonical menu path only in letter case. The sidebar
// highlight used to compare raw bytes and left such a page with no active row
// (C-081); these pin the case-insensitive behaviour and the prefix rules it has
// to keep.

const menu = [
    { path: "/dashboard", menu_name: "Dashboard" },
    {
        path: "/master_data",
        menu_name: "Master Data",
        children: [
            { path: "/facilities", menu_name: "Facilities" },
            { path: "/identification_proof", menu_name: "Identification Proof" },
            { path: "/tax_types", menu_name: "Tax Types" },
        ],
    },
    {
        path: "/restaurant",
        menu_name: "Restaurant",
        children: [{ path: "/orders", menu_name: "Orders" }],
    },
];

describe("findMenuByPath", () => {
    it("finds a top-level path", () => {
        const result = findMenuByPath(menu, "/dashboard");
        expect(result.activeMenu.menu_name).toBe("Dashboard");
        expect(result.activePath).toEqual([]);
    });

    it("finds a submenu leaf and returns the click path to it", () => {
        const result = findMenuByPath(menu, "/orders");
        expect(result.activeMenu.menu_name).toBe("Restaurant");
        expect(result.activePath).toEqual([0]);
    });

    it("finds a submenu leaf nested one level deeper", () => {
        const result = findMenuByPath(menu, "/tax_types");
        expect(result.activeMenu.menu_name).toBe("Master Data");
        expect(result.activePath).toEqual([2]);
    });

    it("matches a case-variant submenu path (C-081)", () => {
        const result = findMenuByPath(menu, "/Identification_Proof");
        expect(result.activeMenu.menu_name).toBe("Master Data");
        expect(result.activePath).toEqual([1]);
    });

    it("matches a case-variant top-level path (C-081)", () => {
        expect(findMenuByPath(menu, "/Dashboard").activeMenu.menu_name).toBe("Dashboard");
    });

    it("matches a mixed-case canonical path such as /ReservationView", () => {
        const mixed = [{ path: "/ReservationView", menu_name: "Reservation View" }];
        expect(findMenuByPath(mixed, "/ReservationView").activeMenu.menu_name).toBe("Reservation View");
    });

    it("matches a child path on its parent prefix", () => {
        const result = findMenuByPath([{ path: "/reservation", menu_name: "Reservation" }], "/reservation/25");
        expect(result.activeMenu.menu_name).toBe("Reservation");
    });

    it("does not treat a longer word as a prefix match", () => {
        expect(findMenuByPath([{ path: "/reservation", menu_name: "Reservation" }], "/reservations"))
            .toBeNull();
    });

    it("returns null for an unknown path", () => {
        expect(findMenuByPath(menu, "/no_such_page_qa")).toBeNull();
    });

    it("returns null for an empty or invalid menu", () => {
        expect(findMenuByPath([], "/dashboard")).toBeNull();
        expect(findMenuByPath(null, "/dashboard")).toBeNull();
    });

    it("does not throw on a missing pathname", () => {
        expect(findMenuByPath(menu, undefined)).toBeNull();
    });
});

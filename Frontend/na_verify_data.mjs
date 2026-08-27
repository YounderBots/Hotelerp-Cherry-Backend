/**
 * Night Audit -- data-path verification.
 *
 * The first pass proved the pages render cleanly, but on the current business
 * date, which has no occupancy, so every figure was legitimately 0. This pass
 * drives the date filter to a night that DOES have data and checks the screen
 * shows the same numbers the API does -- specifically that the rows in the
 * table sum to the total in the stat tile, which is the property that makes
 * the report reconcilable.
 *
 * Usage: node na_verify_data.mjs
 */
import { chromium } from "playwright";
import { mkdirSync } from "fs";

const BASE = "http://127.0.0.1:5173";
const API = "http://127.0.0.1:8000";
const EMAIL = "admin@hotel.com";
const PASSWORD = "Admin@123";
const NIGHT = "2026-08-01";
const OUT = ".pw/night-audit";

mkdirSync(OUT, { recursive: true });

const results = [];
const record = (label, ok, detail = "") => {
    results.push({ label, ok, detail });
    console.log(`  [${ok ? "PASS" : "FAIL"}] ${label}${detail ? `  ${detail}` : ""}`);
};

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();

const consoleErrors = [];
page.on("console", (m) => {
    if (m.type() === "error" && !/favicon|\[vite\]|DevTools/i.test(m.text())) {
        consoleErrors.push(m.text());
    }
});

console.log("=".repeat(74));
await page.goto(BASE + "/", { waitUntil: "networkidle" });
await page.fill('input[type="email"], input[name="email"]', EMAIL);
await page.fill('input[type="password"], input[name="password"]', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(/dashboard/, { timeout: 20000 });
console.log("logged in");

// Ground truth straight from the API, using the browser's own token.
const token = await page.evaluate(() => localStorage.getItem("AuthToken"));
const truth = await page.evaluate(
    async ([api, night, tok]) => {
        const r = await fetch(`${api}/hotel/night_audit/preview?business_date=${night}`, {
            headers: { Authorization: `Bearer ${tok}` },
        });
        return (await r.json()).data;
    },
    [API, NIGHT, token],
);
console.log(`API truth for ${NIGHT}: room_revenue=${truth.revenue.room_revenue} ` +
    `gross=${truth.revenue.gross_revenue} rooms=${truth.occupancy.rooms_occupied} ` +
    `occupying=${truth.lists.occupying.length}`);

// ---------------------------------------------------------------- Room Booked
console.log("=".repeat(74));
console.log(`Room Booked Details @ ${NIGHT}`);
await page.goto(BASE + "/room_booked_details", { waitUntil: "networkidle" });
await page.fill("#rb-date", NIGHT);
await page.waitForTimeout(1200);

const subtitle = await page.locator(".na-report__subtitle").first().textContent();
record("subtitle names the audited night", /1 Aug 2026/.test(subtitle), subtitle.trim().slice(0, 68));

const tiles = await page.locator(".na-stat").allTextContents();
const tileText = tiles.join(" | ");
record("rooms sold tile matches API",
    tileText.includes(String(truth.occupancy.rooms_occupied)),
    `expected ${truth.occupancy.rooms_occupied}`);
record("room revenue tile matches API",
    tileText.includes(new Intl.NumberFormat("en-US").format(Math.round(truth.revenue.room_revenue))) ||
    tileText.includes(new Intl.NumberFormat("en-IN").format(Math.round(truth.revenue.room_revenue))),
    `expected ${truth.revenue.room_revenue}`);

// The reconcilable property: the Night Revenue column must sum to the total.
const cellSum = await page.evaluate(() => {
    const table = document.querySelector("table");
    if (!table) return null;
    const headers = [...table.querySelectorAll("thead th")].map((th) => th.textContent.trim());
    const col = headers.findIndex((h) => /Night Revenue/i.test(h));
    if (col < 0) return null;
    let total = 0;
    for (const tr of table.querySelectorAll("tbody tr")) {
        const cell = tr.children[col];
        if (!cell) continue;
        const n = Number(cell.textContent.replace(/[^0-9.-]/g, ""));
        if (Number.isFinite(n)) total += n;
    }
    return Math.round(total * 100) / 100;
});
// Page size is 10 and there are 10 occupying rows, so one page holds them all.
record("Night Revenue column sums to the API total",
    cellSum !== null && Math.abs(cellSum - truth.revenue.room_revenue) < 0.02,
    `table=${cellSum} api=${truth.revenue.room_revenue}`);

// Scoped to the VISIBLE table. TableTemplate also renders a second,
// off-screen `#export-table-full` (positioned at x=-9999) that the PDF export
// reads from, so a bare `table tbody tr` counts every row twice.
const rowCount = await page.locator(".table-wrapper table tbody tr").count();
record("row count matches occupying list",
    rowCount === truth.lists.occupying.length,
    `${rowCount} rows vs ${truth.lists.occupying.length}`);

await page.screenshot({ path: `${OUT}/room-booked-data-1440.png`, fullPage: true });
await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(400);
await page.screenshot({ path: `${OUT}/room-booked-data-390.png`, fullPage: true });
await page.setViewportSize({ width: 1440, height: 900 });

// --------------------------------------------------------------- Settlement
console.log("=".repeat(74));
console.log(`Settlement Summary @ ${NIGHT}`);
await page.goto(BASE + "/settlement_summary", { waitUntil: "networkidle" });
await page.fill("#ss-date", NIGHT);
await page.waitForTimeout(1200);

const ssTiles = (await page.locator(".na-stat").allTextContents()).join(" | ");
record("outstanding tile matches API",
    ssTiles.includes(new Intl.NumberFormat("en-US").format(Math.round(truth.settlement.outstanding_balance))) ||
    ssTiles.includes(new Intl.NumberFormat("en-IN").format(Math.round(truth.settlement.outstanding_balance))),
    `expected ${truth.settlement.outstanding_balance}`);
record("gross revenue tile matches API",
    ssTiles.includes(new Intl.NumberFormat("en-US").format(Math.round(truth.revenue.gross_revenue))) ||
    ssTiles.includes(new Intl.NumberFormat("en-IN").format(Math.round(truth.revenue.gross_revenue))),
    `expected ${truth.revenue.gross_revenue}`);

const unsettledTab = await page.locator(".tab-button, [role='tab'], button").filter({ hasText: /Unsettled/ }).first().textContent().catch(() => "");
record("unsettled tab count matches API",
    unsettledTab.includes(String(truth.lists.unsettled_folios.length)),
    `${unsettledTab.trim()} vs ${truth.lists.unsettled_folios.length}`);

await page.screenshot({ path: `${OUT}/settlement-data-1440.png`, fullPage: true });

// ---- View modal opens and shows the per-night accrual ----
await page.locator("table tbody tr").first().locator("button[title^='View']").click();
await page.waitForTimeout(600);
const modalVisible = await page.locator(".modal-content, [role='dialog']").count();
record("View modal opens", modalVisible > 0);
const modalText = await page.locator("[role='dialog']").first().textContent().catch(() => "");
record("modal shows the accrual section", /Accrued for/i.test(modalText));
record("modal shows folio section", /Folio/i.test(modalText));
await page.screenshot({ path: `${OUT}/settlement-modal-1440.png` });

console.log("=".repeat(74));
record("no console errors across the run", consoleErrors.length === 0,
    consoleErrors.slice(0, 2).join(" ⏐ ").slice(0, 120));

const failed = results.filter((r) => !r.ok);
console.log(`RESULT: ${results.length - failed.length}/${results.length} passed`);
if (failed.length) {
    console.log("\nFAILURES:");
    failed.forEach((f) => console.log(`  - ${f.label}  ${f.detail}`));
}
console.log(`\nScreenshots in Frontend/${OUT}/`);

await browser.close();
process.exit(failed.length ? 1 : 0);

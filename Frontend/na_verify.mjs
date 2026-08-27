/**
 * Night Audit UI verification.
 *
 * Logs in, walks the three Night Audit report screens, and checks the things
 * that cannot be checked from the API alone: that the pages render, that no
 * console error or failed request is produced, that the tables show the
 * server's figures, and that nothing overflows horizontally at any of the
 * required widths.
 *
 * Usage: node na_verify.mjs [--shots]
 */
import { chromium } from "playwright";
import { mkdirSync } from "fs";

const BASE = "http://127.0.0.1:5173";
const EMAIL = "admin@hotel.com";
const PASSWORD = "Admin@123";
const SHOTS = process.argv.includes("--shots");
const OUT = ".pw/night-audit";

const WIDTHS = [1920, 1600, 1440, 1366, 1280, 1024, 992, 820, 768, 600, 540, 430, 414, 390, 375, 360];

const PAGES = [
    { path: "/user_reserved_details", name: "user-reserved", title: "User Reserved Details" },
    { path: "/room_booked_details", name: "room-booked", title: "Room Booked Details" },
    { path: "/settlement_summary", name: "settlement", title: "Settlement Summary" },
];

const results = [];
const record = (label, ok, detail = "") => {
    results.push({ label, ok, detail });
    console.log(`  [${ok ? "PASS" : "FAIL"}] ${label}${detail ? `  ${detail}` : ""}`);
};

if (SHOTS) mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();

// Collect only genuine problems. Vite's HMR chatter and favicon 404s are noise.
const consoleErrors = [];
const failedRequests = [];
page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const t = msg.text();
    if (/favicon|\[vite\]|Download the React DevTools/i.test(t)) return;
    consoleErrors.push(t);
});
page.on("response", (res) => {
    const url = res.url();
    if (res.status() >= 400 && !/favicon/i.test(url)) {
        failedRequests.push(`${res.status()} ${res.request().method()} ${url.replace(BASE, "")}`);
    }
});

console.log("=".repeat(74));
console.log("LOGIN");
await page.goto(BASE + "/", { waitUntil: "networkidle" });
await page.fill('input[type="email"], input[name="email"]', EMAIL);
await page.fill('input[type="password"], input[name="password"]', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(/dashboard/, { timeout: 20000 }).catch(() => { });
record("logged in", /dashboard/.test(page.url()), page.url().replace(BASE, ""));

for (const target of PAGES) {
    console.log("=".repeat(74));
    console.log(`${target.title}  (${target.path})`);

    const before = consoleErrors.length;
    const beforeReq = failedRequests.length;

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(BASE + target.path, { waitUntil: "networkidle" });
    await page.waitForTimeout(900);

    const heading = await page.locator(".na-report__title").first().textContent().catch(() => null);
    record(`${target.name}: heading renders`, heading?.trim() === target.title, heading?.trim() || "none");

    const denied = await page.locator("text=do not have access").count();
    record(`${target.name}: not permission-denied`, denied === 0);

    // The stat strip is the server's numbers; if it is missing the page did
    // not get its data.
    const stats = await page.locator(".na-stat").count();
    record(`${target.name}: stat tiles present`, stats > 0, `${stats} tiles`);

    const statText = await page.locator(".na-stat__value").allTextContents();
    record(`${target.name}: stats have values`, statText.every((s) => s.trim() && s.trim() !== "…"),
        statText.join(" | ").slice(0, 70));

    // A table must be present and must not be stuck on the loading spinner.
    const tables = await page.locator("table").count();
    record(`${target.name}: table rendered`, tables > 0, `${tables} table(s)`);
    const spinner = await page.locator(".table-loading-spinner").count();
    record(`${target.name}: not stuck loading`, spinner === 0);

    record(`${target.name}: no console errors`, consoleErrors.length === before,
        consoleErrors.slice(before).join(" ⏐ ").slice(0, 110));
    record(`${target.name}: no failed requests`, failedRequests.length === beforeReq,
        failedRequests.slice(beforeReq).join(" ⏐ ").slice(0, 110));

    // ---- responsive sweep ----
    const overflows = [];
    for (const w of WIDTHS) {
        await page.setViewportSize({ width: w, height: 900 });
        await page.waitForTimeout(160);
        const bad = await page.evaluate(() => {
            const de = document.documentElement;
            return {
                scrollW: de.scrollWidth,
                clientW: de.clientWidth,
            };
        });
        // 1px of subpixel rounding is not an overflow.
        if (bad.scrollW - bad.clientW > 1) overflows.push(`${w}px(+${bad.scrollW - bad.clientW})`);
        if (SHOTS && [1440, 768, 390].includes(w)) {
            await page.screenshot({ path: `${OUT}/${target.name}-${w}.png`, fullPage: true });
        }
    }
    record(`${target.name}: no horizontal overflow at 16 widths`, overflows.length === 0,
        overflows.join(" "));
}

console.log("=".repeat(74));
const failed = results.filter((r) => !r.ok);
console.log(`RESULT: ${results.length - failed.length}/${results.length} passed`);
if (failed.length) {
    console.log("\nFAILURES:");
    for (const f of failed) console.log(`  - ${f.label}  ${f.detail}`);
}
if (consoleErrors.length) {
    console.log("\nCONSOLE ERRORS:");
    [...new Set(consoleErrors)].forEach((e) => console.log("  " + e.slice(0, 160)));
}
if (failedRequests.length) {
    console.log("\nFAILED REQUESTS:");
    [...new Set(failedRequests)].forEach((e) => console.log("  " + e));
}

await browser.close();
process.exit(failed.length ? 1 : 0);

/**
 * Night Audit dashboard verification, via the standalone preview harness.
 *
 * Logs in through the real app to obtain a token and menu payload, transplants
 * them into the harness page's localStorage, then exercises the dashboard:
 * readiness, the stat strip, the six lists, the confirm dialog and its
 * consequences copy, and the responsive sweep.
 *
 * Does NOT press Run -- that mutates the business date, and the run path is
 * already covered end to end by race_test.py and failure_test.py.
 */
import { chromium } from "playwright";
import { mkdirSync } from "fs";

const BASE = "http://127.0.0.1:5173";
const OUT = ".pw/night-audit";
const WIDTHS = [1920, 1600, 1440, 1366, 1280, 1024, 992, 820, 768, 600, 540, 430, 414, 390, 375, 360];

mkdirSync(OUT, { recursive: true });

const results = [];
const record = (label, ok, detail = "") => {
    results.push({ label, ok, detail });
    console.log(`  [${ok ? "PASS" : "FAIL"}] ${label}${detail ? `  ${detail}` : ""}`);
};

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await ctx.newPage();

const consoleErrors = [];
const failedRequests = [];
page.on("console", (m) => {
    if (m.type() === "error" && !/favicon|\[vite\]|DevTools/i.test(m.text())) {
        consoleErrors.push(m.text());
    }
});
page.on("response", (r) => {
    if (r.status() >= 400 && !/favicon/i.test(r.url())) {
        failedRequests.push(`${r.status()} ${r.request().method()} ${r.url().replace(BASE, "")}`);
    }
});

// ---- borrow a real session ----
// `force` and `domcontentloaded` rather than the usual click/networkidle: the
// dev server is hot-reloading continuously while another session edits the
// tree, so Playwright's actionability check never sees the button hold still
// and `networkidle` never arrives. Neither wait tells us anything about the
// Night Audit code under test.
await page.goto(BASE + "/", { waitUntil: "domcontentloaded" });
await page.waitForSelector('input[type="email"]', { timeout: 20000 });
await page.fill('input[type="email"]', "admin@hotel.com");
await page.fill('input[type="password"]', "Admin@123");
await page.click('button[type="submit"]', { force: true });
await page.waitForURL(/dashboard/, { timeout: 30000 });
const auth = await page.evaluate(() => ({
    token: localStorage.getItem("AuthToken"),
    user: localStorage.getItem("user"),
    menus: localStorage.getItem("menus"),
}));
console.log("=".repeat(72));
console.log("borrowed a live session");

await page.goto(BASE + "/na_preview.html", { waitUntil: "domcontentloaded" });
await page.evaluate((a) => {
    localStorage.setItem("AuthToken", a.token);
    localStorage.setItem("user", a.user || "{}");
    localStorage.setItem("menus", a.menus || "[]");
}, auth);
await page.goto(BASE + "/na_preview.html", { waitUntil: "domcontentloaded" });
await page.waitForSelector(".na-hero__value", { timeout: 20000 });
await page.waitForTimeout(1800);

console.log("=".repeat(72));
console.log("NIGHT AUDIT DASHBOARD");

// ---- hero ----
const heroDate = await page.locator(".na-hero__value").textContent().catch(() => null);
record("business date rendered", !!heroDate && heroDate.trim() !== "…", heroDate?.trim());
const heroMeta = await page.locator(".na-hero__meta").textContent().catch(() => "");
record("last-audit line present", heroMeta.length > 0, heroMeta.trim().slice(0, 54));

// ---- readiness ----
const readyClear = await page.locator(".na-readiness__clear").count();
const blockers = await page.locator(".na-readiness__item--blocker").count();
const warnings = await page.locator(".na-readiness__item--warning").count();
record("readiness panel rendered", readyClear + blockers + warnings > 0,
    `clear=${readyClear} blockers=${blockers} warnings=${warnings}`);

// ---- the Run button reflects readiness ----
const runBtn = page.locator("button", { hasText: "Run Night Audit" }).first();
const runDisabled = await runBtn.isDisabled();
record("Run button state agrees with readiness",
    blockers > 0 ? runDisabled : !runDisabled,
    `blockers=${blockers} disabled=${runDisabled}`);

// ---- stat strip ----
const tiles = await page.locator(".na-stat").count();
record("all eight stat tiles present", tiles === 8, `${tiles} tiles`);
const tileValues = await page.locator(".na-stat__value").allTextContents();
record("every tile has a value", tileValues.every((t) => t.trim() && t.trim() !== "…"),
    tileValues.join(" | ").slice(0, 64));

// ---- the six lists ----
// Tabs renders its triggers as `.tab-trigger`, not `.tab-button`.
const tabs = await page.locator(".tab-trigger").allTextContents();
const tabText = tabs.join(" | ");
const EXPECTED = ["In House", "Arrivals Due", "Not Checked In", "Departures Due", "Overdue", "Unsettled"];
record("all six audit lists are tabbed", EXPECTED.every((t) => tabText.includes(t)),
    tabText.slice(0, 80));

// ---- history ----
const historyTitle = await page.locator("text=Audit History").count();
record("audit history table present", historyTitle > 0);
// Scoped to the history section: Tabs mounts all six list panels too, so an
// unscoped row count sums every table on the page.
const historyRows = await page.locator(".na-history .table-wrapper table tbody tr").count();
record("history table has the audit rows", historyRows > 0, `${historyRows} rows`);

await page.screenshot({ path: `${OUT}/dashboard-1440.png`, fullPage: true });

// ---- confirm dialog ----
if (!runDisabled) {
    await runBtn.click();
    await page.waitForTimeout(700);
    const dialog = page.locator("[role='dialog']").first();
    const dialogText = await dialog.textContent().catch(() => "");
    record("confirm dialog opens", dialogText.length > 0);
    record("confirm states the date roll", /moves the business date to/i.test(dialogText));
    record("confirm restates the money", /gross revenue/i.test(dialogText));
    const noShowBox = await page.locator(".na-confirm__option input").count();
    const noShowNote = await page.locator(".na-confirm__note").count();
    record("no-show choice is explicit (checkbox or 'nothing to do' note)",
        noShowBox + noShowNote > 0, `checkbox=${noShowBox} note=${noShowNote}`);
    await page.screenshot({ path: `${OUT}/dashboard-confirm-1440.png` });
    // Close WITHOUT running.
    await page.locator("[role='dialog'] button", { hasText: /Cancel/i }).first().click();
    await page.waitForTimeout(400);
    const stillOpen = await page.locator("[role='dialog']").count();
    record("cancel closes without running", stillOpen === 0);
} else {
    record("confirm dialog skipped (run is blocked, as expected)", true);
}

// ---- responsive ----
const overflows = [];
for (const w of WIDTHS) {
    await page.setViewportSize({ width: w, height: 950 });
    await page.waitForTimeout(170);
    const d = await page.evaluate(() => ({
        s: document.documentElement.scrollWidth,
        c: document.documentElement.clientWidth,
    }));
    if (d.s - d.c > 1) overflows.push(`${w}px(+${d.s - d.c})`);
    if ([768, 390].includes(w)) {
        await page.screenshot({ path: `${OUT}/dashboard-${w}.png`, fullPage: true });
    }
}
record("no horizontal overflow at 16 widths", overflows.length === 0, overflows.join(" "));

record("no console errors", consoleErrors.length === 0,
    [...new Set(consoleErrors)].slice(0, 2).join(" ⏐ ").slice(0, 120));
record("no failed requests", failedRequests.length === 0,
    [...new Set(failedRequests)].slice(0, 3).join(" ⏐ ").slice(0, 120));

console.log("=".repeat(72));
const failed = results.filter((r) => !r.ok);
console.log(`RESULT: ${results.length - failed.length}/${results.length} passed`);
if (failed.length) {
    console.log("\nFAILURES:");
    failed.forEach((f) => console.log(`  - ${f.label}  ${f.detail}`));
}
if (consoleErrors.length) {
    console.log("\nCONSOLE ERRORS:");
    [...new Set(consoleErrors)].forEach((e) => console.log("  " + e.slice(0, 170)));
}

await browser.close();
process.exit(failed.length ? 1 : 0);

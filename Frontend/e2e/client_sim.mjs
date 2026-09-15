/**
 * Final client simulation: sign in through the form and do a full round trip
 * on a Master Data screen with nothing but the mouse and keyboard --
 * add a record, see it in the table, edit it, see the change, delete it,
 * confirm it is gone -- then sign out and back in and confirm the sign-out
 * actually took.
 */
import { chromium } from "playwright";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const EMAIL = process.argv[2];
const PASSWORD = process.env.PW_PASSWORD;
const NAME = `Client Sim ${Date.now().toString().slice(-6)}`;
const RENAMED = `${NAME} edited`;

let failures = 0;
const step = (label, ok, detail = "") => {
  if (!ok) failures += 1;
  console.log(`  ${ok ? "ok  " : "FAIL"} ${label}${detail ? `  ${detail}` : ""}`);
};

const browser = await chromium.launch();
const page = await browser.newContext({ viewport: { width: 1440, height: 900 } }).then((c) => c.newPage());

const consoleErrors = [];
const httpErrors = [];
page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text().slice(0, 200)));
page.on("response", (r) => r.status() >= 400 && httpErrors.push(`${r.status()} ${r.url().slice(-60)}`));

// ---- sign in ---------------------------------------------------------------
await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL((u) => u.pathname !== "/", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(1500);
step("signs in and lands inside the app", !new URL(page.url()).pathname.match(/^\/$/), page.url());

// ---- the dashboard is the first thing a client sees ------------------------
await page.goto(`${BASE}/dashboard`, { waitUntil: "domcontentloaded" });
await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(600);
const dashText = await page.locator("body").innerText();
step("the dashboard renders content", dashText.trim().length > 400, `${dashText.trim().length} chars`);

// ---- create ----------------------------------------------------------------
await page.goto(`${BASE}/bed_type`, { waitUntil: "domcontentloaded" });
await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(500);

// Scoped to `table.table` on purpose. TableTemplate also renders an off-screen
// copy of the full data set (#export-table-full) as the source for CSV and PDF
// export, so an unscoped "table tbody tr" counts every row twice.
const rowsOf = async (text) =>
  page.locator("table.table tbody tr", { hasText: text }).count();

await page.locator(".table-action-button").first().click();
await page.waitForTimeout(500);
let modal = page.locator(".modal, [role='dialog']").first();

// An empty submit must be refused before anything is sent.
await modal.locator("button", { hasText: /^Submit$/i }).first().click();
await page.waitForTimeout(600);
step("an empty Add is refused", await page.locator(".modal, [role='dialog']").count() > 0);

await modal.locator('input[type="text"]').first().fill(NAME);
await modal.locator("button", { hasText: /^Submit$/i }).first().click();
await page.waitForTimeout(1200);
step("the dialog closes on a valid save", (await page.locator(".modal, [role='dialog']").count()) === 0);
step("the new record appears in the table", (await rowsOf(NAME)) === 1);

// ---- a duplicate is refused, and says so -----------------------------------
await page.locator(".table-action-button").first().click();
await page.waitForTimeout(500);
modal = page.locator(".modal, [role='dialog']").first();
await modal.locator('input[type="text"]').first().fill(NAME);
await modal.locator("button", { hasText: /^Submit$/i }).first().click();
await page.waitForTimeout(1200);
const toast = await page.locator(".toast, [role='alert']").first().innerText().catch(() => "");
step("a duplicate is refused with a message", /exist/i.test(toast), toast.slice(0, 80));
await page.locator("button", { hasText: /^Cancel$/i }).first().click().catch(() => {});
await page.waitForTimeout(500);

// ---- edit ------------------------------------------------------------------
await page.locator("table.table tbody tr", { hasText: NAME }).first()
  .locator("button[aria-label^='Edit']").click();
await page.waitForTimeout(600);
modal = page.locator(".modal, [role='dialog']").first();
const prefilled = await modal.locator('input[type="text"]').first().inputValue();
step("Edit opens with the record's value", prefilled === NAME, prefilled);
await modal.locator('input[type="text"]').first().fill(RENAMED);
await modal.locator("button", { hasText: /^Submit$/i }).first().click();
await page.waitForTimeout(1200);
step("the edit is saved and shown", (await rowsOf(RENAMED)) === 1);
const tableText = await page.locator("table.table").innerText();
step("the table shows the new value, not the old",
  tableText.includes(RENAMED) && !tableText.includes(`${NAME}	`));

// ---- it survives a reload --------------------------------------------------
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(600);
step("the record survives a page reload", (await rowsOf(RENAMED)) === 1);

// ---- delete ----------------------------------------------------------------
await page.locator("table.table tbody tr", { hasText: RENAMED }).first()
  .locator("button[aria-label^='Delete']").click();
await page.waitForTimeout(600);
step("delete asks for confirmation first",
  await page.locator(".modal, [role='dialog']").count() > 0);
await page.locator("button", { hasText: /^Delete$/i }).last().click();
await page.waitForTimeout(1300);
step("the record is gone after deleting", (await rowsOf(RENAMED)) === 0);

await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(600);
step("and stays gone after a reload", (await rowsOf(RENAMED)) === 0);

// ---- sign out really signs out ---------------------------------------------
await page.locator("button[aria-label^='Account menu']").first().click();
await page.waitForTimeout(600);
const signOut = page.locator("button, a", { hasText: /^(Log ?out|Sign ?out)$/i }).first();
step("the account menu offers a sign-out", (await signOut.count()) > 0);
await signOut.click();
await page.waitForTimeout(1500);
await page.goto(`${BASE}/bed_type`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1200);
step("a signed-out session cannot reach a page by URL",
  new URL(page.url()).pathname === "/" || (await page.locator('input[type="password"]').count()) > 0,
  page.url());

console.log(`\nconsole errors: ${consoleErrors.length}  |  4xx/5xx responses: ${httpErrors.filter((h) => !h.startsWith("409")).length}`);
for (const e of consoleErrors.slice(0, 5)) console.log("   console:", e);
for (const h of httpErrors.filter((x) => !x.startsWith("409")).slice(0, 5)) console.log("   http:", h);

console.log(failures === 0 ? "\nclient simulation: every step passed" : `\nclient simulation: ${failures} step(s) failed`);
await browser.close();
process.exit(failures === 0 ? 0 : 1);

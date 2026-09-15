/**
 * Interaction audit: drive the controls on every table screen the way a client
 * would -- search, sort, page, open the Add dialog, submit it empty, cancel,
 * open a row's View and Edit, apply and clear filters -- and report anything
 * that throws, 4xx/5xxs, or leaves the page blank.
 *
 *   node interact.mjs <email> <label>
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const EMAIL = process.argv[2];
const LABEL = process.argv[3] || "run";
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";
const OUT = process.env.OUT || `./e2e-reports/interact-${LABEL}`;

// Every screen built on TableTemplate, i.e. every screen with the same set of
// controls. The bespoke screens (dashboard, room view, night audit, floor
// layout, kitchen display) are covered by the load audit and by the API flows.
const PAGES = [
  "/guest_enquiry", "/task_assign", "/room_incident_log",
  "/employee", "/roles", "/department", "/designation", "/shift",
  "/restaurant_roster", "/restaurant_shift_planning",
  "/bar_roster", "/bar_shift_planning",
  "/reservation", "/booking",
  "/menus", "/combo_deals", "/table_master", "/orders", "/table_reservation",
  "/billing_payments", "/stock", "/recipe_management", "/guest_management",
  "/bar_menus", "/bar_table_master", "/bar_orders",
  "/bar_billing_payments", "/bar_stock", "/bar_recipe_management",
  "/bar_guest_management",
  "/facilities", "/room_type", "/bed_type", "/hall_floor", "/rooms",
  "/discount_type", "/tax_types", "/payment_methods", "/identification_proof",
  "/currency_country", "/hsk_task_type", "/complementary", "/reservation_status",
];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();

let bucket = null;
const fresh = () => ({ consoleErrors: [], pageErrors: [], httpErrors: [], steps: [] });
page.on("console", (m) => { if (bucket && m.type() === "error") bucket.consoleErrors.push(m.text().slice(0, 300)); });
page.on("pageerror", (e) => bucket && bucket.pageErrors.push(String(e).slice(0, 300)));
page.on("response", (r) => {
  if (!bucket) return;
  // A 4xx the test deliberately provokes is still worth seeing, so record all.
  if (r.status() >= 400) bucket.httpErrors.push(`${r.status()} ${r.request().method()} ${r.url().replace("http://127.0.0.1:8000", "")}`);
});

// ---- sign in --------------------------------------------------------------
bucket = fresh();
await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL((u) => u.pathname !== "/", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(1200);

const settle = async () => {
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.waitForTimeout(350);
};

const report = [];

for (const path of PAGES) {
  bucket = fresh();
  const step = (name, detail = "") => bucket.steps.push(detail ? `${name}: ${detail}` : name);
  let fatal = null;

  try {
    await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await settle();

    if (await page.locator(".error-boundary").count()) {
      fatal = "page shows the error boundary";
      throw new Error(fatal);
    }

    const rowsBefore = await page.locator("table tbody tr:not(.table-message-row)").count();
    step("rows", String(rowsBefore));

    // ---- sort by the first sortable header --------------------------------
    const headers = page.locator("table thead th");
    const headerCount = await headers.count();
    if (headerCount > 1 && rowsBefore > 1) {
      const firstCellBefore = await page.locator("table tbody tr:not(.table-message-row) td").first().innerText().catch(() => "");
      await headers.nth(0).click({ timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(250);
      await headers.nth(0).click({ timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(250);
      const firstCellAfter = await page.locator("table tbody tr:not(.table-message-row) td").first().innerText().catch(() => "");
      step("sort", firstCellBefore === firstCellAfter ? "order unchanged after two clicks" : "reorders");
    }

    // ---- search: a term that matches nothing must show the empty state ----
    const search = page.locator(".toolbar-left input").first();
    if (await search.count()) {
      await search.fill("zzzz-no-such-record-zzzz");
      await page.waitForTimeout(450);
      const empty = await page.locator(".table-empty-text").count();
      const rowsNow = await page.locator("table tbody tr:not(.table-message-row)").count();
      step("search-miss", empty > 0 && rowsNow === 0 ? "empty state shown" : `NO EMPTY STATE (rows ${rowsNow})`);
      await search.fill("");
      await page.waitForTimeout(400);
      const restored = await page.locator("table tbody tr:not(.table-message-row)").count();
      step("search-clear", restored === rowsBefore ? "restores" : `restored ${restored} of ${rowsBefore}`);
    }

    // ---- pagination --------------------------------------------------------
    const nextBtn = page.locator(".pagination-btn", { hasText: "Next" });
    if (await nextBtn.count() && await nextBtn.isEnabled()) {
      const firstBefore = await page.locator("table tbody tr:not(.table-message-row) td").first().innerText().catch(() => "");
      await nextBtn.click();
      await page.waitForTimeout(300);
      const firstAfter = await page.locator("table tbody tr:not(.table-message-row) td").first().innerText().catch(() => "");
      step("paginate", firstBefore === firstAfter ? "PAGE 2 LOOKS IDENTICAL" : "advances");
      await page.locator(".pagination-btn", { hasText: "First" }).click().catch(() => {});
      await page.waitForTimeout(250);
    }

    // ---- filters: clear must be reachable ---------------------------------
    const filterSelect = page.locator(".toolbar-filters select").first();
    if (await filterSelect.count()) {
      const options = await filterSelect.locator("option").all();
      if (options.length > 1) {
        const value = await options[1].getAttribute("value");
        if (value) {
          await filterSelect.selectOption(value).catch(() => {});
          await page.waitForTimeout(400);
          const filtered = await page.locator("table tbody tr:not(.table-message-row)").count();
          step("filter", `${filtered} of ${rowsBefore} rows`);
          const clear = page.locator("button", { hasText: /^Clear/ }).first();
          if (await clear.count()) {
            await clear.click().catch(() => {});
            await page.waitForTimeout(400);
            const cleared = await page.locator("table tbody tr:not(.table-message-row)").count();
            step("filter-clear", cleared === rowsBefore ? "restores" : `restored ${cleared} of ${rowsBefore}`);
          } else {
            step("filter-clear", "NO CLEAR CONTROL");
          }
        }
      }
    }

    // ---- Add dialog: open, submit empty, expect a validation stop ---------
    const addBtn = page.locator(".table-action-button").first();
    if (await addBtn.count()) {
      const label = (await addBtn.innerText().catch(() => "")).trim();
      if (/^(add|assign|new|create)/i.test(label)) {
        await addBtn.click();
        await page.waitForTimeout(500);
        const modal = page.locator(".modal, [role='dialog']").first();
        if (await modal.count()) {
          step("add-modal", "opens");
          const submit = modal.locator("button", { hasText: /^(Submit|Save|Add|Create|Assign)/i }).first();
          if (await submit.count()) {
            await submit.click().catch(() => {});
            await page.waitForTimeout(700);
            const stillOpen = await page.locator(".modal, [role='dialog']").count();
            const complaint =
              (await page.locator(".input-error-text, .form-field__error, .toast--error, [role='alert']").count()) > 0;
            step("empty-submit",
              stillOpen && complaint ? "refused with a message"
              : stillOpen ? "refused (no visible message)"
              : "DIALOG CLOSED ON AN EMPTY SUBMIT");
          }
          const cancel = page.locator("button", { hasText: /^(Cancel|Close)$/i }).first();
          if (await cancel.count()) {
            await cancel.click().catch(() => {});
            await page.waitForTimeout(400);
            step("cancel", (await page.locator(".modal, [role='dialog']").count()) ? "MODAL STILL OPEN" : "closes");
          } else {
            await page.keyboard.press("Escape");
            await page.waitForTimeout(400);
          }
        } else {
          step("add-modal", "NO DIALOG APPEARED");
        }
      }
    }

    // ---- row View, then close ---------------------------------------------
    const viewBtn = page.locator("button[aria-label^='View']").first();
    if (await viewBtn.count()) {
      await viewBtn.click().catch(() => {});
      await page.waitForTimeout(600);
      const open = await page.locator(".modal, [role='dialog']").count();
      step("row-view", open ? "opens" : "NO DIALOG");
      if (open) {
        const close = page.locator("button", { hasText: /^(Close|Cancel)$/i }).first();
        if (await close.count()) await close.click().catch(() => {});
        else await page.keyboard.press("Escape");
        await page.waitForTimeout(400);
        step("row-view-close", (await page.locator(".modal, [role='dialog']").count()) ? "STILL OPEN" : "closes");
      }
    }

    // ---- row Edit: opens prefilled, then cancel ---------------------------
    const editBtn = page.locator("button[aria-label^='Edit']").first();
    if (await editBtn.count()) {
      await editBtn.click().catch(() => {});
      await page.waitForTimeout(600);
      const modal = page.locator(".modal, [role='dialog']").first();
      if (await modal.count()) {
        const title = (await modal.locator(".modal-title, h2, h3").first().innerText().catch(() => "")) || "";
        const firstInput = modal.locator("input:not([type=file]):not([type=checkbox])").first();
        const val = (await firstInput.inputValue().catch(() => "")) || "";
        // Stock and Recipe Management put an ADJUSTMENT behind the Edit icon --
        // "how much to add or remove", "which ingredient to add" -- so an empty
        // first field is the correct starting state there, not a lost value.
        const isAdjustment = /adjust|recipe|movement/i.test(title);
        step("row-edit",
          val.trim() ? "opens prefilled"
          : isAdjustment ? `opens blank (adjustment dialog: ${title.trim().slice(0, 40)})`
          : "OPENS EMPTY");
        const cancel = page.locator("button", { hasText: /^(Cancel|Close)$/i }).first();
        if (await cancel.count()) await cancel.click().catch(() => {});
        else await page.keyboard.press("Escape");
        await page.waitForTimeout(400);
      } else {
        step("row-edit", "NO DIALOG");
      }
    }

    const bodyText = (await page.locator("body").innerText()).trim();
    if (bodyText.length < 60) fatal = "page ended blank";
  } catch (e) {
    fatal = fatal || String(e).slice(0, 200);
  }

  const problems = [];
  if (fatal) problems.push(`FATAL ${fatal}`);
  if (bucket.pageErrors.length) problems.push(`pageErr:${bucket.pageErrors.length}`);
  const unexpected = bucket.httpErrors.filter((h) => !h.startsWith("400") && !h.startsWith("409") && !h.startsWith("422"));
  if (unexpected.length) problems.push(`http:${unexpected.length}`);
  const badSteps = bucket.steps.filter((s) => /[A-Z]{4,}/.test(s.split(": ")[1] || ""));
  if (badSteps.length) problems.push(...badSteps);

  report.push({ path, problems, steps: bucket.steps, httpErrors: bucket.httpErrors,
                pageErrors: bucket.pageErrors, consoleErrors: bucket.consoleErrors });
  console.log(`${problems.length ? "!!" : "ok"}  ${path.padEnd(30)} ${problems.join(" | ")}`);
}

mkdirSync(OUT.slice(0, OUT.lastIndexOf('/')) || '.', { recursive: true });
writeFileSync(`${OUT}.json`, JSON.stringify(report, null, 1));
console.log(`\nwrote ${OUT}.json`);
await browser.close();

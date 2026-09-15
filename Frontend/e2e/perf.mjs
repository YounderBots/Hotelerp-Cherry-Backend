/**
 * Page-load and request-shape audit.
 *
 * For every route: time to first paint and to a settled network, the API calls
 * the page issues, and whether any of them is issued more than once. Duplicate
 * requests for the same URL within one page load are the cheap win -- two
 * components each fetching the same reference list.
 *
 *   node perf.mjs <email> <label>
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const API = process.env.API || "http://127.0.0.1:8000";
const EMAIL = process.argv[2];
const LABEL = process.argv[3] || "run";
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";

const ROUTES = [
  "/dashboard", "/reservation", "/add_new_reservation", "/booking", "/room_view",
  "/reservation_view", "/night_audit", "/user_reserved_details",
  "/room_booked_details", "/settlement_summary", "/guest_enquiry", "/task_assign",
  "/room_incident_log", "/employee", "/user", "/roles", "/department",
  "/designation", "/shift", "/restaurant_roster", "/restaurant_shift_planning",
  "/bar_roster", "/bar_shift_planning", "/menus", "/combo_deals", "/floor_layout",
  "/table_master", "/orders", "/table_reservation", "/kot/main_kitchen",
  "/kot/grill", "/kot/dessert", "/billing_payments", "/stock",
  "/recipe_management", "/guest_management", "/reports_analytics", "/bar_menus",
  "/bar_floor_layout", "/bar_table_master", "/bar_orders", "/bar_station",
  "/bar_billing_payments", "/bar_stock", "/bar_recipe_management",
  "/bar_guest_management", "/bar_reports_analytics", "/facilities", "/room_type",
  "/bed_type", "/hall_floor", "/rooms", "/discount_type", "/tax_types",
  "/payment_methods", "/identification_proof", "/currency_country",
  "/hsk_task_type", "/complementary", "/reservation_status", "/profile", "/settings",
];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();

let calls = [];
page.on("request", (r) => {
  const u = r.url();
  if (u.startsWith(API)) calls.push(`${r.method()} ${u.slice(API.length).split("?")[0]}`);
});

await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL((u) => u.pathname !== "/", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(1500);

const report = [];
for (const route of ROUTES) {
  calls = [];
  const t0 = Date.now();
  await page.goto(`${BASE}${route}`, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});
  const domReady = Date.now() - t0;
  await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
  const settled = Date.now() - t0;

  const counts = {};
  for (const c of calls) counts[c] = (counts[c] || 0) + 1;
  const dupes = Object.entries(counts).filter(([, n]) => n > 1);

  report.push({ route, domReady, settled, apiCalls: calls.length, dupes });
  const flags = [];
  if (settled > 3000) flags.push(`SLOW ${settled}ms`);
  if (calls.length > 8) flags.push(`${calls.length} API calls`);
  if (dupes.length) flags.push("DUP " + dupes.map(([k, n]) => `${k} x${n}`).join(", "));
  console.log(
    `${flags.length ? "!!" : "ok"}  ${route.padEnd(28)} dom ${String(domReady).padStart(5)}ms  ` +
    `settled ${String(settled).padStart(5)}ms  api ${String(calls.length).padStart(2)}  ${flags.join(" | ")}`
  );
}

const settledTimes = report.map((r) => r.settled).sort((a, b) => a - b);
const p50 = settledTimes[Math.floor(settledTimes.length * 0.5)];
const p95 = settledTimes[Math.floor(settledTimes.length * 0.95)];
console.log(`\nsettled: median ${p50}ms, p95 ${p95}ms, slowest ${settledTimes.at(-1)}ms`);
console.log(`routes with duplicate API calls: ${report.filter((r) => r.dupes.length).length}`);
mkdirSync("./e2e-reports", { recursive: true });
writeFileSync(`./e2e-reports/perf-${LABEL}.json`, JSON.stringify(report, null, 1));
await browser.close();

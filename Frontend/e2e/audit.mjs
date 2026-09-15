/**
 * Full-application browser audit.
 *   node audit.mjs <email> <label> [--width=1440] [--shots]
 * Walks every route as the given account and reports, per page:
 *   console errors/warnings, uncaught page errors, failed network requests,
 *   blank render, horizontal overflow, and the "no access" panel.
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const EMAIL = process.argv[2];
const LABEL = process.argv[3] || EMAIL;
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";
const WIDTH = Number((process.argv.find(a => a.startsWith("--width=")) || "").split("=")[1] || 1440);
const HEIGHT = Number((process.argv.find(a => a.startsWith("--height=")) || "").split("=")[1] || 900);
const SHOTS = process.argv.includes("--shots");
const OUT = process.env.OUT || `./e2e-reports/audit-${LABEL}`;

const ROUTES = [
  "/dashboard",
  "/reservation", "/add_new_reservation", "/booking", "/room_view", "/reservation_view",
  "/night_audit", "/user_reserved_details", "/room_booked_details", "/settlement_summary",
  "/guest_enquiry",
  "/task_assign", "/room_incident_log",
  "/employee", "/user", "/roles", "/department", "/designation", "/shift",
  "/restaurant_roster", "/restaurant_shift_planning", "/bar_roster", "/bar_shift_planning",
  "/menus", "/combo_deals", "/floor_layout", "/table_master", "/orders", "/table_reservation",
  "/kot/main_kitchen", "/kot/grill", "/kot/dessert", "/billing_payments",
  "/stock", "/recipe_management", "/guest_management", "/reports_analytics",
  "/bar_menus", "/bar_floor_layout", "/bar_table_master", "/bar_orders", "/bar_station",
  "/bar_billing_payments", "/bar_stock", "/bar_recipe_management", "/bar_guest_management",
  "/bar_reports_analytics",
  "/facilities", "/room_type", "/bed_type", "/hall_floor", "/rooms", "/discount_type",
  "/tax_types", "/payment_methods", "/identification_proof", "/currency_country",
  "/hsk_task_type", "/complementary", "/reservation_status",
  "/profile", "/settings",
  "/nope-does-not-exist",
];

if (SHOTS) mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: WIDTH, height: HEIGHT } });
const page = await ctx.newPage();

let bucket = null;
page.on("console", (m) => {
  if (!bucket) return;
  const t = m.type();
  if (t === "error") bucket.consoleErrors.push(m.text().slice(0, 400));
  else if (t === "warning") bucket.consoleWarnings.push(m.text().slice(0, 400));
});
page.on("pageerror", (e) => bucket && bucket.pageErrors.push(String(e).slice(0, 400)));
page.on("requestfailed", (r) => bucket && bucket.netFailed.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`));
page.on("response", (r) => {
  if (!bucket) return;
  if (r.status() >= 400) bucket.httpErrors.push(`${r.status()} ${r.request().method()} ${r.url().replace(BASE, "")}`);
});

const fresh = () => ({ consoleErrors: [], consoleWarnings: [], pageErrors: [], netFailed: [], httpErrors: [] });

// ---- login through the real form ----
bucket = fresh();
await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
await Promise.all([
  page.waitForURL((u) => !u.pathname.match(/^\/$/), { timeout: 30000 }).catch(() => {}),
  page.click('button[type="submit"]'),
]);
await page.waitForTimeout(1500);
const loginReport = { route: "LOGIN", url: page.url(), ...bucket };

const report = [loginReport];

for (const route of ROUTES) {
  bucket = fresh();
  let navErr = null;
  try {
    await page.goto(`${BASE}${route}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    // settle: wait for network quiet-ish then a beat for lazy chunk + data
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(700);
  } catch (e) { navErr = String(e).slice(0, 200); }

  const probe = await page.evaluate(() => {
    const de = document.documentElement;
    const body = document.body;
    const text = (body?.innerText || "").trim();
    const overflow = Math.max(de.scrollWidth, body?.scrollWidth || 0) - de.clientWidth;
    // widest offending element, for a usable bug report
    let widest = null;
    if (overflow > 1) {
      const lim = de.clientWidth;
      for (const el of document.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width === 0) continue;
        if (r.right > lim + 1) {
          const over = Math.round(r.right - lim);
          if (!widest || over > widest.over) {
            widest = { over, tag: el.tagName.toLowerCase(), cls: String(el.className || "").slice(0, 80) };
          }
        }
      }
    }
    const brokenImgs = [...document.images]
      .filter((i) => i.complete && i.naturalWidth === 0)
      .map((i) => i.getAttribute("src") || "(no src)");
    const imgsNoAlt = [...document.images].filter((i) => !i.hasAttribute("alt")).length;
    return {
      textLen: text.length,
      head: text.slice(0, 120).replace(/\s+/g, " "),
      overflow: Math.round(overflow),
      widest,
      brokenImgs,
      imgsNoAlt,
      imgCount: document.images.length,
      denied: text.includes("You do not have access to this page"),
      notFound: text.includes("Page not found") || text.includes("404"),
      crashed: text.includes("Something went wrong"),
    };
  });

  report.push({ route, url: page.url(), navErr, ...probe, ...bucket });
  if (SHOTS) await page.screenshot({ path: `${OUT}/${route.replace(/\//g, "_") || "root"}.png`, fullPage: false });
  const flag = [];
  if (probe.crashed) flag.push("CRASH");
  if (probe.denied) flag.push("denied");
  if (probe.textLen < 60 && !probe.denied) flag.push("BLANK");
  if (probe.overflow > 1) flag.push(`overflow+${probe.overflow}`);
  if (bucket.pageErrors.length) flag.push(`pageErr:${bucket.pageErrors.length}`);
  if (bucket.consoleErrors.length) flag.push(`consoleErr:${bucket.consoleErrors.length}`);
  if (bucket.httpErrors.length) flag.push(`http:${bucket.httpErrors.length}`);
  if (probe.brokenImgs.length) flag.push(`brokenImg:${probe.brokenImgs.length}`);
  console.log(`${flag.length ? "!!" : "ok"}  ${route.padEnd(30)} ${flag.join(" ")}`);
}

mkdirSync(OUT.slice(0, OUT.lastIndexOf('/')) || '.', { recursive: true });
writeFileSync(`${OUT}.json`, JSON.stringify(report, null, 1));
console.log(`\nwrote ${OUT}.json`);
await browser.close();

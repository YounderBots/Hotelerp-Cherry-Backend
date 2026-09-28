/**
 * Authenticated admin-dashboard interaction and responsive audit.
 * Read-only: it changes only in-memory report dates and navigates between
 * existing screens; it does not create, edit, or delete records.
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const API = process.env.API || "http://127.0.0.1:8000";
const EMAIL = process.argv[2] || "admin@cherryhotel.com";
const LABEL = process.argv[3] || "admin";
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";
const OUT = process.env.OUT || `./e2e-reports/dashboard-audit-${LABEL}.json`;
const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1024, height: 900 },
  { name: "tablet", width: 768, height: 900 },
  { name: "mobile", width: 375, height: 667 },
];

const report = [];
const browser = await chromium.launch();

for (const viewport of VIEWPORTS) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  let bucket = null;
  const fresh = () => ({ consoleErrors: [], pageErrors: [], httpErrors: [], failedRequests: [], steps: [] });
  page.on("console", (message) => {
    if (bucket && message.type() === "error") bucket.consoleErrors.push(message.text().slice(0, 300));
  });
  page.on("pageerror", (error) => bucket?.pageErrors.push(String(error).slice(0, 300)));
  page.on("requestfailed", (request) => bucket?.failedRequests.push(`${request.method()} ${request.url()} ${request.failure()?.errorText}`));
  page.on("response", (response) => {
    if (bucket && response.status() >= 400) {
      bucket.httpErrors.push(`${response.status()} ${response.request().method()} ${response.url().replace(API, "")}`);
    }
  });

  const step = (name, detail = "") => bucket.steps.push(detail ? `${name}: ${detail}` : name);
  const probe = async (label) => {
    const result = await page.evaluate(() => {
      const root = document.documentElement;
      const body = document.body;
      const overflow = Math.max(root.scrollWidth, body?.scrollWidth || 0) - root.clientWidth;
      return {
        textLength: (body?.innerText || "").trim().length,
        overflow: Math.round(overflow),
        brokenImages: [...document.images]
          .filter((image) => image.complete && image.naturalWidth === 0)
          .map((image) => image.getAttribute("src") || "(no src)"),
        visibleButtons: [...document.querySelectorAll("button")].filter((button) => {
          const rect = button.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0;
        }).length,
      };
    });
    bucket.steps.push(`${label}: overflow=${result.overflow}px, text=${result.textLength}`);
    return result;
  };

  bucket = fresh();
  await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
  await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
  await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
  await Promise.all([
    page.waitForURL((url) => url.pathname !== "/", { timeout: 30000 }).catch(() => {}),
    page.click('button[type="submit"]'),
  ]);
  await page.goto(`${BASE}/dashboard`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(500);
  step("dashboard", "authenticated and loaded");
  await probe("overview");

  const tab = (name) => page.locator(".admin-dashboard .tab-trigger", { hasText: name }).first();

  await tab("Hotel").click();
  await page.getByText("Hotel operations overview", { exact: true }).waitFor({ timeout: 10000 });
  step("hotel-tab", "opened");
  await probe("hotel");
  const hotelRefresh = page.getByRole("button", { name: "Refresh dashboard" }).last();
  await hotelRefresh.click();
  await page.waitForTimeout(350);
  step("hotel-refresh", "clicked");

  await tab("Restaurant").click();
  await page.getByText("Restaurant Overview", { exact: true }).waitFor({ timeout: 10000 });
  step("restaurant-tab", "opened");
  await probe("restaurant");
  const restaurantDate = page.locator('.admin-dashboard input[aria-label="Report date"]:visible').last();
  const beforeDate = await restaurantDate.inputValue();
  await restaurantDate.fill("2026-09-23");
  await page.waitForTimeout(600);
  const afterDate = await restaurantDate.inputValue();
  step("restaurant-date", `${beforeDate} -> ${afterDate}`);
  const dateRequest = await page.evaluate(() => performance.getEntriesByType("resource")
    .map((entry) => entry.name)
    .filter((name) => name.includes("restaurant/reports/") && name.includes("report_date=2026-09-23"))
    .length);
  step("restaurant-date-api", `${dateRequest} matching request(s)`);
  await page.getByRole("button", { name: "Refresh dashboard" }).last().click();
  await page.waitForTimeout(350);
  step("restaurant-refresh", "clicked");

  await tab("Bar").click();
  await page.getByText("Bar Overview", { exact: true }).waitFor({ timeout: 10000 });
  step("bar-tab", "opened");
  await probe("bar");
  const barDate = page.locator('.admin-dashboard input[aria-label="Report date"]:visible').last();
  await barDate.fill("2026-09-23");
  await page.waitForTimeout(600);
  const barAfterDate = await barDate.inputValue();
  const barDateRequest = await page.evaluate(() => performance.getEntriesByType("resource")
    .map((entry) => entry.name)
    .filter((name) => name.includes("bar/reports/") && name.includes("report_date=2026-09-23"))
    .length);
  step("bar-date", `2026-09-24 -> ${barAfterDate}; ${barDateRequest} matching request(s)`);
  await page.getByRole("button", { name: "Refresh dashboard" }).last().click();
  await page.waitForTimeout(350);
  step("bar-refresh", "clicked");

  await tab("Overview").click();
  await page.getByText("Quick Actions", { exact: true }).waitFor({ timeout: 10000 });
  step("overview-return", "opened");
  await probe("overview-return");

  // Exercise navigation targets without submitting any business form.
  const quickTargets = [
    ["New Reservation", "/add_new_reservation"],
    ["New Restaurant Order", "/orders"],
    ["New Bar Order", "/bar_orders"],
  ];
  for (const [label, expectedPath] of quickTargets) {
    await page.getByRole("button", { name: label, exact: true }).click();
    await page.waitForURL((url) => url.pathname === expectedPath, { timeout: 10000 }).catch(() => {});
    step(`quick-${label}`, page.url().endsWith(expectedPath) ? expectedPath : `unexpected ${new URL(page.url()).pathname}`);
    await page.goBack({ waitUntil: "domcontentloaded" });
    await page.getByText("Quick Actions", { exact: true }).waitFor({ timeout: 10000 });
  }

  // Hotel's row action and its Add Booking action are checked on every viewport;
  // this remains read-only and leaves the demo data unchanged.
  await tab("Hotel").click();
  await page.getByText("Recent Bookings", { exact: true }).waitFor({ timeout: 10000 });
  const firstBooking = page.locator(".booking-list-wrap table tbody tr").first();
  if (await firstBooking.count()) {
    await firstBooking.click();
    await page.getByRole("button", { name: "Back to reservations" }).waitFor({ timeout: 10000 });
    step("hotel-row", page.url().endsWith("/ReservationView") ? "opened detail" : `unexpected ${new URL(page.url()).pathname}`);
    await page.goBack({ waitUntil: "domcontentloaded" });
    await page.getByText("Quick Actions", { exact: true }).waitFor({ timeout: 10000 });
    await tab("Hotel").click();
    await page.getByText("Recent Bookings", { exact: true }).waitFor({ timeout: 10000 });
  } else {
    step("hotel-row", "no recent booking row");
  }
  await page.getByRole("button", { name: "Create a new reservation" }).click();
  await page.getByText("Add Reservation", { exact: true }).waitFor({ timeout: 10000 });
  step("hotel-add", "opened");
  await page.goBack({ waitUntil: "domcontentloaded" });

  const final = await probe("final");
  report.push({ viewport, ...bucket, final });
  await context.close();
}

mkdirSync(OUT.slice(0, OUT.lastIndexOf("/")) || ".", { recursive: true });
writeFileSync(OUT, JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.map((row) => ({
  viewport: row.viewport.name,
  steps: row.steps,
  consoleErrors: row.consoleErrors.length,
  pageErrors: row.pageErrors.length,
  httpErrors: row.httpErrors,
  failedRequests: row.failedRequests.length,
  finalOverflow: row.final.overflow,
})), null, 2));
console.log(`wrote ${OUT}`);
await browser.close();
if (report.some((row) => row.consoleErrors.length || row.pageErrors.length || row.httpErrors.length || row.failedRequests.length || row.final.overflow > 1)) {
  process.exitCode = 1;
}

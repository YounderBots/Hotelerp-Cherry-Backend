/**
 * Focused responsive/read-only audit for the three reservation surfaces that
 * sit around the reservation list: the URL-addressable detail view, the add
 * reservation flow, and booking enquiries.
 *
 *   node e2e/reservation_pages_audit.mjs admin@cherryhotel.com focused
 *
 * It does not submit a business form. It does open and cancel the booking
 * dialog so the modal layout is measured at every supported width.
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const API = process.env.API || "http://127.0.0.1:8000";
const EMAIL = process.argv[2] || "admin@cherryhotel.com";
const LABEL = process.argv[3] || "admin";
const PASSWORD = process.env.PW_PASSWORD;
const OUT = process.env.OUT || `./e2e-reports/reservation-pages-${LABEL}.json`;
const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1024, height: 900 },
  { name: "tablet", width: 768, height: 900 },
  { name: "mobile", width: 375, height: 667 },
];

const ROUTES = [
  { name: "detail-valid", path: "/ReservationView?reservationId=25", expect: "RES-202609-0025" },
  { name: "detail-missing-id", path: "/ReservationView", expect: "No reservation was selected" },
  { name: "add-reservation", path: "/add_new_reservation", expect: "Add Reservation" },
  { name: "booking", path: "/booking", expect: "Booking Requests" },
  { name: "room-view", path: "/room_view", expect: "Room View" },
  { name: "profile", path: "/profile", expect: "Aarav Sharma" },
  { name: "settings", path: "/settings", expect: "Settings" },
  { name: "guest-enquiry", path: "/guest_enquiry", expect: "Guest Enquiry" },
  { name: "employee", path: "/employee", expect: "Employees" },
  { name: "user", path: "/user", expect: "Role Permissions" },
  { name: "department", path: "/department", expect: "Departments" },
  { name: "designation", path: "/designation", expect: "Designations" },
  { name: "roles", path: "/roles", expect: "Roles" },
  { name: "shift", path: "/shift", expect: "Shifts" },
  { name: "restaurant-roster", path: "/restaurant_roster", expect: "Restaurant Roster" },
  { name: "restaurant-shift-planning", path: "/restaurant_shift_planning", expect: "Restaurant Shift Planning" },
  { name: "bar-roster", path: "/bar_roster", expect: "Bar Roster" },
  { name: "bar-shift-planning", path: "/bar_shift_planning", expect: "Bar Shift Planning" },
  { name: "task-assign", path: "/task_assign", expect: "Task Assign" },
  { name: "room-incident", path: "/room_incident_log", expect: "Room Incident Log" },
  { name: "floor-layout", path: "/floor_layout", expect: "Floor Layout" },
  { name: "table-master", path: "/table_master", expect: "Table Master" },
  { name: "orders", path: "/orders", expect: "Orders" },
  { name: "table-reservation", path: "/table_reservation", expect: "Table Reservations" },
  { name: "menus", path: "/menus", expect: "Menu Management" },
  { name: "combo-deals", path: "/combo_deals", expect: "Combo / Package Deals" },
  { name: "main-kitchen", path: "/kot/main_kitchen", expect: "Main Kitchen" },
  { name: "grill-kitchen", path: "/kot/grill", expect: "Grill — Active KOTs" },
  { name: "dessert-kitchen", path: "/kot/dessert", expect: "Dessert Station — Active KOTs" },
  { name: "billing-payments", path: "/billing_payments", expect: "Billing & Payments" },
  { name: "stock", path: "/stock", expect: "Stock" },
  { name: "recipe-management", path: "/recipe_management", expect: "Recipes" },
  { name: "guest-management", path: "/guest_management", expect: "Guests" },
  { name: "reports-analytics", path: "/reports_analytics", expect: "Sales Report" },
  { name: "bar-floor-layout", path: "/bar_floor_layout", expect: "Bar Floor Layout" },
  { name: "bar-table-master", path: "/bar_table_master", expect: "Bar Table Master" },
  { name: "bar-orders", path: "/bar_orders", expect: "Bar Orders" },
  { name: "bar-menus", path: "/bar_menus", expect: "Bar Menu Management" },
  { name: "bar-station", path: "/bar_station", expect: "Bar Station Display" },
  { name: "bar-billing", path: "/bar_billing_payments", expect: "Bar Billing & Payments" },
  { name: "bar-stock", path: "/bar_stock", expect: "Bar Stock" },
  { name: "bar-recipe", path: "/bar_recipe_management", expect: "Bar Recipes" },
  { name: "bar-guest", path: "/bar_guest_management", expect: "Bar Guests" },
  { name: "bar-reports", path: "/bar_reports_analytics", expect: "Sales Report" },
  { name: "facilities", path: "/facilities", expect: "Facilities" },
  { name: "room-type", path: "/room_type", expect: "Room Types" },
  { name: "bed-type", path: "/bed_type", expect: "Bed Types" },
  { name: "rooms", path: "/rooms", expect: "Rooms" },
  { name: "discount-type", path: "/discount_type", expect: "Discount Types" },
  { name: "tax-types", path: "/tax_types", expect: "Tax Types" },
  { name: "payment-methods", path: "/payment_methods", expect: "Payment Methods" },
  { name: "identification-proof", path: "/identification_proof", expect: "Identification Proofs" },
  { name: "currency-country", path: "/currency_country", expect: "Countries & Currencies" },
  { name: "hsk-task-type", path: "/hsk_task_type", expect: "Task Types" },
  { name: "complementary", path: "/complementary", expect: "Complementary" },
  { name: "reservation-status", path: "/reservation_status", expect: "Reservation Status" },
];

const browser = await chromium.launch();
const report = [];

for (const viewport of VIEWPORTS) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  let bucket = null;
  const fresh = () => ({ consoleErrors: [], pageErrors: [], failedRequests: [], httpErrors: [], steps: [] });
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

  // The first login after a service restart is intermittently refused: the
  // click can land before the form's submit handler is attached, leaving the
  // SPA on the login page while the run "passes" every route as a false
  // failure. Watch the login response, require it to be 200, and only then trust
  // the token.
  for (let attempt = 0; attempt < 5; attempt += 1) {
    await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
    await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
    await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
    const answered = page
      .waitForResponse((r) => r.url().includes("/login_post"), { timeout: 20000 })
      .catch(() => null);
    await page.click('button[type="submit"]');
    const response = await answered;
    const status = response ? response.status() : null;
    await page.waitForTimeout(1500);
    if (status === 200 && (await page.evaluate(() => !!localStorage.getItem("AuthToken")))) break;
    await page.waitForTimeout(3000);
    if (attempt === 4) {
      throw new Error(`login failed after 5 attempts (last /login_post status: ${status})`);
    }
  }

  for (const route of ROUTES) {
    bucket = fresh();
    await page.goto(`${BASE}${route.path}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(500);

    const probe = async (label) => {
      const result = await page.evaluate(() => {
        const root = document.documentElement;
        const body = document.body;
        const overflow = Math.max(root.scrollWidth, body?.scrollWidth || 0) - root.clientWidth;
        return {
          text: (body?.innerText || "").trim(),
          overflow: Math.round(overflow),
          visibleButtons: [...document.querySelectorAll("button")].filter((button) => {
            const rect = button.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          }).length,
          brokenImages: [...document.images]
            .filter((image) => image.complete && image.naturalWidth === 0)
            .map((image) => image.getAttribute("src") || "(no src)"),
        };
      });
      bucket.steps.push(`${label}: overflow=${result.overflow}px, text=${result.text.length}`);
      return result;
    };

    const initial = await probe("initial");
    let modal = null;
    if (route.name === "booking") {
      const add = page.getByRole("button", { name: "Add Booking", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(250);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "room-view") {
      const room = page.locator(".rvw-card").first();
      if (await room.count()) {
        await room.click();
        await page.waitForTimeout(200);
        modal = await probe("room-dialog");
        await page.keyboard.press("Escape");
      }
    }
    if (route.name === "guest-enquiry") {
      const search = page.locator('input[aria-label^="Search"]').first();
      if (await search.count()) {
        await search.fill("Sarah");
        await page.waitForTimeout(100);
        await search.fill("");
      }
      const add = page.getByRole("button", { name: "Add Enquiry", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "employee") {
      const add = page.getByRole("button", { name: "Add Employee", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(250);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "user") {
      const role = page.locator(".perm-panel select").first();
      if (await role.count()) {
        await role.selectOption("1");
        await page.waitForTimeout(250);
        const matrix = page.locator(".permission-table");
        if (await matrix.count()) await matrix.waitFor({ state: "visible" });
      }
    }
    if (route.name === "department") {
      const add = page.getByRole("button", { name: "Add Department", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "designation") {
      const add = page.getByRole("button", { name: "Add Designation", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "roles") {
      const add = page.getByRole("button", { name: "Add Role", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "shift") {
      const add = page.getByRole("button", { name: "Add Shift", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "restaurant-roster") {
      const date = page.locator('input[aria-label="Roster date"]');
      if (await date.count()) {
        await date.fill("2026-09-26");
        await page.waitForTimeout(150);
      }
      const add = page.getByRole("button", { name: "Assign Staff", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("assign-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "restaurant-shift-planning") {
      const date = page.locator('input[aria-label="Planning date"]');
      if (await date.count()) {
        await date.fill("2026-09-26");
        await page.waitForTimeout(150);
      }
      const add = page.getByRole("button", { name: "Add Shift", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-roster") {
      const date = page.locator('input[aria-label="Roster date"]');
      if (await date.count()) {
        await date.fill("2026-09-26");
        await page.waitForTimeout(150);
      }
      const add = page.getByRole("button", { name: "Assign Staff", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("assign-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-shift-planning") {
      const date = page.locator('input[aria-label="Planning date"]');
      if (await date.count()) {
        await date.fill("2026-09-26");
        await page.waitForTimeout(150);
      }
      const add = page.getByRole("button", { name: "Add Shift", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "task-assign") {
      const add = page.getByRole("button", { name: "Assign Task", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("assign-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "room-incident") {
      const add = page.getByRole("button", { name: "Add Incident", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "floor-layout") {
      const add = page.getByRole("button", { name: "Add Floor", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "table-master") {
      const add = page.getByRole("button", { name: "Add Table", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "orders") {
      const add = page.getByRole("button", { name: "Add Order", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "table-reservation") {
      const add = page.getByRole("button", { name: "Add Reservation", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "menus") {
      const add = page.getByRole("button", { name: "Add Item", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "combo-deals") {
      const add = page.getByRole("button", { name: "Add Combo", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "main-kitchen") {
      const view = page.getByRole("button", { name: /^View KOT / }).first();
      if (await view.count()) {
        await view.click();
        await page.waitForTimeout(250);
        modal = await probe("kot-dialog");
        const close = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await close.count()) await close.click();
      }
    }
    if (route.name === "grill-kitchen") {
      const view = page.getByRole("button", { name: /^View KOT / }).first();
      if (await view.count()) {
        await view.click();
        await page.waitForTimeout(250);
        modal = await probe("kot-dialog");
        const close = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await close.count()) await close.click();
      }
    }
    if (route.name === "dessert-kitchen") {
      const view = page.getByRole("button", { name: /^View KOT / }).first();
      if (await view.count()) {
        await view.click();
        await page.waitForTimeout(250);
        modal = await probe("kot-dialog");
        const close = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await close.count()) await close.click();
      }
    }
    if (route.name === "billing-payments") {
      const generate = page.getByRole("button", { name: "Generate Bill", exact: true });
      if (await generate.count()) {
        await generate.click();
        await page.waitForTimeout(200);
        modal = await probe("generate-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "stock") {
      const add = page.getByRole("button", { name: "Add Item", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "recipe-management") {
      const edit = page.getByRole("button", { name: /^Edit recipe for / }).first();
      if (await edit.count()) {
        await edit.click();
        await page.waitForTimeout(250);
        modal = await probe("recipe-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "guest-management") {
      const add = page.getByRole("button", { name: "Add Guest", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "reports-analytics") {
      const inventoryTab = page.getByRole("button", { name: "Inventory", exact: true });
      if (await inventoryTab.count()) {
        await inventoryTab.click();
        await page.waitForTimeout(250);
        await probe("inventory-report");
      }
    }
    if (route.name === "bar-floor-layout") {
      const add = page.getByRole("button", { name: "Add Floor", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-table-master") {
      const add = page.getByRole("button", { name: "Add Table", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-orders") {
      const add = page.getByRole("button", { name: "Add Order", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-menus") {
      const add = page.getByRole("button", { name: "Add Item", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-station") {
      const view = page.getByRole("button", { name: /^View BOT / }).first();
      if (await view.count()) {
        await view.click();
        await page.waitForTimeout(250);
        modal = await probe("bot-dialog");
        const close = page.getByRole("button", { name: "Close", exact: true }).last();
        if (await close.count()) await close.click();
      }
    }
    if (route.name === "bar-billing") {
      const generate = page.getByRole("button", { name: "Generate Bill", exact: true });
      if (await generate.count()) {
        await generate.click();
        await page.waitForTimeout(200);
        modal = await probe("generate-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-stock") {
      const add = page.getByRole("button", { name: "Add Item", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-recipe") {
      const edit = page.getByRole("button", { name: /^Edit recipe for / }).first();
      if (await edit.count()) {
        await edit.click();
        await page.waitForTimeout(250);
        modal = await probe("recipe-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-guest") {
      const add = page.getByRole("button", { name: "Add Guest", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bar-reports") {
      const stations = page.getByRole("button", { name: "Stations", exact: true });
      if (await stations.count()) {
        await stations.click();
        await page.waitForTimeout(250);
        await probe("stations-report");
      }
    }
    if (route.name === "facilities") {
      const add = page.getByRole("button", { name: "Add Facility", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "room-type") {
      const add = page.getByRole("button", { name: "Add Room Type", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "bed-type") {
      const add = page.getByRole("button", { name: "Add Bed Type", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "rooms") {
      const add = page.getByRole("button", { name: "Add Room", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "discount-type") {
      const add = page.getByRole("button", { name: "Add Discount Type", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    if (route.name === "tax-types") {
      const add = page.getByRole("button", { name: "Add Tax Type", exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }
    const addButtonLabels = {
      "payment-methods": "Add Payment Method",
      "identification-proof": "Add Identification Proof",
      "currency-country": "Add Country",
      "hsk-task-type": "Add Task Type",
      complementary: "Add Complementary",
      "reservation-status": "Add Reservation Status",
    };
    if (addButtonLabels[route.name]) {
      const add = page.getByRole("button", { name: addButtonLabels[route.name], exact: true });
      if (await add.count()) {
        await add.click();
        await page.waitForTimeout(200);
        modal = await probe("add-dialog");
        const cancel = page.getByRole("button", { name: "Cancel", exact: true }).last();
        if (await cancel.count()) await cancel.click();
      }
    }

    report.push({
      viewport: viewport.name,
      route: route.name,
      url: page.url(),
      expectedText: route.expect,
      expectedTextPresent: initial.text.includes(route.expect),
      ...initial,
      modal,
      ...bucket,
    });
  }
  await context.close();
}

mkdirSync(OUT.slice(0, OUT.lastIndexOf("/")) || ".", { recursive: true });
writeFileSync(OUT, JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.map((row) => ({
  viewport: row.viewport,
  route: row.route,
  expectedTextPresent: row.expectedTextPresent,
  overflow: row.overflow,
  modalOverflow: row.modal?.overflow,
  consoleErrors: row.consoleErrors.length,
  pageErrors: row.pageErrors.length,
  failedRequests: row.failedRequests.length,
  httpErrors: row.httpErrors,
})), null, 2));
console.log(`wrote ${OUT}`);
await browser.close();
if (report.some((row) => !row.expectedTextPresent || row.overflow > 1 || (row.modal && row.modal.overflow > 1) || row.consoleErrors.length || row.pageErrors.length || row.failedRequests.length || row.httpErrors.length)) {
  process.exitCode = 1;
}

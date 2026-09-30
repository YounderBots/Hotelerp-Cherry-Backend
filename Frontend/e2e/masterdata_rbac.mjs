/** Master-data RBAC probe for the tail of the Master Data sweep.
 *  Covers: identity proof, country & currency, housekeeping task type,
 *  complementary, reservation status, payment methods.
 *  Read-only: it only inspects the rendered controls, it never writes. */
import { chromium } from "playwright";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const PASSWORD = process.env.PW_PASSWORD;

const pages = [
  { key: "identification-proof", path: "/identification_proof", add: "Add Identification Proof" },
  { key: "currency-country", path: "/currency_country", add: "Add Country" },
  { key: "hsk-task-type", path: "/hsk_task_type", add: "Add Task Type" },
  { key: "complementary", path: "/complementary", add: "Add Complementary" },
  { key: "reservation-status", path: "/reservation_status", add: "Add Reservation Status" },
  { key: "payment-methods", path: "/payment_methods", add: "Add Payment Method" },
];

const roles = [
  ["admin", "admin@cherryhotel.com"],
  ["front-office-manager", "priya.menon@cherryhotel.com"],
  ["front-desk", "rahul.nair@cherryhotel.com"],
  ["housekeeping", "imran.khan@cherryhotel.com"],
  ["food-beverage", "vikram.singh@cherryhotel.com"],
];

const browser = await chromium.launch();
const out = [];

for (const [label, email] of roles) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("response", (r) => {
    if (r.status() >= 500) errors.push(`${r.status()} ${r.url()}`);
  });

  await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
  for (let attempt = 0; attempt < 2; attempt += 1) {
    if (attempt > 0) {
      await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
    }
    await page.fill('input[type="email"], input[name="email"], #email', email);
    await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    if (await page.evaluate(() => !!localStorage.getItem("AuthToken"))) break;
  }

  for (const spec of pages) {
    await page.goto(`${BASE}${spec.path}`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(700);
    const probe = await page.evaluate((addLabel) => {
      const buttons = Array.from(document.querySelectorAll("button"));
      const labelled = (prefix) =>
        buttons.some(
          (b) =>
            (b.getAttribute("aria-label") || b.getAttribute("title") || "").startsWith(prefix) ||
            b.innerText.trim() === prefix,
        );
      return {
        accessible: !document.body.innerText.includes("You do not have access to this page"),
        add: buttons.some((b) => b.innerText.trim() === addLabel),
        view: labelled("View"),
        edit: labelled("Edit"),
        del: labelled("Delete"),
      };
    }, spec.add);
    out.push({ role: label, page: spec.key, ...probe, errors });
  }

  await context.close();
}

console.log(JSON.stringify(out, null, 2));
await browser.close();

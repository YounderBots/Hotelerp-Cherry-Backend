/** Read-only guest-enquiry role probe; no CRUD submissions. */
import { chromium } from "playwright";
const BASE = process.env.BASE || "http://127.0.0.1:5173";
const PASSWORD = process.env.PW_PASSWORD;
const ROLES = [
  ["admin", "admin@cherryhotel.com"],
  ["front-office-manager", "priya.menon@cherryhotel.com"],
  ["front-desk", "rahul.nair@cherryhotel.com"],
  ["housekeeping", "imran.khan@cherryhotel.com"],
  ["food-beverage", "vikram.singh@cherryhotel.com"],
];
const browser = await chromium.launch();
const results = [];
for (const [label, email] of ROLES) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("response", (r) => { if (r.status() >= 500) errors.push(`${r.status()} ${r.url()}`); });
  await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
  await page.fill('input[type="email"], input[name="email"], #email', email);
  await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(700);
  await page.goto(`${BASE}/guest_enquiry`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(800);
  const state = await page.evaluate(() => ({
    add: !!Array.from(document.querySelectorAll("button")).find((x) => x.innerText.trim() === "Add Enquiry"),
    edit: Array.from(document.querySelectorAll("button")).some((x) => x.getAttribute("aria-label")?.startsWith("Edit enquiry")),
    delete: Array.from(document.querySelectorAll("button")).some((x) => x.getAttribute("aria-label")?.startsWith("Delete enquiry")),
    body: document.body.innerText.slice(-220),
  }));
  results.push({ label, email, ...state, errors });
  await context.close();
}
console.log(JSON.stringify(results, null, 2));
await browser.close();

/** User role-permission page RBAC probe; no permission changes. */
import { chromium } from "playwright";
const BASE = process.env.BASE || "http://127.0.0.1:5173";
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";
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
  page.on("response", (r) => { if (r.status() >= 500) errors.push(`${r.status()} ${r.url()}`); });
  await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
  await page.fill('input[type="email"], input[name="email"], #email', email);
  await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(700);
  await page.goto(`${BASE}/user`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(800);
  const state = await page.evaluate(() => ({
    accessible: !document.body.innerText.includes("You do not have access to this page"),
    roleSelect: !!document.querySelector(".perm-panel select"),
    matrix: !!document.querySelector(".permission-table"),
    body: document.body.innerText.slice(-180),
  }));
  out.push({ label, ...state, errors });
  await context.close();
}
console.log(JSON.stringify(out, null, 2));
await browser.close();

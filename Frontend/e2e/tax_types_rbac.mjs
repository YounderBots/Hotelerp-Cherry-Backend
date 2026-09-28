/** Tax type RBAC probe; no tax writes. */
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
  await page.waitForTimeout(1500);
  await page.goto(`${BASE}/tax_types`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(800);
  out.push({ label, ...(await page.evaluate(() => ({
    accessible: !document.body.innerText.includes("You do not have access to this page"),
    add: !!Array.from(document.querySelectorAll("button")).find((x) => x.innerText.trim() === "Add Tax Type"),
    view: !!Array.from(document.querySelectorAll("button")).find((x) => x.getAttribute("aria-label") === "View tax type"),
    edit: !!Array.from(document.querySelectorAll("button")).find((x) => x.getAttribute("aria-label") === "Edit tax type"),
    del: !!Array.from(document.querySelectorAll("button")).find((x) => x.getAttribute("aria-label") === "Delete tax type"),
    body: document.body.innerText.slice(-180),
  }))), errors });
  await context.close();
}
console.log(JSON.stringify(out, null, 2));
await browser.close();

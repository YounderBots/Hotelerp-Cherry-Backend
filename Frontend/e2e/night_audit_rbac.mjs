/**
 * Night-audit role/control probe. It never submits the irreversible run.
 * It checks what each seeded role can see and whether the run control is
 * enabled, then records the result for the QA register.
 */
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
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("response", (response) => {
    if (response.status() >= 500) errors.push(`${response.status()} ${response.url()}`);
  });
  await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
  await page.fill('input[type="email"], input[name="email"], #email', email);
  await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(800);
  await page.goto(`${BASE}/night_audit`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(900);
  const state = await page.evaluate(() => {
    const button = [...document.querySelectorAll("button")].find((x) => x.innerText.trim() === "Run Night Audit");
    return {
      visible: !!button,
      disabled: button ? button.disabled : null,
      title: button?.getAttribute("title") || "",
      body: document.body.innerText.slice(-300),
    };
  });
  results.push({ label, email, ...state, errors });
  await context.close();
}
console.log(JSON.stringify(results, null, 2));
await browser.close();

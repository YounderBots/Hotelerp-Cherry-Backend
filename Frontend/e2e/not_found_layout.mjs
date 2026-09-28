/** Not-found fallback layout check at the four supported widths. */
import { chromium } from "playwright";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const WIDTHS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1024, height: 900 },
  { name: "tablet", width: 768, height: 900 },
  { name: "mobile", width: 375, height: 667 },
];

const browser = await chromium.launch();
const rows = [];
for (const vp of WIDTHS) {
  const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(`${BASE}/no_such_page_qa`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(500);
  const metrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    heading: (document.querySelector("h1, h2") || {}).innerText || "",
    hasDashboardLink: !!Array.from(document.querySelectorAll("a")).find((a) => a.getAttribute("href") === "/dashboard"),
  }));
  rows.push({
    width: vp.name,
    ...metrics,
    overflowPx: metrics.scrollWidth - metrics.clientWidth,
    errors,
  });
  await context.close();
}
console.log(JSON.stringify(rows, null, 2));
await browser.close();

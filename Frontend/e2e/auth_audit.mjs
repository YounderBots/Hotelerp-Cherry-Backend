/**
 * Public authentication surface audit.
 *
 * The full route audit signs in before it walks the app, so it cannot catch a
 * login card that overflows a phone. This sweep opens every public auth URL at
 * all four supported viewport classes before any session exists.
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const OUT = process.env.OUT || "./e2e-reports/auth-audit.json";
const ROUTES = [
  "/",
  "/authentication/forgotpassword",
  "/authentication/lockscreen",
  "/authentication/register",
];
const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1024, height: 900 },
  { name: "tablet", width: 768, height: 900 },
  { name: "mobile", width: 375, height: 667 },
];

const browser = await chromium.launch();
const report = [];

for (const viewport of VIEWPORTS) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  let bucket = null;
  page.on("console", (message) => {
    if (message.type() === "error") bucket.consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => bucket.pageErrors.push(String(error)));
  page.on("requestfailed", (request) => bucket.networkErrors.push(`${request.url()} ${request.failure()?.errorText}`));

  for (const route of ROUTES) {
    bucket = { consoleErrors: [], pageErrors: [], networkErrors: [] };
    await page.goto(`${BASE}${route}`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(300);
    const probe = await page.evaluate(() => {
      const root = document.documentElement;
      const body = document.body;
      const overflow = Math.max(root.scrollWidth, body?.scrollWidth || 0) - root.clientWidth;
      return {
        text: (body?.innerText || "").trim(),
        overflow: Math.round(overflow),
        brokenImages: [...document.images]
          .filter((image) => image.complete && image.naturalWidth === 0)
          .map((image) => image.getAttribute("src") || "(no src)"),
        imagesWithoutAlt: [...document.images].filter((image) => !image.hasAttribute("alt")).length,
      };
    });
    report.push({
      viewport: viewport.name,
      route,
      textLength: probe.text.length,
      overflow: probe.overflow,
      brokenImages: probe.brokenImages,
      imagesWithoutAlt: probe.imagesWithoutAlt,
      ...bucket,
    });
    const problems = [];
    if (probe.overflow > 1) problems.push(`overflow+${probe.overflow}`);
    if (probe.brokenImages.length) problems.push(`brokenImages:${probe.brokenImages.length}`);
    if (bucket.consoleErrors.length) problems.push(`console:${bucket.consoleErrors.length}`);
    if (bucket.pageErrors.length) problems.push(`page:${bucket.pageErrors.length}`);
    if (bucket.networkErrors.length) problems.push(`network:${bucket.networkErrors.length}`);
    console.log(`${problems.length ? "!!" : "ok"} ${viewport.name.padEnd(7)} ${route.padEnd(34)} ${problems.join(" ")}`);
  }
  await context.close();
}

mkdirSync(OUT.slice(0, OUT.lastIndexOf("/")) || ".", { recursive: true });
writeFileSync(OUT, JSON.stringify(report, null, 2));
console.log(`\nwrote ${OUT}`);
await browser.close();
if (report.some((row) => row.overflow > 1 || row.brokenImages.length || row.consoleErrors.length || row.pageErrors.length || row.networkErrors.length)) {
  process.exitCode = 1;
}

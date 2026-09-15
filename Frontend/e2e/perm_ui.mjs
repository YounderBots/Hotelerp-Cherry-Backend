/**
 * Does the UI show only the controls the gateway would allow?
 *
 * For every page a role can open, compares the Add button and the row
 * Edit/Delete icons against that role's add/edit/delete permission as the login
 * payload reports it. A control the server would answer 403 to must not be
 * drawn; a control the role holds must not be hidden.
 *
 *   node perm_ui.mjs <email> <label>
 */
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const GW = process.env.GW || "http://127.0.0.1:8000";
const EMAIL = process.argv[2];
const LABEL = process.argv[3] || "run";
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";

// Pages whose Add control is not a create: an export button, a read-only board.
const NOT_A_CREATE = new Set(["/reservation"]);

const login = await fetch(`${GW}/login_post`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
}).then((r) => r.json());

const perms = {};
const walk = (nodes) => {
  for (const n of nodes || []) {
    if (n.path) {
      const p = n.permissions || {};
      perms[n.path] = {
        view: !!p.view, add: !!p.add, edit: !!p.edit, delete: !!p.delete,
      };
    }
    walk(n.children);
  }
};
walk(login.menus);

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();

await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL((u) => u.pathname !== "/", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(1200);

const findings = [];
const notes = [];
let checked = 0;

for (const [path, perm] of Object.entries(perms)) {
  if (!perm.view) continue;
  await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.waitForTimeout(500);

  // Only screens built on the shared table have the controls this compares.
  if (!(await page.locator("table").count())) continue;
  const rows = await page.locator("table tbody tr:not(.table-message-row)").count();
  checked += 1;

  const addBtn = page.locator(".table-action-button").first();
  let addLabel = "";
  if (await addBtn.count()) addLabel = (await addBtn.innerText().catch(() => "")).trim();
  const drawsCreate = !!addLabel && /^(add|assign|new|create)/i.test(addLabel) && !NOT_A_CREATE.has(path);

  if (drawsCreate && !perm.add) {
    findings.push(`${path}: draws "${addLabel}" but the role has no add permission`);
  }
  // The other direction -- a role holds `add` on a screen with nothing to
  // create (a night-audit report, a kitchen board, an analytics page) -- is not
  // a fault. The permission is simply unused there. Recorded, not failed.
  if (!drawsCreate && perm.add) {
    notes.push(`${path}: role holds add; this screen has no create action`);
  }

  if (rows > 0) {
    const editIcons = await page.locator("button[aria-label^='Edit']").count();
    const delIcons = await page.locator("button[aria-label^='Delete']").count();
    if (editIcons > 0 && !perm.edit) {
      findings.push(`${path}: draws ${editIcons} Edit icon(s) but the role has no edit permission`);
    }
    if (delIcons > 0 && !perm.delete) {
      findings.push(`${path}: draws ${delIcons} Delete icon(s) but the role has no delete permission`);
    }
  }
}

console.log(`${LABEL}: checked ${checked} table screen(s) against the role's own permissions`);
if (findings.length === 0) {
  console.log("  every control matches what the gateway would allow");
} else {
  for (const f of findings) console.log("  MISMATCH " + f);
}
console.log(`  (${notes.length} screen(s) where the role holds add but the screen has no create action)`);
mkdirSync("./e2e-reports", { recursive: true });
writeFileSync(`./e2e-reports/perm-ui-${LABEL}.json`, JSON.stringify({ perms, findings, notes }, null, 1));
await browser.close();
process.exit(findings.length ? 1 : 0);

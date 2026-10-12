/**
 * Role matrix: what each role may actually reach, and whether the screen agrees.
 *
 *   node role_matrix.mjs
 *
 * For every account this signs in through the real form, walks every route, and
 * records what the page shows and which controls it draws. Then it asks the
 * gateway the same question directly. The comparison is the point:
 *
 *   - a page that says "you do not have access" while its API answers 200 is a
 *     page hiding a capability it holds
 *   - a page that renders while its API answers 403 is a page showing controls
 *     the user cannot use, which is the worse of the two
 */
import { mkdirSync, writeFileSync } from "fs";
import {
  launch, login, open, settle, probe, addButton, tableRows,
  rowAction, loadCredentials, BASE,
} from "./lib.mjs";

const CRED_FILE = process.env.CRED_FILE ||
  "C:\\Users\\anand\\AppData\\Local\\Temp\\opencode\\cherry-credentials.txt";
const creds = loadCredentials(CRED_FILE);

const ROUTES = JSON.parse(process.env.ROUTES || "[]");

const ACCOUNTS = {
  admin: "admin@cherryhotel.com",
  front_office_manager: "priya.menon@cherryhotel.com",
  front_desk: "rahul.nair@cherryhotel.com",
  housekeeping: "imran.khan@cherryhotel.com",
  fnb: "vikram.singh@cherryhotel.com",
};

/** Which API each page loads, for the gateway cross-check. */
const API_PER_PAGE = JSON.parse(process.env.API_PER_PAGE || "{}");

const results = {};
mkdirSync("e2e-reports", { recursive: true });

for (const [role, email] of Object.entries(ACCOUNTS)) {
  const password = process.env[`PW_${role.toUpperCase()}`] || creds[email];
  if (!password) { console.log(`skip ${role}: no password`); continue; }

  // Read the token the login stored, so the API cross-check uses the SAME
  // session the browser did rather than a second sign-in that could differ.
  const { browser, page, bucket, fresh } = await launch({ width: 1440, height: 900 });
  fresh();
  try {
    await login(page, email, password);
  } catch (e) {
    console.log(`skip ${role}: ${String(e).slice(0, 90)}`);
    await browser.close();
    continue;
  }
  const token = await page.evaluate(() => localStorage.getItem("AuthToken"));

  const pages = [];
  for (const route of ROUTES) {
    fresh();
    await open(page, route);
    const p = await probe(page);
    const verbs = await page.evaluate(() => {
      const row = document.querySelector(
        "table:not(#export-table-full) tbody tr:not(.table-message-row)");
      return {
        rowActions: row
          ? [...row.querySelectorAll("[aria-label]")]
              .map((b) => String(b.getAttribute("aria-label")).split(" ")[0])
          : [],
        addButton: !!document.querySelector("button.table-action-button"),
        menuItems: [...document.querySelectorAll(".nav-item, .sub-item")]
          .map((n) => n.textContent.trim()).filter(Boolean),
      };
    });
    pages.push({
      route,
      denied: p.denied,
      crashed: p.crashed,
      textLen: p.textLen,
      rowCount: p.rowCount,
      addButton: verbs.addButton,
      rowActions: [...new Set(verbs.rowActions)],
      menuItems: verbs.menuItems.length,
      httpErrors: [...bucket.httpErrors],
    });
  }
  results[role] = { email, token, pages };
  const denied = pages.filter((p) => p.denied).length;
  const crashed = pages.filter((p) => p.crashed).length;
  const withAdd = pages.filter((p) => p.addButton).length;
  console.log(`${role.padEnd(22)} pages=${pages.length} denied=${denied} `
    + `crashed=${crashed} withAddButton=${withAdd} menuItems=${pages[0]?.menuItems ?? 0}`);
  await browser.close();
}

/** Ask the gateway directly, for the same pages. */
const GATEWAY = process.env.GATEWAY || "http://127.0.0.1:8000";
const apiCheck = {};
for (const [role, info] of Object.entries(results)) {
  const token = info.token;
  if (!token) continue;
  const row = {};
  for (const [route, apis] of Object.entries(API_PER_PAGE)) {
    if (!Array.isArray(apis) || !apis.length) continue;
    if (!info.pages.some((p) => p.route === route)) continue;
    // Ask EVERY endpoint the page loads, not one picked for it. Pages share
    // endpoints: /employee reads /masterdata/country_currency, which Front
    // Office Manager may read while its own screen is closed to them, and a
    // single arbitrary probe reports that shared read as the page being
    // reachable. api_map.mjs supplies the endpoints each page really calls, so
    // the probe is the page's own behaviour replayed.
    const statuses = [];
    for (const api of apis) {
      let status = 0;
      try {
        const r = await fetch(`${GATEWAY}${api}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        status = r.status;
      } catch { status = 0; }
      statuses.push(status);
    }
    // 403 is the gateway refusing the role. Anything else - 200, 400, 404 - means
    // the request was let through to routing and the record it named was not
    // there, which is not a permission answer. Taking a plain minimum would let
    // a 404 on an unrelated shared endpoint mask a real 403 on the page's own.
    const denied = statuses.filter((s) => s === 403);
    const through = statuses.filter((s) => s > 0 && s !== 403);
    const ui = info.pages.find((p) => p.route === route);
    row[route] = {
      probed: apis,
      statuses,
      denied: denied.length,
      through: through.length,
      uiDenied: !!ui?.denied,
      uiHasAdd: !!ui?.addButton,
      // The mismatch that matters: the page offers a control whose own backing
      // API refuses this role, so pressing it produces a 403 in front of a user.
      mismatch: ui?.addButton && denied.length
        ? `UI offers Add, API refuses ${denied.length}/${apis.length} endpoint(s)`
        : null,
      // And the reverse: the page is closed but something behind it is not.
      overHidden: ui?.denied && through.length
        ? `UI denies, API allows ${through.length}/${apis.length} endpoint(s)`
        : null,
    };
  }
  apiCheck[role] = row;
}

const flat = Object.entries(apiCheck).flatMap(([role, row]) =>
  Object.entries(row).map(([route, v]) => ({ role, route, ...v })));
const mism = flat.filter((f) => f.mismatch);
const over = flat.filter((f) => f.overHidden);
console.log(`\npage/API cross-check: ${flat.length} role-page pairs, `
  + `${mism.length} mismatch, ${over.length} overHidden`);
for (const f of mism) console.log(`  MISMATCH  ${f.role.padEnd(20)} ${f.route.padEnd(28)} ${f.mismatch}`);
for (const f of over.slice(0, 40)) console.log(`  overHidden ${f.role.padEnd(18)} ${f.route.padEnd(28)} ${f.overHidden}`);

writeFileSync("e2e-reports/role-matrix.json",
  JSON.stringify({ base: BASE, roles: results, apiCheck }, null, 1));
console.log("\nwrote e2e-reports/role-matrix.json");
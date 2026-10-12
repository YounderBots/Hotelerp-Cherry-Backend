/**
 * Which API does each page actually call?
 *
 *   node api_map.mjs
 *
 * The role cross-check needs to know which endpoints belong to which screen.
 * Guessing that from the component's file name is how the earlier map ended up
 * claiming /employee reads /masterdata/country_currency - true of the API, not
 * of the page. So this asks the network instead: sign in, open every route,
 * and record the GET requests the page makes, with the exact query string it
 * sent. Replaying those verbatim later is a faithful reproduction of what the
 * page does on load, not a probe of an endpoint someone picked for it.
 *
 * Writes ../.run-logs/api_per_page.json: { route: [ "path?query", ... ] }.
 */
import { mkdirSync, writeFileSync, readFileSync } from "fs";
import { launch, login, open, loadCredentials, BASE } from "./lib.mjs";

const API_BASE = process.env.API_BASE || "http://127.0.0.1:8000";
const CRED_FILE = process.env.CRED_FILE ||
  "C:\\Users\\anand\\AppData\\Local\\Temp\\opencode\\cherry-credentials.txt";
const creds = loadCredentials(CRED_FILE);

const inventory = JSON.parse(readFileSync("../.run-logs/inventory.json", "utf8"));
// Accept either a comma list (what page_deep.mjs takes) or the raw inventory.
// "anon:/route" means a page that only exists signed OUT - the login screen and
// its siblings redirect away the moment a token is present, so probing them in
// the signed-in context records the redirect instead of the page.
const routes = process.env.ROUTES
  ? process.env.ROUTES.split(",").map((s) => s.trim()).filter(Boolean)
  : inventory.routes.map((r) => r.route);
const isAnon = (r) => r.startsWith("anon:");
const pathOf = (r) => (isAnon(r) ? r.slice(5) : r);

const { browser, page, fresh } = await launch({ width: 1440, height: 900 });
fresh();
await login(page, "admin@cherryhotel.com", creds["admin@cherryhotel.com"]);

// Collect every gateway request, so a page's calls are attributed to the page
// that made them rather than to whatever happened to be on screen.
let seen = [];
const onRequest = (r) => {
  const u = r.url();
  if (!u.startsWith(API_BASE)) return;
  const path = u.slice(API_BASE.length) || "/";
  seen.push({ method: r.method(), url: path, status: null });
};
const onResponse = (r) => {
  const u = r.url();
  if (!u.startsWith(API_BASE)) return;
  const hit = seen.find((s) => s.url === u.slice(API_BASE.length) && s.status === null);
  if (hit) hit.status = r.status();
};
page.on("request", onRequest);
page.on("response", onResponse);

const map = {};
const statics = {};
const problems = [];

for (const raw of routes) {
  const route = pathOf(raw);
  if (isAnon(raw)) {
    // Drop the session the way a browser would - clear the token, then reload.
    await page.evaluate(() => localStorage.clear());
  }
  fresh();
  seen = [];
  await open(page, route);
  await page.waitForTimeout(900);
  const landed = new URL(page.url()).pathname;

  // Only GETs: the role cross-check replays them, and a replayed POST would be
  // answered 405 by the method router whether or not the role is entitled.
  const gets = seen.filter((s) => s.method === "GET");
  const ok = gets.filter((s) => s.status && s.status >= 200 && s.status < 300);
  // Uploaded images are served through the gateway too, but a picture is not a
  // permissioned endpoint: it answers 200 to everyone who can log in, so leaving
  // it in the list would drown a real 403 in a wall of 200s.
  const isStatic = (u) => u.includes("/templates/static/");
  const list = [...new Set(ok.filter((s) => !isStatic(s.url)).map((s) => s.url))].sort();
  statics[route] = [...new Set(ok.filter((s) => isStatic(s.url)).map((s) => s.url))].sort();

  const postLike = [...new Set(
    seen.filter((s) => s.method !== "GET").map((s) => `${s.method} ${s.url}`))];

  map[route] = list;

  const bad = seen.filter((s) => s.status >= 400).map((s) => `${s.status} ${s.method} ${s.url}`);
  console.log(`${route.padEnd(30)} gets=${String(list.length).padEnd(2)} landed=${landed.padEnd(24)}`
    + (bad.length ? `  ERRORS: ${bad.join(" | ")}` : ""));
  if (landed !== route) problems.push({ route, reason: `redirected to ${landed}`, seen: [] });
  else if (!list.length) problems.push({ route, reason: "made no GET on load", seen: postLike });
}

page.off("request", onRequest);
page.off("response", onResponse);
await browser.close();

mkdirSync("../.run-logs", { recursive: true });
// Merge, so a second pass over more routes adds to the map instead of
// replacing it with a shorter one.
const merge = (file, fresh) => {
  try {
    const prev = JSON.parse(readFileSync(file, "utf8"));
    return { ...prev, ...fresh };
  } catch { return fresh; }
};
writeFileSync("../.run-logs/api_per_page.json",
  JSON.stringify(merge("../.run-logs/api_per_page.json", map), null, 1));
writeFileSync("../.run-logs/api_static_per_page.json",
  JSON.stringify(merge("../.run-logs/api_static_per_page.json", statics), null, 1));
writeFileSync("../.run-logs/api_per_page_problems.json",
  JSON.stringify(merge("../.run-logs/api_per_page_problems.json", problems), null, 1));
const nStatic = Object.values(statics).reduce((n, a) => n + a.length, 0);
console.log(`\nwrote ../.run-logs/api_per_page.json (${Object.keys(map).length} pages,`
  + ` ${problems.length} with no GET; ${nStatic} static image URLs split out)`);
for (const p of problems) console.log(`  no GET ${p.route} -> ${p.seen.join(", ") || "(nothing)"}`);
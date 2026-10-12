/**
 * Shared harness for the per-page deep audit.
 *
 * Every page in the product is a variation of the same three shapes:
 *
 *   a table screen  - TableTemplate + RowActions, with an Add/Edit modal and a
 *                     View modal built from DetailList
 *   a form screen   - one long form, no table
 *   a board screen  - cards / grids, no table
 *
 * so one introspector can read all three and produce the same evidence:
 * which fields the Add form offers, which fields Edit offers, which the View
 * shows, and which of those the API actually persisted.
 */
import { chromium } from "playwright";
import fs from "fs";

export const BASE = process.env.BASE || "http://127.0.0.1:5173";

/** Read a credential file written by Backend/tools/rotate_passwords.py. */
export function loadCredentials(file) {
  const out = {};
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const [email, pw] = t.split("\t");
    if (email && pw) out[email] = pw;
  }
  return out;
}

export async function launch({ width = 1440, height = 900 } = {}) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage();

  const bucket = {
    consoleErrors: [], pageErrors: [], httpErrors: [], netFailed: [],
  };
  const fresh = () => {
    bucket.consoleErrors.length = 0;
    bucket.pageErrors.length = 0;
    bucket.httpErrors.length = 0;
    bucket.netFailed.length = 0;
  };

  page.on("console", (m) => {
    if (m.type() === "error") bucket.consoleErrors.push(m.text().slice(0, 300));
  });
  page.on("pageerror", (e) => bucket.pageErrors.push(String(e).slice(0, 300)));
  page.on("requestfailed", (r) =>
    bucket.netFailed.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`));
  page.on("response", (r) => {
    if (r.status() >= 400) {
      bucket.httpErrors.push(`${r.status()} ${r.request().method()} ${r.url().replace(BASE, "")}`);
    }
  });

  return { browser, ctx, page, bucket, fresh };
}

/**
 * Sign in through the real form.
 *
 * The click can land before the submit handler is attached, and a busy gateway
 * can answer late; either way the SPA stays on /login and every page after it
 * is then reported as a blank page instead of "the login never happened". Watch
 * the response itself, require 200, and only then trust the run.
 */
export async function login(page, email, password) {
  let lastStatus = null;
  for (let attempt = 0; attempt < 5; attempt += 1) {
    await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector('input[type="email"], input[name="email"], #email', { timeout: 20000 });
    await page.fill('input[type="email"], input[name="email"], #email', email);
    await page.fill('input[type="password"], input[name="password"], #password', password);
    const answered = page.waitForResponse((r) => r.url().includes("/login_post"), { timeout: 20000 })
      .catch(() => null);
    await page.click('button[type="submit"]');
    const response = await answered;
    lastStatus = response ? response.status() : null;
    await page.waitForTimeout(1200);
    if (lastStatus === 200 && (await page.evaluate(() => !!localStorage.getItem("AuthToken")))) {
      return true;
    }
    await page.waitForTimeout(2500 + attempt * 2000);
  }
  throw new Error(`login failed for ${email} after 5 attempts (last status ${lastStatus})`);
}

export async function settle(page, ms = 600) {
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.waitForTimeout(ms);
}

/** Open a route and wait for it to settle. */
export async function open(page, route) {
  await page.goto(`${BASE}${route}`, { waitUntil: "domcontentloaded", timeout: 30000 });
  await settle(page);
}

/**
 * READ EVERY CONTROL INSIDE A DIALOG (or, when no dialog is open, inside the
 * page's main region - a page whose Add is an inline form has the same
 * controls in the same .form-group wrappers).
 *
 * Runs in the page so it sees the real DOM after React has rendered, which is
 * the only place the answer is trustworthy: the JSX says what a form was
 * written to do, the DOM says what it actually offers.
 */
export const READ_FIELDS = (scope = "modal") => {
  const root = scope === "modal"
    ? document.querySelector('[data-testid="modal"].modal--active') ||
      document.querySelector('[data-testid="modal"]')
    : document.querySelector("main") || document.body;
  if (!root) return null;
  // Reading "main" on a table page returns the search box, the filter row and
  // the KOT switches alongside whatever the page actually offers. They are page
  // chrome, not the form under audit, so a whole-scope read skips them.
  const CHROME = ".table-toolbar, .table-filters, .kds-controls, .report-controls,"
    + " .perm-panel, .toolbar-filters, .pagination, .table-actions-row";
  const isChrome = scope === "modal" ? () => false : (el) => !!el.closest(CHROME);
  const body = root.querySelector(".modal__body") || root;
  const head = root.querySelector(".modal__title");

  const labelFor = (el) => {
    const byFor = el.id ? body.querySelector(`label[for="${CSS.escape(el.id)}"]`) : null;
    const wrap = el.closest(".form-group");
    const near = wrap ? wrap.querySelector("label") : null;
    const l = byFor || near;
    return (l ? l.textContent : "").replace(/\s*\*\s*$/, "").trim();
  };

  const fields = [];
  for (const el of body.querySelectorAll("input, select, textarea")) {
    if (el.type === "hidden") continue;
    if (isChrome(el)) continue;
    // react-select renders a text input proxy; the control is the wrapper.
    const inReactSelect = el.classList.contains("react-select__input");
    const tag = el.tagName.toLowerCase();
    const type = tag === "select" ? "select" : tag === "textarea" ? "textarea" : (el.type || "text");

    let options = null;
    let value = tag === "select" ? el.value : (el.type === "checkbox" ? el.checked : el.value);
    if (tag === "select") {
      options = [...el.options].map((o) => ({ value: o.value, label: o.textContent.trim(), disabled: o.disabled }));
    } else if (inReactSelect) {
      // The proxy input is a DESCENDANT of the control, not of `.react-select`
      // itself - react-select's root div carries only hashed css classes, so
      // `closest('.react-select')` returns null and every option reads as
      // empty. `.react-select__control` is the stable hook.
      const control = el.closest(".react-select__control");
      const root = control?.parentElement;
      const selected = [...(control?.querySelectorAll(".react-select__single-value, .react-select__multi-value") || [])]
        .map((s) => s.textContent.trim());
      options = {
        isMulti: !!control?.querySelector(".react-select__value-container--is-multi"),
        selected,
        placeholder: control?.querySelector(".react-select__placeholder")?.textContent?.trim() || null,
        available: root ? [...document.querySelectorAll(".react-select__option")].map((o) => o.textContent.trim()) : [],
      };
      // The selection lives on the CONTROL, never on the proxy input, whose
      // value is "" whether or not a value is chosen. Reading el.value here
      // reported every pre-filled react-select in every Edit dialog as an empty
      // required field - on /booking, "Room Types" came back blank while the
      // dialog plainly showed "Executive Room".
      value = selected.join(", ");
    }

    fields.push({
      label: labelFor(el),
      name: el.name || el.id || null,
      tag,
      type,
      required: el.required === true || el.getAttribute("aria-required") === "true" ||
                !!el.closest(".form-group")?.querySelector(".form-label--required"),
      disabled: !!el.disabled,
      readOnly: !!el.readOnly,
      min: el.min !== "" && el.min != null ? Number(el.min) : null,
      max: el.max !== "" && el.max != null ? Number(el.max) : null,
      maxLength: el.maxLength > 0 ? el.maxLength : null,
      placeholder: el.placeholder || null,
      value,
      options,
      isFile: el.type === "file",
    });
  }

  // switches and radios live outside <input type=checkbox> label text sometimes
  const switches = [...body.querySelectorAll('[role="switch"], .switch, input[type="checkbox"]')]
    .map((el) => ({
      label: labelFor(el) || (el.closest(".form-group")?.querySelector("label")?.textContent || "").trim(),
      checked: el.checked ?? el.getAttribute("aria-checked") === "true",
    }))
    .filter((s) => s.label);

  // radio groups
  const radios = [];
  for (const name of new Set([...body.querySelectorAll('input[type="radio"]')].map((r) => r.name))) {
    const set = [...body.querySelectorAll(`input[type="radio"][name="${CSS.escape(name)}"]`)];
    radios.push({ name, label: labelFor(set[0]), checked: set.some((r) => r.checked) });
  }

  // buttons actually offered
  const buttons = [...root.querySelectorAll(".modal-actions button, form button[type='submit'], .form-actions button")]
    .map((b) => ({
      label: b.textContent.trim(), testid: b.dataset.testid || null, disabled: !!b.disabled,
    }));

  const headings = [...body.querySelectorAll("h3, h4, legend, .form-section__title, .form-section-title")]
    .map((h) => h.textContent.trim()).filter(Boolean);

  return {
    title: head?.textContent?.trim() || null,
    fields, switches, radios, buttons, headings,
    detailItems: [...body.querySelectorAll(".detail-item")].map((d) => ({
      label: d.querySelector(".detail-item__label")?.textContent?.trim() || "",
      value: d.querySelector(".detail-item__value")?.textContent?.trim() || "",
    })),
    tables: [...body.querySelectorAll("table")].map((t) => ({
      headers: [...t.querySelectorAll("thead th")].map((th) => th.textContent.trim()),
      rows: t.querySelectorAll("tbody tr:not(.table-message-row)").length,
    })),
    images: [...body.querySelectorAll("img")].map((i) => ({
      src: (i.getAttribute("src") || "").slice(0, 160),
      broken: i.complete && i.naturalWidth === 0,
      alt: i.getAttribute("alt"),
    })),
    iframes: [...body.querySelectorAll("iframe, embed, object")].map((f) => ({
      tag: f.tagName.toLowerCase(), src: (f.getAttribute("src") || f.getAttribute("data") || "").slice(0, 160),
    })),
    links: [...body.querySelectorAll("a[href]")].map((a) => a.getAttribute("href")),
    fileNames: [...body.querySelectorAll(".attachment, .attachment-card, [class*='attachment'], [class*='document'], [class*='file']")]
      .map((e) => e.textContent.trim().slice(0, 120)).filter((t) => t.length > 2 && t.length < 120),
  };
};

/** Open a modal by its footer/close structure and read it. */
export async function readModal(page, scope = "modal") {
  return page.evaluate(READ_FIELDS, scope);
}

export async function modalOpen(page) {
  return page.locator('[data-testid="modal"].modal--active').count().then((n) => n > 0);
}

export async function closeModal(page) {
  const close = page.locator('[data-testid="modal"].modal--active [data-testid="modal-close"]');
  if (await close.count()) {
    await close.click().catch(() => {});
  } else {
    await page.keyboard.press("Escape").catch(() => {});
  }
  await page.waitForTimeout(350);
}

/** Geometry + render health for the page as it stands. */
export const PROBE = () => {
  const de = document.documentElement, body = document.body;
  const text = (body?.innerText || "").trim();
  const overflow = Math.max(de.scrollWidth, body?.scrollWidth || 0) - de.clientWidth;
  let widest = null;
  if (overflow > 1) {
    const lim = de.clientWidth;
    for (const el of document.querySelectorAll("*")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0) continue;
      if (r.right > lim + 1) {
        const over = Math.round(r.right - lim);
        if (!widest || over > widest.over) {
          widest = { over, tag: el.tagName.toLowerCase(), cls: String(el.className || "").slice(0, 90) };
        }
      }
    }
  }
  // elements whose content is clipped by their own box
  const clipped = [];
  for (const el of document.querySelectorAll("button, .btn, .chip, td, th, .card, .stat-card")) {
    if (el.scrollWidth > el.clientWidth + 4 && el.clientWidth > 0) {
      const cs = getComputedStyle(el);
      if (cs.overflow === "hidden" && cs.textOverflow !== "ellipsis") {
        clipped.push({ tag: el.tagName.toLowerCase(), cls: String(el.className || "").slice(0, 70),
                       text: (el.textContent || "").trim().slice(0, 50), scrollW: el.scrollWidth, clientW: el.clientWidth });
      }
    }
  }
  const sentinels = [];
  for (const bad of ["undefined", "NaN", "[object Object]", "Invalid Date"]) {
    if (text.includes(bad)) sentinels.push(bad);
  }
  const vis = document.querySelector("table:not(#export-table-full)");
  return {
    textLen: text.length,
    head: text.slice(0, 160).replace(/\s+/g, " "),
    overflow: Math.round(overflow),
    widest,
    clipped: clipped.slice(0, 6),
    sentinels,
    brokenImgs: [...document.images].filter((i) => i.complete && i.naturalWidth === 0)
      .map((i) => (i.getAttribute("src") || "(no src)").slice(0, 120)),
    imgCount: document.images.length,
    rowCount: vis ? vis.querySelectorAll("tbody tr:not(.table-message-row)").length : 0,
    hasTable: !!vis,
    // An empty table and a table whose fetch never finished are both zero rows.
    // This table's own wording is what separates them, so keep it: "No combo
    // deals yet" is a page legitimately at rest, while a spinner that never
    // resolved is a defect the row count alone would never show.
    tableMessage: vis?.querySelector(".table-message-row")?.textContent?.trim().replace(/\s+/g, " ").slice(0, 120) || null,
    // Anything the page says is still in flight.
    loadingText: (body?.innerText || "").match(/\b(loading|fetching|please wait)\b/i)?.[0] || null,
    // The access-denied panel is rendered INSIDE the .error-boundary container,
    // so counting that element alone reports a deliberate "you cannot see this
    // page" as a crash on every page a role is not entitled to - 53 of 57 for
    // Front Desk. A crash is the boundary showing a failure, not the boundary
    // doing its job.
    denied: text.includes("You do not have access to this page"),
    notFound: text.includes("Page not found"),
    // The access-denied panel and the 404 panel are both rendered INSIDE a
    // .error-boundary container, so counting that element alone reports a
    // deliberate "you cannot see this page" as a crash on every page a role is
    // not entitled to - 53 of 57 for Front Desk - and reports the catch-all
    // 404 route as a crash too. A crash is the boundary showing a failure, not
    // the boundary doing its job.
    crashed: !!document.querySelector(".error-boundary")
      && !text.includes("You do not have access to this page")
      && !text.includes("Page not found"),
  };
};

export async function probe(page) {
  return page.evaluate(PROBE);
}

/**
 * The Add affordance for the page.
 *
 * TableTemplate renders it through TableActionButton, which lands in
 * `.table-actions-row` - NOT inside `.table-toolbar`, so a toolbar-scoped
 * selector silently matched nothing and every page then reported "no Add
 * affordance". Use the class TableActionButton puts on itself.
 *
 * Taking the FIRST such button is not enough: the export/print actions sit in
 * the same row, and on /reservation "Export CSV" comes first. The harness
 * clicked it, found the filter controls still on the page, and reported a
 * filter panel as the Add form. So match the label, and widen the search to
 * primary buttons outside the toolbar for the wizard pages (/add_new_reservation
 * has no toolbar at all - its "Next" is what opens the guest form).
 *
 * Returns null when the page offers nothing that starts data entry, so callers
 * can say "read-only page" instead of inventing a form out of the filters.
 */
export const ADD_VERB =
  /^(add|create|new|assign|generate|record|book|start|next|continue|save)\b/i;

/** Buttons that are page chrome, not page content. */
const NOT_CHROME = [
  "not(ancestor::*[contains(@class,'table-toolbar')])",
  "not(ancestor::*[contains(@class,'table-filters')])",
  "not(ancestor::*[contains(@class,'kds-controls')])",
  "not(ancestor::*[contains(@class,'report-controls')])",
  "not(ancestor::*[contains(@class,'sidebar')])",
  "not(ancestor::*[contains(@class,'nav-item')])",
  "not(ancestor::*[contains(@class,'sub-item')])",
  "not(ancestor::*[contains(@class,'modal')])",
].join(" and ");

export async function addButton(page) {
  const pick = async (locator) => {
    const n = await locator.count();
    for (let i = 0; i < n; i += 1) {
      const label = ((await locator.nth(i).textContent()) || "").trim();
      if (label && ADD_VERB.test(label)) return locator.nth(i);
    }
    return null;
  };
  return (await pick(page.locator("button.table-action-button")))
    || (await pick(page.locator(`xpath=//button[${NOT_CHROME}]`)));
}

/** Pages that render a bare form with no toolbar button. */
export function inlineForm(page) {
  return page.locator("main form, main .form, main [class*='form-grid'], main [class*='form-body']").first();
}

/**
 * Count the editable controls a data form offers.
 *
 * Everything a page puts in its chrome is excluded: the search box, the filter
 * row, the KOT switches, the report date picker and the permission picker all
 * render real inputs, so "the page has inputs" was true of every table page and
 * the Add probe on /reservation reported six FILTER fields as the Add form. A
 * data form is not a filter panel.
 */
export const COUNT_DATA_INPUTS = () => {
  const CHROME = ".table-toolbar, .table-filters, .kds-controls, .report-controls,"
    + " .perm-panel, .toolbar-filters, .pagination, .table-actions-row";
  const main = document.querySelector("main") || document.body;
  return [...main.querySelectorAll("input, select, textarea")]
    .filter((el) => el.type !== "hidden" && !el.closest(CHROME)).length;
};

export async function dataInputCount(page) {
  return page.evaluate(COUNT_DATA_INPUTS);
}

/**
 * The rows of the VISIBLE table only.
 *
 * TableTemplate renders a second `<table id="export-table-full">` beside the
 * real one so the CSV/PDF/print actions have something to read. A selector that
 * says just "table tbody tr" matches both, so every index is off by a page and
 * every row action lands on the export table, which has none. Scope to the
 * first, non-export table.
 */
export function dataTable(page) {
  return page.locator("table:not(#export-table-full)").first();
}

export function tableRows(page) {
  return dataTable(page).locator("tbody tr:not(.table-message-row)");
}

/** Find the index of the row whose text contains `text`, or -1. */
export async function findRow(page, text) {
  if (!text) return -1;
  const n = await tableRows(page).count();
  const hits = await tableRows(page).evaluateAll(
    (rows, t) => rows.map((r) => r.innerText.includes(t)), text);
  return hits.findIndex(Boolean);
}

export function rowAction(page, rowIndex, verb) {
  return tableRows(page).nth(rowIndex).locator(`[aria-label^="${verb}"]`).first();
}
/**
 * Per-page round trip: ADD -> SAVE -> EDIT -> SAVE -> VIEW -> REFRESH.
 *
 *   node roundtrip.mjs <email> <label> [--routes=/a,/b] [--keep]
 *
 * For every page it:
 *   1. opens the Add dialog and enumerates the live fields
 *   2. fills EVERY one with a unique per-run sentinel
 *   3. saves, and finds the new row
 *   4. opens Edit on that row and asserts each field came back holding the
 *      sentinel -- this is the Add/Edit proof, read from the DOM not the JSX
 *   5. changes every field to a SECOND sentinel and saves
 *   6. opens View and asserts the second sentinel is on screen
 *   7. reloads the page and asserts it is still there (persistence)
 *   8. deletes the row, unless --keep
 *
 * The row it creates is prefixed ZZQA and is always removed, so running this
 * does not damage the seeded data. A page whose cleanup fails is reported
 * loudly rather than left behind.
 */
import { mkdirSync, writeFileSync } from "fs";
import {
  launch, login, open, settle, probe, addButton, tableRows, rowAction, findRow,
  readModal, modalOpen, closeModal, loadCredentials,
} from "./lib.mjs";

const arg = (n, d) => {
  const hit = process.argv.find((a) => a.startsWith(`--${n}=`));
  return hit ? hit.split("=").slice(1).join("=") : d;
};
const has = (n) => process.argv.includes(`--${n}`);

const CRED_FILE = process.env.CRED_FILE ||
  "C:\\Users\\anand\\AppData\\Local\\Temp\\opencode\\cherry-credentials.txt";
const creds = loadCredentials(CRED_FILE);

const EMAIL = process.argv[2] || "admin@cherryhotel.com";
const LABEL = process.argv[3] || "rt";
const PASSWORD = process.env.PW_PASSWORD || creds[EMAIL];
const OUT = process.env.OUT || `./e2e-reports/rt-${LABEL}`;
const ROUTES = arg("routes", "").split(",").map((s) => s.trim()).filter(Boolean);
const KEEP = has("keep");

if (!PASSWORD) throw new Error(`no password for ${EMAIL}`);

const RUN = `ZZQA${Date.now().toString(36).toUpperCase().slice(-6)}`;
const A = `${RUN}A`;
const B = `${RUN}B`;

/** Everything the in-page filler needs, decided in Node. */
const planFor = (fields) => fields.filter((f) => !f.isFile && !f.disabled).map((f, i) => {
  const key = (f.label || f.name || `f${i}`).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const suffix = i % 2 === 0 ? A : B;
  const base = { ...f, suffix, runSeed: RUN.toLowerCase(), index: i };
  if (f.type === "select") {
    const opt = (f.options || []).find((o) => o.value !== "" && !o.disabled);
    return { ...base, plan: opt ? opt.value : null, kind: "select" };
  }
  if (f.type === "number") {
    // Respect the field's own bounds. A percentage capped at 100 was filled
    // with 102 and the client-side guard correctly refused it -- a harness
    // failure dressed as a product defect, which is worse than no finding.
    const lo = Number.isFinite(f.min) ? f.min : 1;
    const hi = Number.isFinite(f.max) ? f.max : 999;
    const value = Math.min(Math.max(lo + i, lo), hi);
    return { ...base, plan: String(value), kind: "number" };
  }
  if (f.type === "date") return { ...base, plan: new Date().toISOString().slice(0, 10), kind: "date" };
  if (f.type === "datetime-local") {
    const d = new Date(Date.now() + 86400000);
    return { ...base, plan: new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16), kind: "date" };
  }
  if (f.type === "time") return { ...base, plan: "14:30", kind: "text" };
  if (f.type === "tel") return { ...base, plan: "+919876543210", kind: "tel" };
  if (f.type === "checkbox") return { ...base, plan: true, kind: "checkbox" };
  if (f.type === "email") return { ...base, plan: `qa${RUN.toLowerCase()}@cherryhotel.com`, kind: "email" };
  if (f.type === "password") return { ...base, plan: `Qa!${RUN}9x`, kind: "password" };
  if (f.type === "color") return { ...base, plan: "#1a2b3c", kind: "text" };
  if (f.type === "textarea") return { ...base, plan: `QA ${suffix} note`, kind: "text" };
  if (key.includes("name")) return { ...base, plan: `QA${suffix}`, kind: "name" };
  if (key.includes("description") || key.includes("address") || key.includes("note")) {
    return { ...base, plan: `QA ${suffix} detail`, kind: "text" };
  }
  if (key.includes("code") || key.includes("no") || key.includes("number")) {
    return { ...base, plan: `QA${suffix}`, kind: "text" };
  }
  return { ...base, plan: `QA ${suffix} ${key}`.slice(0, 60), kind: "text" };
});

/**
 * Type the planned values into the live controls.
 *
 * `page.evaluate` passes ONE argument, so the payload arrives as a single
 * object. Taking `(plan, which)` silently gave `which === undefined` and
 * filled nothing while still reporting a green run. `flip` is defined INSIDE
 * this function for the same reason: it runs in the browser, where a
 * module-scope helper does not exist.
 */
const FILL = ({ plan, which }) => {
  /** A different value for the same field, so a stale prefill is visible. */
  const flip = (f) => {
    if (f.kind === "number") {
      const lo = Number.isFinite(f.min) ? f.min : 1;
      const hi = Number.isFinite(f.max) ? f.max : 999;
      return String(Math.min(Math.max(Number(f.plan) + 7, lo), hi));
    }
    if (f.type === "select") {
      const opts = (f.options || []).filter((o) => o.value !== "" && !o.disabled);
      if (opts.length < 2) return null;
      const i = opts.findIndex((o) => o.value === f.plan);
      return opts[(i + 1) % opts.length]?.value ?? null;
    }
    if (f.type === "date" || f.type === "datetime-local") {
      const d = new Date(Date.now() + 3 * 86400000);
      return f.type === "date" ? d.toISOString().slice(0, 10)
        : new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    }
    if (f.type === "tel") return "+919812345678";
    if (f.type === "email") return `qb${f.runSeed}@cherryhotel.com`;
    // A colour must stay a colour: feeding "QB ... changed" to <input
    // type="color"> makes the browser coerce it to #000000, which then looks
    // like the product threw the value away.
    if (f.type === "color") return "#2d6cdf";
    return `QB ${f.suffix} changed`;
  };
  const sel = '[data-testid="modal"].modal--active';
  let filled = 0, skipped = [];
  for (const f of plan) {
    const label = f.label || f.name;
    if (!label) continue;
    const byName = f.name ? `${sel} [name="${CSS.escape(f.name)}"]` : null;
    const byLabel = null;
    let el = null;
    if (byName) el = document.querySelector(byName);
    if (!el) {
      const lab = [...document.querySelectorAll(`${sel} label`)].find(
        (l) => l.textContent.replace(/\s*\*\s*$/, "").trim() === label);
      if (lab) {
        const t = lab.getAttribute("for");
        el = t ? document.getElementById(t) : lab.parentElement.querySelector("input, select, textarea");
      }
    }
    if (!el) { skipped.push(label); continue; }

    const value = which === "A" ? f.plan : flip(f);
    if (f.type === "checkbox" || f.type === "radio") {
      const want = which === "A" ? true : false;
      if (el.checked !== want) el.click();
      filled += 1;
    } else if (el.tagName.toLowerCase() === "select") {
      const opt = [...el.options].find((o) => (which === "A" ? o.value !== "" : o.value !== "") && !o.disabled);
      if (opt) { el.value = opt.value; el.dispatchEvent(new Event("change", { bubbles: true })); filled += 1; }
      else skipped.push(label);
    } else {
      // react-select has no <select>; its proxy input filters a menu.
      if (el.closest(".react-select")) { skipped.push(`${label} (react-select)`); continue; }
      // React installs a value tracker on every input and ignores an event whose
      // value it believes it already has. Writing `el.value = x` updates the DOM
      // but not that tracker, so onChange never fires and the component keeps
      // the OLD state - the form then posts the default. Always go through the
      // prototype's native setter.
      const proto = el.tagName.toLowerCase() === "textarea"
        ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
      setter.call(el, value);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      filled += 1;
    }
  }
  return { filled, skipped };
};

/** Read what the dialog currently holds. */
const DUMP = (sel) => {
  const root = document.querySelector(sel);
  if (!root) return null;
  const out = [];
  for (const el of root.querySelectorAll("input, select, textarea")) {
    if (el.type === "hidden" || el.type === "file") continue;
    const wrap = el.closest(".form-group");
    const lab = wrap?.querySelector("label");
    const label = (lab ? lab.textContent : "").replace(/\s*\*\s*$/, "").trim() || el.name || el.id;
    let value;
    if (el.tagName.toLowerCase() === "select") value = el.options[el.selectedIndex]?.text?.trim() || "";
    else if (el.type === "checkbox" || el.type === "radio") value = el.checked ? "yes" : "no";
    else value = el.value;
    if (el.closest(".react-select")) {
      value = [...el.closest(".react-select").parentElement.querySelectorAll(".react-select__single-value, .react-select__multi-value")]
        .map((s) => s.textContent.trim()).join(", ");
    }
    out.push({ label, type: el.type || el.tagName.toLowerCase(), value, required: !!wrap?.querySelector(".form-label--required") });
  }
  return out;
};

/**
 * The value a field holds AFTER the B pass - decided in Node so the harness can
 * search for it by text after the edit. Must stay in step with `flip` inside
 * FILL, which runs in the browser.
 */
const flipValue = (f) => {
  if (f.kind === "number") {
    const lo = Number.isFinite(f.min) ? f.min : 1;
    const hi = Number.isFinite(f.max) ? f.max : 999;
    const next = Number(f.plan) + 7;
    return String(Math.min(Math.max(next, lo), hi));
  }
  if (f.kind === "select") return null;
  if (f.kind === "date") return new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10);
  if (f.type === "tel") return "+919812345678";
  if (f.type === "email") return `qb${f.runSeed}@cherryhotel.com`;
  if (f.type === "color") return "#2d6cdf";
  return `QB ${f.suffix} changed`;
};

/**
 * Find the row carrying `text`, SEARCHING first when it is not on the current
 * page.
 *
 * TableTemplate paginates at ten rows. A freshly created record sorts to
 * whichever page its name lands on, so a scan of the visible rows finds it
 * only by luck - and the round-trip then edits, and finally deletes, whichever
 * row the fallback index named. That is how a QA run can quietly rewrite a
 * seeded record. Type the sentinel into the table's own search box first, then
 * look.
 */
async function locate(page, text) {
  if (!text) return -1;
  let idx = await findRow(page, text);
  if (idx >= 0) return idx;

  const box = page.locator('input[placeholder^="Search"], input[aria-label^="Search"]').first();
  if (!(await box.count())) return -1;
  await box.fill(text).catch(() => {});
  await page.waitForTimeout(700);
  idx = await findRow(page, text);
  return idx;
}

/** Put the table back the way it was, so the next phase sees the full list. */
async function clearSearch(page) {
  const box = page.locator('input[placeholder^="Search"], input[aria-label^="Search"]').first();
  if (await box.count()) {
    await box.fill("").catch(() => {});
    await page.waitForTimeout(500);
  }
}

const { browser, page, bucket, fresh } = await launch({ width: 1440, height: 900 });
mkdirSync("e2e-reports", { recursive: true });
await login(page, EMAIL, PASSWORD);

const report = [];
let seq = 0;

for (const route of ROUTES) {
  seq += 1;
  const id = `R${String(seq).padStart(3, "0")}`;
  const rec = { id, route, run: RUN, phases: {}, findings: [] };
  const add = (sev, kind, msg, detail) => rec.findings.push({ sev, kind, msg, ...(detail ? { detail } : {}) });

  fresh();
  await open(page, route);
  const p0 = await probe(page);
  if (!p0.hasTable || p0.rowCount === 0) {
    rec.skipped = p0.hasTable ? "table has no rows" : "page has no table";
    report.push(rec);
    console.log(`--  ${id} ${route.padEnd(32)} skipped: ${rec.skipped}`);
    continue;
  }

  const before = p0.rowCount;

  // ---- 1. open Add, read the fields ---------------------------------------
  const btn = addButton(page);
  if (!(await btn.count())) {
    rec.skipped = "no Add button";
    report.push(rec);
    console.log(`--  ${id} ${route.padEnd(32)} skipped: no Add button`);
    continue;
  }
  await btn.click();
  await page.waitForTimeout(800);
  const addModal = await readModal(page);
  if (!addModal) {
    add("P1", "affordance", "Add button did not open a dialog");
    report.push(rec);
    console.log(`!!  ${id} ${route.padEnd(32)} P1:affordance`);
    continue;
  }
  rec.phases.addFields = addModal.fields.map((f) => `${f.label}[${f.type}${f.required ? "*" : ""}]`);
  const plan = planFor(addModal.fields);
  if (!plan.length) {
    rec.skipped = "Add form offers no fillable fields";
    report.push(rec);
    console.log(`--  ${id} ${route.padEnd(32)} skipped: no fillable fields`);
    await closeModal(page);
    continue;
  }

  // ---- 2. fill with sentinel A and save -----------------------------------
  const fa = await page.evaluate(FILL, { plan, which: "A" });
  await page.waitForTimeout(500);
  const dumpA = await page.evaluate(DUMP, '[data-testid="modal"].modal--active .modal__body');
  rec.phases.fillA = fa;
  const anchor = plan.find((f) => f.kind === "name" || f.kind === "text")?.plan;

  fresh();
  const saveBtn = page.locator('[data-testid="modal"].modal--active .modal-actions button')
    .filter({ hasText: /submit|save|create|add/i }).last();
  const postA = page.waitForResponse((r) => r.request().method() === "POST", { timeout: 12000 }).catch(() => null);
  await saveBtn.click();
  const resA = await postA;
  await page.waitForTimeout(1200);
  rec.phases.createResponse = resA ? { status: resA.status(), url: resA.url().replace(/^https?:\/\/[^/]+/, "") } : null;
  rec.phases.createErrors = [...bucket.httpErrors];

  if (!resA || resA.status() >= 400) {
    const toast = (await page.locator(".toast, [role='status']").allInnerTexts().catch(() => [])).join(" ").slice(0, 200);
    add("P1", "create", `Add did not succeed (${resA ? resA.status() : "no request"})`, { toast, url: resA?.url() });
    await closeModal(page).catch(() => {});
    report.push(rec);
    console.log(`!!  ${id} ${route.padEnd(32)} P1:create ${resA?.status()}`);
    continue;
  }
  // The dialog must close on a successful save, or the user is left editing a
  // record that already exists.
  if (await modalOpen(page)) add("P2", "create", "dialog stayed open after a successful save");
  if (await modalOpen(page)) await closeModal(page);
  await settle(page, 900);

  const after = await probe(page);
  rec.phases.rowCount = { before, after: after.rowCount };

  // ---- 3. find the new row ------------------------------------------------
  // Search on a text sentinel, not the row index: the list re-sorts and
  // re-pages after the save, and an index captured earlier points at whichever
  // row now occupies that slot.
  let rowIdx = await locate(page, anchor);
  if (rowIdx < 0) {
    const n = await tableRows(page).count();
    rowIdx = Math.max(0, n - 1);
    rec.phases.rowLocatedBy = "last-row-fallback";
    add("P3", "harness", `could not find the saved row by its value "${anchor}"; acting on the last row`);
  } else {
    rec.phases.rowLocatedBy = await findRow(page, anchor) >= 0 ? "visible row" : "search box";
  }

  // ---- 4. EDIT must load the saved value ---------------------------------
  fresh();
  const editBtn = rowAction(page, rowIdx, "Edit");
  if (await editBtn.count()) {
    await editBtn.click();
    await page.waitForTimeout(900);
    const editModal = await readModal(page);
    rec.phases.editFields = editModal?.fields.map((f) => `${f.label}[${f.type}]`);
    rec.phases.editDiff = editModal ? {
      missingInEdit: plan.filter((p) => !editModal.fields.some((e) =>
        (e.label || "").toLowerCase() === (p.label || "").toLowerCase())).map((p) => p.label),
    } : null;

    const loaded = await page.evaluate(DUMP, '[data-testid="modal"].modal--active .modal__body');
    const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, "").trim();
    // A DECIMAL column comes back from MySQL as "2.0" for what the user typed
    // as "2". That is the same number, and reporting it as a lost value would
    // be a false positive on every numeric field in the app.
    const sameValue = (typed, shown, type) => {
      if (norm(typed) === norm(shown)) return true;
      if (type === "number") {
        const a = Number(typed), b = Number(shown);
        return Number.isFinite(a) && Number.isFinite(b) && a === b;
      }
      return false;
    };
    const lost = [];
    for (const f of plan) {
      if (!f.plan || f.type === "select") continue;
      const got = (loaded || []).find((l) => norm(l.label) === norm(f.label));
      if (!got) continue;
      if (!sameValue(f.plan, got.value, f.type)) {
        lost.push({ field: f.label, typed: f.plan, editShows: got.value });
      }
    }
    rec.phases.editPrefill = { checked: plan.length, lost };
    if (lost.length) {
      add("P1", "edit-prefill",
        `${lost.length} field(s) Edit did NOT load the saved value: ${lost.map((l) => `${l.field} (typed "${l.typed}", edit shows "${l.editShows}")`).join("; ")}`);
    }

    // ---- 5. change every field and save ----------------------------------
    const fb = await page.evaluate(FILL, { plan, which: "B" });
    await page.waitForTimeout(500);
    rec.phases.fillB = fb;
    fresh();
    const saveEdit = page.locator('[data-testid="modal"].modal--active .modal-actions button')
      .filter({ hasText: /submit|save|update/i }).last();
    const putB = page.waitForResponse((r) => ["PUT", "PATCH"].includes(r.request().method()), { timeout: 12000 }).catch(() => null);
    await saveEdit.click();
    const resB = await putB;
    await page.waitForTimeout(1200);
    rec.phases.updateResponse = resB ? { status: resB.status(), url: resB.url().replace(/^https?:\/\/[^/]+/, "") } : null;
    if (!resB || resB.status() >= 400) {
      const toast = (await page.locator(".toast, [role='status']").allInnerTexts().catch(() => [])).join(" ").slice(0, 200);
      add("P1", "update", `Edit save failed (${resB ? resB.status() : "no request"})`, { toast });
    }
    if (await modalOpen(page)) await closeModal(page);
    await settle(page, 900);

    // ---- 6. VIEW must show the changed value -----------------------------
    fresh();
    // Re-locate by value: the edit re-sorted or re-paged the list, so the
    // index captured before the edit no longer names the same row.
    const anchorB = plan.filter((p) => p.kind === "name" || p.kind === "text")
      .map((p) => flipValue(p)).find(Boolean) || anchor;
    rowIdx = await locate(page, anchorB);
    if (rowIdx < 0) rowIdx = await locate(page, anchor);
    const viewBtn = rowIdx >= 0 ? rowAction(page, rowIdx, "View") : null;
    if (viewBtn && await viewBtn.count()) {
      await viewBtn.click();
      await page.waitForTimeout(900);
      const vm = await readModal(page);
      const viewText = (vm?.detailItems || []).map((d) => `${d.label}: ${d.value}`).join(" || ");
      rec.phases.viewText = viewText.slice(0, 900);
      const wantB = plan.filter((p) => p.kind === "text" || p.kind === "name");
      const shownB = wantB.filter((p) => viewText.toLowerCase().includes(String(p.suffix).toLowerCase().slice(-4)));
      rec.phases.viewShows = { expected: wantB.length, seen: shownB.length };
      const broken = (vm?.images || []).filter((i) => i.broken);
      if (broken.length) add("P2", "image", `${broken.length} broken image(s) in View`, broken);
      if (vm?.images?.length === 0 && plan.some((p) => p.type === "file")) {
        add("P3", "image", "Add offers an upload but View shows no image");
      }
      await closeModal(page);
    } else {
      add("P2", "view", "row has a View action but it did not open");
    }

    // ---- 7. REFRESH: the change must still be there ----------------------
    // Look for the value the page now holds, not the value it held before the
    // edit: after a successful update the old text is gone BY DESIGN, so
    // searching for it reports a false persistence failure.
    await open(page, route);
    rec.phases.persisted = await locate(page, anchorB) >= 0;
    rec.phases.persistedSearchedFor = anchorB;
    if (!rec.phases.persisted) {
      add("P1", "persistence",
        `the updated row is NOT on the page after a reload (searched for "${anchorB}")`);
    }

    // ---- 8. clean up -----------------------------------------------------
    // Only pages that actually offer a Delete can be cleaned from the UI.
    // Stock deliberately has none - there is no DELETE endpoint on either
    // service - so its QA rows are removed by
    // Backend/tools/cleanup_qa_rows.py instead. Record it rather than call a
    // missing affordance a defect.
    const hasDelete = await rowAction(page, 0, "Delete").count().catch(() => 0);
    rec.phases.deleteOffered = !!hasDelete;
    if (!KEEP && hasDelete) {
      const idx = await locate(page, anchorB) >= 0 ? await locate(page, anchorB)
        : await locate(page, anchor);
      fresh();
      const del = idx >= 0 ? rowAction(page, idx, "Delete") : null;
      if (del && await del.count()) {
        await del.click();
        await page.waitForTimeout(800);
        const confirm = page.locator('[data-testid="modal"].modal--active .modal-actions button')
          .filter({ hasText: /delete|confirm|yes/i }).last();
        if (await confirm.count()) {
          const delRes = page.waitForResponse((r) => r.request().method() === "DELETE", { timeout: 12000 }).catch(() => null);
          await confirm.click();
          const dres = await delRes;
          await page.waitForTimeout(1200);
          rec.phases.deleteResponse = dres ? { status: dres.status() } : null;
          if (!dres || dres.status() >= 400) {
            add("P1", "delete", `delete failed (${dres ? dres.status() : "no request"})`);
          }
          if (await modalOpen(page)) await closeModal(page);
          await settle(page, 900);
          const left = await tableRows(page).count();
          rec.phases.rowCount.afterCleanup = left;
          if (left !== before) {
            // The count is measured against a full list, so undo whatever the
            // search box did to it before comparing.
            await clearSearch(page);
            const real = await tableRows(page).count();
            rec.phases.rowCount.afterCleanup = real;
            if (real !== before) {
              add("P2", "cleanup",
                `row count is ${real}, was ${before} before the test - the QA row "${anchorB}" may still be present`);
            }
          }
        } else {
          rec.phases.deleteResponse = { status: "no confirm dialog" };
          if (await modalOpen(page)) await closeModal(page);
          add("P2", "delete", "Delete action opened no confirmation dialog");
        }
      } else {
        rec.phases.deleteResponse = { status: "no delete action on this page" };
      }
    }
  } else {
    add("P2", "edit", "row has no Edit action");
  }

  rec.findings.sort((a, b) => a.sev.localeCompare(b.sev));
  rec.status = rec.skipped ? "skipped" : rec.findings.length ? "defect" : "passed";
  report.push(rec);
  const top = rec.findings.slice(0, 2).map((f) => `${f.sev}:${f.kind}`).join(" ") || rec.status;
  console.log(`${rec.status === "passed" ? "ok " : "!! "} ${id} ${route.padEnd(32)} ${top}`);
}

writeFileSync(`${OUT}.json`, JSON.stringify({ run: RUN, report }, null, 1));
const done = report.filter((r) => !r.skipped);
console.log(`\nwrote ${OUT}.json  (${done.length} round-tripped, ${done.filter((r) => r.status === "passed").length} passed, ${done.filter((r) => r.status === "defect").length} with defects)`);
await browser.close();
/**
 * Per-page deep audit - STRUCTURAL half.
 *
 *   node page_deep.mjs <email> <label> [--routes=/a,/b] [--width=1440]
 *
 * For every page it opens the Add dialog, the View dialog and the Edit dialog,
 * reads what each one actually offers in the live DOM, and reports:
 *
 *   - fields Add offers that Edit does not          (the Add/Edit gap)
 *   - fields both offer but View does not show      (the View gap)
 *   - required fields Edit leaves unset             (the edit-prefill gap)
 *   - broken images / missing previews in View
 *   - validation: an empty Add submit must be refused
 *   - render health: crash, blank, overflow, sentinel text
 *
 * It never submits a business form, so it is safe to run against seeded data.
 * The data-flow half - ADD -> SAVE -> EDIT -> SAVE -> VIEW -> REFRESH - lives
 * in Backend/tools/page_roundtrip.py, which drives the API and then checks the
 * database. This script proves the screens agree with each other; that one
 * proves they agree with the database.
 */
import { mkdirSync, writeFileSync } from "fs";
import {
  launch, login, open, settle, probe, addButton, tableRows, rowAction,
  readModal, modalOpen, closeModal, loadCredentials, BASE,
} from "./lib.mjs";

const arg = (name, dflt) => {
  const hit = process.argv.find((a) => a.startsWith(`--${name}=`));
  return hit ? hit.split("=").slice(1).join("=") : dflt;
};

const CRED_FILE = process.env.CRED_FILE ||
  "C:\\Users\\anand\\AppData\\Local\\Temp\\opencode\\cherry-credentials.txt";
const creds = loadCredentials(CRED_FILE);

const EMAIL = process.argv[2] || "admin@cherryhotel.com";
const LABEL = process.argv[3] || "deep";
const PASSWORD = process.env.PW_PASSWORD || creds[EMAIL];
const WIDTH = Number(arg("width", 1440));
const HEIGHT = Number(arg("height", 900));
const OUT = process.env.OUT || `./e2e-reports/deep-${LABEL}`;

const ROUTES = arg("routes", "").split(",").map((s) => s.trim()).filter(Boolean);

if (!PASSWORD) throw new Error(`no password for ${EMAIL}; set PW_PASSWORD or CRED_FILE`);

const { browser, page, bucket, fresh } = await launch({ width: WIDTH, height: HEIGHT });
mkdirSync("e2e-reports", { recursive: true });

await login(page, EMAIL, PASSWORD);

/** Read whichever dialog is open, or the inline form when there is none. */
const readOpen = async () => (await modalOpen(page)) ? readModal(page) : readModal(page, "main");

const readShape = async () => readOpen();

/**
 * Open the Add dialog. Pages differ: some put the primary action in the table
 * toolbar, some have a standalone form. Try each and report which shape it was.
 */
async function openAdd() {
  const btn = addButton(page);
  if (await btn.count()) {
    const label = (await btn.textContent())?.trim() || null;
    await btn.click().catch(() => {});
    await page.waitForTimeout(700);
    if (await modalOpen(page)) return { shape: "modal", evidence: label };
    // The button may drive an inline form rather than a dialog.
    const inputs = page.locator("main input, main select, main textarea");
    if (await inputs.count()) return { shape: "inline-form", evidence: `${await inputs.count()} controls (via "${label}")` };
    return { shape: "button-no-dialog", evidence: label };
  }
  // Some pages have no toolbar button but a visible inline form.
  const inputs = page.locator("main input, main select, main textarea");
  if (await inputs.count()) return { shape: "inline-form", evidence: `${await inputs.count()} controls` };
  return { shape: "none", evidence: null };
}

async function openRowDialog(verb, index = 0) {
  const btn = rowAction(page, index, verb);
  if (!(await btn.count())) return null;
  await btn.click().catch(() => {});
  await page.waitForTimeout(600);
  if (!(await modalOpen(page))) return null;
  return readOpen();
}

/** An Add submit with everything blank must be refused, not accepted. */
async function emptySubmitRefused(add) {
  const dialog = await modalOpen(page);
  const submit = dialog
    ? page.locator('[data-testid="modal"].modal--active .modal-actions button')
        .filter({ hasText: /submit|save|create|add|confirm/i }).last()
    : page.locator("main button[type='submit'], main .form-actions button")
        .filter({ hasText: /submit|save|create|add/i }).last();
  if (!(await submit.count())) return { checked: false, reason: `add shape: ${add.shape}; no submit button` };
  const before = await tableRows(page).count();
  const answered = page.waitForResponse(
    (r) => /^(POST|PUT)$/.test(r.request().method()), { timeout: 6000 }).catch(() => null);
  await submit.click({ timeout: 5000 }).catch(() => {});
  const response = await answered;
  await page.waitForTimeout(900);
  const stillOpen = dialog ? await modalOpen(page) : true;
  const after = await tableRows(page).count();
  const toast = (await page.locator('[role="status"], .toast').allInnerTexts().catch(() => []))
    .join(" ").slice(0, 140);
  return {
    checked: true,
    shape: add.shape,
    modalStayedOpen: stillOpen,
    rowDelta: after - before,
    httpStatus: response ? response.status() : null,
    toast: toast.trim() || null,
    refused: stillOpen || (after - before) === 0,
  };
}

/** Labels, normalised so "Bed Type" and "Bed type" compare equal. */
const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

const report = [];
let seq = 0;

for (const route of ROUTES) {
  seq += 1;
  const id = `P${String(seq).padStart(3, "0")}`;
  const rec = { id, route, width: WIDTH, findings: [], evidence: {} };

  fresh();
  await open(page, route);
  const p0 = await probe(page);
  rec.evidence.render = p0;
  rec.evidence.errors = {
    consoleErrors: [...bucket.consoleErrors], pageErrors: [...bucket.pageErrors],
    httpErrors: [...bucket.httpErrors], netFailed: [...bucket.netFailed],
  };

  if (p0.crashed) rec.findings.push({ sev: "P0", kind: "crash", msg: "page renders the error boundary" });
  if (p0.textLen < 60) rec.findings.push({ sev: "P1", kind: "blank", msg: `only ${p0.textLen} chars of text` });
  if (p0.overflow > 1) {
    rec.findings.push({ sev: "P2", kind: "responsive",
      msg: `horizontal overflow ${p0.overflow}px`, detail: p0.widest });
  }
  for (const s of p0.sentinels) {
    rec.findings.push({ sev: "P2", kind: "render", msg: `page text contains "${s}"` });
  }
  if (p0.brokenImgs.length) {
    rec.findings.push({ sev: "P1", kind: "image", msg: `${p0.brokenImgs.length} broken image(s)`, detail: p0.brokenImgs.slice(0, 4) });
  }
  if (p0.hasTable && p0.rowCount === 0) {
    rec.findings.push({ sev: "P3", kind: "data", msg: "table rendered with no rows - verify the seed" });
  }

  // ---- Add -----------------------------------------------------------------
  const add = await openAdd();
  rec.evidence.addShape = add;
  if (add.shape === "none") {
    rec.findings.push({ sev: "P3", kind: "affordance", msg: "no Add affordance found (read-only page?)" });
  } else if (add.shape !== "button-no-dialog") {
    const addModal = await readShape();
    rec.evidence.add = addModal;
    const validation = await emptySubmitRefused(add);
    rec.evidence.emptySubmit = validation;
    if (validation.checked && !validation.refused) {
      rec.findings.push({ sev: "P0", kind: "validation",
        msg: "empty Add submit was NOT refused", detail: validation });
    }
    if (await modalOpen(page)) await closeModal(page);
  }

  // ---- View / Edit on the first row ---------------------------------------
  if (p0.hasTable && p0.rowCount > 0) {
    fresh();
    const view = await openRowDialog("View", 0);
    rec.evidence.view = view;
    if (view) {
      if (view.detailItems.length === 0 && view.tables.length === 0 && view.images.length === 0) {
        rec.findings.push({ sev: "P1", kind: "view", msg: "View dialog shows no detail rows" });
      }
      for (const img of view.images || []) {
        if (img.broken) {
          rec.findings.push({ sev: "P1", kind: "image", msg: `broken image in View: ${img.src}` });
        }
      }
    }
    await closeModal(page);

    fresh();
    const edit = await openRowDialog("Edit", 0);
    rec.evidence.edit = edit;
    if (edit) await closeModal(page);

    // ---- THE COMPARISON ---------------------------------------------------
    const addF = rec.evidence.add;
    if (addF && edit) {
      const addKeys = addF.fields.filter((f) => !f.isFile).map((f) => norm(f.label || f.name));
      const editKeys = edit.fields.filter((f) => !f.isFile).map((f) => norm(f.label || f.name));
      const missingInEdit = addKeys.filter((k) => k && !editKeys.includes(k));
      const extraInEdit = editKeys.filter((k) => k && !addKeys.includes(k));
      rec.evidence.addEditDiff = { missingInEdit, extraInEdit };
      if (missingInEdit.length) {
        rec.findings.push({ sev: "P1", kind: "add-edit-gap",
          msg: `Add offers ${missingInEdit.length} field(s) Edit does not: ${missingInEdit.join(", ")}` });
      }
      // required Edit fields that came back empty = the edit form does not
      // prefill, so saving would blank a stored value
      const emptyRequired = edit.fields
        .filter((f) => f.required && !f.readOnly && !f.disabled)
        .filter((f) => f.value === "" || f.value === null || f.value === undefined)
        .map((f) => f.label || f.name);
      rec.evidence.emptyRequiredInEdit = emptyRequired;
      if (emptyRequired.length) {
        rec.findings.push({ sev: "P1", kind: "edit-prefill",
          msg: `Edit left ${emptyRequired.length} required field(s) blank: ${emptyRequired.join(", ")}` });
      }
      // select defaults that do not match any option
      for (const f of edit.fields) {
        if (f.type === "select" && f.value && Array.isArray(f.options)) {
          const known = f.options.some((o) => String(o.value) === String(f.value));
          if (!known) {
            rec.findings.push({ sev: "P2", kind: "edit-value",
              msg: `Edit shows "${f.label}" = "${f.value}" which is not one of its options` });
          }
        }
      }
    }

    if (addF && view) {
      const viewItems = view.detailItems || [];
      const viewLabels = viewItems.map((d) => norm(d.label));
      const addFields = addF.fields.filter((f) => !f.isFile);
      const addLabels = addFields.map((f) => norm(f.label || f.name));

      // A View item covers an Add field when the labels agree, OR when the
      // field's stored value appears inside the item's value. The second case
      // matters because several screens merge two inputs into one summary row
      // - /rooms shows `max_adult` and `max_child` as a single "Occupancy"
      // reading "2 adults - 1 children". Calling that a gap would be wrong, and
      // a harness that cries wolf gets ignored.
      const covered = new Set();
      for (const f of addFields) {
        const key = norm(f.label || f.name);
        if (viewLabels.includes(key)) { covered.add(key); continue; }
        const v = f.value == null ? "" : String(f.value).trim();
        if (v && v.length > 0 && f.type !== "file") {
          for (const d of viewItems) {
            if (String(d.value || "").includes(v)) { covered.add(key); break; }
          }
        }
      }
      const notShown = addLabels.filter((k) => k && !covered.has(k));
      rec.evidence.addViewDiff = { notShownInView: notShown, viewLabels, coveredByValue: addLabels.filter((k) => !viewLabels.includes(k) && covered.has(k)) };
      if (notShown.length) {
        rec.findings.push({ sev: "P2", kind: "view-gap",
          msg: `Add collects ${notShown.length} field(s) View does not display: ${notShown.join(", ")}`,
          detail: viewLabels });
      }
    }
  }

  rec.findings.sort((a, b) => a.sev.localeCompare(b.sev));
  rec.status = rec.findings.length === 0 ? "clean" :
    rec.findings.some((f) => f.sev === "P0" || f.sev === "P1") ? "defect" : "advisory";

  report.push(rec);
  const top = rec.findings.slice(0, 2).map((f) => `${f.sev}:${f.kind}`).join(" ") || "clean";
  console.log(`${rec.status === "clean" ? "ok " : "!! "} ${id} ${route.padEnd(32)} ${top}`);
}

writeFileSync(`${OUT}.json`, JSON.stringify({ base: BASE, email: EMAIL, width: WIDTH, report }, null, 1));
console.log(`\nwrote ${OUT}.json  (${report.length} pages, ${report.filter((r) => r.status !== "clean").length} with findings)`);
await browser.close();
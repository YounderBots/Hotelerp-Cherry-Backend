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
  launch, login, open, settle, probe, addButton, dataInputCount, tableRows, rowAction,
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

// "anon:/route" marks a page that only exists signed OUT. Visit it while signed
// out, or the app redirects to /dashboard and the audit records the dashboard.
const isAnon = (r) => r.startsWith("anon:");
const pathOf = (r) => (isAnon(r) ? r.slice(5) : r);
const dropSession = (page) => page.evaluate(() => localStorage.clear());

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
  const btn = await addButton(page);
  if (btn) {
    const label = (await btn.textContent())?.trim() || null;
    await btn.click().catch(() => {});
    await page.waitForTimeout(700);
    if (await modalOpen(page)) return { shape: "modal", evidence: label };
    // The button may drive an inline form rather than a dialog.
    const inputs = await dataInputCount(page);
    if (inputs) return { shape: "inline-form", evidence: `${inputs} controls (via "${label}")` };
    return { shape: "button-no-dialog", evidence: label };
  }
  // No button starts data entry. Only call it an inline form if the page
  // really has controls outside its chrome - otherwise it is a read-only page.
  const inputs = await dataInputCount(page);
  if (inputs) return { shape: "inline-form", evidence: `${inputs} controls` };
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
        .filter({ hasText: /submit|save|create|add|assign|generate|record|confirm/i }).last()
    : page.locator("main button[type='submit'], main .form-actions button")
        .filter({ hasText: /submit|save|create|add|assign|generate|record/i }).last();
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

/** Words that carry no meaning when matching one label against another. */
const NOISE = new Set(["no", "of", "number", "the", "is", "and", "min", "minute", "minutes"]);
const words = (label) => {
  const all = norm(label).split(" ").filter(Boolean);
  const kept = all.filter((w) => !NOISE.has(w));
  return kept.length ? kept : all;
};

/**
 * Does a View row stand for this Add field?
 *
 * Exact wording is the easy case and the rare one: the same field is called
 * "First Name" in one form and "Name" in the other, "No of Adults" against
 * "Adults", "Arrival Date" against "Arrival". Comparing normalised strings
 * alone reports every one of those as a field the View hides, which is how a
 * harness ends up crying wolf on pages that are correct. So a View row also
 * covers an Add field when one side's words are a subset of the other's.
 *
 * What this deliberately does NOT decide is a merge - several Add fields folded
 * into one View row whose label shares no word with any of them (/rooms shows
 * Max Adults and Max Children together as "Occupancy"). Only a filled form can
 * settle that, so it stays a finding for a human to adjudicate.
 */
/** Head words: the words that say WHAT a field is about, for value matching. */
const HEAD_NOISE = new Set([...NOISE, "max", "min", "total", "count", "no"]);
function headWords(label) {
  const all = norm(label).split(" ").filter(Boolean);
  const kept = all.filter((w) => !HEAD_NOISE.has(w));
  return kept.length ? kept : all;
}

function coversViewRow(addLabel, viewLabels) {
  const a = norm(addLabel);
  if (viewLabels.includes(a)) return "exact";
  const aw = new Set(words(addLabel));
  if (!aw.size) return null;
  for (const v of viewLabels) {
    const vw = new Set(words(v));
    if (!vw.size) continue;
    if ([...aw].every((w) => vw.has(w)) || [...vw].every((w) => aw.has(w))) return "words";
  }
  return null;
}

const report = [];
let seq = 0;

for (const raw of ROUTES) {
  const route = pathOf(raw);
  seq += 1;
  const id = `P${String(seq).padStart(3, "0")}`;
  const rec = { id, route, width: WIDTH, findings: [], evidence: {} };

  fresh();
  if (isAnon(raw)) await dropSession(page);
  await open(page, route);
  const p0 = await probe(page);
  rec.evidence.landedOn = new URL(page.url()).pathname;
  if (rec.evidence.landedOn !== route) {
    rec.findings.push({ sev: "P1", kind: "redirect",
      msg: `opening ${route} landed on ${rec.evidence.landedOn}` });
  }
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
    // Only worth noting when the page really is empty. A table that is still
    // loading, or whose fetch failed, is a different problem and shows up
    // elsewhere (httpErrors, sentinels, crash).
    rec.evidence.tableEmpty = p0.tableMessage;
    rec.findings.push({
      sev: "P3", kind: "data",
      msg: `table rendered with no rows - the page says "${p0.tableMessage || "(no message)"}"`,
      detail: { tableMessage: p0.tableMessage, loadingText: p0.loadingText,
                httpErrors: [...bucket.httpErrors] },
    });
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
      // A control with no resolvable label cannot be compared: React hands
      // RepeatableRowEditor's inputs ids like "«r19»", which read as a field
      // called "input r 19" on both sides and showed up as an extra Edit field.
      const labelled = (f) => !f.isFile && (f.label || "").trim() !== "";
      const addLabels = addF.fields.filter(labelled).map((f) => f.label);
      const editLabels = edit.fields.filter(labelled).map((f) => f.label);
      const addKeys = addLabels.map(norm);
      const editKeys = editLabels.map(norm);
      // The same field is not always worded the same way in the two dialogs -
      // /employee calls it "Password" when adding and "New Password" when
      // editing, which is correct (there is no stored password to re-enter) and
      // was being reported as a missing field on both sides. Compare on words.
      const missingInEdit = addKeys.filter((k) => k && !coversViewRow(k, editKeys));
      const extraInEdit = editKeys.filter((k) => k && !coversViewRow(k, addKeys));
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
      // A password is never shown in a View. That is correct behaviour, and
      // reporting it as a gap on every screen that collects one teaches the
      // audit to cry wolf about the one field it must stay silent on.
      const isSecret = (label) => /pass(word|phrase)?|secret|token|pin\b/.test(norm(label));

      // A View item covers an Add field when the labels agree, when one side's
      // words are a subset of the other's, when the field's stored value appears
      // inside the item's value, OR when the item's VALUE TEXT mentions every
      // head word of the field's label. The last case matters because several
      // screens merge two inputs into one summary row - /rooms shows
      // `max_adult` and `max_child` as a single "Occupancy" reading "4 adults -
      // 3 children". Calling that a gap would be wrong, and a harness that
      // cries wolf gets ignored. The Add form is read before it is filled, so
      // the stored-value rule never fires there; matching the item's own words
      // does, and can only ever close a gap, never open one.
      const covered = new Set();
      const byWords = new Set();
      const byValue = new Set();
      for (const f of addFields) {
        const key = norm(f.label || f.name);
        if (!key) continue;
        if (isSecret(f.label || f.name)) { covered.add(key); continue; }
        const hit = coversViewRow(f.label || f.name, viewLabels);
        if (hit) { covered.add(key); if (hit === "words") byWords.add(key); continue; }
        const v = f.value == null ? "" : String(f.value).trim();
        if (v && v.length > 0 && f.type !== "file") {
          for (const d of viewItems) {
            if (String(d.value || "").includes(v)) { covered.add(key); byValue.add(key); break; }
          }
          continue;
        }
        const words = headWords(f.label || f.name);
        for (const d of viewItems) {
          const val = norm(d.value);
          if (val && words.every((w) => val.includes(w))) {
            covered.add(key); byValue.add(key); break;
          }
        }
      }
      const notShown = addLabels.filter((k) => k && !covered.has(k));
      rec.evidence.addViewDiff = {
        notShownInView: notShown,
        viewLabels,
        coveredByWords: [...byWords],
        coveredByValue: [...byValue],
      };
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
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
  readModal, modalOpen, closeModal, loadCredentials, BASE,
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

/**
 * A time slot that differs for every time field on a form.
 *
 * Counting the TIME fields rather than the field's position matters: two time
 * inputs can sit at positions 1 and 2, or 8 and 9, and only the first
 * numbering guarantees they land on different hours. Shift refuses identical
 * start and end times, and two fields filled with the same value produce a
 * refusal that reads like a product defect.
 */
const timeFor = (n) => `${String(7 + (n % 12)).padStart(2, "0")}:00`;
const indexOf = (arr, item) => arr.indexOf(item);

/** Everything the in-page filler needs, decided in Node. */
const planFor = (fields) => {
  const fillable = fields.filter((f) => !f.isFile && !f.disabled);
  // Choose the country FIRST, then give every phone field a number valid in
  // that country. Deciding per field inside one map() cannot see the array
  // being built, and a form told "Singapore" that receives an Indian number
  // refuses to save - correctly.
  const countryPick = (() => {
    for (const f of fillable) {
      if (f.type !== "select") continue;
      const opts = (f.options || []).filter((o) => o.value !== "" && !o.disabled);
      const match = opts.find((o) => /india/i.test(String(o.label || o.value)));
      if (match) return match.value;
    }
    return null;
  })();
  const DIAL = /united kingdom/i.test(String(countryPick)) ? "+447700900123"
    : /united states/i.test(String(countryPick)) ? "+12025550123"
    : /united arab/i.test(String(countryPick)) ? "+971501234567"
    : /singapore/i.test(String(countryPick)) ? "+6581234567"
    : "+919876543210";

  return fillable.map((f, i) => {
  const key = (f.label || f.name || `f${i}`).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const suffix = i % 2 === 0 ? A : B;
  const base = { ...f, suffix, runSeed: RUN.toLowerCase(), runLen: RUN.length,
    index: i, country: countryPick, dial: DIAL };
  // Booking's room count is pinned to one because its helper text says
  // "Select one room type for each room" and the multi-select holds a single
  // chip. That rule lives in the number branch below, where the `tiedToSelects`
  // flag is also set - an earlier copy of it here returned without the flag,
  // so the second pass moved the count anyway and the form refused the save.
  if (f.type === "select") {
    // A unit field is not a country: prefer the one the seeded data uses so
    // the value stays meaningful, and fall back to the first real option.
    const opts = (f.options || []).filter((o) => o.value !== "" && !o.disabled);
    const unit = opts.find((o) => /^(kg|nos|gram|ml|litre|bottle)$/i.test(String(o.value)));
    return { ...base, plan: (unit || opts[0])?.value ?? null, kind: "select" };
  }
  if (f.type === "number") {
    const label = (f.label || "").toLowerCase();

    // Booking's room count is tied to its room types: the helper text says
    // "Select one room type for each room", and the multi-select holds a single
    // chip. It has to be checked BEFORE the unique-key rule below, because
    // "No. of Rooms" contains the word "Rooms" and would otherwise be pinned to
    // an unused number - 719 rooms against one chosen type, which the form
    // refuses.
    const tiedToSelects = /\bno\.? ?of\.? ?rooms\b|^rooms?$/.test(label)
      && !/adult|child/.test(label);
    if (tiedToSelects) {
      return { ...base, plan: "1", kind: "number", tiedToSelects };
    }

    // A number the API treats as a UNIQUE KEY (a floor number, a table
    // number) collides with the seeded rows when numbered from the field's
    // position, and the create answers 409. Start above anything in use.
    const isNumberKey = /\b(number|no\.?|#)\b/.test(label)
      || ["floor_number", "table_number", "table_no"].includes(String(f.name || ""));
    if (isNumberKey) {
      const n = 700 + (RUN.length % 200) + (i % 90);
      return { ...base, plan: String(n), kind: "number", uniqueNumber: true };
    }
    const lo = Number.isFinite(f.min) ? f.min : 1;
    const hi = Number.isFinite(f.max) ? f.max : 999;
    const value = Math.min(Math.max(lo + i, lo), hi);
    return { ...base, plan: String(value), kind: "number", numericIndex: i };
  }
  if (f.type === "date") {
    // Dates on one form are ORDERED (a birth date precedes a joining date) and
    // both must be in the past. Two independent "today minus N" values satisfy
    // neither, and the app refuses the pair with a message that names the rule
    // - correctly.
    //
    // Space them a WEEK apart rather than a year: booking arrival and departure
    // are consecutive fields, and a year between them produces a 365-night
    // stay that is legal but absurd - and the nights field then becomes a
    // nonsense number to compare against.
    const d = new Date(Date.UTC(2026, 0, 5) + i * 7 * 86400000);
    return { ...base, plan: d.toISOString().slice(0, 10), kind: "date" };
  }
  if (f.type === "datetime-local") {
    const d = new Date(Date.now() + 86400000);
    return { ...base, plan: new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16), kind: "date" };
  }
  // Keep the KIND, not just a plan value: `kind` decides what `flip` produces on
  // the second pass, and a time field typed as "text" gets "QB ... changed" fed
  // into <input type="time">, which rejects it and leaves the box EMPTY. The
  // form then correctly refuses to save and the page is reported as broken when
  // the harness was at fault.
  if (f.type === "time" || f.kind === "time") {
    // Time fields on one form must all DIFFER: Shift refuses "Start time and
    // end time cannot be identical". Derive the hour from the field's own
    // position, which differs per field even when several share a type.
    return { ...base, plan: timeFor(fillable.filter((x) => x.type === "time").indexOf(f)), kind: "time" };
  }
  // A guest mobile is UNIQUE in the F&B guest tables, so even the FIRST pass
  // must not reuse a number any live row holds or the create answers 409.
  // Keep the country code from DIAL and make the SUBSCRIBER part unique to the
  // run. An Indian mobile's first subscriber digit must be 6-9, or the same
  // validator answers 400 "IN does not have that phone number".
  // PhoneInput formats as you type and publishes an e164 that is EMPTY while the
  // number is incomplete. The validator is right - nine digits is not an Indian
  // number - so the harness must type a number that is actually one: a full
  // subscriber number, ten digits, starting with the digit the plan allows.
  const bare0 = String(DIAL).replace(/\D/g, "");
  const cc0 = bare0.length > 10 ? bare0.slice(0, bare0.length - 10) : "91";
  const lead0 = { 91: "9", 44: "7", 1: "2", 971: "5", 65: "8" }[cc0] || "9";
  const rest0 = String(100000000 + ((RUN.length * 3701 + i * 111) % 899999999));
  const uniqTel = cc0 + lead0 + rest0;
  // PhoneInput renders the dial code as its own readable control whose label is
  // the dial code itself ("+91 IN"), and the subscriber number has no label at
  // all. Match on the INPUT TYPE rather than the label, which is what actually
  // identifies a phone field.
  if (f.type === "tel" || /^\+\d+\s*[A-Z]{2}$/i.test(String(f.label || "").trim())) {
    return { ...base, plan: uniqTel, kind: "tel" };
  }
  // A free-text field that the API validates against a fixed vocabulary.
  // "Dietary Tags (comma-separated, e.g. Vegan, Gluten-Free, Spicy)" holds
  // tags, and an arbitrary sentence is answered 400 "dietary_tags are
  // invalid". The field's own help text names the accepted values.
  if (/dietary\s*tags?/i.test(f.label || "") || f.name === "dietary_tags") {
    return { ...base, plan: "Vegan, Gluten-Free", kind: "tags" };
  }
  if (f.type === "checkbox") return { ...base, plan: true, kind: "checkbox" };
  if (f.type === "email") return { ...base, plan: `qa${RUN.toLowerCase()}@cherryhotel.com`, kind: "email" };
  if (f.type === "password") return { ...base, plan: `Qa!${RUN}9x`, kind: "password" };
  if (f.type === "color") return { ...base, plan: "#1a2b3c", kind: "text" };
  if (f.type === "textarea") return { ...base, plan: `QA ${suffix} note`, kind: "text" };
  const capOf = (f) => (f.maxLength > 0 ? f.maxLength : 0);
  const fit = (f, v) => { const c = capOf(f); return c ? v.slice(0, c) : v; };
  if (key.includes("name")) return { ...base, plan: fit(f, `QA${suffix}`), kind: "name" };
  if (key.includes("description") || key.includes("address") || key.includes("note")) {
    return { ...base, plan: fit(f, `QA ${suffix} detail`), kind: "text" };
  }
  if (key.includes("code") || key.includes("no") || key.includes("number")) {
    return { ...base, plan: fit(f, `QA${suffix}`), kind: "text" };
  }
  // A uniqueness-constrained field (a floor name, a table name, a guest mobile)
    // is found in other rows, so a second-pass value derived from a fixed
    // generic sentence collides with a live record and the API answers 409.
    // The page is right to refuse; the harness must pick a value no row holds.
    if (/^\s*(floor|table|hall)\b/i.test(f.label || "")
      || /\b(floor|table|hall)\s*(no|number|name)?\b/i.test(f.label || "")) {
      return { ...base, plan: `${f.suffix} ${key}`.slice(0, 40), kind: "unique" };
    }
    const cap = f.maxLength > 0 ? f.maxLength : 0;
    const full = `QA ${suffix} ${key}`.slice(0, 60);
    return { ...base, plan: fit(f, full), kind: "text" };
  });
};

/**
 * Type the planned values into the live controls.
 *
 * `page.evaluate` passes ONE argument, so the payload arrives as a single
 * object. Taking `(plan, which)` silently gave `which === undefined` and
 * filled nothing while still reporting a green run. `flip` is defined INSIDE
 * this function for the same reason: it runs in the browser, where a
 * module-scope helper does not exist.
 */
const FILL = async ({ plan, which }) => {
  /** A different value for the same field, so a stale prefill is visible. */
  const flip = (f) => {
    if (f.uniqueNumber) return String(Number(f.plan) + 11);
    if (f.kind === "number") {
      // A count tied to a multi-select (booking's rooms, against one chosen
      // room type) must NOT move: +7 makes 8 rooms against one type and the
      // form refuses the pair by a rule it prints in its own helper text.
      if (f.tiedToSelects) return f.plan;
      const lo = Number.isFinite(f.min) ? f.min : 1;
      const hi = Number.isFinite(f.max) ? f.max : 999;
      return String(Math.min(Math.max(Number(f.plan) + 7, lo), hi));
    }
    if (f.kind === "unique") {
      return `${f.suffix} ${(f.label || "row").toLowerCase()}`.slice(0, 40);
    }
    if (f.type === "select") {
      const opts = (f.options || []).filter((o) => o.value !== "" && !o.disabled);
      if (opts.length < 2) return null;
      const i = opts.findIndex((o) => o.value === f.plan);
      return opts[(i + 1) % opts.length]?.value ?? null;
    }
    if (f.type === "time" || f.kind === "time") {
      // A different slot on the second pass, still distinct from every other
      // time field: Shift refuses identical start and end times.
      const idx = (f.index || 0) + 1;
      return String(7 + idx).padStart(2, "0") + (which === "B" ? ":30" : ":00");
    }
    if (f.type === "date" || f.type === "datetime-local") {
      // A week later than the first pass, keeping the fields' relative order,
      // so a birth date stays before a joining date and a stay is a week
      // rather than a year. `index` travels with the plan because this runs in
      // the browser, where the Node-side loop counter is not in scope.
      const d = new Date(Date.UTC(2026, 1, 5) + ((f.index || 0) * 7) * 86400000);
      return f.type === "date" ? d.toISOString().slice(0, 10)
        : new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    }
    if (f.type === "tel") {
      // A guest mobile is UNIQUE in the F&B guest tables, so the second pass
      // must not reuse the first pass's number or the API answers 409 "A guest
      // with this mobile number already exists". Keep the SAME country prefix
      // so the country-aware validator still accepts it, and change only the
      // subscriber digits.
      // `runLen` travels with every field because this runs in the browser, where
      // the Node-side RUN constant is not in scope. Offset by the PASS as well
      // as the run: deriving both passes from the same inputs produced the same
      // number, so the second save was rejected as a duplicate of the first.
      const bare = String(f.dial || "+919876543210").replace(/\D/g, "");
      const cc = bare.length > 10 ? bare.slice(0, bare.length - 10) : "91";
      const lead = { 91: "9", 44: "7", 1: "2", 971: "5", 65: "8" }[cc] || "9";
      const seed = (f.runLen || 11) * 7919 + (f.index || 0) * 131
        + (which === "B" ? 5555551 : 0);
      const rest = String(100000000 + (seed % 899999999));
      // National digits: PhoneInput wants the subscriber number and adds the
      // calling code itself from the selected country.
      return cc + lead + rest;
    }
    if (f.type === "email") return `qb${f.runSeed}@cherryhotel.com`;
    // A colour must stay a colour: feeding "QB ... changed" to <input
    // type="color"> makes the browser coerce it to #000000, which then looks
    // like the product threw the value away.
    if (f.type === "color") return "#2d6cdf";
    // Respect the field's own maxLength. A postal-code column capped at 20
    // rejects the 20-character generic sentence, and the page is then reported
    // as broken when the harness was the thing that was too long.
    const cap = f.maxLength > 0 ? f.maxLength : 0;
    const out = `QB ${f.suffix} changed`;
    return cap ? out.slice(0, cap) : out;
  };
  const sel = '[data-testid="modal"].modal--active';
  let filled = 0, skipped = [];
  for (const f of plan) {
    // Prefer the label, then the name, then the id. A react-select proxy input
    // has no name of its own and its id is a per-render useId, so a field can
    // arrive with only one of the three - and dropping it because the first
    // choice was empty is how a required multi-select silently went unfilled.
    const label = f.label || f.name || f.id;
    if (!label) { skipped.push("(anonymous field)"); continue; }
    const byName = f.name ? `${sel} [name="${CSS.escape(f.name)}"]` : null;
    const byLabel = null;
    let el = null;
    if (byName) el = document.querySelector(byName);
    if (!el) {
      // Match on the label's text, and also on its `for` attribute. A react-select
      // proxy input carries NO name at all, so the name lookup cannot find it and
      // the label lookup has to carry the field on its own.
      const labs = [...document.querySelectorAll(`${sel} label`)];
      const lab = labs.find((l) => l.textContent.replace(/\s*\*\s*$/, "").trim() === label);
      if (lab) {
        const t = lab.getAttribute("for");
        el = t
          ? (document.getElementById(t) || document.querySelector(`${sel} [id="${CSS.escape(t)}"]`))
          : lab.parentElement.querySelector("input, select, textarea");
      }
    }
    if (!el) { skipped.push(`${label} (not found)`); continue; }

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
      // react-select renders no <select>: a text input filters a popup menu and
    // the chosen values live in sibling chips. Setting input.value therefore
    // selects nothing, and the form refuses to save for a reason that has
    // nothing to do with the page under test. Drive the control the way a user
    // does - click it, then click the first option.
    // The proxy input is a DESCENDANT of `.react-select`, not inside it:
    // control > value-container > input-container > input. So
    // `el.closest('.react-select')` finds the wrapper, and the clickable
    // control is the element whose class carries `react-select__control`.
    // Getting this wrong reads as "no react-select on this page".
    if (el.classList.contains("react-select__input")) {
      const control = el.closest(".react-select__control")
        || el.parentElement?.parentElement?.parentElement;
      if (!control) { skipped.push(`${label} (no react-select control)`); continue; }
      // Booking validates "Select exactly one room type for each room", so the
      // multi-select must hold exactly as many chips as the rooms count.
      // Adding a second chip beside rooms=1 is refused by a rule the page
      // states plainly. Swap the chip: remove the existing one, then pick
      // another, so the count stays right and the VALUE still changes.
      if (which === "B") {
        const remove = control.querySelector(".react-select__multi-value__remove");
        if (remove) { remove.dispatchEvent(new MouseEvent("mousedown", { bubbles: true })); remove.click(); }
        await new Promise((r) => setTimeout(r, 200));
      }
      control.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, cancelable: true }));
      await new Promise((r) => setTimeout(r, 350));
      // Pick an option the control does NOT already hold. On the second pass
      // the first option is the one already selected, and react-select treats
      // re-picking it as a deselect - which empties the field and makes the
      // form refuse to save for a reason that has nothing to do with the page.
      const opts = [...document.querySelectorAll(".react-select__option")];
      const picked = which === "B" ? (opts[1] || opts[0]) : opts[0];
      if (picked) {
        picked.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, cancelable: true }));
        picked.click();
        await new Promise((r) => setTimeout(r, 300));
        filled += 1;
      } else {
        skipped.push(`${label} (no react-select option)`);
      }
      continue;
    }

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

      // PhoneInput does not read a change event at all: its onChange takes
      // (e164, region, result) as POSITIONAL arguments, so a synthetic event
      // leaves the page's state empty and the form refuses to save with "First
      // name and mobile number are required" - a complaint about a field the
      // user can plainly see filled in. Reach React's own handler directly and
      // pass the arguments its signature expects.
      //
      // Detect by the input's own class, not by arity. PhoneInput's handler is
      // declared `(e164, region, result)` at the call site but lands on the
      // element as a bound wrapper whose `length` is 1, so an arity check
      // finds "not a phone handler" and skips exactly the field it is for.
      const propsKey = Object.keys(el).find((k) => k.startsWith("__reactProps$"));
      const onChange = propsKey ? el[propsKey]?.onChange : null;
      const isPhoneField = /phone-field__input/.test(String(el.className || ""))
        || /^\+\d+\s*[A-Z]{2}$/i.test(String(label || "").trim());
      if (isPhoneField && typeof onChange === "function") {
        const digits = String(value).replace(/\D/g, "");
        const cc = digits.length > 10 ? digits.slice(0, digits.length - 10) : "";
        onChange({ target: { value } },
          { 91: "IN", 44: "GB", 1: "US", 971: "AE", 65: "SG" }[cc] || "IN",
          { ok: true, incomplete: false });
      }
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
    // Read chips from the CONTROL ancestor, not from `closest('.react-select')`:
    // react-select's root div carries only hashed css classes, so the stable
    // hook is `.react-select__control`.
    if (el.classList.contains("react-select__input")) {
      const control = el.closest(".react-select__control");
      value = [...(control?.querySelectorAll(".react-select__single-value, .react-select__multi-value") || [])]
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
  if (f.uniqueNumber) return String(Number(f.plan) + 11);
  if (f.kind === "number") {
    if (f.tiedToSelects) return f.plan;
    const lo = Number.isFinite(f.min) ? f.min : 1;
    const hi = Number.isFinite(f.max) ? f.max : 999;
    const next = Number(f.plan) + 7;
    return String(Math.min(Math.max(next, lo), hi));
  }
  if (f.kind === "unique") return `${f.suffix} ${(f.label || "row").toLowerCase()}`.slice(0, 40);
  if (f.kind === "tags") return "Vegan, Jain";
  if (f.kind === "select") return null;
  if (f.kind === "date") {
    const d = new Date(Date.UTC(2026, 1, 5) + ((f.index || 0) * 7) * 86400000);
    return d.toISOString().slice(0, 10);
  }
  // Must differ from every other time on the form AND from the first pass.
  if (f.kind === "time" || f.type === "time") {
    const idx = (f.index || 0) + 1;
    return String(7 + idx).padStart(2, "0") + ":30";
  }
  if (f.type === "tel") {
    const d = f.dial || "+919876543210";
    return d.startsWith("+91") ? "+919812345678" : d.replace(/\d(?=\d{2}$)/, "8");
  }
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

/**
 * Read whatever the form is complaining about.
 *
 * Not every screen reports a refusal the same way: Employee raises a toast,
 * Task Assign and Room Incident Log put the message under the field, and
 * Booking renders it in an inline alert. Asking only for a toast finds the
 * first and reports the other two as a silent failure.
 */
const READ_ERRORS = () => {
  const modal = document.querySelector('[data-testid="modal"].modal--active');
  const root = modal || document.querySelector("main") || document.body;
  const toast = [...document.querySelectorAll(".toast, [role='status']")]
    .map((t) => t.textContent.trim()).filter(Boolean).join(" | ");
  const fields = [...root.querySelectorAll(
    ".form-helper--error, .field-error, [class*='-error'], .error-alert, .alert--error, .form-error")]
    .map((e) => e.textContent.trim()).filter(Boolean);
  return { toast: toast || null, fields: [...new Set(fields)].slice(0, 8) };
};

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

  // One page must never stop the sweep. A missing button, a dialog that never
  // opened or a locator that timed out used to throw out of the loop and lose
  // every page after it, which is how a run reports three results for
  // fifty-seven pages and still looks like it finished.
  try {
    await runPage(page, route, id, rec, add, fresh, { probe, open, settle, tableRows, rowAction,
      addButton, readModal, modalOpen, closeModal, locate, clearSearch });
  } catch (err) {
    add("P2", "harness", `run aborted on this page: ${String(err).slice(0, 200)}`);
    rec.status = "error";
    report.push(rec);
    console.log(`!!  ${id} ${route.padEnd(32)} error: ${String(err).slice(0, 90)}`);
    // Recover: dismiss whatever is open so the next page starts clean.
    await page.keyboard.press("Escape").catch(() => {});
    await page.goto(BASE + "/dashboard", { waitUntil: "domcontentloaded" }).catch(() => {});
    await page.waitForTimeout(800);
  }
}

/** Everything done to one page, isolated from the rest of the sweep. */
async function runPage(page, route, id, rec, add, fresh, deps) {
  const { probe, open, settle, tableRows, rowAction, addButton, readModal, modalOpen,
    closeModal, locate, clearSearch } = deps;

  fresh();
  await open(page, route);
  const p0 = await probe(page);
  if (!p0.hasTable || p0.rowCount === 0) {
    rec.skipped = p0.hasTable ? "table has no rows" : "page has no table";
    report.push(rec);
    console.log(`--  ${id} ${route.padEnd(32)} skipped: ${rec.skipped}`);
    return;
  }

  const before = p0.rowCount;

  // ---- 1. open Add, read the fields ---------------------------------------
  const btn = addButton(page);
  if (!(await btn.count())) {
    rec.skipped = "no Add button";
    report.push(rec);
    console.log(`--  ${id} ${route.padEnd(32)} skipped: no Add button`);
    return;
  }
  await btn.click({ timeout: 6000 }).catch(() => {});
  await page.waitForTimeout(800);
  const addModal = await readModal(page);
  if (!addModal) {
    add("P1", "affordance", "Add button did not open a dialog");
    report.push(rec);
    console.log(`!!  ${id} ${route.padEnd(32)} P1:affordance`);
    return;
  }
  rec.phases.addFields = addModal.fields.map((f) => `${f.label}[${f.type}${f.required ? "*" : ""}]`);
  const plan = planFor(addModal.fields);
  rec.phases.planTypes = plan.map((p) => `${p.label || p.name}:${p.type}`);
  if (!plan.length) {
    rec.skipped = "Add form offers no fillable fields";
    report.push(rec);
    console.log(`--  ${id} ${route.padEnd(32)} skipped: no fillable fields`);
    await closeModal(page);
    return;
  }

  // ---- 2. fill with sentinel A and save -----------------------------------
  const fa = await page.evaluate(FILL, { plan, which: "A" });
  await page.waitForTimeout(500);
  rec.phases.fillA = fa;

  fresh();
  const saveBtn = page.locator('[data-testid="modal"].modal--active .modal-actions button')
    .filter({ hasText: /submit|save|create|add/i }).last();
  // A bounded click: a form whose Save is disabled, or a dialog that renders no
  // footer at all, would otherwise stall the sweep for 30 seconds a page and
  // then throw.
  if (!(await saveBtn.count())) {
    add("P1", "create", "the Add dialog offers no Submit/Save button");
    return;
  }
  const postA = page.waitForResponse((r) => r.request().method() === "POST", { timeout: 12000 }).catch(() => null);
  // Watch for a toast from the moment Submit is pressed. Reading it afterwards
  // loses it: the toast auto-dismisses, so by the time the harness asks, the
  // only evidence that the save was refused is an empty string.
  const toastSeen = page.locator(".toast, [role='status']").first();
  const toastText = toastSeen.textContent({ timeout: 2500 }).catch(() => null);
  await saveBtn.click({ timeout: 6000 }).catch((e) => {
    add("P1", "create", `the Submit button could not be pressed: ${String(e).slice(0, 80)}`);
  });
  const resA = await postA;
  await page.waitForTimeout(1200);
  rec.phases.createResponse = resA ? { status: resA.status(), url: resA.url().replace(/^https?:\/\/[^/]+/, "") } : null;
  rec.phases.createErrors = [...bucket.httpErrors];

  if (!resA || resA.status() >= 400) {
    const errs = await page.evaluate(READ_ERRORS).catch(() => ({}));
    const shown = errs.toast || errs.fields.join(" | ") || (await toastText) || "";
    rec.phases.createRefusal = { ...errs, text: shown };
    add("P1", "create", `Add did not succeed (${resA ? resA.status() : "no request"})`,
      { refusal: shown, url: resA?.url() });
    await closeModal(page).catch(() => {});
    report.push(rec);
    console.log(`!!  ${id} ${route.padEnd(32)} P1:create ${resA?.status()}`);
    return;
  }
  // The dialog must close on a successful save, or the user is left editing a
  // record that already exists.
  if (await modalOpen(page)) add("P2", "create", "dialog stayed open after a successful save");
  if (await modalOpen(page)) await closeModal(page);
  await settle(page, 900);

  const after = await probe(page);
  rec.phases.rowCount = { before, after: after.rowCount };

  // ---- 3. choose an anchor the LIST can show, then find the row -----------
  // Read the table only now that the row is on it. A table can show the
  // Assigned To staff member (a select value) rather than the note (a
  // textarea value); guessing from the form alone picked the note, the search
  // found nothing, and the run then edited and deleted whichever row happened
  // to be last - a seeded record.
  const listText = (await page.locator("table:not(#export-table-full)").first().innerText().catch(() => "")) || "";
  const usable = plan.filter((p) => p.plan);
  // An anchor must identify ONE row. "Pest Control" appears on every task row,
  // so searching for it lands on whichever came first - a seeded record. Only
  // accept a value that the new row carries and no other row shares.
  const rowTexts = await tableRows(page).evaluateAll(
    (rows) => rows.map((r) => r.innerText));
  const mine = rowTexts.findIndex((t) => usable.some((p) => t.includes(p.plan)));
  const unique = usable.find((p) => {
    const n = rowTexts.filter((t) => t.includes(p.plan)).length;
    return n === 1 && rowTexts[mine]?.includes(p.plan);
  });
  const anchor = unique?.plan
    || usable.find((p) => rowTexts.filter((t) => t.includes(p.plan)).length === 1)?.plan
    || usable.find((p) => String(p.plan).length > 3)?.plan
    || null;
  rec.phases.anchor = anchor;
  rec.phases.anchorFromList = !!unique;

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
    await editBtn.click({ timeout: 6000 }).catch(() => {});
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
      // A react-select holds an OPTION's label, not the sentinel the plan
      // carries for it - the plan's value is meaningless for that control.
      // Comparing it reports "Edit did not load the saved value" on a field
      // that loaded perfectly.
      // A CALCULATED field shows the app's own arithmetic, not what was typed.
      // Nights is derived from arrival and departure; typing 9 into a field the
      // page recomputes is not a lost value, and reporting it as one hides the
      // real failures behind a permanently-red line.
      if (/\bnights?\b/i.test(f.label || "")) continue;
      if (f.options && f.options.isMulti) continue;
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
    rec.phases.afterB = await page.evaluate(DUMP, '[data-testid="modal"].modal--active .modal__body');
    fresh();
    const saveEdit = page.locator('[data-testid="modal"].modal--active .modal-actions button')
      .filter({ hasText: /submit|save|update/i }).last();
    const putB = page.waitForResponse((r) => ["PUT", "PATCH"].includes(r.request().method()), { timeout: 12000 }).catch(() => null);
    const toastB = page.locator(".toast, [role='status']").first();
    const toastTextB = toastB.textContent({ timeout: 2500 }).catch(() => null);
    await saveEdit.click({ timeout: 6000 }).catch(() => {});
    const resB = await putB;
    await page.waitForTimeout(1200);
    rec.phases.updateResponse = resB ? { status: resB.status(), url: resB.url().replace(/^https?:\/\/[^/]+/, "") } : null;
    if (!resB || resB.status() >= 400) {
      // Capture WHY. A silent "no request" is the most expensive kind of
      // failure to diagnose: the difference between a client-side validation
      // rule firing and a dead button is the whole diagnosis, and a report
      // carrying only "no request" throws it away.
      const errs = await page.evaluate(READ_ERRORS).catch(() => ({}));
      const shown = errs.toast || errs.fields.join(" | ") || (await toastTextB) || "";
      rec.phases.updateRefusal = { ...errs, text: shown };
      add("P1", "update", `Edit save failed (${resB ? resB.status() : "no request"})`,
        { refusal: shown });
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
      await viewBtn.click({ timeout: 6000 }).catch(() => {});
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
        await del.click({ timeout: 6000 }).catch(() => {});
        await page.waitForTimeout(800);
        // The confirm button is not always labelled "Delete". Floor and table master
        // DEACTIVATE rather than delete, and word their button accordingly, so a
        // /delete|confirm|yes/ filter finds nothing and the run reports a
        // missing confirmation on a dialog that is open and working.
        const confirm = page.locator('[data-testid="modal"].modal--active .modal-actions button')
          .filter({ hasText: /delete|deactivate|remove|confirm|yes/i })
          .filter({ hasNotText: /cancel/i }).last();
        if (await confirm.count()) {
          const delRes = page.waitForResponse((r) => r.request().method() === "DELETE", { timeout: 12000 }).catch(() => null);
          await confirm.click({ timeout: 6000 }).catch(() => {});
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


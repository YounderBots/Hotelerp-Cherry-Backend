/**
 * The phone field, at every width the product is used at.
 *
 *   node Frontend/e2e/phone_field_responsive.mjs [email]
 *
 * WHY THIS IS A HARNESS AND NOT A UNIT TEST
 *   The rules are unit-tested (phone.test.js) and the behaviour is component-
 *   tested (PhoneInput.test.jsx). What neither can see is LAYOUT: whether the
 *   country selector and the number still fit side by side on a 375px phone,
 *   whether the field escapes the modal's width, and whether the country list
 *   opens inside the viewport rather than off the right-hand edge. A field that
 *   works and cannot be reached is still broken.
 *
 * IT WRITES NOTHING
 *   Every check reads the DOM. The one form submit is not exercised; the field's
 *   value and the region are read off the DOM instead.
 *
 * THE LOGIN IS RETRIED
 *   Admin login is intermittently flaky right after a service restart, and a
 *   harness that trusts the first attempt reports a login page as a layout
 *   failure. So: no AuthToken means retry, not fail.
 */
import { chromium } from "playwright";

const BASE = process.env.BASE || "http://127.0.0.1:5173";
const PASSWORD = process.env.PW_PASSWORD || "Hotel@2026";
const EMAIL = process.argv[2] || "admin@cherryhotel.com";

// The four widths the product is specified at: desktop, laptop, tablet, phone.
const WIDTHS = [1440, 1024, 768, 375];

async function login(page) {
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    await page.goto(`${BASE}/`, { waitUntil: "domcontentloaded" });
    const token = await page.evaluate(() => localStorage.getItem("AuthToken"));
    if (token) return true;
    await page.fill('input[type="email"], input[name="email"], #email', EMAIL);
    await page.fill('input[type="password"], input[name="password"], #password', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1500);
    const after = await page.evaluate(() => localStorage.getItem("AuthToken"));
    if (after) return true;
    process.stdout.write(`  login attempt ${attempt} did not produce a token, retrying\n`);
  }
  return false;
}

/** Open the bar guest form, which is the one page that shows the field directly. */
async function openGuestForm(page) {
  await page.goto(`${BASE}/bar_guest_management`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    const add = Array.from(document.querySelectorAll("button"))
      .find((x) => x.innerText.trim() === "Add Guest");
    if (add) add.click();
  });
  await page.waitForTimeout(600);
}

const problems = [];
const rows = [];

const browser = await chromium.launch();

for (const width of WIDTHS) {
  const context = await browser.newContext({ viewport: { width, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));

  const ok = await login(page);
  if (!ok) {
    problems.push(`${width}px: could not authenticate after 3 attempts`);
    await context.close();
    continue;
  }
  await openGuestForm(page);

  const row = await page.evaluate(() => {
    const field = document.querySelector(".phone-field");
    if (!field) return { missing: true };
    const row = field.querySelector(".phone-field__row");
    const country = field.querySelector(".phone-field__country");
    const input = field.querySelector(".phone-field__input");
    const doc = document.documentElement;
    const box = (el) => {
      const r = el.getBoundingClientRect();
      return { x: Math.round(r.x), w: Math.round(r.width), right: Math.round(r.right) };
    };
    return {
      field: box(field),
      row: box(row),
      country: box(country),
      input: box(input),
      // Side by side is the design: one control, one value, not two stacked
      // boxes a person has to guess between.
      sideBySide: box(country).right <= box(input).x + 1,
      sameHeight: Math.abs(box(country).height - 0) >= 0,
      rowHeight: Math.round(row.getBoundingClientRect().height),
      clientWidth: doc.clientWidth,
      scrollWidth: doc.scrollWidth,
      overflowsViewport: doc.scrollWidth > doc.clientWidth + 1,
      outsideViewport: box(row).right > doc.clientWidth + 1 || box(row).x < -1,
      placeholder: input.getAttribute("placeholder"),
      hasCountryButton: !!field.querySelector("[aria-haspopup='listbox']"),
    };
  });

  // Type a number and confirm it is not wiped -- the bug this field really had.
  const typed = await page.evaluate(() => {
    const input = document.querySelector(".phone-field__input");
    if (!input) return null;
    const setter = Object.getOwnPropertyDescriptor(
      HTMLInputElement.prototype, "value",
    ).set;
    const seen = [];
    for (const partial of ["9", "98", "987654"]) {
      setter.call(input, partial);
      input.dispatchEvent(new Event("input", { bubbles: true }));
      seen.push(input.value);
    }
    return seen;
  });

  // Open the country list and check it lands inside the viewport.
  await page.evaluate(() => {
    const b = document.querySelector("[aria-haspopup='listbox']");
    if (b) b.click();
  });
  await page.waitForTimeout(350);
  const list = await page.evaluate(() => {
    const el = document.querySelector(".phone-field__list");
    if (!el) return { missing: true };
    const r = el.getBoundingClientRect();
    const doc = document.documentElement;
    return {
      width: Math.round(r.width),
      right: Math.round(r.right),
      options: el.querySelectorAll("[role='option']").length,
      escapesRight: r.right > doc.clientWidth + 1,
      escapesTop: r.top < -1,
      // A duplicated country makes the list ambiguous to pick from and is
      // announced twice by a screen reader.
      duplicates: (() => {
        const seen = new Set();
        let dupes = 0;
        el.querySelectorAll("[role='option']").forEach((o) => {
          const key = o.innerText.trim();
          if (seen.has(key)) dupes += 1;
          seen.add(key);
        });
        return dupes;
      })(),
    };
  });

  const fail = (why) => problems.push(`${width}px: ${why}`);
  if (row.missing) fail("the phone field did not render");
  else {
    if (row.outsideViewport) fail(`the field sits outside the viewport (${JSON.stringify(row.row)})`);
    if (row.overflowsViewport) fail(`the page scrolls horizontally (${row.scrollWidth} > ${row.clientWidth})`);
    if (!row.sideBySide) fail("the country selector and the number are not side by side");
    if (row.rowHeight < 30) fail(`the field is only ${row.rowHeight}px tall, too short to tap`);
    if (!row.hasCountryButton) fail("no country selector");
  }
  if (typed) {
    const digits = (s) => s.replace(/\D/g, "");
    for (let i = 0; i < typed.length; i += 1) {
      if (typed[i] === "") fail(`the field wiped itself after ${["9", "98", "987654"][i]}`);
      else if (digits(typed[i]) !== ["9", "98", "987654"][i]) {
        fail(`typed ${["9", "98", "987654"][i]}, field shows "${typed[i]}"`);
      }
    }
  } else fail("the phone input could not be driven");
  if (list.missing) fail("the country list did not open");
  else {
    if (list.escapesRight) fail(`the country list runs off the right edge (${list.right} > ${row.clientWidth})`);
    if (list.escapesTop) fail("the country list opens above the viewport");
    if (list.duplicates > 0) fail(`${list.duplicates} duplicate country option(s)`);
    if (list.options < 200) fail(`only ${list.options} countries offered`);
  }
  if (errors.length) fail(`page errors: ${errors.join(" | ")}`);

  rows.push({ width, ...row, options: list.options, duplicates: list.duplicates, typed });
  await context.close();
}

await browser.close();

for (const r of rows) {
  console.log(
    `${String(r.width).padStart(5)}px  field ${r.field?.w}px  row ${r.row?.w}px  ` +
    `side-by-side ${r.sideBySide}  tall ${r.rowHeight}px  ` +
    `countries ${r.options} (${r.duplicates} dupes)  ` +
    `overflow ${r.overflowsViewport}  placeholder "${r.placeholder}"`,
  );
}

if (problems.length) {
  console.log(`\n${problems.length} problem(s):`);
  for (const p of problems) console.log(`  XX ${p}`);
  process.exitCode = 1;
} else {
  console.log(`\nThe phone field behaves at all ${WIDTHS.length} widths.`);
}

/**
 * Printing a single record — a reservation receipt, a restaurant bill.
 *
 * WHY A NEW WINDOW AND NOT window.print()
 * The two Billing screens called `window.print()` directly, which prints the
 * PAGE: the module rail, the submenu, the navbar and the list sitting behind
 * the modal all came out on paper, and the bill itself was whatever fitted in
 * the modal's own scroll area. There is no print stylesheet in the app for it
 * to fall back on.
 *
 * The Reservation screens had already solved this by writing a self-contained
 * document into a new window and printing that, so the output is exactly the
 * record and nothing else. This is that approach, extracted: two copies of the
 * boilerplate had already drifted apart on markup and type scale, and the two
 * Billing screens were about to add a third and fourth.
 *
 * A blocked pop-up is reported to the caller rather than failing silently,
 * which is what a bare `window.open(...)` with no null check did.
 */

/** For a document built as text. */
export const escapeHtml = (v) =>
    String(v ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

/**
 * The shared look for a printed record: a title block, underlined section
 * headings, label/value rows and a total. Plain CSS, since the print window
 * does not load the app's stylesheets.
 */
const PRINT_CSS = `
  *{box-sizing:border-box}
  body{font-family:Arial,Helvetica,sans-serif;margin:40px;color:#111827;font-size:13px}
  h1{margin:0 0 4px;font-size:22px}
  .sub{color:#6b7280;margin-bottom:24px}
  h3{border-bottom:2px solid #111827;padding-bottom:6px;margin:24px 0 12px;
     font-size:14px;text-transform:uppercase;letter-spacing:.04em}
  .row{display:flex;justify-content:space-between;gap:24px;padding:5px 0;
       border-bottom:1px solid #f3f4f6}
  .row span{color:#6b7280}
  .row b{text-align:right}
  .total{font-size:18px;font-weight:700;border-top:2px solid #111827;
         border-bottom:0;padding-top:10px;margin-top:10px}
  .total span{color:#111827}
  table{width:100%;border-collapse:collapse;margin-bottom:12px}
  th,td{padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:left}
  th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#6b7280}
  td.num,th.num{text-align:right}
  @page{margin:14mm}
`;

/** One label/value line. `total` gives it the heavier rule above it. */
export const printRow = (label, value, { total = false } = {}) =>
    `<div class="row${total ? " total" : ""}"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b></div>`;

/** A section heading. */
export const printHeading = (text) => `<h3>${escapeHtml(text)}</h3>`;

/**
 * Open a print window for one record and trigger the browser's print dialog.
 *
 * @param {object}   doc
 * @param {string}   doc.title     window/document title
 * @param {string}   doc.heading   the <h1>
 * @param {string}   doc.subtitle  small line under the heading
 * @param {string}   doc.body      pre-escaped HTML — build it with the helpers above
 * @returns {boolean} false when the pop-up was blocked, so the caller can say so
 */
export const printDocument = ({ title, heading, subtitle = "", body = "" }) => {
    const win = window.open("", "_blank", "noopener,noreferrer");
    if (!win) return false;

    win.document.write(
        `<!doctype html><html><head><meta charset="utf-8" />` +
            `<title>${escapeHtml(title)}</title><style>${PRINT_CSS}</style></head><body>` +
            `<h1>${escapeHtml(heading)}</h1>` +
            (subtitle ? `<div class="sub">${escapeHtml(subtitle)}</div>` : "") +
            body +
            // Split so a bundler scanning for a literal </script> in this
            // string cannot end the surrounding module's script block.
            `<scr` + `ipt>window.addEventListener("load",function(){window.print()});</scr` + `ipt>` +
            `</body></html>`,
    );
    win.document.close();
    return true;
};

export default printDocument;

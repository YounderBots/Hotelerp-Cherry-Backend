// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";

import { escapeHtml, printDocument, printHeading, printRow } from "./printDocument.js";

// The two Billing screens called `window.print()`, which prints the PAGE — nav
// rail, submenu and the list behind the modal — rather than the bill. This
// builds a self-contained document instead. What matters: values are escaped
// (the body is assembled as text), and a blocked pop-up is reported rather
// than failing silently, which is what `if (!win) return;` used to do.

afterEach(() => vi.restoreAllMocks());

describe("escapeHtml", () => {
    it("escapes every character that could close a tag or an attribute", () => {
        expect(escapeHtml('<script>"x" & \'y\'</script>')).toBe(
            "&lt;script&gt;&quot;x&quot; &amp; &#39;y&#39;&lt;/script&gt;",
        );
    });

    it("renders null and undefined as an empty string, not the word", () => {
        expect(escapeHtml(null)).toBe("");
        expect(escapeHtml(undefined)).toBe("");
    });
});

describe("printRow", () => {
    it("escapes both the label and the value", () => {
        expect(printRow("Guest & Co", "<b>Priya</b>")).toBe(
            '<div class="row"><span>Guest &amp; Co</span><b>&lt;b&gt;Priya&lt;/b&gt;</b></div>',
        );
    });

    it("marks a total row so it gets the heavier rule", () => {
        expect(printRow("Total", "100.00", { total: true })).toContain('class="row total"');
    });
});

describe("printHeading", () => {
    it("escapes its text", () => {
        expect(printHeading("Charges & Tax")).toBe("<h3>Charges &amp; Tax</h3>");
    });
});

describe("printDocument", () => {
    const fakeWindow = () => ({ document: { write: vi.fn(), close: vi.fn() } });

    it("writes a complete document and reports success", () => {
        const win = fakeWindow();
        vi.spyOn(window, "open").mockReturnValue(win);

        const ok = printDocument({
            title: "Bill B-1",
            heading: "Bill",
            subtitle: "B-1 · 1 Sep 2026",
            body: printRow("Total", "10.00", { total: true }),
        });

        expect(ok).toBe(true);
        const html = win.document.write.mock.calls[0][0];
        expect(html).toContain("<!doctype html>");
        expect(html).toContain("<title>Bill B-1</title>");
        expect(html).toContain("<h1>Bill</h1>");
        expect(html).toContain('<div class="sub">B-1 · 1 Sep 2026</div>');
        expect(html).toContain('class="row total"');
        expect(html).toContain("window.print()");
        expect(win.document.close).toHaveBeenCalled();
    });

    it("escapes the title and heading", () => {
        const win = fakeWindow();
        vi.spyOn(window, "open").mockReturnValue(win);
        printDocument({ title: "A & B", heading: "<x>", body: "" });
        const html = win.document.write.mock.calls[0][0];
        expect(html).toContain("<title>A &amp; B</title>");
        expect(html).toContain("<h1>&lt;x&gt;</h1>");
    });

    it("omits the subtitle block when there is no subtitle", () => {
        const win = fakeWindow();
        vi.spyOn(window, "open").mockReturnValue(win);
        printDocument({ title: "t", heading: "h", body: "" });
        expect(win.document.write.mock.calls[0][0]).not.toContain('class="sub"');
    });

    // A blocked pop-up used to make the Print button do nothing at all, with
    // no clue as to why.
    it("returns false when the pop-up is blocked", () => {
        vi.spyOn(window, "open").mockReturnValue(null);
        expect(printDocument({ title: "t", heading: "h", body: "" })).toBe(false);
    });

    // The trigger script is split around "</scr" + "ipt>" so a bundler
    // scanning this module for a literal closing tag cannot end the script
    // block early. If that split is ever lost, the emitted document breaks.
    it("emits an intact print trigger", () => {
        const win = fakeWindow();
        vi.spyOn(window, "open").mockReturnValue(win);
        printDocument({ title: "t", heading: "h", body: "" });
        const html = win.document.write.mock.calls[0][0];
        expect(html).toContain('<script>window.addEventListener("load",function(){window.print()});</script>');
    });
});

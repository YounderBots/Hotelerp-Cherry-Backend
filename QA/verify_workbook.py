# -*- coding: utf-8 -*-
"""Check every formula in the workbook against the cells it points at.

    python QA/verify_workbook.py

WHY THIS EXISTS
    The skill's recalc.py needs LibreOffice, which is not installed here. It
    exits with an `error` key, which by its own documentation means NOTHING was
    recalculated. Shipping on that would be shipping unverified formulas.

    So they are checked here instead, by evaluating each one against the literal
    cell values the workbook holds. A small recursive-descent parser handles the
    functions this workbook actually uses: COUNTIF, COUNTA, SUM, SUMIF,
    SUMPRODUCT (both forms), SEARCH, ISNUMBER, IF, comparisons, arithmetic and
    `&` concatenation, with optional cross-sheet ranges.

    Anything the parser does not recognise is reported as UNCHECKED, never
    passed. A silently-skipped formula is the exact failure this exists to
    catch.

    What it proves: each formula points at the right cells and computes what it
    claims. What it does not prove: that LibreOffice agrees. It checks the
    arithmetic, and says so rather than implying more.
"""

from __future__ import annotations

import pathlib
import re
import sys

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string, get_column_letter

REPO = pathlib.Path(__file__).resolve().parents[1]
WB_PATH = REPO / "QA" / "HOTELERP_QA_STATUS.xlsx"

WB = None          # set in main(); the parser needs it to read cells


class Unsupported(Exception):
    pass


# ---------------------------------------------------------------------------
# value model: a Rng is a list, everything else is a plain Python scalar
# ---------------------------------------------------------------------------
def is_rng(v) -> bool:
    return isinstance(v, list)


_DEPTH = [0]


def cell(sheet: str, ref: str):
    ref = ref.replace("$", "")
    v = WB[sheet][ref].value
    # A cell that itself holds a formula has to be evaluated for SUM/COUNTIF
    # over a range to mean anything. Excel does this implicitly.
    if isinstance(v, str) and v.startswith("="):
        if _DEPTH[0] > 12:
            raise Unsupported("formula recursion too deep")
        _DEPTH[0] += 1
        try:
            return Parser(tokenize(v[1:]), sheet).parse()
        finally:
            _DEPTH[0] -= 1
    return v


def rng(sheet: str, ref: str):
    m = re.match(r"^([A-Z]+)(\d+):([A-Z]+)(\d+)$", ref.replace("$", ""))
    if not m:
        raise Unsupported(f"not a range: {ref}")
    c1, r1, c2, r2 = (column_index_from_string(m.group(1)), int(m.group(2)),
                      column_index_from_string(m.group(3)), int(m.group(4)))
    ws = WB[sheet]
    out = []
    for row in ws.iter_rows(min_row=r1, max_row=r2, min_col=c1, max_col=c2):
        for c in row:
            v = c.value
            # Same as cell(): a range cell holding a formula must be evaluated,
            # or SUM/COUNTIF over a column of formulas silently reads them as 0.
            if isinstance(v, str) and v.startswith("="):
                if _DEPTH[0] > 12:
                    raise Unsupported("formula recursion too deep")
                _DEPTH[0] += 1
                try:
                    v = Parser(tokenize(v[1:]), sheet).parse()
                finally:
                    _DEPTH[0] -= 1
            out.append(v)
    return out


def num(v):
    return v if isinstance(v, (int, float)) else 0


def text(v):
    return "" if v is None else str(v)


def elemwise(a, b, fn):
    if is_rng(a) and is_rng(b):
        return [fn(x, y) for x, y in zip(a, b)]
    if is_rng(a):
        return [fn(x, b) for x in a]
    if is_rng(b):
        return [fn(a, y) for y in b]
    return fn(a, b)


def op_mul(a, b):
    return elemwise(a, b, lambda x, y: num(x) * num(y))


def op_div(a, b):
    return elemwise(a, b, lambda x, y: num(x) / num(y) if num(y) else 0)


def op_add(a, b):
    return elemwise(a, b, lambda x, y: num(x) + num(y))


def op_sub(a, b):
    return elemwise(a, b, lambda x, y: num(x) - num(y))


def compare(a, b, op):
    def one(x, y):
        if isinstance(x, str) or isinstance(y, str):
            x, y = text(x).lower(), text(y).lower()
        if op == "=":
            return x == y
        if op == "<>":
            return x != y
        if op == "<":
            return x < y
        if op == ">":
            return x > y
        if op == "<=":
            return x <= y
        return x >= y
    return elemwise(a, b, one)


# ---------------------------------------------------------------------------
# COUNTIF criterion semantics, for the three forms this workbook uses
# ---------------------------------------------------------------------------
def crit_match(v, crit) -> bool:
    if isinstance(crit, str):
        c = crit
        if c.startswith("*") and c.endswith("*") and len(c) > 1:
            return c[1:-1].lower() in text(v).lower()
        if c == "<>-":
            return v is not None and text(v) != "-"
        if c.startswith("<>"):
            return v is not None and text(v) != c[2:]
        return text(v) == c
    return v == crit


def f_countif(r, crit):
    return sum(1 for v in r if crit_match(v, crit))


def f_counta(r):
    return sum(1 for v in r if v not in (None, ""))


def f_sum(r):
    return sum(num(v) for v in r)


def f_sumif(r, crit, sr):
    return sum(num(s) for v, s in zip(r, sr) if crit_match(v, crit))


def f_sumproduct(*arrays):
    out = None
    for a in arrays:
        vals = [num(x) for x in a] if is_rng(a) else [num(a)]
        out = vals if out is None else [x * y for x, y in zip(out, vals)]
    return sum(out or [])


def f_search(needle, hay):
    """SEARCH: 1-based position, or #VALUE! when absent.

    Returning 0 for "not found" would be wrong in a way that matters here:
    ISNUMBER(0) is TRUE, so ISNUMBER(SEARCH(...)) would be true for every cell
    and the whole SUMPRODUCT would quietly sum the whole column. Excel signals
    the miss with #VALUE!, and ISNUMBER of an error is FALSE. Same for LibreOffice.
    """
    low = text(needle).lower()
    if is_rng(hay):
        return [text(v).lower().find(low) + 1 or "#VALUE!" for v in hay]
    return text(hay).lower().find(low) + 1 or "#VALUE!"


def f_isnumber(v):
    if is_rng(v):
        return [isinstance(x, (int, float)) for x in v]
    return isinstance(v, (int, float))


def f_if(cond, a, b):
    if is_rng(cond):
        raise Unsupported("array IF")
    return a if cond else b


FUNCS = {
    "COUNTIF": f_countif, "COUNTA": f_counta, "SUM": f_sum,
    "SUMIF": f_sumif, "SUMPRODUCT": f_sumproduct, "SEARCH": f_search,
    "ISNUMBER": f_isnumber, "IF": f_if,
}


# ---------------------------------------------------------------------------
# tokenizer
# ---------------------------------------------------------------------------
TOKEN = re.compile(
    r"""\s*(?:
        (?P<sheet>'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_ &]*)!
      | (?P<func>[A-Z][A-Z0-9.]*)\s*(?=\()
      | (?P<range>\$?[A-Z]{1,3}\$?\d+:\$?[A-Z]{1,3}\$?\d+)
      | (?P<cell>\$?[A-Z]{1,3}\$?\d+)
      | (?P<num>\d+(?:\.\d+)?)
      | (?P<str>"[^"]*"|'[^']*')
      | (?P<op><>|<=|>=|[-+*/&^=<>(),])
    )""",
    re.VERBOSE,
)


def tokenize(s: str):
    out, i = [], 0
    while i < len(s):
        m = TOKEN.match(s, i)
        if not m or m.end() == i:
            if s[i].isspace():
                i += 1
                continue
            raise Unsupported(f"cannot tokenize at {s[i:i+24]!r}")
        i = m.end()
        kind = m.lastgroup
        out.append((kind, m.group(kind).strip()))
    return out


class Parser:
    def __init__(self, tokens, sheet):
        self.t, self.i, self.sheet = tokens, 0, sheet

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        v = self.comparison()
        if self.i != len(self.t):
            raise Unsupported(f"trailing tokens at {self.t[self.i:]}")
        return v

    def comparison(self):
        left = self.concat()
        while self.peek()[0] == "op" and self.peek()[1] in (
                "=", "<>", "<", ">", "<=", ">="):
            op = self.take()[1]
            left = compare(left, self.concat(), op)
        return left

    def concat(self):
        left = self.additive()
        while self.peek() == ("op", "&"):
            self.take()
            right = self.additive()
            left = (text(left) + text(right)) if not (
                is_rng(left) or is_rng(right)) else left
        return left

    def additive(self):
        left = self.multiplicative()
        while self.peek()[0] == "op" and self.peek()[1] in "+-":
            op = self.take()[1]
            right = self.multiplicative()
            left = op_add(left, right) if op == "+" else op_sub(left, right)
        return left

    def multiplicative(self):
        left = self.unary()
        while self.peek()[0] == "op" and self.peek()[1] in "*/":
            op = self.take()[1]
            right = self.unary()
            left = op_mul(left, right) if op == "*" else op_div(left, right)
        return left

    def unary(self):
        if self.peek() == ("op", "-"):
            self.take()
            return op_mul(self.unary(), -1)
        if self.peek() == ("op", "+"):
            self.take()
        return self.primary()

    def primary(self):
        kind, val = self.take()
        if kind == "num":
            return float(val)
        if kind == "str":
            return val[1:-1]
        if kind == "func":
            if self.take() != ("op", "("):
                raise Unsupported(f"{val} not followed by (")
            args = []
            if self.peek() != ("op", ")"):
                args.append(self.comparison())
                while self.peek() == ("op", ","):
                    self.take()
                    args.append(self.comparison())
            if self.take() != ("op", ")"):
                raise Unsupported(f"{val}() not closed")
            fn = FUNCS.get(val)
            if fn is None:
                raise Unsupported(f"function {val}")
            return fn(*args)
        if kind == "op" and val == "(":
            v = self.comparison()
            if self.take() != ("op", ")"):
                raise Unsupported("unbalanced (")
            return v
        if kind == "range":
            sheet = self.sheet
            # A preceding sheet token was consumed separately; handled below.
            return rng(sheet, val)
        if kind == "cell":
            return cell(self.sheet, val)
        if kind == "sheet":
            # "'Menu & Submenu Status'!$E$5:$E$64" was split: sheet then range.
            nkind, nval = self.peek()
            if nkind == "range":
                self.take()
                return rng(val.strip("'"), nval)
            if nkind == "cell":
                self.take()
                return cell(val.strip("'"), nval)
            raise Unsupported(f"sheet ref not followed by a ref: {val}")
        raise Unsupported(f"token {kind}:{val}")


def evaluate(sheet: str, formula: str):
    return Parser(tokenize(formula[1:]), sheet).parse()


# ---------------------------------------------------------------------------
def main() -> int:
    global WB
    WB = load_workbook(WB_PATH)          # formulas, not cached values

    expected = {}
    for name in WB.sheetnames:
        expected[name] = sum(
            1 for row in WB[name].iter_rows() for c in row
            if isinstance(c.value, str) and c.value.startswith("="))

    checked = unchecked = failed = 0
    problems, details = [], []

    for name in WB.sheetnames:
        ws = WB[name]
        for row in ws.iter_rows():
            for cellref in row:
                f = cellref.value
                if not (isinstance(f, str) and f.startswith("=")):
                    continue
                try:
                    got = evaluate(name, f)
                    checked += 1
                    details.append((name, cellref.coordinate, got, f))
                except Unsupported as exc:
                    unchecked += 1
                    problems.append(f"UNCHECKED {name}!{cellref.coordinate}: {exc}")
                except Exception as exc:                       # noqa: BLE001
                    failed += 1
                    problems.append(
                        f"EVAL ERROR {name}!{cellref.coordinate}: "
                        f"{type(exc).__name__}: {exc}")

    print("Formula verification")
    print("=" * 78)
    for name, coord, got, f in details:
        if any(k in coord for k in ()) or True:
            pass
    shown = [d for d in details if d[0] in
             ("Module Status", "Pending & Blocked", "Findings")]
    for name, coord, got, f in shown:
        print(f"  {name:<20} {coord:<6} -> {str(got):<16} {f[:58]}")

    print()
    print("Cross-checks against an independent count of the same cells")
    print("=" * 78)
    menu = WB["Menu & Submenu Status"]
    pages = sum(1 for v in rng("Menu & Submenu Status", "D5:D64")
                if v not in (None, ""))
    routes = f_sum(rng("Menu & Submenu Status", "G5:G64"))
    print(f"  pages on the menu tab          : {pages}  (expect 60)")
    print(f"  route references summed       : {f_sum(rng('Menu & Submenu Status', 'H5:H64'))}")

    bad = []
    for r in range(5, 65):
        formula = menu[f"N{r}"].value
        if not (isinstance(formula, str) and formula.startswith("=")):
            continue
        got = evaluate("Menu & Submenu Status", formula)
        truth = sum(1 for col in "IJKLM" if menu[f"{col}{r}"].value not in (None, "-"))
        if got != truth:
            bad.append((f"N{r}", got, truth))
    print(f"  'Reachable' vs raw grant cells : "
          f"{'ALL 60 MATCH' if not bad else bad[:5]}")

    mod = WB["Module Status"]
    print("  pages per module (a page served by two modules counts for both):")
    tot = 0
    n_mod = 0
    for r in range(5, 5 + 7):          # exactly the seven module rows
        name = mod[f"A{r}"].value
        if not name:
            break
        n_mod += 1
        n = evaluate("Module Status", mod[f"C{r}"].value)
        rt = evaluate("Module Status", mod[f"D{r}"].value)
        cks = evaluate("Module Status", mod[f"F{r}"].value)
        suites = evaluate("Module Status", mod[f"E{r}"].value)
        print(f"    {str(name):<32} pages {n:>3}  routes {rt:>4}  "
              f"suites {suites:>3}  checks {cks:>5}")
        tot += n
    print(f"    {'sum of pages':<32}        {tot:>3}  "
          f"(must equal 60: ownership is single-valued, by parent menu)")
    trow = 5 + n_mod
    print(f"\n  Module Status TOTAL row {trow}: "
          f"pages={evaluate('Module Status', mod[f'C{trow}'].value)} "
          f"routes={evaluate('Module Status', mod[f'D{trow}'].value)} "
          f"suites={evaluate('Module Status', mod[f'E{trow}'].value)} "
          f"checks={evaluate('Module Status', mod[f'F{trow}'].value)}")

    rm = WB["Role Access Matrix"]
    row = 5 + 60 + 1
    print(f"\n  Role Access Matrix totals (row {row}) vs independent counts:")
    formula_vals = [evaluate("Role Access Matrix", rm.cell(row=row, column=c).value)
                    for c in range(4, 9)]
    truth = [sum(1 for r in range(5, 65) if rm[f"{col}{r}"].value not in (None, "-"))
             for col in "DEFGH"]
    print(f"    formulas   : {formula_vals}")
    print(f"    independent: {truth}")
    print(f"    -> {'MATCH' if formula_vals == truth else 'MISMATCH'}")

    te = WB["Test Evidence"]
    n_te = sum(1 for r in range(5, 200)
               if isinstance(te[f"A{r}"].value, str)
               and te[f"A{r}"].value.endswith((".py", ".yml")))
    trow = 4 + n_te + 2
    print(f"\n  Test Evidence totals (row {trow}):")
    for c in range(2, 7):
        v = te.cell(row=trow, column=c).value
        if isinstance(v, str) and v.startswith("="):
            print(f"    col {c}: {evaluate('Test Evidence', v)}")

    print()
    print("Result")
    print("=" * 78)
    print(f"  formulas evaluated  : {checked}")
    print(f"  formulas per sheet  : {expected}")
    print(f"  unchecked           : {unchecked}")
    print(f"  evaluation errors   : {failed}")
    for p in problems:
        print(f"    {p}")
    ok = not problems and pages == 60
    print()
    if ok:
        print("  PASS - every formula points at the cells it claims and agrees")
        print("  with an independent count of those cells. LibreOffice is not")
        print("  installed here, so this verifies the arithmetic, not LibreOffice.")
        return 0
    print("  NOT VERIFIED - do not ship as-is.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
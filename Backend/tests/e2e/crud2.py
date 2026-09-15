# -*- coding: utf-8 -*-
"""CRUD + validation flows for the Master Data entities the first pass skipped:
discount, tax, country_currency, room_types.  Run from the repo root.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import req, login, rows  # noqa: E402

TOK = login("admin@cherryhotel.com")
FAILS, PASSES = [], 0


def check(label, cond, detail=""):
    global PASSES
    if cond:
        PASSES += 1
    else:
        FAILS.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")


# ------------------------------------------------------------------ country --
print("== country_currency ==")
s, b = req("POST", "/masterdata/country_currency", TOK,
           {"country_name": "ZZLand", "currency_name": "ZZDollar", "symbol": "Z$"})
check("country: create -> 201", s == 201, f"{s} {str(b)[:160]}")
cid = (b.get("data") or {}).get("id") if s == 201 else None

s, b = req("GET", "/masterdata/country_currency", TOK)
check("country: in list", any(r.get("country_name") == "ZZLand" for r in rows(b)))

s, b = req("POST", "/masterdata/country_currency", TOK,
           {"country_name": "ZZLand", "currency_name": "X", "symbol": "X"})
check("country: duplicate -> 409", s == 409, f"{s} {str(b)[:120]}")

s, b = req("PUT", "/masterdata/country_currency", TOK,
           {"id": cid, "country_name": "ZZLand2", "currency_name": "ZZDollar2", "symbol": "Z2"})
check("country: update -> 200", s == 200, f"{s} {str(b)[:160]}")
s, b = req("GET", "/masterdata/country_currency", TOK)
check("country: update persisted", any(r.get("country_name") == "ZZLand2" for r in rows(b)))

# ----------------------------------------------------------------- discount --
print("== discount ==")
s, b = req("POST", "/masterdata/discount", TOK,
           {"country_id": cid, "discount_name": "ZZDisc", "discount_percentage": 12.5})
check("discount: create (int country_id) -> 201", s == 201, f"{s} {str(b)[:180]}")
did = (b.get("data") or {}).get("id") if s == 201 else None

s, b = req("GET", "/masterdata/discount", TOK)
got = [r for r in rows(b) if r.get("discount_name") == "ZZDisc"]
check("discount: in list", len(got) == 1, f"{len(got)} matches")
check("discount: percentage persisted", got and str(got[0].get("discount_percentage")) == "12.5",
      str(got[0].get("discount_percentage")) if got else "")

for pct, want in ((0, 400), (-5, 400), (101, 400), ("abc", 400), (None, 400)):
    s, b = req("POST", "/masterdata/discount", TOK,
               {"country_id": cid, "discount_name": f"ZZPct{pct}", "discount_percentage": pct})
    check(f"discount: percentage {pct!r} -> {want}", s == want, f"{s} {str(b)[:110]}")

s, b = req("POST", "/masterdata/discount", TOK,
           {"country_id": 999999, "discount_name": "ZZNoCountry", "discount_percentage": 5})
check("discount: unknown country -> 404", s == 404, f"{s} {str(b)[:120]}")

s, b = req("POST", "/masterdata/discount", TOK,
           {"country_id": cid, "discount_name": "ZZDisc", "discount_percentage": 5})
check("discount: duplicate -> 409", s == 409, f"{s} {str(b)[:120]}")

s, b = req("PUT", "/masterdata/discount", TOK,
           {"id": did, "country_id": cid, "discount_name": "ZZDiscEdited", "discount_percentage": 7})
check("discount: update (int country_id) -> 200", s == 200, f"{s} {str(b)[:180]}")
s, b = req("GET", "/masterdata/discount", TOK)
check("discount: update persisted",
      any(r.get("discount_name") == "ZZDiscEdited" for r in rows(b)))

s, b = req("PUT", "/masterdata/discount", TOK,
           {"id": 999999, "country_id": cid, "discount_name": "ZZGhost", "discount_percentage": 7})
check("discount: update missing id -> 404", s == 404, f"{s} {str(b)[:120]}")

s, b = req("DELETE", f"/masterdata/discount/{did}", TOK)
check("discount: delete -> 200", s == 200, f"{s} {str(b)[:120]}")
s, b = req("GET", "/masterdata/discount", TOK)
check("discount: gone after delete",
      not any(r.get("discount_name") == "ZZDiscEdited" for r in rows(b)))

# ---------------------------------------------------------------------- tax --
print("== tax ==")
s, b = req("POST", "/masterdata/tax", TOK,
           {"country_id": cid, "tax_name": "ZZTax", "tax_percentage": 18})
check("tax: create -> 201", s == 201, f"{s} {str(b)[:180]}")
tid = (b.get("data") or {}).get("id") if s == 201 else None
s, b = req("POST", "/masterdata/tax", TOK,
           {"country_id": cid, "tax_name": "ZZTax", "tax_percentage": 5})
check("tax: duplicate -> 409", s == 409, f"{s} {str(b)[:120]}")
s, b = req("PUT", "/masterdata/tax", TOK,
           {"id": tid, "country_id": cid, "tax_name": "ZZTaxEdited", "tax_percentage": 9})
check("tax: update -> 200", s == 200, f"{s} {str(b)[:160]}")
s, b = req("DELETE", f"/masterdata/tax/{tid}", TOK)
check("tax: delete -> 200", s == 200, f"{s} {str(b)[:120]}")

# --------------------------------------------------------------- room_types --
print("== room_types ==")
s, b = req("GET", "/masterdata/complementry", TOK)
comp = rows(b)
comp_id = str(comp[0]["id"]) if comp else ""
s, b = req("POST", "/masterdata/room_types", TOK,
           {"type_name": "ZZSuite", "complementry": comp_id,
            "room_cost": 1000, "bed_cost": 300, "daily_rate": 1200, "weekly_rate": 7000,
            "bed_only_rate": 900, "bed_breakfast_rate": 1100,
            "half_board_rate": 1400, "full_board_rate": 1700})
check("room_type: create -> 201", s == 201, f"{s} {str(b)[:200]}")
rtid = (b.get("data") or {}).get("id") if s == 201 else None
s, b = req("GET", "/masterdata/room_types", TOK)
check("room_type: in list", any(r.get("room_type_name") == "ZZSuite" for r in rows(b)),
      f"keys={list(rows(b)[0].keys()) if rows(b) else []}")
s, b = req("POST", "/masterdata/room_types", TOK, {"type_name": "ZZSuite", "complementry": comp_id,
                                            "room_cost": 1000, "bed_cost": 300})
check("room_type: duplicate -> 409", s == 409, f"{s} {str(b)[:120]}")
if rtid:
    s, b = req("DELETE", f"/masterdata/room_types/{rtid}", TOK)
    check("room_type: delete -> 200", s == 200, f"{s} {str(b)[:120]}")

# ------------------------------------------------------------------- tidy up --
s, b = req("GET", "/masterdata/discount", TOK)
for r in rows(b):
    if str(r.get("discount_name", "")).startswith("ZZ"):
        req("DELETE", f"/masterdata/discount/{r['id']}", TOK)
s, b = req("GET", "/masterdata/tax", TOK)
for r in rows(b):
    if str(r.get("tax_name", "")).startswith("ZZ"):
        req("DELETE", f"/masterdata/tax/{r['id']}", TOK)
if cid:
    s, b = req("DELETE", f"/masterdata/country_currency/{cid}", TOK)
    check("country: delete -> 200", s == 200, f"{s} {str(b)[:120]}")

print(f"\n{PASSES} passed, {len(FAILS)} failed")
for f in FAILS:
    print("  -", f)

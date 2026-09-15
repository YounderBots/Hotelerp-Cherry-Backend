# -*- coding: utf-8 -*-
"""Restaurant and Bar: order -> kitchen ticket -> bill -> payment, end to end.

Same shapes the SPA sends. Run from the repo root.
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
        print(f"  ok   {label}")
    else:
        FAILS.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")


def venue_flow(prefix, ticket_path, label, dine_in):
    print(f"\n======== {label} ========")

    s, b = req("GET", f"/{prefix}/table", TOK)
    tables = rows(b)
    check(f"{label}: tables load", s == 200 and len(tables) > 0, f"{s} {len(tables)}")
    free = [t for t in tables if t.get("table_status") != "Occupied"] or tables
    table_id = free[0]["id"]

    s, b = req("GET", f"/{prefix}/menu", TOK)
    menu = rows(b)
    check(f"{label}: menu loads", s == 200 and len(menu) > 0, f"{s} {len(menu)}")
    item = menu[0]

    s, b = req("GET", f"/{prefix}/payment_method", TOK)
    methods = rows(b)
    check(f"{label}: payment methods load", s == 200 and len(methods) > 0, f"{s} {len(methods)}")
    method_id = methods[0]["id"]

    # ---- create ------------------------------------------------------------
    s, b = req("POST", f"/{prefix}/order", TOK, {
        "order_type": dine_in, "table_id": table_id, "room_no": None,
        "guest_name": "Flow Tester", "guest_mobile": "9876500999", "no_of_guests": 2,
    })
    check(f"{label}: create order -> 201/200", s in (200, 201), f"{s} {str(b)[:200]}")
    order = (b.get("data") or {}) if s in (200, 201) else {}
    oid = order.get("id")
    if not oid:
        return

    s, b = req("POST", f"/{prefix}/order", TOK, {"order_type": dine_in, "table_id": 999999})
    check(f"{label}: unknown table refused", s >= 400, f"{s} {str(b)[:150]}")

    s, b = req("POST", f"/{prefix}/order", TOK, {"order_type": "Not A Type", "table_id": table_id})
    check(f"{label}: unknown order type refused", s >= 400, f"{s} {str(b)[:150]}")

    # ---- items -------------------------------------------------------------
    s, b = req("POST", f"/{prefix}/order/{oid}/items", TOK,
               {"items": [{"menu_id": item["id"], "variant_id": None,
                           "quantity": 2, "special_instructions": "no ice"}]})
    check(f"{label}: add item -> 200/201", s in (200, 201), f"{s} {str(b)[:200]}")

    s, b = req("POST", f"/{prefix}/order/{oid}/items", TOK,
               {"items": [{"menu_id": item["id"], "quantity": 0}]})
    check(f"{label}: zero quantity refused", s >= 400, f"{s} {str(b)[:150]}")
    s, b = req("POST", f"/{prefix}/order/{oid}/items", TOK,
               {"items": [{"menu_id": item["id"], "quantity": -3}]})
    check(f"{label}: negative quantity refused", s >= 400, f"{s} {str(b)[:150]}")
    s, b = req("POST", f"/{prefix}/order/{oid}/items", TOK,
               {"items": [{"menu_id": 999999, "quantity": 1}]})
    check(f"{label}: unknown menu item refused", s >= 400, f"{s} {str(b)[:150]}")

    s, b = req("GET", f"/{prefix}/order/{oid}", TOK)
    detail = (b.get("data") or {})
    items = detail.get("items") or []
    check(f"{label}: order carries its item", len(items) >= 1, f"{len(items)} items")
    check(f"{label}: line total is quantity x price",
          bool(items) and abs(float(items[0].get("total_price") or 0)
                              - float(items[0].get("unit_price") or 0)
                              * float(items[0].get("quantity") or 0)) < 0.02,
          str(items[0])[:200] if items else "")

    CHARGES = {"cgst_percentage": 2.5, "sgst_percentage": 2.5,
               "service_charge_percentage": 0, "discount_type": None, "discount_value": 0}

    # ---- an order the kitchen has not seen is not billable -----------------
    s, b = req("POST", f"/{prefix}/bill/generate/{oid}", TOK, CHARGES)
    check(f"{label}: unconfirmed order cannot be billed", s == 400, f"{s} {str(b)[:180]}")

    # ---- confirm -> kitchen ticket -----------------------------------------
    s, b = req("POST", f"/{prefix}/order/{oid}/confirm", TOK, {})
    check(f"{label}: confirm order", s in (200, 201), f"{s} {str(b)[:200]}")

    s, b = req("GET", f"/{prefix}/{ticket_path}", TOK)
    tickets = [t for t in rows(b) if str(t.get("order_id")) == str(oid)]
    check(f"{label}: confirming raised a kitchen ticket", len(tickets) >= 1,
          f"{len(rows(b))} tickets in all, {len(tickets)} for this order")

    # ---- money guards -------------------------------------------------------
    s, b = req("POST", f"/{prefix}/bill/generate/{oid}", TOK,
               {**CHARGES, "discount_type": "Flat", "discount_value": 999999})
    check(f"{label}: discount larger than the order refused", s == 400, f"{s} {str(b)[:180]}")
    s, b = req("POST", f"/{prefix}/bill/generate/{oid}", TOK,
               {**CHARGES, "discount_type": "Percentage", "discount_value": 500})
    check(f"{label}: discount over 100% refused", s == 400, f"{s} {str(b)[:180]}")
    s, b = req("POST", f"/{prefix}/bill/generate/{oid}", TOK, {**CHARGES, "cgst_percentage": -50})
    check(f"{label}: negative tax refused", s == 400, f"{s} {str(b)[:180]}")

    # ---- bill ---------------------------------------------------------------
    s, b = req("POST", f"/{prefix}/bill/generate/{oid}", TOK, CHARGES)
    check(f"{label}: generate bill -> 200/201", s in (200, 201), f"{s} {str(b)[:250]}")
    bill = (b.get("data") or {})
    bill_id = bill.get("id")
    check(f"{label}: bill has an id", bool(bill_id), str(bill)[:200])
    if not bill_id:
        return

    s, b = req("GET", f"/{prefix}/bill/{bill_id}", TOK)
    bill = (b.get("data") or {})
    net = float(bill.get("grand_total") or 0)
    print(f"       bill {bill.get('bill_no') or bill_id}: net {net}")
    check(f"{label}: bill is readable and has a total", s == 200 and net > 0, f"{s} {str(bill)[:220]}")

    s, b = req("POST", f"/{prefix}/bill/generate/{oid}", TOK, CHARGES)
    check(f"{label}: billing the same order twice refused", s >= 400, f"{s} {str(b)[:180]}")

    # ---- payment ------------------------------------------------------------
    s, b = req("POST", f"/{prefix}/bill/{bill_id}/payment", TOK,
               {"payment_method_id": method_id, "paid_amount": -5,
                "payment_reference": None, "remarks": None})
    check(f"{label}: negative payment refused", s >= 400, f"{s} {str(b)[:150]}")
    s, b = req("POST", f"/{prefix}/bill/{bill_id}/payment", TOK,
               {"payment_method_id": 999999, "paid_amount": net,
                "payment_reference": None, "remarks": None})
    check(f"{label}: unknown payment method refused", s >= 400, f"{s} {str(b)[:150]}")

    s, b = req("POST", f"/{prefix}/bill/{bill_id}/payment", TOK,
               {"payment_method_id": method_id, "paid_amount": net,
                "payment_reference": "FLOWTEST", "remarks": "flow test"})
    check(f"{label}: settle the bill -> 200/201", s in (200, 201), f"{s} {str(b)[:250]}")

    s, b = req("GET", f"/{prefix}/bill/{bill_id}", TOK)
    settled = (b.get("data") or {})
    print(f"       after payment: status={settled.get('payment_status') or settled.get('status')} "
          f"paid={settled.get('paid_amount')}")
    paid = sum(float(pmt.get("paid_amount") or 0) for pmt in (settled.get("payments") or []))
    check(f"{label}: bill records the payment", abs(paid - net) < 0.02,
          f"paid {paid} of {net}")
    check(f"{label}: bill reads as paid", settled.get("payment_status") == "Paid",
          str(settled.get("payment_status")))

    # ---- reports pick it up --------------------------------------------------
    s, b = req("GET", f"/{prefix}/reports/daily_sales", TOK)
    check(f"{label}: daily sales report -> 200", s == 200, f"{s} {str(b)[:150]}")
    s, b = req("GET", f"/{prefix}/reports/payment_mode", TOK)
    check(f"{label}: payment mode report -> 200", s == 200, f"{s} {str(b)[:150]}")

    return {"order_id": oid, "bill_id": bill_id}


made = {}
made["restaurant"] = venue_flow("restaurant", "kot", "Restaurant", "Dine-In")
made["bar"] = venue_flow("bar", "bot", "Bar", "At Table")

print(f"\n{PASSES} passed, {len(FAILS)} failed")
for f in FAILS:
    print("  -", f)
print("\ncreated:", made)

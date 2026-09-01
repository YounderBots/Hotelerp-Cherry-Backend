"""hotelerp_restaurant and hotelerp_bar: two outlets, seeded the same way.

The two schemas are near-mirrors of each other -- a kitchen or a station, a
category, an item, a floor, a table, a guest, an order, a bill -- so they share
one seeder parameterised by the handful of names and enum values that differ.

WHAT IS AND IS NOT SEEDED HERE
    Seeded: the catalogue and configuration an outlet cannot open without
    (kitchens/stations, categories, priced menu items WITH images, floors,
    tables, payment methods, settings), its guest book, its inventory, and a
    day's completed trade -- orders that became bills that were paid.

    The trade is deliberately modest and all CLOSED. Open orders would put the
    seeded property mid-service, which makes every screen's totals depend on
    when you happen to look at them; a settled day is reproducible and is what
    the billing and report screens are built to show.
"""

from __future__ import annotations

import datetime as dt
import uuid

from . import images as im
from .common import COMPANY, RNG, SYSTEM, at, day, insert, money, upload_dir

BRANCH = "1"


def _audit(created=None, **extra):
    """F&B tables carry branch_id alongside company_id."""
    row = {
        "status": "ACTIVE",
        "created_by": SYSTEM,
        "created_at": created or at(day(0), 9, 0),
        "updated_at": None,
        "updated_by": None,
        "company_id": COMPANY,
        "branch_id": BRANCH,
    }
    row.update(extra)
    return row


# ---------------------------------------------------------------------------
# Restaurant catalogue
# ---------------------------------------------------------------------------
R_KITCHENS = [
    (1, "KIT-MAIN", "Main Kitchen", "Main"),
    (2, "KIT-GRILL", "Grill Kitchen", "Grill"),
    (3, "KIT-DESS", "Dessert Kitchen", "Dessert"),
]

# (id, code, name, kitchen_id, order)
R_CATEGORIES = [
    (1, "CAT-STR", "Starters", 1, 1),
    (2, "CAT-SOUP", "Soups & Salads", 1, 2),
    (3, "CAT-MAIN", "Main Course", 1, 3),
    (4, "CAT-GRILL", "Tandoor & Grill", 2, 4),
    (5, "CAT-BRD", "Breads & Rice", 1, 5),
    (6, "CAT-DES", "Desserts", 3, 6),
]

# (name, category_id, price, veg, prep_minutes)
R_ITEMS = [
    ("Paneer Tikka", 1, 320, True, 18),
    ("Chicken 65", 1, 340, False, 16),
    ("Gobi Manchurian", 1, 260, True, 14),
    ("Prawn Koliwada", 1, 420, False, 18),
    ("Sweet Corn Soup", 2, 180, True, 10),
    ("Mulligatawny Soup", 2, 200, False, 12),
    ("Garden Green Salad", 2, 160, True, 6),
    ("Butter Chicken", 3, 480, False, 25),
    ("Paneer Butter Masala", 3, 380, True, 22),
    ("Chettinad Chicken Curry", 3, 460, False, 26),
    ("Dal Makhani", 3, 300, True, 20),
    ("Kerala Fish Curry", 3, 520, False, 24),
    ("Vegetable Biryani", 3, 340, True, 28),
    ("Hyderabadi Chicken Biryani", 3, 460, False, 32),
    ("Tandoori Chicken (Half)", 4, 420, False, 30),
    ("Seekh Kebab", 4, 380, False, 22),
    ("Tandoori Pomfret", 4, 620, False, 28),
    ("Grilled Vegetable Platter", 4, 340, True, 20),
    ("Butter Naan", 5, 70, True, 8),
    ("Garlic Naan", 5, 90, True, 8),
    ("Laccha Paratha", 5, 80, True, 9),
    ("Steamed Basmati Rice", 5, 150, True, 12),
    ("Gulab Jamun", 6, 140, True, 5),
    ("Rasmalai", 6, 160, True, 5),
    ("Chocolate Brownie", 6, 220, True, 8),
]

R_FLOORS = [
    (1, "FL-GRD", "Ground Floor", 1, "Restaurant", 8, 32),
    (2, "FL-FST", "First Floor", 2, "Restaurant", 6, 28),
    (3, "FL-TER", "Rooftop Terrace", 3, "Outdoor", 4, 16),
]

R_PAYMENTS = ["Cash", "Credit Card", "Debit Card", "UPI", "Room Charge"]

R_SETTINGS = [
    ("service_charge_percent", "10", "ServiceCharge", "Service charge added to dine-in bills"),
    ("default_tax_percent", "5", "Tax", "GST applied to restaurant bills"),
    ("opening_time", "07:00", "OperatingHours", "Kitchen opens"),
    ("closing_time", "23:30", "OperatingHours", "Last order"),
    ("bill_prefix", "RB", "Numbering", "Prefix for restaurant bill numbers"),
    ("order_prefix", "RO", "Numbering", "Prefix for restaurant order numbers"),
]

R_INVENTORY = [
    ("Basmati Rice", "Kg", 120), ("Paneer", "Kg", 340), ("Chicken", "Kg", 260),
    ("Prawns", "Kg", 620), ("Refined Oil", "Litre", 140), ("Wheat Flour", "Kg", 48),
    ("Onion", "Kg", 40), ("Tomato", "Kg", 36), ("Fresh Cream", "Litre", 220),
    ("Mixed Spices", "Kg", 480),
]

# ---------------------------------------------------------------------------
# Bar catalogue
# ---------------------------------------------------------------------------
B_STATIONS = [
    (1, "STN-BAR", "Main Bar"),
    (2, "STN-LNG", "Lounge Bar"),
]

B_CATEGORIES = [
    (1, "BC-SPI", "Spirits", 1, 1),
    (2, "BC-BEER", "Beer", 1, 2),
    (3, "BC-WINE", "Wine", 2, 3),
    (4, "BC-COCK", "Cocktails", 1, 4),
    (5, "BC-NON", "Non-Alcoholic", 2, 5),
]

B_ITEMS = [
    ("Single Malt 12 Yr (30ml)", 1, 650, 3),
    ("Blended Whisky (30ml)", 1, 380, 3),
    ("Premium Vodka (30ml)", 1, 340, 3),
    ("London Dry Gin (30ml)", 1, 360, 3),
    ("Dark Rum (30ml)", 1, 300, 3),
    ("Lager Pint", 2, 320, 2),
    ("Wheat Beer Pint", 2, 380, 2),
    ("Craft IPA Pint", 2, 420, 2),
    ("House Red (Glass)", 3, 450, 3),
    ("House White (Glass)", 3, 450, 3),
    ("Sparkling Wine (Glass)", 3, 620, 3),
    ("Old Fashioned", 4, 620, 6),
    ("Negroni", 4, 640, 5),
    ("Mojito", 4, 480, 5),
    ("Margarita", 4, 560, 5),
    ("Espresso Martini", 4, 660, 6),
    ("Virgin Mojito", 5, 260, 4),
    ("Fresh Lime Soda", 5, 180, 3),
]

B_FLOORS = [
    (1, "BF-MAIN", "Bar Level", 1, 6, 24),
    (2, "BF-LNG", "Lounge", 2, 4, 20),
]

B_PAYMENTS = ["Cash", "Credit Card", "Debit Card", "UPI", "Room Charge"]

B_INVENTORY = [
    ("Single Malt 12 Yr", "Bottle", 6800), ("Blended Whisky", "Bottle", 2400),
    ("Premium Vodka", "Bottle", 2200), ("London Dry Gin", "Bottle", 2600),
    ("Dark Rum", "Bottle", 1800), ("Lager Keg", "Litre", 340),
    ("Red Wine", "Bottle", 2800), ("White Wine", "Bottle", 2600),
    ("Tonic Water", "Can", 90), ("Fresh Lime", "Nos", 8),
]

GUEST_NAMES = [
    ("Deepak", "Anand", "Regular"), ("Sridevi", "Raman", "VIP"),
    ("Michael", "Fernandes", "Walk-In"), ("Aisha", "Rahman", "Regular"),
    ("Ganesh", "Iyer", "VIP"), ("Sarah", "Thomas", "Walk-In"),
    ("Rohan", "Mehta", "Hotel Guest"), ("Priya", "Nair", "Hotel Guest"),
]


def _menu_rows(items, image_dir, *, bar: bool):
    """Menu items, each with a generated tile. Shared shape, two column sets."""
    rows = []
    for i, entry in enumerate(items, start=1):
        if bar:
            name, cat, price, prep = entry
            veg, station = True, B_CATEGORIES[cat - 1][3]
            category_name = B_CATEGORIES[cat - 1][2]
        else:
            name, cat, price, veg, prep = entry
            station = R_CATEGORIES[cat - 1][3]
            category_name = R_CATEGORIES[cat - 1][2]

        fname = im.hex_name("jpg")
        im.save(im.menu_image(name, category_name, veg=veg), image_dir, fname)
        image_path = f"/templates/static/upload_image/{fname}"

        base = dict(
            id=i,
            item_code=("BAR" if bar else "RES") + f"-{i:03d}",
            item_name=name,
            description=f"{category_name} — prepared to order.",
            category_id=cat,
            sub_category_id=None,
            price=float(price),
            cost_price=money(price * 0.38),
            tax_percentage=5.0,
            service_charge_applicable=1,
            preparation_time=prep,
            availability_status="Available",
            dietary_tags=None,
            has_variants=0,
            item_image=image_path,
            happy_hour_eligible=1 if (bar and cat in (2, 4)) else 0,
        )
        if bar:
            base["station_id"] = station
        else:
            base["kitchen_id"] = station
            base["is_veg"] = 1 if veg else 0
        rows.append({**base, **_audit()})
    return rows


def seed_restaurant(conn) -> dict:
    image_dir = upload_dir("hotelerp_restaurant", "upload_image")

    insert(conn, "kitchen", [
        dict(id=i, kitchen_code=c, kitchen_name=n, kitchen_type=t,
             printer_name=f"{c}-PRN", is_active=1, **_audit())
        for i, c, n, t in R_KITCHENS])

    insert(conn, "menu_category", [
        dict(id=i, category_code=c, category_name=n, description=f"{n} menu section",
             kitchen_id=k, display_order=o, **_audit())
        for i, c, n, k, o in R_CATEGORIES])

    menu = _menu_rows(R_ITEMS, image_dir, bar=False)
    insert(conn, "restaurant_menu", menu)

    insert(conn, "restaurant_floor", [
        dict(id=i, floor_code=c, floor_name=n, floor_number=num, floor_type=t,
             description=f"{n} seating", total_tables=tables, total_capacity=cap,
             layout_json=None, color_code="#850126", is_open=1, **_audit())
        for i, c, n, num, t, tables, cap in R_FLOORS])

    tables, tid = [], 1
    for floor_id, code, _n, _num, ftype, count, _cap in R_FLOORS:
        for seat in range(1, count + 1):
            tables.append(dict(
                id=tid, table_code=f"{code}-T{seat:02d}",
                table_name=f"Table {tid}", table_number=tid,
                floor_id=floor_id, floor_code=code,
                table_type="VIP" if seat == 1 and floor_id == 3 else "Standard",
                seating_capacity=4 if seat % 3 else 2,
                section="Outdoor" if ftype == "Outdoor" else "Restaurant",
                current_order_id=None, server_id=None, server_name=None,
                position_x=float(60 * (seat % 4)), position_y=float(60 * (seat // 4)),
                shape="round" if seat % 2 else "square", color_code="#E5E7EB",
                table_status="Available", is_mergeable=1, **_audit()))
            tid += 1
    insert(conn, "restaurant_table", tables)

    insert(conn, "payment_method", [
        dict(id=i, method_name=n, **_audit())
        for i, n in enumerate(R_PAYMENTS, start=1)])

    insert(conn, "restaurant_settings", [
        dict(id=i, setting_key=k, setting_value=v, setting_group=g,
             description=d, **_audit())
        for i, (k, v, g, d) in enumerate(R_SETTINGS, start=1)])

    insert(conn, "guest", [
        dict(id=i, guest_code=f"RG-{i:04d}", first_name=f, last_name=l,
             mobile=f"98401{20000 + i * 7:05d}"[:10],
             email=f"{f.lower()}.{l.lower()}@example.com",
             guest_type=t, **_audit())
        for i, (f, l, t) in enumerate(GUEST_NAMES, start=1)])

    insert(conn, "inventory_item", [
        dict(id=i, item_code=f"RIN-{i:03d}", item_name=n, category="Kitchen Store",
             unit=u, min_stock_level=float(10 + i),
             is_perishable=1 if u in ("Kg", "Litre") else 0, **_audit())
        for i, (n, u, _c) in enumerate(R_INVENTORY, start=1)])

    insert(conn, "inventory_stock", [
        dict(id=i, inventory_item_id=i, kitchen_id=1,
             available_quantity=float(40 + i * 6), last_updated_date=day(-1),
             **_audit())
        for i, (_n, _u, _c) in enumerate(R_INVENTORY, start=1)])

    return _trade(conn, menu, tables, len(R_PAYMENTS), prefix="R",
                  order_table="restaurant_order", item_table="restaurant_order_item",
                  bill_table="restaurant_bill", bill_item_table="restaurant_bill_item",
                  pay_table="restaurant_bill_payment", bar=False)


def seed_bar(conn) -> dict:
    image_dir = upload_dir("hotelerp_bar", "upload_image")

    insert(conn, "bar_station", [
        dict(id=i, station_code=c, station_name=n, printer_name=f"{c}-PRN",
             is_active=1, **_audit())
        for i, c, n in B_STATIONS])

    insert(conn, "bar_menu_category", [
        dict(id=i, category_code=c, category_name=n, description=f"{n} selection",
             station_id=s, display_order=o, **_audit())
        for i, c, n, s, o in B_CATEGORIES])

    menu = _menu_rows(B_ITEMS, image_dir, bar=True)
    insert(conn, "bar_menu_item", menu)

    insert(conn, "bar_floor", [
        dict(id=i, floor_code=c, floor_name=n, floor_number=num,
             description=f"{n} seating", total_tables=t, total_capacity=cap,
             layout_json=None, color_code="#850126", is_open=1, **_audit())
        for i, c, n, num, t, cap in B_FLOORS])

    tables, tid = [], 1
    for floor_id, code, _n, _num, count, _cap in B_FLOORS:
        for seat in range(1, count + 1):
            tables.append(dict(
                id=tid, table_code=f"{code}-T{seat:02d}",
                table_name=f"{'Counter' if seat == 1 else 'Table'} {tid}",
                table_number=tid, floor_id=floor_id, floor_code=code,
                table_type="Counter" if seat == 1 else
                           ("VIP Lounge" if floor_id == 2 and seat == 2 else "Table"),
                seating_capacity=2 if seat % 2 else 4,
                current_order_id=None, server_id=None, server_name=None,
                table_status="Available", **_audit()))
            tid += 1
    insert(conn, "bar_table", tables)

    insert(conn, "bar_payment_method", [
        dict(id=i, method_name=n, **_audit())
        for i, n in enumerate(B_PAYMENTS, start=1)])

    insert(conn, "bar_guest", [
        dict(id=i, guest_code=f"BG-{i:04d}", first_name=f, last_name=l,
             mobile=f"98402{30000 + i * 11:05d}"[:10],
             email=f"{f.lower()}.{l.lower()}@example.com",
             guest_type=t, **_audit())
        for i, (f, l, t) in enumerate(GUEST_NAMES[:6], start=1)])

    insert(conn, "bar_inventory_item", [
        dict(id=i, item_code=f"BIN-{i:03d}", item_name=n, category="Bar Store",
             unit=u, min_stock_level=float(6 + i),
             is_perishable=1 if u == "Nos" else 0, **_audit())
        for i, (n, u, _c) in enumerate(B_INVENTORY, start=1)])

    insert(conn, "bar_inventory_stock", [
        dict(id=i, inventory_item_id=i, station_id=1,
             available_quantity=float(18 + i * 3), last_updated_date=day(-1),
             **_audit())
        for i, (_n, _u, _c) in enumerate(B_INVENTORY, start=1)])

    return _trade(conn, menu, tables, len(B_PAYMENTS), prefix="B",
                  order_table="bar_order", item_table="bar_order_item",
                  bill_table="bar_bill", bill_item_table="bar_bill_item",
                  pay_table="bar_bill_payment", bar=True)


def _trade(conn, menu, tables, n_payments, *, prefix, order_table, item_table,
           bill_table, bill_item_table, pay_table, bar):
    """A settled day's trade: orders served, billed and paid in full.

    Every bill's grand total is derived from its own lines, so the billing
    screen, the payment rows and the day's report all agree.
    """
    orders, order_items, bills, bill_items, payments = [], [], [], [], []
    oi_id = bi_id = pay_id = 1
    tax_pct, service_pct = 5.0, 10.0

    for n in range(1, 9):
        served_on = day(-(n % 3))
        hour = 12 + (n % 8)
        table = tables[(n * 3) % len(tables)]
        picks = RNG.sample(menu, k=3 + (n % 3))

        subtotal = 0.0
        lines = []
        for pick in picks:
            qty = 1 + (n + pick["id"]) % 3
            amount = money(pick["price"] * qty)
            subtotal = money(subtotal + amount)
            lines.append((pick, qty, amount))

        service = money(subtotal * service_pct / 100.0)
        tax = money((subtotal + service) * tax_pct / 100.0)
        grand = money(subtotal + service + tax)

        order_number = f"{prefix}O-{served_on:%Y%m%d}-{n:03d}"
        bill_number = f"{prefix}B-{served_on:%Y%m%d}-{n:03d}"

        orders.append(dict(
            id=n, order_number=order_number, order_date=served_on,
            order_time=dt.time(hour, 15), table_id=table["id"],
            order_type=("At Table" if bar else "Dine-In"),
            order_status="Completed", payment_status="Paid",
            sub_total=subtotal, tax_amount=tax, service_charge=service,
            discount_amount=0.0, grand_total=grand,
            token=str(uuid.uuid4()),
            **_audit(created=at(served_on, hour, 15))))

        for pick, qty, amount in lines:
            item = dict(
                id=oi_id, order_id=n, menu_id=pick["id"], quantity=qty,
                price=pick["price"], item_status="Served",
                **_audit(created=at(served_on, hour, 20)))
            if bar:
                item["station_id"] = pick["station_id"]
            else:
                item["kitchen_id"] = pick["kitchen_id"]
            order_items.append(item)

            bill_items.append(dict(
                id=bi_id, bill_id=n, order_item_id=oi_id, menu_id=pick["id"],
                item_name=pick["item_name"], quantity=qty,
                rate=pick["price"], amount=amount,
                **_audit(created=at(served_on, hour, 55))))
            oi_id += 1
            bi_id += 1

        # GST is levied as CGST + SGST in halves for an intra-state sale, which
        # is what the bill stores and what a compliant invoice has to print.
        # IGST stays zero: it applies only to inter-state supply, which a
        # restaurant serving at its own table never is.
        half = money(tax / 2)
        bill = dict(
            id=n, bill_number=bill_number, bill_date=served_on,
            bill_time=dt.time(hour, 55), order_id=n, order_number=order_number,
            table_id=table["id"], table_code=table["table_code"],
            guest_id=None, guest_name=None, guest_mobile=None,
            sub_total=subtotal,
            cgst_percentage=tax_pct / 2, cgst_amount=half,
            sgst_percentage=tax_pct / 2, sgst_amount=money(tax - half),
            service_charge_percentage=service_pct, service_charge_amount=service,
            discount_type=None, discount_value=0.0, discount_amount=0.0,
            round_off=0.0, grand_total=grand,
            bill_status="Paid", payment_status="Paid", remarks=None,
            token=str(uuid.uuid4()),
            **_audit(created=at(served_on, hour, 55)))
        if not bar:
            # Only the restaurant can post a bill to a room, and only it
            # carries IGST -- the bar bills at its own counter, always
            # intra-state, so those columns do not exist on that table.
            bill["room_no"] = None
            bill["igst_percentage"] = 0.0
            bill["igst_amount"] = 0.0
        bills.append(bill)

        payments.append(dict(
            id=pay_id, bill_id=n, payment_method_id=1 + (n % n_payments),
            paid_amount=grand, payment_date=served_on,
            payment_time=dt.time(hour, 58), payment_status="Success",
            **_audit(created=at(served_on, hour, 58))))
        pay_id += 1

    insert(conn, order_table, orders)
    insert(conn, item_table, order_items)
    insert(conn, bill_table, bills)
    insert(conn, bill_item_table, bill_items)
    insert(conn, pay_table, payments)

    return {"menu_items": len(menu), "tables": len(tables), "orders": len(orders),
            "bills": len(bills), "revenue": money(sum(b["grand_total"] for b in bills))}

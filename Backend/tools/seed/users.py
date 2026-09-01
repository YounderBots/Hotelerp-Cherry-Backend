"""hotelerp_users: roles, navigation, permissions and staff.

THE NAVIGATION IS THE CONTRACT
    `menus` / `submenus` are not decoration. Three things read them:

      * the sidebar the user navigates by;
      * `role_permissions`, which is keyed on menu and submenu ids;
      * `Backend/tools/build_rbac_map.py`, which reads the live menu table to
        decide which page grants which endpoint. A menu path that matches no
        route in App.jsx therefore produces a permission nobody can hold, and a
        missing menu produces an endpoint nobody can call.

    So every link below is checked against App.jsx at seed time (see
    `verify_links`) and the seed refuses to run if one does not resolve. The
    previous dataset carried five dead links -- a duplicate "MasterData" menu
    at /masters, a "Roles" entry filed under Reservation pointing at
    /master/roles, /kot/bar, /staff_master and /staff_planning -- all of which
    rendered as sidebar items that led to a Not Found page.
"""

from __future__ import annotations

import os
import re

import bcrypt

from . import images as im
from .common import ACTIVE, COMPANY, SYSTEM, ROOT, at, audit, day, insert, upload_dir

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
# Five roles that describe how a hotel is actually staffed. Every one is ACTIVE:
# the previous dataset shipped two INACTIVE roles ("Front Office Manager",
# "Camera Man") that could be assigned to nobody and explained nothing.
ROLES = [
    (1, "Admin", "Full access to every module, including Master Data and HRM."),
    (2, "Front Office Manager", "Reservations, night audit, guest enquiry and reporting."),
    (3, "Front Desk", "Day-to-day reservations: book, check in, take payment, check out."),
    (4, "Housekeeping", "Room status, task assignment and incident logging."),
    (5, "Food & Beverage", "Restaurant and bar: menu, orders, kitchen and billing."),
]

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
# (id, name, link, icon, order). A blank link is a parent that only groups
# submenus -- the sidebar renders it as an expander, never as a destination.
MENUS = [
    (1, "Dashboard", "/dashboard", "dashboard", 1),
    (2, "Reservation", "/reservation", "reservation", 2),
    (3, "Night Audit", "", "night-auditing", 3),
    (4, "Guest Enquiry", "/guest_enquiry", "guest-enquiry", 4),
    (5, "House Keeper", "", "house-keeper", 5),
    (6, "HRM", "", "hrm", 6),
    (7, "Restaurant", "", "restaurant", 7),
    (8, "Bar", "", "bar", 8),
    (9, "Master Data", "", "master-data", 9),
]

# (id, menu_id, name, link, order)
SUBMENUS = [
    # Reservation
    (101, 2, "Add New Reservation", "/add_new_reservation", 1),
    (102, 2, "Booking", "/booking", 2),
    (103, 2, "Room View", "/room_view", 3),
    (104, 2, "Reservation View", "/reservation_view", 4),
    # Night Audit
    (111, 3, "Night Audit", "/night_audit", 1),
    (112, 3, "User Reserved Details", "/user_reserved_details", 2),
    (113, 3, "Room Booked Details", "/room_booked_details", 3),
    (114, 3, "Settlement Summary", "/settlement_summary", 4),
    # House Keeper
    (121, 5, "Task Assign", "/task_assign", 1),
    (122, 5, "Room Incident Log", "/room_incident_log", 2),
    # HRM
    (131, 6, "Employee", "/employee", 1),
    (132, 6, "User", "/user", 2),
    (133, 6, "Roles", "/roles", 3),
    (134, 6, "Department", "/department", 4),
    (135, 6, "Designation", "/designation", 5),
    (136, 6, "Shift", "/shift", 6),
    (137, 6, "Restaurant Roster", "/restaurant_roster", 7),
    (138, 6, "Restaurant Shift Planning", "/restaurant_shift_planning", 8),
    (139, 6, "Bar Roster", "/bar_roster", 9),
    (140, 6, "Bar Shift Planning", "/bar_shift_planning", 10),
    # Restaurant
    (151, 7, "Menu Management", "/menus", 1),
    (152, 7, "Combo / Package Deals", "/combo_deals", 2),
    (153, 7, "Floor Layout", "/floor_layout", 3),
    (154, 7, "Table Master", "/table_master", 4),
    (155, 7, "Order Management", "/orders", 5),
    (156, 7, "Table Reservation", "/table_reservation", 6),
    (157, 7, "Main Kitchen", "/kot/main_kitchen", 7),
    (158, 7, "Grill Kitchen", "/kot/grill", 8),
    (159, 7, "Dessert Kitchen", "/kot/dessert", 9),
    (160, 7, "Billing & Payments", "/billing_payments", 10),
    (161, 7, "Inventory Control", "/stock", 11),
    (162, 7, "Recipe Management", "/recipe_management", 12),
    (163, 7, "Guest Management", "/guest_management", 13),
    (164, 7, "Report & Analytics", "/reports_analytics", 14),
    # Bar
    (171, 8, "Menu Management", "/bar_menus", 1),
    (172, 8, "Floor Layout", "/bar_floor_layout", 2),
    (173, 8, "Table Master", "/bar_table_master", 3),
    (174, 8, "Order Management", "/bar_orders", 4),
    (175, 8, "Station Display", "/bar_station", 5),
    (176, 8, "Billing & Payments", "/bar_billing_payments", 6),
    (177, 8, "Stock", "/bar_stock", 7),
    (178, 8, "Recipe Management", "/bar_recipe_management", 8),
    (179, 8, "Guest Management", "/bar_guest_management", 9),
    (180, 8, "Report & Analytics", "/bar_reports_analytics", 10),
    # Master Data
    (191, 9, "Facilities", "/facilities", 1),
    (192, 9, "Room Type", "/room_type", 2),
    (193, 9, "Bed Type", "/bed_type", 3),
    (194, 9, "Hall / Floor", "/hall_floor", 4),
    (195, 9, "Rooms", "/rooms", 5),
    (196, 9, "Discount Type", "/discount_type", 6),
    (197, 9, "Tax Types", "/tax_types", 7),
    (198, 9, "Payment Methods", "/payment_methods", 8),
    (199, 9, "Identification Proof", "/identification_proof", 9),
    (200, 9, "Currency & Country", "/currency_country", 10),
    (201, 9, "HSK Task Type", "/hsk_task_type", 11),
    (202, 9, "Complementary", "/complementary", 12),
    (203, 9, "Reservation Status", "/reservation_status", 13),
]

# ---------------------------------------------------------------------------
# Who can do what
# ---------------------------------------------------------------------------
# Per role: which menus it can reach, and what it may do there.
#   "*"  every action (view, add, edit, delete)
#   "rw" view, add, edit -- but never delete
#   "r"  view only
#
# Deliberately NOT everyone-gets-everything. The gateway authorises against
# exactly this, so a role that should not be able to delete a reservation has
# to actually lack the bit -- and the RBAC tests assert that property.
ROLE_ACCESS = {
    1: {"__all__": "*"},                                  # Admin
    2: {                                                  # Front Office Manager
        1: "r", 2: "*", 3: "rw", 4: "rw", 5: "r", 9: "r",
    },
    3: {                                                  # Front Desk
        1: "r", 2: "rw", 4: "rw",
    },
    4: {                                                  # Housekeeping
        1: "r", 5: "rw", 2: "r",
    },
    5: {                                                  # Food & Beverage
        1: "r", 7: "rw", 8: "rw",
    },
}

BITS = {
    "*": (1, 1, 1, 1),
    "rw": (1, 1, 1, 0),
    "r": (1, 0, 0, 0),
}

# ---------------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------------
DEPARTMENTS = [
    "Front Office", "Housekeeping", "Food & Beverage", "Kitchen",
    "Maintenance", "Accounts", "Human Resources", "Security",
]

DESIGNATIONS = [
    "General Manager", "Front Office Manager", "Front Desk Executive",
    "Reservation Executive", "Housekeeping Supervisor", "Room Attendant",
    "Restaurant Manager", "Chef", "Bartender", "Accountant",
]

SHIFTS = [
    ("Morning", "06:00", "14:00"),
    ("Evening", "14:00", "22:00"),
    ("Night", "22:00", "06:00"),
    ("General", "09:00", "18:00"),
]

# (user_code, username, first, last, dept_id, desig_id, role_id, shift_id, gender, mobile)
STAFF = [
    ("EMP001", "admin", "Aarav", "Sharma", 1, 1, 1, 4, "Male", "9840100001"),
    ("EMP002", "priya.menon", "Priya", "Menon", 1, 2, 2, 4, "Female", "9840100002"),
    ("EMP003", "rahul.nair", "Rahul", "Nair", 1, 3, 3, 1, "Male", "9840100003"),
    ("EMP004", "divya.rao", "Divya", "Rao", 1, 4, 3, 2, "Female", "9840100004"),
    ("EMP005", "imran.khan", "Imran", "Khan", 2, 5, 4, 1, "Male", "9840100005"),
    ("EMP006", "lakshmi.iyer", "Lakshmi", "Iyer", 2, 6, 4, 2, "Female", "9840100006"),
    ("EMP007", "vikram.singh", "Vikram", "Singh", 3, 7, 5, 2, "Male", "9840100007"),
    ("EMP008", "sunita.patel", "Sunita", "Patel", 4, 8, 5, 1, "Female", "9840100008"),
    ("EMP009", "joseph.dsouza", "Joseph", "D'Souza", 3, 9, 5, 2, "Male", "9840100009"),
    ("EMP010", "meera.krishnan", "Meera", "Krishnan", 6, 10, 2, 4, "Female", "9840100010"),
]

# Every seeded account uses this password. Printed by the seed so it cannot
# become folklore, and hashed with bcrypt because that is what
# UserServices /verify_credentials checks against.
DEMO_PASSWORD = "Hotel@2026"


def verify_links() -> None:
    """Refuse to seed navigation that points at routes the app does not have.

    A dead sidebar link is not a cosmetic problem: role_permissions rows hang
    off it, and build_rbac_map turns menu paths into the grants the gateway
    authorises with. Catching it here is the difference between "this menu item
    404s" and "this endpoint is denied to everyone in production".
    """
    app = os.path.join(ROOT, "Frontend", "src", "App.jsx")
    with open(app, encoding="utf-8") as fh:
        routes = set(re.findall(r'path="([^"]+)"', fh.read()))

    dead = [(f"menu {mid}", name, link) for mid, name, link, _i, _o in MENUS
            if link and link not in routes]
    dead += [(f"submenu {sid}", name, link) for sid, _m, name, link, _o in SUBMENUS
             if link not in routes]
    if dead:
        lines = "\n".join(f"    {w:<14} {n:<28} {l}" for w, n, l in dead)
        raise SystemExit(
            f"Refusing to seed: {len(dead)} navigation link(s) match no route "
            f"in App.jsx.\n{lines}\n"
            "Fix the link or add the route before seeding."
        )


def seed(conn) -> None:
    verify_links()

    insert(conn, "department", [
        dict(id=i, Department_Name=name, **audit())
        for i, name in enumerate(DEPARTMENTS, start=1)
    ])
    insert(conn, "designation", [
        dict(id=i, Designation_Name=name, **audit())
        for i, name in enumerate(DESIGNATIONS, start=1)
    ])
    insert(conn, "shift", [
        dict(id=i, Shift_Name=n, Start_Time=s, End_Time=e, **audit())
        for i, (n, s, e) in enumerate(SHIFTS, start=1)
    ])
    insert(conn, "roles", [
        dict(id=i, role_name=n, description=d, **audit()) for i, n, d in ROLES
    ])
    insert(conn, "menus", [
        {"id": i, "menu_name": n, "menu_link": l, "menu_icon": ic, "order": o, **audit()}
        for i, n, l, ic, o in MENUS
    ])
    insert(conn, "submenus", [
        {"id": i, "menu_id": str(m), "submenu_name": n, "submenu_link": l,
         "order": o, **audit()}
        for i, m, n, l, o in SUBMENUS
    ])

    # --- permissions -------------------------------------------------------
    by_menu: dict[int, list[int]] = {}
    for sid, mid, *_ in SUBMENUS:
        by_menu.setdefault(mid, []).append(sid)

    perms, pid = [], 1
    for role_id, access in ROLE_ACCESS.items():
        for menu_id, *_ in MENUS:
            level = access.get("__all__") or access.get(menu_id)
            if not level:
                continue
            view, create, edit, delete = BITS[level]
            perms.append(dict(
                id=pid, role_id=str(role_id), menu_id=str(menu_id), submenu_id=None,
                view_permission=view, create_permission=create,
                edit_permission=edit, delete_permission=delete, **audit()))
            pid += 1
            for sub_id in by_menu.get(menu_id, []):
                perms.append(dict(
                    id=pid, role_id=str(role_id), menu_id=str(menu_id),
                    submenu_id=str(sub_id),
                    view_permission=view, create_permission=create,
                    edit_permission=edit, delete_permission=delete, **audit()))
                pid += 1
    insert(conn, "role_permissions", perms)

    # --- staff, each with a real photo file --------------------------------
    photo_dir = upload_dir("hotelerp_users", "users")
    hashed = bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt()).decode()

    rows = []
    for i, (code, username, first, last, dept, desig, role, shift, gender, mobile) \
            in enumerate(STAFF, start=1):
        fname = im.user_name("png")
        im.save(im.avatar_image(first, last), photo_dir, fname)
        rows.append(dict(
            id=i,
            User_Code=code,
            Photo=f"/templates/static/users/{fname}",
            username=username,
            First_Name=first,
            Last_Name=last,
            Personal_Email=f"{username}@example.com",
            Company_Email=f"{username}@cherryhotel.example",
            Password=hashed,
            Mobile=mobile,
            Alternative_Mobile="",
            D_O_B=f"19{80 + i % 15}-0{1 + i % 9}-1{i % 9}",
            Gender=gender,
            Marital_Status="Single" if i % 3 else "Married",
            Address=f"{10 + i} Anna Salai",
            City="Chennai",
            State="Tamil Nadu",
            Postal_Code="600002",
            Country="India",
            Department_ID=str(dept),
            Designation_ID=str(desig),
            Role_ID=str(role),
            Shift_ID=str(shift),
            Date_Of_Joining=str(day(-400 + i * 20)),
            Experience=f"{1 + i % 9} years",
            Salary_Details=str(25000 + i * 3500),
            Register_Code=f"REG{1000 + i}",
            Emergency_Name=f"{last} Family",
            Emergency_Contact=f"98401100{i:02d}",
            Emergency_Relationship="Spouse" if i % 3 == 0 else "Parent",
            Acknowledgment_of_Hotel_Policies=1,
            **audit(created=at(day(-400 + i * 20))),
        ))
    insert(conn, "users", rows)
    return {"password": DEMO_PASSWORD, "staff": len(rows), "permissions": len(perms)}

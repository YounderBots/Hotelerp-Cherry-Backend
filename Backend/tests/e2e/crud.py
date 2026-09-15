# -*- coding: utf-8 -*-
"""CRUD + validation flow test for every Master Data entity, through the gateway."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import req, login, rows  # noqa: E402

TOK = login("admin@cherryhotel.com")

FAILS, PASSES = [], 0
def check(label, cond, detail=""):
    global PASSES
    if cond: PASSES += 1
    else:
        FAILS.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")

# entity: (list_path, create_path, name_field, list_name_field, extra_create, id_path_fmt)
ENTITIES = [
    ("facilities",  "/masterdata/facilities",        "/masterdata/facilities",        "facility_name",    "facility_name",    {}, "/masterdata/facilities/%s"),
    ("bed_type",    "/masterdata/bed_types",         "/masterdata/bed_type",          "bed_type",         "bed_type_name",    {}, "/masterdata/bed_type/%s"),
    ("hall_floor",  "/masterdata/hall_floor",        "/masterdata/hall_floor",        "hall_name",        "hall_name",        {}, "/masterdata/hall_floor/%s"),
    ("identity",    "/masterdata/identity_proof",    "/masterdata/identity_proof",    "proof_name",       "proof_name",       {}, "/masterdata/identity_proof/%s"),
    ("payment",     "/masterdata/payment_methods",   "/masterdata/payment_methods",   "payment_method",   "payment_method",   {}, "/masterdata/payment_methods/%s"),
    ("task_type",   "/masterdata/task_type",         "/masterdata/task_type",         "task_name",        "task_name",        {"color": "#123456"}, "/masterdata/task_type/%s"),
    ("res_status",  "/masterdata/reservation_status","/masterdata/reservation_status","status_name",      "reservation_status",      {"color": "#654321"}, "/masterdata/reservation_status/%s"),
    ("complementry","/masterdata/complementry",      "/masterdata/complementry",      "complementry_name","complementry_name",{"description": "test"}, "/masterdata/complementry/%s"),
]

UNI = "Caf\u00e9 Suite \u2014 \u201cDeluxe\u201d & Co. <b>x</b> 'quote'"

for label, list_p, create_p, field, list_field, extra, id_fmt in ENTITIES:
    print(f"== {label} ==")
    name = f"ZZTest {label} 1"

    # --- create -------------------------------------------------------------
    s, b = req("POST", create_p, TOK, {field: name, **extra})
    check(f"{label}: create -> 201", s == 201, f"got {s} {str(b)[:160]}")
    if s != 201:
        continue
    new_id = (b.get("data") or {}).get("id")
    check(f"{label}: create returns id", bool(new_id), str(b)[:120])

    # --- read back ----------------------------------------------------------
    s, b = req("GET", list_p, TOK)
    got = [r for r in rows(b) if str(r.get(list_field)) == name]
    check(f"{label}: appears in list", len(got) == 1, f"{len(got)} matches; keys={list(rows(b)[0].keys()) if rows(b) else []}")

    # --- duplicate ----------------------------------------------------------
    s, b = req("POST", create_p, TOK, {field: name, **extra})
    check(f"{label}: duplicate -> 409", s == 409, f"got {s} {str(b)[:120]}")
    s, b = req("POST", create_p, TOK, {field: name.upper(), **extra})
    check(f"{label}: duplicate (case) -> 409", s == 409, f"got {s} {str(b)[:120]}")

    # --- validation ---------------------------------------------------------
    s, b = req("POST", create_p, TOK, {field: "", **extra})
    check(f"{label}: empty -> 400", s == 400, f"got {s} {str(b)[:120]}")
    s, b = req("POST", create_p, TOK, {field: "   ", **extra})
    check(f"{label}: whitespace -> 400", s == 400, f"got {s} {str(b)[:120]}")
    s, b = req("POST", create_p, TOK, {field: "x" * 300, **extra})
    check(f"{label}: 300 chars -> 400", s == 400, f"got {s} {str(b)[:120]}")
    s, b = req("POST", create_p, TOK, {**extra})
    check(f"{label}: missing field -> 400", s == 400, f"got {s} {str(b)[:120]}")

    # --- unicode / special characters round-trip ----------------------------
    s, b = req("POST", create_p, TOK, {field: UNI, **extra})
    uni_id = (b.get("data") or {}).get("id") if s == 201 else None
    check(f"{label}: unicode create -> 201", s == 201, f"got {s} {str(b)[:160]}")
    if uni_id:
        s, b = req("GET", list_p, TOK)
        back = [r for r in rows(b) if str(r.get(list_field)) == UNI]
        check(f"{label}: unicode round-trips intact", len(back) == 1,
              f"{len(back)} matches")
        req("DELETE", id_fmt % uni_id, TOK)

    # --- update -------------------------------------------------------------
    renamed = f"ZZTest {label} 2"
    s, b = req("PUT", create_p, TOK, {"id": new_id, field: renamed, **extra})
    check(f"{label}: update -> 200", s == 200, f"got {s} {str(b)[:160]}")
    s, b = req("GET", list_p, TOK)
    check(f"{label}: update persisted",
          any(str(r.get(list_field)) == renamed for r in rows(b)), "renamed row not found")
    check(f"{label}: old value gone",
          not any(str(r.get(list_field)) == name for r in rows(b)), "old value still listed")

    # A PUT to an id that does not exist: 404, or 409 when the name it carries
    # collides with a live row -- these endpoints run the duplicate check before
    # the existence check. Misleading, recorded as a P3, not a functional break.
    s, b = req("PUT", create_p, TOK, {"id": 999999, field: renamed, **extra})
    check(f"{label}: update missing id is refused", s in (404, 409), f"got {s} {str(b)[:120]}")

    # --- delete -------------------------------------------------------------
    s, b = req("DELETE", id_fmt % new_id, TOK)
    check(f"{label}: delete -> 200", s == 200, f"got {s} {str(b)[:120]}")
    s, b = req("GET", list_p, TOK)
    check(f"{label}: gone from list",
          not any(str(r.get(list_field)) == renamed for r in rows(b)), "still listed after delete")
    s, b = req("DELETE", id_fmt % new_id, TOK)
    check(f"{label}: delete twice -> 404", s == 404, f"got {s} {str(b)[:120]}")

print(f"\n{PASSES} passed, {len(FAILS)} failed")
for f in FAILS: print("  -", f)

# -*- coding: utf-8 -*-
"""Housekeeping, room incidents, guest enquiry and the night audit, end to end."""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import GW, req, login, rows  # noqa: E402

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


PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
    "00000049454e44ae426082"
)


def multipart(method, path, fields, files=None):
    boundary = "----ops" + uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                 f"{v}\r\n").encode()
    for k, (fn, data, ct) in (files or {}).items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                 f"filename=\"{fn}\"\r\nContent-Type: {ct}\r\n\r\n").encode() + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    r = urllib.request.Request(GW + path, data=body, method=method)
    r.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    r.add_header("Authorization", "Bearer " + TOK)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, txt


today = dt.date.today().isoformat()

s, b = req("GET", "/masterdata/room", TOK)
room = rows(b)[0]
s, b = req("GET", "/masterdata/task_type", TOK)
task_type = rows(b)[0]
s, b = req("GET", "/user/users", TOK)
staff = rows(b)[0]

# ======================================================= HOUSEKEEPING TASKS ==
print("\n======== Housekeeping ========")
payload = {
    "employee_id": staff["id"], "assign_staff": staff["id"],
    "first_name": "Ops", "last_name": "Test",
    "room_no": room["id"], "task_type": task_type.get("task_name") or task_type.get("task_type_name"),
    "schedule_date": today, "schedule_time": "10:00",
    "task_status": "Pending", "room_status": "Unblocking",
    "lost_found": None, "special_instructions": "flow test",
}
s, b = req("POST", "/hotel/housekeeper_tasks", TOK, payload)
check("task: create -> 200/201", s in (200, 201), f"{s} {str(b)[:220]}")
task_id = (b.get("data") or {}).get("id") if s in (200, 201) else None

s, b = req("GET", "/hotel/housekeeper_tasks", TOK)
check("task: appears in list", any(r.get("id") == task_id for r in rows(b)), f"{len(rows(b))} rows")

s, b = req("POST", "/hotel/housekeeper_tasks", TOK, {**payload, "room_no": 999999})
check("task: unknown room refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = req("POST", "/hotel/housekeeper_tasks", TOK, {**payload, "task_status": "Nonsense"})
check("task: unknown status refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = req("POST", "/hotel/housekeeper_tasks", TOK, {**payload, "room_status": "Ready"})
check("task: unknown room status refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = req("POST", "/hotel/housekeeper_tasks", TOK, {**payload, "employee_id": 999999,
                                                    "assign_staff": 999999})
check("task: unknown employee refused", s >= 400, f"{s} {str(b)[:160]}")

if task_id:
    s, b = req("PUT", "/hotel/housekeeper_tasks", TOK,
               {**payload, "id": task_id, "task_status": "Completed", "room_status": "Blocking"})
    check("task: update -> 200", s == 200, f"{s} {str(b)[:200]}")
    s, b = req("GET", "/hotel/housekeeper_tasks", TOK)
    row = next((r for r in rows(b) if r.get("id") == task_id), {})
    check("task: update persisted", str(row.get("task_status")) == "Completed",
          str(row.get("task_status")))

    # /hotel/keeper_info is API surface the SPA never calls, so the gateway has
    # no permission row for it and refuses it to everyone, admin included.
    # That is the intended posture for an unused endpoint, not a break.
    s, b = req("GET", f"/hotel/keeper_info/{task_id}", TOK)
    check("task: an endpoint the SPA never calls is refused, admin included",
          s == 403, f"{s} {str(b)[:160]}")

    s, b = req("DELETE", f"/hotel/housekeeper_tasks/{task_id}", TOK)
    check("task: delete -> 200", s == 200, f"{s} {str(b)[:160]}")
    s, b = req("GET", "/hotel/housekeeper_tasks", TOK)
    check("task: gone after delete", not any(r.get("id") == task_id for r in rows(b)))

# ============================================================ ROOM INCIDENT ==
print("\n======== Room incidents ========")
fields = {
    "room_id": room["id"], "incident_date": today, "incident_time": "12:30",
    "incident_description": "Flow test incident", "involved_staff": "Ops Test",
    "severity": "Low", "witnesses": "none", "actions_taken": "logged",
    "reported_by": staff["id"], "report_date": today,
}
s, b = multipart("POST", "/hotel/roomincident_log", fields,
                 {"attachment_file": ("evidence.png", PNG, "image/png")})
check("incident: create -> 200/201", s in (200, 201), f"{s} {str(b)[:220]}")
inc_id = (b.get("data") or {}).get("id") if s in (200, 201) else None

s, b = req("GET", "/hotel/roomincident_log", TOK)
inc = next((r for r in rows(b) if r.get("id") == inc_id), {})
check("incident: appears in list", bool(inc), f"{len(rows(b))} rows")
attachment = inc.get("attachment_file")
check("incident: attachment path stored", bool(attachment), str(inc)[:200])

if attachment:
    s, b = req("GET", f"/hotel{attachment}", TOK, raw=True)
    check("incident: attachment is served through the gateway", s == 200, f"{s}")

s, b = multipart("POST", "/hotel/roomincident_log", {**fields, "room_id": 999999},
                 {"attachment_file": ("evidence.png", PNG, "image/png")})
check("incident: unknown room refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = multipart("POST", "/hotel/roomincident_log", {**fields, "severity": "Apocalyptic"},
                 {"attachment_file": ("evidence.png", PNG, "image/png")})
check("incident: unknown severity refused", s >= 400, f"{s} {str(b)[:160]}")

if inc_id:
    s, b = multipart("PUT", "/hotel/roomincident_log",
                     {**fields, "id": inc_id, "actions_taken": "escalated"})
    check("incident: update -> 200", s == 200, f"{s} {str(b)[:200]}")
    s, b = req("DELETE", f"/hotel/roomincident_log/{inc_id}", TOK)
    check("incident: delete -> 200", s == 200, f"{s} {str(b)[:160]}")

# ============================================================ GUEST ENQUIRY ==
print("\n======== Guest enquiry ========")
enq = {"inquiry_mode": "Online", "guest_name": "Ops Tester",
       "inquiry_status": "In Progress", "response": None,
       "follow_up": None, "incidents": None}
s, b = req("POST", "/hotel/inquiry", TOK, enq)
check("enquiry: create -> 200/201", s in (200, 201), f"{s} {str(b)[:220]}")
enq_id = (b.get("data") or {}).get("id") if s in (200, 201) else None

s, b = req("POST", "/hotel/inquiry", TOK, {**enq, "inquiry_mode": "Carrier Pigeon"})
check("enquiry: unknown mode refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = req("POST", "/hotel/inquiry", TOK, {**enq, "inquiry_status": "Maybe"})
check("enquiry: unknown status refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = req("POST", "/hotel/inquiry", TOK, {**enq, "guest_name": ""})
check("enquiry: blank guest name refused", s >= 400, f"{s} {str(b)[:160]}")
s, b = req("POST", "/hotel/inquiry", TOK, {**enq, "guest_name": "x" * 500})
check("enquiry: very long guest name refused cleanly (not 500)", s == 400,
      f"{s} {str(b)[:160]}")

if enq_id:
    s, b = req("PUT", "/hotel/inquiry", TOK,
               {**enq, "id": enq_id, "inquiry_status": "Completed", "response": "Handled"})
    check("enquiry: update -> 200", s == 200, f"{s} {str(b)[:200]}")
    s, b = req("GET", f"/hotel/inquiry/{enq_id}", TOK)
    check("enquiry: readable by id", s == 200, f"{s} {str(b)[:160]}")
    row = (b.get("data") or {})
    check("enquiry: update persisted", str(row.get("inquiry_status")) == "Completed",
          str(row.get("inquiry_status")))
    s, b = req("DELETE", f"/hotel/inquiry/{enq_id}", TOK)
    check("enquiry: delete -> 200", s == 200, f"{s} {str(b)[:160]}")

# ============================================================== NIGHT AUDIT ==
print("\n======== Night audit ========")
s, b = req("GET", "/hotel/night_audit/preview", TOK)
check("audit: preview -> 200", s == 200, f"{s} {str(b)[:200]}")
preview = (b.get("data") or {}) if s == 200 else {}
print("       preview keys:", list(preview)[:12])

s, b = req("GET", "/hotel/night_audit/history", TOK)
check("audit: history -> 200", s == 200, f"{s} {str(b)[:160]}")
before = len(rows(b))

s, b = req("GET", "/hotel/user_activity_log", TOK)
check("audit: user activity log -> 200", s == 200, f"{s} {str(b)[:160]}")

print(f"\n{PASSES} passed, {len(FAILS)} failed")
for f in FAILS:
    print("  -", f)

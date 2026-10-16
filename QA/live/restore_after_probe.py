# -*- coding: utf-8 -*-
"""Restore the two staging rows removed by the first privilege-escalation probe.

That probe issued DELETE against real record ids expecting a 403. The gateway
was in audit mode, so the DELETEs succeeded and removed two rows from LIVE. This
script puts them back from the snapshot captured in the probe's own output.

The probe itself was renamed to `privesc_probe.REPLACED-BY-privesc_matrix.txt`
and is not runnable: it is kept only as a record of what happened, and because
the lesson belongs in the repository. The safe replacement is
`privesc_matrix.py`, which probes record id 999999999 only, so a write verb has
nothing to act on.

Run once, then confirm with the counts printed at the end.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GW = os.environ.get("QA_GATEWAY", "http://168.231.103.18:9010")
PW = os.environ.get("QA_PASSWORD", "")  # never stored in this repo; see qa_common.py

def _resolve_password(default_email):
    """QA_PASSWORD, or a message explaining how to set it.

    Without this an unset variable produced a bare
    `email and password are required` 400 from the gateway, which reads as a
    broken account rather than a missing environment variable.
    """
    if PW:
        return PW
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from qa_common import password_for
    return password_for(default_email)


def call(method, path, tok=None, body=None, ctype=None, limit=2000000):
    r = urllib.request.Request(GW + path, data=body, method=method)
    if ctype:
        r.add_header("Content-Type", ctype)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:limit]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:limit]
    except Exception as e:
        return 0, str(e)[:200]


def login(email):
    password = _resolve_password(email)
    for a in range(6):
        s, b = call("POST", "/login_post",
                    body=json.dumps({"email": email, "password": password}).encode(),
                    ctype="application/json", limit=200000)
        if s == 200:
            return json.loads(b)["access_token"]
        if s == 429:
            time.sleep(20 * (a + 1))
            continue
        raise SystemExit(f"login failed {email}: {s} {b}")
    raise SystemExit("rate limited")


def multipart(fields):
    b = "----qa" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n")
    parts.append(f"--{b}--\r\n")
    return b, "".join(parts).encode()


def rows(b):
    d = b.get("data") if isinstance(b, dict) else None
    if isinstance(d, dict):
        d = d.get("data", d)
    return d if isinstance(d, list) else []


def get_list(path, tok):
    s, b = call("GET", path, tok=tok)
    return s, json.loads(b) if b.startswith("{") else b


tok = login("admin@cherryhotel.com")
print("admin logged in")

# ---------------------------------------------------------------- tax id 6
s, b = get_list("/masterdata/tax", tok)
taxes = rows(json.loads(b) if isinstance(b, str) else b)
have = {(t.get("id"), t.get("tax_name")) for t in taxes}
if (6, "No Tax") in have:
    print("tax 'No Tax' already present -- nothing to restore")
elif any(t.get("tax_name") == "No Tax" for t in taxes):
    print("tax 'No Tax' present with a different id:")
    for t in taxes:
        if t.get("tax_name") == "No Tax":
            print("   ", t)
else:
    s, b = call("POST", "/masterdata/tax", tok=tok,
                body=json.dumps({"country_id": 1, "tax_name": "No Tax",
                                 "tax_percentage": 0}).encode(),
                ctype="application/json")
    print(f"restore tax 'No Tax' -> {s} {b}")

# --------------------------------------------------------------- room 601
s, b = get_list("/masterdata/room", tok)
rooms = rows(json.loads(b) if isinstance(b, str) else b)
existing = {r.get("room_no") for r in rooms}
if "601" in existing:
    print("room 601 already present -- nothing to restore")
else:
    boundary, data = multipart({
        "room_no": "601",
        "room_name": "Presidential Suite 601",
        "room_type_id": "7",
        "bed_type_id": "5",
        "room_telephone": "1601",
        "max_adult": "4",
        "max_child": "3",
    })
    s, b = call("POST", "/masterdata/room", tok=tok, body=data,
                ctype=f"multipart/form-data; boundary={boundary}")
    print(f"restore room 601 -> {s} {b}")

# ------------------------------------------------------------- verify
s, b = get_list("/masterdata/room", tok)
rooms = rows(json.loads(b) if isinstance(b, str) else b)
r601 = next((r for r in rooms if r.get("room_no") == "601"), None)
print("\nroom 601 now:", json.dumps(r601, indent=1) if r601 else "MISSING")
s, b = get_list("/masterdata/tax", tok)
taxes = rows(json.loads(b) if isinstance(b, str) else b)
ntax = next((t for t in taxes if t.get("tax_name") == "No Tax"), None)
print("tax 'No Tax' now:", ntax)
print("\ncounts: rooms=%d taxes=%d" % (len(rooms), len(taxes)))

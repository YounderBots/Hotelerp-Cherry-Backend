# -*- coding: utf-8 -*-
"""Authentication and authorisation probes against the running gateway."""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import GW, PW, req, login, rows  # noqa: E402

FAILS, PASSES = [], 0


def check(label, cond, detail=""):
    global PASSES
    if cond:
        PASSES += 1
        print(f"  ok   {label}")
    else:
        FAILS.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")


PROTECTED = [
    ("GET", "/user/users"),
    ("GET", "/masterdata/room"),
    ("GET", "/hotel/room_reservation"),
    ("GET", "/restaurant/order"),
    ("GET", "/bar/order"),
    ("GET", "/user/me"),
]

print("== no token ==")
for method, path in PROTECTED:
    s, b = req(method, path)
    check(f"{method} {path} without a token -> 401", s == 401, f"got {s} {str(b)[:90]}")

print("\n== malformed and tampered tokens ==")
admin = login("admin@cherryhotel.com")
frontdesk = login("rahul.nair@cherryhotel.com")

for label, tok in [
    ("gibberish", "not.a.token"),
    ("empty", ""),
    ("bearer of nothing", "   "),
    ("truncated", admin[:-12]),
]:
    s, b = req("GET", "/user/users", tok)
    check(f"{label} token -> 401", s == 401, f"got {s} {str(b)[:90]}")

# Re-sign the payload with a different secret: same shape, wrong signature.
head, payload, sig = admin.split(".")
forged = f"{head}.{payload}.{'A' * len(sig)}"
s, b = req("GET", "/user/users", forged)
check("token with a replaced signature -> 401", s == 401, f"got {s} {str(b)[:90]}")


def b64url(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()


claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
print(f"       admin claims: {sorted(claims)}")

# Widen the permission claim and keep the original signature: the classic
# "edit the JWT payload" attempt.
widened = dict(claims)
widened["perm"] = {p: 15 for p in ["/employee", "/user", "/rooms", "/reservation"]}
s, b = req("GET", "/user/users", f"{head}.{b64url(widened)}.{sig}")
check("a widened `perm` claim with the original signature -> 401", s == 401,
      f"got {s} {str(b)[:110]}")

# Swap identity: front desk's token body under admin's signature.
fd_payload = frontdesk.split(".")[1]
s, b = req("GET", "/user/users", f"{head}.{fd_payload}.{sig}")
check("another user's claims under this signature -> 401", s == 401, f"got {s} {str(b)[:110]}")

print("\n== authorisation is not client-side ==")
s, b = req("GET", "/user/users", frontdesk)
check("Front Desk is refused the staff directory -> 403", s == 403, f"got {s} {str(b)[:110]}")
s, b = req("DELETE", "/masterdata/bed_type/1", frontdesk)
check("Front Desk is refused a Master Data delete -> 403", s == 403, f"got {s} {str(b)[:110]}")
s, b = req("POST", "/masterdata/bed_type", frontdesk, {"bed_type": "SecurityProbe"})
check("Front Desk is refused a Master Data create -> 403", s == 403, f"got {s} {str(b)[:110]}")
s, b = req("GET", "/bar/bill", frontdesk)
check("Front Desk is refused the bar folio -> 403", s == 403, f"got {s} {str(b)[:110]}")

print("\n== self-service reaches only the caller ==")
s, admin_me = req("GET", "/user/me", admin)
s2, fd_me = req("GET", "/user/me", frontdesk)
check("/user/me answers each caller with their own record",
      (admin_me.get("data") or {}).get("id") != (fd_me.get("data") or {}).get("id"),
      f"{(admin_me.get('data') or {}).get('id')} vs {(fd_me.get('data') or {}).get('id')}")
check("/user/me does not carry salary",
      "salary" not in json.dumps(admin_me).lower(), "salary present in the payload")
s, b = req("GET", "/user/me/photo", frontdesk, raw=True)
check("a role with no HRM access can still load its own avatar", s == 200, f"got {s}")
s, b = req("GET", "/user/templates/static/users/anything.png", frontdesk)
check("...but not a colleague's photo by path -> 403", s == 403, f"got {s} {str(b)[:90]}")

print("\n== password change ==")
s, b = req("PUT", "/user/me/password", frontdesk,
           {"current_password": "wrong-password", "new_password": "N3wPassword!x"})
check("wrong current password -> 4xx", 400 <= s < 500, f"got {s} {str(b)[:110]}")
s, b = req("PUT", "/user/me/password", frontdesk,
           {"current_password": PW, "new_password": "short"})
check("a too-short new password is refused", 400 <= s < 500, f"got {s} {str(b)[:110]}")

# The gateway allows a small number of login attempts per minute per peer, and
# everything above has already spent several. The credential checks below are
# themselves failed logins, so without draining the window first they start
# reporting 429 where they mean 401 -- the suite that tests the limiter defeated
# by it.
def drain_login_limiter(seconds=61):
    print(f"\n  (waiting {seconds}s for the login rate-limit window to drain)")
    time.sleep(seconds)


drain_login_limiter()

print("\n== credentials ==")
for label, body, want in [
    ("empty body", {}, 400),
    ("no password", {"email": "admin@cherryhotel.com"}, 400),
    ("unknown email", {"email": "nobody@nowhere.test", "password": "x"}, 401),
    ("wrong password", {"email": "admin@cherryhotel.com", "password": "nope"}, 401),
    ("SQL-ish email", {"email": "' OR 1=1 --", "password": "x"}, 401),
]:
    s, b = req("POST", "/login_post", body=body)
    check(f"login with {label} -> {want}", s == want, f"got {s} {str(b)[:110]}")

s, b = req("POST", "/login_post", body={"email": "ADMIN@CherryHotel.COM", "password": PW})
check("email is matched case-insensitively", s == 200, f"got {s} {str(b)[:90]}")

s, b = req("POST", "/login_post", body={"email": "admin@cherryhotel.com", "password": "nope"})
check("a failed login does not say which half was wrong",
      "invalid credentials" in str(b).lower(), str(b)[:110])

# Deliberately last: this exhausts the window on purpose, so anything after it
# would have to wait a minute to sign in.
print("\n== login rate limiting ==")
drain_login_limiter()
codes = []
for _ in range(16):
    s, _b = req("POST", "/login_post", body={"email": "spray@nowhere.test", "password": "x"})
    codes.append(s)
check("repeated failed logins are rate limited", 429 in codes,
      f"statuses: {codes}")
# Let the window drain so the rest of the run is not throttled.
time.sleep(2)

print(f"\n{PASSES} passed, {len(FAILS)} failed")
for f in FAILS:
    print("  -", f)

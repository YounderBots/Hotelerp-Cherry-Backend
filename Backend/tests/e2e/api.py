# -*- coding: utf-8 -*-
"""Shared gateway client for the manual test harnesses."""
import json
import os
import time
import urllib.error
import urllib.request

GW = os.environ.get("E2E_GATEWAY", "http://127.0.0.1:8000")

# The seeded password. Once Backend/tools/rotate_passwords.py has replaced it --
# which every production deployment must do -- point these suites at the new one
# with E2E_PASSWORD, or run them against a freshly seeded demo database.
PW = os.environ.get("E2E_PASSWORD", "Hotel@2026")


def req(method, path, tok=None, body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(GW + path, data=data, method=method)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            body_bytes = resp.read()
            if raw:
                return resp.status, body_bytes
            text = body_bytes.decode("utf-8", "replace")
            try:
                return resp.status, json.loads(text)
            except ValueError:
                return resp.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(text)
        except ValueError:
            return e.code, text
    except Exception as e:  # connection refused, timeout, ...
        return 0, str(e)


def login(email, password=PW):
    """Sign in, waiting out the gateway's login rate limiter if it is tripped.

    The limiter is per-peer and per-minute, and the security suite exhausts it
    on purpose. Without this, whichever suite ran next could not sign in at all
    and reported a failure that was really the previous suite's tail.
    """
    for attempt in range(4):
        s, b = req("POST", "/login_post", body={"email": email, "password": password})
        if s == 200:
            return b["access_token"]
        if s != 429:
            break
        wait = 20 * (attempt + 1)
        print(f"  (login rate limited; waiting {wait}s for the window to drain)")
        time.sleep(wait)
    raise SystemExit(f"login failed for {email}: {s} {b}")


def rows(res):
    d = res.get("data") if isinstance(res, dict) else None
    if isinstance(d, dict):
        d = d.get("data")
    return d if isinstance(d, list) else []


def refused(status_code) -> bool:
    """Did the API *refuse* this request -- as opposed to crashing on it?

    WHY THIS IS NOT `status >= 400`
        It was, in 26 assertions across three suites, and that let a real bug
        sit in a green run: posting a payment with an unknown
        `payment_method_id` reached the INSERT, the foreign key rejected it,
        and the endpoint answered 500 with an unhandled IntegrityError. The
        suite asserted "unknown payment method refused", saw 500, and passed.

        A refusal is a rule the API states: 4xx, with a message naming what was
        wrong. A 500 is the opposite -- the request got far enough to break
        something, and the caller is told only "Internal server error". Any
        check that accepts both cannot tell a working guard from a missing one,
        which is the only thing it was written to find out.
    """
    return 400 <= int(status_code) < 500

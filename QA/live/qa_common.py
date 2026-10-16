# -*- coding: utf-8 -*-
"""Shared credential handling for the LIVE QA harnesses.

NO PASSWORD IS WRITTEN IN THIS DIRECTORY.

These scripts talk to a deployment that requires authentication, so they need
a credential -- but a credential committed to the repository is a published
one. The value is therefore read from the environment every time:

    # PowerShell
    $env:QA_GATEWAY   = "http://168.231.103.18:9010"
    $env:QA_EMAIL     = "admin@cherryhotel.com"
    $env:QA_PASSWORD  = "<the demo password>"

    # bash
    export QA_GATEWAY=http://168.231.103.18:9010
    export QA_EMAIL=admin@cherryhotel.com
    export QA_PASSWORD='<the demo password>'

The account matrix below is the five demo roles. Each harness logs in every one
of them, so `QA_PASSWORD` is the shared demo password the brief supplies; set
`QA_CREDENTIALS` to a file of `email<TAB>password` lines instead if the accounts
ever hold different values (the repository's own `rotate_passwords.py` writes
one).

Nothing here is echoed, logged or written to a report.
"""
from __future__ import annotations

import os
import pathlib
import time
import urllib.error
import urllib.request

ACCOUNTS = {
    "Admin": "admin@cherryhotel.com",
    "FrontOfficeManager": "meera.krishnan@cherryhotel.com",
    "FrontDesk": "divya.rao@cherryhotel.com",
    "Housekeeping": "imran.khan@cherryhotel.com",
    "FoodAndBeverage": "joseph.dsouza@cherryhotel.com",
}

GATEWAY = os.environ.get("QA_GATEWAY", "http://168.231.103.18:9010")
HOST = GATEWAY.split("//")[-1].split(":")[0]

# gateway proxy prefix -> service port, found by scanning 8990-9089 on the host
SERVICES = {
    "hotel": 9005,
    "masterdata": 9015,
    "user": 9020,
    "bar": 9025,
    "restaurant": 9030,
}


def _per_account() -> dict:
    path = os.environ.get("QA_CREDENTIALS", "")
    if not path or not os.path.isfile(path):
        return {}
    out = {}
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            email, _, pw = line.partition("\t")
            if email and pw:
                out[email] = pw
    return out


_PER_ACCOUNT = _per_account()


def password_for(email: str) -> str:
    """The password for one account, or a clear message about what is missing."""
    if email in _PER_ACCOUNT:
        return _PER_ACCOUNT[email]
    pw = os.environ.get("QA_PASSWORD", "")
    if pw:
        return pw
    raise SystemExit(
        "QA_PASSWORD is not set.\n"
        "These harnesses need a credential to reach the deployment, and none is\n"
        "stored in this repository on purpose. Set it in the environment:\n"
        "    $env:QA_PASSWORD = '<the demo password>'\n"
        "or point QA_CREDENTIALS at a file of 'email<TAB>password' lines."
    )


def call(method, url, tok=None, body=None, ctype="application/json", timeout=30, limit=2_000_000):
    """One HTTP call. Returns (status, parsed_body_or_text, content_type)."""
    data = None
    if body is not None:
        import json
        data = json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method)
    if data is not None and ctype:
        r.add_header("Content-Type", ctype)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")[:limit]
            try:
                import json
                return resp.status, json.loads(raw), resp.headers.get("Content-Type", "")
            except ValueError:
                return resp.status, raw, resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")[:limit]
        try:
            import json
            return e.code, json.loads(raw), e.headers.get("Content-Type", "")
        except ValueError:
            return e.code, raw, e.headers.get("Content-Type", "")
    except Exception as e:  # connection refused, timeout, ...
        return 0, str(e)[:200], ""


def login(email, attempts=6):
    """Sign in, waiting out the gateway's per-peer login rate limiter.

    The limiter is real and shared across every account, so a run that trips it
    must drain the window rather than reporting the account as broken.
    """
    pw = password_for(email)
    for attempt in range(attempts):
        s, b, _ = call("POST", GATEWAY + "/login_post", None,
                       {"email": email, "password": pw})
        if s == 200:
            import json
            return b["access_token"]
        if s == 429:
            wait = 20 * (attempt + 1)
            print(f"  (login rate limited for {email}; waiting {wait}s)")
            time.sleep(wait)
            continue
        raise SystemExit(f"login failed for {email}: {s} {str(b)[:160]}")
    raise SystemExit(f"login rate limited persistently for {email}")


def claims(tok):
    import base64
    import json
    try:
        seg = tok.split(".")[1]
        return json.loads(base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4)))
    except Exception:
        return {}
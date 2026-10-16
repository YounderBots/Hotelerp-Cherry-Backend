# -*- coding: utf-8 -*-
"""Does the repo's JWT signing key verify the LIVE token? Then: does the
committed verify_authentication() reject that token because `exp` has passed?

No secret is printed. The key is read from the repo's own service .env, which
is gitignored and is the same provisioning the staging host was cut from (see
QA/LIVE_FIX_QUEUE.md LIVE-001, where a locally seeded password authenticated
against LIVE).
"""
import base64
import datetime
import hashlib
import json
import pathlib
import sys
import time

from jose import JWTError, jwt

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENV = ROOT / "Backend" / "Services" / "LoginServices" / ".env"
ALGORITHM = "HS256"
ISSUER = "hotelerp-login"


def read_secret():
    for line in ENV.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("JWT_SECRET_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no JWT_SECRET_KEY in " + str(ENV))


def claims(tok):
    seg = tok.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4)))


def committed_verify(token, secret):
    """Exactly resources/utils.py::verify_authentication's decode block."""
    payload = jwt.decode(token, secret, algorithms=[ALGORITHM], issuer=ISSUER)
    for claim in ("exp", "iat"):
        if claim not in payload:
            raise ValueError(f"missing {claim}")
    return payload


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    token = sys.argv[1].strip()
    secret = read_secret()
    fp = hashlib.sha256(secret.encode()).hexdigest()[:12]
    c = claims(token)
    now = int(time.time())

    print(f"repo signing key fingerprint : sha256[:12]={fp}  (value not printed)")
    print(f"LIVE token iat/exp          : {c.get('iat')} / {c.get('exp')}")
    print(f"now                         : {now}")
    print(f"seconds since exp            : {now - c.get('exp', 0)}  "
          f"({(now - c.get('exp', 0)) / 60:.1f} min past expiry)")

    # Step 1: signature. Separate the two failures so we know which we hit.
    try:
        jwt.decode(token, secret, algorithms=[ALGORITHM], issuer=ISSUER,
                   options={"verify_exp": False})
        sig_ok = True
    except JWTError as e:
        sig_ok = False
        print(f"\nsignature check failed: {type(e).__name__}: {e}")
        print("The repo key does not sign LIVE tokens; stop here -- a different key")
        print("means the isolation test below cannot be run from this checkout.")
        return 2

    print("\nsignature verifies against the repo key -> LIVE and this checkout "
          "share JWT_SECRET_KEY")

    # Step 2: does the committed logic honour exp?
    try:
        committed_verify(token, secret)
        print("committed verify_authentication(): ACCEPTED the expired token")
        print("  -> python-jose here is not enforcing exp; the code path is the cause")
        return 1
    except (JWTError, ValueError) as e:
        print(f"committed verify_authentication(): refused ({type(e).__name__}: {e})")
        print("  -> the committed code is correct and LIVE is not running it")
        print(f"  -> LIVE returned 200 for this same token: DEPLOYMENT DRIFT confirmed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
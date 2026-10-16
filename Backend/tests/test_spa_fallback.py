# -*- coding: utf-8 -*-
"""The SPA host must 404 a missing asset and serve the shell for a route.

Run from the repository root:

    python Backend/tests/test_spa_fallback.py

Starts Frontend/serve-spa.mjs against a SYNTHETIC build tree in a temp
directory, then asks it real HTTP questions over the wire. Synthetic rather
than `Frontend/dist`, deliberately: dist's asset names are content-hashed, so
a test that reads them would pass or fail depending on whether someone had run
`npm run build` and on what that build hashed to. The behaviour under test has
nothing to do with the real bundle's filenames.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
SERVER = REPO / "Frontend" / "serve-spa.mjs"

NODE = shutil.which("node") or shutil.which("node.exe")


def build_tree(root: pathlib.Path) -> None:
    """A minimal but realistic build output."""
    (root / "assets").mkdir(parents=True, exist_ok=True)
    (root / "templates" / "static" / "upload_image").mkdir(parents=True, exist_ok=True)
    (root / "index.html").write_text(
        "<!doctype html><html><body><div id='root'></div>"
        "<script type='module' src='/assets/index-abc123.js'></script></body></html>",
        encoding="utf-8",
    )
    (root / "assets" / "index-abc123.js").write_text("console.log(1)", encoding="utf-8")
    (root / "assets" / "index-abc123.css").write_text("body{}", encoding="utf-8")
    # One real image, so the "exists" side of the asset case is covered too.
    (root / "assets" / "logo.png").write_bytes(bytes.fromhex(
        "89504e470d0a1a0a0000000d494844520000000100000001080600000"
        "01f15c4890000000a49444154789c6360000002000100ffff0300000600"
        "0557bfabd40000000049454e44ae426082"))
    (root / "templates" / "static" / "upload_image" / "present.jpg").write_bytes(b"\xff\xd8\xff")


def request(port: int, path: str, accept: str | None = None, method: str = "GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method)
    if accept is not None:
        req.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()
    except Exception as e:                                   # noqa: BLE001
        return 0, str(e)[:120], b""


def raw_request(port: int, raw_target: str, method: str = "GET") -> tuple[int, str, bytes]:
    """Send a request target VERBATIM over a socket.

    urllib normalises `..` in the path before it reaches the wire, which would
    make the traversal cases test the wrong thing -- the server would never see
    an attempt. This puts the exact bytes on the wire, which is the point.
    """
    import socket

    lines = [
        f"{method} {raw_target} HTTP/1.1",
        f"Host: 127.0.0.1:{port}",
        "Accept: text/html,application/xhtml+xml,*/*;q=0.8",
        "Connection: close",
        "",
        "",
    ]
    payload = "\r\n".join(lines).encode("utf-8")
    with socket.create_connection(("127.0.0.1", port), timeout=10) as sock:
        sock.sendall(payload)
        chunks = []
        while True:
            data = sock.recv(65536)
            if not data:
                break
            chunks.append(data)
    raw = b"".join(chunks)
    head, _, body = raw.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n", 1)[0].decode("latin-1", "replace")
    status = int(status_line.split()[1]) if len(status_line.split()) > 1 else 0
    ctype = ""
    for line in head.decode("latin-1", "replace").split("\r\n")[1:]:
        if line.lower().startswith("content-type:"):
            ctype = line.split(":", 1)[1].strip()
    return status, ctype, body


def main() -> int:
    if not NODE:
        print("node not found -- cannot run the SPA host tests")
        return 1
    if not SERVER.is_file():
        print(f"missing {SERVER}")
        return 1

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="spa-"))
    root = tmp / "dist"
    build_tree(root)

    port = 5787
    proc = subprocess.Popen(
        [NODE, str(SERVER), "--dir", str(root), "--port", str(port), "--host", "127.0.0.1"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        for _ in range(50):
            if request(port, "/", "text/html")[0] == 200:
                break
            time.sleep(0.1)
        else:
            print("server did not come up")
            print(proc.communicate(timeout=5)[0])
            return 1

        failures = []

        def check(label, path, accept, want_status, want_type=None):
            status, ctype, body = request(port, path, accept, "GET")
            ok = status == want_status
            if ok and want_type:
                ok = want_type in ctype
            failures.append((label, status, want_status, ctype, ok))
            mark = "PASS" if ok else "FAIL"
            extra = f"  {ctype.split(';')[0]}" if ok and want_type else ""
            print(f"  [{mark}] {label:<52} {status} (want {want_status}){extra}")

        HTML = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ASSET = "image/avif,image/webp,*/*"

        print("\n-- a client-side route gets the shell --")
        check("/dashboard", "/dashboard", HTML, 200, "text/html")
        check("/room_view", "/room_view", HTML, 200, "text/html")
        check("/hotel/room_reservation", "/hotel/room_reservation", HTML, 200, "text/html")
        check("nested deep route", "/a/b/c/d", HTML, 200, "text/html")

        print("\n-- a real asset is served with its own type --")
        check("js bundle", "/assets/index-abc123.js", ASSET, 200, "javascript")
        check("css bundle", "/assets/index-abc123.css", ASSET, 200, "text/css")
        check("existing png", "/assets/logo.png", ASSET, 200, "image/png")

        print("\n-- a MISSING asset is a 404, never the shell --")
        check("missing js", "/assets/index-DOESNOTEXIST.js", ASSET, 404)
        check("missing png", "/assets/nope.png", ASSET, 404)
        check("missing upload image", "/templates/static/upload_image/gone.jpg",
              ASSET, 404)
        check("missing asset with an HTML Accept", "/assets/nope.js", HTML, 404)

        print("\n-- and the shell is never served for an asset path, whatever the Accept --")
        status, ctype, body = request(port, "/does-not-exist-xyz.jpg", HTML)
        ok = status == 404 and b"id='root'" not in body and b"id=\"root\"" not in body
        print(f"  [{'PASS' if ok else 'FAIL'}] /does-not-exist-xyz.jpg with Accept: text/html   "
              f"{status} (want 404, and never the index)")
        failures.append(("jpg with html accept", status, 404, ctype, ok))

        print("\n-- root and index --")
        check("/", "/", HTML, 200, "text/html")
        check("/index.html", "/index.html", HTML, 200, "text/html")

        print("\n-- path traversal (raw request targets: urllib would normalise them away) --")
        # Two different invariants, and they are not the same assertion.
        #
        #  A path that actually resolves `..` out of root must be REFUSED (400):
        #  the attempt is real and is being made deliberately.
        #
        #  A path that merely LOOKS like one -- double-encoded, so it decodes to
        #  a literal filename containing "%2f" and no segment is ".." -- is just
        #  a path that does not exist. It must not leak a file, and it must not
        #  be answered with the shell, but 404 is the right answer and forcing
        #  400 would be asserting a status for no reason.
        #
        #  Note what is NOT here: `/....//....//etc`. `....` is a legal
        #  directory name, not a parent reference, so that path is an ordinary
        #  unknown extensionless path and returning the shell is the SPA working
        # correctly. Inventing it and then expecting it to be refused was a
        #  mistake in the test, not a finding.
        for label, target, want in (
            ("/../Backend/Services", "/../Backend/Services", 400),
            ("/assets/../../etc/passwd", "/assets/../../etc/passwd", 400),
            ("/..%2f..%2fetc/passwd (encoded slash)", "/..%2f..%2fetc/passwd", 400),
            ("/index.html%00.png (null byte)", "/index.html%00.png", 400),
            ("/..%252f..%252fetc (double encoded)", "/..%252f..%252fetc", 404),
        ):
            status, ctype, body = raw_request(port, target)
            leaked = any(m in body for m in (b"root:", b"passwd", b"RSA", b"backend"))
            served_shell = b"id='root'" in body or b'id="root"' in body
            if want is None:
                ok = not leaked and not served_shell and status >= 400
                shown = f"{status} (want >=400, never the shell, never a leak)"
            else:
                ok = status == want and not leaked and not served_shell
                shown = f"{status} (want {want})"
            print(f"  [{'PASS' if ok else 'FAIL'}] {label:<44} {shown}")
            failures.append((label, status, want, ctype, ok))

        print("\n-- methods --")
        s, _, _ = request(port, "/dashboard", HTML, "HEAD")
        print(f"  [{'PASS' if s == 200 else 'FAIL'}] HEAD /dashboard{s} (want 200)")
        if s != 200:
            failures.append(("HEAD", s, 200, "", False))

        print("\n-- headers --")
        req = urllib.request.Request(f"http://127.0.0.1:{port}/dashboard")
        req.add_header("Accept", HTML)
        with urllib.request.urlopen(req, timeout=10) as resp:
            nosniff = resp.headers.get("X-Content-Type-Options")
            cache = resp.headers.get("Cache-Control")
        ok = nosniff == "nosniff" and cache == "no-cache"
        print(f"  [{'PASS' if ok else 'FAIL'}] nosniff + no-cache on the shell   "
              f"{nosniff} / {cache}")
        failures.append(("headers", 0, 0, "", ok))

        print()
        bad = [f for f in failures if not f[4]]
        if bad:
            for label, got, want, ctype, _ in bad:
                print(f"  FAILED: {label}: got {got} ({ctype}), want {want}")
            print(f"\n{len(bad)} case(s) failed")
            return 1
        print(f"all {len(failures)} SPA host cases pass -- "
              f"routes get the shell, missing assets are 404, traversal is refused")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:                       # pragma: no cover
            proc.kill()
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
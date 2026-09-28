"""Uploads are validated by their bytes, not only by their name (C-085).

    python -m pytest Backend/tests/test_upload_content.py -q

WHY THIS SUITE EXISTS
    Every upload path checked the file's *extension* and nothing else, so
    `POST /masterdata/room` accepted an HTML document containing a `<script>`
    tag as long as it was called `evil.png`, and wrote it into the directory the
    static mount serves. The served response carried `X-Content-Type-Options:
    nosniff` and the extension's content type, so a browser would not have run
    it -- this was a content-integrity hole, not a working stored XSS, and the
    register records it as P2 for that reason. What it did prove is that "upload
    a room photo" was a channel for storing anything at all.

    The fix sniffs the first bytes and requires them to match the claimed type.
    These tests pin the decision function directly, because a validation that
    only ever runs behind a multipart request is a validation nobody tests:
    before this suite, the only proof the check worked was a probe made by hand.

    Runs from one service root at a time (see `run_all.py`): each service is a
    separate top-level package, and `models`/`configs` mean the same thing in
    all six.
"""

from __future__ import annotations

import io
import pathlib
import sys

import pytest
from fastapi import HTTPException, UploadFile

SERVICE_ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(SERVICE_ROOT))

# Real header bytes for each accepted family. Only the header is ever compared,
# so a truncated sample is enough -- and is what these are.
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 16
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 16
GIF = b"GIF89a" + b"\x00" * 16
WEBP = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBPVP8 " + b"\x00" * 8
PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n" + b"0" * 16


def load_sanitizers():
    """Every upload validator this service defines, with its own allow-list.

    Returns `(label, callable, allowed_extensions, is_async)` tuples. The
    extension set is read from the module rather than assumed, because the
    services differ on purpose: Master Data takes images only, housekeeping
    also takes PDFs, and the identity-proof path keeps its own list.
    """
    candidates = {
        "MasterDataServices": [("resources.masterController", "_sanitize_upload", "ALLOWED_UPLOAD_EXTS")],
        "RestaurantServices": [("resources.menuController", "_sanitize_upload", "ALLOWED_UPLOAD_EXTS")],
        "BarServices": [("resources.menuController", "_sanitize_upload", "ALLOWED_UPLOAD_EXTS")],
        "HotelServices": [
            ("resources.frontOffice.housekeepingController", "_sanitize_upload", "ALLOWED_UPLOAD_EXTS"),
            ("resources.reservationController", "_store_identity_document", "ALLOWED_PROOF_EXTENSIONS"),
        ],
    }
    name = SERVICE_ROOT.name
    if name not in candidates:
        return []
    found = []
    for module_path, attr, ext_attr in candidates[name]:
        try:
            module = __import__(module_path, fromlist=[attr])
        except Exception:
            continue
        fn = getattr(module, attr, None)
        if fn is None:
            continue
        allowed = {str(e).lower() for e in (getattr(module, ext_attr, None) or set())}
        found.append((f"{module_path}.{attr}", fn, allowed, _is_async(fn)))
    return found


def _is_async(fn) -> bool:
    import inspect
    return inspect.iscoroutinefunction(fn)


SANITIZERS = load_sanitizers()
pytestmark = pytest.mark.skipif(not SANITIZERS, reason="no upload validator in this service")


def upload(name: str, data: bytes) -> UploadFile:
    return UploadFile(filename=name, file=io.BytesIO(data))


def call(validator, is_async: bool, file: UploadFile):
    """The identity-proof path is async and takes the file as `identity_file`."""
    if is_async:
        import asyncio
        return asyncio.run(validator(identity_file=file))
    return validator(file)


ACCEPTED = {"jpg": JPEG, "jpeg": JPEG, "png": PNG, "gif": GIF, "webp": WEBP, "pdf": PDF}
REJECTED = {
    "html": b"<html><body><script>alert(document.domain)</script></body></html>",
    "script": b"#!/bin/sh\nrm -rf /\n",
    "zip": b"PK\x03\x04" + b"\x00" * 20,
    "elf": b"\x7fELF" + b"\x00" * 20,
    "xml": b'<?xml version="1.0"?><svg onload="alert(1)"/>',
}


def ids(label, ext):
    return f"{label}-{ext}"


def cases(kind: str):
    """(label, validator, allowed, is_async, ext) for every service x extension."""
    out = []
    for label, fn, allowed, is_async in SANITIZERS:
        for ext in sorted(allowed):
            out.append((label, fn, allowed, is_async, ext))
    return out


@pytest.mark.parametrize("label,fn,allowed,is_async,ext", cases("accept"), ids=lambda v: str(v)[:60])
def test_a_file_of_the_claimed_type_is_accepted(label, fn, allowed, is_async, ext):
    data = ACCEPTED[ext]
    try:
        result = call(fn, is_async, upload(f"photo.{ext}", data))
    except HTTPException as exc:  # pragma: no cover - only on failure
        pytest.fail(f"{label} rejected a real {ext}: {exc.detail}")
    assert result is not None


@pytest.mark.parametrize("label,fn,allowed,is_async,ext", cases("reject"), ids=lambda v: str(v)[:60])
@pytest.mark.parametrize("label_key", sorted(REJECTED))
def test_content_that_is_not_that_type_is_refused(label, fn, allowed, is_async, ext, label_key):
    """The whole point: a name is a claim, and the bytes have to agree."""
    with pytest.raises(HTTPException) as caught:
        call(fn, is_async, upload(f"payload.{ext}", REJECTED[label_key]))
    assert caught.value.status_code == 400
    assert "not a valid" in str(caught.value.detail).lower()


@pytest.mark.parametrize("label,fn,allowed,is_async,ext", cases("names"), ids=lambda v: str(v)[:60])
@pytest.mark.parametrize("name", ["photo.svg", "photo.exe", "photo.html", "photo", "photo."])
def test_unsupported_names_are_refused(label, fn, allowed, is_async, ext, name):
    with pytest.raises(HTTPException) as caught:
        call(fn, is_async, upload(name, PNG))
    assert caught.value.status_code == 400


@pytest.mark.parametrize("label,fn,allowed,is_async,ext", cases("rename"), ids=lambda v: str(v)[:60])
def test_a_renamed_file_cannot_change_its_type(label, fn, allowed, is_async, ext):
    """A file whose bytes are another accepted type is not this type.

    Each target family is fed a header from a *different* accepted family -- a
    PDF header for every image, a PNG header for the PDF case -- because
    "rename the file" is only an attack when the name and the content disagree.
    """
    other = PDF if ext != "pdf" else PNG
    with pytest.raises(HTTPException) as caught:
        call(fn, is_async, upload(f"photo.{ext}", other))
    assert caught.value.status_code == 400

    if ext in ("jpg", "jpeg"):
        with pytest.raises(HTTPException):
            call(fn, is_async, upload(f"photo.{ext}", PNG))


@pytest.mark.parametrize("label,fn,allowed,is_async,ext", cases("missing"), ids=lambda v: str(v)[:60])
def test_a_missing_file_is_refused(label, fn, allowed, is_async, ext):
    with pytest.raises(HTTPException):
        call(fn, is_async, None)
    with pytest.raises(HTTPException):
        call(fn, is_async, UploadFile(filename="", file=io.BytesIO(PNG)))


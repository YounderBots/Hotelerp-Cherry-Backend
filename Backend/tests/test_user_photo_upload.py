"""The staff-photo upload is validated by its bytes and by a size ceiling.

    python -m pytest Backend/tests/test_user_photo_upload.py -q

WHY THIS SUITE EXISTS
    `create_user` used to take the extension off the client's own filename and
    append it to a generated name, having checked only `Content-Type`. A file
    called `avatar.svg` (or `.html`) declaring `image/png` was therefore written
    with a markup extension into `templates/static/users`, which the static
    mount serves -- an avatar upload as a stored-XSS channel. The body was also
    read without a ceiling, so a single request could allocate as much memory
    as it liked.

    The replacement (`_save_staff_photo`) decides the extension from the
    declared type, requires the first bytes to match that type, and reads with
    a limit. These tests pin that function directly, for the same reason
    `test_upload_content.py` pins the other services' sanitizers: validation
    that only ever runs behind a multipart request is validation nobody runs.

    Runs from the UserServices root, which is where the module lives.
"""

from __future__ import annotations

import io
import pathlib
import sys

import pytest
from fastapi import HTTPException, UploadFile

SERVICE_ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(SERVICE_ROOT))

from resources import userController  # noqa: E402
from resources.userController import _save_staff_photo, _text  # noqa: E402

JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 16
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 16
HTML = b"<html><body><script>alert(document.domain)</script></body></html>"
SVG = b'<?xml version="1.0"?><svg onload="alert(1)"/>'


def upload(name: str, data: bytes, content_type: str) -> UploadFile:
    return UploadFile(filename=name, file=io.BytesIO(data), headers={"content-type": content_type})


def save(name: str, data: bytes, content_type: str) -> str:
    import asyncio
    return asyncio.run(_save_staff_photo(upload(name, data, content_type)))


@pytest.fixture(autouse=True)
def _nowhere_real(tmp_path, monkeypatch):
    """Never write into the service's real upload tree during a test run."""
    monkeypatch.setattr(userController, "UPLOAD_DIR", str(tmp_path))
    return tmp_path


def test_a_real_photo_is_stored_under_a_generated_name():
    stored = save("photo.png", PNG, "image/png")
    assert stored.startswith("/templates/static/users/user_")
    assert stored.endswith(".png")


def test_the_extension_comes_from_the_type_not_the_filename():
    """A .svg name with PNG bytes is stored as .png -- the name cannot win."""
    stored = save("avatar.svg", PNG, "image/png")
    assert stored.endswith(".png")
    assert ".svg" not in stored


def test_markup_declared_as_an_image_is_refused():
    for name in ("avatar.png", "avatar.svg", "avatar.html", "avatar"):
        with pytest.raises(HTTPException) as caught:
            save(name, HTML, "image/png")
        assert caught.value.status_code == 400
        assert "not a valid" in str(caught.value.detail).lower()


def test_a_type_outside_the_allow_list_is_refused():
    with pytest.raises(HTTPException) as caught:
        save("avatar.svg", SVG, "image/svg+xml")
    assert caught.value.status_code == 400
    assert "JPG and PNG" in str(caught.value.detail)


def test_a_missing_content_type_is_refused():
    with pytest.raises(HTTPException) as caught:
        save("avatar.png", PNG, "")
    assert caught.value.status_code == 400


def test_jpeg_bytes_must_claim_jpeg_and_png_bytes_must_claim_png():
    with pytest.raises(HTTPException):
        save("avatar.jpg", PNG, "image/jpeg")
    with pytest.raises(HTTPException):
        save("avatar.png", JPEG, "image/png")


def test_an_empty_upload_is_refused():
    with pytest.raises(HTTPException) as caught:
        save("avatar.png", b"", "image/png")
    assert caught.value.status_code == 400


def test_an_oversized_upload_is_refused_before_it_is_stored(_nowhere_real):
    too_big = PNG + b"\x00" * (userController.MAX_PHOTO_BYTES + 1)
    with pytest.raises(HTTPException) as caught:
        save("avatar.png", too_big, "image/png")
    assert caught.value.status_code == 413
    assert list(_nowhere_real.iterdir()) == []


def test_a_stored_photo_is_really_a_file_in_the_upload_dir(_nowhere_real):
    stored = save("photo.png", PNG, "image/png")
    on_disk = _nowhere_real / pathlib.Path(stored).name
    assert on_disk.is_file()
    assert on_disk.read_bytes() == PNG


def test_a_filename_cannot_escape_the_upload_dir(_nowhere_real, tmp_path):
    """The name is generated here, so a traversal attempt lands inside anyway."""
    stored = save("../../evil.png", PNG, "image/png")
    written = _nowhere_real / pathlib.Path(stored).name
    assert written.parent == _nowhere_real.resolve() or written.parent == _nowhere_real
    assert written.is_file()


# ---------------------------------------------------------------------------
# _text: JSON `null` reads as the default instead of raising.
# ---------------------------------------------------------------------------

def test_null_reads_as_the_default():
    assert _text({"description": None}, "description") == ""


def test_an_absent_key_reads_as_the_default():
    assert _text({}, "role_name", "") == ""
    assert _text({}, "role_name") == ""


def test_a_real_value_is_trimmed():
    assert _text({"role_name": "  Night Audit  "}, "role_name") == "Night Audit"


def test_a_number_is_accepted_as_text_rather_than_crashing_the_request():
    """The matrix used to send `description: 1`, and .strip() on an int 500'd."""
    assert _text({"description": 1}, "description") == "1"


def test_a_structured_value_is_a_400_not_a_500():
    for value in ({"a": 1}, ["b"]):
        with pytest.raises(HTTPException) as caught:
            _text({"description": value}, "description")
        assert caught.value.status_code == 400

"""Preflight check 6: does a deployment actually serve the images it stores?

    python -m pytest Backend/tests/test_preflight_images.py -v

WHY THIS SUITE EXISTS
    Restoring a release is two steps -- load the SQL, then copy
    `Backend/db/<release>/uploads/` into the services' static trees. The
    deployment at 168.231.103.18 did the first and not the second, so all 88
    image paths its API served resolved to nothing.

    Preflight's checks 1-5 passed throughout, because not one of them fetched
    an image. Check 6 does, and these assert it both catches that failure and
    stays quiet on a healthy deployment -- the half that is easy to get wrong,
    since a check that can only fail is no better than no check at all.

The HTTP layer is stubbed: the point is the decision logic, and a test that
needs a running server to say "images are missing" could not run in CI.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"


def load_preflight():
    """Import preflight.py by path -- it is a script, not an installed module."""
    spec = importlib.util.spec_from_file_location(
        "preflight_under_test", TOOLS / "preflight.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def pf():
    mod = load_preflight()
    mod.FAILS.clear()
    mod.WARNS.clear()
    return mod


# A list payload shaped like the ones the modules actually return: the image
# path is a value on a row, which is where check 6's regex has to find it.
def rows_with(path):
    return ('[{"id": 1, "name": "x", "image": "%s"}]' % path).encode()


IMG = "/templates/static/upload_image/abc123.jpg"


def install(pf, list_body, image_status, image_ctype):
    """Point check 6 at a fake deployment."""
    def fake_get(url, token=None, timeout=20):
        if "/templates/static/" in url:
            return image_status, b"irrelevant"
        return 200, list_body

    def fake_get_typed(url, token=None, timeout=20):
        if "/templates/static/" in url:
            return image_status, b"\xff\xd8\xff", image_ctype
        return 200, list_body, "application/json"

    pf.get = fake_get
    pf.get_typed = fake_get_typed


def test_missing_files_are_reported(pf):
    """The static tree was never populated: the API 404s the path it just served."""
    install(pf, rows_with(IMG), 404, "application/json")
    pf.check_images("host", 9010, "token")

    assert pf.FAILS, "a deployment serving 404 for every image must fail"
    assert any("stored images do not load" in f for f in pf.FAILS)


def test_missing_files_name_the_fix(pf, capsys):
    """An operator reading the output must be told what to run."""
    install(pf, rows_with(IMG), 404, "application/json")
    pf.check_images("host", 9010, "token")

    assert "restore_uploads.py" in capsys.readouterr().out


def test_healthy_deployment_passes(pf):
    """The half that matters: real image bytes must NOT be reported as broken."""
    install(pf, rows_with(IMG), 200, "image/jpeg")
    pf.check_images("host", 9010, "token")

    assert pf.FAILS == []


def test_json_body_under_a_200_is_not_an_image(pf):
    """A 200 carrying JSON is a proxy answering, not a file being served.

    Worth its own case: a gateway that rewrites a missing file into a friendly
    200 would otherwise read as success.
    """
    install(pf, rows_with(IMG), 200, "application/json")
    pf.check_images("host", 9010, "token")

    assert pf.FAILS, "content-type must decide, not the status alone"


def test_no_token_warns_rather_than_failing(pf):
    """Not being able to sign in is check 3's finding, not a broken image."""
    pf.check_images("host", 9010, None)

    assert pf.FAILS == []
    assert pf.WARNS


def test_a_module_with_no_stored_paths_is_skipped(pf):
    """An empty module proves nothing either way, so it must not fail."""
    install(pf, b"[]", 404, "application/json")
    pf.check_images("host", 9010, "token")

    assert pf.FAILS == []


def test_a_refused_module_is_skipped_not_failed(pf):
    """A low-privilege token is SUPPOSED to be refused; check 3 owns that."""
    def fake_get(url, token=None, timeout=20):
        return 403, b'{"detail":"Forbidden"}'

    pf.get = fake_get
    pf.check_images("host", 9010, "token")

    assert pf.FAILS == []

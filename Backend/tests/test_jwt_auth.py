"""Token verification invariants, run from inside any service directory.

The missing-claim cases matter most: python-jose ignores PyJWT's
`options={"require": [...]}` spelling, so an earlier fix that looked correct
silently accepted tokens that never expired.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from configs import BaseConfig
from resources.utils import verify_authentication

KEY = BaseConfig.SECRET_KEY
ALG = BaseConfig.ALGORITHM
ISS = BaseConfig.JWT_ISSUER

_now = datetime.now(timezone.utc)
IAT = int(_now.timestamp())
FUTURE = int((_now + timedelta(minutes=30)).timestamp())


class FakeRequest:
    """Minimal stand-in; `session` asserts, as it does without the middleware."""

    def __init__(self, token=None):
        self._token = token

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self._token}"} if self._token else {}

    @property
    def session(self):
        raise AssertionError("SessionMiddleware is not installed")


def sign(key=KEY, **claims):
    return jwt.encode(claims, key, algorithm=ALG)


def test_valid_token_is_accepted():
    token = sign(user_id=7, role_id=1, company_id="c1", iss=ISS, iat=IAT, exp=FUTURE)
    user_id, role_id, company_id, returned = verify_authentication(FakeRequest(token))
    assert (user_id, role_id, company_id) == (7, 1, "c1")
    assert returned == token


@pytest.mark.parametrize(
    "label, token",
    [
        ("no exp claim", sign(user_id=7, iss=ISS, iat=IAT)),
        ("no iat claim", sign(user_id=7, iss=ISS, exp=FUTURE)),
        ("wrong issuer", sign(user_id=7, iss="other", iat=IAT, exp=FUTURE)),
        (
            "expired",
            sign(
                user_id=7,
                iss=ISS,
                iat=int((_now - timedelta(hours=2)).timestamp()),
                exp=int((_now - timedelta(hours=1)).timestamp()),
            ),
        ),
        ("wrong signing key", sign(key="not-the-key", user_id=7, iss=ISS, iat=IAT, exp=FUTURE)),
        ("no user_id", sign(role_id=1, iss=ISS, iat=IAT, exp=FUTURE)),
        ("garbage string", "not-a-jwt"),
        ("empty bearer", ""),
        ("no header at all", None),
    ],
)
def test_token_is_rejected(label, token):
    with pytest.raises(HTTPException) as exc:
        verify_authentication(FakeRequest(token))
    assert exc.value.status_code == 401, label

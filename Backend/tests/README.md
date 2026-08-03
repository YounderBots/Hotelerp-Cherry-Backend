# Backend tests

These cover the security invariants the audit established. They need no MySQL
instance — the RBAC suite builds the schema in in-memory SQLite.

Each service is its own top-level package root (`configs`, `models`, `resources`
are imported absolutely), so the suites run from inside a service directory:

```bash
pip install pytest

cd Backend/Services/UserServices
ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_rbac.py -v

# The JWT suite is service-agnostic; run it against each service in turn.
for svc in LoginServices UserServices MasterDataServices \
           HotelServices RestaurantServices BarServices; do
  (cd "Backend/Services/$svc" && \
   ASCEND_ENV=dev DB_AUTO_CREATE=false python -m pytest ../../tests/test_jwt_auth.py -q)
done
```

`test_jwt_auth.py` asserts that a token is rejected when it lacks `exp` or
`iat`, carries the wrong issuer, has expired, or is signed with the wrong key.
The missing-claim cases are the ones that regressed silently before: python-jose
ignores PyJWT's `options={"require": [...]}` spelling, so a token that never
expired was accepted.

`test_rbac.py` asserts that `role_permissions` is actually consulted — most
importantly that a non-admin role cannot grant itself permissions, and that a
role from one company cannot act on another company's data.

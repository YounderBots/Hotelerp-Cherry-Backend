"""RBAC enforcement invariants. Run from Backend/Services/UserServices.

The escalation case is the reason this module exists: before enforcement,
`role_permissions` was written but never read, so any authenticated user could
POST to /role_permissions and grant their own role full access.
"""

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

import models.models as models
from resources.authorization import (
    has_permission,
    require_any_permission,
    require_permission,
)

ADMIN, HOUSEKEEPING, UNKNOWN_ROLE = 1, 3, 99
TENANT, OTHER_TENANT = "1", "2"


@pytest.fixture()
def db():
    """A real schema in in-memory SQLite — no MySQL required."""
    engine = sa.create_engine("sqlite://")
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    session.add_all([
        models.Menus(id=6, menu_name="HRM", menu_link="", order=6,
                     status="ACTIVE", created_by="1", company_id=TENANT),
        models.Submenus(id=43, menu_id="6", submenu_name="Roles",
                        submenu_link="/roles", order=1, status="ACTIVE",
                        created_by="1", company_id=TENANT),
        models.Submenus(id=131, menu_id="6", submenu_name="Employee",
                        submenu_link="/employee", order=2, status="ACTIVE",
                        created_by="1", company_id=TENANT),
        # Admin: full rights on /roles. Housekeeping: view only.
        models.RolePermissions(
            role_id="1", menu_id="6", submenu_id="43",
            view_permission=True, create_permission=True,
            edit_permission=True, delete_permission=True,
            status="ACTIVE", created_by="1", company_id=TENANT),
        models.RolePermissions(
            role_id="3", menu_id="6", submenu_id="43",
            view_permission=True, create_permission=False,
            edit_permission=False, delete_permission=False,
            status="ACTIVE", created_by="1", company_id=TENANT),
        # Housekeeping may work on /employee and nothing on /roles. An any-of
        # check has to answer from the one grant, not from the denial beside
        # it -- GET /users is reachable from seven different screens and the
        # gateway's map already treats that as "any of".
        models.RolePermissions(
            role_id="3", menu_id="6", submenu_id="131",
            view_permission=True, create_permission=True,
            edit_permission=False, delete_permission=False,
            status="ACTIVE", created_by="1", company_id=TENANT),
    ])
    session.commit()
    try:
        yield session
    finally:
        session.close()


def allowed(db, role, action, page="/roles", tenant=TENANT):
    try:
        require_permission(db, role, tenant, page, action)
        return True
    except HTTPException as exc:
        assert exc.status_code == 403
        return False


@pytest.mark.parametrize("action", ["view", "create", "edit", "delete"])
def test_admin_has_every_action(db, action):
    assert allowed(db, ADMIN, action)


def test_readonly_role_can_view(db):
    assert allowed(db, HOUSEKEEPING, "view")


@pytest.mark.parametrize("action", ["create", "edit", "delete"])
def test_readonly_role_cannot_escalate(db, action):
    """The headline case: a view-only role must not grant itself permissions."""
    assert not allowed(db, HOUSEKEEPING, action)


def test_role_with_no_permission_row_is_denied(db):
    assert not allowed(db, UNKNOWN_ROLE, "view")


def test_tenants_are_isolated(db):
    """Admin of company 1 has no rights inside company 2."""
    assert not allowed(db, ADMIN, "create", tenant=OTHER_TENANT)


def test_unconfigured_page_fails_closed(db):
    """A page missing from the menu tables must not become the open one."""
    assert not allowed(db, ADMIN, "view", page="/not-configured")
    assert has_permission(db, ADMIN, TENANT, "/not-configured", "view") is None


def test_missing_claims_are_denied(db):
    assert not allowed(db, None, "view")
    assert has_permission(db, ADMIN, None, "/roles", "view") is False


def test_unknown_action_is_a_programming_error(db):
    with pytest.raises(ValueError):
        has_permission(db, ADMIN, TENANT, "/roles", "approve")


# ---------------------------------------------------------------------------
# require_any_permission: an endpoint reachable from several screens.
# ---------------------------------------------------------------------------

def allowed_any(db, role, pages, action, tenant=TENANT):
    try:
        require_any_permission(db, role, tenant, pages, action)
        return True, None
    except HTTPException as exc:
        assert exc.status_code == 403
        return False, str(exc.detail)


def test_any_one_grant_in_the_list_is_enough(db):
    """Housekeeping is denied on /roles but holds /employee -- allowed."""
    assert allowed_any(db, HOUSEKEEPING, ("/roles", "/employee"), "create")[0]


def test_a_denial_stands_when_no_page_in_the_list_grants_it(db):
    ok, detail = allowed_any(db, HOUSEKEEPING, ("/roles", "/employee"), "delete")
    assert not ok
    assert "does not have" in detail


def test_one_unconfigured_page_does_not_excuse_a_denial(db):
    """Fail closed, but say the true thing: the page exists, the role is denied."""
    ok, detail = allowed_any(db, HOUSEKEEPING, ("/not-configured", "/roles"), "delete")
    assert not ok
    assert "not configured" not in detail


def test_every_page_unconfigured_fails_closed_with_the_config_message(db):
    ok, detail = allowed_any(db, ADMIN, ("/nope-a", "/nope-b"), "view")
    assert not ok
    assert "not configured" in detail


def test_an_empty_page_list_is_a_programming_error(db):
    with pytest.raises(ValueError):
        require_any_permission(db, ADMIN, TENANT, (), "view")


def test_the_staff_directory_rule_matches_the_gateway_map(db):
    """The seven pages ROUTE_PERMISSIONS names for GET /user/users.

    Granted on any one of them is enough; Front Desk, which holds none, is
    refused -- which is exactly what the gateway's enforce mode already says.
    """
    pages = ("/bar_roster", "/bar_shift_planning", "/employee",
             "/restaurant_roster", "/restaurant_shift_planning",
             "/room_incident_log", "/task_assign")
    assert allowed_any(db, HOUSEKEEPING, pages, "view")[0]
    assert not allowed_any(db, UNKNOWN_ROLE, pages, "view")[0]

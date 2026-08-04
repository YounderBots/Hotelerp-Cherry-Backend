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
from resources.authorization import has_permission, require_permission

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

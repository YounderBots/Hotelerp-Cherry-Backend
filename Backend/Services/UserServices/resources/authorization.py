"""Server-side RBAC enforcement.

The `role_permissions` table has always described who may view/create/edit/delete
each page, but nothing ever consulted it on the API side: `verify_authentication`
returned a `role_id` that every controller then ignored. Permissions were applied
only when the SPA decided which menu entries to render, so any authenticated
user — a housekeeper, say — could call `POST /role_permissions` directly and
grant their own role full access to the entire system.

Permissions are keyed by page link (`/roles`, `/user`, ...), matching how the
data is modelled and how the SPA consumes it, so nothing here hardcodes menu ids
— those differ per tenant.

Scope note: this module is applied to the user/role/menu administration surface,
where the mapping from endpoint to page is unambiguous. The operational services
(hotel, restaurant, bar, masterdata) need the same treatment, but their
endpoint-to-page mapping does not exist in the schema and has to be authored
deliberately rather than guessed.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models.models as models
from configs.base_config import CommonWords

logger = logging.getLogger(__name__)

VIEW, CREATE, EDIT, DELETE = "view", "create", "edit", "delete"

_ACTION_FIELD = {
    VIEW: "view_permission",
    CREATE: "create_permission",
    EDIT: "edit_permission",
    DELETE: "delete_permission",
}

# Escape hatch for staged rollout. Enforcement is on by default: an operator has
# to opt *out* deliberately, rather than a missing variable silently disabling
# every check.
ENFORCE = os.getenv("RBAC_ENFORCE", "true").lower() in ("1", "true", "yes")


def _forbidden(page_link: str, action: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Your role does not have {action} permission for {page_link}.",
    )


def has_permission(
    db: Session,
    role_id,
    company_id,
    page_link: str,
    action: str,
) -> Optional[bool]:
    """True/False if the page is known to this tenant, None if it is not.

    None is distinct from False so the caller can tell "this role is denied"
    apart from "this tenant has no such page configured", which is a data
    problem an operator needs to see rather than a permission decision.
    """
    field = _ACTION_FIELD.get(action)
    if field is None:
        raise ValueError(f"unknown action: {action}")

    if role_id is None or company_id is None:
        return False

    role_id, company_id = str(role_id), str(company_id)

    # A page is normally a submenu; top-level pages (e.g. /dashboard) are menus.
    submenu = (
        db.query(models.Submenus)
        .filter(
            models.Submenus.submenu_link == page_link,
            models.Submenus.company_id == company_id,
            models.Submenus.status == CommonWords.STATUS,
        )
        .first()
    )

    query = db.query(models.RolePermissions).filter(
        models.RolePermissions.role_id == role_id,
        models.RolePermissions.company_id == company_id,
        models.RolePermissions.status == CommonWords.STATUS,
    )

    if submenu is not None:
        permission = query.filter(
            models.RolePermissions.menu_id == str(submenu.menu_id),
            models.RolePermissions.submenu_id == str(submenu.id),
        ).first()
    else:
        menu = (
            db.query(models.Menus)
            .filter(
                models.Menus.menu_link == page_link,
                models.Menus.company_id == company_id,
                models.Menus.status == CommonWords.STATUS,
            )
            .first()
        )
        if menu is None:
            return None
        permission = query.filter(
            models.RolePermissions.menu_id == str(menu.id),
            models.RolePermissions.submenu_id.is_(None),
        ).first()

    if permission is None:
        return False
    return bool(getattr(permission, field, False))


def require_permission(
    db: Session,
    role_id,
    company_id,
    page_link: str,
    action: str,
) -> None:
    """Raises 403 unless `role_id` may perform `action` on `page_link`."""
    if not ENFORCE:
        return

    allowed = has_permission(db, role_id, company_id, page_link, action)

    if allowed is None:
        # Fail closed. Granting access because a page is missing from the menu
        # tables would make a misconfigured tenant the most permissive one.
        logger.error(
            "rbac_page_not_configured page=%s company=%s role=%s action=%s",
            page_link, company_id, role_id, action,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Page '{page_link}' is not configured for this company, so "
                "permissions for it cannot be resolved. Add it under Menus / "
                "Submenus and grant the role access."
            ),
        )

    if not allowed:
        logger.info(
            "rbac_denied page=%s company=%s role=%s action=%s",
            page_link, company_id, role_id, action,
        )
        raise _forbidden(page_link, action)

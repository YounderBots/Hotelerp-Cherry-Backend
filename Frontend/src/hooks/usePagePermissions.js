import { useMemo } from "react";

import { useAuth } from "../Context/AuthContext";

/**
 * The signed-in role's view/add/edit/delete rights for one page.
 *
 * WHY THIS EXISTS
 * The login payload has always carried per-page permissions — the sidebar uses
 * them to decide which entries to draw, and RequirePage uses them to gate the
 * route. Nothing used them *inside* a page, so a role holding only `view` was
 * shown an "Add" button and a full row of Edit/Delete icons, and found out it
 * could not use them only when the gateway answered 403.
 *
 * RowActions has carried `canView` / `canEdit` / `canDelete` props since it was
 * written, with no caller. This is what they were for.
 *
 * THIS IS NOT THE SECURITY CONTROL
 * The gateway authorises every request against the `perm` claim in the JWT
 * (Backend/Services/LoginServices/resources/rbac.py). Hiding a control the
 * server would refuse is a usability measure on top of that, never instead of
 * it.
 *
 * FAILING OPEN
 * An empty menu payload means the permissions service did not answer at login,
 * not that the user has no rights. RequirePage already falls open in that case
 * for exactly this reason; falling closed here instead would turn a transient
 * upstream blip into a silently read-only application, which is far harder to
 * diagnose than a 403.
 *
 * USAGE
 *     const perms = usePagePermissions("/guest_enquiry");
 *     {perms.add && <AddButton />}
 *     <RowActions canEdit={perms.edit} canDelete={perms.delete} ... />
 */

const ALL = Object.freeze({ view: true, add: true, edit: true, delete: true });
const NONE = Object.freeze({ view: false, add: false, edit: false, delete: false });

const findByPath = (nodes, path) => {
    if (!Array.isArray(nodes)) return null;
    for (const node of nodes) {
        if (node?.path === path) return node;
        const hit = findByPath(node?.children, path);
        if (hit) return hit;
    }
    return null;
};

export function usePagePermissions(path) {
    const { menus } = useAuth();

    return useMemo(() => {
        if (!Array.isArray(menus) || menus.length === 0) return ALL;

        const node = findByPath(menus, path);
        // A populated payload that omits this page means the role genuinely
        // does not hold it. RequirePage will normally have shown the "no
        // access" panel before the page mounted; this is the same answer for
        // any caller that runs outside a gated route.
        if (!node) return NONE;

        const permissions = node.permissions || {};
        return {
            view: !!permissions.view,
            add: !!permissions.add,
            edit: !!permissions.edit,
            delete: !!permissions.delete,
        };
    }, [menus, path]);
}

export default usePagePermissions;

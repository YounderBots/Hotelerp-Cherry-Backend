import { useLocation } from "react-router-dom";
import { useAuth } from "../Context/AuthContext";
import "./ErrorBoundary.css";

/**
 * Route-level permission gate.
 *
 * The RBAC payload from login was only ever used to decide which menu entries
 * to draw, so any authenticated user could reach any page by typing its URL —
 * the navigation was filtered but the routes were not.
 *
 * This is a usability guard, not the security control: the API is what
 * actually enforces access. Hiding a page the server would refuse anyway keeps
 * a user from walking into a screen full of 403s.
 */

/**
 * Routes that are never gated by the menu tree.
 *
 * These have no menu row on purpose -- they are reached from the avatar menu,
 * not the sidebar -- so gating on the menu tree would deny them to everyone,
 * an owner holding every permission included.
 *
 *   /dashboard  the post-login landing page and the target of every "go back"
 *               affordance
 *   /profile    the signed-in user's own record
 *   /settings   their own password
 *
 * The hidden `/view` floor detail route is checked against the visible
 * `/floor_layout` permission instead of being ungated. It has no sidebar row,
 * but a role without floor-layout access must receive the same clear denial as
 * it receives for the parent screen rather than an empty “no floor” shell.
 * `/ReservationView` remains ungated for its stateful reservation row action;
 * its API calls remain authorised by the gateway.
 *
 * The last two mirror the gateway's ALWAYS_ALLOW set, and for the same reason:
 * `/user/me` and `/user/me/password` take no user id, so they can only ever
 * reach the caller's own row and there is nothing here a page permission would
 * be protecting.
 */
const UNGATED = new Set([
  "/dashboard",
  "/profile",
  "/settings",
  // Stateful reservation detail surface reached from a permitted list screen.
  "/ReservationView",
]);

// Lower-cased copy of the same set, so the check below does not depend on how
// the visitor typed the URL.
const UNGATED_LOWER = new Set(Array.from(UNGATED, (path) => path.toLowerCase()));

const collectPaths = (nodes, into = new Set()) => {
    if (!Array.isArray(nodes)) return into;
    for (const node of nodes) {
        // A menu path is not permission proof. The permissions payload can
        // contain a page with view=false; drawing its row while allowing a
        // direct URL produced a page full of controls the gateway would refuse.
        // Older menu payloads had no permissions object, so absence remains
        // backwards-compatible and is treated as allowed.
        const view = node?.permissions?.view;
        // Stored lower-cased: React Router matches routes case-insensitively, so
        // `/Identification_Proof` mounts the page component while a byte-exact
        // comparison here answered "no access" to a user who holds the
        // permission (C-081).
        if (node?.path && (view === undefined || view === true)) into.add(node.path.toLowerCase());
        if (Array.isArray(node?.children)) collectPaths(node.children, into);
    }
    return into;
};

const Denied = () => (
    <div className="error-boundary">
        <div className="error-boundary__panel">
            <h2 className="error-boundary__title">You do not have access to this page</h2>
            <p className="error-boundary__message">
                Your role does not include this section. If you believe this is a
                mistake, ask an administrator to review your permissions.
            </p>
            <div className="error-boundary__actions">
                <a className="error-boundary__btn error-boundary__btn--primary" href="/dashboard">
                    Go to dashboard
                </a>
            </div>
        </div>
    </div>
);

const RequirePage = ({ children }) => {
    const { menus } = useAuth();
    const location = useLocation();

    // No menu payload means the permissions service did not answer at login.
    // Falling open is deliberate: falling closed would lock every user out of
    // the entire app over a transient upstream failure, and the API still
    // enforces access on each request.
    if (!Array.isArray(menus) || menus.length === 0) return children;

    const allowed = collectPaths(menus);

    // Compared case-insensitively for the same reason as `collectPaths`: the
    // router already treats `/Identification_Proof` as `/identification_proof`,
    // so gating on the raw bytes denied a page the user can see in the sidebar.
    const current = (location.pathname || "").toLowerCase();

    if (UNGATED_LOWER.has(current)) return children;

    // The floor view is a hidden child of Floor Layout. Gate it by the
    // parent's permission so direct URLs cannot expose a misleading empty
    // screen to roles that cannot read the underlying floor data.
    const requiredPath = current === "/view" ? "/floor_layout" : current;
    return allowed.has(requiredPath) ? children : <Denied />;
};

export default RequirePage;

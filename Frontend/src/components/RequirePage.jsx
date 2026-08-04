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

const collectPaths = (nodes, into = new Set()) => {
    if (!Array.isArray(nodes)) return into;
    for (const node of nodes) {
        if (node?.path) into.add(node.path);
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

    // The dashboard is the post-login landing page and the target of every
    // "go back" affordance, so it must never be gated.
    if (location.pathname === "/dashboard") return children;

    return allowed.has(location.pathname) ? children : <Denied />;
};

export default RequirePage;

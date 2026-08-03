import { Link } from "react-router-dom";
import "./ErrorBoundary.css";

/**
 * Catch-all for unmatched routes.
 *
 * Without this, a typo or a stale bookmark matched no <Route> and React Router
 * rendered nothing — the shell appeared with an empty content area and no
 * indication anything had gone wrong.
 */
const NotFound = () => (
    <div className="error-boundary">
        <div className="error-boundary__panel">
            <h2 className="error-boundary__title">Page not found</h2>
            <p className="error-boundary__message">
                The page you are looking for does not exist, or it may have been moved.
            </p>
            <div className="error-boundary__actions">
                <Link className="error-boundary__btn error-boundary__btn--primary" to="/dashboard">
                    Go to dashboard
                </Link>
            </div>
        </div>
    </div>
);

export default NotFound;

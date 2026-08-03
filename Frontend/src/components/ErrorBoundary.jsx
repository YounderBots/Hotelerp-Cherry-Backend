import React from "react";
import "./ErrorBoundary.css";

/**
 * Catches render-time errors from the subtree.
 *
 * The app previously declared an `ErrorBoundaryFallback` component and never
 * mounted it, so there was no boundary anywhere: a single throw in any page
 * unmounted the whole tree and left a blank white page with no way back.
 *
 * Chunk-load failures are treated separately because they are the common case
 * in production rather than a code defect — after a deploy, an open tab still
 * holds the old chunk manifest and lazy imports 404. Reloading genuinely fixes
 * that, so the copy says so.
 */
const isChunkLoadError = (error) => {
    const text = `${error?.name || ""} ${error?.message || ""}`;
    return (
        /ChunkLoadError/i.test(text) ||
        /Loading (CSS )?chunk .* failed/i.test(text) ||
        /Failed to fetch dynamically imported module/i.test(text) ||
        /error loading dynamically imported module/i.test(text)
    );
};

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { error: null };
    }

    static getDerivedStateFromError(error) {
        return { error };
    }

    componentDidCatch(error, errorInfo) {
        // Kept as console.error deliberately: it is the only signal a developer
        // gets locally, and it is where a real error reporter would be wired in.
        console.error("Unhandled render error:", error, errorInfo);
    }

    componentDidUpdate(prevProps) {
        // A boundary that stays broken after navigation traps the user on the
        // error screen, so reset when the route key changes.
        if (this.state.error && prevProps.resetKey !== this.props.resetKey) {
            this.setState({ error: null });
        }
    }

    handleRetry = () => this.setState({ error: null });

    handleReload = () => window.location.reload();

    render() {
        const { error } = this.state;
        if (!error) return this.props.children;

        const stale = isChunkLoadError(error);

        return (
            <div className="error-boundary" role="alert">
                <div className="error-boundary__panel">
                    <h2 className="error-boundary__title">
                        {stale ? "This page is out of date" : "Something went wrong"}
                    </h2>
                    <p className="error-boundary__message">
                        {stale
                            ? "The application was updated while this tab was open. Reload to get the latest version."
                            : "This section failed to load. You can try again, or go back to the dashboard."}
                    </p>

                    <div className="error-boundary__actions">
                        {stale ? (
                            <button type="button" className="error-boundary__btn error-boundary__btn--primary" onClick={this.handleReload}>
                                Reload page
                            </button>
                        ) : (
                            <>
                                <button type="button" className="error-boundary__btn error-boundary__btn--primary" onClick={this.handleRetry}>
                                    Try again
                                </button>
                                <a className="error-boundary__btn" href="/dashboard">
                                    Go to dashboard
                                </a>
                            </>
                        )}
                    </div>

                    {import.meta.env?.DEV && (
                        <pre className="error-boundary__details">{String(error?.stack || error)}</pre>
                    )}
                </div>
            </div>
        );
    }
}

export default ErrorBoundary;

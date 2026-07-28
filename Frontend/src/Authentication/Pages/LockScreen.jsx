import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash, FaExclamationCircle, FaSpinner, FaUserCircle } from "react-icons/fa";

import "./LockScreen.css";
import logo from "../../assets/layout/Cherry.png";
import { useAuth } from "../../Context/AuthContext";
import APICall, { ApiError } from "../../APICalls/APICalls";

const isSafeInternalPath = (path) =>
  typeof path === "string" &&
  path.startsWith("/") &&
  !path.startsWith("//") &&
  !path.includes("\r") &&
  !path.includes("\n");

const messageForApi = (err) => {
  if (err instanceof ApiError) {
    if (err.status === 401) return "Password did not match. Please try again.";
    if (err.status === 429) return "Too many attempts. Please wait a minute and try again.";
    if (err.status === 502 || err.status === 503) return "Authentication service is unavailable. Please try again shortly.";
    if (err.code === "timeout") return "The request timed out. Please try again.";
    if (err.code === "network") return "Cannot reach the server. Check your connection.";
    return err.message || "Could not unlock the session. Please try again.";
  }
  return "Could not unlock the session. Please try again.";
};

const displayName = (user) => {
  if (!user || typeof user !== "object") return "Signed in user";
  return user.name || user.username || user.email || user.company_email || "Signed in user";
};

const displayEmail = (user) => {
  if (!user || typeof user !== "object") return "";
  return user.email || user.company_email || "";
};

const initials = (name) => {
  if (!name) return "?";
  const parts = String(name).trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

const LockScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, login, logout, isAuthenticated } = useAuth();

  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [capsOn, setCapsOn] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const mounted = useRef(true);

  const nextParam = new URLSearchParams(location.search).get("next");
  const safeNext = isSafeInternalPath(nextParam) ? nextParam : null;
  const email = displayEmail(user);
  const name = displayName(user);

  useEffect(() => {
    mounted.current = true;
    // There is nothing to "unlock" without a signed-in user. Send the visitor
    // back to the full login flow, preserving the intended destination.
    if (!isAuthenticated() || !email) {
      const nxt = safeNext ? `?next=${encodeURIComponent(safeNext)}` : "";
      navigate(`/${nxt}`, { replace: true });
    }
    return () => { mounted.current = false; };
  }, [isAuthenticated, email, navigate, safeNext]);

  const handleCapsCheck = (e) => {
    if (typeof e.getModifierState === "function") {
      setCapsOn(e.getModifierState("CapsLock"));
    }
  };

  const canSubmit = password.length >= 1 && !loading;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setError("");
    setLoading(true);
    try {
      const data = await APICall.postWT("/login_post", { email, password });
      if (!data || !data.access_token) {
        setError("Unlock response was malformed. Please try again.");
        return;
      }
      login(data);
      if (!mounted.current) return;

      const serverRedirect = data.redirect_url;
      const target =
        safeNext ||
        (isSafeInternalPath(serverRedirect) && serverRedirect !== "/"
          ? serverRedirect
          : "/dashboard");
      navigate(target, { replace: true });
    } catch (err) {
      if (!mounted.current) return;
      setError(messageForApi(err));
    } finally {
      if (mounted.current) setLoading(false);
    }
  };

  const handleSignOut = () => {
    logout();
    navigate("/", { replace: true });
  };

  if (!email) {
    // While the redirect effect runs, render nothing to avoid flashing the
    // locked shell with placeholder data.
    return null;
  }

  return (
    <div className="auth-page lock-page">
      <div className="auth-card lock-card" role="main" aria-labelledby="lock-heading">

        <div className="lock-logo-wrap">
          <img src={logo} alt="Cherry Hotel ERP" />
        </div>

        <div className="lock-avatar" aria-hidden="true">
          <FaUserCircle className="lock-avatar-fallback" />
          <span className="lock-avatar-initials">{initials(name)}</span>
        </div>

        <div className="auth-header">
          <h2 id="lock-heading">{name}</h2>
          <p className="lock-email">{email}</p>
          <p className="lock-subtitle">Session locked. Enter your password to continue.</p>
        </div>

        {error && (
          <div className="error-text" role="alert" aria-live="assertive">
            <FaExclamationCircle aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group password-group">
            <label htmlFor="lock-password">Password</label>
            <div className="password-input-wrap">
              <input
                id="lock-password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); if (error) setError(""); }}
                onKeyUp={handleCapsCheck}
                onKeyDown={handleCapsCheck}
                disabled={loading}
                minLength={1}
                maxLength={255}
                required
                autoFocus
                aria-invalid={Boolean(error)}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                aria-pressed={showPassword}
                disabled={loading}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </button>
            </div>
            {capsOn && (
              <div className="auth-hint" role="status">Caps Lock is on</div>
            )}
          </div>

          <button
            type="submit"
            className="primary-btn"
            disabled={!canSubmit}
            aria-busy={loading}
          >
            {loading ? (
              <>
                <FaSpinner className="spin" aria-hidden="true" />
                <span>Unlocking…</span>
              </>
            ) : (
              <span>Unlock</span>
            )}
          </button>
        </form>

        <div className="auth-footer-row">
          <button
            type="button"
            className="auth-link-button"
            onClick={handleSignOut}
            disabled={loading}
          >
            Sign in as a different user
          </button>
        </div>

        <div className="auth-footer">
          <Link className="auth-link inline" to="/authentication/forgotpassword">
            Forgot password?
          </Link>
          <span className="dot" aria-hidden="true">•</span>
          <span>© 2026 Cherry</span>
        </div>
      </div>
    </div>
  );
};

export default LockScreen;

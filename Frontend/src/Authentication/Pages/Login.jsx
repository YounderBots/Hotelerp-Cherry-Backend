import React, { useEffect, useRef, useState } from "react";
import "./Login.css";
import logo from "../../assets/layout/Cherry.png";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../Context/AuthContext";
import APICall, { ApiError } from "../../APICalls/APICalls";
import { FaEye, FaEyeSlash, FaCheckCircle, FaExclamationCircle } from "react-icons/fa";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const isSafeInternalPath = (path) =>
  typeof path === "string" &&
  path.startsWith("/") &&
  !path.startsWith("//") &&
  !path.includes("\r") &&
  !path.includes("\n");

const messageForApi = (err) => {
  if (err instanceof ApiError) {
    if (err.status === 401) return "Invalid email or password.";
    if (err.status === 429) return "Too many attempts. Please wait a minute and try again.";
    if (err.status === 502 || err.status === 503) return "The authentication service is unavailable. Please try again shortly.";
    if (err.code === "timeout") return "The request timed out. Please try again.";
    if (err.code === "network") return "Cannot reach the server. Check your connection.";
    return err.message || "Login failed. Please try again.";
  }
  return "Login failed. Please try again.";
};

const displayName = (user) => {
  if (!user || typeof user !== "object") return "back";
  return user.name || user.username || user.email || user.company_email || "back";
};

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [capsOn, setCapsOn] = useState(false);
  const mounted = useRef(true);

  const nextParam = new URLSearchParams(location.search).get("next");
  const safeNext = isSafeInternalPath(nextParam) ? nextParam : null;

  useEffect(() => {
    mounted.current = true;
    if (isAuthenticated()) {
      navigate(safeNext || "/dashboard", { replace: true });
    }
    return () => { mounted.current = false; };
  }, [isAuthenticated, navigate, safeNext]);

  const handleCapsCheck = (e) => {
    if (typeof e.getModifierState === "function") {
      setCapsOn(e.getModifierState("CapsLock"));
    }
  };

  const canSubmit =
    email.trim().length > 0 && password.length >= 1 && !loading;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setError("");
    setSuccess("");

    const trimmedEmail = email.trim().toLowerCase();
    if (!EMAIL_RE.test(trimmedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      const data = await APICall.postWT("/login_post", {
        email: trimmedEmail,
        password,
      });

      if (!data || !data.access_token) {
        setError("Login response was malformed. Please try again.");
        return;
      }

      login(data);

      if (!mounted.current) return;

      setSuccess(`Welcome ${displayName(data.user)}`);

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

  return (
    <div className="auth-page">
      <div className="auth-card" role="main" aria-labelledby="login-heading">

        {/* LOGO */}
        <div className="auth-logo-wrap">
          <img src={logo} alt="Cherry Hotel ERP" />
        </div>

        {/* HEADER */}
        <div className="auth-header">
          <h2 id="login-heading">Welcome Back</h2>
          <p>Sign in to access your dashboard</p>
        </div>

        {/* ERROR */}
        {error && (
          <div className="error-text" role="alert" aria-live="assertive">
            <FaExclamationCircle aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        {/* SUCCESS */}
        {success && !error && (
          <div className="success-text" role="status" aria-live="polite">
            <FaCheckCircle aria-hidden="true" />
            <span>{success}</span>
          </div>
        )}

        {/* FORM */}
        <form className="auth-form" onSubmit={handleSubmit} noValidate>

          {/* EMAIL */}
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              inputMode="email"
              placeholder="you@hotel.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              maxLength={100}
              required
              aria-invalid={Boolean(error)}
              aria-describedby={error ? "login-error" : undefined}
            />
          </div>

          {/* PASSWORD */}
          <div className="form-group password-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrap">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyUp={handleCapsCheck}
                onKeyDown={handleCapsCheck}
                disabled={loading}
                minLength={1}
                maxLength={255}
                required
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

          {/* ROW LINKS */}
          <div className="auth-row-links">
            <Link className="auth-link" to="/authentication/forgotpassword">
              Forgot password?
            </Link>
          </div>

          {/* SUBMIT */}
          <button
            type="submit"
            className="primary-btn"
            disabled={!canSubmit}
            aria-busy={loading}
          >
            {loading ? "Signing in…" : "Login"}
          </button>

        </form>

        {/* FOOTER */}
        <div className="auth-footer-row">
          <span>Don't have an account?</span>
          <Link className="auth-link" to="/authentication/register">
            Request access
          </Link>
        </div>

        <div className="auth-footer">© 2026 Cherry</div>

      </div>
    </div>
  );
};

export default Login;

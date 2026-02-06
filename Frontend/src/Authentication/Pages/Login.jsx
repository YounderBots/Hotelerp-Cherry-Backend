import React, { useState } from "react";
import "./Login.css";
import logo from "../../assets/layout/Cherry.png";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../Context/AuthContext";
import APICall from "../../APICalls/APICalls";
import { FaEye, FaEyeSlash, FaCheckCircle } from "react-icons/fa";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // ---------------- VALIDATION ----------------
    if (!email || !password) {
      setError("Email and Password are required");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    try {
      setLoading(true);

      // ---------------- API CALL ----------------
      const data = await APICall.postWT("/login_post", {
        email,
        password,
      });

      // ---------------- ROLE DETECTION ----------------
      const roleName =
        data?.role_name ||
        data?.role ||
        data?.user_role ||
        data?.user?.role ||
        data?.user?.role_name ||
        "Admin";

      // ---------------- SUCCESS UI ----------------
      setSuccess(`Login successful! Welcome ${roleName}`);

      // Save auth data
      login(data);

      // Smooth redirect
      setTimeout(() => {
        navigate(data.redirect_url || "/");
      }, 1300);

    } catch (err) {
      setError(err?.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* LOGO */}
        <div className="auth-logo-wrap">
          <img src={logo} alt="Cherry Logo" />
        </div>

        {/* HEADER */}
        <div className="auth-header">
          <h2>Welcome Back</h2>
          <p>Sign in to access your dashboard</p>
        </div>

        {/* ERROR MESSAGE */}
        {error && <p className="error-text">{error}</p>}

        {/* SUCCESS MESSAGE */}
        {success && (
          <div className="success-text">
            <FaCheckCircle /> {success}
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
              required
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
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
                required
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />

              <span
                className="password-toggle"
                tabIndex={-1}
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </span>
            </div>
          </div>

          {/* SUBMIT BUTTON */}
          <button
            type="submit"
            className="primary-btn"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>

        {/* FOOTER */}
        <div className="auth-footer">
          © 2026 Cherry
        </div>

      </div>
    </div>
  );
};

export default Login;

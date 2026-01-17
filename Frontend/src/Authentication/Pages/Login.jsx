import React from "react";
import "./Authentication.css";
import { Link } from "react-router-dom";

const Login = () => {
  return (
    <div className="auth-page">

      <div className="auth-card">

        {/* ================= HEADER ================= */}
        <div className="auth-header">
          <h2>Welcome Back</h2>
          <p>Please login to continue</p>
        </div>

        {/* ================= FORM ================= */}
        <form className="auth-form">

          {/* EMAIL */}
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              placeholder="Enter your email"
              required
            />
          </div>

          {/* PASSWORD */}
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              required
            />
          </div>

          {/* LOGIN BUTTON */}
          <Link to="/dashboard/admin" className="btn-link">
            <button type="button" className="primary-btn">
              Login
            </button>
          </Link>

        </form>

        {/* ================= FOOTER ================= */}
        <div className="auth-footer">
          <span>© 2026 Hotel ERP</span>
        </div>

      </div>

    </div>
  );
};

export default Login;

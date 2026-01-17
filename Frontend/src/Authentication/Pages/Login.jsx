import React, { useState } from "react";
import "./Login.css";
import logo from "../../assets/layout/Cherry.png";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* LOGO */}
        <div className="auth-logo-wrap">
          <img src={logo} alt="Logo" />
        </div>

        {/* HEADER */}
        <div className="auth-header">
          <h2>Welcome Back</h2>
          <p>Please login to continue</p>
        </div>

        {/* FORM */}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="primary-btn">
            Login
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

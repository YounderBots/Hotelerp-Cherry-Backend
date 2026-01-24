import React, { useState } from "react";
import "./Login.css";
import logo from "../../assets/layout/Cherry.png";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../Context/AuthContext";
import APICall from "../../APICalls/APICalls";
import { FaEye, FaEyeSlash } from "react-icons/fa";

const Login = () => {
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // 🔹 Frontend validations
    if (!email || !password) {
      setError("Email and Password are required");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Enter a valid email address");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    try {
      const data = await APICall.postWT("/login_post", {
        email,
        password,
      });

      login(data);
      navigate(data.redirect_url || "/");
    } catch (err) {
      setError(err?.response?.data?.error || "Login failed");
    }
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

        {/* ERROR */}
        {error && <p className="error-text">{error}</p>}

        {/* FORM */}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group password-group">
            <label>Password</label>
            <div className="password-input-wrap">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <span
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </span>
            </div>
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

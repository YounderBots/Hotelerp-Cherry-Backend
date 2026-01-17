import React from "react";
import "./Authentication.css";

const Register = () => {
  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-header">
          <h2>Create Account</h2>
          <p>Register to get started</p>
        </div>

        <form className="auth-form">
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" placeholder="Enter full name" required />
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <input type="email" placeholder="Enter email" required />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input type="password" placeholder="Create password" required />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input type="password" placeholder="Confirm password" required />
          </div>

          <div className="form-options">
            <label className="checkbox">
              <input type="checkbox" required />
              I agree to Terms & Conditions
            </label>
          </div>

          <button className="primary-btn">Register</button>
        </form>

        <div className="auth-footer">
          <span>
            Already have an account? <span className="link-text">Login</span>
          </span>
        </div>

      </div>
    </div>
  );
};

export default Register;

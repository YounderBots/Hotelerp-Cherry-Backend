import React from "react";
import "./Authentication.css";

const ForgotPassword = () => {
  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-header">
          <h2>Forgot Password</h2>
          <p>We’ll send a reset link to your email</p>
        </div>

        <form className="auth-form">
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" placeholder="Enter registered email" required />
          </div>

          <button className="primary-btn">Send Reset Link</button>
        </form>

        <div className="auth-footer">
          <span className="link-text">Back to Login</span>
        </div>

      </div>
    </div>
  );
};

export default ForgotPassword;

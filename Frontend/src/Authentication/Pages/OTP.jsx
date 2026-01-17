import React from "react";
import "./Authentication.css";

const OTP = () => {
  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-header">
          <h2>OTP Verification</h2>
          <p>Enter the 6-digit OTP sent to your email</p>
        </div>

        <form className="auth-form otp-form">
          <div className="otp-inputs">
            <input maxLength="1" />
            <input maxLength="1" />
            <input maxLength="1" />
            <input maxLength="1" />
            <input maxLength="1" />
            <input maxLength="1" />
          </div>

          <button className="primary-btn">Verify OTP</button>
        </form>

        <div className="auth-footer">
          <span className="link-text">Resend OTP</span>
        </div>

      </div>
    </div>
  );
};

export default OTP;

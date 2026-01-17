import React from "react";
import "./Authentication.css";

const LockScreen = () => {
  return (
    <div className="auth-page">
      <div className="auth-card lock-card">

        <div className="user-avatar">
          <img
            src="https://images.unsplash.com/photo-1603415526960-f7e0328c63b1?w=100"
            alt="User"
          />
        </div>

        <div className="auth-header">
          <h2>Johan Abraham</h2>
          <p>Session Locked</p>
        </div>

        <form className="auth-form">
          <div className="form-group">
            <label>Password</label>
            <input type="password" placeholder="Enter password" required />
          </div>

          <button className="primary-btn">Unlock</button>
        </form>

      </div>
    </div>
  );
};

export default LockScreen;

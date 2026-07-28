import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCheckCircle, FaExclamationCircle, FaSpinner } from "react-icons/fa";

import "./ForgotPassword.css";
import logo from "../../assets/layout/Cherry.png";
import { useAuth } from "../../Context/AuthContext";

const ADMIN_CONTACT_EMAIL =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_ADMIN_CONTACT_EMAIL) ||
  "admin@hotel.com";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const buildMailto = (email) => {
  const subject = `Password reset request — ${email}`;
  const bodyLines = [
    `A user has requested a password reset.`,
    ``,
    `Account email: ${email}`,
    ``,
    `Please verify the requester and reset their password in HRM.`,
    ``,
    `— Sent from the Cherry Hotel ERP password-reset form`,
  ];
  const params = new URLSearchParams({
    subject,
    body: bodyLines.join("\n"),
  });
  return `mailto:${ADMIN_CONTACT_EMAIL}?${params.toString()}`;
};

const ForgotPassword = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [email, setEmail] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    if (isAuthenticated()) {
      navigate("/dashboard", { replace: true });
    }
    return () => { mounted.current = false; };
  }, [isAuthenticated, navigate]);

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    if (fieldError) setFieldError("");
    if (submitError) setSubmitError("");
  };

  const canSubmit = email.trim().length > 0 && !submitting && !submitted;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    const trimmed = email.trim().toLowerCase();
    if (!EMAIL_RE.test(trimmed)) {
      setFieldError("Enter a valid email address.");
      const el = document.getElementById("fp-email");
      if (el) el.focus();
      return;
    }
    if (trimmed.length > 100) {
      setFieldError("Email must be under 100 characters.");
      return;
    }

    setSubmitting(true);
    try {
      window.location.href = buildMailto(trimmed);
      if (mounted.current) setSubmitted(true);
    } catch {
      if (mounted.current) {
        setSubmitError("Could not open your email client. Please email us directly.");
      }
    } finally {
      if (mounted.current) setSubmitting(false);
    }
  };

  const disabled = submitting || submitted;

  return (
    <div className="auth-page forgot-page">
      <div className="auth-card forgot-card" role="main" aria-labelledby="fp-heading">

        <div className="auth-logo-wrap">
          <img src={logo} alt="Cherry Hotel ERP" />
        </div>

        <div className="auth-header">
          <h2 id="fp-heading">Forgot Password</h2>
          <p>
            Password resets are handled by your administrator. Enter the email
            on your Cherry account and we&rsquo;ll prepare a request for them.
          </p>
        </div>

        {submitError && (
          <div className="error-text" role="alert" aria-live="assertive">
            <FaExclamationCircle aria-hidden="true" />
            <span>{submitError}</span>
          </div>
        )}

        {submitted && !submitError && (
          <div className="success-text" role="status" aria-live="polite">
            <FaCheckCircle aria-hidden="true" />
            <span>
              Your reset request has been prepared in your email client. If
              nothing opened, email{" "}
              <a className="auth-link inline" href={`mailto:${ADMIN_CONTACT_EMAIL}`}>
                {ADMIN_CONTACT_EMAIL}
              </a>{" "}
              directly.
            </span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="fp-email">Email Address</label>
            <input
              id="fp-email"
              name="email"
              type="email"
              autoComplete="email"
              inputMode="email"
              placeholder="you@hotel.com"
              value={email}
              onChange={handleEmailChange}
              disabled={disabled}
              maxLength={100}
              aria-invalid={Boolean(fieldError)}
              aria-describedby={fieldError ? "fp-email-err" : undefined}
              required
              autoFocus
            />
            {fieldError && (
              <div className="field-error" id="fp-email-err" role="alert">
                {fieldError}
              </div>
            )}
          </div>

          <button
            type="submit"
            className="primary-btn"
            disabled={!canSubmit}
            aria-busy={submitting}
          >
            {submitting ? (
              <>
                <FaSpinner className="spin" aria-hidden="true" />
                <span>Sending…</span>
              </>
            ) : submitted ? (
              <span>Request sent</span>
            ) : (
              <span>Send reset request</span>
            )}
          </button>
        </form>

        <div className="auth-footer-row">
          <Link className="auth-link back-link" to="/">
            <FaArrowLeft aria-hidden="true" />
            <span>Back to sign in</span>
          </Link>
        </div>

        <div className="auth-footer">© 2026 Cherry</div>
      </div>
    </div>
  );
};

export default ForgotPassword;

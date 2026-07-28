import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaCheckCircle, FaExclamationCircle, FaSpinner } from "react-icons/fa";

import "./Register.css";
import logo from "../../assets/layout/Cherry.png";
import { useAuth } from "../../Context/AuthContext";

const ADMIN_CONTACT_EMAIL =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_ADMIN_CONTACT_EMAIL) ||
  "admin@hotel.com";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+\d][\d\s\-()]{6,19}$/;

const initialForm = {
  fullName: "",
  workEmail: "",
  companyName: "",
  phone: "",
  notes: "",
  agree: false,
};

const validate = (form) => {
  const errors = {};

  const name = form.fullName.trim();
  if (!name || name.length < 2) {
    errors.fullName = "Please enter your full name (at least 2 characters).";
  } else if (name.length > 100) {
    errors.fullName = "Full name must be under 100 characters.";
  }

  const email = form.workEmail.trim();
  if (!email) errors.workEmail = "Work email is required.";
  else if (email.length > 100) errors.workEmail = "Email must be under 100 characters.";
  else if (!EMAIL_RE.test(email)) errors.workEmail = "Enter a valid email address.";

  const company = form.companyName.trim();
  if (!company || company.length < 2) {
    errors.companyName = "Please enter your hotel or company name.";
  } else if (company.length > 120) {
    errors.companyName = "Hotel/company name must be under 120 characters.";
  }

  const phone = form.phone.trim();
  if (phone && !PHONE_RE.test(phone)) {
    errors.phone = "Enter a valid phone number, digits and + - ( ) only.";
  }

  if (form.notes.length > 1000) {
    errors.notes = "Notes must be under 1000 characters.";
  }

  if (!form.agree) {
    errors.agree = "You must accept the Terms & Privacy Policy.";
  }

  return errors;
};

const buildMailto = (form) => {
  const subject = `Access request — ${form.fullName.trim()} (${form.companyName.trim()})`;
  const bodyLines = [
    `Name: ${form.fullName.trim()}`,
    `Work email: ${form.workEmail.trim().toLowerCase()}`,
    `Hotel / Company: ${form.companyName.trim()}`,
    form.phone.trim() ? `Phone: ${form.phone.trim()}` : null,
    "",
    "Notes:",
    form.notes.trim() || "(none)",
    "",
    "— Sent from the Cherry Hotel ERP access-request form",
  ].filter(Boolean);
  const params = new URLSearchParams({
    subject,
    body: bodyLines.join("\n"),
  });
  return `mailto:${ADMIN_CONTACT_EMAIL}?${params.toString()}`;
};

const Register = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
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

  const setField = (field) => (e) => {
    const value = field === "agree" ? e.target.checked : e.target.value;
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
    if (submitError) setSubmitError("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (submitting || submitted) return;

    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const el = document.getElementById(`reg-${firstKey}`);
      if (el && typeof el.focus === "function") el.focus();
      return;
    }

    setSubmitting(true);
    try {
      const href = buildMailto(form);
      window.location.href = href;
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
    <div className="auth-page register-page">
      <div className="auth-card register-card" role="main" aria-labelledby="reg-heading">

        <div className="auth-logo-wrap">
          <img src={logo} alt="Cherry Hotel ERP" />
        </div>

        <div className="auth-header">
          <h2 id="reg-heading">Request Access</h2>
          <p>
            Cherry is an internal Hotel ERP. Accounts are provisioned by your
            administrator. Fill in your details and we&rsquo;ll route your
            request.
          </p>
        </div>

        {submitError && (
          <div className="error-text" role="alert" aria-live="assertive">
            <FaExclamationCircle aria-hidden="true" />
            <span>{submitError}</span>
          </div>
        )}

        {submitted && (
          <div className="success-text" role="status" aria-live="polite">
            <FaCheckCircle aria-hidden="true" />
            <span>
              Your access request has been prepared in your email client. If
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
            <label htmlFor="reg-fullName">Full Name</label>
            <input
              id="reg-fullName"
              name="fullName"
              type="text"
              autoComplete="name"
              placeholder="e.g. Priya Sharma"
              value={form.fullName}
              onChange={setField("fullName")}
              disabled={disabled}
              maxLength={100}
              aria-invalid={Boolean(errors.fullName)}
              aria-describedby={errors.fullName ? "reg-fullName-err" : undefined}
              required
            />
            {errors.fullName && (
              <div className="field-error" id="reg-fullName-err" role="alert">
                {errors.fullName}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="reg-workEmail">Work Email</label>
            <input
              id="reg-workEmail"
              name="workEmail"
              type="email"
              autoComplete="email"
              inputMode="email"
              placeholder="you@hotel.com"
              value={form.workEmail}
              onChange={setField("workEmail")}
              disabled={disabled}
              maxLength={100}
              aria-invalid={Boolean(errors.workEmail)}
              aria-describedby={errors.workEmail ? "reg-workEmail-err" : undefined}
              required
            />
            {errors.workEmail && (
              <div className="field-error" id="reg-workEmail-err" role="alert">
                {errors.workEmail}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="reg-companyName">Hotel / Company Name</label>
            <input
              id="reg-companyName"
              name="companyName"
              type="text"
              autoComplete="organization"
              placeholder="e.g. Grand Cherry Blossom Resort"
              value={form.companyName}
              onChange={setField("companyName")}
              disabled={disabled}
              maxLength={120}
              aria-invalid={Boolean(errors.companyName)}
              aria-describedby={errors.companyName ? "reg-companyName-err" : undefined}
              required
            />
            {errors.companyName && (
              <div className="field-error" id="reg-companyName-err" role="alert">
                {errors.companyName}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="reg-phone">
              Phone <span className="optional">(optional)</span>
            </label>
            <input
              id="reg-phone"
              name="phone"
              type="tel"
              autoComplete="tel"
              inputMode="tel"
              placeholder="+91 98765 43210"
              value={form.phone}
              onChange={setField("phone")}
              disabled={disabled}
              maxLength={20}
              aria-invalid={Boolean(errors.phone)}
              aria-describedby={errors.phone ? "reg-phone-err" : undefined}
            />
            {errors.phone && (
              <div className="field-error" id="reg-phone-err" role="alert">
                {errors.phone}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="reg-notes">
              Notes <span className="optional">(optional)</span>
            </label>
            <textarea
              id="reg-notes"
              name="notes"
              rows={3}
              placeholder="Tell us about your role or which modules you need"
              value={form.notes}
              onChange={setField("notes")}
              disabled={disabled}
              maxLength={1000}
              aria-invalid={Boolean(errors.notes)}
              aria-describedby={errors.notes ? "reg-notes-err" : "reg-notes-count"}
            />
            <div className="field-help">
              {errors.notes ? (
                <span className="field-error" id="reg-notes-err" role="alert">
                  {errors.notes}
                </span>
              ) : (
                <span className="field-hint" id="reg-notes-count">
                  {form.notes.length} / 1000
                </span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label className="checkbox-row" htmlFor="reg-agree">
              <input
                id="reg-agree"
                name="agree"
                type="checkbox"
                checked={form.agree}
                onChange={setField("agree")}
                disabled={disabled}
                aria-invalid={Boolean(errors.agree)}
                aria-describedby={errors.agree ? "reg-agree-err" : undefined}
                required
              />
              <span>
                I agree to the{" "}
                <a
                  className="auth-link inline"
                  href="/terms"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Terms
                </a>{" "}
                &amp;{" "}
                <a
                  className="auth-link inline"
                  href="/privacy"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </a>
                .
              </span>
            </label>
            {errors.agree && (
              <div className="field-error" id="reg-agree-err" role="alert">
                {errors.agree}
              </div>
            )}
          </div>

          <button
            type="submit"
            className="primary-btn"
            disabled={disabled}
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
              <span>Request access</span>
            )}
          </button>
        </form>

        <div className="auth-footer-row">
          <span>Already have an account?</span>
          <Link className="auth-link" to="/">Sign in</Link>
        </div>

        <div className="auth-footer">© 2026 Cherry</div>
      </div>
    </div>
  );
};

export default Register;

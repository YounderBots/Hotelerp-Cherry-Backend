import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCheckCircle, FaExclamationCircle, FaSpinner } from "react-icons/fa";

import "./OTP.css";
import logo from "../../assets/layout/Cherry.png";
import { useAuth } from "../../Context/AuthContext";
import APICall, { ApiError } from "../../APICalls/APICalls";

const CODE_LENGTH = 6;
const EXPIRY_SECONDS = 5 * 60;   // 5-minute code validity
const RESEND_COOLDOWN_SECONDS = 45;

const DIGIT_RE = /^[0-9]$/;

const isSafeInternalPath = (path) =>
  typeof path === "string" &&
  path.startsWith("/") &&
  !path.startsWith("//") &&
  !path.includes("\r") &&
  !path.includes("\n");

const messageForApi = (err) => {
  if (err instanceof ApiError) {
    if (err.status === 400) return "The code you entered is invalid. Please try again.";
    if (err.status === 401) return "The code was rejected. Please try again.";
    if (err.status === 404) return "Two-factor authentication is not enabled on this backend yet. Contact your administrator.";
    if (err.status === 410) return "This code has expired. Please request a new one.";
    if (err.status === 429) return "Too many attempts. Please wait a moment and try again.";
    if (err.status === 501) return "Two-factor authentication is not implemented yet. Contact your administrator.";
    if (err.status === 503) return "Verification service is unavailable. Please try again shortly.";
    if (err.code === "timeout") return "The request timed out. Please try again.";
    if (err.code === "network") return "Cannot reach the server. Check your connection.";
    return err.message || "Could not verify the code. Please try again.";
  }
  return "Could not verify the code. Please try again.";
};

const formatMMSS = (totalSeconds) => {
  if (totalSeconds <= 0) return "0:00";
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
};

const OTP = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  const query = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const challengeId = query.get("challenge_id") || "";
  const channelParam = (query.get("channel") || "email").toLowerCase();
  const maskedTarget = query.get("target") || "";
  const nextParam = query.get("next");
  const safeNext = isSafeInternalPath(nextParam) ? nextParam : null;

  const [digits, setDigits] = useState(() => Array(CODE_LENGTH).fill(""));
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);
  const [expirySeconds, setExpirySeconds] = useState(EXPIRY_SECONDS);
  const [resendCooldown, setResendCooldown] = useState(RESEND_COOLDOWN_SECONDS);

  const inputRefs = useRef([]);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    if (isAuthenticated()) {
      navigate(safeNext || "/dashboard", { replace: true });
    }
    return () => { mounted.current = false; };
  }, [isAuthenticated, navigate, safeNext]);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  // Expiry countdown
  useEffect(() => {
    if (expirySeconds <= 0) return undefined;
    const id = setInterval(() => {
      setExpirySeconds((s) => (s <= 1 ? 0 : s - 1));
    }, 1000);
    return () => clearInterval(id);
  }, [expirySeconds]);

  // Resend cooldown countdown
  useEffect(() => {
    if (resendCooldown <= 0) return undefined;
    const id = setInterval(() => {
      setResendCooldown((s) => (s <= 1 ? 0 : s - 1));
    }, 1000);
    return () => clearInterval(id);
  }, [resendCooldown]);

  const code = digits.join("");
  const expired = expirySeconds <= 0;
  const canSubmit = code.length === CODE_LENGTH && !submitting && !expired;

  const clearInlineMessages = () => {
    if (error) setError("");
    if (success) setSuccess("");
  };

  const focusIndex = (idx) => {
    const bounded = Math.max(0, Math.min(CODE_LENGTH - 1, idx));
    const el = inputRefs.current[bounded];
    if (el) el.focus();
  };

  const handleDigitChange = (idx) => (e) => {
    clearInlineMessages();
    const raw = e.target.value;
    if (raw === "") {
      setDigits((prev) => {
        const next = [...prev];
        next[idx] = "";
        return next;
      });
      return;
    }
    // Handle rapid multi-char (autofill / IME) into a single slot by
    // spreading across subsequent slots.
    const stripped = raw.replace(/\D/g, "");
    if (!stripped) return;

    setDigits((prev) => {
      const next = [...prev];
      let cursor = idx;
      for (let i = 0; i < stripped.length && cursor < CODE_LENGTH; i += 1, cursor += 1) {
        next[cursor] = stripped[i];
      }
      // Move focus to the first empty slot after the last one we filled,
      // or the last-filled slot if all are full.
      const nextFocus = Math.min(idx + stripped.length, CODE_LENGTH - 1);
      queueMicrotask(() => focusIndex(nextFocus));
      return next;
    });
  };

  const handleKeyDown = (idx) => (e) => {
    if (e.key === "Backspace") {
      if (digits[idx]) {
        // Clear this slot; keep focus here.
        setDigits((prev) => {
          const next = [...prev];
          next[idx] = "";
          return next;
        });
        clearInlineMessages();
      } else if (idx > 0) {
        // Empty slot → jump back and clear that one.
        e.preventDefault();
        setDigits((prev) => {
          const next = [...prev];
          next[idx - 1] = "";
          return next;
        });
        focusIndex(idx - 1);
        clearInlineMessages();
      }
      return;
    }
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      focusIndex(idx - 1);
      return;
    }
    if (e.key === "ArrowRight") {
      e.preventDefault();
      focusIndex(idx + 1);
      return;
    }
    if (e.key === "Home") {
      e.preventDefault();
      focusIndex(0);
      return;
    }
    if (e.key === "End") {
      e.preventDefault();
      focusIndex(CODE_LENGTH - 1);
      return;
    }
    // Block non-digit keys silently (except common navigation/paste combos).
    if (
      e.key.length === 1 &&
      !e.metaKey && !e.ctrlKey && !e.altKey &&
      !DIGIT_RE.test(e.key)
    ) {
      e.preventDefault();
    }
  };

  const handlePaste = (idx) => (e) => {
    const pasted = (e.clipboardData?.getData("text") || "").replace(/\D/g, "");
    if (!pasted) return;
    e.preventDefault();
    clearInlineMessages();
    setDigits((prev) => {
      const next = [...prev];
      let cursor = idx;
      for (let i = 0; i < pasted.length && cursor < CODE_LENGTH; i += 1, cursor += 1) {
        next[cursor] = pasted[i];
      }
      const nextFocus = Math.min(idx + pasted.length, CODE_LENGTH - 1);
      queueMicrotask(() => focusIndex(nextFocus));
      return next;
    });
  };

  const handleSubmit = useCallback(async (e) => {
    e?.preventDefault?.();
    if (!canSubmit) return;
    setError("");
    setSuccess("");
    setSubmitting(true);
    try {
      const data = await APICall.postWT("/verify_otp", {
        challenge_id: challengeId || undefined,
        code,
      });
      if (!mounted.current) return;
      setSuccess("Verified. Redirecting…");
      const target =
        safeNext ||
        (isSafeInternalPath(data?.redirect_url) ? data.redirect_url : "/dashboard");
      navigate(target, { replace: true });
    } catch (err) {
      if (!mounted.current) return;
      setError(messageForApi(err));
    } finally {
      if (mounted.current) setSubmitting(false);
    }
  }, [canSubmit, challengeId, code, navigate, safeNext]);

  // Auto-submit once all 6 slots are filled (nice UX for pasted codes).
  useEffect(() => {
    if (code.length === CODE_LENGTH && !submitting && !expired && !success) {
      handleSubmit();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, expired]);

  const handleResend = async () => {
    if (resendCooldown > 0 || resending) return;
    setError("");
    setSuccess("");
    setResending(true);
    try {
      await APICall.postWT("/resend_otp", {
        challenge_id: challengeId || undefined,
        channel: channelParam,
      });
      if (!mounted.current) return;
      setSuccess("A new code has been sent.");
      setDigits(Array(CODE_LENGTH).fill(""));
      setExpirySeconds(EXPIRY_SECONDS);
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
      focusIndex(0);
    } catch (err) {
      if (!mounted.current) return;
      setError(messageForApi(err));
    } finally {
      if (mounted.current) setResending(false);
    }
  };

  const channelLabel = channelParam === "sms" ? "phone" : "email";

  return (
    <div className="auth-page otp-page">
      <div className="auth-card otp-card" role="main" aria-labelledby="otp-heading">

        <div className="auth-logo-wrap">
          <img src={logo} alt="Cherry Hotel ERP" />
        </div>

        <div className="auth-header">
          <h2 id="otp-heading">Verify your identity</h2>
          <p>
            Enter the 6-digit code we sent to your {channelLabel}
            {maskedTarget ? <> at <strong>{maskedTarget}</strong></> : null}.
          </p>
        </div>

        {error && (
          <div className="error-text" role="alert" aria-live="assertive">
            <FaExclamationCircle aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        {success && !error && (
          <div className="success-text" role="status" aria-live="polite">
            <FaCheckCircle aria-hidden="true" />
            <span>{success}</span>
          </div>
        )}

        {!challengeId && !error && !success && (
          <div className="info-text" role="status">
            <span>
              This page verifies a code from an active sign-in challenge. If you
              landed here directly, please <Link className="auth-link inline" to="/">sign in</Link> to receive a code.
            </span>
          </div>
        )}

        <form className="auth-form otp-form" onSubmit={handleSubmit} noValidate>
          <div
            className="otp-inputs"
            role="group"
            aria-labelledby="otp-heading"
            aria-describedby="otp-timer"
          >
            {digits.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => { inputRefs.current[idx] = el; }}
                type="text"
                inputMode="numeric"
                autoComplete={idx === 0 ? "one-time-code" : "off"}
                pattern="[0-9]*"
                maxLength={CODE_LENGTH /* accept pastes; we still enforce 1 digit visible */}
                value={digit}
                onChange={handleDigitChange(idx)}
                onKeyDown={handleKeyDown(idx)}
                onPaste={handlePaste(idx)}
                onFocus={(e) => e.target.select()}
                disabled={submitting || expired}
                aria-label={`Digit ${idx + 1} of ${CODE_LENGTH}`}
                aria-invalid={Boolean(error)}
              />
            ))}
          </div>

          <div className="otp-meta" id="otp-timer">
            {expired ? (
              <span className="otp-expired">Your code has expired.</span>
            ) : (
              <span>Code expires in <strong>{formatMMSS(expirySeconds)}</strong></span>
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
                <span>Verifying…</span>
              </>
            ) : (
              <span>Verify code</span>
            )}
          </button>
        </form>

        <div className="auth-footer-row">
          <button
            type="button"
            className="auth-link-button"
            onClick={handleResend}
            disabled={resending || resendCooldown > 0}
            aria-busy={resending}
          >
            {resending
              ? "Resending…"
              : resendCooldown > 0
                ? `Resend in ${resendCooldown}s`
                : "Resend code"}
          </button>
        </div>

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

export default OTP;

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff, KeyRound, User as UserIcon } from "lucide-react";

import APICall from "../APICalls/APICalls";
import { errMsg } from "../functions/apiHelpers";
import { useToast } from "../hooks/useToast";
import ErrorAlert from "../stories/ErrorAlert";
import Toast from "../stories/Toast";
import "./Account.css";

/**
 * Account settings for the signed-in user.
 *
 * WHAT IS HERE, AND WHAT IS NOT
 *   Only the settings that are genuinely the account holder's own and that the
 *   API can actually act on. Today that is the password.
 *
 *   Deliberately NOT a page of switches for things nothing reads: there is no
 *   per-user preferences table, so a theme picker or a notification toggle
 *   here would be a control that changes nothing -- the same reason the
 *   GROUP_RESERVATION option was taken out of the Reservation form. When
 *   per-user preferences exist server-side, this is where they belong.
 */

// Kept in step with PASSWORD_MIN_LENGTH in UserServices/resources/
// userController.py. Validated in both places on purpose: here so the user is
// told before a round trip, there because the browser is not the authority.
const PASSWORD_MIN_LENGTH = 8;

const Settings = () => {
  const navigate = useNavigate();
  const { toast, showToast } = useToast();

  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [reveal, setReveal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const set = (key) => (e) => {
    setForm((f) => ({ ...f, [key]: e.target.value }));
    setError(null);
  };

  // The mismatch is worth saying as the user types rather than on submit --
  // finding out after pressing the button means retyping all three.
  const mismatch =
    form.confirm_password.length > 0 && form.new_password !== form.confirm_password;

  const tooShort =
    form.new_password.length > 0 && form.new_password.length < PASSWORD_MIN_LENGTH;

  const unchanged =
    form.new_password.length > 0 && form.new_password === form.current_password;

  const canSubmit =
    form.current_password &&
    form.new_password &&
    form.confirm_password &&
    !mismatch &&
    !tooShort &&
    !unchanged &&
    !saving;

  const submit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setSaving(true);
    setError(null);
    try {
      await APICall.putT("/user/me/password", {
        current_password: form.current_password,
        new_password: form.new_password,
      });
      setForm({ current_password: "", new_password: "", confirm_password: "" });
      setReveal(false);
      showToast("success", "Your password has been changed.");
    } catch (err) {
      setError(errMsg(err, "The password could not be changed."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="account-page">
      <div className="account-toolbar">
        <button
          type="button"
          className="account-back"
          onClick={() => navigate(-1)}
          aria-label="Go back"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="account-toolbar-actions">
          <button
            type="button"
            className="account-btn"
            onClick={() => navigate("/profile")}
          >
            <UserIcon size={16} aria-hidden="true" />
            <span>Profile</span>
          </button>
        </div>
      </div>

      <header className="account-header">
        <h1>Settings</h1>
        <p>Your account, on this device and everywhere you sign in.</p>
      </header>

      <section className="acct-card acct-card--narrow">
        <h2 className="acct-card__title">
          <KeyRound size={15} aria-hidden="true" />
          <span>Change Password</span>
        </h2>
        <form className="account-form" onSubmit={submit} noValidate>
          <ErrorAlert message={error} />

          <div className="account-field">
            <label className="account-label" htmlFor="current-password">
              Current password
            </label>
            <input
              id="current-password"
              className="account-input"
              type={reveal ? "text" : "password"}
              value={form.current_password}
              onChange={set("current_password")}
              autoComplete="current-password"
              required
            />
            <p className="account-hint">
              Asked for even though you are signed in — it is what tells your
              account apart from whoever is standing at your screen.
            </p>
          </div>

          <div className="account-field">
            <label className="account-label" htmlFor="new-password">
              New password
            </label>
            <input
              id="new-password"
              className="account-input"
              type={reveal ? "text" : "password"}
              value={form.new_password}
              onChange={set("new_password")}
              autoComplete="new-password"
              aria-invalid={tooShort || unchanged}
              aria-describedby="new-password-hint"
              required
            />
            <p
              id="new-password-hint"
              className={`account-hint${tooShort || unchanged ? " error" : ""}`}
            >
              {unchanged
                ? "Choose something different from your current password."
                : `At least ${PASSWORD_MIN_LENGTH} characters.`}
            </p>
          </div>

          <div className="account-field">
            <label className="account-label" htmlFor="confirm-password">
              Confirm new password
            </label>
            <input
              id="confirm-password"
              className="account-input"
              type={reveal ? "text" : "password"}
              value={form.confirm_password}
              onChange={set("confirm_password")}
              autoComplete="new-password"
              aria-invalid={mismatch}
              aria-describedby="confirm-password-hint"
              required
            />
            <p
              id="confirm-password-hint"
              className={`account-hint${mismatch ? " error" : ""}`}
              role={mismatch ? "alert" : undefined}
            >
              {mismatch ? "The two passwords do not match." : "Type it once more."}
            </p>
          </div>

          <div className="account-form-actions">
            <button
              type="button"
              className="account-btn"
              onClick={() => setReveal((v) => !v)}
              aria-pressed={reveal}
            >
              {reveal ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
              <span>{reveal ? "Hide" : "Show"} passwords</span>
            </button>
            <button type="submit" className="account-btn primary" disabled={!canSubmit}>
              {saving ? "Changing…" : "Change password"}
            </button>
          </div>
        </form>
      </section>

      <Toast {...toast} />
    </div>
  );
};

export default Settings;

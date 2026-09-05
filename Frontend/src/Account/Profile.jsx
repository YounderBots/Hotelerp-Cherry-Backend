import React from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft, RefreshCw, Settings as SettingsIcon,
  Mail, Phone, CalendarDays, Clock, IdCard, ShieldAlert, Briefcase,
} from "lucide-react";

import APICall from "../APICalls/APICalls";
import { useApiResource } from "../hooks/useApiResource";
import useAuthedMedia from "../hooks/useAuthedMedia";
import ErrorAlert from "../stories/ErrorAlert";
import { formatDate } from "../functions/formatters";
import "./Account.css";

/**
 * The signed-in user's own record.
 *
 * WHY IT DOES NOT REUSE THE HRM EMPLOYEE SCREEN
 *   /employee reads and writes ANY employee and is gated behind the HRM page
 *   permission, which most roles do not hold. This reads `/user/me`, which
 *   takes no id and resolves the row from the token, so a Front Desk clerk
 *   can see their own record without being able to see anyone else's.
 *
 * WHY IT DOES NOT USE DetailList
 *   DetailList lays out on `auto-fit, minmax(190px, 1fr)`, which is right for
 *   a modal: the column count follows the modal's width. On a full-width page
 *   it means every section computes a DIFFERENT column count from its own item
 *   count -- four fields here, five there -- so no two sections lined up and a
 *   lone fourth field stretched across half the row. This page uses one fixed
 *   grid for every section instead, so the columns are a single rhythm down
 *   the page.
 */

const initials = (name) => {
  const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

/** One label/value pair. `wide` spans the full row for long free text. */
const Field = ({ label, value, wide = false }) => {
  const empty = value === null || value === undefined || value === "";
  return (
    <div className={`acct-field${wide ? " acct-field--wide" : ""}`}>
      <dt>{label}</dt>
      <dd className={empty ? "is-empty" : undefined}>{empty ? "—" : value}</dd>
    </div>
  );
};

const Card = ({ title, icon: Icon, children }) => (
  <section className="acct-card">
    <h2 className="acct-card__title">
      {Icon && <Icon size={15} aria-hidden="true" />}
      <span>{title}</span>
    </h2>
    <dl className="acct-grid">{children}</dl>
  </section>
);

const Profile = () => {
  const navigate = useNavigate();

  const { data: me, loading, error, reload } = useApiResource(
    () => APICall.getT("/user/me"),
    {
      select: (res) => res?.data || null,
      initial: null,
      fallback: "Your profile could not be loaded.",
    },
  );

  // The photo sits behind the authenticated gateway proxy, so a plain <img
  // src> is answered 401 -- see hooks/useAuthedMedia.js.
  const photo = useAuthedMedia(me?.photo || null, "/user");

  const fullName =
    [me?.first_name, me?.last_name].filter(Boolean).join(" ").trim() ||
    me?.username ||
    "—";

  const shift = me?.shift_name
    ? `${me.shift_name}${me.shift_start ? ` · ${me.shift_start}–${me.shift_end}` : ""}`
    : null;

  const address =
    [me?.address, me?.city, me?.state, me?.postal_code, me?.country]
      .filter(Boolean)
      .join(", ") || null;

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
          <button type="button" className="account-btn" onClick={reload} disabled={loading}>
            <RefreshCw size={16} aria-hidden="true" />
            <span>Refresh</span>
          </button>
          <button
            type="button"
            className="account-btn primary"
            onClick={() => navigate("/settings")}
          >
            <SettingsIcon size={16} aria-hidden="true" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      <ErrorAlert message={error} />

      {loading && (
        <div className="account-loading" role="status" aria-live="polite">
          Loading your profile…
        </div>
      )}

      {me && (
        <div className="account-layout">
          {/* Identity stays beside the detail on a wide screen rather than
              stacked above it: it is short, and stacking left a band of empty
              space to its right on anything above ~1100px. */}
          <aside className="acct-identity">
            <span className="acct-avatar">
              {photo.url ? (
                <img src={photo.url} alt="" />
              ) : (
                <span className="acct-avatar__initials" aria-hidden="true">
                  {initials(fullName)}
                </span>
              )}
            </span>

            <h1 className="acct-name">{fullName}</h1>
            <p className="acct-title">
              {me.designation_name || me.role_name || "Staff"}
            </p>
            {me.department_name && (
              <p className="acct-dept">{me.department_name}</p>
            )}

            <div className="acct-tags">
              {me.role_name && <span className="acct-tag is-role">{me.role_name}</span>}
              {me.user_code && <span className="acct-tag is-code">{me.user_code}</span>}
            </div>

            <dl className="acct-quick">
              {shift && (
                <div>
                  <Clock size={14} aria-hidden="true" />
                  <dt className="sr-only">Shift</dt>
                  <dd>{shift}</dd>
                </div>
              )}
              {me.date_of_joining && (
                <div>
                  <CalendarDays size={14} aria-hidden="true" />
                  <dt className="sr-only">Joined</dt>
                  <dd>Joined {formatDate(me.date_of_joining)}</dd>
                </div>
              )}
              {me.mobile && (
                <div>
                  <Phone size={14} aria-hidden="true" />
                  <dt className="sr-only">Mobile</dt>
                  <dd>{me.mobile}</dd>
                </div>
              )}
              {me.company_email && (
                <div>
                  <Mail size={14} aria-hidden="true" />
                  <dt className="sr-only">Company email</dt>
                  <dd className="is-truncate" title={me.company_email}>
                    {me.company_email}
                  </dd>
                </div>
              )}
            </dl>
          </aside>

          <div className="account-main">
            <Card title="Account" icon={IdCard}>
              <Field label="Username" value={me.username} />
              <Field label="Role" value={me.role_name} />
              <Field label="Employee Code" value={me.user_code} />
              <Field label="Company Email" value={me.company_email} />
              <Field label="Personal Email" value={me.personal_email} />
            </Card>

            <Card title="Work" icon={Briefcase}>
              <Field label="Department" value={me.department_name} />
              <Field label="Designation" value={me.designation_name} />
              <Field label="Shift" value={shift} />
              <Field label="Date of Joining" value={formatDate(me.date_of_joining)} />
              <Field label="Experience" value={me.experience} />
            </Card>

            <Card title="Contact" icon={Phone}>
              <Field label="Mobile" value={me.mobile} />
              <Field label="Alternative Mobile" value={me.alternative_mobile} />
              <Field label="Date of Birth" value={me.dob} />
              <Field label="Address" value={address} wide />
            </Card>

            <Card title="In an Emergency" icon={ShieldAlert}>
              <Field label="Contact Name" value={me.emergency_name} />
              <Field label="Relationship" value={me.emergency_relationship} />
              <Field label="Phone" value={me.emergency_contact} />
            </Card>

            <p className="account-note">
              Your role, department and shift are maintained by HR — ask them to
              change anything on this page. Your password is yours to change,
              under{" "}
              <button
                type="button"
                className="account-link"
                onClick={() => navigate("/settings")}
              >
                Settings
              </button>
              .
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;

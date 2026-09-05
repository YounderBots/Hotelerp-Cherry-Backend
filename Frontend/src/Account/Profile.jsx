import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, RefreshCw, Settings as SettingsIcon } from "lucide-react";

import APICall from "../APICalls/APICalls";
import { useApiResource } from "../hooks/useApiResource";
import useAuthedMedia from "../hooks/useAuthedMedia";
import ViewSection from "../stories/ViewSection";
import DetailList, { DetailItem } from "../stories/DetailList";
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
 * READ-ONLY, DELIBERATELY
 *   Who someone reports to, what they are paid and which role they hold are
 *   HRM's to change, not the employee's. The one thing here that IS the
 *   account holder's own is their password, and that lives on the Settings
 *   page next door.
 */
const initials = (name) => {
  const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

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
            onClick={reload}
            disabled={loading}
          >
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
        <>
          <header className="account-header">
            <span className="account-avatar" aria-hidden="true">
              {photo.url ? (
                <img src={photo.url} alt="" />
              ) : (
                <span className="account-avatar-initials">{initials(fullName)}</span>
              )}
            </span>
            <div className="account-identity">
              <h1>{fullName}</h1>
              <p>
                {[me.designation_name, me.department_name].filter(Boolean).join(" · ") ||
                  me.role_name ||
                  "Staff"}
              </p>
              {me.user_code && (
                <code className="account-code">{me.user_code}</code>
              )}
            </div>
          </header>

          <ViewSection title="Account">
            <DetailList columns={3}>
              <DetailItem label="Username" value={me.username} />
              <DetailItem label="Role" value={me.role_name} />
              <DetailItem label="Company Email" value={me.company_email} span={2} />
              <DetailItem label="Personal Email" value={me.personal_email} span={2} />
            </DetailList>
          </ViewSection>

          <ViewSection title="Work">
            <DetailList columns={3}>
              <DetailItem label="Department" value={me.department_name} />
              <DetailItem label="Designation" value={me.designation_name} />
              <DetailItem label="Shift" value={shift} />
              <DetailItem label="Date of Joining" value={formatDate(me.date_of_joining)} />
              <DetailItem label="Experience" value={me.experience} />
            </DetailList>
          </ViewSection>

          <ViewSection title="Contact">
            <DetailList columns={3}>
              <DetailItem label="Mobile" value={me.mobile} />
              <DetailItem label="Alternative Mobile" value={me.alternative_mobile} />
              <DetailItem label="Date of Birth" value={me.dob} />
              <DetailItem
                label="Address"
                span={3}
                value={
                  [me.address, me.city, me.state, me.postal_code, me.country]
                    .filter(Boolean)
                    .join(", ") || null
                }
              />
            </DetailList>
          </ViewSection>

          <ViewSection title="In an Emergency">
            <DetailList columns={3}>
              <DetailItem label="Contact Name" value={me.emergency_name} />
              <DetailItem label="Relationship" value={me.emergency_relationship} />
              <DetailItem label="Phone" value={me.emergency_contact} />
            </DetailList>
          </ViewSection>

          <p className="account-note">
            Your role, department and shift are maintained by HR. Ask them to
            change anything on this page — except your password, which is
            yours to change under <button type="button" className="account-link"
              onClick={() => navigate("/settings")}>Settings</button>.
          </p>
        </>
      )}
    </div>
  );
};

export default Profile;

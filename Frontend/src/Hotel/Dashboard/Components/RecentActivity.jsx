import React from "react";

const RecentActivity = ({ items = [], loading = false, error = null }) => {
  const hasData = Array.isArray(items) && items.length > 0;

  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>Recent Activity</h4>
        {!loading && !error && hasData && (
          <span className="card-meta">{items.length}</span>
        )}
      </div>

      {loading && (
        <div className="dashboard-empty" role="status" aria-live="polite">
          Loading activity…
        </div>
      )}

      {!loading && error && (
        <div className="dashboard-alert inline" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && !hasData && (
        <div className="dashboard-empty">
          No recent activity in the selected window.
        </div>
      )}

      {!loading && !error && hasData && (
        <ul className="activity-list" role="list">
          {items.map((activity) => (
            <li key={activity.key}>
              <div className="activity-body">
                <div className="activity-title-row">
                  <span className="activity-title">{activity.title}</span>
                  <span className={`activity-badge ${activity.kind}`}>
                    {activity.kind === "success" ? "Housekeeping" : "Reservation"}
                  </span>
                </div>
                <div className="activity-desc">{activity.desc}</div>
              </div>
              {activity.time && <span className="activity-time">{activity.time}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RecentActivity;

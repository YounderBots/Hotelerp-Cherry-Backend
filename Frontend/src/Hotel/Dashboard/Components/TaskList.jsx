import React, { useMemo } from "react";

import { formatDate, isoDay, todayIso } from "../../../functions/formatters";

/**
 * "My Tasks" — the signed-in staff member's own housekeeping tasks.
 *
 * This card was a stub: a "Coming soon" tag over an empty body, on a dashboard
 * whose other three cards are all live. The tasks exist and the API already
 * carries the assignee on every row (`GET /hotel/housekeeper_tasks`), so the
 * card is fed from there by the parent and keeps only the rows whose
 * `employee_id` matches the signed-in user — that field is the `/user/users`
 * id, which is the same id the login payload hands back as `user.id`.
 *
 * WHAT THE THREE STATES MUST NOT CONFLATE
 *   loading  the call has not settled yet — say so, do not draw an empty list.
 *   error    the gateway maps that GET to /task_assign and /user_reserved_details
 *            (rbac_map), so a role holding only the Dashboard is refused. The
 *            refusal is shown verbatim: an empty list here would read as "you
 *            have been given no work", which is a different — and false — claim.
 *   empty    the call succeeded and none of the rows are yours.
 */
const TaskList = ({ tasks = [], userId, loading = false, error = null }) => {
  const today = todayIso();

  // Soonest first, with work that is still to come ahead of work already done.
  const allMine = useMemo(() => {
    const identity = userId === undefined || userId === null ? "" : String(userId);
    if (!identity) return null; // no id to match against: not "zero tasks"

    const day = (t) => isoDay(t?.schedule_date);
    return tasks
      .filter((t) => String(t?.employee_id) === identity)
      .sort((a, b) => {
        const da = day(a);
        const db = day(b);
        const aUpcoming = da >= today;
        const bUpcoming = db >= today;
        if (aUpcoming !== bUpcoming) return aUpcoming ? -1 : 1;
        return aUpcoming ? da.localeCompare(db) : db.localeCompare(da);
      });
  }, [tasks, userId, today]);

  const known = allMine !== null;
  const total = known ? allMine.length : 0;
  // Only the handful that fit this card; the count in the header stays the
  // real total, so the cut is visible rather than silent.
  const shown = known ? allMine.slice(0, 6) : [];

  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>My Tasks</h4>
        {!loading && !error && known && total > 0 && (
          <span className="card-meta">{total} assigned</span>
        )}
      </div>

      {loading && (
        <div className="dashboard-empty" role="status" aria-live="polite">
          Loading your tasks…
        </div>
      )}

      {!loading && error && (
        <div className="dashboard-alert inline" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && !known && (
        <div className="dashboard-empty">
          Your session carries no user id, so tasks cannot be matched to you.
        </div>
      )}

      {!loading && !error && known && total === 0 && (
        <div className="dashboard-empty">
          No tasks assigned to you. Anything assigned to you on House Keeper →
          Task Assign appears here.
        </div>
      )}

      {!loading && !error && known && total > 0 && (
        <ul className="activity-list" role="list">
          {shown.map((task) => {
            const status = String(task?.task_status || "Pending");
            const kind = status.toLowerCase() === "completed" ? "success" : "primary";
            const time = task?.schedule_time ? String(task.schedule_time).slice(0, 5) : "";
            return (
              <li key={task.id}>
                <div className="activity-body">
                  <div className="activity-title-row">
                    <span className="activity-title">{task?.task_type || "Task"}</span>
                    <span className={`activity-badge ${kind}`}>{status}</span>
                  </div>
                  <div className="activity-desc">
                    Room {task?.room_no ?? "—"} · {formatDate(task?.schedule_date)}
                    {time ? ` · ${time}` : ""}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default TaskList;

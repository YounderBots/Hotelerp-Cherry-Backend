import React from "react";

const TaskList = () => {
  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>My Tasks</h4>
        <span className="sample-tag" title="Personal task list — no backend endpoint wired yet">
          Coming soon
        </span>
      </div>

      <div className="dashboard-empty">
        A personal task list will appear here once the tasks endpoint is available.
      </div>
    </div>
  );
};

export default TaskList;

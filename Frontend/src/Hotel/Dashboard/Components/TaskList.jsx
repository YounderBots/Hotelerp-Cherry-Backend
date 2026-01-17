import React from "react";

const TaskList = () => {
  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>Tasks</h4>
        <button className="btn-outline">+</button>
      </div>

      <ul className="task-list">
        <li className="done">
          <small>June 19, 2028</small>
          <span>Prepare Conference Room B (10 AM)</span>
        </li>

        <li className="progress">
          <small>June 19, 2028</small>
          <span>Restock 3rd Floor Supplies</span>
        </li>

        <li>
          <small>June 20, 2028</small>
          <span>Inspect and Clean Pool Area</span>
        </li>

        <li>
          <small>June 20, 2028</small>
          <span>Check-In Assistance (4–6 PM)</span>
        </li>
      </ul>
    </div>
  );
};

export default TaskList;

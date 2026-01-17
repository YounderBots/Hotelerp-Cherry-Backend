// AdminDashboard.jsx
import React from "react";
import "./AdminDashboard.css";

import KPISection from "./Components/KPISection";
import BookingPlatform from "./Components/BookingPlatform";
import RoomAvailability from "./Components/RoomAvailability";
import TaskList from "./Components/TaskList";
import BookingTable from "./Components/BookingTable";
import RecentActivity from "./Components/RecentActivity";

const AdminDashboard = () => {
  return (
    <div className="dashboard-wrapper container-fluid">
      {/* KPI SECTION - Full width */}
      <div className="row mb-4">
        <div className="col-12">
          <KPISection />
        </div>
      </div>

      {/* TOP ROW - 2/3 + 1/3 (Booking Platform + Room Availability, Tasks) */}
      <div className="dashboard-row">

        {/* LEFT SIDE - 2/3 */}
        {/* <div className="dashboard-col dashboard-col-8">
          <div className="dashboard-row"> */}
            <div className="dashboard-col dashboard-col-4">
              <BookingPlatform />
            </div>

            <div className="dashboard-col dashboard-col-4">
              <RoomAvailability />
            </div>
          {/* </div>
        </div> */}

        {/* RIGHT SIDE - 1/3 */}
        <div className="dashboard-col dashboard-col-4">
          <TaskList />
        </div>

      </div>



      {/* BOTTOM ROW - 2/3 + 1/3 (Booking List, Recent Activities) */}
      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-8">
          <div className="booking-list-wrap full-height">
            <BookingTable />
          </div>
        </div>

        <div className="dashboard-col dashboard-col-4">
          <div className="recent-activity-wrap full-height">
            <RecentActivity />
          </div>
        </div>
      </div>
    </div>

  );
};

export default AdminDashboard;
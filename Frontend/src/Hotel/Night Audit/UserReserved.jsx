import React, { useEffect, useState } from "react";
import Tabs, { Tab } from "../../stories/Tabs";
import TableTemplate from "../../stories/TableTemplate";
import { Download, Eye, X } from "lucide-react";
import "./NightAudit.css";
import APICall from "../../APICalls/APICalls";

const UserReserved = () => {
  const [reservations, setReservations] = useState([]);
  const [tasks, setTasks] = useState([]);

  const [viewReservation, setViewReservation] = useState(null);
  const [viewKeeper, setViewKeeper] = useState(null);

  /* =====================================================
     USER ACTIVITY LOG DATA (FIXED)
  ===================================================== */

  const getAllroomReservation = async () => {
    try {
      const response = await APICall.getT("/hotel/room_reservation");
      console.log("Full Response:", response);
      setReservations(response.data);
    } catch (error) {
      console.error("Error fetching reservations:", error);
    }
  };

  const getTaskAssign = async () => {
    const AllTaskAssign = await APICall.getT("/hotel/housekeeper_tasks");
    setTasks(AllTaskAssign.data);
  }


  // const userActivityColumns = [
  //   { key: "room_reservation_id", title: "Reservation ID" },

  //   {
  //     key: "first_name",
  //     title: "Name",
  //   },

  //   { key: "phone_number", title: "Phone Number" },
  //   { key: "arrival_date", title: "Arrival Date" },
  //   { key: "departure_date", title: "Departure Date" },

  //   {
  //     key: "reservation_status",
  //     title: "Status",
  //     align: "center",
  //   },

  //   {
  //     key: "action",
  //     title: "Action",
  //     type: "custom",
  //     render: (row) => (
  //       <button
  //         className="table-action-btn view"
  //         onClick={() => setViewReservation(row)}
  //       >
  //         <Eye size={16} />
  //       </button>
  //     ),
  //   },
  // ];

  /* =====================================================
     HOUSE KEEPER DATA (FIXED)
  ===================================================== */
  const houseKeeperData = [
    {
      id: 1,
      employeeId: "EMP-101",
      FirstName: "Ravi",
      LastName: "Kumar",
      scheduleDate: "2026-01-12",
      scheduleTime: "09:00 AM - 12:00 PM",
      roomNumber: "202",
      taskType: "Room Cleaning",
      assignedStaff: "Ravi Kumar",
      taskStatus: "Completed",
      roomStatus: "Cleaned",
      lostAndFound: "No",
      specialInstruction: "Deep cleaning required",
      status: "Active",
    },
    {
      id: 2,
      employeeId: "EMP-102",
      FirstName: "Priya",
      LastName: "Sharma",
      scheduleDate: "2026-01-12",
      scheduleTime: "01:00 PM - 04:00 PM",
      roomNumber: "203",
      taskType: "Bed Linen Change",
      assignedStaff: "Priya Sharma",
      taskStatus: "In Progress",
      roomStatus: "In Service",
      lostAndFound: "Wallet",
      specialInstruction: "Handle guest belongings carefully",
      status: "Active",
    },
    {
      id: 1,
      employeeId: "EMP-101",
      FirstName: "Smith",
      LastName: "Kumar",
      scheduleDate: "2026-01-12",
      scheduleTime: "09:00 AM - 12:00 PM",
      roomNumber: "202",
      taskType: "Room Cleaning",
      assignedStaff: "Ravi Kumar",
      taskStatus: "Completed",
      roomStatus: "Cleaned",
      lostAndFound: "No",
      specialInstruction: "Deep cleaning required",
      status: "Active",
    },
    {
      id: 1,
      employeeId: "EMP-101",
      FirstName: "Siva",
      LastName: "Kumar",
      scheduleDate: "2026-01-12",
      scheduleTime: "09:00 AM - 12:00 PM",
      roomNumber: "202",
      taskType: "Room Cleaning",
      assignedStaff: "Ravi Kumar",
      taskStatus: "Completed",
      roomStatus: "Cleaned",
      lostAndFound: "No",
      specialInstruction: "Deep cleaning required",
      status: "Active",
    },
    {
      id: 1,
      employeeId: "EMP-101",
      FirstName: "Raj",
      LastName: "S",
      scheduleDate: "2026-01-12",
      scheduleTime: "09:00 AM - 12:00 PM",
      roomNumber: "202",
      taskType: "Room Cleaning",
      assignedStaff: "Ravi Kumar",
      taskStatus: "Completed",
      roomStatus: "Cleaned",
      lostAndFound: "No",
      specialInstruction: "Deep cleaning required",
      status: "Active",
    },
  ];

  const houseKeeperColumns = [
    { key: "employee_id", title: "Employee ID" },
    { key: "first_name", title: "Name", type: "custom", render: (row) => [row.FirstName, row.LastName].filter(Boolean).join(" ") },
    {
      key: "room_no",
      title: "Room Number",
      align: "center",
    },
    { key: "task_type", title: "Task Type" },
    { key: "assign_staff", title: "Assigned Staff" },
    {
      key: "task_status",
      title: "Task Status",
      align: "center",
    },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => (
        <button
          className="table-action-btn view"
          onClick={() => setViewKeeper(row)}
        >
          <Eye size={16} />
        </button>
      ),
    },
  ];

  useEffect(() => {
    getAllroomReservation();
    getTaskAssign()
  }, [])

  return (
    <div className="userreserved-wrapper">
      <Tabs variant="default">
        <Tab label="User Activity Logs">
          <TableTemplate

            variant="striped"
            pagination
            pageSize={5}
            searchable
            exportable
            hasActionButton
            actionButton={{
              icon: <Download size={18} />,
              label: "Export Reservations",
              onClick: () => { },
              size: "small",
              variant: "outline",
            }}
            columns={[
              {
                key: "room_reservation_id",
                title: "Reservation ID",
                align: "center",
              },
              {
                key: "first_name",
                title: "First Name",
              },
              {
                key: "phone_number",
                title: "Phone",
              },
              {
                key: "arrival_date",
                title: "Arrival",
              },
              {
                key: "departure_date",
                title: "Departure",
              },
              {
                key: "reservation_status",
                title: "Status",
                align: "center",
              },
              {
                key: "action",
                title: "Action",
                type: "custom",
                render: (row) => (
                  <button
                    className="table-action-btn view"
                    onClick={() => setViewReservation(row)}
                  >
                    <Eye size={16} />
                  </button>
                ),
              },
            ]}

            data={reservations}
          />
        </Tab>

        <Tab label="House Keeper Details">
          <TableTemplate
            title="House Keeper Task"
            columns={houseKeeperColumns}
            data={tasks}
            hasActionButton
            pageSize={4}
            searchable
            pagination
          />
        </Tab>
      </Tabs>

      {/* ================= RESERVATION VIEW ================= */}
      {viewReservation && (
        <div className="modal-overlay">
          <div className="modal-card large">
            <div className="modal-header">
              <h3>Reservation Details</h3>
              <button onClick={() => setViewReservation(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid view">
              {Object.entries(viewReservation)
                .filter(([key]) => key !== "id") // remove unwanted keys
                .map(([key, value]) => (
                  <div className="form-group" key={key}>
                    <label>
                      {key
                        .replace(/_/g, " ") // replace underscores
                        .replace(/\b\w/g, (char) => char.toUpperCase())} {/* Capitalize */}
                    </label>
                    <input
                      value={value ?? "N/A"} // prevent undefined crash
                      disabled
                    />
                  </div>
                ))}
            </div>

            <div className="modal-footer">
              <button
                className="btn secondary"
                onClick={() => setViewReservation(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= HOUSE KEEPER VIEW ================= */}
      {viewKeeper && (
        <div className="modal-overlay">
          <div className="modal-card large">
            <div className="modal-header">
              <h3>House Keeper Task Details</h3>
              <button onClick={() => setViewKeeper(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid view">
              {Object.entries(viewKeeper).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn secondary"
                onClick={() => setViewKeeper(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserReserved;

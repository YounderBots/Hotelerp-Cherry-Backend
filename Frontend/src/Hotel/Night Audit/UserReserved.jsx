import React, { useState } from "react";
import Tabs, { Tab } from "../../stories/Tabs";
import TableTemplate from "../../stories/TableTemplate";
import { Download, Eye, X } from "lucide-react";
import "./NightAudit.css";

const UserReserved = () => {
  const [viewReservation, setViewReservation] = useState(null);
  const [viewKeeper, setViewKeeper] = useState(null);

  /* =====================================================
     USER ACTIVITY LOG DATA (FIXED)
  ===================================================== */
  const userActivityData = [
    {
        id: 1,
        reservationId: "RES-1001",
        FirstName: "Anand",
        LastName:"Kumar",
        phone: "9876543210",
        email: "anand.kumar@gmail.com",
        arrivalDate: "2026-01-12",
        departureDate: "2026-01-13",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 1,
        paymentMode: "Debit Card",
        extraBedCost: 0,
        totalAmount: 1000,
        taxAmount: 150,
        discountAmount: 0,
        overallAmount: 1150,
        paidAmount: 0,
        balanceAmount: 1150,
        bookingStatus: "Confirmed",
        reservationType: "Reservation",
        roomComplementary: "No",
        commonComplementary: "Breakfast",
      },
      {
        id: 2,
        reservationId: "RES-1002",
        FirstName: "Madhu1",
        LastName: "Priya",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 3,
        reservationId: "RES-1002",
        FirstName: "Esha",
        LastName: "Raj",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 4,
        reservationId: "RES-1002",
        FirstName: "Sam",
        LastName: "C",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 5,
        reservationId: "RES-1002",
        FirstName: "Raj",
        LastName: "Kumar",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 6,
        reservationId: "RES-1002",
        FirstName: "Rakesh",
        LastName: "Kumar",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 7,
        reservationId: "RES-1002",
        FirstName: "Smith",
        LastName: "J",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 8,
        reservationId: "RES-1002",
        FirstName: "Bob",
        LastName: "S",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
       {
        id: 9,
        reservationId: "RES-1002",
        FirstName: "Ram",
        LastName: "Kumar",
        phone: "9123456780",
        email: "madhu.priya@gmail.com",
        arrivalDate: "2026-01-15",
        departureDate: "2026-01-18",
        noOfRooms: 1,
        noOfAdults: 2,
        noOfChildren: 0,
        paymentMode: "UPI",
        extraBedCost: 0,
        totalAmount: 3000,
        taxAmount: 450,
        discountAmount: 200,
        overallAmount: 3250,
        paidAmount: 2000,
        balanceAmount: 1250,
        bookingStatus: "Checked In",
        reservationType: "Reservation",
        roomComplementary: "Yes",
        commonComplementary: "Breakfast, WiFi",
      },
    ];

  const userActivityColumns = [
    { key: "reservationId", title: "Reservation ID" },
    { key: "fullname", title: "Name",type:"custom",render:(row)=>row.name||[row.FirstName,row.LastName].filter(Boolean).join(" ")},
    { key: "phone", title: "Phone Number" },
    { key: "arrivalDate", title: "Arrival Date" },
    { key: "departureDate", title: "Departure Date" },
    {
      key: "bookingStatus",
      title: "Status",
      align: "center",
    },
    {
      key: "action",
      title: "Action",
      align: "left",
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
  ];

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
    { key: "employeeId", title: "Employee ID" },
    { key: "name", title: "Name", type: "custom", render: (row) => [row.FirstName, row.LastName].filter(Boolean).join(" ") },
    {
      key: "roomNumber",
      title: "Room Number",
      align: "center",
    },
    { key: "taskType", title: "Task Type" },
    { key: "assignedStaff", title: "Assigned Staff" },
    {
      key: "taskStatus",
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

  return (
    <div className="userreserved-wrapper">
      <Tabs variant="default">
        <Tab label="User Activity Logs">
          <TableTemplate
            actionButton={{
              icon: <Download size={18} />,
              label: 'Export Team',
              onClick: () => {},
              size: 'small',
              variant: 'outline'
            }}
            columns=
          {userActivityColumns}
            data=
          {userActivityData}
            hasActionButton
            pageSize={4}
            pagination
            searchable
            title="User Activity Log"
            // variant="striped"
/>
        </Tab>

        <Tab label="House Keeper Details">
          <TableTemplate
            title="House Keeper Task"
            columns={houseKeeperColumns}
            data={houseKeeperData}
            has ActionButton
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
              {Object.entries(viewReservation).map(
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

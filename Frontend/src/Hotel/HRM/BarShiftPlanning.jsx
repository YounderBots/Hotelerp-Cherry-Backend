import React from "react";
import StaffShiftPlanning from "./staff/StaffShiftPlanning";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";

// Bar staff shift scheduling and clock in/out. Lives under HRM (not Bar) because staffing is an HR
// concern; the bar module only contributes the day-to-day shift data.
//
// The endpoint literals below are what the gateway RBAC generator reads to
// decide this page may call them — keep them literal, not composed.
const api = {
  readList,
  listShifts: () => APICall.getT("/bar/staff_assignment"),
  listEmployees: () => APICall.getT("/user/users"),
  listFloors: () => APICall.getT("/bar/floor"),
  createShift: (body) => APICall.postT("/bar/staff_assignment", body),
  updateShift: (id, body) => APICall.putT(`/bar/staff_assignment/${id}`, body),
  cancelShift: (id) => APICall.deleteT(`/bar/staff_assignment/${id}`),
  clockIn: (id, body) => APICall.postT(`/bar/staff_assignment/${id}/clock_in`, body),
  clockOut: (id, body) => APICall.postT(`/bar/staff_assignment/${id}/clock_out`, body),
};

// Mirrors the SAEnum on BarStaffAssignment.role in Backend/Services/BarServices/models/models.py.
// Adding a value here without the matching migration writes a value the column
// rejects.
const ROLE_OPTIONS = ["Bartender", "Cashier", "Manager"];

const BarShiftPlanning = () => (
  <StaffShiftPlanning
    venueLabel="Bar"
    roleOptions={ROLE_OPTIONS}
    hasSection={false}
    api={api}
  />
);

export default BarShiftPlanning;

import React from "react";
import StaffShiftPlanning from "./staff/StaffShiftPlanning";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";

// Restaurant staff shift scheduling and clock in/out. Lives under HRM (not Restaurant) because staffing is an HR
// concern; the restaurant module only contributes the day-to-day shift data.
//
// The endpoint literals below are what the gateway RBAC generator reads to
// decide this page may call them — keep them literal, not composed.
const api = {
  readList,
  listShifts: () => APICall.getT("/restaurant/staff_assignment"),
  listEmployees: () => APICall.getT("/user/users"),
  listFloors: () => APICall.getT("/restaurant/floor"),
  createShift: (body) => APICall.postT("/restaurant/staff_assignment", body),
  updateShift: (id, body) => APICall.putT(`/restaurant/staff_assignment/${id}`, body),
  cancelShift: (id) => APICall.deleteT(`/restaurant/staff_assignment/${id}`),
  clockIn: (id, body) => APICall.postT(`/restaurant/staff_assignment/${id}/clock_in`, body),
  clockOut: (id, body) => APICall.postT(`/restaurant/staff_assignment/${id}/clock_out`, body),
};

// Mirrors the SAEnum on RestaurantStaffAssignment.role in Backend/Services/RestaurantServices/models/models.py.
// Adding a value here without the matching migration writes a value the column
// rejects.
const ROLE_OPTIONS = ["Waiter", "Chef", "Cashier", "Manager"];

const RestaurantShiftPlanning = () => (
  <StaffShiftPlanning
    venueLabel="Restaurant"
    roleOptions={ROLE_OPTIONS}
    hasSection={true}
    api={api}
  />
);

export default RestaurantShiftPlanning;

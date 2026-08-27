import React from "react";
import StaffRoster from "./staff/StaffRoster";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";

// Restaurant staff roster for today. Lives under HRM (not Restaurant) because staffing is an HR
// concern; the restaurant module only contributes the day-to-day shift data.
//
// The endpoint literals below are what the gateway RBAC generator reads to
// decide this page may call them — keep them literal, not composed.
// Only the calls this screen makes. Extra entries would be read by the RBAC
// generator as permissions this page needs.
const api = {
  readList,
  listShifts: () => APICall.getT("/restaurant/staff_assignment", { shift_date: new Date().toISOString().slice(0, 10) }),
  listEmployees: () => APICall.getT("/user/users"),
  listFloors: () => APICall.getT("/restaurant/floor"),
  createShift: (body) => APICall.postT("/restaurant/staff_assignment", body),
};

// Mirrors the SAEnum on RestaurantStaffAssignment.role in Backend/Services/RestaurantServices/models/models.py.
// Adding a value here without the matching migration writes a value the column
// rejects.
const ROLE_OPTIONS = ["Waiter", "Chef", "Cashier", "Manager"];

const RestaurantRoster = () => (
  <StaffRoster
    venueLabel="Restaurant"
    roleOptions={ROLE_OPTIONS}
    hasSection={true}
    api={api}
  />
);

export default RestaurantRoster;

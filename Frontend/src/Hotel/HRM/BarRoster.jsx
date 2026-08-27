import React from "react";
import StaffRoster from "./staff/StaffRoster";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";

// Bar staff roster for today. Lives under HRM (not Bar) because staffing is an HR
// concern; the bar module only contributes the day-to-day shift data.
//
// The endpoint literals below are what the gateway RBAC generator reads to
// decide this page may call them — keep them literal, not composed.
// Only the calls this screen makes. Extra entries would be read by the RBAC
// generator as permissions this page needs.
const api = {
  readList,
  listShifts: () => APICall.getT("/bar/staff_assignment", { shift_date: new Date().toISOString().slice(0, 10) }),
  listEmployees: () => APICall.getT("/user/users"),
  listFloors: () => APICall.getT("/bar/floor"),
  createShift: (body) => APICall.postT("/bar/staff_assignment", body),
};

// Mirrors the SAEnum on BarStaffAssignment.role in Backend/Services/BarServices/models/models.py.
// Adding a value here without the matching migration writes a value the column
// rejects.
const ROLE_OPTIONS = ["Bartender", "Cashier", "Manager"];

const BarRoster = () => (
  <StaffRoster
    venueLabel="Bar"
    roleOptions={ROLE_OPTIONS}
    hasSection={false}
    api={api}
  />
);

export default BarRoster;

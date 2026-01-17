import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Users, X } from "lucide-react";

const StaffPlanning = () => {
  const [showShiftModal, setShowShiftModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedShift, setSelectedShift] = useState(null);

  const shiftData = [
    {
      id: 1,
      date: "2025-01-12",
      name: "Evening",
      department: "Service",
      startTime: "16:00",
      endTime: "23:00",
      staffCount: 6,
      status: "Planned",
    },
    {
      id: 2,
      date: "2025-01-11",
      name: "Morning",
      department: "Kitchen",
      startTime: "07:00",
      endTime: "15:00",
      staffCount: 4,
      status: "Active",
    },
  ];

  const openShiftModal = (row = null) => {
    setSelectedShift(row);
    setShowShiftModal(true);
  };

  const openAssignModal = (row) => {
    setSelectedShift(row);
    setShowAssignModal(true);
  };

  const openViewModal = (row) => {
    setSelectedShift(row);
    setShowViewModal(true);
  };

  const closeAllModals = () => {
    setSelectedShift(null);
    setShowShiftModal(false);
    setShowAssignModal(false);
    setShowViewModal(false);
  };

  return (
    <>
      {/* ================= SHIFT PLANNING TABLE ================= */}
      <TableTemplate
        title="Shift Planning"
        searchable
        pagination
        actionButton={{
          label: "Add Shift",
          variant: "primary",
          onClick: () => openShiftModal(),
        }}
        columns={[
          { key: "date", title: "Shift Date" },
          { key: "name", title: "Shift Name" },
          { key: "department", title: "Department" },
          { key: "startTime", title: "Start Time" },
          { key: "endTime", title: "End Time" },
          {
            key: "staffCount",
            title: "Assigned Staff",
            align: "center",
          },
          {
            key: "status",
            title: "Shift Status",
            type: "badge",
            align: "center",
          },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div
                style={{
                  display: "flex",
                  gap: "8px",
                  justifyContent: "center",
                }}
              >
                <button
                  className="table-action-btn view"
                  onClick={() => openViewModal(row)}
                >
                  <Eye size={16} />
                </button>

                <button
                  className="table-action-btn edit"
                  onClick={() => openShiftModal(row)}
                >
                  <Pencil size={16} />
                </button>

                <button
                  className="table-action-btn"
                  onClick={() => openAssignModal(row)}
                >
                  <Users size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={shiftData}
      />

      {/* ================= ADD / EDIT SHIFT MODAL ================= */}
      {showShiftModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>{selectedShift ? "Edit Shift" : "Add Shift"}</h3>
              <button onClick={closeAllModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="grid-4">
                <div className="form-group">
                  <label>Shift Name</label>
                  <select defaultValue={selectedShift?.name || ""}>
                    <option>Morning</option>
                    <option>Evening</option>
                    <option>Night</option>
                    <option>Custom</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Shift Date</label>
                  <input type="date" defaultValue={selectedShift?.date || ""} />
                </div>

                <div className="form-group">
                  <label>Start Time</label>
                  <input
                    type="time"
                    defaultValue={selectedShift?.startTime || ""}
                  />
                </div>

                <div className="form-group">
                  <label>End Time</label>
                  <input
                    type="time"
                    defaultValue={selectedShift?.endTime || ""}
                  />
                </div>

                <div className="form-group">
                  <label>Department</label>
                  <select defaultValue={selectedShift?.department || ""}>
                    <option>Service</option>
                    <option>Kitchen</option>
                    <option>Bar</option>
                    <option>Billing</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Allowed Roles</label>
                  <select multiple>
                    <option>Waiter</option>
                    <option>Chef</option>
                    <option>Bartender</option>
                    <option>Cashier</option>
                    <option>Manager</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Min Staff</label>
                  <input type="number" />
                </div>

                <div className="form-group">
                  <label>Max Staff</label>
                  <input type="number" />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeAllModals}>
                Cancel
              </button>
              <button className="btn primary">Save Shift</button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ASSIGN STAFF MODAL ================= */}
      {showAssignModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "800px", width: "95%" }}>
            <div className="modal-header">
              <h3>Assign Staff</h3>
              <button onClick={closeAllModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Staff ID</th>
                    <th>Staff Name</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th style={{ textAlign: "center" }}>Assign</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>STF102</td>
                    <td>Ramesh Kumar</td>
                    <td>Waiter</td>
                    <td>
                      <span className="badge success">Available</span>
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <input type="checkbox" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeAllModals}>
                Cancel
              </button>
              <button className="btn primary">Assign Staff</button>
            </div>
          </div>
        </div>
      )}

      {/* ================= VIEW SHIFT MODAL ================= */}
      {showViewModal && selectedShift && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "500px", width: "95%" }}>
            <div className="modal-header">
              <h3>Shift Details</h3>
              <button onClick={closeAllModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <p><strong>Shift:</strong> {selectedShift.name}</p>
              <p><strong>Date:</strong> {selectedShift.date}</p>
              <p><strong>Department:</strong> {selectedShift.department}</p>
              <p>
                <strong>Time:</strong>{" "}
                {selectedShift.startTime} – {selectedShift.endTime}
              </p>
              <p><strong>Status:</strong> {selectedShift.status}</p>
              <p><strong>Assigned Staff:</strong> {selectedShift.staffCount}</p>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeAllModals}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default StaffPlanning;

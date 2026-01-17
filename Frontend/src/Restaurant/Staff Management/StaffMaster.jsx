import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, X } from "lucide-react";

const StaffMaster = () => {
  const [showStaffModal, setShowStaffModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState(null);

  const staffData = [
    {
      id: 1,
      staffId: "STF102",
      name: "Ramesh Kumar",
      department: "Service",
      role: "Waiter",
      shift: "Evening",
      phone: "9876543210",
      status: "Active",
    },
    {
      id: 2,
      staffId: "STF118",
      name: "Anitha S",
      department: "Billing",
      role: "Cashier",
      shift: "Morning",
      phone: "9123456780",
      status: "Inactive",
    },
  ];

  const openAddEditModal = (row = null) => {
    setSelectedStaff(row);
    setShowStaffModal(true);
  };

  const closeAddEditModal = () => {
    setSelectedStaff(null);
    setShowStaffModal(false);
  };

  const openViewModal = (row) => {
    setSelectedStaff(row);
    setShowViewModal(true);
  };

  const closeViewModal = () => {
    setSelectedStaff(null);
    setShowViewModal(false);
  };

  return (
    <>

      {/* ================= STAFF TABLE ================= */}
      <TableTemplate
        title="Staff List"
        searchable
        pagination
        actionButton={{
          label: "Add Staff",
          variant: "primary",
          onClick: () => openAddEditModal(),
        }}
        columns={[
          { key: "staffId", title: "Staff ID" },
          { key: "name", title: "Staff Name" },
          { key: "department", title: "Department" },
          { key: "role", title: "Role" },
          { key: "shift", title: "Shift" },
          { key: "phone", title: "Contact No" },
          {
            key: "status",
            title: "Status",
            type: "badge",
            align: "center",
          },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button
                  className="table-action-btn view"
                  onClick={() => openViewModal(row)}
                >
                  <Eye size={16} />
                </button>
                <button
                  className="table-action-btn edit"
                  onClick={() => openAddEditModal(row)}
                >
                  <Pencil size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={staffData}
      />

      {/* ================= ADD / EDIT STAFF MODAL ================= */}
      {showStaffModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>{selectedStaff ? "Edit Staff" : "Add Staff"}</h3>
              <button onClick={closeAddEditModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="grid-3">
                <div className="form-group">
                  <label>Staff ID</label>
                  <input type="text" defaultValue={selectedStaff?.staffId || ""} />
                </div>

                <div className="form-group">
                  <label>Staff Name</label>
                  <input type="text" defaultValue={selectedStaff?.name || ""} />
                </div>

                <div className="form-group">
                  <label>Mobile Number</label>
                  <input type="text" defaultValue={selectedStaff?.phone || ""} />
                </div>

                <div className="form-group">
                  <label>Department</label>
                  <select defaultValue={selectedStaff?.department || ""}>
                    <option>Service</option>
                    <option>Kitchen</option>
                    <option>Billing</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Role</label>
                  <select defaultValue={selectedStaff?.role || ""}>
                    <option>Waiter</option>
                    <option>Chef</option>
                    <option>Cashier</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Shift</label>
                  <select defaultValue={selectedStaff?.shift || ""}>
                    <option>Morning</option>
                    <option>Evening</option>
                    <option>Night</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeAddEditModal}>
                Cancel
              </button>
              <button className="btn primary">Save Staff</button>
            </div>
          </div>
        </div>
      )}

      {/* ================= VIEW STAFF MODAL ================= */}
      {showViewModal && selectedStaff && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "500px", width: "95%" }}>
            <div className="modal-header">
              <h3>Staff Details</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <p><strong>Name:</strong> {selectedStaff.name}</p>
              <p><strong>Department:</strong> {selectedStaff.department}</p>
              <p><strong>Role:</strong> {selectedStaff.role}</p>
              <p><strong>Shift:</strong> {selectedStaff.shift}</p>
              <p><strong>Status:</strong> {selectedStaff.status}</p>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default StaffMaster;

import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, X } from "lucide-react";
import "../../MasterData/MasterData.css";

const GuestManagement = () => {
  const [showGuestModal, setShowGuestModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedGuest, setSelectedGuest] = useState(null);

  const guestData = [
    {
      id: 1,
      guestId: "GST302",
      name: "Anita Sharma",
      mobile: "9123456789",
      guestType: "Walk-in",
      lastVisit: "2025-01-10",
      visits: 6,
      loyalty: "Member",
      status: "Active",
      preference: "Veg",
      allergies: "None",
    },
    {
      id: 2,
      guestId: "GST315",
      name: "Rahul Verma",
      mobile: "9988776655",
      guestType: "Hotel Guest",
      lastVisit: "2025-01-08",
      visits: 3,
      loyalty: "Non-Member",
      status: "Inactive",
      preference: "-",
      allergies: "-",
    },
  ];

  const openGuestModal = (row = null) => {
    setSelectedGuest(row);
    setShowGuestModal(true);
  };

  const openViewModal = (row) => {
    setSelectedGuest(row);
    setShowViewModal(true);
  };

  const closeAllModals = () => {
    setSelectedGuest(null);
    setShowGuestModal(false);
    setShowViewModal(false);
  };

  return (
    <>
      

      {/* ================= GUEST TABLE ================= */}
      <TableTemplate
        title="Guests"
        searchable
        pagination
        actionButton={{
          label: "Add Guest",
          variant: "primary",
          onClick: () => openGuestModal(),
        }}
        columns={[
          { key: "guestId", title: "Guest ID" },
          { key: "name", title: "Guest Name" },
          { key: "mobile", title: "Mobile No" },
          { key: "guestType", title: "Guest Type" },
          { key: "lastVisit", title: "Last Visit" },
          { key: "visits", title: "Total Visits", align: "center" },
          {
            key: "loyalty",
            title: "Loyalty",
            type: "badge",
            align: "center",
          },
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
                  onClick={() => openGuestModal(row)}
                >
                  <Pencil size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={guestData}
      />

      {/* ================= ADD / EDIT GUEST MODAL ================= */}
      {showGuestModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>{selectedGuest ? "Edit Guest" : "Add Guest"}</h3>
              <button onClick={closeAllModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="grid-3">
                <div className="form-group">
                  <label>Guest Name</label>
                  <input defaultValue={selectedGuest?.name || ""} />
                </div>

                <div className="form-group">
                  <label>Mobile Number</label>
                  <input defaultValue={selectedGuest?.mobile || ""} />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input type="email" />
                </div>

                <div className="form-group">
                  <label>Guest Type</label>
                  <select defaultValue={selectedGuest?.guestType || ""}>
                    <option>Walk-in</option>
                    <option>Hotel Guest</option>
                    <option>Delivery</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Food Preference</label>
                  <select defaultValue={selectedGuest?.preference || ""}>
                    <option>Veg</option>
                    <option>Non-Veg</option>
                    <option>Vegan</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Allergies</label>
                  <input defaultValue={selectedGuest?.allergies || ""} />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeAllModals}>
                Cancel
              </button>
              <button className="btn primary">Save Guest</button>
            </div>
          </div>
        </div>
      )}

      {/* ================= VIEW GUEST PROFILE MODAL ================= */}
      {showViewModal && selectedGuest && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "500px", width: "95%" }}>
            <div className="modal-header">
              <h3>Guest Profile</h3>
              <button onClick={closeAllModals}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <p><strong>Name:</strong> {selectedGuest.name}</p>
              <p><strong>Mobile:</strong> {selectedGuest.mobile}</p>
              <p><strong>Guest Type:</strong> {selectedGuest.guestType}</p>
              <p><strong>Total Visits:</strong> {selectedGuest.visits}</p>
              <p><strong>Loyalty:</strong> {selectedGuest.loyalty}</p>
              <p><strong>Preference:</strong> {selectedGuest.preference}</p>
              <p><strong>Allergies:</strong> {selectedGuest.allergies}</p>
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

export default GuestManagement;

import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const Booking = () => {
  const [data, setData] = useState([
    {
      id: 1,
      roomNo: "202",
      firstName: "John",
      lastName: "Doe",
      email: "john@example.com",
      phone: "9876543210",
      roomType: "Deluxe",
      arrivalDate: "2026-01-10",
      departureDate: "2026-01-12",
      noOfRooms: 1,
      noOfAdults: 2,
      noOfChilds: 0,
      noOfNights: 2,
    },
    {
      id: 2,
      roomNo: "203",
      firstName: "Sarah",
      lastName: "Wilson",
      email: "sarah@example.com",
      phone: "9123456780",
      roomType: "Suite",
      arrivalDate: "2026-01-15",
      departureDate: "2026-01-18",
      noOfRooms: 1,
      noOfAdults: 2,
      noOfChilds: 1,
      noOfNights: 3,
    },
  ]);

  const initialForm = {
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    roomType: "",
    arrivalDate: "",
    departureDate: "",
    noOfRooms: 1,
    noOfAdults: 1,
    noOfChilds: 0,
    noOfNights: 1,
  };

  const [formData, setFormData] = useState(initialForm);
  const [showModal, setShowModal] = useState(false);
  const [mode, setMode] = useState("add"); // add | edit | view
  const [selectedId, setSelectedId] = useState(null);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData(initialForm);
    setMode("add");
    setSelectedId(null);
    setShowModal(true);
  };

  const openEditModal = (row) => {
    setFormData(row);
    setSelectedId(row.id);
    setMode("edit");
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setFormData(row);
    setMode("view");
    setShowModal(true);
  };

  const handleDelete = (row) => {
    if (window.confirm("Are you sure you want to delete this booking?")) {
      setData((prev) => prev.filter((i) => i.id !== row.id));
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedId(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.firstName || !formData.lastName) return;

    if (mode === "edit") {
      setData((prev) =>
        prev.map((i) => (i.id === selectedId ? { ...formData } : i))
      );
    } else {
      setData((prev) => [
        ...prev,
        { ...formData, id: Date.now(), roomNo: "Auto" },
      ]);
    }
    closeModal();
  };

  const isView = mode === "view";

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Booking List"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Booking",
          onClick: openAddModal,
          variant: "primary",
        }}
        columns={[
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "firstName", title: "First Name", align: "center" },
          { key: "lastName", title: "Last Name", align: "center" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div className="table-actions">
                <button
                  className="table-action-btn view"
                  title="View"
                  onClick={() => openViewModal(row)}
                >
                  <Eye size={16} />
                </button>
                <button
                  className="table-action-btn edit"
                  title="Edit"
                  onClick={() => openEditModal(row)}
                >
                  <Pencil size={16} />
                </button>
                <button
                  className="table-action-btn delete"
                  title="Delete"
                  onClick={() => handleDelete(row)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            {/* ===== HEADER ===== */}
            <div className="modal-header">
              <h3>
                {mode === "add"
                  ? "Add Booking"
                  : mode === "edit"
                  ? "Edit Booking"
                  : "View Booking"}
              </h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            {/* ===== BODY (ALL FIELDS ALWAYS VISIBLE) ===== */}
            <div className="modal-body grid">
              {[
                ["First Name", "firstName"],
                ["Last Name", "lastName"],
                ["Email", "email"],
                ["Phone", "phone"],
                ["Room Type", "roomType"],
                ["Arrival Date", "arrivalDate", "date"],
                ["Departure Date", "departureDate", "date"],
                ["No of Rooms", "noOfRooms"],
                ["No of Adults", "noOfAdults"],
                ["No of Children", "noOfChilds"],
                ["No of Nights", "noOfNights"],
              ].map(([label, name, type]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input
                    type={type || "text"}
                    name={name}
                    value={formData[name]}
                    onChange={handleChange}
                    disabled={isView}
                  />
                </div>
              ))}
            </div>

            {/* ===== FOOTER ===== */}
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                {isView ? "Close" : "Cancel"}
              </button>
              {!isView && (
                <button className="btn primary" onClick={handleSave}>
                  Save
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Booking;

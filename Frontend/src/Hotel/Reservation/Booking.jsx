import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import { useEffect } from "react";

const Booking = () => {
  const [data, setData] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);

  const initialForm = {
    salutation: "",
    first_name: "",
    last_name: "",
    phone_number: "",
    email: "",
    arrival_date: "",
    departure_date: "",
    no_of_nights: "",
    room_type: [],
    no_of_rooms: "",
    no_of_adults: "",
    no_of_children: 0,
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
    setFormData({
      ...row,
      room_type: (row.room_type || []).map(Number),
    });
    setSelectedId(row.id);
    setMode("edit");
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setFormData({
      ...row,
      room_type: (row.room_type || []).map(Number),
    });
    setMode("view");
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedId(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };
  
  const getAllBookings = async ()=> {
    try {
      const response = await APICall.getT("/hotel/room_booking");
      setData(response.data);
    }
    catch (err) {
      console.log("Rooms API Error:", err);
    }
  }
  const getAllroom_types = async () => {
    try {
      const response = await APICall.getT("/masterdata/room_types");

      console.log("Room Types Full Response:", response);

      setRoomTypes(response?.data|| []);
    } catch (err) {
      console.log("Room Types API Error:", err);
    }
  };


  useEffect(() => {
    getAllBookings();
    getAllroom_types();
  }, []);

  const createBooking = async () => {
    try {
      const response = await APICall.postT("/hotel/room_booking", formData);
      getAllBookings();
      closeModal();
    }
    catch (err) {
      console.log("Rooms API Error:", err);
    }
  }
  const updateBooking = async () => {
    try {
      const payload = {
        ...formData,
        id: selectedId,
      };

      const response = await APICall.putT(
        "/hotel/room_booking",
        payload
      );

      console.log("Update Success:", response);

      getAllBookings();
      closeModal();
    } catch (err) {
      console.log("Update Booking API Error:", err);
    }
  };

  const deleteBooking = async () => {
    try {
      const response = await APICall.deleteT(`/hotel/room_booking/${selectedId}`);
      getAllBookings();
      closeModal();
    }
    catch (err) {
      console.log("Rooms API Error:", err);
    }
  }


  const handleSave = async () => {
    if (!formData.first_name || !formData.last_name) return;

    if (mode === "edit") {
      await updateBooking();
    } else {
      await createBooking();
    }
  };

  const handleDelete = (row) => {
    if (window.confirm("Are you sure you want to delete this booking?")) {
      setSelectedId(row.id);
      deleteBooking();
    }
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
          { key: "first_name", title: "First Name", align: "center" },
          { key: "last_name", title: "Last Name", align: "center" },
          { key: "no_of_rooms", title: "No. of Rooms", align: "center" },
          { key: "arrival_date", title: "Arrival Date", align: "center" },
          { key: "departure_date", title: "Departure Date", align: "center" },
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
              <div className="form-group">
                <label>Salutation</label>
                <select
                  name="salutation"
                  value={formData.salutation}
                  onChange={handleChange}
                  disabled={isView}
                >
                  <option value="Mr">Mr</option>
                  <option value="Mrs">Mrs</option>
                </select>
              </div>

              {[
                ["First Name", "first_name"],
                ["Last Name", "last_name"],
                ["Email", "email"],
                ["phone_number", "phone_number"],
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
              <div className="form-group">
                <label>Room Type</label>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "6px",
                    padding: "8px",
                    border: "1px solid #ccc",
                    borderRadius: "8px",
                    minHeight: "45px",
                    background: isView ? "#f5f5f5" : "white",
                  }}
                >
                  {formData.room_type.length > 0 ? (
                    formData.room_type.map((id) => {
                      const room = roomTypes.find((r) => r.id === id);

                      return (
                        <span
                          key={id}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            padding: "4px 10px",
                            borderRadius: "20px",
                            background: "#e0f2fe",
                            fontSize: "13px",
                          }}
                        >
                          {room?.room_type_name}
                          {!isView && (
                            <button
                              type="button"
                              onClick={() => {
                                setFormData((prev) => ({
                                  ...prev,
                                  room_type: prev.room_type.filter((x) => x !== id),
                                }));
                              }}
                              style={{
                                marginLeft: "6px",
                                border: "none",
                                background: "transparent",
                                cursor: "pointer",
                                fontWeight: "bold",
                              }}
                            >
                              ×
                            </button>
                          )}
                        </span>
                      );
                    })
                  ) : (
                    <span style={{ fontSize: "13px", color: "#888" }}>
                      Select Room Types...
                    </span>
                  )}
                </div>
                {!isView && (
                  <select
                    style={{
                      marginTop: "8px",
                      width: "100%",
                      padding: "10px",
                      borderRadius: "8px",
                    }}
                    onChange={(e) => {
                      const selectedId = Number(e.target.value);

                      if (!selectedId) return;
                      if (formData.room_type.includes(selectedId)) return;

                      setFormData((prev) => ({
                        ...prev,
                        room_type: [...prev.room_type, selectedId],
                      }));
                      e.target.value = "";
                    }}
                  >
                    <option value="">+ Add Room Type</option>

                    {roomTypes.map((room) => (
                      <option key={room.id} value={room.id}>
                        {room.room_type_name}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {[
                ["Arrival Date", "arrival_date", "date"],
                ["Departure Date", "departure_date", "date"],
                ["No of Rooms", "no_of_rooms"],
                ["No of Adults", "no_of_adults"],
                ["No of Children", "no_of_children"],
                ["No of Nights", "no_of_nights"],
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

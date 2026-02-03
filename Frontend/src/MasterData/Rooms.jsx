import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";
import { useEffect } from "react";

const Rooms = () => {
  const [data, setData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [roomTypes, setRoomTypes] = useState([]);
  const [bedTypes, setBedTypes] = useState([]);

  const initialForm = {
    room_no: "",
    room_name: "",
    room_type_id: null,
    bed_type_id: null,
    room_telephone: "",
    max_adult: "",
    max_child: "",
    booking_status: "No",
    working_status: "Working",
    room_status: "Available",
    images: [null, null, null, null],
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);

    setFormData({
      ...initialForm,
      images: [null, null, null, null],
    });

    setShowModal(true);
  };


  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };
  const handleEdit = (row) => {
    setEditId(row.id);

    setFormData({
      ...row,
      images: [
        row.images?.image_1 || null,
        row.images?.image_2 || null,
        row.images?.image_3 || null,
        row.images?.image_4 || null,
      ],
    });

    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditId(null);
  };

  const closeViewModal = () => {
    setShowViewModal(false);
    setViewData(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === "room_type_id" || name === "bed_type_id") {
      setFormData((prev) => ({
        ...prev,
        [name]: parseInt(value),
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };


  const getAllRooms = async () => {
    const response = await APICall.getT("/masterdata/room");

    console.log("Rooms Response:", response.data);

    const formatted = response.data.map((room) => ({
      ...room,
      images: room.images,
    }));

    setData(formatted);
  };


 const getAllroom_type_ids = async () => {
    const res = await APICall.getT("/masterdata/room_types");

    console.log("Room Types Response:", res.data);

    setRoomTypes(res.data || []);
  };

  const getAllbed_type_ids = async () => {
    const res = await APICall.getT("/masterdata/bed_types");

    console.log("Bed Types Response:", res.data);

    setBedTypes(res.data || []);
  };


  useEffect(() => {
    getAllRooms();
    getAllroom_type_ids();
    getAllbed_type_ids();
  }
, []);
  const addRoom = async () => {
      try {
        const form = new FormData();

        form.append("room_no", formData.room_no);
        form.append("room_name", formData.room_name);
        form.append("room_type_id", formData.room_type_id);
        form.append("bed_type_id", formData.bed_type_id);
        form.append("room_telephone", formData.room_telephone);
        form.append("max_adult", formData.max_adult);
        form.append("max_child", formData.max_child);
        form.append("booking_status", formData.booking_status);
        form.append("working_status", formData.working_status);
        form.append("room_status", formData.room_status);
        if (!formData.images[0]) {
          alert("Please upload Image 1");
          return;
        }

        form.append("image_1", formData.images[0]);

        if (formData.images[1]) form.append("image_2", formData.images[1]);
        if (formData.images[2]) form.append("image_3", formData.images[2]);
        if (formData.images[3]) form.append("image_4", formData.images[3]);

        await APICall.postT("/masterdata/room", form);

        getAllRooms();
      } catch (error) {
        console.log(error);
      }
    };

  const updateRoom = async (id, updatedData) => {
    try {
      const form = new FormData();
      form.append("room_id", id);

      form.append("room_no", updatedData.room_no);
      form.append("room_name", updatedData.room_name);

      form.append("room_type_id", updatedData.room_type_id);
      form.append("bed_type_id", updatedData.bed_type_id);

      form.append("room_telephone", updatedData.room_telephone);

      form.append("max_adult", updatedData.max_adult);
      form.append("max_child", updatedData.max_child);

      form.append("room_condition", updatedData.room_status);

      form.append("booking_status", updatedData.booking_status);
      form.append("working_status", updatedData.working_status);

      form.append("room_status", updatedData.room_status);

      if (updatedData.images[0] instanceof File)
        form.append("image_1", updatedData.images[0]);

      if (updatedData.images[1] instanceof File)
        form.append("image_2", updatedData.images[1]);

      if (updatedData.images[2] instanceof File)
        form.append("image_3", updatedData.images[2]);

      if (updatedData.images[3] instanceof File)
        form.append("image_4", updatedData.images[3]);
      await APICall.putT(`/masterdata/room`, form);

      getAllRooms();
    } catch (error) {
      console.log("Update Error:", error);
    }
  };

  
  const deleteRoom = async (id) => {
    try {
            await APICall.deleteT(`/masterdata/room/${id}`);
            getAllRooms();
        }
      catch (error) {
            return error, " to delete a Room";
        }
  };

  const handleImageChange = (index, file) => {
    if (!file) return;
    const preview = URL.createObjectURL(file);
    setFormData((prev) => {
      const images = [...prev.images];
      images[index] = file;
      return { ...prev, images };
    });
  };

  const handleSave = () => {
    if (!formData.room_no || !formData.room_name) {
      alert("Room No and Room Name are required");
      return;
    }

    if (!formData.room_telephone) {
      alert("Room Telephone is required");
      return;
    }

    if (!formData.images[0]) {
      alert("Please upload Image 1");
      return;
    }
    if (!formData.images[1]) {
      alert("Please upload Image 2");
      return;
    }
    if (!formData.images[2]) {
      alert("Please upload Image 3");
      return;
    }
    if (!formData.images[3]) {
      alert("Please upload Image 4");
      return;
    }

    if (editId) {
      updateRoom(editId, formData);
    } else {
      addRoom();
    }

    closeModal();
  };


  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this room?")) {
      deleteRoom(id);
    }
  };

  /* ================= COMMON STYLES ================= */
  const gridStyle = {
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  };

  const imageGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: "14px",
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Room List"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Room",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "room_no", title: "Room No", align: "center" },
          { key: "room_name", title: "Room Name", align: "center" },
          { key: "booking_status", title: "Booked Status", align: "center", type: "badge" },
          { key: "working_status", title: "Working Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => openViewModal(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => handleEdit(row)}>
                  <Pencil size={16} />
                </button>
                <button className="table-action-btn delete" onClick={() => handleDelete(row.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW MODAL ================= */}
      {showViewModal && viewData && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>View Room</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid view" style={gridStyle}>
              {Object.entries(viewData).map(
                ([key, value]) =>
                  key !== "id" &&
                  key !== "images" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Room Images</label>
                <div style={imageGridStyle}>
                  {[
                    viewData.images?.image_1,
                    viewData.images?.image_2,
                    viewData.images?.image_3,
                    viewData.images?.image_4,
                  ].filter(Boolean).map((img, i) => (
                    <img
                      key={i}
                      src={img}
                      alt="room"
                      style={{
                        width: "100%",
                        height: "120px",
                        objectFit: "cover",
                        borderRadius: "8px",
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>{editId ? "Edit Room" : "Add Room"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid" style={gridStyle}>
              {[
                ["Room No", "room_no"],
                ["Room Name", "room_name"],
              ].map(([label, name]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input name={name} value={formData[name]} onChange={handleChange} />
                </div>
              ))}
              {/* room type and bed type using id and name */}

              <div className="form-group">
                <label>Room Type</label>
                <select
                  name="room_type_id"
                  value={formData.room_type_id || ""}
                  onChange={handleChange}
                >
                  <option value="">Select Room Type</option>
                  {roomTypes.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.room_type_name}
                      </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Bed Type</label>
                <select
                  name="bed_type_id"
                  value={formData.bed_type_id || ""}  
                  onChange={handleChange}
                >
                  <option value="">Select Bed Type</option>
                  {bedTypes.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.bed_type_name}
                      </option>
                  ))}
                </select>
              </div>


              {[
                ["Room Telephone", "room_telephone", "tel"],
                ["Max Adult", "max_adult", "number"],
                ["Max Child", "max_child", "number"],
              ].map(([label, name, type]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input name={name} value={formData[name]} onChange={handleChange} type={type || "text"} />
                </div>
              ))}

              {/* 🔥 FIXED SELECT SIZE */}
              <div className="form-group">
                <label>Booked Status</label>
                <select
                  name="booking_status"
                  value={formData.booking_status}
                  onChange={handleChange}
                >
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
              </div>

              <div className="form-group">
                <label>Working Status</label>
                <select
                  name="working_status"
                  value={formData.working_status}
                  onChange={handleChange}
                >
                  <option value="Working">Working</option>
                  <option value="Not Working">Not Working</option>
                </select>
              </div>
              <div className="form-group">
                <label>Room Status</label>
                <select
                  name="room_status"
                  value={formData.room_status}
                  onChange={handleChange}
                  disabled
                >
                  <option value="Available">Available</option>
                </select>
              </div>
              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Room Images</label>

                <div style={imageGridStyle}>
                  {(formData.images || []).map((img, i) => (
                    <div key={i}>
                      
                      {img instanceof File ? (
                        <img
                          src={URL.createObjectURL(img)}
                          alt="preview"
                          style={{
                            width: "100%",
                            height: "120px",
                            objectFit: "cover",
                            borderRadius: "8px",
                            marginBottom: "6px",
                          }}
                        />
                      ) : (
                        <div
                          style={{
                            width: "100%",
                            height: "120px",
                            border: "1px dashed gray",
                            borderRadius: "8px",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            fontSize: "12px",
                            color: "gray",
                            marginBottom: "6px",
                          }}
                        >
                          Upload Image {i + 1}
                        </div>
                      )}
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleImageChange(i, e.target.files[0])}
                      />
                    </div>
                  ))}
                </div>
              </div>

            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>Close</button>
              <button className="btn primary" onClick={handleSave}>Submit</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Rooms;

import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal"
import Input from "../stories/Form/Input";
import Select from "../stories/Form/Select";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";
import { useEffect } from "react";

const Rooms = () => {
  const [data, setData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
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

  const [alerts, setAlerts] = useState({
    show: false,
    message: "",
    type: "success",
    exiting: false,
  });

  const showAlert = (message, type = "success") => {
    setAlerts({
      show: true,
      message,
      type,
      exiting: false,
    });

    setTimeout(() => {
      setAlerts((prev) => ({ ...prev, exiting: true }));
    }, 1800);

    setTimeout(() => {
      setAlerts({
        show: false,
        message: "",
        type: "success",
        exiting: false,
      });
    }, 2200);
  };
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
    // GET /masterdata/room returns each row keyed as `id` (not `room_id`);
    // using row.room_id here made editId undefined, so the PUT sent an invalid
    // room_id and the update silently failed (422). Use row.id.
    setEditId(row.id);

    setFormData({
      room_no: row.room_no,
      room_name: row.room_name,
      room_status: row.room_status,
      room_telephone: row.room_telephone,
      room_type_id: row.room_type_id,
      bed_type_id : row.bed_type_id,
      max_adult: row.max_adult,
      max_child: row.max_child,
      booking_status: row.booking_status,
      working_status: row.working_status,
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
    try {
      const response = await APICall.getT("/masterdata/room");
      const rows = Array.isArray(response?.data) ? response.data : [];
      setData(rows.map((room) => ({ ...room, images: room.images })));
    } catch (err) {
      // Previously uncaught: the request rejected, nothing handled it, and the
      // table just stayed empty as though there were no rooms.
      setData([]);
      showAlert(err?.message || "Failed to load rooms.", "error");
    }
  };


  const getAllroom_type_ids = async () => {
    try {
      const res = await APICall.getT("/masterdata/room_types");
      setRoomTypes(Array.isArray(res?.data) ? res.data : []);
    } catch (err) {
      setRoomTypes([]);
      showAlert(err?.message || "Failed to load room types.", "error");
    }
  };

  const getAllbed_type_ids = async () => {
    try {
      const res = await APICall.getT("/masterdata/bed_types");
      setBedTypes(Array.isArray(res?.data) ? res.data : []);
    } catch (err) {
      setBedTypes([]);
      showAlert(err?.message || "Failed to load bed types.", "error");
    }
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
        showAlert("Please upload Image 1", "error");
        return;
      }

      form.append("image_1", formData.images[0]);

      if (formData.images[1]) form.append("image_2", formData.images[1]);
      if (formData.images[2]) form.append("image_3", formData.images[2]);
      if (formData.images[3]) form.append("image_4", formData.images[3]);

      await APICall.postT("/masterdata/room", form);
      showAlert("Room added successfully", "success");
      getAllRooms();
    } catch (error) {
      showAlert(error.detail, "error");
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

      // Backend PUT /masterdata/room reads the telephone as `tele_no`; sending
      // it under `room_telephone` left the number unchanged on every edit.
      form.append("tele_no", updatedData.room_telephone);

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
      showAlert("Room updated successfully", "update");
      getAllRooms();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };


  const deleteRoom = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/room/${id}`);
      showAlert("Room deleted successfully", "delete");
      getAllRooms();
    }
    catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  };

  const handleImageChange = (index, file) => {
    if (!file) return;
    setFormData((prev) => {
      const images = [...prev.images];
      images[index] = file;
      return { ...prev, images };
    });
  };

  const handleSave = () => {
    if (!formData.room_no || !formData.room_name) {
      showAlert("Room No and Room Name are required", "error");
      return;
    }

    if (!formData.room_telephone) {
      showAlert("Room Telephone is required", "error");
      return;
    }

    if (!formData.images[0]) {
      showAlert("Please upload Image 1", "error");
      return;
    }
    if (!formData.images[1]) {
      showAlert("Please upload Image 2", "error");
      return;
    }
    if (!formData.images[2]) {
      showAlert("Please upload Image 3", "error");
      return;
    }
    if (!formData.images[3]) {
      showAlert("Please upload Image 4", "error");
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
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteRoom(deleteId);
    setDeleteId(null);
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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} onClick={() => openViewModal(row)} ariaLabel="View" />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} onClick={() => handleEdit(row)} ariaLabel="Edit" />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} onClick={() => handleDelete(row.id)} ariaLabel="Delete" />
              </div>
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW MODAL ================= */}
      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          title="View Room"
          onClose={() => setShowViewModal(false)}
          size="large"
        >
          <div style={{ display: "grid", gap: "18px 20px", ...gridStyle }}>
            {[
              ["Room No", "room_no"],
              ["Room Name", "room_name"],
            ].map(([label, name]) => (
              <Input key={name} label={label} name={name} value={viewData[name]} disabled />
            ))}

            <Input
              label="Room Type"
              disabled
              value={
                roomTypes.find(
                  (r) => String(r.id) === String(viewData?.room_type_id)
                )?.room_type_name || "-"
              }
            />

            <Input
              label="Bed Type"
              disabled
              value={
                bedTypes.find(
                  (b) => String(b.id) === String(viewData?.bed_type_id)
                )?.bed_type_name || "-"
              }
            />


            {[
              ["Room Telephone", "room_telephone", "tel"],
              ["Max Adult", "max_adult", "number"],
              ["Max Child", "max_child", "number"],
            ].map(([label, name]) => (
              <Input key={name} label={label} name={name} value={viewData[name]} disabled />
            ))}

            <Input label="Booked Status" disabled value={viewData.booking_status} />

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

        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {
        showModal && (
          <Modal
            isOpen={showModal}
            title={editId ? "Edit Room" : "Add Room"}
            onClose={() => setShowModal(false)}
            showFooter
            size="large"
            bodyLayout="single"
            actions={[
              {
                label: "Close",
                variant: "secondary",
                onClick: () => setShowModal(false),
              },
              {
                label: "Submit",
                variant: "primary",
                onClick: handleSave,
                autoFocus: true,
              },
            ]}
          >
            <div style={{ display: "grid", gap: "18px 20px", ...gridStyle }}>
              {[
                ["Room No", "room_no"],
                ["Room Name", "room_name"],
              ].map(([label, name]) => (
                <Input key={name} label={label} name={name} value={formData[name]} onChange={handleChange} />
              ))}
              {/* room type and bed type using id and name */}

              <Select
                label="Room Type"
                name="room_type_id"
                value={formData.room_type_id || ""}
                onChange={handleChange}
                placeholder="Select Room Type"
                options={roomTypes.map((r) => ({ value: r.id, label: r.room_type_name }))}
              />
              <Select
                label="Bed Type"
                name="bed_type_id"
                value={formData.bed_type_id || ""}
                onChange={handleChange}
                placeholder="Select Bed Type"
                options={bedTypes.map((b) => ({ value: b.id, label: b.bed_type_name }))}
              />


              {[
                ["Room Telephone", "room_telephone", "tel"],
                ["Max Adult", "max_adult", "number"],
                ["Max Child", "max_child", "number"],
              ].map(([label, name, type]) => (
                <Input key={name} label={label} name={name} value={formData[name]} onChange={handleChange} type={type || "text"} />
              ))}

              <Select
                label="Room Status"
                name="room_status"
                value={formData.room_status}
                onChange={handleChange}
                options={[
                  { value: "", label: "select Room Status", disabled: true },
                  { value: "Available", label: "Available" },
                  { value: "Occupied", label: "Occupied" },
                  { value: "Maintenance", label: "Maintenance" },
                ]}
              />


              <Select
                label="Working Status"
                name="working_status"
                value={formData.working_status}
                onChange={handleChange}
                options={[
                  { value: "Working", label: "Working" },
                  { value: "Not Working", label: "Not Working" },
                ]}
              />
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
          </Modal>
        )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Room"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this room? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default Rooms;

import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";

const defaultImages = [
  "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
  "https://images.unsplash.com/photo-1560066984-138dadb4c035",
  "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",
  "https://images.unsplash.com/photo-1590490360182-c33d57733427",
];

const Rooms = () => {
  const [data, setData] = useState([
    {
      id: 1,
      roomNo: "101",
      roomName: "Deluxe 101",
      roomType: "Deluxe",
      bedType: "King Bed",
      roomTelephone: "2001",
      maxAdult: 2,
      maxChild: 1,
      bookedStatus: "No",
      workingStatus: "Working",
      images: defaultImages,
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    roomNo: "",
    roomName: "",
    roomType: "",
    bedType: "",
    roomTelephone: "",
    maxAdult: "",
    maxChild: "",
    bookedStatus: "No",
    workingStatus: "Working",
    images: [...defaultImages],
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData(row);
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
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleImageChange = (index, file) => {
    if (!file) return;
    const preview = URL.createObjectURL(file);
    setFormData((prev) => {
      const images = [...prev.images];
      images[index] = preview;
      return { ...prev, images };
    });
  };

  const handleSave = () => {
    if (!formData.roomNo || !formData.roomName) return;

    if (editId) {
      setData((prev) =>
        prev.map((r) => (r.id === editId ? { ...r, ...formData } : r))
      );
    } else {
      setData((prev) => [...prev, { id: Date.now(), ...formData }]);
    }
    closeModal();
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((r) => r.id !== id));
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
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "roomName", title: "Room Name", align: "center" },
          { key: "bookedStatus", title: "Booked Status", align: "center", type: "badge" },
          { key: "workingStatus", title: "Working Status", align: "center", type: "badge" },
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
                  {viewData.images.map((img, i) => (
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
                ["Room No", "roomNo"],
                ["Room Name", "roomName"],
                ["Room Type", "roomType"],
                ["Bed Type", "bedType"],
                ["Room Telephone", "roomTelephone"],
                ["Max Adult", "maxAdult"],
                ["Max Child", "maxChild"],
              ].map(([label, name]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input name={name} value={formData[name]} onChange={handleChange} />
                </div>
              ))}

              {/* 🔥 FIXED SELECT SIZE */}
              <div className="form-group">
                <label>Booked Status</label>
                <select
                  name="bookedStatus"
                  value={formData.bookedStatus}
                  onChange={handleChange}
                >
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
              </div>

              <div className="form-group">
                <label>Working Status</label>
                <select
                  name="workingStatus"
                  value={formData.workingStatus}
                  onChange={handleChange}
                >
                  <option value="Working">Working</option>
                  <option value="Not Working">Not Working</option>
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Room Images</label>
                <div style={imageGridStyle}>
                  {formData.images.map((img, i) => (
                    <div key={i}>
                      <img
                        src={img}
                        alt="preview"
                        style={{
                          width: "100%",
                          height: "120px",
                          objectFit: "cover",
                          borderRadius: "8px",
                          marginBottom: "6px",
                        }}
                      />
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

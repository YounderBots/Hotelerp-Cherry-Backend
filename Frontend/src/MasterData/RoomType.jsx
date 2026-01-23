import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { UserPlus, X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";

const RoomType = () => {
  const [data, setData] = useState([
    {
      id: 1,
      roomType: "Deluxe",
      complementary: "Yes",
      roomCost: 3500,
      extraBedCost: 800,
      dailyRate: 3500,
      weeklyRate: 22000,
      bedOnlyRate: 3000,
      bedBreakfastRate: 3800,
      halfBoardRate: 4200,
      fullBoardRate: 4800,
    },
    {
      id: 2,
      roomType: "Executive",
      complementary: "No",
      roomCost: 4500,
      extraBedCost: 1000,
      dailyRate: 4500,
      weeklyRate: 28000,
      bedOnlyRate: 4000,
      bedBreakfastRate: 4800,
      halfBoardRate: 5200,
      fullBoardRate: 5800,
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    roomType: "",
    complementary: "No",
    roomCost: "",
    extraBedCost: "",
    dailyRate: "",
    weeklyRate: "",
    bedOnlyRate: "",
    bedBreakfastRate: "",
    halfBoardRate: "",
    fullBoardRate: "",
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
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.roomType.trim()) return;

    if (editId) {
      setData((prev) =>
        prev.map((item) =>
          item.id === editId ? { ...item, ...formData } : item
        )
      );
    } else {
      setData((prev) => [...prev, { id: Date.now(), ...formData }]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData(row);
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Room Type List"
        hasActionButton
        searchable
        pagination
        pageSize={4}
        exportable
        actionButton={{ 
          label: "Add Room Type",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "roomType", title: "Room Type", align: "center" },
          { key: "roomCost", title: "Room Cost", align: "center" },
          { key: "extraBedCost", title: "Extra Bed Cost", align: "center" },
          {
            key: "complementary",
            title: "Complementary",
            align: "center",
            type: "badge",
          },
          { key: "dailyRate", title: "Daily Rate", align: "center" },
          { key: "weeklyRate", title: "Weekly Rate", align: "center" },
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
                  onClick={() => handleEdit(row)}
                >
                  <Pencil size={16} />
                </button>
                <button
                  className="table-action-btn delete"
                  onClick={() => handleDelete(row.id)}
                >
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
          <div className="modal-card">
            <div className="modal-header">
              <h3>View Room Type</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid view">
              {Object.entries(viewData).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
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
          <div className="modal-card">
            <div className="modal-header">
              <h3>{editId ? "Edit Room Type" : "Add Room Type"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid">
              {[
                ["Room Type", "roomType"],
                ["Room Cost", "roomCost"],
                ["Extra Bed Cost", "extraBedCost"],
                ["Daily Rate", "dailyRate"],
                ["Weekly Rate", "weeklyRate"],
                ["Bed Only Rate", "bedOnlyRate"],
                ["Bed & Breakfast Rate", "bedBreakfastRate"],
                ["Half Board Rate", "halfBoardRate"],
                ["Full Board Rate", "fullBoardRate"],
              ].map(([label, name]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input
                    type={name === "roomType" ? "text" : "number"}
                    name={name}
                    value={formData[name]}
                    onChange={handleChange}
                  />
                </div>
              ))}

              <div className="form-group">
                <label>Complementary</label>
                <select
                  name="complementary"
                  value={formData.complementary}
                  onChange={handleChange}
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Close
              </button>
              <button className="btn primary" onClick={handleSave}>
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RoomType;

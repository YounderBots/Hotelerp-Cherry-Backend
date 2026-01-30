import React, { useState, useEffect } from "react";
import TableTemplate from "../stories/TableTemplate";
import { UserPlus, X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const RoomType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [complementary, setComplementary] = useState([])

  const initialForm = {
    roomType: "",
    complementary: "",
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

  const getComplementary = async () => {
    const optionVal = await APICall.getT("/masterdata/complementry")
    setComplementary(optionVal.data)
  }

  const getRoomTypes = async () => {
    try {
      const res = await APICall.getT("/masterdata/room_types");
      setData(res.data.data || res.data || []);
    } catch (error) {
      console.error("Get room types error", error);
    }
  };


  const createRoomType = async () => {
    try {
      await APICall.postT("/masterdata/room_types", {
        type_name: formData.roomType,
        room_cost: formData.roomCost,
        bed_cost: formData.extraBedCost,
        complementry: formData.complementary,
        daily_rate: formData.dailyRate,
        weekly_rate: formData.weeklyRate,
        bed_only_rate: formData.bedOnlyRate,
        bed_breakfast_rate: formData.bedBreakfastRate,
        half_board_rate: formData.halfBoardRate,
        full_board_rate: formData.fullBoardRate,
      });

      getRoomTypes();
    } catch (error) {
      console.error("Create room type error", error);
    }
  };

  const updateRoomType = async () => {
    try {
      await APICall.putT("/masterdata/room_types", {
        id: editId,
        type_name: formData.roomType,
        room_cost: formData.roomCost,
        bed_cost: formData.extraBedCost,
        complementry: formData.complementary,
        daily_rate: formData.dailyRate,
        weekly_rate: formData.weeklyRate,
        bed_only_rate: formData.bedOnlyRate,
        bed_breakfast_rate: formData.bedBreakfastRate,
        half_board_rate: formData.halfBoardRate,
        full_board_rate: formData.fullBoardRate

      });
      getRoomTypes();
    } catch (error) {
      console.error("Update room type error", error);
    }
  };

  const deleteRoomType = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/room_types/${id}`);
      getRoomTypes();
    } catch (error) {
      console.error("Delete room type error", error);
    }
  };



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
    const { name, value, type } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  };


  const handleSave = async () => {
    if (!formData.roomType.trim()) return;

    if (editId) {
      await updateRoomType();
    } else {
      await createRoomType();
    }

    closeModal();
  };


  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      roomType: row.room_type_name,
      roomCost: row.room_cost,
      extraBedCost: row.bed_cost,
      complementary: row.complementry,
      dailyRate: row.daily_rate,
      weeklyRate: row.weekly_rate,
      bedOnlyRate: row.bed_only_rate,
      bedBreakfastRate: row.bed_breakfast_rate,
      halfBoardRate: row.half_board_rate,
      fullBoardRate: row.full_board_rate,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Delete this room type?")) {
      deleteRoomType(id);
    }
  };


  useEffect(() => {
     getComplementary();
    getRoomTypes();
  }, []);


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
          { key: "room_type_name", title: "Room Type", align: "center" },
          { key: "room_cost", title: "Room Cost", align: "center" },
          { key: "bed_cost", title: "Extra Bed Cost", align: "center" },
          {
            key: "complementry",
            title: "Complementary",
            align: "center",
            type: "badge",
          },
          { key: "daily_rate", title: "Daily Rate", align: "center" },
          { key: "weekly_rate", title: "Weekly Rate", align: "center" },
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
                  <option value="" disabled>Select Complementary</option>
                  {complementary.map((e) => (
                    <option key={e.id} value={e.id}>{e.complementry_name}</option>
                  ))}
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

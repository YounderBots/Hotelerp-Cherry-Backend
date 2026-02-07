import React, { useState, useEffect } from "react";
import Modal from "../stories/Modal";
import TableTemplate from "../stories/TableTemplate";
import {
  UserPlus, X, Pencil, Trash2, Eye, CheckCircle,
  AlertTriangle,
} from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const RoomType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [complementary, setComplementary] = useState([])

  const [alerts, setAlerts] = useState({
    show: false,
    message: "",
    type: "success",
    exiting: false,
  });

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
      showAlert("RoomType added successfully", "success");
      getRoomTypes();
    } catch (error) {
      showAlert(error.detail, "error");
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
      showAlert("RoomType updated successfully", "update");
      getRoomTypes();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };

  const deleteRoomType = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/room_types/${id}`);
      showAlert("Room Type deleted successfully", "delete");
      getRoomTypes();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
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

  const exceptField = [
    "status",
    "created_by",
    "created_at",
    "updated_at",
    "company_id",
  ]

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
    if (window.confirm("Are you sure you want to delete this Facilities?")) {
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
        <Modal
          isOpen={showViewModal}
          title="View Room Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="modal-body grid view">
            {[
              ["Room Type", "room_type_name"],
              ["Room Cost", "room_cost"],
              ["Bed Cost", "bed_cost"],
              ["Daily Rate", "daily_rate"],
              ["Weekly Rate", "weekly_rate"],
              ["Bed Only Rate", "bed_only_rate"],
              ["Bed & Breakfast Rate", "bed_and_breakfast_rate"],
              ["Half Board Rate", "half_board_rate"],
              ["Full Board Rate", "full_board_rate"],
              ["Status", "status"],
            ].map(([label, key]) => (
              <div className="form-group" key={key}>
                <label>{label}</label>
                <input
                  value={viewData?.[key] ?? "-"}
                  disabled
                />
              </div>
            ))}

            <div className="form-group">
              <label>Complementary</label>
              <input
               style={{width:"110%"}}
                disabled
                value={
                  complementary.find(
                    (c) => String(c.id) === String(viewData?.complementry)
                  )?.complementry_name || "-"
                }
              />
            </div>
          </div>
        </Modal >

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {
        showModal && (
          <Modal
            isOpen={showModal}
            title={editId ? "Edit Room Type" : "Add Room Type"}
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


          </Modal>
        )
      }
      {
        alerts.show && (
          <div
            className={`toast toast-${alerts.type} ${alerts.exiting ? "toast-exit" : ""
              }`}
          >
            <span className="toast-icon">
              {alerts.type === "success" && <CheckCircle />}
              {alerts.type === "update" && <Pencil />}
              {alerts.type === "delete" && <Trash2 />}
              {alerts.type === "error" && <AlertTriangle />}
            </span>
            <span>{alerts.message}</span>
          </div>
        )
      }
    </>
  );
};

export default RoomType;

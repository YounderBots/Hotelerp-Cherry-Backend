import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal"
import {
  UserPlus, X, Pencil, Trash2, Eye, CheckCircle,
  AlertTriangle,
} from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const HallFloor = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    hall_name: "",
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

  const getHallFloor = async () => {
    const AllFloor = await APICall.getT("/masterdata/hall_floor");
    setData(AllFloor.data);
  };

  const createNewHall = async () => {
    try {
      await APICall.postT("/masterdata/hall_floor", {
        hall_name: formData.hall_name,
      });
      showAlert("HallFloor added successfully", "success");
      getHallFloor();
    } catch (error) {
      showAlert(error.detail, "error");
    }
  };

  const updatedHallFloor = async () => {
    try {
      await APICall.putT("/masterdata/hall_floor", {
        id: editId,
        hall_name: formData.hall_name,
      });
      showAlert("HallFloor updated successfully", "update");
      getHallFloor();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };

  const deleteHallFloor = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/hall_floor/${id}`);
      showAlert("HallFloor deleted successfully", "delete");
      getHallFloor();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  };

  useEffect(() => {
    getHallFloor();
  }, []);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.hall_name.trim()) return;

    if (editId) {
      updatedHallFloor();

    } else {
      createNewHall();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      hall_name: row.hall_name,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this room?")) {
      deleteHallFloor(id);
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Hall Floor List"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Hall Floor",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "hall_name",
            title: "Hall Floor Name",
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
          title="View Hall/Floor"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="modal-body single view">
            <div className="form-group">
              <label>Hall Floor Name</label>
              <input value={viewData.hall_name} disabled />
            </div>
          </div>
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Hall/Floor" : "Add Hall/Floor"}
          onClose={() => setShowModal(false)}
          showFooter
          size="medium"
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

          <div className="modal-body single">
            <div className="form-group">
              <label>Hall Floor Name</label>
              <input
                type="text"
                name="hall_name"
                value={formData.hall_name}
                onChange={handleChange}
              />
            </div>
          </div>
        </Modal>
      )}

      {alerts.show && (
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
      )}
    </>
  );
};

export default HallFloor;

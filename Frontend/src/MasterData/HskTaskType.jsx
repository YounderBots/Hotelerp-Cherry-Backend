import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const HskTaskType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    taskType: "",
    color: "#22c55e",
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

  const closeViewModal = () => {
    setShowViewModal(false);
    setViewData(null);
  };

  const getTask = async () => {
    const AllTask = await APICall.getT("/masterdata/task_type");
    setData(AllTask.data);
  }

  const createTask = async () => {
    try {
      await APICall.postT("/masterdata/task_type", {
        task_name: formData.taskType,
        color: formData.color
      });
      showAlert("Task Type added successfully", "success");
      getTask();
    } catch (error) {
      showAlert(error.detail, "error");
    }
  }

  const updateTask = async () => {
    try {
      await APICall.putT("/masterdata/task_type", {
        id: editId,
        task_name: formData.taskType,
        color: formData.color

      });
      showAlert("Task Type updated successfully", "update");
      getTask();
    }
    catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  }

  const deleteTask = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/task_type/${id}`)
      showAlert("Task Type deleted successfully", "delete");
      getTask();
    }
    catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.taskType.trim()) return;

    if (editId) {
      updateTask();
    } else {
      createTask();
    }
    getTask();

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      taskType: row.task_name,
      color: row.color,
    });
    setShowModal(true);
  };


  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this HSK TaskType?")) {
    deleteTask(id)}
  };

  useEffect(() => {
    getTask();
  }, []);

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Housekeeping Task Type"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Task Type",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "task_name",
            title: "Task Type",
            align: "center",
          },
          {
            key: "color",
            title: "Color",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    width: "20px",
                    height: "20px",
                    borderRadius: "50%",
                    backgroundColor: row.color,
                    border: "1px solid #e5e7eb",
                  }}
                />
              </div>
            ),
          },
          {
            key: "actions",
            title: "Actions",
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
          title="View HSK Task Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >

          <div className="modal-body single view">
            <div className="form-group">
              <label>Task Type</label>
              <input value={viewData.task_name} disabled />
            </div>

            <div className="form-group">
              <label>Color</label>
              <div style={{ display: "flex", justifyContent: "left" }}>
                <span

                  style={{
                    width: "28px",
                    height: "28px",
                    borderRadius: "50%",
                    backgroundColor: viewData.color,
                    border: "1px solid #e5e7eb",
                  }}
                />
              </div>
            </div>
          </div>
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit HSK Task Type" : "Add HSK Task Type"}
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

          <div className="modal-body single">
            <div className="form-group">
              <label>Task Type</label>
              <input
                name="taskType"
                value={formData.taskType}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Color</label>
              <input
                type="color"
                name="color"
                value={formData.color}
                onChange={handleChange}
                style={{ height: "42px", padding: "4px" }}
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

export default HskTaskType;

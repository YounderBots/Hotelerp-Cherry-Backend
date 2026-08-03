import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const HskTaskType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

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
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteTask(deleteId);
    setDeleteId(null);
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
          title="View HSK Task Type"
          onClose={() => setShowViewModal(false)}
          size="small"
          bodyLayout="grid"
        >
          <Input label="Task Type" disabled value={viewData.task_name} />

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
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit HSK Task Type" : "Add HSK Task Type"}
          onClose={() => setShowModal(false)}
          showFooter
          size="small"
          bodyLayout="grid"
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
          <Input
            label="Task Type"
            name="taskType"
            value={formData.taskType}
            onChange={handleChange}
          />
          <Input
            label="Color"
            type="color"
            name="color"
            value={formData.color}
            onChange={handleChange}
            style={{ height: "42px", padding: "4px" }}
          />
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Task Type"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this housekeeping task type? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default HskTaskType;

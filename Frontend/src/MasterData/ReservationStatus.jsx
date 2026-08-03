import React, { useState, useEffect } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const ReservationStatus = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const initialForm = {
    statusName: "",
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const getReserveStatus = async () => {
    const AllReserveStatus = await APICall.getT("/masterdata/reservation_status");
    setData(AllReserveStatus.data);
  }

  const createReserveStatus = async () => {
    try {
      await APICall.postT("/masterdata/reservation_status", {
        status_name: formData.statusName,
        color: formData.color
      });
      showAlert("Reservation status added successfully", "success");
      getReserveStatus();
    } catch (error) {
      showAlert(error.detail || "Create failed", "error");
    }
  }

  const updateReserveStatus = async () => {
    try {
      await APICall.putT("/masterdata/reservation_status", {
        id: editId,
        status_name: formData.statusName,
        color: formData.color

      });
      showAlert("Reservation status updated successfully", "update");
      getReserveStatus();
    }
    catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  }

  const deleteReserveStatus = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/reservation_status/${id}`)
      showAlert("Reservation status deleted successfully", "delete");
      getReserveStatus();
    }
    catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  }

  const handleSave = () => {
    if (!formData.statusName.trim()) return;

    if (editId) {
      updateReserveStatus();
    } else {
      createReserveStatus();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      statusName: row.reservation_status,
      color: row.color,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteReserveStatus(deleteId);
    setDeleteId(null);
  };

  useEffect(() => {
    getReserveStatus();
  }, [])
  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Reservation Status"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Reservation Status",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "reservation_status",
            title: "Reservation Status",
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
              <div
                style={{
                  display: "flex",
                  gap: "8px",
                  justifyContent: "center",
                }}
              >
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
          title="View Reservation Status"
          onClose={() => setShowViewModal(false)}
          size="small"
          bodyLayout="grid"
        >
          <Input label="Reservation Status" disabled value={viewData.reservation_status} />

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
          title={editId ? "Edit Reservation Status" : "Add Reservation Status"}
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
            label="Reservation Status"
            name="statusName"
            value={formData.statusName}
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
        title="Delete Reservation Status"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this reservation status? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />

    </>
  );
};

export default ReservationStatus;

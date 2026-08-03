import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal"
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import {
  UserPlus, X, Pencil, Trash2, Eye, CheckCircle,
  AlertTriangle,
} from "lucide-react";
import APICall from "../APICalls/APICalls";

const HallFloor = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

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
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteHallFloor(deleteId);
    setDeleteId(null);
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
          title="View Hall/Floor"
          onClose={() => setShowViewModal(false)}
          size="small"
        >
          <div className="modal-body single view">
            <Input label="Hall Floor Name" disabled value={viewData.hall_name} />
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
          size="small"
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
            <Input
              label="Hall Floor Name"
              type="text"
              name="hall_name"
              value={formData.hall_name}
              onChange={handleChange}
            />
          </div>
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Hall/Floor"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this hall/floor? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default HallFloor;

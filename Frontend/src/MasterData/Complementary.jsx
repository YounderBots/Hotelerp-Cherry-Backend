import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const Complementary = () => {

  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    name: "",
    description: "",
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


  const getAllData = async () => {
    const AllData = await APICall.getT("/masterdata/complementry");
    setData(AllData.data);
  }

  const createComplementary = async () => {
    try {
      await APICall.postT("/masterdata/complementry", {
        complementry_name: formData.name,
        description: formData.description,
      });
      showAlert("Complementry added successfully", "success");
      getAllData();
    }
    catch (error) {
      showAlert(error.detail || "Create failed", "error");
    }
  }

  const updateComplementary = async () => {
    try {
      await APICall.putT("/masterdata/complementry", {
        id: editId,
        complementry_name: formData.name,
        description: formData.description,

      })
      showAlert("Complementry updated successfully", "update");
      getAllData();
    }
    catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  }

  const deleteComplementry = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/complementry/${id}`)
      showAlert("Complementry deleted successfully", "delete");
    }
    catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  }

  useEffect(() => {
    getAllData();
  }, []);


  const handleSave = async () => {
    if (!formData.name.trim()) return;

    if (editId) {
      updateComplementary();
    } else {
      createComplementary();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      name: row.complementry_name,
      description: row.description
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this Complementry?")) {
      deleteComplementry(id);
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Complementary"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Complementary",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "complementry_name",
            title: "Complementary Name",
            align: "center",
          },
          {
            key: "description",
            title: "Description",
            align: "center",
            type: "custom",
            render: (row) => (
              <div
                style={{
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                  lineHeight: "1.4",
                }}
              >
                {row.description}
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
          title="View Complementry"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >

          <div className="modal-body single view">
            <div className="form-group">
              <label>Complementary Name</label>
              <input value={viewData.complementry_name} disabled />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={viewData.description}
                disabled
                rows={4}
                style={{ resize: "none" }}
              />
            </div>
          </div>
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Complementry" : "Add Complementry"}
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
              <label>Complementary Name</label>
              <input
                name="name"
                value={formData.name}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                placeholder="Enter full description"
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

export default Complementary;

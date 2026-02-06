import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const IdentificationProof = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    name: "",
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

  const getProof = async () => {
    const res = await APICall.getT("/masterdata/identity_proof");
    setData(res.data?.data || res.data || []);
  };

  const createProof = async () => {
    try {
      await APICall.postT("/masterdata/identity_proof", {
        proof_name: formData.name
      });
      showAlert("Identity Proof added successfully", "success");
      getProof();
    } catch (error) {
      showAlert(error.detail, "error");
    }
  }

  const updateProof = async () => {
    try {
      await APICall.putT("/masterdata/identity_proof", {
        id: editId,
        proof_name: formData.name
      });
      showAlert("Identity Proof updated successfully", "update");
      getProof();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };

  const deleteProof = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/identity_proof/${id}`);
      showAlert("Identity Proof deleted successfully", "delete");
      getProof();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }

  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.name.trim()) return;

    if (editId) {
      updateProof();
    } else {
      createProof();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({ name: row.proof_name });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this Identify Proof?")) {
      deleteProof(id)
    }
  };

  useEffect(() => {
    getProof();
  }, [])

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Identification Proof"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Identification Proof",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "proof_name",
            title: "Identification Proof Name",
            align: "center",
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
          title="View Identify Proof"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="modal-body single view">
            <div className="form-group">
              <label>Identification Proof Name</label>
              <input value={viewData.proof_name} disabled />
            </div>
          </div>

        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit  Identify Proof" : "Add  Identify Proof"}
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
              <label>Identification Proof Name</label>
              <input
                name="name"
                value={formData.name}
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

export default IdentificationProof;

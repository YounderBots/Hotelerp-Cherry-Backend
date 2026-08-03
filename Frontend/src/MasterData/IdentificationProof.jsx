import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const IdentificationProof = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

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
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteProof(deleteId);
    setDeleteId(null);
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
          title="View Identify Proof"
          onClose={() => setShowViewModal(false)}
          size="small"
        >
          <div className="modal-body single view">
            <Input label="Identification Proof Name" disabled value={viewData.proof_name} />
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
              label="Identification Proof Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
            />
          </div>
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Identification Proof"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this identification proof? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default IdentificationProof;

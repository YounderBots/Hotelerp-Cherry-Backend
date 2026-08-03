import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const PaymentMethods = () => {
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const getAllpayMethod = async () => {
    const AllpayMethod = await APICall.getT("/masterdata/payment_methods");
    setData(AllpayMethod.data);
  }

  const createPaymentMethod = async () => {
    try {
      await APICall.postT("/masterdata/payment_methods", {
        payment_method: formData.name,

      });
      showAlert("Payment Method added successfully", "success");
      getAllpayMethod();
    }
    catch (error) {
     showAlert(error.detail, "error");
    }
  }
  const updatePaymentMethod = async () => {
    try {
      await APICall.putT("/masterdata/payment_methods", {
        id: editId,
        payment_method: formData.name,

      });
      showAlert("Payment Method updated successfully", "update");
      getAllpayMethod();
    }
    catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  }


  const deletePaymentMethod = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/payment_methods/${id}`);
      showAlert("Paymeent Method deleted successfully", "delete");
      getAllpayMethod();
    }
    catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  }
  useEffect(() => {
    getAllpayMethod();

  }, [])

  const handleSave = () => {
    if (!formData.name.trim()) return;

    if (editId) {
      updatePaymentMethod();

    } else {
      createPaymentMethod();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      name: row.payment_method
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deletePaymentMethod(deleteId);
    setDeleteId(null);
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Payment Methods"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Payment Method",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "payment_method",
            title: "Payment Method Name",
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
          title="View Payment Method"
          onClose={() => setShowViewModal(false)}
          size="small"
        >

          <div className="modal-body single view">
            <Input label="Payment Method Name" disabled value={viewData.payment_method} />
          </div>
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit  Payment Method" : "Add  Payment Method"}
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
              label="Payment Method Name"
              name="name" value={formData.name}
              onChange={handleChange} />
          </div>
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Payment Method"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this payment method? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default PaymentMethods;

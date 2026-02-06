import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import { X, Pencil, Trash2, Eye,CheckCircle,AlertTriangle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const DiscountType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    discountCountry: "",
    discountName: "",
    discountPercentage: "",
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

  const getDiscountType = async () => {
    const AllDiscount = await APICall.getT("/masterdata/discount")
    setData(AllDiscount.data)
  }

  const createDiscount = async () => {
    try {
      await APICall.postT("/masterdata/discount", {
        country_id: formData.discountCountry,
        discount_name: formData.discountName,
        discount_percentage: formData.discountPercentage,
      });
      showAlert("Discount Type added successfully", "success");
      getDiscountType();
    } catch (error) {
      showAlert(error.detail, "error");
    }
  }

  const updatedDiscount = async () => {
    try {
      await APICall.putT("/masterdata/discount", {
        id: editId,
        country_id: formData.discountCountry,
        discount_name: formData.discountName,
        discount_percentage: formData.discountPercentage
      });
      showAlert("Discount Type updated successfully", "update");
      getDiscountType();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };

  const deleteDiscount = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/discount/${id}`);
      showAlert("Discount Type deleted successfully", "delete");
      getDiscountType();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  };

  useEffect(() => {
    getDiscountType();
  }, []);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (
      !formData.discountCountry ||
      !formData.discountName ||
      !formData.discountPercentage
    )
      return;

    if (editId) {
      updatedDiscount();
    } else {
      createDiscount();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      discountCountry: row.country_id,
      discountName: row.discount_name,
      discountPercentage: row.discount_percentage,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
     if (window.confirm("Are you sure you want to delete this Discount Type?")) {
    deleteDiscount(id);}
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Discount Type List"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Discount",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "country_id",
            title: "Discount Country",
            align: "center",
          },
          {
            key: "discount_name",
            title: "Discount Name",
            align: "center",
          },
          {
            key: "discount_percentage",
            title: "Discount Percentage (%)",
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
          title="View Discount Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >

          <div className="modal-body single view">
            <div className="form-group">
              <label>Discount Country</label>
              <input value={viewData.country_id} disabled />
            </div>

            <div className="form-group">
              <label>Discount Name</label>
              <input value={viewData.discount_name} disabled />
            </div>

            <div className="form-group">
              <label>Discount Percentage</label>
              <input value={viewData.discount_percentage} disabled />
            </div>
          </div>
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit  Discount Type" : "Add  Discount Type"}
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
              <label>Country Name</label>
              <input
                name="discountCountry"
                value={formData.discountCountry}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Discount Name</label>
              <input
                name="discountName"
                value={formData.discountName}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Discount Percentage</label>
              <input
                type="number"
                name="discountPercentage"
                value={formData.discountPercentage}
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

export default DiscountType;

import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const PaymentMethods = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    name: "",
  };

  const [formData, setFormData] = useState(initialForm);

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
      getAllpayMethod();
    }
    catch (error) {
      return error, " to create a Complementary";
    }
  }
  const updatePaymentMethod = async () => {
    try {
      await APICall.putT("/masterdata/payment_methods", {
        id: editId,
        payment_method: formData.name,

      });
      getAllpayMethod();
    }
    catch (error) {
      return error, " to create a Complementary";
    }
  }

  
  const deletePaymentMethod = async(id) => {
    try{
      await APICall.deleteT(`/masterdata/payment_methods/${id}`)
    }
    catch(error){
      return error
    }
  }
  useEffect(() => {
    getAllpayMethod();
    
  },[])

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
      name:row.payment_method
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deletePaymentMethod(id);
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
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Payment Method</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label>Payment Method Name</label>
                <input value={viewData.payment_method} disabled />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>{editId ? "Edit Payment Method" : "Add Payment Method"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Payment Method Name</label>
                <input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Close
              </button>
              <button className="btn primary" onClick={handleSave}>
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PaymentMethods;

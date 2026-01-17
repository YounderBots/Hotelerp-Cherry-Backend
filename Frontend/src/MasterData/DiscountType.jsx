import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";

const DiscountType = () => {
  const [data, setData] = useState([
    {
      id: 1,
      discountCountry: "India",
      discountName: "Festival Offer",
      discountPercentage: 10,
    },
    {
      id: 2,
      discountCountry: "UAE",
      discountName: "Seasonal Discount",
      discountPercentage: 15,
    },
  ]);

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

  const handleSave = () => {
    if (
      !formData.discountCountry ||
      !formData.discountName ||
      !formData.discountPercentage
    )
      return;

    if (editId) {
      setData((prev) =>
        prev.map((item) =>
          item.id === editId ? { ...item, ...formData } : item
        )
      );
    } else {
      setData((prev) => [...prev, { id: Date.now(), ...formData }]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData(row);
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
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
            key: "discountCountry",
            title: "Discount Country",
            align: "center",
          },
          {
            key: "discountName",
            title: "Discount Name",
            align: "center",
          },
          {
            key: "discountPercentage",
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
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Discount</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label>Discount Country</label>
                <input value={viewData.discountCountry} disabled />
              </div>

              <div className="form-group">
                <label>Discount Name</label>
                <input value={viewData.discountName} disabled />
              </div>

              <div className="form-group">
                <label>Discount Percentage</label>
                <input value={viewData.discountPercentage} disabled />
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
              <h3>{editId ? "Edit Discount" : "Add Discount"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

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

export default DiscountType;

import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const TaxTypes = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [taxcountry, setTaxNewCountry] = useState([])

  const initialForm = {
    taxCountry: "",
    taxName: "",
    taxPercentage: "",
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


  const getCountry = async () => {
    try {
      const res = await APICall.getT("/masterdata/country_currency")

      setTaxNewCountry(res.data);

    } catch (error) {
      console.error("Get country error", error);
    }
  };


  const getTax = async () => {
    const res = await APICall.getT("/masterdata/tax");
    setData(Array.isArray(res.data) ? res.data : res.data?.data || []);
  };

  const createTax = async () => {
    try {
      await APICall.postT("/masterdata/tax", {
        country_id: Number(formData.taxCountry),
        tax_name: formData.taxName,
        tax_percentage: Number(formData.taxPercentage),
      });
      showAlert("Tax Type added successfully", "success");
      getTax();
    } catch (error) {
      showAlert(error.detail, "error");

    }

  };

  const updateTax = async () => {
    try {
      await APICall.putT("/masterdata/tax", {
        id: editId,
        country_id: Number(formData.taxCountry),
        tax_name: formData.taxName,
        tax_percentage: Number(formData.taxPercentage),
      });
      showAlert("Tax Type updated successfully", "update");
      getTax();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }

  };

  const deleteTax = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/tax/${id}`);
      showAlert("Tax Type deleted successfully", "delete");
      getTax();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }

  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    if (!formData.taxCountry || !formData.taxName || !formData.taxPercentage)
      return;

    if (editId) {
      updateTax();
    } else {
      await createTax();
    }
    await getTax();

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      taxCountry: row.country_id,
      taxName: row.tax_name,
      taxPercentage: row.tax_percentage,
    });
    setShowModal(true);
  };


  const countryMap = taxcountry.reduce((map, c) => {
    map[c.id] = c.country_name;
    return map;
  }, {});



  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this Tax Type?")) {
      await deleteTax(id);
      await getTax();
    }
  };

  useEffect(() => {
    getTax();
    getCountry();
  }, []);

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Tax Types List"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Tax",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "country_id",
            title: "Tax Country",
            align: "center",
            type: "custom",
            render: (row) => countryMap[row.country_id] || "—",
          },

          {
            key: "tax_name",
            title: "Tax Name",
            align: "center",
          },
          {
            key: "tax_percentage",
            title: "Tax Percentage (%)",
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
      <p>Countries loaded: {taxcountry.length}</p>

      {/* ================= VIEW MODAL ================= */}
      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          title="View Tax Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="modal-body single view">
            <div className="form-group">
              <label>Tax Country</label>
              <input value={countryMap[viewData.country_id]} disabled />
            </div>

            <div className="form-group">
              <label>Tax Name</label>
              <input value={viewData.tax_name} disabled />
            </div>

            <div className="form-group">
              <label>Tax Percentage</label>
              <input value={viewData.tax_percentage} disabled />
            </div>
          </div>
        </Modal>




      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Tax Type" : "Add Tax Type"}
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
              <select
                name="taxCountry"
                value={formData.taxCountry}
                onChange={handleChange}
              >
                <option value="">Select Country</option>
                {taxcountry.map((e) => (
                  <option key={e.id} value={e.id}>{e.country_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Tax Name</label>
              <input
                name="taxName"
                value={formData.taxName}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Tax Percentage</label>
              <input
                type="number"
                name="taxPercentage"
                value={formData.taxPercentage}
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

export default TaxTypes;

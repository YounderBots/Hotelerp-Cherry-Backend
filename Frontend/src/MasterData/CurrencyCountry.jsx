import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import { X, Pencil, Trash2, Eye,CheckCircle,AlertTriangle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const CurrencyCountry = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    countryName: "",
    currencySymbol: "",
    currencyName: "",
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

  const getCurrency = async () => {
    const AllCurrency = await APICall.getT("/masterdata/country_currency")
    setData(AllCurrency.data)
  }

  const createCurrency = async () => {
    try {
      await APICall.postT("/masterdata/country_currency", {
        country_name: formData.countryName,
        symbol: formData.currencySymbol,
        currency_name: formData.currencyName,
      });
      showAlert("Country/Currency added successfully", "success");
      getCurrency();
    } catch (error) {
      showAlert(error.detail, "error");
    }
  };

  const updatedCurrency = async () => {
    try {
      await APICall.putT("/masterdata/country_currency", {
        id: editId,
        country_name: formData.countryName,
        symbol: formData.currencySymbol,
        currency_name: formData.countryName
      });
      showAlert("Country/Currency updated successfully", "update");
      getCurrency();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };

  const deleteCurrency = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/country_currency/${id}`)
      showAlert("Country/Currency deleted successfully", "delete");
      getCurrency();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (
      !formData.countryName.trim() ||
      !formData.currencySymbol.trim() ||
      !formData.currencyName.trim()
    )
      return;

    if (editId) {
      updatedCurrency();
    } else {
      createCurrency();
    }

    closeModal();
  };

  useEffect(() => {
    getCurrency();
  }, []);

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      countryName: row.country_name,
      currencySymbol: row.symbol,
      currencyName: row.currency_name
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this Country and Currency?")) {
      deleteCurrency(id);
    }
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Currency Country"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Currency",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "country_name",
            title: "Country Name",
            align: "center",
          },
          {
            key: "symbol",
            title: "Currency Symbol",
            align: "center",
          },
          {
            key: "currency_name",
            title: "Currency Name",
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
          title="View Currency/Country"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="modal-body single view">
            <div className="form-group">
              <label>Country Name</label>
              <input value={viewData.country_name} disabled />
            </div>

            <div className="form-group">
              <label>Currency Symbol</label>
              <input value={viewData.symbol} disabled />
            </div>

            <div className="form-group">
              <label>Currency Name</label>
              <input value={viewData.currency_name} disabled />
            </div>
          </div>

        </Modal>



      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Currency/Country" : "Add Currency/Country"}
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
                name="countryName"
                value={formData.countryName}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Currency Symbol</label>
              <input
                name="currencySymbol"
                value={formData.currencySymbol}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Currency Name</label>
              <input
                name="currencyName"
                value={formData.currencyName}
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

export default CurrencyCountry;

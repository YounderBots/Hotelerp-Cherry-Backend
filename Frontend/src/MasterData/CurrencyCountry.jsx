import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye,CheckCircle,AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const CurrencyCountry = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

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
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteCurrency(deleteId);
    setDeleteId(null);
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
          title="View Currency/Country"
          onClose={() => setShowViewModal(false)}
          size="medium"
          bodyLayout="grid"
        >
          <Input label="Country Name" disabled value={viewData.country_name} />
          <Input label="Currency Symbol" disabled value={viewData.symbol} />
          <Input label="Currency Name" disabled value={viewData.currency_name} />
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Currency/Country" : "Add Currency/Country"}
          onClose={() => setShowModal(false)}
          showFooter
          size="medium"
          bodyLayout="grid"
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
          <Input
            label="Country Name"
            name="countryName"
            value={formData.countryName}
            onChange={handleChange}
          />
          <Input
            label="Currency Symbol"
            name="currencySymbol"
            value={formData.currencySymbol}
            onChange={handleChange}
          />
          <Input
            label="Currency Name"
            name="currencyName"
            value={formData.currencyName}
            onChange={handleChange}
          />
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Currency/Country"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this currency/country entry? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default CurrencyCountry;

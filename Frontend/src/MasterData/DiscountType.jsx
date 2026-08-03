import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import Select from "../stories/Form/Select";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye,CheckCircle,AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const DiscountType = () => {
  const [data, setData] = useState([]);
  const [countries, setCountries] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

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

  const getCountry = async () => {
    try {
      const res = await APICall.getT("/masterdata/country_currency");
      setCountries(res.data);
    } catch (error) {
      console.error("Get country error", error);
    }
  };

  const getDiscountType = async () => {
    const AllDiscount = await APICall.getT("/masterdata/discount")
    setData(AllDiscount.data)
  }

  const createDiscount = async () => {
    try {
      await APICall.postT("/masterdata/discount", {
        country_id: Number(formData.discountCountry),
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
        country_id: Number(formData.discountCountry),
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
    getCountry();
  }, []);

  const countryMap = countries.reduce((map, c) => {
    map[c.id] = c.country_name;
    return map;
  }, {});

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
    setDeleteId(id);
  };

  const confirmDelete = () => {
    deleteDiscount(deleteId);
    setDeleteId(null);
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
            type: "custom",
            render: (row) => countryMap[row.country_id] || "—",
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
          title="View Discount Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
          bodyLayout="grid"
        >
          <Input label="Discount Country" disabled value={countryMap[viewData.country_id] || ""} />
          <Input label="Discount Name" disabled value={viewData.discount_name} />
          <Input label="Discount Percentage" disabled value={viewData.discount_percentage} />
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit  Discount Type" : "Add  Discount Type"}
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
          <Select
            label="Country Name"
            name="discountCountry"
            value={formData.discountCountry}
            onChange={handleChange}
            placeholder="Select Country"
            options={countries.map((c) => ({ value: c.id, label: c.country_name }))}
          />
          <Input
            label="Discount Name"
            name="discountName"
            value={formData.discountName}
            onChange={handleChange}
          />
          <Input
            label="Discount Percentage"
            type="number"
            name="discountPercentage"
            value={formData.discountPercentage}
            onChange={handleChange}
          />
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Discount Type"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this discount type? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default DiscountType;

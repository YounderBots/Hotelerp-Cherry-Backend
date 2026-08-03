import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import Select from "../stories/Form/Select";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import { X, Pencil, Trash2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import APICall from "../APICalls/APICalls";

const TaxTypes = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
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
      // Swallowed into the console before: the picker silently stayed empty.
      setTaxNewCountry([]);
      showAlert(error?.message || "Failed to load countries.", "error");
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



  const handleDelete = (id) => {
    setDeleteId(id);
  };

  const confirmDelete = async () => {
    await deleteTax(deleteId);
    await getTax();
    setDeleteId(null);
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
          title="View Tax Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
          bodyLayout="grid"
        >
          <Input label="Tax Country" disabled value={countryMap[viewData.country_id]} />
          <Input label="Tax Name" disabled value={viewData.tax_name} />
          <Input label="Tax Percentage" disabled value={viewData.tax_percentage} />
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Tax Type" : "Add Tax Type"}
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
            name="taxCountry"
            value={formData.taxCountry}
            onChange={handleChange}
            placeholder="Select Country"
            options={taxcountry.map((e) => ({ value: e.id, label: e.country_name }))}
          />
          <Input
            label="Tax Name"
            name="taxName"
            value={formData.taxName}
            onChange={handleChange}
          />
          <Input
            label="Tax Percentage"
            type="number"
            name="taxPercentage"
            value={formData.taxPercentage}
            onChange={handleChange}
          />
        </Modal>
      )}

      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Tax Type"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this tax type? This action cannot be undone.
      </ConfirmModal>

      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default TaxTypes;

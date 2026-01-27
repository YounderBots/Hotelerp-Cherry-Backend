import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const TaxTypes = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const[taxcountry,setTaxNewCountry]= useState([])

  const initialForm = {
    taxCountry: "",
    taxName: "",
    taxPercentage: "",
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
  await APICall.postT("/masterdata/tax", {
    country_id: Number(formData.taxCountry), // ensure number
    tax_name: formData.taxName,
    tax_percentage: Number(formData.taxPercentage),
  });
};

const updateTax = async () => {
  await APICall.putT("/masterdata/tax", {
    id: editId,
    country_id: Number(formData.taxCountry),
    tax_name: formData.taxName,
    tax_percentage: Number(formData.taxPercentage),
  });
};

const deleteTax = async (id) => {
  await APICall.deleteT(`/masterdata/tax/${id}`);
};

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async() => {
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
    await deleteTax(id);
    await getTax();
  };

  useEffect(()=>{
    getTax();
    getCountry();
  },[]);

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
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Tax</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

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
              <h3>{editId ? "Edit Tax" : "Add Tax"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Country Name</label>
                <select
                  name="taxCountry"
                  value={formData.taxCountry}
                  onChange={handleChange}
                >
                   <option value="">Select Country</option>
                  {taxcountry.map((e)=>(
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

export default TaxTypes;

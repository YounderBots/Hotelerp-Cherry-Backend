import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
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

  const getCurrency = async () =>{
    const AllCurrency = await APICall.getT("/masterdata/country_currency")
    setData(AllCurrency.data)
  }

  const createCurrency = async () =>{
    try{
      await APICall.postT("/masterdata/country_currency",{
        country_name:formData.countryName,
        symbol:formData.currencySymbol,
        currency_name:formData.currencyName,
      });
      getCurrency();
    } catch(error){
      return error,"Create Currency"
    }
  };

  const updatedCurrency = async ()=>{
    try{
      await APICall.putT("/masterdata/country_currency",{
        id:editId,
        country_name:formData.countryName,
        symbol:formData.currencySymbol,
        currency_name:formData.countryName
      });
      getCurrency();
    }catch(error){
      return error
    }
  };
  
  const deleteCurrency = async (id) =>{
    try{
      await APICall.deleteT(`/masterdata/country_currency/${id}`)
      getCurrency();
    } catch(error){
      return error;
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
  
  useEffect(()=>{
    getCurrency();
  },[]);

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      countryName:row.country_name,
      currencySymbol:row.symbol,
      currencyName:row.currency_name
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deleteCurrency(id);
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
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Currency</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

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
              <h3>{editId ? "Edit Currency" : "Add Currency"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

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

export default CurrencyCountry;

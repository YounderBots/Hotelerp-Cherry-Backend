import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const Complementary = () => {

  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    name: "",
    description: "",
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


  const getAllData = async () => {
    const AllData = await APICall.getT("/masterdata/complementry");
    setData(AllData.data);
  }

  const createComplementary = async () => {
    try {
      await APICall.postT("/masterdata/complementry", {
        complementry_name: formData.name,
        description: formData.description,
      });
      getAllData();
    }
    catch (error) {
      return error, " to create a Complementary";
    }
  }

  const updateComplementary = async () => {
    try {
      await APICall.putT("/masterdata/complementry", {
        id: editId,
        complementry_name: formData.name,
        description: formData.description,

      })
      getAllData();
    }
    catch (error) {
      return error, "to update bedType"
    }
  }

  const deleteComplementry = async(id) => {
    try{
      await APICall.deleteT(`/masterdata/complementry/${id}`)
    }
    catch(error){
      return error
    }
  }

  useEffect(() => {
    getAllData();
  }, []);


  const handleSave = async () => {
    if (!formData.name.trim() ) return;

    if (editId) {
      updateComplementary();
    } else {
      createComplementary();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      name:row.complementry_name,
      description : row.description
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deleteComplementry(id);
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Complementary"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Complementary",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "complementry_name",
            title: "Complementary Name",
            align: "center",
          },
          {
            key: "description",
            title: "Description",
            align: "center",
            type: "custom",
            render: (row) => (
              <div
                style={{
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                  lineHeight: "1.4",
                }}
              >
                {row.description}
              </div>
            ),
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
              <h3>View Complementary</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label>Complementary Name</label>
                <input value={viewData.complementry_name} disabled />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={viewData.description}
                  disabled
                  rows={4}
                  style={{ resize: "none" }}
                />
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
              <h3>
                {editId ? "Edit Complementary" : "Add Complementary"}
              </h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Complementary Name</label>
                <input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Enter full description"
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

export default Complementary;

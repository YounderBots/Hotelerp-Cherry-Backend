import React, { useState,useEffect } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const ReservationStatus = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    statusName: "",
    color: "#22c55e",
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

   const getReserveStatus = async () => {
    const AllReserveStatus = await APICall.getT("/masterdata/reservation_status");
    setData(AllReserveStatus.data);
  }

  const createReserveStatus = async () => {
    try {
      await APICall.postT("/masterdata/reservation_status", {
        status_name: formData.statusName,
        color: formData.color
      });
      getReserveStatus();
    } catch (error) {
      return error
    }
  }

   const updateReserveStatus = async () => {
    try {
      await APICall.putT("/masterdata/reservation_status", {
        id: editId,
        status_name: formData.statusName,
        color: formData.color

      });
      getReserveStatus();
    }
    catch (error) {
      return error ;
    }
  }

   const deleteReserveStatus = async (id)=>{
    try{
      await APICall.deleteT(`/masterdata/reservation_status/${id}`)
    }
    catch(error){
      return error
    }
  }

  const handleSave = () => {
    if (!formData.statusName.trim()) return;

    if (editId) {
     updateReserveStatus();
    } else {
      createReserveStatus();
    }
   
    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      statusName:row.reservation_status,
       color: row.color,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deleteReserveStatus(id);
  };

  useEffect(()=>{
    getReserveStatus();
  },[])
  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Reservation Status"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Reservation Status",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "reservation_status",
            title: "Reservation Status",
            align: "center",
          },
          {
            key: "color",
            title: "Color",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    width: "20px",
                    height: "20px",
                    borderRadius: "50%",
                    backgroundColor: row.color,
                    border: "1px solid #e5e7eb",
                  }}
                />
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
              <h3>View Reservation Status</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label>Reservation Status</label>
                <input value={viewData.reservation_status} disabled />
              </div>

              <div className="form-group">
                <label>Color</label>
                <div style={{ display: "flex", justifyContent: "left" }}>
                  <span
                    style={{
                      width: "28px",
                      height: "28px",
                      borderRadius: "50%",
                      backgroundColor: viewData.color,
                      border: "1px solid #e5e7eb",
                    }}
                  />
                </div>
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
                {editId ? "Edit Reservation Status" : "Add Reservation Status"}
              </h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Reservation Status</label>
                <input
                  name="statusName"
                  value={formData.statusName}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Color</label>
                <input
                  type="color"
                  name="color"
                  value={formData.color}
                  onChange={handleChange}
                  style={{ height: "42px", padding: "4px" }}
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

export default ReservationStatus;

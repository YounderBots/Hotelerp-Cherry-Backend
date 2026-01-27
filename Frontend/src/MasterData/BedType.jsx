import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { UserPlus, X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const BedType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [bedName, setbedNmae] = useState("")



  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setbedNmae("");
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const closeModal = () => {
    setbedNmae("")
    setShowModal(false);
    setEditId(null);
  };

  const closeViewModal = () => {
    setShowViewModal(false);
    setViewData(null);
  };


  const getBedData = async () => {
    const AllBedData = await APICall.getT("/masterdata/bed_types");
    setData(AllBedData.data);
  }

  const createBedType = async () => {
    try {
      await APICall.postT("/masterdata/bed_type", {
        bed_type: bedName
      });
      getBedData();
    }
    catch (error) {
      return error, " to create a BedType";
    }
  }

  const updateBedType = async () => {
    try {
      await APICall.putT("/masterdata/bed_type", {
        id: editId,
        bed_type: bedName
      })
      getBedData();
    }
    catch (error) {
      return error, "to update bedType"
    }
  }

  const deleteBedType = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/bed_type/${id}`)
      getBedData();
    }
    catch (error) {
      return error, "to Delete BedType"
    }
  }

  useEffect(() => {
    getBedData();
  }, []);

  const handleSave = async () => {
    if (!bedName.trim()) return;

    if (editId) {
      updateBedType();
    } else {
      await createBedType();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setbedNmae(row.bed_type_name)
    setEditId(row.id);
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deleteBedType(id);
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Bed Type List"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Bed Type",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          {
            key: "bed_type_name",
            title: "Bed Type",
            align: "center",
          },
          {
            key: "actions",
            title: "Action",
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
              <h3>View Bed Type</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label>Bed Type</label>
                <input value={viewData.bed_type_name} disabled />
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
              <h3>{editId ? "Edit Bed Type" : "Add Bed Type"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Bed Type</label>
                <input
                  type="text"
                  name="bedType"
                  value={bedName}
                  onChange={(e) => setbedNmae(e.target.value)}
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

export default BedType;

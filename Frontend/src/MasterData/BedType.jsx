import React, { useEffect, useState } from "react";
import Modal from "../stories/Modal"
import TableTemplate from "../stories/TableTemplate";
import {
  UserPlus, X, Pencil, Trash2, Eye, CheckCircle,
  AlertTriangle,
} from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const BedType = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [bedName, setbedNmae] = useState("")

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
      showAlert("Bed Type added successfully", "success");
      getBedData();
    }
    catch (error) {
      showAlert(error.detail, "error");
    }
  }

  const updateBedType = async () => {
    try {
      await APICall.putT("/masterdata/bed_type", {
        id: editId,
        bed_type: bedName
      })
      showAlert("Bed Type updated successfully", "update");
      getBedData();
    }
    catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  }

  const deleteBedType = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/bed_type/${id}`)
      showAlert("Bed Type deleted successfully", "delete");
      getBedData();
    }
    catch (error) {
      showAlert(error.detail || "Delete failed", "error");
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
        <Modal
          isOpen={showViewModal}
          title="View Bed Type"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="modal-body single view">
            <div className="form-group">
              <label>Bed Type</label>
              <input value={viewData.bed_type_name} disabled />
            </div>
          </div>
        </Modal>

      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Bed Type" : "Add Bed Type"}
          onClose={() => setShowModal(false)}
          showFooter
          size="medium"
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
              <label>Bed Type</label>
              <input
                type="text"
                name="bedType"
                value={bedName}
                onChange={(e) => setbedNmae(e.target.value)}
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

export default BedType;

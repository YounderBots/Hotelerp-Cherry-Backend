import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal";
import {
  Pencil,
  Trash2,
  Eye,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const Facilities = () => {

  const [data, setData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const [alerts, setAlerts] = useState({
    show: false,
    message: "",
    type: "success",
    exiting: false,
  });

  const initialForm = { facility_name: "" };
  const [formData, setFormData] = useState(initialForm);

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

  const getFacilitiesData = async () => {
    const res = await APICall.getT("/masterdata/facilities");
    setData(res.data);
  };

  const createFacility = async () => {
    try {
      await APICall.postT("/masterdata/facilities", {
        facility_name: formData.facility_name,
      });
      showAlert("Facility added successfully", "success");
      getFacilitiesData();
    } catch (error) {
      showAlert(error.detail, "error");
    }
  };

  const updateFacility = async () => {
    try {
      await APICall.putT("/masterdata/facilities", {
        id: editId,
        facility_name: formData.facility_name,
      });
      showAlert("Facility updated successfully", "update");
      getFacilitiesData();
    } catch (error) {
      showAlert(error.detail || "Update failed", "error");
    }
  };

  const deleteFacility = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/facilities/${id}`);
      showAlert("Facility deleted successfully", "delete");
      getFacilitiesData();
    } catch (error) {
      showAlert(error.detail || "Delete failed", "error");
    }
  };

  /* ================= HANDLERS ================= */
  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!formData.facility_name.trim()) {
      showAlert("Facility name is required", "error");
      return;
    }

    if (editId) {
      await updateFacility();
    } else {
      await createFacility();
    }

    setShowModal(false);
  };

  const handleEdit = (row) => {
    setFormData({ facility_name: row.facility_name });
    setEditId(row.id);
    setShowModal(true);
  };

  const handleView = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const handledelete = (id) => {
    if (window.confirm("Are you sure you want to delete this Facilities?")) {
      deleteFacility(id);
    }
  }

  useEffect(() => {
    getFacilitiesData();
  }, []);

  /* ================= UI ================= */
  return (
    <>
      <TableTemplate
        title="Facilities"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Facilities",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "facility_name", title: "Facility Name", align: "center" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
                <button
                  className="table-action-btn view"
                  onClick={() => handleView(row)}
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
                  onClick={() => handledelete(row.id)}
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
          title="View Facility"
          onClose={() => setShowViewModal(false)}
          size="medium"
        >
          <div className="form-group">
            <label>Facility Name</label>
            <input value={viewData.facility_name} readOnly />
          </div>
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Facility" : "Add Facility"}
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
          <div className="form-group">
            <label>Facility Name</label>
            <input
              type="text"
              value={formData.facility_name}
              onChange={(e) =>
                setFormData({ facility_name: e.target.value })
              }
            />
          </div>
        </Modal>
      )}

      {/* ================= TOAST ================= */}
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

export default Facilities;

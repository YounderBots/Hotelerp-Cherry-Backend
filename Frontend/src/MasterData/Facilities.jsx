import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal, { ConfirmModal } from "../stories/Modal";
import Input from "../stories/Form/Input";
import IconButton from "../stories/IconButton";
import Toast from "../stories/Toast";
import {
  Pencil,
  Trash2,
  Eye,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";
import APICall from "../APICalls/APICalls";
import { useApiResource } from "../hooks/useApiResource";

const Facilities = () => {

  const { data, reload: getFacilitiesData } = useApiResource(
    () => APICall.getT("/masterdata/facilities"),
    { select: (res) => res?.data ?? [] },
  );
  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

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

;

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
    if (saving) return;
    if (!formData.facility_name.trim()) {
      showAlert("Facility name is required", "error");
      return;
    }

    setSaving(true);
    try {
      if (editId) {
        await updateFacility();
      } else {
        await createFacility();
      }
      setShowModal(false);
    } finally {
      setSaving(false);
    }
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
    setDeleteId(id);
  }

  const confirmDelete = () => {
    deleteFacility(deleteId);
    setDeleteId(null);
  };


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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} onClick={() => handleView(row)} ariaLabel="View" />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} onClick={() => handleEdit(row)} ariaLabel="Edit" />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} onClick={() => handledelete(row.id)} ariaLabel="Delete" />
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
          size="small"
        >
          <Input label="Facility Name" value={viewData.facility_name} disabled />
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Facility" : "Add Facility"}
          onClose={() => setShowModal(false)}
          showFooter
          size="small"
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
              disabled: saving,
              autoFocus: true,
            },
          ]}
        >
          <Input
            label="Facility Name"
            type="text"
            value={formData.facility_name}
            onChange={(e) =>
              setFormData({ facility_name: e.target.value })
            }
          />
        </Modal>
      )}

      {/* ================= DELETE CONFIRM MODAL ================= */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
        title="Delete Facility"
        confirmText="Delete"
        destructive
      >
        Are you sure you want to delete this facility? This action cannot be undone.
      </ConfirmModal>

      {/* ================= TOAST ================= */}
      <Toast show={alerts.show} message={alerts.message} type={alerts.type} exiting={alerts.exiting} />
    </>
  );
};

export default Facilities;

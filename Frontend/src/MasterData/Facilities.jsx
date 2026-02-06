import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import Modal from "../stories/Modal"
import AlertModal from "../stories/Modal.stories"
import { UserPlus, X, Pencil, Trash2, Eye, CheckCircle } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const Facilities = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [alert, setalert] = useState({
    show: false,
    message: "",
    type: "success",
  });



  const initialForm = {
    facility_name: "",
  };

  const [formData, setFormData] = useState(initialForm);

  /* -------------------- HANDLERS -------------------- */

  const openAddModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const closeModal = () => {
    setFormData(initialForm);
    setEditId(null);
    setShowModal(false);
  };

  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const showalert = (message, type = "success") => {
    setalert({ show: true, message, type });

    setTimeout(() => {
      setalert({ show: false, message: "", type: "" });
    }, 2000);
  };



  const getFacilitiesData = async () => {
    const AllFacilitesAPI = await APICall.getT("/masterdata/facilities");
    setData(AllFacilitesAPI.data);
  };

  const createNewFacility = async () => {
    try {
      await APICall.postT("/masterdata/facilities", {
        facility_name: formData.facility_name,
      });
      showalert("Facility added successfully","success");
      getFacilitiesData();

    } catch (error) {
      return error, "Create facility"
    }
  };


  const updateNewFacility = async () => {
    try {
      await APICall.putT("/masterdata/facilities", {
        id: editId,
        facility_name: formData.facility_name,
      });
      showalert("Facility updated successfully","update");
      getFacilitiesData();
    } catch (error) {
      return error, "Update facility"
    }
  };


  const deleteFacility = async (id) => {
    try {
      await APICall.deleteT(`/masterdata/facilities/${id}`);
      getFacilitiesData();
      showalert("Facility deleted successfully","delete");
    } catch (error) {
      return error, "Delete facility";
    }
  };


  const handleSave = async () => {
    if (!formData.facility_name.trim()) return;

    if (editId) {
      await updateNewFacility();
    } else {
      await createNewFacility();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setFormData({
      facility_name: row.facility_name
    });
    setEditId(row.id);
    setShowModal(true);
  };

  const handleDelete = (id) => {

    deleteFacility(id);
  };

  useEffect(() => {
    getFacilitiesData();
  }, []);

  /* -------------------- UI -------------------- */

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
          title="View Facilities"
          data={viewData}
          onClose={closeViewModal}
          size="medium">

          <div className="form-group">
            <label>Facility Name</label>
            <input
              name="facility_name"
              value={viewData.facility_name}
              readOnly
            />
          </div>

        </Modal>


      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (

        <Modal
          isOpen={showModal}
          title={editId ? "Edit Facilities" : "Add Facilities"}
          onClose={closeModal}
          showFooter={true}
          size="medium"
          bodyLayout="single"
          actions={[
            {
              label: "Close",
              variant: "secondary",
              onClick: closeModal,
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
              name="facility_name"
              value={formData.facility_name}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  facility_name: e.target.value,
                })
              }
            />

          </div>
        </Modal>


      )}


      {alert.show && (
        <div className={`toast toast-${alert.type}`}>
          <span className="toast-icon">
            {alert.type === "success" && <CheckCircle/>}
            {alert.type === "update" && <Pencil/>}
            {alert.type === "delete" && <Trash2/>}
          </span>
          <span>{alert.message}</span>
        </div>
      )}



    </>
  );
};

export default Facilities;

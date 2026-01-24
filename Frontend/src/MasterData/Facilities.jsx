import React, { useEffect, useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { UserPlus, X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";
import APICall from "../APICalls/APICalls";

const Facilities = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [facilityName, setFacilityName] = useState("");
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  /* -------------------- HANDLERS -------------------- */

  const openAddModal = () => {
    setFacilityName("");
    setEditId(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const closeModal = () => {
    setFacilityName("");
    setEditId(null);
    setShowModal(false);
  };

  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };
  const getFacilitiesData = async () => {
    // const companyId = "COMP001";
    const AllFacilitesAPI = await APICall.getT("/masterdata/facilities");
    setData(AllFacilitesAPI.data);
  };

  const createNewFacility = async () => {
    const formdata = {
      facility_name: facilityName,
      company_id: "COMP001",
      created_by: "admin",
    };
    //     {
    //   "facility_name": "Conference Hall",
    //   "company_id": "COMP001",
    //   "created_by": "admin"
    // }

    await APICall.postT("/masterdata/facilities", formdata);
    getFacilitiesData();
  };
  const updateNewFacility = async () => {
    const formdata = {
      id: editId,
      facility_name: facilityName,
      company_id: "COMP001",
    };

  

    await APICall.putT("/masterdata/facilities", formdata);
    getFacilitiesData();
  };

  const handleSave = () => {
    if (!facilityName.trim()) return;

    if (editId) {
      updateNewFacility();
    } else {
      // setData((prev) => [...prev, { id: Date.now(), name: facilityName }]);
      createNewFacility();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setFacilityName(row.Facility_Name);
    setEditId(row.id);
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
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
          { key: "Facility_Name", title: "Facility Name", align: "center" },
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
              <h3>View Facility</h3>
              <button onClick={closeViewModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single view">
              <div className="form-group">
                <label>Facility Name</label>
                <input value={viewData.name} disabled />
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
          <div className="modal-card modal-md">
            <div className="modal-header">
              <h3>{editId ? "Edit Facility" : "Add Facility"}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single edit">
              <div className="form-group">
                <label>Facility Name</label>
                <input
                  type="text"
                  value={facilityName}
                  onChange={(e) => setFacilityName(e.target.value)}
                  autoFocus
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Cancel
              </button>
              <button className="btn primary" onClick={handleSave}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Facilities;

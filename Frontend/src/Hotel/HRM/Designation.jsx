import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const Designation = () => {
    const [data, setData] = useState([]);

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [editId, setEditId] = useState(null);
    const [viewData, setViewData] = useState(null);

    const initialForm = {
        designationName: "",
    };

    const [formData, setFormData] = useState(initialForm);

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

    const getDesignation = async () => {
        const AllRoles = await APICall.getT("/user/designations");
        setData(AllRoles.data);
    }

    const createDesignation = async () => {
        try {
            await APICall.postT("/user/designations", {
                designation_name: formData.designationName,

            });
            getDesignation();
        } catch (error) {
            return error
        }
    }

    const updateDesignation = async () => {
        try {
            await APICall.putT("/user/designations", {
                id: editId,
                designation_name: formData.designationName,


            });
            getDesignation();
        }
        catch (error) {
            return error;
        }
    }

    const deleteDesignation = async (id) => {
        try {
            await APICall.deleteT(`/user/designations/${id}`)
        }
        catch (error) {
            return error
        }
    }

    useEffect(() => {
        getDesignation();
    }, [])

    const handleSave = () => {
        if (!formData.designationName)
            return;

        if (editId) {
            updateDesignation();
        } else {
            createDesignation();
        }

        closeModal();
    };

    const handleEdit = (row) => {
        setEditId(row.id);
        setFormData({
            designationName: row.designation_name
        });
        setShowModal(true);
    };

    const handleDelete = (id) => {
        deleteDesignation(id);
    }
    return (
        <>
            <TableTemplate
                title="Designation List"
                hasActionButton
                searchable
                pagination
                exportable
                actionButton={{
                    label: "Add Designation",
                    onClick: openAddModal,
                    size: "medium",
                    variant: "primary",
                }}
                columns={[
                    {
                        key: "designation_name",
                        title: "Designation Name",
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
                            <h3>View Designation</h3>
                            <button onClick={closeViewModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single view">
                            <div className="form-group">
                                <label>Designation Name</label>
                                <input value={viewData.designation_name} disabled />
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


            {showModal && (
                <div className="modal-overlay">
                    <div className="modal-card modal-sm">
                        <div className="modal-header">
                            <h3>{editId ? "Edit Designation" : "Add Designation"}</h3>
                            <button onClick={closeModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single">
                            <div className="form-group">
                                <label>Designation Name</label>
                                <input
                                    name="designationName"
                                    value={formData.designationName}
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


export default Designation;

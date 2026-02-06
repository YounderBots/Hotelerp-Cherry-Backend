import React, { use, useState, useEffect } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal"
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const Department = () => {
    const [data, setData] = useState([]);

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [editId, setEditId] = useState(null);
    const [viewData, setViewData] = useState(null);

    const initialForm = {
        department_name: "",
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

    const getAllData = async () => {
        const getAllData = await APICall.getT("/user/departments");
        setData(getAllData.data);
    }
    useEffect(() => {
        getAllData();
    }, []);

    const createDepartment = async () => {
        try {
            await APICall.postT("/user/departments", {
                department_name: formData.department_name,
            });
            getAllData();
        } catch (error) {
            return error, " to create a Department";
        }
    };
    const updateDepartment = async () => {
        try {
            await APICall.putT("/user/departments", {
                id: editId,
                department_name: formData.department_name,
            });
            getAllData();
        } catch (error) {
            return error, " to update a Department";
        }
    };
    const deleteDepartment = async (id) => {
        try {
            await APICall.deleteT(`/user/departments/${id}`);
            getAllData();
        } catch (error) {
            return error, " to delete a Department";
        }
    };

    const handleSave = async () => {
        if (
            !formData.department_name
        )
            return;

        if (editId) {
            await updateDepartment();
        } else {
            await createDepartment();
        }

        closeModal();
    };

    const handleEdit = (row) => {
        setEditId(row.id);
        setFormData(row);
        setShowModal(true);
    };

    const handleDelete = (id) => {
        deleteDepartment(id);
    };

    return (
        <>
            <TableTemplate
                title="Department List"
                hasActionButton
                searchable
                pagination
                exportable
                actionButton={{
                    label: "Add Department",
                    onClick: openAddModal,
                    size: "medium",
                    variant: "primary",
                }}
                columns={[
                    {
                        key: "department_name",
                        title: "Department Name",
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
                <Modal
                    isOpen={showViewModal}
                    title="View Department"
                    data={viewData}
                    onClose={closeViewModal}
                    size="small">
                    <div className="form-group">
                        <label>Department Name</label>
                        <input
                            name="department_name"
                            value={viewData.department_name}
                            onChange={handleChange}
                            readOnly
                        />
                    </div>
                </Modal>
            )}



            {showModal && (
                <Modal
                    isOpen={showModal}
                    title={editId ? "Edit Department" : "Add Department"}
                    onClose={closeModal}
                    showFooter={true}
                    size="small"
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
                        <label>Department Name</label>
                        <input
                            name="department_name"
                            value={formData.department_name}
                            onChange={handleChange}
                        />
                    </div>
                </Modal>
            )}

        </>
    );
};

export default Department;

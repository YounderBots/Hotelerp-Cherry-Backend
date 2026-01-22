import React, { useState } from "react";
import TableTemplate from "../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../MasterData/MasterData.css";

const Department = () => {
    const [data, setData] = useState([
        {
            id: 1,
            departmentName: "Store"
        },

    ]);

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [editId, setEditId] = useState(null);
    const [viewData, setViewData] = useState(null);

    const initialForm = {
        departmentName: "",
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

    const handleSave = () => {
        if (
            !formData.departmentName

        )
            return;

        if (editId) {
            setData((prev) =>
                prev.map((item) =>
                    item.id === editId ? { ...item, ...formData } : item
                )
            );
        } else {
            setData((prev) => [...prev, { id: Date.now(), ...formData }]);
        }

        closeModal();
    };

    const handleEdit = (row) => {
        setEditId(row.id);
        setFormData(row);
        setShowModal(true);
    };

    const handleDelete = (id) => {
        setData((prev) => prev.filter((item) => item.id !== id));
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
                        key: "departmentName",
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
                <div className="modal-overlay">
                    <div className="modal-card modal-sm">
                        <div className="modal-header">
                            <h3>View Department</h3>
                            <button onClick={closeViewModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single view">
                            <div className="form-group">
                                <label>Department Name</label>
                                <input value={viewData.departmentName} disabled />
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
                            <h3>{editId ? "Edit Department" : "Add Department"}</h3>
                            <button onClick={closeModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single">
                            <div className="form-group">
                                <label>Department Name</label>
                                <input
                                    name="departmentName"
                                    value={formData.departmentName}
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

export default Department;

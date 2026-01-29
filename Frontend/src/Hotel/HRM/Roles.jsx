import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../../MasterData/MasterData.css";

const Role = () => {
    const [data, setData] = useState([
        {
            id: 1,
            roleName: "Admin",
            description: "Handles Entire System",
        },
    ]);

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [editId, setEditId] = useState(null);
    const [viewData, setViewData] = useState(null);

    const initialForm = {
        roleName: "",
        description: "",
    };

    const [formData, setFormData] = useState(initialForm);

    // ---------------- OPEN / CLOSE ----------------
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
        setFormData(initialForm);
    };

    const closeViewModal = () => {
        setShowViewModal(false);
        setViewData(null);
    };

    // ---------------- FORM HANDLING ----------------
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSave = () => {
        if (!formData.roleName || !formData.description) return;

        if (editId) {
            setData((prev) =>
                prev.map((item) =>
                    item.id === editId
                        ? { ...item, ...formData }
                        : item
                )
            );
        } else {
            setData((prev) => [
                ...prev,
                { id: Date.now(), ...formData },
            ]);
        }

        closeModal();
    };

    const handleEdit = (row) => {
        setEditId(row.id);
        setFormData({
            roleName: row.roleName,
            description: row.description,
        });
        setShowModal(true);
    };

    const handleDelete = (id) => {
        setData((prev) => prev.filter((item) => item.id !== id));
    };

    return (
        <>
            <TableTemplate
                title="Role List"
                hasActionButton
                searchable
                pagination
                exportable
                actionButton={{
                    label: "Add Role",
                    onClick: openAddModal,
                    size: "medium",
                    variant: "primary",
                }}
                columns={[
                    {
                        key: "roleName",
                        title: "Role Name",
                        align: "center",
                    },
                    {
                        key: "description",
                        title: "Description",
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
                            <h3>View Role</h3>
                            <button onClick={closeViewModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single view">
                            <div className="form-group">
                                <label>Role Name</label>
                                <input value={viewData.roleName} disabled />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    value={viewData.description}
                                    disabled
                                />
                            </div>
                        </div>

                        <div className="modal-footer">
                            <button
                                className="btn secondary"
                                onClick={closeViewModal}
                            >
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
                            <h3>{editId ? "Edit Role" : "Add Role"}</h3>
                            <button onClick={closeModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single">
                            <div className="form-group">
                                <label>Role Name</label>
                                <input
                                    name="roleName"
                                    value={formData.roleName}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div className="modal-footer">
                            <button
                                className="btn secondary"
                                onClick={closeModal}
                            >
                                Close
                            </button>
                            <button
                                className="btn primary"
                                onClick={handleSave}
                            >
                                Submit
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Role;

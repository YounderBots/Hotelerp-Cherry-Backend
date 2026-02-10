import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";
const Role = () => {
    const [data, setData] = useState([]);

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

    const getRoles = async () => {
        const AllRoles = await APICall.getT("/user/roles");
        setData(AllRoles.data);
    }

    const createRoles = async () => {
        try {
            await APICall.postT("/user/roles", {
                role_name: formData.roleName,
                description: formData.description
            });
            getRoles();
        } catch (error) {
            return error
        }
    }

    const updateRoles = async () => {
        try {
            await APICall.putT("/user/roles", {
                id: editId,
                role_name: formData.roleName,
                description: formData.description

            });
            getRoles();
        }
        catch (error) {
            return error;
        }
    }

    const deleteRoles = async (id) => {
        try {
            await APICall.deleteT(`/user/roles/${id}`)
        }
        catch (error) {
            return error
        }
    }

    useEffect(() => {
        getRoles();
    }, [])
    const handleSave = () => {
        if (!formData.roleName || !formData.description) return;

        if (editId) {
            updateRoles();
        } else {
            createRoles();
        }

        closeModal();
    };

    const handleEdit = (row) => {
        setEditId(row.id);
        setFormData({
            roleName: row.role_name,
            description: row.description,
        });
        setShowModal(true);
    };

    const handleDelete = (id) => {
        deleteRoles(id);
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
                        key: "role_name",
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
                <Modal
                    isOpen={showViewModal}
                    title="view Role"
                    onClose={() => setShowViewModal(false)}>
                    <div className="modal-body single view">
                        <div className="form-group">
                            <label>Role Name</label>
                            <input value={viewData.role_name} disabled />
                        </div>

                        <div className="form-group">
                            <label>Description</label>
                            <textarea
                                value={viewData.description}
                                disabled
                            />
                        </div>
                    </div>
                </Modal>
            )}

            {/* ================= ADD / EDIT MODAL ================= */}
            {showModal && (
                <Modal
                    isOpen={showModal}
                    title={editId ? "Edit Roles" : "Add Roles"}
                    onClose={() => setShowModal(false)}
                    showFooter
                    size="large"
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
                </Modal>
            )}
        </>
    );
};

export default Role;

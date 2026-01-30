import React, { use, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { X, Pencil, Trash2, Eye } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const Shift = () => {
    const [data, setData] = useState([]);

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [editId, setEditId] = useState(null);
    const [viewData, setViewData] = useState(null);

    const initialForm = {
        shift_name: "",
        start_time: "",
        end_time: "",
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
        const getAllData = await APICall.getT("/user/shifts");
        setData(getAllData.data);
    }
    useState(() => {
        getAllData();
    }, []);

    const createShift = async () => {
        try {
            await APICall.postT("/user/shifts", {
                shift_name: formData.shift_name,
                start_time: formData.start_time,
                end_time: formData.end_time,
            });
            getAllData();
        } catch (error) {
            return error, " to create a Shift";
        }
    };
    const updateShift = async () => {
        try {
            await APICall.putT("/user/shifts", {
                id: editId,
                shift_name: formData.shift_name,
                start_time: formData.start_time,
                end_time: formData.end_time,
            });
            getAllData();
        } catch (error) {
            return error, " to update a Shift";
        }
    };
    const deleteShift = async (id) => {
        try {
            await APICall.deleteT(`/user/shifts/${id}`);
            getAllData();
        } catch (error) {
            return error, " to delete a Shift";
        }
    };

    const handleSave = async() => {
        if (!formData.shift_name || !formData.start_time || !formData.end_time)
            return;

        if (editId) {
            updateShift();
        } else {
            await createShift();
        }

        closeModal();
    };

    const handleEdit = (row) => {
        setEditId(row.id);
        setFormData(row);
        setShowModal(true);
    };

    const handleDelete = (id) => {
        deleteShift(id);
    };

    return (
        <>
            <TableTemplate
                title="Shift List"
                hasActionButton
                searchable
                pagination
                exportable
                actionButton={{
                    label: "Add Shift",
                    onClick: openAddModal,
                    size: "medium",
                    variant: "primary",
                }}
                columns={[
                    {
                        key: "shift_name",
                        title: "Shift Name",
                        align: "center",
                    },
                    {
                        key: "start_time",
                        title: "Start Time",
                        align: "center",
                    },
                    {
                        key: "end_time",
                        title: "End Time",
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
                            <h3>View Shift</h3>
                            <button onClick={closeViewModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single view">
                            <div className="form-group">
                                <label>Shift Name</label>
                                <input value={viewData.shift_name} disabled />
                            </div>
                            <div className="form-group">
                                <label>Start Time</label>
                                <input value={viewData.start_time} disabled />
                            </div>
                            <div className="form-group">
                                <label>End Time</label>
                                <input value={viewData.end_time} disabled />
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
                    <div className="modal-card modal-sm">
                        <div className="modal-header">
                            <h3>{editId ? "Edit Shift" : "Add Shift"}</h3>
                            <button onClick={closeModal}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="modal-body single">
                            <div className="form-group">
                                <label>Shift Name</label>
                                <input
                                    name="shift_name"
                                    value={formData.shift_name}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label>Start Time</label>
                                <input
                                    type="time"
                                    name="start_time"
                                    value={formData.start_time}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label>End Time</label>
                                <input
                                    type="time"
                                    name="end_time"
                                    value={formData.end_time}
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

export default Shift;

import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";
import "../../MasterData/MasterData.css";

const TaskAssign = () => {
  const [data, setData] = useState([
    {
      id: 1,
      employeeName: "Ravi Kumar",
      roomNo: "101",
      assignedStaff: "Housekeeping",
      assignedDateTime: "2026-01-06 10:30",
      roomStatus: "Clean",
      taskStatus: "Assigned",
    },
    {
      id: 2,
      employeeName: "Suresh",
      roomNo: "203",
      assignedStaff: "Maintenance",
      assignedDateTime: "2026-01-06 14:00",
      roomStatus: "Dirty",
      taskStatus: "In Progress",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    employeeId: "",
    firstName: "",
    lastName: "",
    scheduleDate: "",
    scheduleTime: "",
    roomNo: "",
    taskType: "",
    assignedStaff: "",
    taskStatus: "Assigned",
    roomStatus: "Clean",
    lostAndFound: "",
    specialInstruction: "",
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData(row);
    setShowViewModal(true);
  };

  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.firstName || !formData.roomNo) return;

    const payload = {
      id: editId || Date.now(),
      employeeName: `${formData.firstName} ${formData.lastName}`,
      roomNo: formData.roomNo,
      assignedStaff: formData.assignedStaff,
      assignedDateTime: `${formData.scheduleDate} ${formData.scheduleTime}`,
      roomStatus: formData.roomStatus,
      taskStatus: formData.taskStatus,
    };

    if (editId) {
      setData((prev) => prev.map((i) => (i.id === editId ? payload : i)));
    } else {
      setData((prev) => [...prev, payload]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    const [firstName, lastName = ""] = row.employeeName.split(" ");
    setEditId(row.id);
    setFormData({
      ...initialForm,
      firstName,
      lastName,
      roomNo: row.roomNo,
      assignedStaff: row.assignedStaff,
      taskStatus: row.taskStatus,
      roomStatus: row.roomStatus,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((i) => i.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Task Assign"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{ 
          label: "Assign Task",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "employeeName", title: "Employee Name", align: "center" },
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "assignedStaff", title: "Assigned Staff", align: "center" },
          { key: "assignedDateTime", title: "Assigned Date Time", align: "center" },
          { key: "roomStatus", title: "Room Status", align: "center", type: "badge" },
          { key: "taskStatus", title: "Task Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => openViewModal(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => handleEdit(row)}>
                  <Pencil size={16} />
                </button>
                <button className="table-action-btn delete" onClick={() => handleDelete(row.id)}>
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
              <h3>View Task</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(([k, v]) => (
                <div className="form-group" key={k}>
                  <label>{k.replace(/([A-Z])/g, " $1")}</label>
                  <input value={v} disabled />
                </div>
              ))}
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{editId ? "Edit Task" : "Assign Task"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid">
              {[
                ["Employee ID", "employeeId"],
                ["First Name", "firstName"],
                ["Last Name", "lastName"],
                ["Schedule Date", "scheduleDate", "date"],
                ["Schedule Time", "scheduleTime", "time"],
                ["Room Number", "roomNo"],
                ["Task Type", "taskType"],
                ["Assigned Staff", "assignedStaff"],
                ["Lost & Found", "lostAndFound"],
              ].map(([label, name, type]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input
                    type={type || "text"}
                    name={name}
                    value={formData[name]}
                    onChange={handleChange}
                  />
                </div>
              ))}

              <div className="form-group">
                <label>Task Status</label>
                <select name="taskStatus" value={formData.taskStatus} onChange={handleChange}>
                  <option>Assigned</option>
                  <option>In Progress</option>
                  <option>Completed</option>
                </select>
              </div>

              <div className="form-group">
                <label>Room Status</label>
                <select name="roomStatus" value={formData.roomStatus} onChange={handleChange}>
                  <option>Clean</option>
                  <option>Dirty</option>
                  <option>Under Maintenance</option>
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Special Instruction</label>
                <input
                  name="specialInstruction"
                  value={formData.specialInstruction}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>Close</button>
              <button className="btn primary" onClick={handleSave}>Submit</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TaskAssign;

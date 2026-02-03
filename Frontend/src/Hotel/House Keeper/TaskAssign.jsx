import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const TaskAssign = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [Employee, setEmployee] = useState([]);
  const [roomNo, setroomNo] = useState([]);
  const [userCode, setUserCode] = useState("");

  const initialForm = {
    userCode: "",
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

  const getTaskAssign = async () => {
    const AllTaskAssign = await APICall.getT("/hotel/housekeeper_tasks");
    setData(AllTaskAssign.data);
  }

  const getAllRooms = async () => {
    const response = await APICall.getT("/masterdata/room");
    setroomNo(response.data)
  }


  const getEmployee = async () => {
    const AllRoles = await APICall.getT("/user/users");
    setEmployee(AllRoles.data);

    setUserCode(AllRoles.data[0]?.user_code || "");
  }

  const createHousekeeperTtasks = async () => {
    try {
      await APICall.postT("/hotel/housekeeper_tasks", {
        employee_id: formData.employeeId,
        first_name: formData.firstName,
        last_name: formData.lastName,
        room_no: Number(formData.roomNo),
        assign_staff: Number(formData.assignedStaff),
        schedule_date: formData.scheduleDate,
        schedule_time: formData.scheduleTime,
        task_status: formData.taskStatus,
        task_type: formData.taskType,
        lost_found: formData.lostAndFound,
        room_status: formData.roomStatus,
        special_instructions: formData.specialInstruction,

      });

      getTaskAssign();
    } catch (error) {
      console.error("Create error:", error.response?.data || error);
    }
  };
  const updateHousekeeperTtasks = async () => {
    try {
      await APICall.putT("/hotel/housekeeper_tasks", {
        id: editId,
        employee_id: formData.employeeId,
        first_name: formData.firstName,
        last_name: formData.lastName,
        room_no: formData.roomNo,
        assign_staff: formData.assignedStaff,
        schedule_date: formData.scheduleDate,
        schedule_time: formData.scheduleTime,
        task_status: formData.taskStatus,
        task_type: formData.taskType,
        lost_found: formData.lostAndFound,
        room_status: formData.roomStatus,
        special_instructions: formData.specialInstruction,

      });

      getTaskAssign();
    } catch (error) {
      console.error("Create error:", error.response?.data || error);
    }
  };

  const deleteHousekeeperTtasks = async (id) => {
    try {
      await APICall.deleteT(`/hotel/housekeeper_tasks/${id}`)
    }
    catch (error) {
      return error
    }
  }

  useEffect(() => {
    getTaskAssign();
    getEmployee();
    getAllRooms();
  }, [])
  const employee_name = (row) =>
    `${row?.first_name || ""} ${row?.last_name || ""}`.trim();




  const handleSave = () => {
    if (!formData.firstName || !formData.roomNo) return;

    if (editId) {
      updateHousekeeperTtasks();
    } else {
      createHousekeeperTtasks();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    const firstName = row.first_name || "";
    const lastName = row.last_name || "";

    setEditId(row.id);
    setFormData({
      employeeId: row.employee_id,
      firstName,
      lastName,
      roomNo: row.room_no,
      assignedStaff: row.assign_staff,
      scheduleDate: row.schedule_date,
      scheduleTime: row.schedule_time,
      taskStatus: row.task_status,
      taskType: row.task_type,
      lostAndFound: row.lost_found,
      roomStatus: row.room_status,
      specialInstruction: row.special_instructions,
    });
    setShowModal(true);
  };



  const handleDelete = (id) => {
    deleteHousekeeperTtasks(id);
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
          {
            key: "first_name",
            title: "Employee Name",
            align: "center",
          },
          { key: "room_no", title: "Room No", align: "center" },
          { key: "assign_staff", title: "Assigned Staff", align: "center" },
          { key: "schedule_time", title: "Assigned Date Time", align: "center" },
          { key: "room_status", title: "Room Status", align: "center", type: "badge" },
          { key: "task_status", title: "Task Status", align: "center", type: "badge" },
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

              {Object.entries(viewData).map(([k, v]) => {
                if (k === "employee_id") {
                  return (
                    <div className="form-group">
                      <label>Employee ID</label>
                      <input
                        type="text"
                        value={userCode}
                        readOnly
                        className="form-control"
                      />
                    </div>
                  )

                }

                return (
                  <div className="form-group" key={k}>
                    <label>{k.replace(/([A-Z])/g, " $1")}</label>
                    <input value={v} disabled />
                  </div>
                );
              })}
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
              <div className="form-group">
                <label>Employee ID</label>
                <select>
                  <option value="" disabled>Select ID</option>
                  {Employee.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.user_code}
                    </option>
                  ))}
                </select>
              </div>

              {[
                ["First Name", "firstName"],
                ["Last Name", "lastName"],
                ["Schedule Date", "scheduleDate", "date"],
                ["Schedule Time", "scheduleTime", "time"],
                ["Task Type", "taskType"],
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
                <label>Room Number</label>
                <select name="roomNo" value={formData.roomNo} onChange={handleChange}>
                  <option disabled value="">Select the Room</option>
                  {roomNo.map((room) => (
                    <option key={room.id} value={room.id}>
                      {room.room_no}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Assigned Staff</label>
                <select name="assignedStaff" value={formData.assignedStaff} onChange={handleChange}>
                  <option disabled value="">Select the Staff</option>
                  {Employee.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.username}
                    </option>
                  ))}
                </select>
              </div>
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
                  <option>Blocking</option>
                  <option>Unblocking</option>
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

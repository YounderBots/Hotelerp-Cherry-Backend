import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import { Eye, Pencil, Trash2 } from "lucide-react";
import APICall from "../../APICalls/APICalls";

const TaskAssign = () => {
  const [data, setData] = useState([]);
  // This page had no way to report a failure at all: both save paths logged
  // to the console and the modal closed regardless, so a rejected save looked
  // exactly like a successful one.
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

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
    setFormError("");
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
  };
  const updateHousekeeperTtasks = async () => {
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
  };

  const deleteHousekeeperTtasks = async (id) => {
    // The original returned the error object from its catch, which the caller
    // ignored, so a failed delete looked identical to a successful one.
    try {
      await APICall.deleteT(`/hotel/housekeeper_tasks/${id}`);
      await getTaskAssign();
    } catch (error) {
      setFormError(error?.message || "Could not delete the task assignment.");
    }
  };

  useEffect(() => {
    getTaskAssign();
    getEmployee();
    getAllRooms();
  }, [])




  const handleSave = async () => {
    // A bare `return` gave no feedback — the button simply did nothing.
    if (!formData.firstName || !formData.roomNo) {
      setFormError("Staff first name and room number are required.");
      return;
    }

    setFormError("");
    setSaving(true);
    try {
      // Awaited now. These were fired and forgotten, and closeModal() ran
      // immediately, so the dialog closed before the request had resolved —
      // a rejected save looked exactly like a successful one.
      if (editId) {
        await updateHousekeeperTtasks();
      } else {
        await createHousekeeperTtasks();
      }
      closeModal();
    } catch (error) {
      setFormError(error?.message || "Could not save the task assignment.");
    } finally {
      setSaving(false);
    }
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
      {/* Delete runs from the table, not the dialog, so its failures need a
          home outside the modal — otherwise they are set and never seen. */}
      {formError && !showModal && (
        <div role="alert" style={{ marginBottom: 12, color: "var(--error-color)" }}>
          {formError}
        </div>
      )}

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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} onClick={() => openViewModal(row)} ariaLabel="View" />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} onClick={() => handleEdit(row)} ariaLabel="Edit" />
                <IconButton variant="danger-ghost" size="small" icon={<Trash2 size={16} />} onClick={() => handleDelete(row.id)} ariaLabel="Delete" />
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
          title="View Task"
          onClose={closeViewModal}
          showFooter
          size="large"
          bodyLayout="grid"
          viewMode
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          {Object.entries(viewData).map(([k, v]) => {
            if (k === "employee_id") {
              return <Input key={k} label="Employee ID" value={userCode} readOnly disabled />;
            }

            return (
              <Input key={k} label={k.replace(/([A-Z])/g, " $1")} value={v} disabled />
            );
          })}
        </Modal>
      )}

      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editId ? "Edit Task" : "Assign Task"}
          onClose={closeModal}
          showFooter
          size="xlarge"
          bodyLayout="grid"
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModal, disabled: saving },
            {
              label: saving ? "Saving…" : (editId ? "Update" : "Submit"),
              variant: "primary",
              onClick: handleSave,
              disabled: saving,
            },
          ]}
        >
          {formError && (
            <div role="alert" style={{ gridColumn: "1 / -1", color: "var(--error-color)" }}>
              {formError}
            </div>
          )}
          <Select
            label="Employee ID"
            placeholder="Select ID"
            options={Employee.map((emp) => ({ value: emp.id, label: emp.user_code }))}
          />

          {[
            ["First Name", "firstName"],
            ["Last Name", "lastName"],
            ["Schedule Date", "scheduleDate", "date"],
            ["Schedule Time", "scheduleTime", "time"],
            ["Task Type", "taskType"],
            ["Lost & Found", "lostAndFound"],
          ].map(([label, name, type]) => (
            <Input
              key={name}
              label={label}
              type={type || "text"}
              name={name}
              value={formData[name]}
              onChange={handleChange}
            />
          ))}

          <Select
            label="Room Number"
            name="roomNo"
            value={formData.roomNo}
            onChange={handleChange}
            placeholder="Select the Room"
            options={roomNo.map((room) => ({ value: room.id, label: room.room_no }))}
          />

          <Select
            label="Assigned Staff"
            name="assignedStaff"
            value={formData.assignedStaff}
            onChange={handleChange}
            placeholder="Select the Staff"
            options={Employee.map((emp) => ({ value: emp.id, label: emp.username }))}
          />

          <Select
            label="Task Status"
            name="taskStatus"
            value={formData.taskStatus}
            onChange={handleChange}
            options={[
              { value: "Assigned", label: "Assigned" },
              { value: "In Progress", label: "In Progress" },
              { value: "Completed", label: "Completed" },
            ]}
          />

          <Select
            label="Room Status"
            name="roomStatus"
            value={formData.roomStatus}
            onChange={handleChange}
            options={[
              { value: "Blocking", label: "Blocking" },
              { value: "Unblocking", label: "Unblocking" },
            ]}
          />

          <div style={{ gridColumn: "1 / -1" }}>
            <Input
              label="Special Instruction"
              name="specialInstruction"
              value={formData.specialInstruction}
              onChange={handleChange}
            />
          </div>
        </Modal>
      )}
    </>
  );
};

export default TaskAssign;

import React, { useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X, UserPlus } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";
const Employee = () => {
  const [data, setData] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);;
  const [departments, setDepartments] = useState([]);
  const [designations, setDesignations] = useState([]);
  const [roles, setRoles] = useState([]);
  const [shifts, setShifts] = useState([]);


  const initialForm = {
    username: "",
    first_name: "",
    last_name: "",

    personal_email: "",
    company_email: "",
    password: "",
    mobile: "",
    alternative_mobile: "",

    dob: "",
    gender: "",
    marital_status: "",
    address: "",
    city: "",
    state: "",
    postal_code: "",
    country: "",

    department_id: "",
    designation_id: "",
    role_id: "",
    shift_id: "",
    date_of_joining: "",
    experience: "",
    salary_details: "",
    register_code: "",

    emergency_name: "",
    emergency_contact: "",
    emergency_relationship: "",

    acknowledgment_of_hotel_policies: false,

    photo: null,
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
    const { name, value, type, checked } = e.target;
    setFormData((p) => ({
      ...p,
      [name]: type === "checkbox" ? checked : value,
    }));
  };
  const handlePhotoChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      alert("Only JPG and PNG images are allowed!");
      e.target.value = "";
      return;
    }
    setFormData((p) => ({
      ...p,
      photo: file,
    }));
  };

  const getEmployee = async () => {
    const AllRoles = await APICall.getT("/user/users");
    setData(AllRoles.data);
  }
  const getDepartments = async () => {
    const AllDepartments = await APICall.getT("/user/departments");
    setDepartments(AllDepartments.data);
  }
  const getDesignations = async () => {
    const AllDesignations = await APICall.getT("/user/designations");
    setDesignations(AllDesignations.data);
  }
  const getRoles = async () => {
    const AllRoles = await APICall.getT("/user/roles");
    setRoles(AllRoles.data);
  }
  const getShifts = async () => {
    const AllShifts = await APICall.getT("/user/shifts");
    setShifts(AllShifts.data);
  }


  useEffect(() => {
    getEmployee();
    getDepartments();
    getDesignations();
    getRoles();
    getShifts();
  }, [])

  const addEmployee = async () => {
    try {
      const payload = new FormData();

      Object.entries(formData).forEach(([key, value]) => {

        if (key === "acknowledgment_of_hotel_policies") {
          payload.append(key, value ? "true" : "false");
          return;
        }

        if (key === "photo") {
          if (value) payload.append("photo", value);
          return;
        }

        payload.append(key, value ?? "");
      });

      console.log("Sending Payload:", [...payload.entries()]);
      
      await APICall.postT("/user/users", payload);

      alert("Employee Added Successfully");
      getEmployee();
      closeModal();

    } catch (error) {
      console.log("FULL ERROR:", error);

      if (error.response) {
        console.log("STATUS:", error.response.status);
        console.log("DATA:", error.response.data);
        alert("ERROR: " + JSON.stringify(error.response.data));
      } else {
        alert("Server Not Responding");
      }
    }
  };

  const updateEmployee = async () => {
    try {
      await APICall.putT("/user/users", {
        ...formData,
      });
      getEmployee();
    } catch (error) {
      return error, " to update an Employee";
    }
  };
  const deleteEmployee = async (id) => {
    try {
      await APICall.deleteT(`/user/users/${id}`);
      getEmployee();
    } catch (error) {
      return error, " to delete an Employee";
    }
  };



  const handleSave = async () => {
    if (
      !formData.username ||
      !formData.company_email ||
      !formData.password
    )
      return;

    if (editId) {
      await updateEmployee();
    } else {
      await addEmployee();
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      ...initialForm,
      ...row,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    deleteEmployee(id);
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Employee"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Employee",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "username", title: "Name", align: "center" },
          { key: "company_email", title: "Company Mail", align: "center" },
          { key: "mobile", title: "Mobile", align: "center" },
          { key: "gender", title: "Gender", align: "center" },
          { key: "department", title: "Department", align: "center" },
          {
            key: "actions",
            title: "Actions",
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
          <div className="modal-card">
            <div className="modal-header">
              <h3>View Employee</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid view">
              {Object.entries(viewData).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
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
              <h3>{editId ? "Edit Employee" : "Add Employee"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid">
              <div className="form-group">
                <label>Image</label>
                <input
                  type="file"
                  name="photo"
                  onChange={handlePhotoChange}
                />
              </div>
              {[
                ["Username", "username"],
                ["First Name", "first_name"],
                ["Last Name", "last_name"],

                ["Personal Email", "personal_email"],
                ["Company Email", "company_email"],

                ["Password", "password"],
                ["Mobile", "mobile"],
                ["Alternative Mobile", "alternative_mobile"],

                ["DOB", "dob", "date"],
              ]
              .map(([label, name, type]) => (
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
                <label>Gender</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>Marital Status</label>
                <select
                  name="marital_status"
                  value={formData.marital_status}
                  onChange={handleChange}
                >
                  <option value="">Select Marital Status</option>
                  <option value="Single">Single</option>
                  <option value="Married">Married</option>
                  <option value="Divorced">Divorced</option>
                </select>
              </div>
              {[
                ["Address", "address"],
                ["City", "city"],
                ["State", "state"],
                ["Postal Code", "postal_code"],
                ["Country", "country"],
              ]
              .map(([label, name, type]) => (
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

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Department</label>
                <select
                  name="department_id"
                  value={formData.department_id}
                  onChange={handleChange}
                >
                  <option value="">Select a department</option>
                  {departments.map((department) => (
                    <option key={department.id} value={department.id}>
                      {department.department_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Designation</label>
                <select
                  name="designation_id"
                  value={formData.designation_id}
                  onChange={handleChange}
                >
                  <option value="">Select a designation</option>
                  {designations.map((designation) => (
                    <option key={designation.id} value={designation.id}>
                      {designation.designation_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Role</label>
                <select
                  name="role_id"
                  value={formData.role_id}
                  onChange={handleChange}
                >
                  <option value="">Select a role</option>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.role_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Shift</label>
                <select
                  name="shift_id"
                  value={formData.shift_id}
                  onChange={handleChange}
                >
                  <option value="">Select a shift</option>
                  {shifts.map((shift) => (
                    <option key={shift.id} value={shift.id}>
                      {shift.shift_name}
                    </option>
                  ))}
                </select>
              </div>
              {[

                ["Date of Joining", "date_of_joining", "date"],
                ["Experience", "experience"],
                ["Salary Details", "salary_details"],

                ["Register Code", "register_code"],

                ["Emergency Contact Name", "emergency_name"],
                ["Emergency Contact Number", "emergency_contact"],
                ["Emergency Contact Relationship", "emergency_relationship"],
              ]
              .map(([label, name, type]) => (
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

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Acknowledgment of Hotel Policies</label>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <input
                    type="checkbox"
                    name="acknowledgment_of_hotel_policies"
                    checked={formData.acknowledgment_of_hotel_policies}
                    onChange={handleChange}
                  />
                  <span>
                    I acknowledge that I have read, understood, and agree to comply
                    with the hotel's policies
                  </span>
                </div>
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

export default Employee;

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
  const [viewData, setViewData] = useState(null);
  const [roles, setRoles] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [designations, setDesignations] = useState([]);


  const initialForm = {
    photo: "",
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    mobile: "",
    altMobile: "",
    dob: "",
    gender: "",
    city: "",
    state: "",
    postalCode: "",
    country: "",
    role: "",
    department: "",
    designation: "",
    joiningDate: "",
    salary: "",
    experience: "",
    maritalStatus: "",
    notes: "",
    emergencyName: "",
    emergencyContact: "",
    emergencyRelation: "",
    policyAccepted: false,
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

  const getEmployee = async () => {
    const AllRoles = await APICall.getT("/user/users");
    setData(AllRoles.data);
  }

  useEffect(() => {
    getEmployee();
  }, [])


  const handleSave = () => {
    if (!formData.firstName || !formData.email || !formData.mobile) return;

    const payload = {
      id: editId || Date.now(),
      name: `${formData.firstName} ${formData.lastName}`,
      companyMail: formData.email,
      mobile: formData.mobile,
      gender: formData.gender,
      department: formData.department,
      ...formData,
    };

    if (editId) {
      setData((prev) => prev.map((e) => (e.id === editId ? payload : e)));
    } else {
      setData((prev) => [...prev, payload]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    const [firstName, lastName = ""] = row.name.split(" ");
    setEditId(row.id);
    setFormData({
      ...initialForm,
      ...row,
      firstName,
      lastName,
      email: row.companyMail,
    });
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((e) => e.id !== id));
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
                  value={formData.photo}
                  onChange={handleChange}
                />
              </div>
              {[
                ["First Name", "firstName"],
                ["Last Name", "lastName"],
                ["Email Address", "email"],
                ["Login Password", "password"],
                ["Mobile", "mobile"],
                ["Alternative Mobile", "altMobile"],
                ["Date of Birth", "dob", "date"],
                ["Gender", "gender"],
                ["City", "city"],
                ["State", "state"],
                ["Postal Code", "postalCode"],
                ["Country", "country"],
                ["Role", "role"],
                ["Department", "department"],
                ["Designation", "designation"],
                ["Joining Date", "joiningDate", "date"],
                ["Salary Details", "salary"],
                ["Experience", "experience"],
                ["Marital Status", "maritalStatus"],
                ["Emergency Name", "emergencyName"],
                ["Emergency Contact", "emergencyContact"],
                ["Emergency Relationship", "emergencyRelation"],
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

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Notes</label>
                <input
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Acknowledgment of Hotel Policies</label>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <input
                    type="checkbox"
                    name="policyAccepted"
                    checked={formData.policyAccepted}
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

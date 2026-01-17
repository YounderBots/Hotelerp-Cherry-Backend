import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const MenuManagement = () => {
  const [data, setData] = useState([
    {
      id: 1,
      itemCode: "ITM-001",
      image:
        "https://images.unsplash.com/photo-1600891964599-f61ba0e24092",
      itemName: "Chicken Biryani",
      category: "Main Course",
      subCategory: "Non-Veg",
      kitchen: "Main Kitchen",
      prepTime: "25 mins",
      portionSize: "Full",
      price: 320,
      availability: "Available",
      timeSlot: "Lunch / Dinner",
    },
    {
      id: 2,
      itemCode: "ITM-002",
      image:
        "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe",
      itemName: "Veg Salad",
      category: "Starters",
      subCategory: "Veg",
      kitchen: "Cold Kitchen",
      prepTime: "10 mins",
      portionSize: "Regular",
      price: 180,
      availability: "Available",
      timeSlot: "All Day",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    itemCode: "",
    image: "",
    itemName: "",
    category: "",
    subCategory: "",
    kitchen: "",
    prepTime: "",
    portionSize: "",
    price: "",
    availability: "Available",
    timeSlot: "All Day",
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData({
      ...initialForm,
      itemCode: `ITM-${Date.now().toString().slice(-4)}`,
    });
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

  const handleImageChange = (file) => {
    if (!file) return;
    const preview = URL.createObjectURL(file);
    setFormData((p) => ({ ...p, image: preview }));
  };

  const handleSave = () => {
    if (!formData.itemName || !formData.price) return;

    const payload = {
      id: editId || Date.now(),
      ...formData,
    };

    if (editId) {
      setData((prev) =>
        prev.map((i) => (i.id === editId ? payload : i))
      );
    } else {
      setData((prev) => [...prev, payload]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData(row);
    setShowModal(true);
  };

  const handleDelete = (id) => {
    setData((prev) => prev.filter((i) => i.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Menu Management"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          icon: <UserPlus size={18} />,
          label: "Add Item",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "itemCode", title: "Item Code", align: "center" },
          {
            key: "image",
            title: "Item",
            align: "center",
            type: "custom",
            render: (row) => (
              <img
                src={row.image}
                alt="item"
                style={{
                  width: "40px",
                  height: "40px",
                  objectFit: "cover",
                  borderRadius: "6px",
                }}
              />
            ),
          },
          { key: "itemName", title: "Item Name" },
          { key: "category", title: "Category" },
          { key: "subCategory", title: "Sub Category" },
          { key: "kitchen", title: "Kitchen" },
          { key: "prepTime", title: "Prep Time", align: "center" },
          { key: "portionSize", title: "Portion", align: "center" },
          { key: "price", title: "Price", align: "center" },
          {
            key: "availability",
            title: "Availability",
            align: "center",
            type: "badge",
          },
          { key: "timeSlot", title: "Time Slot", align: "center" },
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
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Menu Item</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      {key === "image" ? (
                        <img
                          src={value}
                          alt="item"
                          style={{
                            width: "100%",
                            height: "140px",
                            objectFit: "cover",
                            borderRadius: "8px",
                          }}
                        />
                      ) : (
                        <input value={value} disabled />
                      )}
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
              <h3>{editId ? "Edit Menu Item" : "Add Menu Item"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid">
              {[
                ["Item Code", "itemCode"],
                ["Item Name", "itemName"],
                ["Category", "category"],
                ["Sub Category", "subCategory"],
                ["Kitchen", "kitchen"],
                ["Preparation Time", "prepTime"],
                ["Portion Size", "portionSize"],
                ["Price", "price"],
              ].map(([label, name]) => (
                <div className="form-group" key={name}>
                  <label>{label}</label>
                  <input
                    name={name}
                    value={formData[name]}
                    onChange={handleChange}
                  />
                </div>
              ))}

              <div className="form-group">
                <label>Availability</label>
                <select
                  name="availability"
                  value={formData.availability}
                  onChange={handleChange}
                >
                  <option>Available</option>
                  <option>Unavailable</option>
                </select>
              </div>

              <div className="form-group">
                <label>Time Slot</label>
                <select
                  name="timeSlot"
                  value={formData.timeSlot}
                  onChange={handleChange}
                >
                  <option>All Day</option>
                  <option>Breakfast</option>
                  <option>Lunch</option>
                  <option>Dinner</option>
                </select>
              </div>

              <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                <label>Item Image</label>
                {formData.image && (
                  <img
                    src={formData.image}
                    alt="preview"
                    style={{
                      width: "120px",
                      height: "120px",
                      objectFit: "cover",
                      borderRadius: "8px",
                      marginBottom: "8px",
                    }}
                  />
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageChange(e.target.files[0])}
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

export default MenuManagement;

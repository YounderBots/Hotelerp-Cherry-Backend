import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const Orders = () => {
  const [data, setData] = useState([
    {
      id: 1,
      orderId: "ORD-1001",
      tableId: "T01",
      roomNo: "333",
      guestName: "Anand M",
      guests: 4,
      orderTime: "12:45 PM",
      assignedServer: "Ravi",
      totalAmount: 2450,
      paymentStatus: "Pending",
    },
    {
      id: 2,
      orderId: "ORD-1002",
      tableId: "T03",
      roomNo: "205",
      guestName: "Suresh K",
      guests: 2,
      orderTime: "01:30 PM",
      assignedServer: "Kumar",
      totalAmount: 1380,
      paymentStatus: "Paid",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    orderId: "",
    tableId: "",
    roomNo: "",
    guestName: "",
    guests: "",
    orderDate: "",
    orderTime: "",
    assignedServer: "",
    totalAmount: "",
    paymentStatus: "Pending",
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData({
      ...initialForm,
      orderId: `ORD-${Date.now().toString().slice(-4)}`,
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

  const handleSave = () => {
    if (!formData.orderId || !formData.guestName) return;

    const payload = {
      id: editId || Date.now(),
      ...formData,
    };

    if (editId) {
      setData((prev) =>
        prev.map((item) => (item.id === editId ? payload : item))
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
    setData((prev) => prev.filter((item) => item.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Orders"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Order",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "orderId", title: "Order ID", align: "center" },
          { key: "tableId", title: "Table ID", align: "center" },
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "guestName", title: "Guest Name", align: "center" },
          { key: "guests", title: "Guests", align: "center" },
          { key: "orderTime", title: "Order Time", align: "center" },
          { key: "assignedServer", title: "Server", align: "center" },
          { key: "totalAmount", title: "Total Amount", align: "center" },
          {
            key: "paymentStatus",
            title: "Payment",
            align: "center",
            type: "badge",
          },
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
              <h3>View Order</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>

            <div className="modal-body single view">
              {Object.entries(viewData).map(([key, value]) => (
                <div className="form-group" key={key}>
                  <label>{key.replace(/([A-Z])/g, " $1")}</label>
                  <input value={value} disabled />
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
              <h3>{editId ? "Edit Order" : "Add Order"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid">
              {[
                ["Order ID", "orderId"],
                ["Table ID", "tableId"],
                ["Room No", "roomNo"],
                ["Guest Name", "guestName"],
                ["No. of Guests", "guests"],
                ["Order Date", "orderDate", "date"],
                ["Order Time", "orderTime", "time"],
                ["Assigned Server", "assignedServer"],
                ["Total Amount", "totalAmount"],
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
                <label>Payment Status</label>
                <select
                  name="paymentStatus"
                  value={formData.paymentStatus}
                  onChange={handleChange}
                >
                  <option>Pending</option>
                  <option>Paid</option>
                  <option>Cancelled</option>
                </select>
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

export default Orders;

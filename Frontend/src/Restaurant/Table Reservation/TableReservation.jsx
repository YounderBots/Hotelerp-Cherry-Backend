import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X } from "lucide-react";

const TableReservation = () => {
  const [data, setData] = useState([
    {
      id: 1,
      reservationId: "TR-1001",
      guestName: "Anand M",
      contact: "9876543210",
      date: "2026-01-07",
      timeSlot: "7:00 PM - 9:00 PM",
      floor: "Indoor Floor",
      tableId: "T01",
      roomNo: "",
      guests: 4,
      source: "Walk-in",
    },
    {
      id: 2,
      reservationId: "TR-1002",
      guestName: "Suresh K",
      contact: "9123456789",
      date: "2026-01-08",
      timeSlot: "8:00 PM - 10:00 PM",
      floor: "Outdoor Floor",
      tableId: "T05",
      roomNo: "203",
      guests: 2,
      source: "Hotel Guest",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);

  const initialForm = {
    reservationId: "",
    guestName: "",
    contact: "",
    date: "",
    timeSlot: "",
    floor: "",
    tableId: "",
    roomNo: "",
    guests: "",
    source: "Walk-in",
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData({
      ...initialForm,
      reservationId: `TR-${Date.now().toString().slice(-4)}`,
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
    if (!formData.guestName || !formData.contact || !formData.date) return;

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
        title="Table Reservation"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Reservation",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "reservationId", title: "Reservation ID", align: "center" },
          { key: "guestName", title: "Guest Name", align: "center" },
          { key: "contact", title: "Contact", align: "center" },
          { key: "date", title: "Date", align: "center" },
          { key: "timeSlot", title: "Time Slot", align: "center" },
          { key: "floor", title: "Floor", align: "center" },
          { key: "tableId", title: "Table ID", align: "center" },
          { key: "roomNo", title: "Room No", align: "center" },
          { key: "guests", title: "Guests", align: "center" },
          { key: "source", title: "Source", align: "center" },
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
              <h3>View Reservation</h3>
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
              <h3>{editId ? "Edit Reservation" : "Add Reservation"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body grid">
              {[
                ["Reservation ID", "reservationId"],
                ["Guest Name", "guestName"],
                ["Contact Number", "contact"],
                ["Reservation Date", "date", "date"],
                ["Time Slot", "timeSlot"],
                ["Floor", "floor"],
                ["Table ID", "tableId"],
                ["Room No", "roomNo"],
                ["No. of Guests", "guests"],
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
                <label>Source</label>
                <select name="source" value={formData.source} onChange={handleChange}>
                  <option>Walk-in</option>
                  <option>Phone</option>
                  <option>Online</option>
                  <option>Hotel Guest</option>
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

export default TableReservation;

import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Activity, X } from "lucide-react";
import "../../MasterData/MasterData.css";

const Stock = () => {
  const [activeModal, setActiveModal] = useState(null); // view | adjust | movement
  const [selectedItem, setSelectedItem] = useState(null);

  /* ================= MOCK DATA ================= */
  const stockData = [
    {
      id: 1,
      itemCode: "ING045",
      itemName: "Tomato",
      category: "Vegetable",
      store: "Kitchen Store",
      unit: "Kg",
      availableQty: 18.5,
      minStock: 10,
      status: "In Stock",
      updatedAt: "10-Jan-2025 18:40",
      movements: [
        {
          date: "10-Jan-2025 10:15",
          type: "In",
          qty: 20,
          source: "Main Store",
          ref: "PO-223",
          by: "Admin",
        },
        {
          date: "10-Jan-2025 17:40",
          type: "Out",
          qty: 1.5,
          source: "Kitchen Usage",
          ref: "KOT-118",
          by: "System",
        },
      ],
    },
    {
      id: 2,
      itemCode: "BEV012",
      itemName: "Whiskey",
      category: "Beverage",
      store: "Bar Store",
      unit: "Ltr",
      availableQty: 2,
      minStock: 5,
      status: "Low Stock",
      updatedAt: "10-Jan-2025 17:20",
      movements: [],
    },
  ];

  /* ================= MODAL HANDLERS ================= */
  const openModal = (type, row) => {
    setSelectedItem(row);
    setActiveModal(type);
  };

  const closeModal = () => {
    setSelectedItem(null);
    setActiveModal(null);
  };

  return (
    <>
      {/* ================= PAGE HEADER ================= */}
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ marginBottom: 4 }}>Stock Management</h3>
        <div style={{ fontSize: 13, color: "#64748b" }}>
          Restaurant → Inventory → Stock
        </div>
      </div>

      {/* ================= STOCK TABLE ================= */}
      <TableTemplate
        title="Stock List"
        searchable
        pagination
        columns={[
          { key: "itemCode", title: "Item Code" },
          { key: "itemName", title: "Item Name" },
          { key: "category", title: "Category" },
          { key: "store", title: "Store" },
          { key: "unit", title: "Unit", align: "center" },
          { key: "availableQty", title: "Available Qty", align: "center" },
          { key: "minStock", title: "Minimum Stock", align: "center" },
          {
            key: "status",
            title: "Stock Status",
            align: "center",
            type: "badge",
          },
          { key: "updatedAt", title: "Last Updated" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: "8px",
                  flexWrap: "nowrap",
                }}
              >
                <button
                  className="table-action-btn view"
                  title="View"
                  onClick={() => openModal("view", row)}
                >
                  <Eye size={16} />
                </button>

                <button
                  className="table-action-btn edit"
                  title="Adjust"
                  onClick={() => openModal("adjust", row)}
                >
                  <Pencil size={16} />
                </button>

                <button
                  className="table-action-btn delete"
                  title="Movements"
                  onClick={() => openModal("movement", row)}
                >
                  <Activity size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={stockData}
      />

      {/* ================= VIEW MODAL ================= */}
      {activeModal === "view" && selectedItem && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 500 }}>
            <div className="modal-header">
              <h3>Stock Details – {selectedItem.itemName}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <p><strong>Store:</strong> {selectedItem.store}</p>
              <p>
                <strong>Available Qty:</strong>{" "}
                {selectedItem.availableQty} {selectedItem.unit}
              </p>
              <p><strong>Minimum Stock:</strong> {selectedItem.minStock}</p>
              <p><strong>Last Updated:</strong> {selectedItem.updatedAt}</p>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= ADJUST MODAL ================= */}
      {activeModal === "adjust" && selectedItem && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 520 }}>
            <div className="modal-header">
              <h3>Adjust Stock – {selectedItem.itemName}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Adjustment Type</label>
                <select>
                  <option>Add</option>
                  <option>Reduce</option>
                </select>
              </div>

              <div className="form-group">
                <label>Quantity</label>
                <input type="number" />
              </div>

              <div className="form-group">
                <label>Reason</label>
                <select>
                  <option>Purchase</option>
                  <option>Wastage</option>
                  <option>Damage</option>
                  <option>Correction</option>
                </select>
              </div>

              <div className="form-group">
                <label>Reference No</label>
                <input type="text" />
              </div>

              <div className="form-group">
                <label>Remarks</label>
                <textarea rows="2" />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Cancel
              </button>
              <button className="btn primary">
                Save Adjustment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= MOVEMENT MODAL ================= */}
      {activeModal === "movement" && selectedItem && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: 900 }}>
            <div className="modal-header">
              <h3>Stock Movements – {selectedItem.itemName}</h3>
              <button onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Type</th>
                    <th>Qty</th>
                    <th>Source / Destination</th>
                    <th>Reference</th>
                    <th>Performed By</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedItem.movements.length === 0 ? (
                    <tr>
                      <td colSpan="6" style={{ textAlign: "center" }}>
                        No movements found
                      </td>
                    </tr>
                  ) : (
                    selectedItem.movements.map((m, i) => (
                      <tr key={i}>
                        <td>{m.date}</td>
                        <td>{m.type}</td>
                        <td>{m.qty}</td>
                        <td>{m.source}</td>
                        <td>{m.ref}</td>
                        <td>{m.by}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Stock;

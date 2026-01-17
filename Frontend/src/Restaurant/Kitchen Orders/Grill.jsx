import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, X } from "lucide-react";

const Grill = () => {
  const [showItemsModal, setShowItemsModal] = useState(false);
  const [selectedKOT, setSelectedKOT] = useState(null);

  const grillKOTData = [
    {
      id: 1,
      kotNo: "GKOT144",
      orderId: "ORD988",
      tableId: "T06",
      itemCount: "3 Items",
      orderTime: "19:34",
      summary: "2 Preparing / 1 Pending",
      priority: "Normal",
      status: "Preparing",
      items: [
        {
          name: "Grilled Chicken",
          qty: 1,
          notes: "Extra char, less oil",
          status: "Preparing",
        },
        {
          name: "Paneer Tikka",
          qty: 2,
          notes: "No onion",
          status: "Pending",
        },
      ],
    },
    {
      id: 2,
      kotNo: "GKOT145",
      orderId: "ORD991",
      tableId: "T09",
      itemCount: "2 Items",
      orderTime: "19:40",
      summary: "2 Pending",
      priority: "High",
      status: "New",
      items: [
        {
          name: "Chicken Tikka",
          qty: 2,
          notes: "Spicy",
          status: "Pending",
        },
      ],
    },
  ];

  const openItemsModal = (row) => {
    setSelectedKOT(row);
    setShowItemsModal(true);
  };

  const closeItemsModal = () => {
    setSelectedKOT(null);
    setShowItemsModal(false);
  };

  return (
    <>
      {/* ================= GRILL KOT TABLE ================= */}
      <TableTemplate
        title="Grill Kitchen – Active KOTs"
        searchable
        pagination
        columns={[
          { key: "kotNo", title: "KOT No", align: "center" },
          { key: "orderId", title: "Order ID", align: "center" },
          { key: "tableId", title: "Table ID", align: "center" },
          { key: "itemCount", title: "Item Count", align: "center" },
          { key: "orderTime", title: "Order Time", align: "center" },
          { key: "summary", title: "Item Status Summary" },
          {
            key: "priority",
            title: "Priority",
            align: "center",
            type: "badge",
          },
          {
            key: "status",
            title: "KOT Status",
            align: "center",
            type: "badge",
          },
          {
            key: "action",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <button
                className="table-action-btn view"
                onClick={() => openItemsModal(row)}
                title="View Items"
              >
                <Eye size={16} />
              </button>
            ),
          },
        ]}
        data={grillKOTData}
      />

      {/* ================= VIEW GRILL ITEMS MODAL ================= */}
      {showItemsModal && selectedKOT && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>Grill Items – {selectedKOT.kotNo}</h3>
              <button onClick={closeItemsModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <table className="table table-hover align-middle">
                <thead>
                  <tr>
                    <th>Item Name</th>
                    <th>Qty</th>
                    <th>Grill Instructions / Notes</th>
                    <th>Status</th>
                    <th style={{ textAlign: "center" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedKOT.items.map((item, index) => (
                    <tr key={index}>
                      <td>{item.name}</td>
                      <td>{item.qty}</td>
                      <td>{item.notes}</td>
                      <td>
                        <span className="badge">{item.status}</span>
                      </td>
                      <td style={{ textAlign: "center" }}>
                        <button className="btn primary btn-sm">
                          Mark Ready
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeItemsModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Grill;

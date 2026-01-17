import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, X } from "lucide-react";

const MainKitchen = () => {
  const [showItemsModal, setShowItemsModal] = useState(false);
  const [selectedKOT, setSelectedKOT] = useState(null);

  const kotData = [
    {
      id: 1,
      kotNo: "MKOT118",
      orderId: "ORD901",
      tableId: "T11",
      itemCount: "5 Items",
      orderTime: "19:18",
      summary: "3 Preparing / 2 Pending",
      priority: "High",
      status: "Preparing",
      items: [
        {
          name: "Paneer Butter Masala",
          qty: 2,
          notes: "Less spicy",
          status: "Preparing",
        },
        {
          name: "Butter Naan",
          qty: 3,
          notes: "-",
          status: "Pending",
        },
      ],
    },
    {
      id: 2,
      kotNo: "MKOT119",
      orderId: "ORD902",
      tableId: "T04",
      itemCount: "3 Items",
      orderTime: "19:25",
      summary: "1 Preparing / 2 Pending",
      priority: "Normal",
      status: "New",
      items: [
        {
          name: "Veg Fried Rice",
          qty: 1,
          notes: "-",
          status: "Pending",
        },
        {
          name: "Gobi Manchurian",
          qty: 2,
          notes: "Extra crispy",
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
      {/* ================= KOT TABLE ================= */}
      <TableTemplate
        title="Active KOTs"
        searchable
        pagination
        columns={[
          { key: "kotNo", title: "KOT No", align: "center" },
          { key: "orderId", title: "Order ID", align: "center" },
          { key: "tableId", title: "Table ID", align: "center" },
          { key: "itemCount", title: "Items", align: "center" },
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
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <button
                className="table-action-btn view"
                onClick={() => openItemsModal(row)}
              >
                <Eye size={16} />
              </button>
            ),
          },
        ]}
        data={kotData}
      />

      {/* ================= VIEW ITEMS MODAL ================= */}
      {showItemsModal && selectedKOT && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>KOT Items – {selectedKOT.kotNo}</h3>
              <button onClick={closeItemsModal}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body single">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Item Name</th>
                    <th>Qty</th>
                    <th>Modifiers / Notes</th>
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
                        <button className="btn primary">
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

export default MainKitchen;

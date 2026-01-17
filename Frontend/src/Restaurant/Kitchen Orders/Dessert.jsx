import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, X } from "lucide-react";

const Dessert = () => {
  const [showItemsModal, setShowItemsModal] = useState(false);
  const [selectedKOT, setSelectedKOT] = useState(null);

  const dessertKOTData = [
    {
      id: 1,
      kotNo: "DKOT318",
      orderId: "ORD1164",
      tableId: "T03",
      itemCount: "2 Items",
      orderTime: "19:52",
      summary: "1 Preparing / 1 Pending",
      priority: "Normal",
      status: "Preparing",
      items: [
        {
          name: "Chocolate Lava Cake",
          qty: 1,
          notes: "Extra molten",
          status: "Preparing",
        },
        {
          name: "Vanilla Ice Cream",
          qty: 1,
          notes: "No nuts",
          status: "Pending",
        },
      ],
    },
    {
      id: 2,
      kotNo: "DKOT319",
      orderId: "ORD1167",
      tableId: "T08",
      itemCount: "3 Items",
      orderTime: "19:58",
      summary: "3 Pending",
      priority: "High",
      status: "New",
      items: [
        {
          name: "Brownie with Ice Cream",
          qty: 2,
          notes: "-",
          status: "Pending",
        },
        {
          name: "Fruit Salad",
          qty: 1,
          notes: "No sugar",
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
      {/* ================= DESSERT KOT TABLE ================= */}
      <TableTemplate
        title="Dessert Kitchen – Active KOTs"
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
        data={dessertKOTData}
      />

      {/* ================= VIEW DESSERT ITEMS MODAL ================= */}
      {showItemsModal && selectedKOT && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>Dessert Items – {selectedKOT.kotNo}</h3>
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
                    <th>Dessert Instructions / Notes</th>
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

export default Dessert;

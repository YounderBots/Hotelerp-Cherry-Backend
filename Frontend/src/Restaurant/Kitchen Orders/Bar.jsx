import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, X } from "lucide-react";

const Bar = () => {
  const [showItemsModal, setShowItemsModal] = useState(false);
  const [selectedKOT, setSelectedKOT] = useState(null);

  const barKOTData = [
    {
      id: 1,
      kotNo: "BKOT209",
      orderId: "ORD1042",
      tableId: "T19",
      itemCount: "4 Items",
      orderTime: "19:46",
      summary: "3 Preparing / 1 Pending",
      priority: "High",
      status: "Preparing",
      items: [
        {
          name: "Mojito",
          qty: 2,
          notes: "Less ice, mint extra",
          status: "Preparing",
        },
        {
          name: "Whiskey Sour",
          qty: 2,
          notes: "Large glass, no sugar",
          status: "Pending",
        },
      ],
    },
    {
      id: 2,
      kotNo: "BKOT210",
      orderId: "ORD1045",
      tableId: "T07",
      itemCount: "2 Items",
      orderTime: "19:52",
      summary: "2 Pending",
      priority: "Normal",
      status: "New",
      items: [
        {
          name: "Beer",
          qty: 2,
          notes: "Chilled",
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
      {/* ================= BAR KOT TABLE ================= */}
      <TableTemplate
        title="Bar Kitchen – Active KOTs"
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
        data={barKOTData}
      />

      {/* ================= VIEW BAR ITEMS MODAL ================= */}
      {showItemsModal && selectedKOT && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>Bar Items – {selectedKOT.kotNo}</h3>
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
                    <th>Drink Modifiers</th>
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

export default Bar;

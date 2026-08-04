import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const itemSummary = (items) => {
  if (!items || items.length === 0) return "No items";
  const counts = items.reduce((acc, it) => {
    acc[it.preparation_status] = (acc[it.preparation_status] || 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts).map(([status, count]) => `${count} ${status}`).join(" / ");
};

const KitchenDisplay = ({ title, kitchenType }) => {
  const [kots, setKots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showItemsModal, setShowItemsModal] = useState(false);
  const [selectedKOT, setSelectedKOT] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/restaurant/kitchen"), APICall.getT("/restaurant/kot")]).then(([kRes, tRes]) => {
      const kitchens = kRes.status === "fulfilled" ? readList(kRes.value) : [];
      const kitchenIds = new Set(kitchens.filter((k) => k.kitchen_type === kitchenType).map((k) => k.id));
      const allKots = tRes.status === "fulfilled" ? readList(tRes.value) : [];
      setKots(allKots.filter((k) => kitchenIds.has(k.kitchen_id)));
      if (tRes.status === "rejected") setError(errMsg(tRes.reason, "Failed to load KOTs."));
      setLoading(false);
    });
  }, [kitchenType]);

  useEffect(() => {
    load();
  }, [load]);

  const openItemsModal = async (row) => {
    try {
      const res = await APICall.getT(`/restaurant/kot/${row.id}`);
      setSelectedKOT(res?.data || row);
      setShowItemsModal(true);
    } catch (err) {
      setError(errMsg(err, "Failed to load KOT items."));
    }
  };
  const closeItemsModal = () => {
    setSelectedKOT(null);
    setShowItemsModal(false);
    load();
  };

  const acknowledgeKot = async (row) => {
    try {
      await APICall.putT(`/restaurant/kot/${row.id}/acknowledge`, {});
      const res = await APICall.getT(`/restaurant/kot/${row.id}`);
      setSelectedKOT(res?.data);
    } catch (err) {
      setError(errMsg(err, "Failed to acknowledge KOT."));
    }
  };

  const markItemReady = async (kotItemId) => {
    try {
      await APICall.putT(`/restaurant/kot/item/${kotItemId}/status`, { preparation_status: "Ready" });
      const res = await APICall.getT(`/restaurant/kot/${selectedKOT.id}`);
      setSelectedKOT(res?.data);
    } catch (err) {
      setError(errMsg(err, "Failed to mark item ready."));
    }
  };

  const markAllReady = async () => {
    try {
      await APICall.putT(`/restaurant/kot/${selectedKOT.id}/status`, { kot_status: "Completed" });
      closeItemsModal();
    } catch (err) {
      setError(errMsg(err, "Failed to mark KOT ready."));
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title={title}
        searchable
        pagination
        loading={loading}
        columns={[
          { key: "kot_number", title: "KOT No", align: "center" },
          { key: "order_id", title: "Order ID", align: "center" },
          { key: "table_code", title: "Table/Room", align: "center", type: "custom", render: (row) => row.table_code || row.room_no || "-" },
          { key: "items", title: "Items", align: "center", type: "custom", render: (row) => `${(row.items || []).length} item(s)` },
          { key: "created_at", title: "Order Time", align: "center", type: "custom", render: (row) => (row.created_at ? new Date(row.created_at).toLocaleTimeString() : "-") },
          { key: "summary", title: "Item Status Summary", type: "custom", render: (row) => itemSummary(row.items) },
          { key: "priority", title: "Priority", align: "center", type: "badge" },
          { key: "kot_status", title: "KOT Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openItemsModal(row)} />,
          },
        ]}
        data={kots}
      />

      {showItemsModal && selectedKOT && (
        <Modal
          isOpen
          title={`KOT Items – ${selectedKOT.kot_number}`}
          onClose={closeItemsModal}
          size="xlarge"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeItemsModal },
            ...(selectedKOT.kot_status !== "Completed" ? [{ label: "Mark Whole KOT Ready", variant: "primary", onClick: markAllReady }] : []),
          ]}
        >
          {selectedKOT.kot_status === "New" && (
            <Button variant="secondary" style={{ marginBottom: "12px" }} onClick={() => acknowledgeKot(selectedKOT)}>
              Acknowledge KOT
            </Button>
          )}
          <table className="table table-hover">
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Qty</th>
                <th>Status</th>
                <th style={{ textAlign: "center" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {(selectedKOT.items || []).map((item) => (
                <tr key={item.kot_item_id}>
                  <td>
                    {item.item_name}
                    {item.variant_name ? ` — ${item.variant_name}` : ""}
                    {item.special_instructions && (
                      <div style={{ fontSize: "12px", color: "#64748b" }}>{item.special_instructions}</div>
                    )}
                  </td>
                  <td>{item.quantity}</td>
                  <td><span className="badge">{item.preparation_status}</span></td>
                  <td style={{ textAlign: "center" }}>
                    {item.preparation_status !== "Ready" && (
                      <Button variant="primary" onClick={() => markItemReady(item.kot_item_id)}>
                        Mark Ready
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
              {(!selectedKOT.items || selectedKOT.items.length === 0) && (
                <tr><td colSpan={4} style={{ textAlign: "center", color: "#9ca3af" }}>No items</td></tr>
              )}
            </tbody>
          </table>
        </Modal>
      )}
    </>
  );
};

export default KitchenDisplay;

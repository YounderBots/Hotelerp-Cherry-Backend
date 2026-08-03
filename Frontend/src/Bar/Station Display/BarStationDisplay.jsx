import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Select from "../../stories/Form/Select";
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

// Bar has only a handful of stations (unlike Restaurant's fixed Main/Grill/Dessert
// kitchens), so one generic page with a station selector replaces per-station wrapper files.
const BarStationDisplay = () => {
  const [stations, setStations] = useState([]);
  const [stationId, setStationId] = useState("");
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showItemsModal, setShowItemsModal] = useState(false);
  const [selectedBOT, setSelectedBOT] = useState(null);

  useEffect(() => {
    APICall.getT("/bar/station")
      .then((res) => {
        const list = readList(res);
        setStations(list);
        if (list.length > 0) setStationId(String(list[0].id));
      })
      .catch((err) => setError(errMsg(err, "Failed to load stations.")));
  }, []);

  const load = useCallback(() => {
    if (!stationId) {
      setBots([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    APICall.getT("/bar/bot", { station_id: stationId })
      .then((res) => setBots(readList(res)))
      .catch((err) => setError(errMsg(err, "Failed to load BOTs.")))
      .finally(() => setLoading(false));
  }, [stationId]);

  useEffect(() => {
    load();
  }, [load]);

  const openItemsModal = async (row) => {
    try {
      const res = await APICall.getT(`/bar/bot/${row.id}`);
      setSelectedBOT(res?.data || row);
      setShowItemsModal(true);
    } catch (err) {
      setError(errMsg(err, "Failed to load BOT items."));
    }
  };
  const closeItemsModal = () => {
    setSelectedBOT(null);
    setShowItemsModal(false);
    load();
  };

  const acknowledgeBot = async (row) => {
    try {
      await APICall.putT(`/bar/bot/${row.id}/acknowledge`, {});
      const res = await APICall.getT(`/bar/bot/${row.id}`);
      setSelectedBOT(res?.data);
    } catch (err) {
      setError(errMsg(err, "Failed to acknowledge BOT."));
    }
  };

  const markItemReady = async (botItemId) => {
    try {
      await APICall.putT(`/bar/bot/item/${botItemId}/status`, { preparation_status: "Ready" });
      const res = await APICall.getT(`/bar/bot/${selectedBOT.id}`);
      setSelectedBOT(res?.data);
    } catch (err) {
      setError(errMsg(err, "Failed to mark item ready."));
    }
  };

  const markAllReady = async () => {
    try {
      await APICall.putT(`/bar/bot/${selectedBOT.id}/status`, { bot_status: "Completed" });
      closeItemsModal();
    } catch (err) {
      setError(errMsg(err, "Failed to mark BOT ready."));
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <div style={{ maxWidth: "260px", marginBottom: "16px" }}>
        <Select
          label="Station"
          value={stationId}
          onChange={(e) => setStationId(e.target.value)}
          options={stations.map((s) => ({ value: s.id, label: s.station_name }))}
          placeholder="— select —"
        />
      </div>

      <TableTemplate
        title="Bar Station Display"
        searchable
        pagination
        loading={loading}
        columns={[
          { key: "bot_number", title: "BOT No", align: "center" },
          { key: "order_id", title: "Order ID", align: "center" },
          { key: "table_code", title: "Table", align: "center", type: "custom", render: (row) => row.table_code || "-" },
          { key: "items", title: "Items", align: "center", type: "custom", render: (row) => `${(row.items || []).length} item(s)` },
          { key: "created_at", title: "Order Time", align: "center", type: "custom", render: (row) => (row.created_at ? new Date(row.created_at).toLocaleTimeString() : "-") },
          { key: "summary", title: "Item Status Summary", type: "custom", render: (row) => itemSummary(row.items) },
          { key: "bot_status", title: "BOT Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openItemsModal(row)} />
            ),
          },
        ]}
        data={bots}
      />

      {showItemsModal && selectedBOT && (
        <Modal
          isOpen
          title={`BOT Items – ${selectedBOT.bot_number}`}
          onClose={closeItemsModal}
          size="xlarge"
          bodyLayout="single"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeItemsModal },
            ...(selectedBOT.bot_status !== "Completed" ? [{ label: "Mark Whole BOT Ready", variant: "primary", onClick: markAllReady }] : []),
          ]}
        >
          {selectedBOT.bot_status === "New" && (
            <Button variant="secondary" style={{ marginBottom: "12px" }} onClick={() => acknowledgeBot(selectedBOT)}>
              Acknowledge BOT
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
              {(selectedBOT.items || []).map((item) => (
                <tr key={item.bot_item_id}>
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
                      <Button variant="primary" size="small" onClick={() => markItemReady(item.bot_item_id)}>
                        Mark Ready
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
              {(!selectedBOT.items || selectedBOT.items.length === 0) && (
                <tr><td colSpan={4} style={{ textAlign: "center", color: "#9ca3af" }}>No items</td></tr>
              )}
            </tbody>
          </table>
        </Modal>
      )}
    </>
  );
};

export default BarStationDisplay;

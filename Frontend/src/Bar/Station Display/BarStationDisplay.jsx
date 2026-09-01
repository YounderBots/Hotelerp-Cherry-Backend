import React, { useState } from "react";
import { RefreshCw } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import Select from "../../stories/Form/Select";
import Switch from "../../stories/Form/Switch";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatDateTime } from "../../functions/formatters";
import { useApiResource } from "../../hooks/useApiResource";
import { usePolling } from "../../hooks/usePolling";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import "../../stories/OrderDetail.css";
import "../../Restaurant/Kitchen Orders/KitchenDisplay.css";

/**
 * One bar station's live ticket list.
 *
 * The bar has a handful of configurable stations rather than the restaurant's
 * fixed Main/Grill/Dessert kitchens, so one page with a station selector
 * replaces per-station wrapper files.
 *
 * Like the kitchen screens, this is a wall display: it refreshes itself rather
 * than waiting for somebody to reload it.
 */
const REFRESH_MS = 30000;

const itemSummary = (items) => {
  if (!items || items.length === 0) return "No items";
  const counts = items.reduce((acc, it) => {
    acc[it.preparation_status] = (acc[it.preparation_status] || 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts)
    .map(([status, count]) => `${count} ${status}`)
    .join(" / ");
};

const BarStationDisplay = () => {
  const perms = usePagePermissions("/bar_station");
  const { toast, showToast } = useToast();

  const [pickedStationId, setPickedStationId] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedBOT, setSelectedBOT] = useState(null);
  const [busy, setBusy] = useState(false);

  const { data: stations, error: stationsError } = useApiResource(
    () => APICall.getT("/bar/station"),
    { select: readList, fallback: "Failed to load stations." },
  );

  // The first station, until the user picks another. Derived rather than
  // written from an effect: the page used to load the station list and then
  // setState the default inside a .then, which cost an extra render and left
  // the first paint with no station selected and an empty table under it.
  const stationId = pickedStationId || (stations[0] ? String(stations[0].id) : "");

  const {
    data: bots,
    loading,
    error,
    reload,
  } = useApiResource(() => APICall.getT("/bar/bot", { station_id: stationId }), {
    select: readList,
    fallback: "Failed to load BOTs.",
    enabled: !!stationId,
    deps: [stationId],
  });

  usePolling(reload, autoRefresh && stationId ? REFRESH_MS : null);

  /* ================= HANDLERS ================= */

  const openItemsModal = async (row) => {
    try {
      const res = await APICall.getT(`/bar/bot/${row.id}`);
      setSelectedBOT(res?.data || row);
    } catch (err) {
      showToast(errMsg(err, "Failed to load BOT items."), "error");
    }
  };

  const closeItemsModal = () => {
    setSelectedBOT(null);
    reload();
  };

  const refreshBot = async (id) => {
    const res = await APICall.getT(`/bar/bot/${id}`);
    setSelectedBOT(res?.data);
  };

  const acknowledgeBot = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await APICall.putT(`/bar/bot/${selectedBOT.id}/acknowledge`, {});
      showToast("BOT acknowledged", "update");
      await refreshBot(selectedBOT.id);
    } catch (err) {
      showToast(errMsg(err, "Failed to acknowledge BOT."), "error");
    } finally {
      setBusy(false);
    }
  };

  const markItemReady = async (botItemId) => {
    if (busy) return;
    setBusy(true);
    try {
      await APICall.putT(`/bar/bot/item/${botItemId}/status`, {
        preparation_status: "Ready",
      });
      showToast("Item marked ready", "update");
      await refreshBot(selectedBOT.id);
    } catch (err) {
      showToast(errMsg(err, "Failed to mark item ready."), "error");
    } finally {
      setBusy(false);
    }
  };

  const markAllReady = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await APICall.putT(`/bar/bot/${selectedBOT.id}/status`, { bot_status: "Completed" });
      showToast("BOT completed", "success");
      closeItemsModal();
    } catch (err) {
      showToast(errMsg(err, "Failed to mark BOT ready."), "error");
    } finally {
      setBusy(false);
    }
  };

  /* ================= UI ================= */

  const items = selectedBOT?.items || [];

  return (
    <>
      <ErrorAlert message={stationsError || error} />

      <TableTemplate
        title="Bar Station Display"
        loading={loading}
        emptyMessage={
          stations.length === 0
            ? "No bar stations are configured yet."
            : "No open tickets for this station."
        }
        searchable
        pagination
        exportable
        filters={
          <div className="kds-controls">
            {/* Was a bare <div style={{maxWidth:260}}> above the table, outside
                the toolbar, so it did not line up with anything. */}
            <Select
              label="Station"
              value={stationId}
              onChange={(e) => setPickedStationId(e.target.value)}
              options={stations.map((s) => ({ value: s.id, label: s.station_name }))}
              placeholder="— select —"
            />
            <Switch
              label={`Auto-refresh (${REFRESH_MS / 1000}s)`}
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <Button variant="secondary" size="small" onClick={reload}>
              <RefreshCw size={14} aria-hidden="true" /> Refresh
            </Button>
          </div>
        }
        columns={[
          { key: "bot_number", title: "BOT No", align: "left" },
          // order_number is resolved by the API. This column was headed
          // "Order ID" and printed the raw bar_order.id.
          { key: "order_number", title: "Order No", align: "left" },
          { key: "table_code", title: "Table", align: "left" },
          {
            key: "items",
            title: "Items",
            align: "right",
            type: "custom",
            render: (row) => (row.items || []).length,
            exportValue: (row) => String((row.items || []).length),
          },
          {
            key: "created_at",
            title: "Order Time",
            align: "left",
            type: "custom",
            render: (row) => formatDateTime(row.created_at),
            exportValue: (row) => formatDateTime(row.created_at),
          },
          {
            key: "summary",
            title: "Item Status",
            align: "left",
            type: "custom",
            render: (row) => itemSummary(row.items),
            exportValue: (row) => itemSummary(row.items),
          },
          {
            key: "priority",
            title: "Priority",
            align: "center",
            type: "badge",
            badgeType: "priority",
          },
          { key: "bot_status", title: "BOT Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`BOT ${row.bot_number || ""}`.trim()}
                onView={() => openItemsModal(row)}
              />
            ),
          },
        ]}
        data={bots}
      />

      {/* ================= BOT ITEMS ================= */}
      <Modal
        isOpen={!!selectedBOT}
        title={`BOT ${selectedBOT?.bot_number || ""}`}
        onClose={closeItemsModal}
        size="xlarge"
        bodyLayout="custom"
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: closeItemsModal },
          ...(selectedBOT?.bot_status === "New" && perms.edit
            ? [
                {
                  label: "Acknowledge",
                  variant: "secondary",
                  onClick: acknowledgeBot,
                  disabled: busy,
                },
              ]
            : []),
          ...(selectedBOT?.bot_status !== "Completed" && perms.edit
            ? [
                {
                  label: "Mark Whole BOT Ready",
                  variant: "primary",
                  onClick: markAllReady,
                  disabled: busy,
                },
              ]
            : []),
        ]}
      >
        <div className="order-detail__summary">
          <span>
            <b>Table</b>
            {selectedBOT?.table_code || "—"}
          </span>
          <span>
            <b>Priority</b>
            {selectedBOT?.priority || "—"}
          </span>
          <span>
            <b>Status</b>
            {selectedBOT?.bot_status || "—"}
          </span>
          <span>
            <b>Placed</b>
            {formatDateTime(selectedBOT?.created_at)}
          </span>
        </div>

        <TableTemplate
          searchable={false}
          pagination={false}
          exportable={false}
          emptyMessage="No items on this ticket."
          columns={[
            {
              key: "item_name",
              title: "Item",
              align: "left",
              type: "custom",
              render: (item) => (
                <>
                  {item.item_name || "Unnamed item"}
                  {item.variant_name ? ` — ${item.variant_name}` : ""}
                  {(item.modifiers || []).length > 0 && (
                    <span className="order-item__note">{item.modifiers.join(", ")}</span>
                  )}
                  {item.special_instructions && (
                    <span className="order-item__note">{item.special_instructions}</span>
                  )}
                </>
              ),
            },
            { key: "quantity", title: "Qty", align: "right" },
            {
              key: "preparation_status",
              title: "Status",
              align: "center",
              type: "badge",
            },
            {
              key: "actions",
              title: "",
              align: "center",
              type: "custom",
              excludeFromExport: true,
              render: (item) =>
                item.preparation_status !== "Ready" &&
                item.preparation_status !== "Cancelled" &&
                perms.edit ? (
                  <Button
                    variant="primary"
                    size="small"
                    onClick={() => markItemReady(item.bot_item_id)}
                    disabled={busy}
                  >
                    Mark Ready
                  </Button>
                ) : null,
            },
          ]}
          data={items}
        />
      </Modal>

      <Toast {...toast} />
    </>
  );
};

export default BarStationDisplay;

import React, { useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import Button from "../../stories/Button";
import Switch from "../../stories/Form/Switch";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatDateTime } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import { usePolling } from "../../hooks/usePolling";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import "../../stories/OrderDetail.css";
import "./KitchenDisplay.css";

/**
 * One kitchen station's live ticket list — Main, Grill or Dessert.
 *
 * WHY IT REFRESHES ITSELF
 * This is a wall screen in a kitchen: nobody is standing at it clicking
 * reload. It used to load once on mount and never again, so a ticket sent from
 * the floor only appeared if a chef happened to navigate away and back. The
 * poll is visible and switchable rather than hidden, so a station that would
 * rather not have the list move under its hands can stop it.
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

const KitchenDisplay = ({ title, kitchenType }) => {
  const perms = usePagePermissions(
    { Main: "/kot/main_kitchen", Grill: "/kot/grill", Dessert: "/kot/dessert" }[kitchenType] ||
      "/kot/main_kitchen",
  );

  const {
    data: [kitchens, allKots],
    loading,
    error,
    reload,
  } = useApiResources([
    { fetch: () => APICall.getT("/restaurant/kitchen"), select: readList },
    {
      fetch: () => APICall.getT("/restaurant/kot"),
      select: readList,
      fallback: "Failed to load KOTs.",
    },
  ]);

  const { toast, showToast } = useToast();

  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedKOT, setSelectedKOT] = useState(null);
  const [busy, setBusy] = useState(false);

  usePolling(reload, autoRefresh ? REFRESH_MS : null);

  // Only this station's tickets. Derived rather than stored, so a reload
  // cannot leave the list showing another station's work.
  const kots = useMemo(() => {
    const ids = new Set(
      kitchens.filter((k) => k.kitchen_type === kitchenType).map((k) => k.id),
    );
    return allKots.filter((k) => ids.has(k.kitchen_id));
  }, [kitchens, allKots, kitchenType]);

  /* ================= HANDLERS ================= */

  const openItemsModal = async (row) => {
    try {
      const res = await APICall.getT(`/restaurant/kot/${row.id}`);
      setSelectedKOT(res?.data || row);
    } catch (err) {
      showToast(errMsg(err, "Failed to load KOT items."), "error");
    }
  };

  const closeItemsModal = () => {
    setSelectedKOT(null);
    reload();
  };

  const refreshKot = async (id) => {
    const res = await APICall.getT(`/restaurant/kot/${id}`);
    setSelectedKOT(res?.data);
  };

  const acknowledgeKot = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await APICall.putT(`/restaurant/kot/${selectedKOT.id}/acknowledge`, {});
      showToast("KOT acknowledged", "update");
      await refreshKot(selectedKOT.id);
    } catch (err) {
      showToast(errMsg(err, "Failed to acknowledge KOT."), "error");
    } finally {
      setBusy(false);
    }
  };

  const markItemReady = async (kotItemId) => {
    if (busy) return;
    setBusy(true);
    try {
      await APICall.putT(`/restaurant/kot/item/${kotItemId}/status`, {
        preparation_status: "Ready",
      });
      showToast("Item marked ready", "update");
      await refreshKot(selectedKOT.id);
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
      await APICall.putT(`/restaurant/kot/${selectedKOT.id}/status`, {
        kot_status: "Completed",
      });
      showToast("KOT completed", "success");
      closeItemsModal();
    } catch (err) {
      showToast(errMsg(err, "Failed to mark KOT ready."), "error");
    } finally {
      setBusy(false);
    }
  };

  /* ================= UI ================= */

  const items = selectedKOT?.items || [];

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title={title}
        loading={loading}
        emptyMessage="No open tickets for this station."
        searchable
        pagination
        exportable
        filters={
          <div className="kds-controls">
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
          { key: "kot_number", title: "KOT No", align: "left" },
          // order_number is resolved by the API. This column was headed
          // "Order ID" and printed the raw restaurant_order.id.
          { key: "order_number", title: "Order No", align: "left" },
          {
            key: "table_code",
            title: "Table / Room",
            align: "left",
            type: "custom",
            render: (row) => row.table_code || row.room_no || "—",
            exportValue: (row) => row.table_code || row.room_no || "",
          },
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
          // badgeType: without it this looked up the status vocabulary, where
          // "ASAP" and "Normal" do not appear, so a rush ticket rendered as the
          // same grey chip as an ordinary one.
          { key: "priority", title: "Priority", align: "center", type: "badge", badgeType: "priority" },
          { key: "kot_status", title: "KOT Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`KOT ${row.kot_number || ""}`.trim()}
                onView={() => openItemsModal(row)}
              />
            ),
          },
        ]}
        data={kots}
      />

      {/* ================= KOT ITEMS ================= */}
      <Modal
        isOpen={!!selectedKOT}
        title={`KOT ${selectedKOT?.kot_number || ""}`}
        onClose={closeItemsModal}
        size="xlarge"
        bodyLayout="custom"
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: closeItemsModal },
          ...(selectedKOT?.kot_status === "New" && perms.edit
            ? [
                {
                  label: "Acknowledge",
                  variant: "secondary",
                  onClick: acknowledgeKot,
                  disabled: busy,
                },
              ]
            : []),
          ...(selectedKOT?.kot_status !== "Completed" && perms.edit
            ? [
                {
                  label: "Mark Whole KOT Ready",
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
            <b>Table / Room</b>
            {selectedKOT?.table_code || selectedKOT?.room_no || "—"}
          </span>
          <span>
            <b>Priority</b>
            {selectedKOT?.priority || "—"}
          </span>
          <span>
            <b>Status</b>
            {selectedKOT?.kot_status || "—"}
          </span>
          <span>
            <b>Placed</b>
            {formatDateTime(selectedKOT?.created_at)}
          </span>
        </div>

        {/* Was a hand-rolled <table className="table table-hover"> with
            per-cell inline styles, hardcoded hex colours and a bare
            <span className="badge"> that had no colour of its own. */}
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
                    onClick={() => markItemReady(item.kot_item_id)}
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

export default KitchenDisplay;

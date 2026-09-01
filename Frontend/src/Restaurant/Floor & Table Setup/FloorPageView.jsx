import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import Tabs, { Tab } from "../../stories/Tabs";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import Button from "../../stories/Button";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { formatCount, formatDate, formatPrecise, todayIso } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import "./FloorTable.css";

/**
 * One floor at a glance: its tables, today's orders on it, and who is working
 * it. Read-only — everything here is edited from its own screen.
 */

// An order is "current" (still open) until it reaches a terminal status.
const TERMINAL_ORDER_STATUSES = new Set(["Completed", "Cancelled"]);

const ViewFloor = () => {
  const { state: floor } = useLocation();
  const navigate = useNavigate();

  const [viewTable, setViewTable] = useState(null);
  const [viewOrder, setViewOrder] = useState(null);
  const [viewStaff, setViewStaff] = useState(null);

  const floorId = floor?.id;

  const {
    data: [tables, orders, staff],
    loading,
    error,
  } = useApiResources(
    [
      {
        fetch: () => APICall.getT("/restaurant/table", { floor_id: floorId }),
        select: readList,
        fallback: "Failed to load tables for this floor.",
      },
      {
        // Filtered server-side. This used to fetch EVERY order in the company
        // and match them against this floor's table ids in the browser.
        fetch: () => APICall.getT("/restaurant/order", { floor_id: floorId }),
        select: readList,
      },
      {
        fetch: () => APICall.getT("/restaurant/staff_assignment", { shift_date: todayIso() }),
        select: readList,
      },
    ],
    { enabled: !!floorId, deps: [floorId] },
  );

  if (!floor) {
    return (
      <ErrorAlert message="No floor was selected. Go back to Floor Layout and open a floor from there." />
    );
  }

  const floorStaff = staff.filter((s) => s.floor_id === floor.id);
  const activeTables = tables.filter((t) => t.table_status !== "Blocked");
  const blockedTables = tables.filter((t) => t.table_status === "Blocked");
  const currentOrders = orders.filter((o) => !TERMINAL_ORDER_STATUSES.has(o.order_status));

  const viewAction = (setter) => ({
    key: "action",
    title: "Actions",
    align: "center",
    type: "custom",
    excludeFromExport: true,
    render: (row) => <RowActions onView={() => setter(row)} />,
  });

  const tableColumns = [
    { key: "table_number", title: "Table No", align: "right" },
    { key: "table_name", title: "Table Name", align: "left" },
    { key: "seating_capacity", title: "Seating Capacity", align: "right" },
    { key: "table_type", title: "Table Type", align: "left" },
    { key: "section", title: "Section", align: "left" },
    { key: "table_status", title: "Status", type: "badge", align: "center" },
    { key: "server_name", title: "Assigned Server", align: "left" },
    viewAction(setViewTable),
  ];

  const orderColumns = [
    { key: "order_number", title: "Order No", align: "left" },
    { key: "order_type", title: "Order Type", align: "left" },
    { key: "guest_name", title: "Guest", align: "left" },
    { key: "order_time", title: "Order Time", align: "left" },
    { key: "order_status", title: "Status", type: "badge", align: "center" },
    {
      key: "grand_total",
      title: "Amount",
      align: "right",
      type: "custom",
      render: (row) => formatPrecise(row.grand_total),
      exportValue: (row) => formatPrecise(row.grand_total),
    },
    viewAction(setViewOrder),
  ];

  const staffColumns = [
    { key: "employee_name", title: "Staff Name", align: "left" },
    { key: "role", title: "Role", align: "left" },
    { key: "section", title: "Section", align: "left" },
    { key: "shift_start", title: "Shift Start", align: "left" },
    { key: "shift_end", title: "Shift End", align: "left" },
    { key: "shift_status", title: "Status", type: "badge", align: "center" },
    viewAction(setViewStaff),
  ];

  return (
    <div className="floor-view">
      {/* Was a <button> carrying eleven inline style properties, three of them
          hardcoded hex colours. */}
      <Button variant="secondary" size="small" onClick={() => navigate("/floor_layout")}>
        <ArrowLeft size={16} aria-hidden="true" /> Back to Floor Layout
      </Button>

      <ErrorAlert message={error} />

      {/* Was eleven `<input readOnly>` controls in a .floor-form grid — tab
          stops the user could focus but not change, with `is_open` printing
          the raw boolean "true". */}
      <ViewSection title="Floor Information">
        <DetailList columns={3}>
          <DetailItem label="Floor Number" value={floor.floor_number} />
          <DetailItem label="Floor Name" value={floor.floor_name} />
          <DetailItem label="Floor Type" value={floor.floor_type} />
          <DetailItem label="Service" value={floor.is_open ? "Open" : "Closed"} />
          <DetailItem label="Planned Tables" value={floor.total_tables} />
          <DetailItem label="Planned Capacity" value={floor.total_capacity} />
          <DetailItem label="Tables in Service" value={formatCount(activeTables.length)} />
          <DetailItem label="Blocked Tables" value={formatCount(blockedTables.length)} />
          <DetailItem label="Open Orders" value={formatCount(currentOrders.length)} />
          <DetailItem label="Orders Today" value={formatCount(orders.length)} />
          <DetailItem label="Staff on Shift" value={formatCount(floorStaff.length)} />
        </DetailList>
      </ViewSection>

      <Tabs variant="default">
        <Tab label="Tables">
          <TableTemplate
            title="Tables on This Floor"
            loading={loading}
            emptyMessage="No tables on this floor yet."
            searchable
            pagination
            exportable
            columns={tableColumns}
            data={activeTables.concat(blockedTables)}
          />
        </Tab>
        <Tab label="Orders">
          <TableTemplate
            title="Orders on This Floor"
            loading={loading}
            emptyMessage="No orders on this floor."
            searchable
            pagination
            exportable
            columns={orderColumns}
            data={orders}
          />
        </Tab>
        <Tab label="Staff">
          <TableTemplate
            title="Staff Assigned Today"
            loading={loading}
            emptyMessage="Nobody is assigned to this floor today."
            searchable
            pagination
            exportable
            columns={staffColumns}
            data={floorStaff}
          />
        </Tab>
      </Tabs>

      {/* Each detail modal used to be `Object.entries(row).map(...)` into
          disabled <Input>s, printing every column including company_id,
          branch_id, created_by and the raw timestamps. */}
      <Modal
        isOpen={!!viewTable}
        title="Table Details"
        onClose={() => setViewTable(null)}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewTable(null) }]}
      >
        <DetailList columns={2}>
          <DetailItem label="Table Code" value={viewTable?.table_code} />
          <DetailItem label="Table Name" value={viewTable?.table_name} />
          <DetailItem label="Table Number" value={viewTable?.table_number} />
          <DetailItem label="Seating Capacity" value={viewTable?.seating_capacity} />
          <DetailItem label="Table Type" value={viewTable?.table_type} />
          <DetailItem label="Section" value={viewTable?.section} />
          <DetailItem label="Status" value={viewTable?.table_status} />
          <DetailItem label="Assigned Server" value={viewTable?.server_name} />
          <DetailItem label="Current Order" value={viewTable?.current_order_number} />
          <DetailItem label="Mergeable" value={viewTable?.is_mergeable ? "Yes" : "No"} />
        </DetailList>
      </Modal>

      <Modal
        isOpen={!!viewOrder}
        title="Order Details"
        onClose={() => setViewOrder(null)}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewOrder(null) }]}
      >
        <DetailList columns={2}>
          <DetailItem label="Order Number" value={viewOrder?.order_number} />
          <DetailItem label="Order Type" value={viewOrder?.order_type} />
          <DetailItem label="Table / Room" value={viewOrder?.service_location} />
          <DetailItem label="Guest" value={viewOrder?.guest_name} />
          <DetailItem label="Guest Mobile" value={viewOrder?.guest_mobile} />
          <DetailItem label="Guests" value={viewOrder?.no_of_guests} />
          <DetailItem label="Order Date" value={formatDate(viewOrder?.order_date)} />
          <DetailItem label="Order Time" value={viewOrder?.order_time} />
          <DetailItem label="Status" value={viewOrder?.order_status} />
          <DetailItem label="Payment" value={viewOrder?.payment_status} />
          <DetailItem label="Subtotal" value={formatPrecise(viewOrder?.sub_total)} />
          <DetailItem label="Grand Total" value={formatPrecise(viewOrder?.grand_total)} />
        </DetailList>
      </Modal>

      <Modal
        isOpen={!!viewStaff}
        title="Staff Details"
        onClose={() => setViewStaff(null)}
        size="medium"
        viewMode
        showFooter
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewStaff(null) }]}
      >
        <DetailList columns={2}>
          <DetailItem label="Staff Name" value={viewStaff?.employee_name} />
          <DetailItem label="Role" value={viewStaff?.role} />
          <DetailItem label="Section" value={viewStaff?.section} />
          <DetailItem label="Shift Date" value={formatDate(viewStaff?.shift_date)} />
          <DetailItem label="Shift Start" value={viewStaff?.shift_start} />
          <DetailItem label="Shift End" value={viewStaff?.shift_end} />
          <DetailItem label="Status" value={viewStaff?.shift_status} />
        </DetailList>
      </Modal>
    </div>
  );
};

export default ViewFloor;

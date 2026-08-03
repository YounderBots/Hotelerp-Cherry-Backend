import { useLocation, useNavigate } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import "./FloorTable.css";
import Tabs, { Tab } from "../../stories/Tabs";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Input from "../../stories/Form/Input";
import ErrorAlert from "../../stories/ErrorAlert";
import { ArrowLeft, Eye } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);
const todayIso = () => new Date().toISOString().slice(0, 10);

// An order is treated as "current" (still open) if it hasn't reached a
// terminal status yet.
const TERMINAL_ORDER_STATUSES = new Set(["Completed", "Cancelled"]);

const ViewFloor = () => {
  const { state: floor } = useLocation();
  const navigate = useNavigate();

  const [tables, setTables] = useState([]);
  const [orders, setOrders] = useState([]);
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [viewTable, setViewTable] = useState(null);
  const [viewOrder, setViewOrder] = useState(null);
  const [viewStaff, setViewStaff] = useState(null);

  const load = useCallback(() => {
    if (!floor?.id) return;
    setLoading(true);
    setError(null);
    Promise.allSettled([
      APICall.getT("/restaurant/table", { floor_id: floor.id }),
      // The order endpoint has no floor-level filter, so every order is
      // fetched once and matched against this floor's table ids below.
      APICall.getT("/restaurant/order"),
      APICall.getT("/restaurant/staff_assignment", { shift_date: todayIso() }),
    ]).then(([tRes, oRes, sRes]) => {
      const tableRows = tRes.status === "fulfilled" ? readList(tRes.value) : [];
      setTables(tableRows);

      const tableIds = new Set(tableRows.map((t) => t.id));
      const allOrders = oRes.status === "fulfilled" ? readList(oRes.value) : [];
      setOrders(allOrders.filter((o) => tableIds.has(o.table_id)));

      const allStaff = sRes.status === "fulfilled" ? readList(sRes.value) : [];
      setStaff(allStaff.filter((s) => s.floor_id === floor.id));

      if (tRes.status === "rejected") setError(errMsg(tRes.reason, "Failed to load tables for this floor."));
      setLoading(false);
    });
  }, [floor?.id]);

  useEffect(() => {
    load();
  }, [load]);

  if (!floor) {
    return (
      <ErrorAlert message='No floor was selected. Go back to Floor Layout and open a floor from there.' />
    );
  }

  const activeTables = tables.filter((t) => t.table_status !== "Blocked");
  const inactiveTables = tables.filter((t) => t.table_status === "Blocked");
  const currentOrders = orders.filter((o) => !TERMINAL_ORDER_STATUSES.has(o.order_status));

  const tableColumns = [
    { key: "table_number", title: "Table No" },
    { key: "table_name", title: "Table Name" },
    { key: "seating_capacity", title: "Seating Capacity" },
    { key: "table_type", title: "Table Type" },
    { key: "section", title: "Section" },
    { key: "table_status", title: "Status", type: "badge", align: "center" },
    { key: "server_name", title: "Assigned Server", type: "custom", render: (row) => row.server_name || "—" },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => setViewTable(row)} />,
    },
  ];

  const orderColumns = [
    { key: "order_number", title: "Order No" },
    { key: "order_type", title: "Order Type" },
    { key: "guest_name", title: "Guest", type: "custom", render: (row) => row.guest_name || "—" },
    { key: "order_time", title: "Order Time" },
    { key: "order_status", title: "Status", type: "badge", align: "center" },
    { key: "grand_total", title: "Amount", align: "center" },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => setViewOrder(row)} />,
    },
  ];

  const staffColumns = [
    { key: "employee_name", title: "Staff Name" },
    { key: "role", title: "Role" },
    { key: "section", title: "Section" },
    { key: "shift_start", title: "Shift Start" },
    { key: "shift_end", title: "Shift End" },
    { key: "shift_status", title: "Status", type: "badge", align: "center" },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => setViewStaff(row)} />,
    },
  ];

  const renderDetailModal = (title, row, onClose) =>
    row && (
      <Modal isOpen={!!row} title={title} onClose={onClose} size="large" bodyLayout="grid" viewMode showFooter actions={[{ label: "Close", variant: "secondary", onClick: onClose }]}>
        {Object.entries(row).map(
          ([key, value]) => key !== "id" && <Input key={key} label={key.replace(/_/g, " ")} value={value ?? "—"} disabled />,
        )}
      </Modal>
    );

  return (
    <div>
      <button
        type="button"
        onClick={() => navigate("/floor_layout")}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          marginBottom: "16px",
          padding: "8px 14px",
          border: "1px solid #d1d5db",
          borderRadius: "8px",
          background: "#ffffff",
          cursor: "pointer",
          fontWeight: 600,
          color: "#334155",
        }}
      >
        <ArrowLeft size={16} />
        <span>Back to Floor Layout</span>
      </button>

      <ErrorAlert message={error} />

      <h2>Floor Information</h2>
      <div className="form-card">
        <div className="floor-form">
          <div className="form-group">
            <label>Floor Number</label>
            <input type="text" value={floor.floor_number ?? "—"} readOnly />
          </div>
          <div className="form-group">
            <label>Floor Name</label>
            <input type="text" value={floor.floor_name ?? "—"} readOnly />
          </div>
          <div className="form-group">
            <label>Floor Type</label>
            <input type="text" value={floor.floor_type ?? "—"} readOnly />
          </div>
          <div className="form-group">
            <label>Open for Service</label>
            <input type="text" value={floor.is_open ?? "—"} readOnly />
          </div>
          <div className="form-group">
            <label>Total Tables</label>
            <input type="text" value={floor.total_tables ?? tables.length} readOnly />
          </div>
          <div className="form-group">
            <label>Active Tables</label>
            <input type="text" value={activeTables.length} readOnly />
          </div>
          <div className="form-group">
            <label>Blocked Tables</label>
            <input type="text" value={inactiveTables.length} readOnly />
          </div>
          <div className="form-group">
            <label>Max Seating Capacity</label>
            <input type="text" value={floor.total_capacity ?? "—"} readOnly />
          </div>
          <div className="form-group">
            <label>Total Orders (loaded)</label>
            <input type="text" value={orders.length} readOnly />
          </div>
          <div className="form-group">
            <label>Current Orders</label>
            <input type="text" value={currentOrders.length} readOnly />
          </div>
          <div className="form-group">
            <label>Staff on Shift Today</label>
            <input type="text" value={staff.length} readOnly />
          </div>
        </div>
      </div>

      <div>
        <Tabs variant="default">
          <Tab label="View Tables">
            <TableTemplate columns={tableColumns} data={activeTables.concat(inactiveTables)} title="Tables on This Floor" loading={loading} />
          </Tab>
          <Tab label="View Orders">
            <TableTemplate columns={orderColumns} data={orders} title="Orders on This Floor" loading={loading} />
          </Tab>
          <Tab label="View Staff">
            <TableTemplate columns={staffColumns} data={staff} title="Staff Assigned to This Floor Today" loading={loading} />
          </Tab>
        </Tabs>
      </div>

      {renderDetailModal("Table Details", viewTable, () => setViewTable(null))}
      {renderDetailModal("Order Details", viewOrder, () => setViewOrder(null))}
      {renderDetailModal("Staff Details", viewStaff, () => setViewStaff(null))}
    </div>
  );
};

export default ViewFloor;

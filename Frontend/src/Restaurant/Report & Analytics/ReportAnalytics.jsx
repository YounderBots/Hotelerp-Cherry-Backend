import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const todayIso = () => new Date().toISOString().slice(0, 10);

const REPORTS = {
  "Sales Reports": {
    endpoint: "/restaurant/reports/item_sales",
    columns: [
      { key: "item_name", title: "Item Name" },
      { key: "quantity_sold", title: "Quantity Sold", align: "center" },
      { key: "total_amount", title: "Total Amount", align: "right" },
    ],
  },
  "Order Reports": {
    endpoint: "/restaurant/reports/cancelled_orders",
    columns: [
      { key: "order_number", title: "Order No" },
      { key: "order_type", title: "Order Type" },
      { key: "guest_name", title: "Guest Name" },
      { key: "order_status", title: "Status", type: "badge", align: "center" },
    ],
  },
  "Kitchen Reports": {
    endpoint: "/restaurant/reports/kitchen_performance",
    columns: [
      { key: "kitchen_name", title: "Kitchen" },
      { key: "total_kots", title: "Total KOTs", align: "center" },
      { key: "completed_kots", title: "Completed", align: "center" },
      { key: "avg_preparation_time_minutes", title: "Avg Prep (min)", align: "center" },
    ],
  },
  "Staff Reports": {
    endpoint: "/restaurant/reports/staff_performance",
    columns: [
      { key: "employee_name", title: "Staff Name" },
      { key: "role", title: "Role" },
      { key: "sales_target", title: "Sales Target", align: "center" },
      { key: "actual_sales", title: "Actual Sales", align: "center" },
      { key: "shift_status", title: "Status", type: "badge", align: "center" },
    ],
  },
  "Table & Floor Reports": {
    endpoint: "/restaurant/reports/table_turnover",
    columns: [
      { key: "table_code", title: "Table" },
      { key: "orders_count", title: "Orders Today", align: "center" },
    ],
  },
  "Inventory Reports": {
    endpoint: "/restaurant/inventory_stock/low_stock",
    dateless: true,
    columns: [
      { key: "item_name", title: "Item Name" },
      { key: "available_quantity", title: "Available Qty", align: "center" },
      { key: "min_stock_level", title: "Reorder Level", align: "center" },
    ],
  },
  "Financial Reports": {
    endpoint: "/restaurant/reports/payment_mode",
    columns: [
      { key: "payment_method", title: "Payment Mode" },
      { key: "total_amount", title: "Total Amount", align: "right" },
    ],
  },
};

const reportTabs = Object.keys(REPORTS);

const ReportAnalytics = () => {
  const [activeReport, setActiveReport] = useState(reportTabs[0]);
  const [reportDate, setReportDate] = useState(todayIso());
  const [rows, setRows] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    const config = REPORTS[activeReport];
    const params = config.dateless ? {} : { report_date: reportDate };

    Promise.allSettled([
      APICall.getT(config.endpoint, params),
      activeReport === "Sales Reports" ? APICall.getT("/restaurant/reports/daily_sales", { report_date: reportDate }) : Promise.resolve(null),
    ]).then(([res, dailyRes]) => {
      if (res.status === "fulfilled") {
        setRows(Array.isArray(res.value?.data) ? res.value.data : []);
      } else {
        setRows([]);
        setError(errMsg(res.reason, "Failed to load report."));
      }
      setSummary(dailyRes && dailyRes.status === "fulfilled" ? dailyRes.value?.data : null);
      setLoading(false);
    });
  }, [activeReport, reportDate]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <>
      <div className="page-card" style={{ marginBottom: 20 }}>
        <div className="modal-body single">
          <div style={{ display: "flex", gap: 10, overflowX: "auto", whiteSpace: "nowrap", paddingBottom: 4, alignItems: "center" }}>
            {reportTabs.map((tab) => (
              <button
                key={tab}
                className={`btn ${activeReport === tab ? "primary" : "secondary"}`}
                style={{ flexShrink: 0 }}
                onClick={() => setActiveReport(tab)}
              >
                {tab}
              </button>
            ))}
            {!REPORTS[activeReport].dateless && (
              <input type="date" value={reportDate} onChange={(e) => setReportDate(e.target.value)} style={{ marginLeft: "auto" }} />
            )}
          </div>
        </div>
      </div>

      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      {summary && (
        <div className="page-card" style={{ marginBottom: 16, padding: "12px 16px", display: "flex", gap: 24, flexWrap: "wrap" }}>
          <span><strong>Orders:</strong> {summary.total_orders}</span>
          <span><strong>Bills:</strong> {summary.total_bills}</span>
          <span><strong>Gross Sales:</strong> {summary.total_sales}</span>
          <span><strong>Tax:</strong> {summary.total_tax}</span>
          <span><strong>Discount:</strong> {summary.total_discount}</span>
          <span><strong>Grand Total:</strong> {summary.grand_total}</span>
        </div>
      )}

      <TableTemplate
        title={activeReport}
        searchable
        pagination
        loading={loading}
        emptyMessage="No data for the selected date"
        columns={REPORTS[activeReport].columns}
        data={rows}
      />
    </>
  );
};

export default ReportAnalytics;

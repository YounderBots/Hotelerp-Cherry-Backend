import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const todayIso = () => new Date().toISOString().slice(0, 10);

const REPORTS = {
  "Sales Reports": {
    endpoint: "/bar/reports/item_sales",
    columns: [
      { key: "item_name", title: "Item Name" },
      { key: "quantity_sold", title: "Quantity Sold", align: "center" },
      { key: "total_amount", title: "Total Amount", align: "right" },
    ],
  },
  "Order Reports": {
    endpoint: "/bar/reports/cancelled_orders",
    columns: [
      { key: "order_number", title: "Order No" },
      { key: "order_type", title: "Order Type" },
      { key: "guest_name", title: "Guest Name" },
      { key: "order_status", title: "Status", type: "badge", align: "center" },
    ],
  },
  "Staff Reports": {
    endpoint: "/bar/reports/staff_performance",
    columns: [
      { key: "employee_name", title: "Staff Name" },
      { key: "role", title: "Role" },
      { key: "sales_target", title: "Sales Target", align: "center" },
      { key: "actual_sales", title: "Actual Sales", align: "center" },
      { key: "shift_status", title: "Status", type: "badge", align: "center" },
    ],
  },
  "Inventory Reports": {
    endpoint: "/bar/inventory_stock/low_stock",
    dateless: true,
    columns: [
      { key: "item_name", title: "Item Name" },
      { key: "available_quantity", title: "Available Qty", align: "center" },
      { key: "min_stock_level", title: "Reorder Level", align: "center" },
    ],
  },
  "Financial Reports": {
    endpoint: "/bar/reports/payment_mode",
    columns: [
      { key: "payment_method", title: "Payment Mode" },
      { key: "total_amount", title: "Total Amount", align: "right" },
    ],
  },
};

const reportTabs = Object.keys(REPORTS);

const BarReportAnalytics = () => {
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
      activeReport === "Sales Reports" ? APICall.getT("/bar/reports/daily_sales", { report_date: reportDate }) : Promise.resolve(null),
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
        <div style={{ display: "flex", flexDirection: "column", gap: "14px", padding: "20px 22px" }}>
          <div style={{ display: "flex", gap: 10, overflowX: "auto", whiteSpace: "nowrap", paddingBottom: 4, alignItems: "center" }}>
            {reportTabs.map((tab) => (
              <Button
                key={tab}
                variant={activeReport === tab ? "primary" : "secondary"}
                style={{ flexShrink: 0 }}
                onClick={() => setActiveReport(tab)}
              >
                {tab}
              </Button>
            ))}
            {!REPORTS[activeReport].dateless && (
              <input type="date" value={reportDate} onChange={(e) => setReportDate(e.target.value)} style={{ marginLeft: "auto" }} />
            )}
          </div>
        </div>
      </div>

      <ErrorAlert message={error} />

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

export default BarReportAnalytics;

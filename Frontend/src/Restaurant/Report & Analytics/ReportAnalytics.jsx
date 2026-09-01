import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Tabs, { Tab } from "../../stories/Tabs";
import Input from "../../stories/Form/Input";
import ErrorAlert from "../../stories/ErrorAlert";
import APICall from "../../APICalls/APICalls";
import { readList } from "../../functions/apiHelpers";
import { formatCount, formatPrecise, todayIso } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import "../../stories/ReportPage.css";

/**
 * Restaurant reporting.
 *
 * Every report is one endpoint plus a column set, so they are declared as data
 * and the page is the same shell for all of them. Amounts and counts go
 * through the shared formatters — they used to be printed as whatever number
 * the API returned, so a total read "1234.5" beside a bill that read "1,234.50".
 */
const money = (key) => ({
  align: "right",
  type: "custom",
  render: (row) => formatPrecise(row[key]),
  exportValue: (row) => formatPrecise(row[key]),
});

const count = (key) => ({
  align: "right",
  type: "custom",
  render: (row) => formatCount(row[key]),
  exportValue: (row) => formatCount(row[key]),
});

const REPORTS = [
  {
    label: "Sales",
    endpoint: "/restaurant/reports/item_sales",
    withSummary: true,
    emptyMessage: "No items were sold on this date.",
    columns: [
      { key: "item_name", title: "Item Name", align: "left" },
      { key: "quantity_sold", title: "Quantity Sold", ...count("quantity_sold") },
      { key: "total_amount", title: "Total Amount", ...money("total_amount") },
    ],
  },
  {
    label: "Orders",
    endpoint: "/restaurant/reports/cancelled_orders",
    emptyMessage: "No cancelled orders on this date.",
    columns: [
      { key: "order_number", title: "Order No", align: "left" },
      { key: "order_type", title: "Order Type", align: "left" },
      { key: "guest_name", title: "Guest Name", align: "left" },
      { key: "order_status", title: "Status", type: "badge", align: "center" },
    ],
  },
  {
    label: "Kitchen",
    endpoint: "/restaurant/reports/kitchen_performance",
    emptyMessage: "No kitchen activity on this date.",
    columns: [
      { key: "kitchen_name", title: "Kitchen", align: "left" },
      { key: "total_kots", title: "Total KOTs", ...count("total_kots") },
      { key: "completed_kots", title: "Completed", ...count("completed_kots") },
      {
        key: "avg_preparation_time_minutes",
        title: "Avg Prep (min)",
        ...money("avg_preparation_time_minutes"),
      },
    ],
  },
  {
    label: "Staff",
    endpoint: "/restaurant/reports/staff_performance",
    emptyMessage: "No staff were scheduled on this date.",
    columns: [
      { key: "employee_name", title: "Staff Name", align: "left" },
      { key: "role", title: "Role", align: "left" },
      { key: "sales_target", title: "Sales Target", ...money("sales_target") },
      { key: "actual_sales", title: "Actual Sales", ...money("actual_sales") },
      { key: "shift_status", title: "Status", type: "badge", align: "center" },
    ],
  },
  {
    label: "Tables",
    endpoint: "/restaurant/reports/table_turnover",
    emptyMessage: "No table activity on this date.",
    columns: [
      { key: "table_code", title: "Table", align: "left" },
      { key: "orders_count", title: "Orders", ...count("orders_count") },
    ],
  },
  {
    label: "Inventory",
    endpoint: "/restaurant/inventory_stock/low_stock",
    // Stock on hand is a right-now figure, not a figure for a past date.
    dateless: true,
    emptyMessage: "Nothing is below its reorder level.",
    columns: [
      { key: "item_name", title: "Item Name", align: "left" },
      { key: "available_quantity", title: "Available Qty", ...money("available_quantity") },
      { key: "min_stock_level", title: "Reorder Level", ...money("min_stock_level") },
    ],
  },
  {
    label: "Financial",
    endpoint: "/restaurant/reports/payment_mode",
    emptyMessage: "No payments were taken on this date.",
    columns: [
      { key: "payment_method", title: "Payment Mode", align: "left" },
      { key: "total_amount", title: "Total Amount", ...money("total_amount") },
    ],
  },
];

const SUMMARY_FIELDS = [
  { key: "total_orders", label: "Orders", format: formatCount },
  { key: "total_bills", label: "Bills", format: formatCount },
  { key: "total_sales", label: "Gross Sales", format: formatPrecise },
  { key: "total_tax", label: "Tax", format: formatPrecise },
  { key: "total_discount", label: "Discount", format: formatPrecise },
  { key: "grand_total", label: "Grand Total", format: formatPrecise },
];

const ReportAnalytics = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [reportDate, setReportDate] = useState(todayIso());

  const report = REPORTS[activeIndex] || REPORTS[0];
  const params = report.dateless ? {} : { report_date: reportDate };

  const {
    data: [rows, summaryRows],
    loading,
    error,
  } = useApiResources(
    [
      {
        fetch: () => APICall.getT(report.endpoint, params),
        select: readList,
        fallback: "Failed to load report.",
      },
      {
        // The daily summary belongs to the Sales tab only; the other tabs skip
        // the request rather than fetching a figure they do not show.
        fetch: () =>
          report.withSummary
            ? APICall.getT("/restaurant/reports/daily_sales", { report_date: reportDate })
            : Promise.resolve(null),
        select: (res) => res?.data || null,
        initial: null,
      },
    ],
    { deps: [activeIndex, reportDate] },
  );

  const summary = report.withSummary ? summaryRows : null;

  return (
    <>
      {/* Was seven <Button>s in a hand-styled scrolling flex row, plus a bare
          <input type="date"> pushed right with `marginLeft:auto`, inside two
          divs carrying a `page-card` class that is not defined anywhere. */}
      <Tabs value={activeIndex} onValueChange={setActiveIndex} scrollable>
        {REPORTS.map((r) => (
          <Tab key={r.label} label={r.label} />
        ))}
      </Tabs>

      <div className="report-controls">
        {!report.dateless && (
          <Input
            label="Report date"
            type="date"
            value={reportDate}
            max={todayIso()}
            onChange={(e) => setReportDate(e.target.value)}
          />
        )}
      </div>

      <ErrorAlert message={error} />

      {summary && (
        <div className="report-summary">
          {SUMMARY_FIELDS.map((f) => (
            <div className="report-summary__stat" key={f.key}>
              <span className="report-summary__label">{f.label}</span>
              <strong className="report-summary__value">{f.format(summary[f.key])}</strong>
            </div>
          ))}
        </div>
      )}

      <TableTemplate
        title={`${report.label} Report`}
        loading={loading}
        emptyMessage={report.emptyMessage}
        searchable
        pagination
        exportable
        columns={report.columns}
        data={rows}
      />
    </>
  );
};

export default ReportAnalytics;

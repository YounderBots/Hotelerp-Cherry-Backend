import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye } from "lucide-react";

const ReportAnalytics = () => {
  const [activeReport, setActiveReport] = useState("Sales Reports");

  /* ================= REPORT DATA ================= */

  const REPORT_DATA = {
    "Sales Reports": [
      {
        id: 1,
        reportName: "Daily Sales",
        date: "2025-01-10",
        totalOrders: 128,
        grossSales: "₹1,24,500",
        discount: "₹5,200",
        tax: "₹9,600",
        netSales: "₹1,28,900",
      },
      {
        id: 2,
        reportName: "Yesterday Sales",
        date: "2025-01-09",
        totalOrders: 104,
        grossSales: "₹98,300",
        discount: "₹4,100",
        tax: "₹7,600",
        netSales: "₹1,01,800",
      },
    ],

    "Order Reports": [
      {
        id: 1,
        reportName: "Completed Orders",
        date: "2025-01-10",
        totalOrders: 95,
        cancelled: 12,
        pending: 8,
      },
      {
        id: 2,
        reportName: "Cancelled Orders",
        date: "2025-01-09",
        totalOrders: 18,
        cancelled: 18,
        pending: 0,
      },
    ],

    "Kitchen Reports": [
      {
        id: 1,
        reportName: "KOT Summary",
        date: "2025-01-10",
        prepared: 210,
        pending: 18,
        delayed: 6,
      },
    ],

    "Staff Reports": [
      {
        id: 1,
        reportName: "Staff Performance",
        staffName: "Arun Kumar",
        ordersHandled: 48,
        avgPrepTime: "12 mins",
      },
      {
        id: 2,
        reportName: "Staff Attendance",
        staffName: "Suresh",
        ordersHandled: 39,
        avgPrepTime: "14 mins",
      },
    ],

    "Table & Floor Reports": [
      {
        id: 1,
        reportName: "Floor Utilization",
        floor: "Ground Floor",
        tablesUsed: 14,
        peakTime: "8:00 PM",
      },
    ],

    "Inventory Reports": [
      {
        id: 1,
        reportName: "Low Stock Items",
        itemName: "Basmati Rice",
        availableQty: "5 Kg",
        reorderLevel: "10 Kg",
      },
    ],

    "Guest Reports": [
      {
        id: 1,
        reportName: "Repeat Guests",
        guestName: "Rahul",
        visits: 6,
        lastVisit: "2025-01-08",
      },
    ],

    "Financial Reports": [
      {
        id: 1,
        reportName: "Payment Summary",
        cash: "₹45,000",
        card: "₹55,000",
        upi: "₹28,900",
      },
    ],
  };

  const reportTabs = Object.keys(REPORT_DATA);

  /* ================= COLUMN MAP ================= */

  const COLUMN_MAP = {
    "Sales Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "date", title: "Date" },
      { key: "totalOrders", title: "Orders", align: "center" },
      { key: "grossSales", title: "Gross Sales" },
      { key: "discount", title: "Discount" },
      { key: "tax", title: "Tax" },
      { key: "netSales", title: "Net Sales" },
    ],

    "Order Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "date", title: "Date" },
      { key: "totalOrders", title: "Total Orders", align: "center" },
      { key: "cancelled", title: "Cancelled", align: "center" },
      { key: "pending", title: "Pending", align: "center" },
    ],

    "Kitchen Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "date", title: "Date" },
      { key: "prepared", title: "Prepared", align: "center" },
      { key: "pending", title: "Pending", align: "center" },
      { key: "delayed", title: "Delayed", align: "center" },
    ],

    "Staff Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "staffName", title: "Staff Name" },
      { key: "ordersHandled", title: "Orders Handled", align: "center" },
      { key: "avgPrepTime", title: "Avg Prep Time", align: "center" },
    ],

    "Table & Floor Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "floor", title: "Floor" },
      { key: "tablesUsed", title: "Tables Used", align: "center" },
      { key: "peakTime", title: "Peak Time", align: "center" },
    ],

    "Inventory Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "itemName", title: "Item Name" },
      { key: "availableQty", title: "Available Qty", align: "center" },
      { key: "reorderLevel", title: "Reorder Level", align: "center" },
    ],

    "Guest Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "guestName", title: "Guest Name" },
      { key: "visits", title: "Visits", align: "center" },
      { key: "lastVisit", title: "Last Visit" },
    ],

    "Financial Reports": [
      { key: "reportName", title: "Report Name" },
      { key: "cash", title: "Cash" },
      { key: "card", title: "Card" },
      { key: "upi", title: "UPI" },
    ],
  };

  return (
    <>
      {/* ================= REPORT TABS (SINGLE ROW) ================= */}
      <div className="page-card" style={{ marginBottom: 20 }}>
        <div className="modal-body single">
          <div
            style={{
              display: "flex",
              gap: 10,
              overflowX: "auto",
              whiteSpace: "nowrap",
              paddingBottom: 4,
            }}
          >
            {reportTabs.map((tab) => (
              <button
                key={tab}
                className={`btn ${
                  activeReport === tab ? "primary" : "secondary"
                }`}
                style={{ flexShrink: 0 }}
                onClick={() => setActiveReport(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ================= REPORT TABLE ================= */}
      <TableTemplate
        title={activeReport}
        searchable
        pagination
        columns={[
          ...COLUMN_MAP[activeReport],
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: () => (
              <button
                className="table-action-btn view"
                style={{ margin: "0 auto" }}
              >
                <Eye size={16} />
              </button>
            ),
          },
        ]}
        data={REPORT_DATA[activeReport]}
      />
    </>
  );
};

export default ReportAnalytics;

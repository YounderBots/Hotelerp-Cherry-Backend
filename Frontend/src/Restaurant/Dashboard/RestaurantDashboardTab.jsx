import React, { useCallback, useEffect, useRef, useState } from "react";

import APICall, { ApiError } from "../../APICalls/APICalls";
import KPICard from "../../Hotel/Dashboard/Components/KPICard";
import DonutChart from "../../Hotel/Dashboard/Components/DonutChart";
import BarListStat from "../../Hotel/Dashboard/Components/BarListStat";
import MiniTableCard from "../../Hotel/Dashboard/Components/MiniTableCard";
import ReportTabHeader from "../../Hotel/Dashboard/Components/ReportTabHeader";

const todayIso = () => new Date().toISOString().slice(0, 10);
const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);

const numberFmt = new Intl.NumberFormat(undefined);
const formatCount = (n) => (Number.isFinite(n) ? numberFmt.format(n) : "—");
const formatCurrency = (n) => (Number.isFinite(n) ? numberFmt.format(Math.round(n)) : "—");

const kitchenColumns = [
  { key: "kitchen_name", title: "Kitchen", render: (r) => r.kitchen_name || `Kitchen #${r.kitchen_id}` },
  { key: "total_kots", title: "Total KOTs", align: "center" },
  { key: "completed_kots", title: "Completed", align: "center" },
  { key: "avg_preparation_time_minutes", title: "Avg Prep (min)", align: "center", render: (r) => r.avg_preparation_time_minutes ?? "—" },
];

const tableColumns = [
  { key: "table_code", title: "Table" },
  { key: "orders_count", title: "Orders Today", align: "center" },
];

const RestaurantDashboardTab = () => {
  const mounted = useRef(true);
  const [reportDate, setReportDate] = useState(todayIso());
  const [summary, setSummary] = useState(null);
  const [avgCheck, setAvgCheck] = useState(null);
  const [categorySales, setCategorySales] = useState(null);
  const [itemSales, setItemSales] = useState(null);
  const [paymentMode, setPaymentMode] = useState(null);
  const [kitchenPerf, setKitchenPerf] = useState(null);
  const [tableTurnover, setTableTurnover] = useState(null);
  const [cancelledCount, setCancelledCount] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setSummary(null);
    setAvgCheck(null);
    setCategorySales(null);
    setItemSales(null);
    setPaymentMode(null);
    setKitchenPerf(null);
    setTableTurnover(null);
    setCancelledCount(null);
    setError(null);

    const params = { report_date: reportDate };

    Promise.allSettled([
      APICall.getT("/restaurant/reports/daily_sales", params),
      APICall.getT("/restaurant/reports/average_check_size", params),
      APICall.getT("/restaurant/reports/category_sales", params),
      APICall.getT("/restaurant/reports/item_sales", params),
      APICall.getT("/restaurant/reports/payment_mode", params),
      APICall.getT("/restaurant/reports/kitchen_performance", params),
      APICall.getT("/restaurant/reports/table_turnover", params),
      APICall.getT("/restaurant/reports/cancelled_orders", params),
    ]).then(([rSummary, rAvg, rCategory, rItems, rPayment, rKitchen, rTable, rCancelled]) => {
      if (!mounted.current) return;

      setSummary(rSummary.status === "fulfilled" ? rSummary.value?.data : { total_orders: 0, total_bills: 0, grand_total: 0 });
      setAvgCheck(rAvg.status === "fulfilled" ? rAvg.value?.data : null);
      setCancelledCount(rCancelled.status === "fulfilled" ? Number(rCancelled.value?.count) || 0 : null);
      setCategorySales({
        data: rCategory.status === "fulfilled" && Array.isArray(rCategory.value?.data) ? rCategory.value.data : [],
        error: rCategory.status === "rejected" ? errMsg(rCategory.reason, "Failed to load category sales.") : null,
      });
      setItemSales({
        data: rItems.status === "fulfilled" && Array.isArray(rItems.value?.data) ? rItems.value.data : [],
        error: rItems.status === "rejected" ? errMsg(rItems.reason, "Failed to load top items.") : null,
      });
      setPaymentMode({
        data: rPayment.status === "fulfilled" && Array.isArray(rPayment.value?.data) ? rPayment.value.data : [],
        error: rPayment.status === "rejected" ? errMsg(rPayment.reason, "Failed to load payment mode breakdown.") : null,
      });
      setKitchenPerf({
        data: rKitchen.status === "fulfilled" && Array.isArray(rKitchen.value?.data) ? rKitchen.value.data : [],
        error: rKitchen.status === "rejected" ? errMsg(rKitchen.reason, "Failed to load kitchen performance.") : null,
      });
      setTableTurnover({
        data: rTable.status === "fulfilled" && Array.isArray(rTable.value?.data) ? rTable.value.data : [],
        error: rTable.status === "rejected" ? errMsg(rTable.reason, "Failed to load table turnover.") : null,
      });

      if (rSummary.status === "rejected") {
        setError(errMsg(rSummary.reason, "Failed to load restaurant sales summary."));
      }
    });
  }, [reportDate]);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load]);

  const loading = summary === null;

  const kpis = [
    { title: "Total Sales", value: loading ? "…" : formatCurrency(summary?.grand_total), type: "sales" },
    { title: "Total Orders", value: loading ? "…" : formatCount(summary?.total_orders), type: "orders" },
    { title: "Total Bills", value: loading ? "…" : formatCount(summary?.total_bills), type: "bills" },
    { title: "Avg Check Size", value: loading || !avgCheck ? "…" : formatCurrency(avgCheck.average_check_size), type: "avgcheck" },
    { title: "Cancelled Orders", value: loading || cancelledCount === null ? "…" : formatCount(cancelledCount), type: "cancelled" },
  ];

  return (
    <div className="dashboard-wrapper">
      <ReportTabHeader
        title="Restaurant Overview"
        subtitle="Restaurant operations"
        reportDate={reportDate}
        onDateChange={setReportDate}
        onRefresh={load}
        loading={loading}
      />

      {error && (
        <div className="dashboard-alert" role="alert">
          <span>{error}</span>
          <button type="button" className="dashboard-alert-action" onClick={load}>Retry</button>
        </div>
      )}

      <div className="kpi-grid">
        {kpis.map((card, index) => (
          <KPICard key={card.title} title={card.title} value={card.value} type={card.type} loading={loading} index={index} />
        ))}
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-6">
          <DonutChart
            title="Sales by Category"
            loading={categorySales === null}
            error={categorySales?.error}
            emptyMessage="No category sales for this date."
            valueFormatter={formatCurrency}
            data={(categorySales?.data || []).map((c) => ({
              label: c.category_name || `Category #${c.category_id}`,
              value: c.total_sales,
            }))}
          />
        </div>
        <div className="dashboard-col dashboard-col-6">
          <DonutChart
            title="Payment Mode"
            loading={paymentMode === null}
            error={paymentMode?.error}
            emptyMessage="No payments recorded for this date."
            valueFormatter={formatCurrency}
            data={(paymentMode?.data || []).map((p) => ({ label: p.payment_method, value: p.total_amount }))}
          />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-6">
          <BarListStat
            title="Top Selling Items"
            loading={itemSales === null}
            error={itemSales?.error}
            emptyMessage="No items sold for this date."
            valueFormatter={formatCurrency}
            items={(itemSales?.data || []).slice(0, 5).map((it) => ({
              label: it.item_name,
              value: it.total_amount,
              sublabel: `${formatCount(it.quantity_sold)} sold`,
            }))}
          />
        </div>
        <div className="dashboard-col dashboard-col-6">
          <MiniTableCard
            title="Kitchen Performance"
            columns={kitchenColumns}
            rows={kitchenPerf?.data || []}
            loading={kitchenPerf === null}
            error={kitchenPerf?.error}
            emptyMessage="No kitchen activity for this date."
            rowKey="kitchen_id"
          />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-12">
          <MiniTableCard
            title="Table Turnover"
            columns={tableColumns}
            rows={tableTurnover?.data || []}
            loading={tableTurnover === null}
            error={tableTurnover?.error}
            emptyMessage="No table orders for this date."
            rowKey="table_code"
          />
        </div>
      </div>
    </div>
  );
};

export default RestaurantDashboardTab;

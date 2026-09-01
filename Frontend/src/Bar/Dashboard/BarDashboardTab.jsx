import React, { useCallback, useEffect, useRef, useState } from "react";

import APICall, { ApiError } from "../../APICalls/APICalls";
import KPICard from "../../Hotel/Dashboard/Components/KPICard";
import DonutChart from "../../Hotel/Dashboard/Components/DonutChart";
import BarListStat from "../../Hotel/Dashboard/Components/BarListStat";
import MiniTableCard from "../../Hotel/Dashboard/Components/MiniTableCard";
import ReportTabHeader from "../../Hotel/Dashboard/Components/ReportTabHeader";
import { todayIso } from "../../functions/formatters";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);

const numberFmt = new Intl.NumberFormat(undefined);
const formatCount = (n) => (Number.isFinite(n) ? numberFmt.format(n) : "—");
const formatCurrency = (n) => (Number.isFinite(n) ? numberFmt.format(Math.round(n)) : "—");

const stationColumns = [
  { key: "station_name", title: "Station", render: (r) => r.station_name || `Station #${r.station_id}` },
  { key: "total_bots", title: "Total BOTs", align: "center" },
  { key: "completed_bots", title: "Completed", align: "center" },
  { key: "avg_preparation_time_minutes", title: "Avg Prep (min)", align: "center", render: (r) => r.avg_preparation_time_minutes ?? "—" },
];

const tableColumns = [
  { key: "table_code", title: "Table" },
  { key: "orders_count", title: "Orders Today", align: "center" },
];

const BarDashboardTab = () => {
  const mounted = useRef(true);
  const [reportDate, setReportDate] = useState(todayIso());
  const [summary, setSummary] = useState(null);
  const [itemSales, setItemSales] = useState(null);
  const [paymentMode, setPaymentMode] = useState(null);
  const [stationPerf, setStationPerf] = useState(null);
  const [tableTurnover, setTableTurnover] = useState(null);
  const [cancelledCount, setCancelledCount] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setSummary(null);
    setItemSales(null);
    setPaymentMode(null);
    setStationPerf(null);
    setTableTurnover(null);
    setCancelledCount(null);
    setError(null);

    const params = { report_date: reportDate };

    Promise.allSettled([
      APICall.getT("/bar/reports/daily_sales", params),
      APICall.getT("/bar/reports/item_sales", params),
      APICall.getT("/bar/reports/payment_mode", params),
      APICall.getT("/bar/reports/station_performance", params),
      APICall.getT("/bar/reports/table_turnover", params),
      APICall.getT("/bar/reports/cancelled_orders", params),
    ]).then(([rSummary, rItems, rPayment, rStation, rTable, rCancelled]) => {
      if (!mounted.current) return;

      setSummary(rSummary.status === "fulfilled" ? rSummary.value?.data : { total_orders: 0, total_bills: 0, grand_total: 0 });
      setCancelledCount(rCancelled.status === "fulfilled" ? Number(rCancelled.value?.count) || 0 : null);
      setItemSales({
        data: rItems.status === "fulfilled" && Array.isArray(rItems.value?.data) ? rItems.value.data : [],
        error: rItems.status === "rejected" ? errMsg(rItems.reason, "Failed to load top items.") : null,
      });
      setPaymentMode({
        data: rPayment.status === "fulfilled" && Array.isArray(rPayment.value?.data) ? rPayment.value.data : [],
        error: rPayment.status === "rejected" ? errMsg(rPayment.reason, "Failed to load payment mode breakdown.") : null,
      });
      setStationPerf({
        data: rStation.status === "fulfilled" && Array.isArray(rStation.value?.data) ? rStation.value.data : [],
        error: rStation.status === "rejected" ? errMsg(rStation.reason, "Failed to load station performance.") : null,
      });
      setTableTurnover({
        data: rTable.status === "fulfilled" && Array.isArray(rTable.value?.data) ? rTable.value.data : [],
        error: rTable.status === "rejected" ? errMsg(rTable.reason, "Failed to load table turnover.") : null,
      });

      if (rSummary.status === "rejected") {
        setError(errMsg(rSummary.reason, "Failed to load bar sales summary."));
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
    { title: "Cancelled Orders", value: loading || cancelledCount === null ? "…" : formatCount(cancelledCount), type: "cancelled" },
  ];

  return (
    <div className="dashboard-wrapper">
      <ReportTabHeader
        title="Bar Overview"
        subtitle="Bar operations"
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
            title="Payment Mode"
            loading={paymentMode === null}
            error={paymentMode?.error}
            emptyMessage="No payments recorded for this date."
            valueFormatter={formatCurrency}
            data={(paymentMode?.data || []).map((p) => ({ label: p.payment_method, value: p.total_amount }))}
          />
        </div>
        <div className="dashboard-col dashboard-col-6">
          <BarListStat
            title="Top Selling Items"
            loading={itemSales === null}
            error={itemSales?.error}
            emptyMessage="No items sold for this date."
            valueFormatter={formatCurrency}
            color="var(--info-color)"
            items={(itemSales?.data || []).slice(0, 5).map((it) => ({
              label: it.item_name,
              value: it.total_amount,
              sublabel: `${formatCount(it.quantity_sold)} sold`,
            }))}
          />
        </div>
      </div>

      <div className="dashboard-row">
        <div className="dashboard-col dashboard-col-6">
          <MiniTableCard
            title="Station Performance"
            columns={stationColumns}
            rows={stationPerf?.data || []}
            loading={stationPerf === null}
            error={stationPerf?.error}
            emptyMessage="No station activity for this date."
            rowKey="station_id"
          />
        </div>
        <div className="dashboard-col dashboard-col-6">
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

export default BarDashboardTab;

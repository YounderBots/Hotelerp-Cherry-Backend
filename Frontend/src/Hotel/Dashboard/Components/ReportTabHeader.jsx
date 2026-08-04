import React from "react";
import { RefreshCw } from "lucide-react";

const todayIso = () => new Date().toISOString().slice(0, 10);

const ReportTabHeader = ({ title, subtitle, reportDate, onDateChange, onRefresh, loading }) => (
  <div className="dashboard-header dashboard-header-inline">
    <div className="dashboard-greeting">
      <div>
        <span className="dashboard-eyebrow">{subtitle}</span>
        <h2 className="dashboard-hello">{title}</h2>
      </div>
    </div>
    <div className="dashboard-actions">
      <input
        type="date"
        className="report-date-input"
        value={reportDate}
        max={todayIso()}
        onChange={(e) => onDateChange(e.target.value)}
        aria-label="Report date"
      />
      <button type="button" className="btn-outline" onClick={onRefresh} disabled={loading} aria-label="Refresh dashboard">
        <RefreshCw size={16} aria-hidden="true" />
        <span>Refresh</span>
      </button>
    </div>
  </div>
);

export default ReportTabHeader;

import React from "react";

const BarListStat = ({
  title,
  items = [],
  loading = false,
  error = null,
  emptyMessage = "No data available.",
  valueFormatter = (v) => String(v),
  color = "var(--primary-color)",
}) => {
  const max = items.reduce((m, it) => Math.max(m, Number(it.value) || 0), 0);

  return (
    <div className="card bar-list-card">
      <div className="card-header-inline">{title && <h4>{title}</h4>}</div>

      {loading && (
        <div className="dashboard-empty" role="status" aria-live="polite">
          Loading…
        </div>
      )}

      {!loading && error && (
        <div className="dashboard-alert inline" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="dashboard-empty">{emptyMessage}</div>
      )}

      {!loading && !error && items.length > 0 && (
        <ol className="platform-legend bar-list-stat" role="list">
          {items.map((it, index) => {
            const value = Number(it.value) || 0;
            const pct = max > 0 ? (value / max) * 100 : 0;
            return (
              <li key={it.label ?? index} className="platform-bar">
                <div className="bar-label">
                  <span>
                    <b className="bar-list-rank">{index + 1}.</b> {it.label}
                    {it.sublabel && <em className="bar-list-sublabel"> · {it.sublabel}</em>}
                  </span>
                  <b>{valueFormatter(value)}</b>
                </div>
                <div className="bar-track" aria-hidden="true">
                  <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
};

export default BarListStat;

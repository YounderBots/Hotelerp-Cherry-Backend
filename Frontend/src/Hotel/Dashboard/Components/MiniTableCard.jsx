import React from "react";

const MiniTableCard = ({ title, columns, rows = [], loading = false, error = null, emptyMessage = "No data available.", rowKey }) => (
  <div className="card table-card">
    <div className="card-header-inline">
      <h4>{title}</h4>
    </div>

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

    {!loading && !error && rows.length === 0 && <div className="dashboard-empty">{emptyMessage}</div>}

    {!loading && !error && rows.length > 0 && (
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key} style={c.align ? { textAlign: c.align } : undefined}>
                  {c.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={rowKey ? row[rowKey] ?? i : i}>
                {columns.map((c) => (
                  <td key={c.key} style={c.align ? { textAlign: c.align } : undefined}>
                    {c.render ? c.render(row) : row[c.key] ?? "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )}
  </div>
);

export default MiniTableCard;

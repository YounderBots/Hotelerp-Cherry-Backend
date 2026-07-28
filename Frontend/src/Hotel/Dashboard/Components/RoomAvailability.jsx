import React from "react";

const COLORS = {
  Occupied: "var(--primary-color)",
  Reserved: "var(--primary-dark)",
  Available: "var(--primary-mild)",
  "Not Ready": "var(--primary-light)",
};

const RoomAvailability = ({ counts, total = 0, loading = false, error = null }) => {
  const rows = counts
    ? [
        { status: "Occupied", count: counts.Occupied ?? 0 },
        { status: "Reserved", count: counts.Reserved ?? 0 },
        { status: "Available", count: counts.Available ?? 0 },
        { status: "Not Ready", count: counts["Not Ready"] ?? 0 },
      ]
    : [];

  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>Room Availability</h4>
        {!loading && !error && total > 0 && (
          <span className="card-meta">{total} rooms</span>
        )}
      </div>

      {loading && (
        <div className="dashboard-empty" role="status" aria-live="polite">
          Loading room status…
        </div>
      )}

      {!loading && error && (
        <div className="dashboard-alert inline" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && total === 0 && (
        <div className="dashboard-empty">
          No rooms configured. Add rooms in Master Data → Rooms.
        </div>
      )}

      {!loading && !error && total > 0 && (
        <div className="availability" role="list">
          {rows.map((row) => {
            const color = COLORS[row.status];
            return (
              <div
                key={row.status}
                role="listitem"
                style={{ borderLeft: `5px solid ${color}`, paddingLeft: "1.25rem" }}
              >
                <span>{row.status}</span>
                <b style={{ color }}>{row.count}</b>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RoomAvailability;

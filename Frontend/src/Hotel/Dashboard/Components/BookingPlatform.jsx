import React from "react";

const data = [
  { label: "Direct Booking", value: 61, color: "var(--primary-mild)" },
  { label: "Booking.com",    value: 12, color: "var(--primary-color)" },
  { label: "Agoda",          value: 11, color: "var(--primary-light)" },
  { label: "Airbnb",         value:  9, color: "var(--primary-lighter)" },
  { label: "Hotels.com",     value:  5, color: "var(--primary-lightest)" },
  { label: "Others",         value:  2, color: "var(--primary-pale)" },
];

const BookingPlatform = () => {
  const radius = 80;
  const strokeWidth = 26;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div
      className="card booking-platform-card"
      aria-label="Booking distribution by platform (sample data)"
    >
      <div className="card-header-inline">
        <h4>Booking by Platform</h4>
        <span className="sample-tag" title="Sample data — no channel-manager integration wired yet">
          Sample
        </span>
      </div>

      <div className="platform-content">
        <svg
          width="240"
          height="240"
          viewBox="0 0 200 200"
          role="img"
          aria-label="Donut chart of booking sources — sample data"
        >
          <g transform="translate(100,100)">
            {data.map((item, index) => {
              const dash = (item.value / 100) * circumference;
              const dashArray = `${dash} ${circumference}`;
              const dashOffset = -offset;
              offset += dash;

              return (
                <circle
                  key={index}
                  r={radius}
                  cx="0"
                  cy="0"
                  fill="transparent"
                  stroke={item.color}
                  strokeWidth={strokeWidth}
                  strokeDasharray={dashArray}
                  strokeDashoffset={dashOffset}
                  transform="rotate(-90)"
                />
              );
            })}
            <text
              textAnchor="middle"
              dy="-0.1em"
              fontSize="30"
              fontWeight="900"
              fill="var(--primary-color)"
            >
              61%
            </text>
            <text
              textAnchor="middle"
              dy="1.6em"
              fontSize="14"
              fontWeight="600"
              fill="var(--gray-600)"
            >
              Direct Booking
            </text>
          </g>
        </svg>

        <ul className="platform-legend" role="list">
          {data.map((item, index) => (
            <li key={index} className="platform-bar">
              <div className="bar-label">
                <span>{item.label}</span>
                <b>{item.value}%</b>
              </div>
              <div className="bar-track" aria-hidden="true">
                <div
                  className="bar-fill"
                  style={{ width: `${item.value}%`, background: item.color }}
                />
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default BookingPlatform;

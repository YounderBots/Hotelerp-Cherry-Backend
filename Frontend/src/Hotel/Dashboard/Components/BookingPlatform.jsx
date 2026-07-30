import React from "react";

const data = [
  { label: "Direct Booking", value: 61, color: "#2a78d6" },
  { label: "Booking.com",    value: 12, color: "#eb6834" },
  { label: "Agoda",          value: 11, color: "#1baf7a" },
  { label: "Airbnb",         value:  9, color: "#eda100" },
  { label: "Hotels.com",     value:  5, color: "#e87ba4" },
  { label: "Others",         value:  2, color: "#008300" },
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
          <defs>
            <filter id="donutShadow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.14" />
            </filter>
          </defs>
          <g transform="translate(100,100)" filter="url(#donutShadow)">
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
              fill="var(--secondary-dark)"
            >
              61%
            </text>
            <text
              textAnchor="middle"
              dy="1.6em"
              fontSize="14"
              fontWeight="600"
              fill="var(--gray-500)"
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

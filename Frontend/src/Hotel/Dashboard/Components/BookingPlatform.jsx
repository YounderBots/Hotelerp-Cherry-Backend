import React from "react";

const data = [
  { label: "Direct Booking", value: 61, color: "var(--primary-mild)" },        // #db1b4b - Vibrant but not too dark
  { label: "Booking.com", value: 12, color: "var(--primary-color)" },          // #850126 - Medium maroon
  { label: "Agoda", value: 11, color: "var(--primary-light)" },                // #d88c9a - Soft rose (lighter)
  { label: "Airbnb", value: 9, color: "var(--primary-lighter)" },              // #f3c9d2 - Blush pink (very light)
  { label: "Hotels.com", value: 5, color: "var(--primary-lightest)" },         // #fff1f4 - Almost white with pink tint
  { label: "Others", value: 2, color: "var(--primary-pale)" }                  // #FFF9F4 - Very pale cream
];

const BookingPlatform = () => {
  const radius = 80;
  const strokeWidth = 26;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="card booking-platform-card">
      {/* Header */}
      <div className="card-header-inline">
        <h4>Booking by Platform</h4>
        <span className="more">⋯</span>
      </div>

      <div className="platform-content">
        {/* DONUT CHART */}
        <svg width="240" height="240" viewBox="0 0 200 200">
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

            {/* Center Text */}
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

        {/* BAR STYLE LEGEND (BIG CHANGE) */}
        <ul className="platform-legend">
          {data.map((item, index) => (
            <li key={index} className="platform-bar">
              <div className="bar-label">
                <span>{item.label}</span>
                <b>{item.value}%</b>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${item.value}%`,
                    background: item.color
                  }}
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

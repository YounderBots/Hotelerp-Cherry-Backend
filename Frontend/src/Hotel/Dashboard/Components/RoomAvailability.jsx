// RoomAvailability.jsx
import React from "react";

const RoomAvailability = () => {
  const rooms = [
    { status: "Occupied", count: 286, color: "var(--primary-color)" },
    { status: "Reserved", count: 87, color: "var(--secondary-color)" },
    { status: "Available", count: 32, color: "var(--success-color)" },
    { status: "Not Ready", count: 13, color: "var(--warning-color)" }
  ];

  return (
    <div className="card">
      <div className="card-header-inline">
        <h4>Room Availability</h4>
        <span className="more">⋯</span>
      </div>
      <div className="availability">
        {rooms.map((room, index) => (
          <div 
            key={index} 
            style={{ 
              borderLeft: `5px solid ${room.color}`,
              paddingLeft: '1.25rem'
            }}
          >
            <span>{room.status}</span>
            <b style={{ color: room.color }}>{room.count}</b>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoomAvailability;

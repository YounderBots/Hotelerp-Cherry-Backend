import React, { useState } from "react";
import { CheckCircle, Ban, CalendarDays, X } from "lucide-react";
import "./Reservation.css";

const STATUS_TABS = [
  { key: "all", label: "All", count: 2 },
  { key: "arrived", label: "Arrived", count: 0 },
  { key: "available", label: "Available", count: 2 },
  { key: "confirmed", label: "Confirmed", count: 0 },
];

const ROOMS = [
  {
    id: 1,
    status: "Available",
    roomName: "Standard Room",
    roomType: "Twin Comfort",
    roomNo: 202,
    image:
      "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
  },
  {
    id: 2,
    status: "Available",
    roomName: "Standard Room",
    roomType: "Delux",
    roomNo: 203,
    image:
      "https://images.unsplash.com/photo-1566073771259-6a8506099945",
  },
];

const RoomView = () => {
  const [activeTab, setActiveTab] = useState("all");
  const [selectedDate, setSelectedDate] = useState("");
  const [activeRoom, setActiveRoom] = useState(null);

  return (
    <div className="roomview-wrapper">
      {/* ================= FILTER BAR ================= */}
      <div className="roomview-filters">
        

        <div className="roomview-tabs">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.key}
              className={`roomview-tab ${
                activeTab === tab.key ? "active" : ""
              }`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
              <span>{tab.count}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ================= ROOM GRID ================= */}
      <div className="roomview-grid-wrapper">
        <div className="roomview-grid">
          {ROOMS.map((room) => (
            <div
              key={room.id}
              className="roomview-card clickable"
              onClick={() => setActiveRoom(room)}
            >
              <div className="roomview-card-status">
                {room.status}
              </div>

              <div className="roomview-room">
                <div className="roomview-room-header">
                  <h4>{room.roomName}</h4>
                  <span className="roomview-room-no">
                    {room.roomNo}
                  </span>
                </div>

                <div className="roomview-room-type">
                  {room.roomType}
                </div>
              </div>

              <div className="roomview-actions">
                <div className="roomview-action-icon">
                  <CheckCircle size={16} />
                </div>
                <div className="roomview-action-icon">
                  <Ban size={16} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ================= IMAGE MODAL ================= */}
      {activeRoom && (
        <div className="room-image-overlay">
          <div className="room-image-modal">
            <button
              className="room-image-close"
              onClick={() => setActiveRoom(null)}
            >
              <X size={18} />
            </button>

            <img
              src={activeRoom.image}
              alt={activeRoom.roomName}
            />

            <div className="room-image-info">
              <h4>{activeRoom.roomName}</h4>
              <p>
                Room No : <b>{activeRoom.roomNo}</b>
              </p>
              <span>{activeRoom.roomType}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoomView;

import React, { useState } from "react";
import "./Reservation.css";

const TABS = [
  { key: "all", label: "All", count: 14 },
  { key: "arrivals", label: "Arrivals", count: 0 },
  { key: "departures", label: "Departures", count: 8 },
  { key: "confirmed", label: "Confirmed", count: 3 },
  { key: "cancelled", label: "Cancelled", count: 3 },
];

const RESERVATIONS = [
  {
    id: 1,
    name: "Anand M",
    checkIn: "29/06/2025",
    checkOut: "30/06/2025",
    total: 150,
    paid: 150,
    balance: 0,
  },
  {
    id: 2,
    name: "Anand M",
    checkIn: "29/06/2025",
    checkOut: "30/06/2025",
    total: 150,
    paid: 0,
    balance: 150,
  },
  {
    id: 3,
    name: "Anand M",
    checkIn: "29/06/2025",
    checkOut: "30/06/2025",
    total: 950,
    paid: null,
    balance: null,
  },
  {
    id: 4,
    name: "Madhu M",
    checkIn: "30/06/2025",
    checkOut: "01/07/2025",
    total: 950,
    paid: 5000,
    balance: 0,
  },
  {
    id: 5,
    name: "Sanjay S",
    checkIn: "30/06/2025",
    checkOut: "01/07/2025",
    total: 1911,
    paid: 5000,
    balance: 0,
  },
  {
    id: 6,
    name: "Anandhi M",
    checkIn: "30/06/2025",
    checkOut: "01/07/2025",
    total: 950,
    paid: 11111,
    balance: 0,
  },
];

const ReservationView = () => {
  const [activeTab, setActiveTab] = useState("all");

  return (
    <div className="reservationview-wrapper">
      {/* ================= FILTER TABS ================= */}
      <div className="reservationview-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`reservationview-tab ${
              activeTab === tab.key ? "active" : ""
            }`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
            <span>{tab.count}</span>
          </button>
        ))}
      </div>

      {/* ================= CARDS GRID ================= */}
      <div className="reservationview-grid">
        {RESERVATIONS.map((item) => (
          <div key={item.id} className="reservation-card">
            {/* Header */}
            <div className="reservation-card-header">
              <h4>{item.name}</h4>
            </div>

            {/* Dates */}
            <div className="reservation-dates">
              <div>
                <p>{item.checkIn}</p>
                <span>12:00:00 AM</span>
                <label>Check In</label>
              </div>

              <div>
                <p>{item.checkOut}</p>
                <span>12:00:00 AM</span>
                <label>Check Out</label>
              </div>
            </div>

            {/* Amounts */}
            <div className="reservation-amount">
              <div>
                <span>Total</span>
                <b>₹ {item.total ?? "None"}</b>
              </div>
              <div>
                <span>Paid</span>
                <b>₹ {item.paid ?? "None"}</b>
              </div>
              <div className="balance">
                <span>Balance</span>
                <b>₹ {item.balance ?? "None"}</b>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReservationView;

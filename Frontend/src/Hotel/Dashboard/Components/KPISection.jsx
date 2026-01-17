// KPISection.jsx
import React, { useState } from "react";
import KPICard from "./KPICard";
import { Plus } from "lucide-react";

const KPISection = () => {
  const [activeIndex, setActiveIndex] = useState(0);

  const cards = [
    {
      title: "New Bookings",
      value: "840",
      change: "+8.70%",
      type: "bookings",
    },
    {
      title: "Check-In",
      value: "231",
      change: "+3.56%",
      type: "checkin",
    },
    {
      title: "Check-Out",
      value: "124",
      change: "-1.06%",
      type: "checkout",
      negative: true,
    },
    {
      title: "Rooms Available",
      value: "32",
      change: "-2.97%",
      type: "available",
      negative: true,
    },
    {
      title: "Total Revenue",
      value: "$123,980",
      change: "+5.70%",
      type: "revenue",
    },
  ];

  return (
    <div className="kpi-section">
      <div
        className="dashboard-header"
        style={{
          background: "transparent",
          boxShadow: "none",
          border: "none",
          padding: "0 0 1rem 0",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
          }}
        >
          <div>
            <h2 style={{ margin: 0, lineHeight: "1.2" }}>
              Welcome back, Admin 
            </h2>
            <p
            >
              Hotel operations overview for today
            </p>
          </div>
          <button className="btn-primary" style={{ height: "42px" }}>
            <Plus/> Add Booking
          </button>
        </div>
      </div>

      <div className="kpi-grid">
        {cards.map((card, index) => (
          <KPICard
            key={index}
            {...card}
            active={activeIndex === index}
            onClick={() => setActiveIndex(index)}
          />
        ))}
      </div>
    </div>
  );
};

export default KPISection;

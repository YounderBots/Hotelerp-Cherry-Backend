import React from "react";
import DonutChart from "./DonutChart";

const data = [
  { label: "Direct Booking", value: 61, color: "#2a78d6" },
  { label: "Booking.com",    value: 12, color: "#eb6834" },
  { label: "Agoda",          value: 11, color: "#1baf7a" },
  { label: "Airbnb",         value:  9, color: "#eda100" },
  { label: "Hotels.com",     value:  5, color: "#e87ba4" },
  { label: "Others",         value:  2, color: "#008300" },
];

const BookingPlatform = () => (
  <DonutChart
    title="Booking by Platform"
    data={data}
    sampleTag="Sample data — no channel-manager integration wired yet"
    valueFormatter={(v) => `${v}%`}
  />
);

export default BookingPlatform;

import React from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye } from "lucide-react";
import "../../MasterData/MasterData.css";

const RoomBooked = () => {
  const columns = [
    {
      key: "reservationId",
      title: "Room Reservation ID",
      align: "center",
    },
    {
      key: "guestName",
      title: "Guest Name",
    },
    {
      key: "phone",
      title: "Phone Number",
      align: "center",
    },
    {
      key: "arrivalDate",
      title: "Arrival Date",
      align: "center",
    },
    {
      key: "departureDate",
      title: "Departure Date",
      align: "center",
    },
    {
      key: "reservationStatus",
      title: "Reservation Status",
      align: "center",
      type: "badge",
    },
    {
      key: "actions",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => (
        <button
          className="table-action-btn view"
          title={`View ${row.reservationId}`}
          onClick={() => console.log("View reservation", row)}
        >
          <Eye size={16} />
        </button>
      ),
    },
  ];

  const data = [
    {
      id: 1,
      reservationId: "RES-1001",
      guestName: "John Doe",
      phone: "9876543210",
      arrivalDate: "2026-01-05",
      departureDate: "2026-01-07",
      reservationStatus: "Confirmed",
    },
    {
      id: 2,
      reservationId: "RES-1002",
      guestName: "Jane Smith",
      phone: "9123456789",
      arrivalDate: "2026-01-06",
      departureDate: "2026-01-08",
      reservationStatus: "Checked In",
    },
    {
      id: 3,
      reservationId: "RES-1003",
      guestName: "Mike Johnson",
      phone: "9001122334",
      arrivalDate: "2026-01-04",
      departureDate: "2026-01-06",
      reservationStatus: "Cancelled",
    },
    {
      id: 4,
      reservationId: "RES-1004",
      guestName: "Sarah Wilson",
      phone: "8899776655",
      arrivalDate: "2026-01-07",
      departureDate: "2026-01-10",
      reservationStatus: "Pending",
    },
    {
      id: 5,
      reservationId: "RES-1005",
      guestName: "Alex Chen",
      phone: "9988776655",
      arrivalDate: "2026-01-03",
      departureDate: "2026-01-05",
      reservationStatus: "Checked Out",
    },
  ];

  return (
    <TableTemplate
      title="Room Booked"
      columns={columns}
      data={data}
      searchable
      pagination
      exportable
    />
  );
};

export default RoomBooked;

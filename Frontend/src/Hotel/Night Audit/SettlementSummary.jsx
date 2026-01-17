import React from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye } from "lucide-react";
import "../../MasterData/MasterData.css";

const SettlementSummary = () => {
  const columns = [
    {
      key: "reservationId",
      title: "Reservation ID",
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
      key: "totalAmount",
      title: "Total Amount",
      align: "right",
    },
    {
      key: "paidAmount",
      title: "Paid Amount",
      align: "right",
    },
    {
      key: "balanceAmount",
      title: "Balance Amount",
      align: "right",
    },
    {
      key: "settlementStatus",
      title: "Settlement Status",
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
          title={`View settlement ${row.reservationId}`}
          onClick={() => console.log("View settlement", row)}
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
      totalAmount: 12500,
      paidAmount: 12500,
      balanceAmount: 0,
      settlementStatus: "Settled",
    },
    {
      id: 2,
      reservationId: "RES-1002",
      guestName: "Jane Smith",
      phone: "9123456789",
      arrivalDate: "2026-01-06",
      departureDate: "2026-01-08",
      totalAmount: 9800,
      paidAmount: 8000,
      balanceAmount: 1800,
      settlementStatus: "Pending",
    },
    {
      id: 3,
      reservationId: "RES-1003",
      guestName: "Mike Johnson",
      phone: "9001122334",
      arrivalDate: "2026-01-04",
      departureDate: "2026-01-06",
      totalAmount: 7600,
      paidAmount: 7600,
      balanceAmount: 0,
      settlementStatus: "Settled",
    },
    {
      id: 4,
      reservationId: "RES-1004",
      guestName: "Sarah Wilson",
      phone: "8899776655",
      arrivalDate: "2026-01-07",
      departureDate: "2026-01-10",
      totalAmount: 15400,
      paidAmount: 10000,
      balanceAmount: 5400,
      settlementStatus: "Partially Paid",
    },
    {
      id: 5,
      reservationId: "RES-1005",
      guestName: "Alex Chen",
      phone: "9988776655",
      arrivalDate: "2026-01-03",
      departureDate: "2026-01-05",
      totalAmount: 6200,
      paidAmount: 6200,
      balanceAmount: 0,
      settlementStatus: "Settled",
    },
  ];

  return (
    <TableTemplate
      title="Settlement Summary"
      columns={columns}
      data={data}
      searchable
      pagination
      exportable
    />
  );
};

export default SettlementSummary;

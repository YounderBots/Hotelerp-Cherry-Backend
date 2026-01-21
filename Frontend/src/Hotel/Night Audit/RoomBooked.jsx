import React,{useState} from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye,X } from "lucide-react";
import "../../MasterData/MasterData.css";

const RoomBooked = () => {
  const [viewReservation, setViewReservation] = useState(null);
  const columns = [
    {
      key: "reservationId",
      title: "Room Reservation ID",
      align: "center",
    },
    {
      key: "Name",
      title: "Name",
      type: "custom",
      render: (row) => [row.FirstName, row.LastName].filter(Boolean).join(" "),
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
      key: "bookingStatus",
      title: "Reservation Status",
      align: "center",
      type: "badge",
    },
    {
      key: "action",
      title: "Action",
      align: "center",
      type: "custom",
      render: (row) => (
        <button
          className="table-action-btn view"
          title={`View ${row.reservationId}`}
          onClick={() => setViewReservation(row)}
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
      FirstName: "Anand",
      LastName:"Kumar",
      phone: "9876543210",
      email: "anand.kumar@gmail.com",
      arrivalDate: "2026-01-12",
      departureDate: "2026-01-13",
      noOfRooms: 1,
      noOfAdults: 2,
      noOfChildren: 1,
      paymentMode: "Debit Card",
      extraBedCost: 0,
      totalAmount: 1000,
      taxAmount: 150,
      discountAmount: 0,
      overallAmount: 1150,
      paidAmount: 0,
      balanceAmount: 1150,
      bookingStatus: "Confirmed",
      reservationType: "Reservation",
      roomComplementary: "No",
      commonComplementary: "Breakfast",
    },
    {
      id: 2,
      reservationId: "RES-1002",
      FirstName: "Madhu",
      LastName: "Priya",
      phone: "9123456780",
      email: "madhu.priya@gmail.com",
      arrivalDate: "2026-01-15",
      departureDate: "2026-01-18",
      noOfRooms: 1,
      noOfAdults: 2,
      noOfChildren: 0,
      paymentMode: "UPI",
      extraBedCost: 0,
      totalAmount: 3000,
      taxAmount: 450,
      discountAmount: 200,
      overallAmount: 3250,
      paidAmount: 2000,
      balanceAmount: 1250,
      bookingStatus: "Checked In",
      reservationType: "Reservation",
      roomComplementary: "Yes",
      commonComplementary: "Breakfast, WiFi",
    },
    {
      id: 3,
      reservationId: "RES-1002",
      FirstName: "Raj",
      LastName: "Kumar",
      phone: "9123456780",
      email: "madhu.priya@gmail.com",
      arrivalDate: "2026-01-15",
      departureDate: "2026-01-18",
      noOfRooms: 1,
      noOfAdults: 2,
      noOfChildren: 0,
      paymentMode: "UPI",
      extraBedCost: 0,
      totalAmount: 3000,
      taxAmount: 450,
      discountAmount: 200,
      overallAmount: 3250,
      paidAmount: 2000,
      balanceAmount: 1250,
      bookingStatus: "Checked In",
      reservationType: "Reservation",
      roomComplementary: "Yes",
      commonComplementary: "Breakfast, WiFi",
    },
  ];

  return (
    <>
    <TableTemplate
      title="Room Booked"
      columns={columns}
      data={data}
      has ActionButton
      pageSize={2}
      searchable
      pagination
      exportable
    />

    {viewReservation && (
        <div className="modal-overlay">
          <div className="modal-card large">
            <div className="modal-header">
              <h3>Booking Details</h3>
              <button onClick={() => setViewReservation(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid view">
              {Object.entries(viewReservation).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn secondary"
                onClick={() => setViewReservation(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RoomBooked;

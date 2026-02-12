import React,{useState,useEffect} from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye,X } from "lucide-react";
import "../../MasterData/MasterData.css";
import APICall from "../../APICalls/APICalls";

const RoomBooked = () => {
    const [data, setData] = useState([]);
  const [viewReservation, setViewReservation] = useState(null);
  const columns = [
    {
      key: "room_reservation_id",
      title: "Room Reservation ID",
      align: "center",
    },
    {
      key: "first_name",
      title: "Name",
      type: "custom",
      render: (row) => [row.first_name, row.last_name].filter(Boolean).join(" "),
    },
    {
      key: "phone_number",
      title: "Phone Number",
      align: "center",
    },
    {
      key: "arrival_date",
      title: "Arrival Date",
      align: "center",
    },
    {
      key: "departure_date",
      title: "Departure Date",
      align: "center",
    },
    {
      key: "reservation_status",
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

  const getAllroomReservation = async () => {
    try {
      const response = await APICall.getT("/hotel/room_reservation");
      console.log("Full Response:", response);
      setData(response.data); 
    } catch (error) {
      console.error("Error fetching reservations:", error);
    }
  };

    useEffect(() => {
      getAllroomReservation();
    }, [])

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

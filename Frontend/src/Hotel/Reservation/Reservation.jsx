import React from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Download, Eye, Pencil,Printer } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./Reservation.css";
const Reservation = () => {
  const Navigate = useNavigate()

  const ViewModel=(row) =>{
    Navigate('/ReservationView',{
      state:row,
    });
  };

  const EditModel=(row)=>{
    Navigate('/ReservationEdit',{
      state:row,
    });
  };

  return (
    <TableTemplate
      title="Reservation List"
      variant="striped"
      pagination
      pageSize={5}
      searchable
      exportable
      hasActionButton
      actionButton={{
        icon: <Download size={18} />,
        label: "Export Reservations",
        onClick: () => {},
        size: "small",
        variant: "outline",
      }}
      columns={[
        {
          key: "reservationId",
          title: "Reservation ID",
          align: "center",
          width: "160px",
        },
        {
          key: "name",
          title: "Guest Name",
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
          key: "status",
          title: "Reservation Status",
          align: "center",
          type: "badge",
        },
        {
          key: "actions",
          title: "Actions",
          align: "center",
          type: "custom",
          render: (row) => (
            <div style={{ display: "flex", justifyContent: "center", gap: "8px" }}>
              <button className="table-action-btn print" title="Print">
                <Printer size={16} />
              </button>
              <button className="table-action-btn view" title="View" onClick={()=>ViewModel(row)}>
                <Eye size={16} />
              </button>
              <button className="table-action-btn edit" title="Edit" onClick={()=>EditModel(row)}>
                <Pencil size={16} />
              </button>
            </div>
          ),
        },
      ]}
      data={[
        {
          id: 1,
          sno: 1,
          reservationId: "RSV-1001",
          name: "John Doe",
          arrivalDate: "2024-02-10",
          departureDate: "2024-02-12",
          status: "confirmed",
          email:"john.doe@example.com",
          phone:"9876543210",
          NumberOfRooms:"1",
          NumberOfNights:"2",
          IdentityType:"1"
        },
        {
          id: 2,
          sno: 2,
          reservationId: "RSV-1002",
          name: "Jane Smith",
          arrivalDate: "2024-02-11",
          departureDate: "2024-02-13",
          status: "pending",
        },
        {
          id: 3,
          sno: 3,
          reservationId: "RSV-1003",
          name: "Michael Brown",
          arrivalDate: "2024-02-15",
          departureDate: "2024-02-18",
          status: "checked-in",
        },
        {
          id: 4,
          sno: 4,
          reservationId: "RSV-1004",
          name: "Sarah Wilson",
          arrivalDate: "2024-02-16",
          departureDate: "2024-02-20",
          status: "cancelled",
        },
      ]}
    />
  );
};

export default Reservation;

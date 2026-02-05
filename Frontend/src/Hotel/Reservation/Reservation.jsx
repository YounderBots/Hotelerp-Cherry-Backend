import React, { useState, useEffect } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Download, Eye, Pencil, Printer, Trash2, Check } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./Reservation.css";
import APICall from "../../APICalls/APICalls";

const Reservation = () => {
  const [data, setData] = useState([])
  const Navigate = useNavigate()

  const ViewModel = (row) => {
    Navigate('/ReservationView', {
      state: row,
    });
  };

  const EditModel = (row) => {
    Navigate("/ReservationEdit", {
      state: { reservation: row },
    });
  };

  const getAllroomReservation = async () => {
    try {
      const AllroomReservation = await APICall.getT("/hotel/room_reservation")
      setData(AllroomReservation.data)
    }
    catch (error) {
      return error
    }

  }

  useEffect(() => {
    getAllroomReservation();
  }, [])
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
        onClick: () => { },
        size: "small",
        variant: "outline",
      }}
      columns={[
        {
          key: "room_reservation_id",
          title: "Reservation ID",
          align: "center",
          width: "160px",
        },
        {
          key: "reservation_type",
          title: "Reservation Type",
          align: "center"
        },
        {
          key: "first_name",
          title: "Name",
          align: "center"
        },
        {
          key: "phone_number",
          title: "Phone",
          align: "center"
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
          key: "actions",
          title: "Actions",
          align: "center",
          type: "custom",
          render: (row) => (
            <div style={{ display: "flex", justifyContent: "center", gap: "8px" }}>
              <button className="table-action-btn print" title="Print">
                <Printer size={16} />
              </button>
              <button className="table-action-btn print" title="check-in">
                <Check size={16} />
              </button>
              <button className="table-action-btn view" title="View" onClick={() => ViewModel(row)}>
                <Eye size={16} />
              </button>
              <button className="table-action-btn edit" title="Edit" onClick={() => EditModel(row)}>
                <Pencil size={16} />
              </button>
              <button className="table-action-btn edit" title="delete" onClick={() => EditModel(row)}>
                <Trash2 size={16} />
              </button>
            </div>
          ),
        },
      ]}
      data={data}
    />
  );
};

export default Reservation;

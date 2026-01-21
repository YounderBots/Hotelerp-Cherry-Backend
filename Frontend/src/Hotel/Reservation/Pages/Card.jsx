import { Building2 } from "lucide-react";
import '../Reservation.css'

const RoomCard = ({ room, isSelected, onSelect }) => {
  if (!room) return null;

  const isAvailable = room.status === "Available";

  return (
    <div
      className={`room-card ${isSelected ? "selected" : ""} ${!isAvailable ? "disabled" : ""}`}

      onClick={() => {
        if (!isAvailable) return;
        onSelect(room);
      }}
    >
      <div className="room-card-header">
        <span>Room No: {room.roomNo}</span>
        <span className={isAvailable ? "status-available" : "status-booked"}>
          {room.status}
        </span>
      </div>

      <div className="room-icon">
        <Building2 size={18} />
      </div>

      <div className="room-card-footer">
        <span>Adult : {room.adults}</span>
        <span>Child : {room.children}</span>
      </div>
    </div>
  );
};

export default RoomCard;

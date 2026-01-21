import { Building2 } from "lucide-react";
import "../Reservation.css";

const RoomCard = ({ room, isSelected, onSelect }) => {
  if (!room) return null;

  return (
    <div
      className={`room-card ${isSelected ? "selected" : ""} `}
      onClick={() => onSelect(room)}
    >
      <div className="room-card-header">
        <span>Room No: {room.roomNo}</span>
        <span className="room-status">{room.status}</span>
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

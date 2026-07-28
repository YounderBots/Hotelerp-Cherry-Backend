import { Building2 } from "lucide-react";
import "../Reservation.css";

const RoomCard = ({ room, isSelected, onSelect, unavailable = false, unavailableReason = "" }) => {
  if (!room) return null;

  return (
    <div
      className={`room-card ${isSelected ? "selected" : ""} ${unavailable ? "unavailable" : ""}`}
      onClick={() => { if (!unavailable) onSelect(room); }}
      aria-disabled={unavailable || undefined}
      title={unavailable ? unavailableReason || "Unavailable" : undefined}
    >
      <div className="room-card-header">
        <span>Room No: {room.room_no}</span>
        <span className="room-status">{unavailable ? (unavailableReason || "Unavailable") : room.booking_status}</span>
      </div>

      <div className="room-icon">
        <Building2 size={18} />
      </div>

      <div className="room-card-footer">
        <span>Adult : {room.max_adult}</span>
        <span>Child : {room.max_child}</span>
      </div>
    </div>
  );
};

export default RoomCard;

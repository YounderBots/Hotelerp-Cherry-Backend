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
        <span className="room-card-no">
          <Building2 size={16} aria-hidden="true" />
          Room No: {room.room_no}
        </span>
        {/* Not room.booking_status: that column is today's occupancy, and this
            screen books a date range. A room whose guest leaves tomorrow is
            free for next month, and labelling its card "Reserved" contradicts
            the availability the page just worked out for these dates. */}
        <span className={`room-status${unavailable ? "" : " is-free"}`}>
          {unavailable ? (unavailableReason || "Unavailable") : "Available"}
        </span>
      </div>

      <div className="room-card-footer">
        <span>Adult : {room.max_adult}</span>
        <span>Child : {room.max_child}</span>
      </div>
    </div>
  );
};

export default RoomCard;

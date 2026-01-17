// BookingTable.jsx
import React from "react";

const BookingTable = () => {
  const bookings = [
    {
      id: "LG-B00113",
      guest: "John Smith",
      roomType: "Standard",
      roomNumber: "Room 101",
      duration: "3 nights",
      checkIn: "Jun 19, 2028",
      checkOut: "Jun 22, 2028",
      status: "Checked-In"
    },
    {
      id: "LG-B00114",
      guest: "Alice Johnson",
      roomType: "Standard",
      roomNumber: "Room 202",
      duration: "2 nights",
      checkIn: "Jun 19, 2028",
      checkOut: "Jun 22, 2028",
      status: "Checked-In"
    },
    {
      id: "LG-B00115",
      guest: "Mark Davis",
      roomType: "Suite",
      roomNumber: "Room 303",
      duration: "5 nights",
      checkIn: "Jun 19, 2028",
      checkOut: "Jun 22, 2028",
      status: "Pending"
    },
    {
      id: "LG-B00116",
      guest: "Emma Watson",
      roomType: "Standard",
      roomNumber: "Room 105",
      duration: "4 nights",
      checkIn: "Jun 19, 2028",
      checkOut: "Jun 22, 2028",
      status: "Confirmed"
    }
  ];

  const getStatusBadge = (status) => {
    switch(status) {
      case 'Checked-In':
        return <span className="badge success">{status}</span>;
      case 'Pending':
        return <span className="badge warning">{status}</span>;
      case 'Confirmed':
        return <span className="badge info">{status}</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  return (
    <div className="card table-card">
      <h4>Booking List</h4>
      <table>
        <thead>
          <tr>
            <th>Booking ID</th>
            <th>Guest Name</th>
            <th>Room Type</th>
            <th>Room Number</th>
            <th>Duration</th>
            <th>Check-In & Check-Out</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {bookings.map((booking, index) => (
            <tr key={index}>
              <td>{booking.id}</td>
              <td><strong>{booking.guest}</strong></td>
              <td>{booking.roomType}</td>
              <td>{booking.roomNumber}</td>
              <td>{booking.duration}</td>
              <td>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontWeight: '500' }}>{booking.checkIn}</span>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>→ {booking.checkOut}</span>
                </div>
              </td>
              <td>{getStatusBadge(booking.status)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BookingTable;
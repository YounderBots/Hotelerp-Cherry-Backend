import React from "react";
import { useLocation } from "react-router-dom";
import "./Reservation.css";

const ReservationModelView = () =>{
    const {state} = useLocation();
    const rooms = [
    {
      sno: 1,
      roomType: "Standard Room",
      roomNo: "202",
      checkIn: "23-01-2026",
      checkOut: "30-01-2026",
      price: 1750,
    },
  ];

  const payments = [
    {
      no: 1,
      date: "25-01-2026",
      amount: 1000,
    },
    {
      no: 2,
      date: "28-01-2026",
      amount: 750,
    },
  ];

  const totalAmount = 1750;
  const taxAmount = 0;
  const discountAmount = 0;
  const overallAmount = totalAmount - discountAmount + taxAmount;

    return(
        <>
            <span className="res">ReservationId:{state.reservationId}</span>
            <div className="Reservation-form-card">
                <div className="Reservation-form">
                    <div className="Reservation-form-group">
                        <label>Customer Name</label>
                        <input type="text" value={state.name} readOnly />
                    </div>
                    <div className="Reservation-form-group">
                        <label>Email</label>
                        <input type="text" value={state.email} readOnly />
                    </div>
                     <div className="Reservation-form-group">
                        <label>Phone Number</label>
                        <input type="text" value={state.phone} readOnly />
                    </div>
                    <div className="Reservation-form-group">
                        <label>Arrival Date</label>
                        <input type="text" value={state.arrivalDate} readOnly />
                    </div>
                     <div className="Reservation-form-group">
                        <label>Depature Date</label>
                        <input type="text" value={state.departureDate} readOnly />
                    </div>
                    <div className="Reservation-form-group">
                        <label>Number of Rooms</label>
                        <input type="text" value={state.NumberOfRooms} readOnly />
                    </div>
                    <div className="Reservation-form-group">
                        <label>Number of Night</label>
                        <input type="text" value={state.NumberOfNights} readOnly />
                    </div>
                    <div className="Reservation-form-group">
                        <label>Reservation Status</label>
                        <input type="text" value={state.status} readOnly />
                    </div>
                </div>
                <p style={{padding:"20px"}}>rrgf</p>
                <div className="invoice-card">
                    <table className="room-table">
                        <thead>
                        <tr>
                            <th>S.No.</th>
                            <th>Room Type</th>
                            <th>Room No</th>
                            <th>Check In</th>
                            <th>Check Out</th>
                            <th>Total Price</th>
                        </tr>
                        </thead>
                        <tbody>
                        {rooms.map((room) => (
                            <tr key={room.sno}>
                            <td>{room.sno}</td>
                            <td>{room.roomType}</td>
                            <td>{room.roomNo}</td>
                            <td>{room.checkIn}</td>
                            <td>{room.checkOut}</td>
                            <td>{room.price}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>

                    <div className="summary-wrapper">
                        <div className="summary">
                        <div>
                            <span>Total Amount :</span>
                            <span>{totalAmount}</span>
                        </div>
                        <div>
                            <span>Tax Amount :</span>
                            <span>{taxAmount}</span>
                        </div>
                        <div>
                            <span>Discount Amount :</span>
                            <span>{discountAmount}</span>
                        </div>
                        <div className="total">
                            <span>Overall Amount :</span>
                            <span>{overallAmount}</span>
                        </div>
                        </div>
                    </div>

                    <h3 className="paid-title">Paid Information</h3>

                    <table className="paid-table">
                        <thead>
                        <tr>
                            <th>No.</th>
                            <th>Date</th>
                            <th>Paid Amount</th>
                        </tr>
                        </thead>
                        <tbody>
                        {payments.map((pay) => (
                            <tr key={pay.no}>
                            <td>{pay.no}</td>
                            <td>{pay.date}</td>
                            <td>{pay.amount}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>

                    </div>

            </div>
           
        </>
    );
}

export default ReservationModelView;
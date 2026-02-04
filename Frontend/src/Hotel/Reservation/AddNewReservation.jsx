import React, { useState } from "react";
import Tabs, { Tab } from "../../stories/Tabs";
import { useEffect } from "react";
import Modal from 'react-modal'
import Button from "../../stories/Button"
import RoomCard from "./Pages/Card";
import Payment from "./payment";
import "./Reservation.css";
import APICall from "../../APICalls/APICalls";

const AddNewReservation = () => {
  const [selectedRooms, setSelectedRooms] = useState([]);
  const [modalView, setModalView] = useState(false);
  const [paymentModal, setpaymentModal] = useState(false);
  const [roomsData, setRoomsData] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);


  const getAllroom_type_ids = async () => {
    try {
      const res = await APICall.getT("/masterdata/room_types");

      console.log("FULL Room Types Response:", res.data);

      if (Array.isArray(res.data.data)) {
        setRoomTypes(res.data.data);
      } else if (Array.isArray(res.data)) {
        setRoomTypes(res.data);
      } else {
        setRoomTypes([]);
      }

    } catch (err) {
      console.log("Room Types API Error:", err);
    }
  };

  const getAllRooms = async () => {
    try {
      const response = await APICall.getT("/masterdata/room");

      console.log("FULL Rooms Response:", response.data);

      if (Array.isArray(response.data.data)) {
        setRoomsData(response.data.data);
      } else if (Array.isArray(response.data)) {
        setRoomsData(response.data);
      } else {
        setRoomsData([]);
      }

    } catch (err) {
      console.log("Rooms API Error:", err);
    }
  };

  useEffect(() => {
    getAllRooms();
    getAllroom_type_ids();
  }, []);



  const [formData, setFormData] = useState({
    title: "Mr",
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    arrivalDate: "",
    departureDate: "",
    nights: "",
    rooms: "1",
    status: "",
    idType: "",
    totalAdult: 2,
    totalChild: 3,
    complementary: false,
  });

  const handleSelect = (room) => {
    setSelectedRooms((prev) =>
      prev.some((r) => r.id === room.id)
        ? prev.filter((r) => r.id !== room.id)
        : [...prev, room]
    );
  };

  const handleSave = () => {
    setModalView(false);
    setpaymentModal(true);
  };

  const isRoomSelected = (room) =>
    selectedRooms.some((r) => r.id === room.id);

  return (
    <div>
      {roomTypes.length === 0 ? (
          <h3>Loading Room Types...</h3>
        ) : (
          <Tabs variant="default">
            {roomTypes.map((type) => (
              <Tab
                key={type.id}
                label={type.room_type || type.room_type_name}
              >
            <h3>{type.room_type} Rooms</h3>

            <RoomGrid
              rooms={roomsData.filter(
                (room) => Number(room.room_type_id) === type.id
              )}
              isSelected={isRoomSelected}
              onSelect={handleSelect}
            />
          </Tab>
            ))}
        </Tabs>
      )}
      <div style={{
        marginTop: "24px", padding: "16px",
        display: "flex",
        justifyContent: "space-between"

      }}>

        <div>
          <strong>Rooms:</strong>{" "}
          {selectedRooms.length === 0
            ? "Book the Rooms"
            : selectedRooms.map((r) => `Room ${r.room_no}`).join(", ")}
        </div>
        <div>
          {selectedRooms.length > 0 && (
            <Button
              className="nxt-btn"
              onClick={() => setModalView(true)}
            >
              Next
            </Button>
          )}
        </div>
      </div>

      <Modal
        isOpen={paymentModal}
        onRequestClose={() => setpaymentModal(false)}
        className="custom-modal"
        overlayClassName="custom-overlay"
      >
        <Payment />
      </Modal>

      <Modal
        isOpen={modalView}
        onRequestClose={() => setModalView(false)}
        className="custom-modal"
        overlayClassName="custom-overlay"

      >

        <div className="reservation-container">
          <div className="reservation-header">
            <h2>Reservation : ROOM_RESERV_62</h2>
          </div>

          <div className="form-card">
            <h3 className="section-title">Other Detail</h3>

            <div className="form-grid">
              <div className="form-group">
                <label>First Name <span className="required">*</span></label>
                <div className="title-input">
                  <select value={formData.title} className="title-select">
                    <option>Mr</option>
                    <option>Ms</option>
                    <option>Mrs</option>
                  </select>
                  <input
                    type="text"
                    placeholder="First Name"
                    style={{ height: "40px" }}
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Last Name <span className="required">*</span></label>
                <input type="text" placeholder="Last Name" />
              </div>

              <div className="form-group">
                <label>Email <span className="required">*</span></label>
                <input type="email" placeholder="Email" />
              </div>

              <div className="form-group">
                <label>Phone Number <span className="required">*</span></label>
                <input type="tel" placeholder="Phone Number" />
              </div>

              <div className="form-group">
                <label>Arrival Date <span className="required">*</span></label>
                <input type="date" placeholder="mm/dd/yyyy" />
              </div>

              <div className="form-group">
                <label>Departure Date <span className="required">*</span></label>
                <input type="date" placeholder="mm/dd/yyyy" />
              </div>

              <div className="form-group">
                <label>Number of Nights <span className="">*</span></label>
                <input type="number" value={formData.nights} />
              </div>

              <div className="form-group">
                <label>Number of Rooms <span className="">*</span></label>
                <input type="number" value="1" readOnly className="readonly-input" />
              </div>

              <div className="form-group">
                <label>Reservation Status <span className="required">*</span></label>
                <select style={{ height: "40px" }}>
                  <option>- select -</option>
                  <option>Confirmed</option>
                  <option>Pending</option>
                </select>
              </div>

              <div className="form-group">
                <label>Identity Type <span className=""></span></label>
                <select style={{ height: "40px" }}>
                  <option>- select -</option>
                  <option>Aadhar Card</option>
                  <option>Passport</option>
                  <option>Driving License</option>
                </select>
              </div>

              <div className="form-group">
                <label>Identity Proof</label>
                <div className="file-upload">
                  <input type="file" id="file" />
                  <label htmlFor="file" className="file-label">
                    Choose File
                  </label>
                  <span className="file-name">No file chosen</span>
                </div>
              </div>
            </div>


            <div className="selected-rooms-section">
              <h3 className="section-title">Selected Rooms:</h3>

              <div className="selected-room-card">
                <div className="room-info">
                  <div className="room-block">
                    <label>Room Type</label>
                    {selectedRooms
                      .map((r) => {
                        const typeObj = roomTypes.find(
                          (t) => Number(t.id) === Number(r.room_type_id)
                        );
                        return typeObj ? typeObj.room_type_name : "Unknown";
                      })
                      .join(", ")}
                  </div>
                  <div className="room-block">
                    <label>Room No</label>
                    {selectedRooms.map((r) => `${r.room_no}`).join(", ")}
                  </div>
                  <div>
                    <label >Rate Type</label>
                    <select className="rate-select">
                      <option>Select Rate Type</option>
                      <option>Daily Rate</option>
                      <option>Weekly Rate</option>
                      <option>Bed Only Rate</option>
                      <option>Bed & Breakfast Rate</option>
                      <option>Half Board Rate</option>
                      <option>Half Board Rate</option>
                      <option>Full Board Rate</option>
                    </select>
                  </div>

                  <div >
                    <label>Total Adult</label>
                    <input type="number" value={2} className="small-input" />
                  </div>
                  <div>
                    <label>Total Child</label>
                    <input type="number" value={3} className="small-input" />
                  </div>
                  <div className="complementary-toggle">
                    <label>Complementary</label>
                    <label className="toggle-switch">
                      <input type="checkbox" />
                      <span className="slider"></span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <Button className="save-btn" onClick={handleSave}>Save</Button>
          </div>

        </div>

      </Modal>






    </div>


  );
};

const RoomGrid = ({ rooms, isSelected, onSelect }) => (
  <div
    style={{
      display: "flex",
      flexWrap: "wrap",
      gap: "16px",
      padding: "16px 0",
    }}
  >
    {rooms.length === 0 ? (
      <p>No rooms available in this category.</p>
    ) : (
      rooms.map((room) => (
        <RoomCard
          key={room.id}
          room={room}
          isSelected={isSelected(room)}
          onSelect={onSelect}
        />
      ))
    )}
  </div>
);

export default AddNewReservation;
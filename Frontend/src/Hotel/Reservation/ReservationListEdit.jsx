import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import Tabs, { Tab } from "../../stories/Tabs";
import RoomCard from "./Pages/Card";

const ReservationListEdit = () => {
  const [selectedRooms, setSelectedRooms] = useState([]);
  const [modalView, setModalView] = useState(false);
  const [paymentModal, setpaymentModal] = useState(false);
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
        : [...prev, room],
    );
  };

  const handleSave = () => {
    setModalView(false);
    setpaymentModal(true);
  };

  const allRooms = [
    {
      id: 1,
      roomNo: 201,
      adults: 2,
      children: 1,
      status: "Available",
      type: "Standard",
    },
    {
      id: 2,
      roomNo: 202,
      adults: 2,
      children: 3,
      status: "Available",
      type: "Standard",
    },
    {
      id: 3,
      roomNo: 301,
      adults: 2,
      children: 0,
      status: "Available",
      type: "Deluxe",
    },
    {
      id: 4,
      roomNo: 302,
      adults: 3,
      children: 2,
      status: "Available",
      type: "Deluxe",
    },
    {
      id: 5,
      roomNo: 401,
      adults: 2,
      children: 2,
      status: "Available",
      type: "Suite",
    },
    {
      id: 6,
      roomNo: 501,
      adults: 4,
      children: 2,
      status: "Available",
      type: "Family",
    },
    {
      id: 7,
      roomNo: 601,
      adults: 2,
      children: 1,
      status: "Available",
      type: "Executive",
    },
  ];

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

  const isRoomSelected = (room) => selectedRooms.some((r) => r.id === room.id);
  return (
    <div className="split-container">
      <div className="left">
        <Tabs variant="default">
          <Tab label="Standard Room">
            <h3>Standard Rooms</h3>
            <RoomGrid
              rooms={allRooms.filter((r) => r.type === "Standard")}
              isSelected={isRoomSelected}
              onSelect={handleSelect}
            />
          </Tab>

          <Tab label="Deluxe Room">
            <h3>Deluxe Rooms</h3>
            <RoomGrid
              rooms={allRooms.filter((r) => r.type === "Deluxe")}
              isSelected={isRoomSelected}
              onSelect={handleSelect}
            />
          </Tab>

          <Tab label="Suite Room">
            <h3>Suite Rooms</h3>
            <RoomGrid
              rooms={allRooms.filter((r) => r.type === "Suite")}
              isSelected={isRoomSelected}
              onSelect={handleSelect}
            />
          </Tab>

          <Tab label="Family Room">
            <h3>Family Rooms</h3>
            <RoomGrid
              rooms={allRooms.filter((r) => r.type === "Family")}
              isSelected={isRoomSelected}
              onSelect={handleSelect}
            />
          </Tab>

          <Tab label="Executive Room">
            <h3>Executive Rooms</h3>
            <RoomGrid
              rooms={allRooms.filter((r) => r.type === "Executive")}
              isSelected={isRoomSelected}
              onSelect={handleSelect}
            />
          </Tab>
        </Tabs>
      </div>
      <div className="right">
        <h1>Table</h1>
      </div>
    </div>
  );
};
export default ReservationListEdit;

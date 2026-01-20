import React, { useState } from "react";
import Tabs, { Tab } from "../../stories/Tabs";
import RoomCard from "./Pages/Card";

const AddNewReservation = () => {
  const [selectedRoom, setSelectedRoom] = useState(null);

  const handleSelected = (room) => {
    setSelectedRoom(room);

  };

  const rooms = [
    { id: 1, roomNo: 201, adults: 2, children: 1, status: "Available" },
    { id: 2, roomNo: 202, adults: 2, children: 3, status: "Available" },
    { id: 3, roomNo: 203, adults: 1, children: 0, status: "Available" },
    { id: 4, roomNo: 203, adults: 1, children: 0, status: "Available" },
  ];


  return (
    <div>
      <Tabs variant="default">
        <Tab label="Standard Room">
          <div>
            <h3>Standard Room</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
              {rooms.map((room) => (
                <RoomCard
                  key={room.id}
                  room={room}
                  isSelected={selectedRoom?.roomNo === room.roomNo}
                  onSelect={handleSelected}
                />
              ))}


            </div>

            {/* <div style={{ display: "flex", gap: "16px" }}>
              <Card
                variant="room"
                roomNo={202}
                adult={2}
                child={3}
                selected={selectedRoom === 202}
                onClick={() => setSelectedRoom(202)}
              />

              <Card
                variant="room"
                roomNo={203}
                adult={1}
                child={1}
                selected={selectedRoom === 203}
                onClick={() => setSelectedRoom(203)}
              />
            </div> */}
          </div>
        </Tab>

        <Tab label="Deluxe Room">
          <h3>Deluxe Room</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
            {rooms.map((room) => (
              <RoomCard
                key={room.id}
                room={room}
                isSelected={selectedRoom?.roomNo === room.roomNo}
                onSelect={handleSelected}
              />
            ))}
          </div>
        </Tab>

        <Tab label="Suite Room">
          <h3>Suite Room</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
            {rooms.map((room) => (
              <RoomCard
                key={room.id}
                room={room}
                isSelected={selectedRoom?.roomNo === room.roomNo}
                onSelect={handleSelected}
              />
            ))}
          </div>
        </Tab>

        <Tab label="Family Room">
          <h3>Family Room</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
            {rooms.map((room) => (
              <RoomCard
                key={room.id}
                room={room}
                isSelected={selectedRoom?.roomNo === room.roomNo}
                onSelect={handleSelected}
              />
            ))}
          </div>
        </Tab>

        <Tab label="Executive Room">
          <h3>Executive Room</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>

            {rooms.map((room) => (
              <RoomCard
                key={room.id}
                room={room}
                isSelected={selectedRoom?.roomNo === room.roomNo}
                onSelect={handleSelected}
              />
            ))}
          </div>
        </Tab>
      </Tabs>

    </div>
  );
};

export default AddNewReservation;

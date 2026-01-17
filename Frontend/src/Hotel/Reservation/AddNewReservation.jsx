import React, { useState } from "react";
import Tabs, { Tab } from "../../stories/Tabs";
import Card from "../../stories/Card";

const AddNewReservation = () => {
  const [selectedRoom, setSelectedRoom] = useState(null);

  return (
    <div>
      <Tabs variant="default">
        <Tab label="Standard Room">
          <div>
            <h3>Standard Room</h3>

            <div style={{ display: "flex", gap: "16px" }}>
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
            </div>
          </div>
        </Tab>

        <Tab label="Deluxe Room">
          <h3>Deluxe Room</h3>
        </Tab>

        <Tab label="Suite Room">
          <h3>Suite Room</h3>
        </Tab>

        <Tab label="Family Room">
          <h3>Family Room</h3>
        </Tab>

        <Tab label="Executive Room">
          <h3>Executive Room</h3>
        </Tab>
      </Tabs>
    </div>
  );
};

export default AddNewReservation;

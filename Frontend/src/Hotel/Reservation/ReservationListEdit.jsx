import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import TableTemplate from "../../stories/TableTemplate";
import Tabs, { Tab } from "../../stories/Tabs";
import RoomCard from "./Pages/Card";
import APICall from "../../APICalls/APICalls";

const ReservationListEdit = () => {
  const [selectedRooms, setSelectedRooms] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [roomsData, setRoomsData] = useState([]);
  const [modalView, setModalView] = useState(false);
  const [paymentModal, setpaymentModal] = useState(false);
  const location = useLocation();
  const reservation = location.state?.reservation;
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
    totaldays: 0,
    totalAdult: 2,
    totalChild: 3,
    complementary: false,
  });

  const handleSelect = (room) => {
    setSelectedRooms((prevSelected) => {
      const exists = prevSelected.some((r) => r.id === room.id);

      const updatedSelectedRooms = exists
        ? prevSelected.filter((r) => r.id !== room.id)
        : [...prevSelected, room];

      setRoomDetails({
        room_ids: updatedSelectedRooms.map((r) => r.id),
        room_type_ids: updatedSelectedRooms.map((r) =>
          Number(r.room_type_id)
        ),
        room_no: updatedSelectedRooms.map((r) => r.room_no),
        rate_type: updatedSelectedRooms.map(() => "daily"),
        room_complementary: updatedSelectedRooms.map(() => ""),
        no_of_adults: updatedSelectedRooms.map(() => 1),
        no_of_children: updatedSelectedRooms.map(() => 0),
      });


      setFormData((prev) => ({
        ...prev,
        no_of_rooms: String(updatedSelectedRooms.length),
      }));

      return updatedSelectedRooms;
    });
  };

  const handleSave = () => {
    setModalView(false);
    setpaymentModal(true);
  };

  const getAllroom_type = async () => {
    try {
      const res = await APICall.getT("/masterdata/room_types");
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

  useEffect(() => {
    getAllroom_type();
    getAllRooms();
  }, [])

  useEffect(() => {
    if (reservation) {
      setFormData((prev) => ({
        ...prev,
        firstName: reservation.first_name || "",
        phone: reservation.phone_number || "",
        arrivalDate: reservation.arrival_date || "",
        departureDate: reservation.departure_date || "",
        // totaldays:reservation.
        status: reservation.reservation_status || "",
      }));
    }
  }, [reservation]);

  useEffect(() => {
    if (formData.arrivalDate && formData.departureDate) {
      const start = new Date(formData.arrivalDate);
      const end = new Date(formData.departureDate);

      const days =
        (end - start) / (1000 * 60 * 60 * 24);

      setFormData((prev) => ({
        ...prev,
        totaldays: days > 0 ? days : 0,
      }));
    }
  }, [formData.arrivalDate, formData.departureDate]);


  return (
    <div className="split-container">
      <div className="left">
        {roomTypes.length === 0 ? (
          <h3>Loading Room Types...</h3>
        ) : (
          <Tabs variant="default">
            {roomTypes.map((type) => (
              <Tab key={type.id} label={type.room_type || type.room_type_name}>
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
      </div>
      <div className="right">
        <div className="top-div">
          <div className="field">
            <input
              type="date"
              value={formData.arrivalDate}
              onChange={(e) =>
                setFormData({ ...formData, arrivalDate: e.target.value })
              }
            />
          </div>

          <div className="field">
            <input
              type="date"
              value={formData.departureDate}
              onChange={(e) =>
                setFormData({ ...formData, departureDate: e.target.value })
              }
            />

          </div>

          <div className="field">
            <input
              type="number"
              value={formData.totaldays}
              readOnly
            />

          </div>
        </div>
        <div>
          
        </div>


        <TableTemplate title={""}
          columns={[
            {
              key: "",
              title: "Room Category",
              align: "center"
            },
            {
              key: "",
              title: "Room No",
              align: "center"
            },
            {
              key: "",
              title: "Total Adult",
              align: "center"
            },
            {
              key: "",
              title: "Total Child",
              align: "center"
            },
            {
              key: "",
              title: "Complementry",
              align: "center"
            },
            {
              key: "",
              title: "Extra Bed",
              align: "center"
            },
            {
              key: "",
              title: "Bed Amt",
              align: "center"
            },
            {
              key: "",
              title: "Amount",
              align: "center"
            },
            {
              key: "",
              title: "Action",
              align: "center"
            },

          ]} />
      </div>

    </div>
  );
};
export default ReservationListEdit;

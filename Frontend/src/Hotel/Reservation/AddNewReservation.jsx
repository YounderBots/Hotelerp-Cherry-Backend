import React, { useState } from "react";
import Tabs, { Tab } from "../../stories/Tabs";
import { useEffect } from "react";
import Modal from 'react-modal'
import Button from "../../stories/Button"
import RoomCard from "./Pages/Card";
import Payment from "./payment";
import "./Reservation.css";
import APICall from "../../APICalls/APICalls";

Modal.setAppElement('#root');

const AddNewReservation = () => {
  const [modalView, setModalView] = useState(false);
  const [paymentModal, setpaymentModal] = useState(false);

  const [identityTypes, setIdentityTypes] = useState([]);
  const [roomsData, setRoomsData] = useState([]);
  const [selectedRooms, setSelectedRooms] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [taxTypes, setTaxTypes] = useState([]);
  const [discountTypes, setDiscountTypes] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [reservationStatusTypes, setReservationStatusTypes] = useState([]);

  const getAllIdentityTypes = async () => {
    const res = await APICall.getT("/masterdata/identity_proof");
    setIdentityTypes(res.data?.data || res.data || []);
  };

  const getAllTaxTypes = async () => {
    const res = await APICall.getT("/masterdata/tax");
    setTaxTypes(res.data?.data || res.data || []);
  };

  const getAllDiscountTypes = async () => {
    const res = await APICall.getT("/masterdata/discount");
    setDiscountTypes(res.data?.data || res.data || []);
  };

  const getAllPaymentMethods = async () => {
    const res = await APICall.getT("/masterdata/payment_methods");
    setPaymentMethods(res.data?.data || res.data || []);
  };

  const getAllReservationStatusTypes = async () => {
    const res = await APICall.getT("/masterdata/reservation_status");
    setReservationStatusTypes(res.data?.data || res.data || []);
  };

  const getAllroom_type_ids = async () => {
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

  useEffect(() => {
    getAllIdentityTypes();
    getAllRooms();
    getAllroom_type_ids();
    getAllTaxTypes();
    getAllDiscountTypes();
    getAllPaymentMethods();
    getAllReservationStatusTypes();
  }, []);

  const [formData, setFormData] = useState({
    salutation: "Mr",
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    arrival_date: "",
    departure_date: "",
    no_of_nights: "",
    no_of_rooms: "1",
    booking_status_id: "",
    identity_type_id: "",
    no_of_adults: 0,
    no_of_children: 0,
    room_complementary: "",
    common_complementary: "",
    room_amount: 0,
    extra_charges: 0,
    extra_bed_count: 0,
    extra_bed_cost: 0,
    total_amount: 0,
    tax_percentage: 0,
    tax_amount: 0,
    discount_percentage: 0,
    discount_amount: 0,
    overall_amount: 0,
    paying_amount: 0,
    paid_amount: 0,
    balance_amount: 0,
    extra_amount: 0
  });

  const [roomDetails, setRoomDetails] = useState({
    room_ids: [],
    room_type_ids: [],
    room_no: [],
    rate_type: [],
    room_complementary: [],
    no_of_adults: [],
    no_of_children: []
  });

  const [errors, setErrors] = useState({
    adults: false,
    children: false
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

  const validateRoomCapacity = (roomIndex, field, value) => {
    const room = selectedRooms[roomIndex];
    const newAdults = field === 'no_of_adults' ? parseInt(value) || 0 : roomDetails.no_of_adults[roomIndex] || 0;
    const newChildren = field === 'no_of_children' ? parseInt(value) || 0 : roomDetails.no_of_children[roomIndex] || 0;
    const maxAdults = parseInt(room.max_adult) || 0;
    const maxChildren = parseInt(room.max_child) || 0;

    const newErrors = { ...errors };

    if (newAdults > maxAdults) {
      newErrors.adults = true;
      alert(`Maximum ${maxAdults} adults allowed for room ${room.room_no}`);
      return false;
    }

    if (newChildren > maxChildren) {
      newErrors.children = true;
      alert(`Maximum ${maxChildren} children allowed for room ${room.room_no}`);
      return false;
    }

    newErrors.adults = false;
    newErrors.children = false;
    setErrors(newErrors);
    return true;
  };

  const handleRoomDetailChange = (index, field, value) => {
    if (field === 'no_of_adults' || field === 'no_of_children') {
      if (!validateRoomCapacity(index, field, value)) {
        return;
      }
    }

    setRoomDetails(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }));

    if (field === 'no_of_adults' || field === 'no_of_children') {
      const totalAdults = field === 'no_of_adults'
        ? roomDetails.no_of_adults.reduce((sum, count, i) => sum + (i === index ? (parseInt(value) || 0) : (parseInt(count) || 0)), 0)
        : roomDetails.no_of_adults.reduce((sum, count) => sum + (parseInt(count) || 0), 0);

      const totalChildren = field === 'no_of_children'
        ? roomDetails.no_of_children.reduce((sum, count, i) => sum + (i === index ? (parseInt(value) || 0) : (parseInt(count) || 0)), 0)
        : roomDetails.no_of_children.reduce((sum, count) => sum + (parseInt(count) || 0), 0);

      setFormData(prev => ({
        ...prev,
        no_of_adults: totalAdults,
        no_of_children: totalChildren
      }));
    }
  };

  const handleSave = () => {
    if (!formData.first_name || !formData.last_name || !formData.email || !formData.phone_number ||
      !formData.arrival_date || !formData.departure_date || !formData.no_of_nights ||
      !formData.booking_status_id || !formData.identity_type_id) {
      alert("Please fill all required fields marked with *");
      return;
    }

    if (selectedRooms.length === 0) {
      alert("Please select at least one room");
      return;
    }

    if (!formData.proof_document) {
      alert("Please upload identity proof document");
      return;
    }

    let capacityValid = true;
    selectedRooms.forEach((room, index) => {
      const adults = roomDetails.no_of_adults[index] || 0;
      const children = roomDetails.no_of_children[index] || 0;
      const maxAdults = parseInt(room.max_adult) || 0;
      const maxChildren = parseInt(room.max_child) || 0;

      if (adults > maxAdults || children > maxChildren) {
        capacityValid = false;
        alert(`Room ${room.room_no} exceeds maximum capacity (Max: ${maxAdults} adults, ${maxChildren} children)`);
      }
    });

    if (!capacityValid) return;

    setModalView(false);
    setpaymentModal(true);
  };

  const isRoomSelected = (room) =>
    selectedRooms.some((r) => r.id === room.id);

  const handleSubmitReservation = async (finalPaymentData) => {
    try {
      const formDataToSend = new FormData();

      formDataToSend.append("room_reservation_id", `ROOM_RES_${Date.now()}`);
      formDataToSend.append("salutation", formData.salutation);
      formDataToSend.append("first_name", formData.first_name);
      formDataToSend.append("last_name", formData.last_name);
      formDataToSend.append("phone_number", formData.phone_number);
      formDataToSend.append("email", formData.email);

      formDataToSend.append("arrival_date", formData.arrival_date);
      formDataToSend.append("departure_date", formData.departure_date);
      formDataToSend.append("no_of_nights", formData.no_of_nights);

      formDataToSend.append("room_type_ids", JSON.stringify(roomDetails.room_type_ids));
      formDataToSend.append("room_ids", JSON.stringify(roomDetails.room_ids));
      formDataToSend.append("rate_type", JSON.stringify(roomDetails.rate_type));

      formDataToSend.append("no_of_rooms", formData.no_of_rooms);
      formDataToSend.append("no_of_adults", formData.no_of_adults);
      formDataToSend.append("no_of_children", formData.no_of_children);

      formDataToSend.append("payment_method_id", finalPaymentData.payment_method_id);
      formDataToSend.append("extra_bed_count", finalPaymentData.extra_bed_count);
      formDataToSend.append("extra_bed_cost", finalPaymentData.extra_bed_cost);

      formDataToSend.append("total_amount", finalPaymentData.total_amount);
      formDataToSend.append("tax_percentage", finalPaymentData.tax_percentage);
      formDataToSend.append("tax_amount", finalPaymentData.tax_amount);
      formDataToSend.append("discount_percentage", finalPaymentData.discount_percentage);
      formDataToSend.append("discount_amount", finalPaymentData.discount_amount);
      formDataToSend.append("extra_charges", finalPaymentData.extra_charges);

      formDataToSend.append("overall_amount", finalPaymentData.overall_amount);
      formDataToSend.append("paid_amount", finalPaymentData.paid_amount);
      formDataToSend.append("balance_amount", finalPaymentData.balance_amount);
      formDataToSend.append("extra_amount", finalPaymentData.extra_amount);

      formDataToSend.append("booking_status_id", formData.booking_status_id);
      formDataToSend.append("room_complementary", formData.room_complementary || "");
      formDataToSend.append("common_complementary", formData.common_complementary || "");

      formDataToSend.append("identity_type_id", formData.identity_type_id);
      if (formData.proof_document) {
        formDataToSend.append("identity_file", formData.proof_document);
      }

      const response = await APICall.postT("/hotel/room_reservation", formDataToSend);
      console.log("Reservation created:", response.data);
      alert("Reservation created successfully!");
      setpaymentModal(false);

      window.location.reload();
    } catch (error) {
      console.error("Error creating reservation:", error);
      alert("Failed to create reservation");
    }
  };

  return (
    <div>
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
      <div style={{
        marginTop: "24px",
        padding: "16px",
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
            <Button className="nxt-btn" onClick={() => setModalView(true)}>
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
        <Payment
          taxTypes={taxTypes}
          discountTypes={discountTypes}
          paymentMethods={paymentMethods}
          formData={formData}
          setFormData={setFormData}
          selectedRooms={selectedRooms}
          roomTypes={roomTypes}
          onSubmit={handleSubmitReservation}
          onClose={() => setpaymentModal(false)}
        />
      </Modal>

      <Modal
        isOpen={modalView}
        onRequestClose={() => setModalView(false)}
        className="custom-modal"
        overlayClassName="custom-overlay"
      >
        <div className="reservation-container">
          <div className="reservation-header">
            <h2>Reservation Details</h2>
            <button className="close-modal" onClick={() => setModalView(false)}>&times;</button>
          </div>

          <div className="form-card">
            <h3 className="section-title">Guest Information</h3>

            <div className="form-grid">
              <div className="form-group">
                <label>First Name <span className="required">*</span></label>
                <div className="title-input">
                  <select
                    value={formData.salutation}
                    className="title-select"
                    onChange={(e) => setFormData({ ...formData, salutation: e.target.value })}
                  >
                    <option>Mr</option>
                    <option>Ms</option>
                    <option>Mrs</option>
                  </select>
                  <input
                    type="text"
                    placeholder="First Name"
                    style={{ height: "40px" }}
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Last Name <span className="required">*</span></label>
                <input
                  type="text"
                  placeholder="Last Name"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email <span className="required">*</span></label>
                <input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone Number <span className="required">*</span></label>
                <input
                  type="tel"
                  placeholder="Phone Number"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Arrival Date <span className="required">*</span></label>
                <input
                  type="date"
                  value={formData.arrival_date}
                  onChange={(e) => {
                    const arrival = e.target.value;
                    const departure = formData.departure_date;

                    let nights = formData.no_of_nights;
                    if (arrival && departure) {
                      const start = new Date(arrival);
                      const end = new Date(departure);
                      const diff = (end - start) / (1000 * 60 * 60 * 24);
                      nights = diff > 0 ? diff : 0;
                    }

                    setFormData({
                      ...formData,
                      arrival_date: arrival,
                      no_of_nights: nights,
                    });
                  }}
                  required
                />
              </div>

              <div className="form-group">
                <label>Departure Date <span className="required">*</span></label>
                <input
                  type="date"
                  value={formData.departure_date}
                  min={formData.arrival_date}
                  onChange={(e) => {
                    const departure = e.target.value;
                    const arrival = formData.arrival_date;

                    let nights = formData.no_of_nights;
                    if (arrival && departure) {
                      const start = new Date(arrival);
                      const end = new Date(departure);
                      const diff = (end - start) / (1000 * 60 * 60 * 24);
                      nights = diff > 0 ? diff : 0;
                    }

                    setFormData({
                      ...formData,
                      departure_date: departure,
                      no_of_nights: nights,
                    });
                  }}
                  required
                />
              </div>

              <div className="form-group">
                <label>Number of Nights <span className="required">*</span></label>
                <input
                  type="number"
                  value={formData.no_of_nights}
                  readOnly
                />
              </div>


              <div className="form-group">
                <label>Number of Rooms</label>
                <input
                  type="number"
                  value={formData.no_of_rooms}
                  readOnly
                  className="readonly-input"
                />
              </div>

              <div className="form-group">
                <label>Reservation Status <span className="required">*</span></label>
                <select
                  style={{ height: "40px" }}
                  value={formData.booking_status_id}
                  onChange={(e) => setFormData({ ...formData, booking_status_id: e.target.value })}
                  required
                >
                  <option value="">- select -</option>
                  {reservationStatusTypes.map((status) => (
                    <option key={status.id} value={status.id}>
                      {status.reservation_status}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Identity Type <span className="required">*</span></label>
                <select
                  style={{ height: "40px" }}
                  value={formData.identity_type_id}
                  onChange={(e) => setFormData({ ...formData, identity_type_id: e.target.value })}
                  required
                >
                  <option value="">- select -</option>
                  {identityTypes.map((identity) => (
                    <option key={identity.id} value={identity.id}>
                      {identity.proof_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Identity Proof <span className="required">*</span></label>
                <div className="file-upload">
                  <input
                    type="file"
                    id="file"
                    onChange={(e) => setFormData({ ...formData, proof_document: e.target.files[0] })}
                    required
                  />
                  <label htmlFor="file" className="file-label">
                    Choose File
                  </label>
                  <span className="file-name">
                    {formData.proof_document ? formData.proof_document.name : "No file chosen"}
                  </span>
                </div>
              </div>
            </div>

            <div className="selected-rooms-section">
              <h3 className="section-title">Selected Rooms:</h3>
              {selectedRooms.map((room, index) => {
                const roomTypeObj = roomTypes.find(t => Number(t.id) === Number(room.room_type_id));
                const maxAdults = parseInt(room.max_adult) || 0;
                const maxChildren = parseInt(room.max_child) || 0;

                return (
                  <div key={room.id} className="selected-room-card">
                    <div className="room-info">
                      <div className="room-block">
                        <label>Room Type</label>
                        <div>{roomTypeObj ? (roomTypeObj.room_type || roomTypeObj.room_type_name) : "Unknown"}</div>
                      </div>
                      <div className="room-block">
                        <label>Room No</label>
                        <div>{room.room_no}</div>
                      </div>
                      <div className="room-block">
                        <label>Max Capacity</label>
                        <div>{maxAdults} adults, {maxChildren} children</div>
                      </div>
                      <div>
                        <label>Rate Type</label>
                        <select
                          className="rate-select"
                          value={roomDetails.rate_type[index] || "daily"}
                          onChange={(e) => handleRoomDetailChange(index, 'rate_type', e.target.value)}
                        >
                          <option value="daily">Daily Rate</option>
                          <option value="weekly">Weekly Rate</option>
                          <option value="bed_only">Bed Only Rate</option>
                          <option value="bed_breakfast">Bed & Breakfast Rate</option>
                          <option value="half_board">Half Board Rate</option>
                          <option value="full_board">Full Board Rate</option>
                        </select>
                      </div>
                      <div>
                        <label>Total Adult</label>
                        <input
                          type="number"
                          value={roomDetails.no_of_adults[index] || 0}
                          className="small-input"
                          onChange={(e) => handleRoomDetailChange(index, 'no_of_adults', parseInt(e.target.value) || 1)}
                          min="1"
                          max={maxAdults}
                        />
                      </div>
                      <div>
                        <label>Total Child</label>
                        <input
                          type="number"
                          value={roomDetails.no_of_children[index] || 0}
                          className="small-input"
                          onChange={(e) => handleRoomDetailChange(index, 'no_of_children', parseInt(e.target.value) || 0)}
                          min="0"
                          max={maxChildren}
                        />
                      </div>
                      <div className="complementary-toggle">
                        <label>Complementary</label>
                        <select
                          value={roomDetails.room_complementary[index] || ""}
                          onChange={(e) => handleRoomDetailChange(index, 'room_complementary', e.target.value)}
                          style={{ height: "40px", marginLeft: "10px" }}
                        >
                          <option value="">No Complementary</option>
                          <option value="Breakfast">Breakfast</option>
                          <option value="Welcome Drink">Welcome Drink</option>
                          <option value="Lunch">Lunch</option>
                          <option value="Dinner">Dinner</option>
                        </select>
                      </div>
                    </div>
                  </div>
                );
              })}
              <div style={{ marginTop: "10px", padding: "10px", backgroundColor: "#f5f5f5", borderRadius: "4px" }}>
                <strong>Total Adults: {formData.no_of_adults}</strong> | <strong>Total Children: {formData.no_of_children}</strong>
              </div>
            </div>

            <div className="form-group" style={{ marginTop: "20px" }}>
              <label>Common Complementary</label>
              <select
                value={formData.common_complementary}
                onChange={(e) => setFormData({ ...formData, common_complementary: e.target.value })}
                style={{ height: "40px", width: "100%" }}
              >
                <option value="">No Complementary</option>
                <option value="Welcome Drink">Welcome Drink</option>
                <option value="Airport Pickup">Airport Pickup</option>
                <option value="Late Checkout">Late Checkout</option>
                <option value="Spa Voucher">Spa Voucher</option>
              </select>
            </div>
          </div>
          <div className="modal-footer">
            <Button className="cancel-btn" onClick={() => setModalView(false)}>Cancel</Button>
            <Button className="save-btn" onClick={handleSave}>Save & Continue to Billing</Button>
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
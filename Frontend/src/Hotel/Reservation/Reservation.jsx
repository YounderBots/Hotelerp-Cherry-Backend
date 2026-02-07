import React, { useState, useEffect } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Download, Eye, Pencil, Printer, Trash2, Check, X } from "lucide-react";
import APICall from "../../APICalls/APICalls";
import "./Reservation.css";

const Reservation = () => {
  const [data, setData] = useState([]);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({});

  const getStatusBadgeClass = (status) => {
    const statusLower = status?.toLowerCase();
    switch(statusLower) {
      case 'pending':
        return "status-pending";
      case 'confirmed':
        return "status-confirmed";
      case 'checked-in':
        return "status-checked-in";
      case 'checked-out':
        return "status-checked-out";
      case 'cancelled':
        return "status-cancelled";
      default:
        return "status-pending";
    }
  };

  const getAllroomReservation = async () => {
    try {
      const AllroomReservation = await APICall.getT("/hotel/room_reservation");
      setData(AllroomReservation.data);
    } catch (error) {
      console.error("Error fetching reservations:", error);
    }
  };

  const UpdateRoomReservation = async (id, formData) => {
    try {
      const formDataToSend = new FormData();
      
      Object.keys(formData).forEach(key => {
        if (key === 'room_type_ids' || key === 'room_ids' || key === 'rate_type') {
          formDataToSend.append(key, Array.isArray(formData[key]) ? JSON.stringify(formData[key]) : formData[key]);
        } else {
          formDataToSend.append(key, formData[key]);
        }
      });
      
      formDataToSend.append('id', id);
      
      await APICall.putT(`/hotel/room_reservation`, formDataToSend);
      getAllroomReservation();
      setIsEditModalOpen(false);
    } catch (error) {
      console.error("Error updating reservation:", error);
    }
  };

  const DeleteRoomReservation = async (id) => {
    try {
      await APICall.deleteT(`/hotel/room_reservation/${id}`);
      getAllroomReservation();
    } catch (error) {
      console.error("Error deleting reservation:", error);
    }
  };

  const handlePrint = (row) => {
    const printWindow = window.open('', '_blank');
    const printContent = `
      <html>
        <head>
          <title>Reservation Receipt - ${row.room_reservation_id}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { text-align: center; margin-bottom: 30px; }
            .section { margin-bottom: 20px; }
            .section h3 { border-bottom: 2px solid #000; padding-bottom: 5px; }
            .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
            .detail-item { margin-bottom: 8px; }
            .label { font-weight: bold; color: #555; }
            .total { font-size: 18px; font-weight: bold; margin-top: 20px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Reservation Receipt</h1>
            <p>Reservation ID: ${row.room_reservation_id}</p>
            <p>Date: ${new Date().toLocaleDateString()}</p>
          </div>
          
          <div class="section">
            <h3>Guest Information</h3>
            <div class="grid">
              <div class="detail-item">
                <span class="label">Name:</span> ${row.first_name} ${row.last_name}
              </div>
              <div class="detail-item">
                <span class="label">Phone:</span> ${row.phone_number}
              </div>
              <div class="detail-item">
                <span class="label">Email:</span> ${row.email || "N/A"}
              </div>
              <div class="detail-item">
                <span class="label">Reservation Type:</span> ${row.reservation_type}
              </div>
              <div class="detail-item">
                <span class="label">Status:</span> ${row.reservation_status}
              </div>
              <div class="detail-item">
                <span class="label">Confirmation Code:</span> ${row.confirmation_code || "N/A"}
              </div>
            </div>
          </div>
          
          <div class="section">
            <h3>Stay Information</h3>
            <div class="grid">
              <div class="detail-item">
                <span class="label">Arrival Date:</span> ${row.arrival_date}
              </div>
              <div class="detail-item">
                <span class="label">Departure Date:</span> ${row.departure_date}
              </div>
              <div class="detail-item">
                <span class="label">Nights:</span> ${row.no_of_nights}
              </div>
              <div class="detail-item">
                <span class="label">Rooms:</span> ${row.no_of_rooms}
              </div>
              <div class="detail-item">
                <span class="label">Adults:</span> ${row.no_of_adults}
              </div>
              <div class="detail-item">
                <span class="label">Children:</span> ${row.no_of_children}
              </div>
              <div class="detail-item">
                <span class="label">Extra Beds:</span> ${row.extra_bed_count || 0}
              </div>
              <div class="detail-item">
                <span class="label">Payment Method:</span> ${row.payment_method_id}
              </div>
            </div>
          </div>
          
          <div class="section">
            <h3>Payment Summary</h3>
            <div class="detail-item">
              <span class="label">Total Amount:</span> $${row.total_amount}
            </div>
            <div class="detail-item">
              <span class="label">Tax Amount:</span> $${row.tax_amount || 0}
            </div>
            <div class="detail-item">
              <span class="label">Discount Amount:</span> $${row.discount_amount || 0}
            </div>
            <div class="detail-item">
              <span class="label">Extra Charges:</span> $${row.extra_charges || 0}
            </div>
            <div class="detail-item">
              <span class="label">Paid Amount:</span> $${row.paid_amount || 0}
            </div>
            <div class="detail-item">
              <span class="label">Balance Amount:</span> $${row.balance_amount || 0}
            </div>
            <div class="detail-item total">
              <span class="label">Overall Amount:</span> $${row.overall_amount}
            </div>
          </div>
        </body>
      </html>
    `;
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this reservation?")) {
      DeleteRoomReservation(id);
    }
  };

  const handleView = (row) => {
    setSelectedReservation(row);
    setIsViewModalOpen(true);
  };

  const handleEdit = (row) => {
    setSelectedReservation(row);
    const roomTypeIds = Array.isArray(row.room_type_ids) ? row.room_type_ids : JSON.parse(row.room_type_ids || '[]');
    const roomIds = Array.isArray(row.room_ids) ? row.room_ids : JSON.parse(row.room_ids || '[]');
    const rateType = Array.isArray(row.rate_type) ? row.rate_type : JSON.parse(row.rate_type || '[]');
    
    setEditFormData({
      ...row,
      room_type_ids: roomTypeIds,
      room_ids: roomIds,
      rate_type: rateType
    });
    setIsEditModalOpen(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditFormData({
      ...editFormData,
      [name]: value
    });
  };

  const handleEditSubmit = (e) => {
    e.preventDefault();
    
    const updatedData = {
      ...editFormData,
      arrival_date: editFormData.arrival_date,
      departure_date: editFormData.departure_date,
      no_of_nights: editFormData.no_of_nights,
      room_type_ids: JSON.stringify(editFormData.room_type_ids || []),
      room_ids: JSON.stringify(editFormData.room_ids || []),
      rate_type: JSON.stringify(editFormData.rate_type || []),
      total_amount: parseFloat(editFormData.total_amount) || 0,
      overall_amount: parseFloat(editFormData.overall_amount) || 0,
      paid_amount: parseFloat(editFormData.paid_amount) || 0,
      balance_amount: parseFloat(editFormData.balance_amount) || 0,
      extra_amount: parseFloat(editFormData.extra_amount) || 0,
      tax_amount: parseFloat(editFormData.tax_amount) || 0,
      discount_amount: parseFloat(editFormData.discount_amount) || 0,
      extra_charges: parseFloat(editFormData.extra_charges) || 0,
      extra_bed_cost: parseFloat(editFormData.extra_bed_cost) || 0,
      extra_bed_count: parseInt(editFormData.extra_bed_count) || 0,
      no_of_rooms: parseInt(editFormData.no_of_rooms) || 1,
      no_of_adults: parseInt(editFormData.no_of_adults) || 1,
      no_of_children: parseInt(editFormData.no_of_children) || 0,
      payment_method_id: parseInt(editFormData.payment_method_id) || 1,
      booking_status_id: parseInt(editFormData.booking_status_id) || 1,
      identity_type_id: parseInt(editFormData.identity_type_id) || 1
    };
    
    UpdateRoomReservation(selectedReservation.id, updatedData);
  };

  const handleApprove = (id) => {
    const reservation = data.find(item => item.id === id);
    if (reservation) {
      const updatedData = {
        ...reservation,
        reservation_status: 'Confirmed',
        booking_status_id: 2
      };
      UpdateRoomReservation(id, updatedData);
    }
  };

  useEffect(() => {
    getAllroomReservation();
  }, []);

  return (
    <>
      <TableTemplate
        title="Reservation List"
        variant="striped"
        pagination
        pageSize={5}
        searchable
        exportable
        hasActionButton
        actionButton={{
          icon: <Download size={18} />,
          label: "Export Reservations",
          onClick: () => {},
          size: "small",
          variant: "outline",
        }}
        columns={[
          {
            key: "room_reservation_id",
            title: "Reservation ID",
            align: "center",
            width: "160px",
          },
          {
            key: "reservation_type",
            title: "Reservation Type",
            align: "center"
          },
          {
            key: "first_name",
            title: "Name",
            align: "center",
            render: (row) => `${row.first_name} ${row.last_name || ''}`
          },
          {
            key: "phone_number",
            title: "Phone",
            align: "center"
          },
          {
            key: "arrival_date",
            title: "Arrival Date",
            align: "center",
          },
          {
            key: "departure_date",
            title: "Departure Date",
            align: "center",
          },
          {
            key: "reservation_status",
            title: "Reservation Status",
            align: "center",
            type: "badge",
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div className="table-actions">
                <button 
                  className="table-action-btn print" 
                  title="Print"
                  onClick={() => handlePrint(row)}
                >
                  <Printer size={16} />
                </button>
                {row.reservation_status !== 'Confirmed' && (
                  <button 
                    className="table-action-btn print" 
                    title="Approve"
                    onClick={() => handleApprove(row.id)}
                  >
                    <Check size={16} />
                  </button>
                )}
                <button 
                  className="table-action-btn view" 
                  title="View" 
                  onClick={() => handleView(row)}
                >
                  <Eye size={16} />
                </button>
                <button 
                  className="table-action-btn edit" 
                  title="Edit" 
                  onClick={() => handleEdit(row)}
                >
                  <Pencil size={16} />
                </button>
                <button 
                  className="table-action-btn delete" 
                  title="Delete" 
                  onClick={() => handleDelete(row.id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />

      {/* View Modal */}
{isViewModalOpen && selectedReservation && (
  <div className="modal-container" onClick={(e) => {
    if (e.target === e.currentTarget) setIsViewModalOpen(false);
  }}>
    <div className="modal-content view-modal">
      <div className="modal-header">
        <h2 className="modal-title">
          Reservation Details
          <span className="reservation-id">
            #{selectedReservation.room_reservation_id}
          </span>
        </h2>
        <button 
          className="modal-close-btn" 
          onClick={() => setIsViewModalOpen(false)}
          aria-label="Close modal"
        >
          <X size={24} />
        </button>
      </div>
      
      <div className="modal-body">
        <div className="view-modal-grid">
          {/* Guest Information */}
          <div className="view-section">
            <h3 className="section-title">Guest Information</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Salutation</span>
                <span className="field-value">{selectedReservation.salutation || "N/A"}</span>
              </div>
              <div className="field-group">
                <span className="field-label">First Name</span>
                <span className="field-value">{selectedReservation.first_name}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Last Name</span>
                <span className="field-value">{selectedReservation.last_name}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Email</span>
                <span className="field-value email-value">{selectedReservation.email || "N/A"}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Phone Number</span>
                <span className="field-value phone-value">{selectedReservation.phone_number}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Reservation Status</span>
                <span className={`field-value status-badge ${getStatusBadgeClass(selectedReservation.reservation_status)}`}>
                  {selectedReservation.reservation_status}
                </span>
              </div>
            </div>
          </div>

          {/* Stay Information */}
          <div className="view-section">
            <h3 className="section-title">Stay Information</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Arrival Date</span>
                <span className="field-value">{selectedReservation.arrival_date}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Departure Date</span>
                <span className="field-value">{selectedReservation.departure_date}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">No. of Nights</span>
                <span className="field-value">{selectedReservation.no_of_nights}</span>
              </div>
              <div className="field-group">
                <span className="field-label">No. of Rooms</span>
                <span className="field-value">{selectedReservation.no_of_rooms}</span>
              </div>
            </div>
          </div>

          {/* Room Details */}
          <div className="view-section">
            <h3 className="section-title">Room Details</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Room IDs</span>
                <span className="field-value json-value">
                  {Array.isArray(selectedReservation.room_ids) 
                    ? selectedReservation.room_ids.join(", ") 
                    : selectedReservation.room_ids}
                </span>
              </div>
              <div className="field-group">
                <span className="field-label">Room Type IDs</span>
                <span className="field-value json-value">
                  {Array.isArray(selectedReservation.room_type_ids) 
                    ? selectedReservation.room_type_ids.join(", ") 
                    : selectedReservation.room_type_ids}
                </span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Room Numbers</span>
                <span className="field-value json-value">
                  {Array.isArray(selectedReservation.room_no) 
                    ? selectedReservation.room_no.join(", ") 
                    : selectedReservation.room_no}
                </span>
              </div>
              <div className="field-group">
                <span className="field-label">Rate Types</span>
                <span className="field-value json-value">
                  {Array.isArray(selectedReservation.rate_type) 
                    ? selectedReservation.rate_type.join(", ") 
                    : selectedReservation.rate_type}
                </span>
              </div>
            </div>
          </div>

          {/* Occupancy */}
          <div className="view-section">
            <h3 className="section-title">Occupancy</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">No. of Adults</span>
                <span className="field-value">{selectedReservation.no_of_adults}</span>
              </div>
              <div className="field-group">
                <span className="field-label">No. of Children</span>
                <span className="field-value">{selectedReservation.no_of_children || 0}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Extra Bed Count</span>
                <span className="field-value">{selectedReservation.extra_bed_count || 0}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Extra Bed Cost</span>
                <span className="field-value">${selectedReservation.extra_bed_cost || 0}</span>
              </div>
            </div>
          </div>

          {/* Complementary */}
          <div className="view-section">
            <h3 className="section-title">Complementary</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Room Complementary</span>
                <span className="field-value">{selectedReservation.room_complementary || "None"}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Common Complementary</span>
                <span className="field-value">{selectedReservation.common_complementary || "None"}</span>
              </div>
            </div>
          </div>

          {/* Payment Details */}
          <div className="view-section">
            <h3 className="section-title">Payment Details</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Total Amount</span>
                <span className="field-value amount">${selectedReservation.total_amount || 0}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Tax Percentage</span>
                <span className="field-value">{selectedReservation.tax_percentage || 0}%</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Tax Amount</span>
                <span className="field-value amount">${selectedReservation.tax_amount || 0}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Tax Type ID</span>
                <span className="field-value">{selectedReservation.tax_type_id || "N/A"}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Discount Percentage</span>
                <span className="field-value">{selectedReservation.discount_percentage || 0}%</span>
              </div>
              <div className="field-group">
                <span className="field-label">Discount Amount</span>
                <span className="field-value amount discount">-${selectedReservation.discount_amount || 0}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Discount Type ID</span>
                <span className="field-value">{selectedReservation.discount_type_id || "N/A"}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Extra Charges</span>
                <span className="field-value amount">${selectedReservation.extra_charges || 0}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Room Amount</span>
                <span className="field-value amount">${selectedReservation.room_amount || 0}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Overall Amount</span>
                <span className="field-value amount total">${selectedReservation.overall_amount || 0}</span>
              </div>
            </div>
          </div>

          {/* Payment Status */}
          <div className="view-section">
            <h3 className="section-title">Payment Status</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Payment Method ID</span>
                <span className="field-value">{selectedReservation.payment_method_id}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Paying Amount</span>
                <span className="field-value amount">${selectedReservation.paying_amount || 0}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Paid Amount</span>
                <span className="field-value amount paid">${selectedReservation.paid_amount || 0}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Balance Amount</span>
                <span className="field-value amount balance">${selectedReservation.balance_amount || 0}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Extra Amount</span>
                <span className="field-value amount">${selectedReservation.extra_amount || 0}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Identity Type ID</span>
                <span className="field-value">{selectedReservation.identity_type_id}</span>
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div className="view-section">
            <h3 className="section-title">Additional Information</h3>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Booking Status ID</span>
                <span className="field-value">{selectedReservation.booking_status_id || "N/A"}</span>
              </div>
              <div className="field-group">
                <span className="field-label">Reservation Type</span>
                <span className="field-value">{selectedReservation.reservation_type || "N/A"}</span>
              </div>
            </div>
            <div className="field-pair">
              <div className="field-group">
                <span className="field-label">Confirmation Code</span>
                <span className="field-value code">{selectedReservation.confirmation_code || "N/A"}</span>
              </div>
              <div className="field-group full-width">
                <span className="field-label">Proof Document</span>
                <span className="field-value">{selectedReservation.proof_document || "No document uploaded"}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="modal-footer">
        <div className="footer-actions">
          <button 
            className="btn btn-icon"
            onClick={() => handlePrint(selectedReservation)}
            title="Print receipt"
          >
            <Printer size={18} />
            Print Receipt
          </button>
          <div className="action-buttons">
            <button 
              className="btn btn-secondary" 
              onClick={() => setIsViewModalOpen(false)}
            >
              Close
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setIsViewModalOpen(false);
                handleEdit(selectedReservation);
              }}
            >
              Edit Reservation
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
)}

      {isEditModalOpen && selectedReservation && (
        <div className="modal-container" onClick={(e) => {
          if (e.target === e.currentTarget) setIsEditModalOpen(false);
        }}>
          <div className="modal-content edit-modal">
            <div className="modal-header">
              <h2 className="modal-title">Edit Reservation</h2>
              <button 
                className="modal-close-btn" 
                onClick={() => setIsEditModalOpen(false)}
              >
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleEditSubmit} className="edit-modal-form">
              <div className="modal-body edit-modal-body">
                <div className="modal-body-content">
                    <div className="modal-section">
              <h3 className="section-title">Guest Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Salutation</label>
                  <select
                    name="salutation"
                    value={editFormData.salutation || ""}
                    onChange={handleInputChange}
                    className="form-select"
                  >
                    <option value="">Select</option>
                    <option value="Mr.">Mr.</option>
                    <option value="Mrs.">Mrs.</option>
                    <option value="Ms.">Ms.</option>
                    <option value="Dr.">Dr.</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">First Name *</label>
                  <input
                    type="text"
                    name="first_name"
                    value={editFormData.first_name || ""}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={editFormData.last_name || ""}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone Number *</label>
                  <input
                    type="text"
                    name="phone_number"
                    value={editFormData.phone_number || ""}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    name="email"
                    value={editFormData.email || ""}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Identity Type ID</label>
                  <input
                    type="number"
                    name="identity_type_id"
                    value={editFormData.identity_type_id || 1}
                    onChange={handleInputChange}
                    min="1"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            <div className="modal-section">
              <h3 className="section-title">Stay Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Arrival Date *</label>
                  <input
                    type="date"
                    name="arrival_date"
                    value={editFormData.arrival_date || ""}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Departure Date *</label>
                  <input
                    type="date"
                    name="departure_date"
                    value={editFormData.departure_date || ""}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Number of Nights *</label>
                  <input
                    type="number"
                    name="no_of_nights"
                    value={editFormData.no_of_nights || ""}
                    onChange={handleInputChange}
                    required
                    min="1"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            <div className="modal-section">
              <h3 className="section-title">Room Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Room Type IDs (JSON) *</label>
                  <input
                    type="text"
                    name="room_type_ids"
                    value={JSON.stringify(editFormData.room_type_ids || [])}
                    onChange={handleInputChange}
                    required
                    className="form-input json-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Room IDs (JSON) *</label>
                  <input
                    type="text"
                    name="room_ids"
                    value={JSON.stringify(editFormData.room_ids || [])}
                    onChange={handleInputChange}
                    required
                    className="form-input json-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Rate Type (JSON) *</label>
                  <input
                    type="text"
                    name="rate_type"
                    value={JSON.stringify(editFormData.rate_type || [])}
                    onChange={handleInputChange}
                    required
                    className="form-input json-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Number of Rooms *</label>
                  <input
                    type="number"
                    name="no_of_rooms"
                    value={editFormData.no_of_rooms || ""}
                    onChange={handleInputChange}
                    required
                    min="1"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Adults *</label>
                  <input
                    type="number"
                    name="no_of_adults"
                    value={editFormData.no_of_adults || ""}
                    onChange={handleInputChange}
                    required
                    min="1"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Children</label>
                  <input
                    type="number"
                    name="no_of_children"
                    value={editFormData.no_of_children || ""}
                    onChange={handleInputChange}
                    min="0"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Extra Bed Count</label>
                  <input
                    type="number"
                    name="extra_bed_count"
                    value={editFormData.extra_bed_count || 0}
                    onChange={handleInputChange}
                    min="0"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Extra Bed Cost</label>
                  <input
                    type="number"
                    name="extra_bed_cost"
                    value={editFormData.extra_bed_cost || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            <div className="modal-section">
              <h3 className="section-title">Reservation Details</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Payment Method ID *</label>
                  <input
                    type="number"
                    name="payment_method_id"
                    value={editFormData.payment_method_id || 1}
                    onChange={handleInputChange}
                    required
                    min="1"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Booking Status ID *</label>
                  <input
                    type="number"
                    name="booking_status_id"
                    value={editFormData.booking_status_id || 1}
                    onChange={handleInputChange}
                    required
                    min="1"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Reservation Type *</label>
                  <select
                    name="reservation_type"
                    value={editFormData.reservation_type || ""}
                    onChange={handleInputChange}
                    required
                    className="form-select"
                  >
                    <option value="RESERVATION">RESERVATION</option>
                    <option value="GROUP_RESERVATION">GROUP_RESERVATION</option>
                    <option value="CHECKIN">CHECKIN</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Reservation Status *</label>
                  <select
                    name="reservation_status"
                    value={editFormData.reservation_status || ""}
                    onChange={handleInputChange}
                    required
                    className="form-select"
                  >
                    <option value="Pending">Pending</option>
                    <option value="Confirmed">Confirmed</option>
                    <option value="Checked-in">Checked-in</option>
                    <option value="Checked-out">Checked-out</option>
                    <option value="Cancelled">Cancelled</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Room Complementary</label>
                  <input
                    type="text"
                    name="room_complementary"
                    value={editFormData.room_complementary || ""}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Common Complementary</label>
                  <input
                    type="text"
                    name="common_complementary"
                    value={editFormData.common_complementary || ""}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            <div className="modal-section">
              <h3 className="section-title">Payment Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Total Amount *</label>
                  <input
                    type="number"
                    name="total_amount"
                    value={editFormData.total_amount || ""}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Tax Percentage</label>
                  <input
                    type="number"
                    name="tax_percentage"
                    value={editFormData.tax_percentage || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Tax Amount</label>
                  <input
                    type="number"
                    name="tax_amount"
                    value={editFormData.tax_amount || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Discount Percentage</label>
                  <input
                    type="number"
                    name="discount_percentage"
                    value={editFormData.discount_percentage || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Discount Amount</label>
                  <input
                    type="number"
                    name="discount_amount"
                    value={editFormData.discount_amount || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Extra Charges</label>
                  <input
                    type="number"
                    name="extra_charges"
                    value={editFormData.extra_charges || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Overall Amount *</label>
                  <input
                    type="number"
                    name="overall_amount"
                    value={editFormData.overall_amount || ""}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Paid Amount</label>
                  <input
                    type="number"
                    name="paid_amount"
                    value={editFormData.paid_amount || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Balance Amount</label>
                  <input
                    type="number"
                    name="balance_amount"
                    value={editFormData.balance_amount || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Extra Amount</label>
                  <input
                    type="number"
                    name="extra_amount"
                    value={editFormData.extra_amount || 0}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setIsEditModalOpen(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn"
                >
                  Update Reservation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default Reservation;
import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, X } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const RESERVATION_STATUSES = ["Reserved", "Checked-In", "Cancelled", "No-Show", "Completed"];

const TableReservation = () => {
  const [data, setData] = useState([]);
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = {
    table_id: "",
    guest_name: "",
    guest_mobile: "",
    guest_email: "",
    reservation_date: "",
    start_time: "",
    end_time: "",
    no_of_guests: "",
    reservation_type: "Walk-In",
    occasion: "",
    special_requests: "",
  };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/restaurant/table_reservation"), APICall.getT("/restaurant/table")]).then(([rRes, tRes]) => {
      setData(rRes.status === "fulfilled" ? readList(rRes.value) : []);
      setTables(tRes.status === "fulfilled" ? readList(tRes.value) : []);
      if (rRes.status === "rejected") setError(errMsg(rRes.reason, "Failed to load reservations."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const tableLabel = (tableId) => {
    const t = tables.find((x) => x.id === tableId);
    return t ? `${t.table_name} (${t.table_code})` : tableId;
  };

  const openAddModal = () => {
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData({ ...row, table: tableLabel(row.table_id) });
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = async () => {
    if (!formData.table_id || !formData.guest_name.trim() || !formData.guest_mobile.trim() || !formData.reservation_date || !formData.start_time || !formData.no_of_guests) {
      setFormError("Table, guest name, mobile, date, start time and guest count are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT("/restaurant/table_reservation", {
        table_id: Number(formData.table_id),
        guest_name: formData.guest_name.trim(),
        guest_mobile: formData.guest_mobile.trim(),
        guest_email: formData.guest_email || null,
        reservation_date: formData.reservation_date,
        start_time: formData.start_time,
        end_time: formData.end_time || null,
        no_of_guests: Number(formData.no_of_guests),
        reservation_type: formData.reservation_type,
        occasion: formData.occasion || null,
        special_requests: formData.special_requests || null,
      });
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to create reservation."));
    } finally {
      setSaving(false);
    }
  };

  const updateStatus = async (row, reservation_status) => {
    try {
      await APICall.putT(`/restaurant/table_reservation/${row.id}`, { reservation_status });
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to update reservation."));
    }
  };

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Table Reservation"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Reservation",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "reservation_code", title: "Reservation Code", align: "center" },
          { key: "guest_name", title: "Guest Name", align: "center" },
          { key: "guest_mobile", title: "Contact", align: "center" },
          { key: "reservation_date", title: "Date", align: "center" },
          { key: "start_time", title: "Start", align: "center" },
          { key: "table_id", title: "Table", align: "center", type: "custom", render: (row) => tableLabel(row.table_id) },
          { key: "no_of_guests", title: "Guests", align: "center" },
          { key: "reservation_type", title: "Source", align: "center" },
          { key: "reservation_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => openViewModal(row)}>
                  <Eye size={16} />
                </button>
                {row.reservation_status === "Reserved" && (
                  <>
                    <button className="table-action-btn edit" title="Check in" onClick={() => updateStatus(row, "Checked-In")}>
                      <Pencil size={16} />
                    </button>
                  </>
                )}
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showViewModal && viewData && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>View Reservation</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>
            <div className="modal-body single view">
              {Object.entries(viewData).map(([key, value]) => (
                <div className="form-group" key={key}>
                  <label>{key.replace(/_/g, " ")}</label>
                  <input value={value ?? "-"} disabled />
                </div>
              ))}
            </div>
            <div className="modal-footer">
              {viewData.reservation_status === "Reserved" && (
                <button className="btn secondary" onClick={() => { updateStatus(viewData, "Cancelled"); closeViewModal(); }}>Cancel Reservation</button>
              )}
              <button className="btn primary" onClick={closeViewModal}>Close</button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Add Reservation</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body grid">
              <div className="form-group">
                <label>Table <span className="required">*</span></label>
                <select name="table_id" value={formData.table_id} onChange={handleChange}>
                  <option value="">— select —</option>
                  {tables.map((t) => (
                    <option key={t.id} value={t.id}>{t.table_name} ({t.table_code})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Guest Name <span className="required">*</span></label>
                <input name="guest_name" value={formData.guest_name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Contact Number <span className="required">*</span></label>
                <input name="guest_mobile" value={formData.guest_mobile} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" name="guest_email" value={formData.guest_email} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Reservation Date <span className="required">*</span></label>
                <input type="date" name="reservation_date" value={formData.reservation_date} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Start Time <span className="required">*</span></label>
                <input type="time" name="start_time" value={formData.start_time} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>End Time</label>
                <input type="time" name="end_time" value={formData.end_time} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>No. of Guests <span className="required">*</span></label>
                <input type="number" name="no_of_guests" value={formData.no_of_guests} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Occasion</label>
                <input name="occasion" value={formData.occasion} onChange={handleChange} placeholder="Birthday, Anniversary…" />
              </div>
              <div className="form-group">
                <label>Source</label>
                <select name="reservation_type" value={formData.reservation_type} onChange={handleChange}>
                  <option value="Walk-In">Walk-In</option>
                  <option value="Phone">Phone</option>
                  <option value="Online">Online</option>
                  <option value="Hotel Guest">Hotel Guest</option>
                </select>
              </div>
              <div className="form-group">
                <label>Special Requests</label>
                <input name="special_requests" value={formData.special_requests} onChange={handleChange} />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal} disabled={saving}>Close</button>
              <button className="btn primary" onClick={handleSave} disabled={saving}>{saving ? "Saving…" : "Submit"}</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TableReservation;

import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, X } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "../../MasterData/MasterData.css";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const GuestManagement = () => {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showGuestModal, setShowGuestModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = { first_name: "", last_name: "", mobile: "", email: "", guest_type: "Walk-In", food_preferences: "", special_notes: "" };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    APICall.getT("/restaurant/guest")
      .then((res) => setGuests(readList(res)))
      .catch((err) => setError(errMsg(err, "Failed to load guests.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setShowGuestModal(true);
  };
  const openEditModal = (row) => {
    setEditId(row.id);
    setFormError(null);
    setFormData({
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      mobile: row.mobile || "",
      email: row.email || "",
      guest_type: row.guest_type || "Walk-In",
      food_preferences: (row.food_preferences || []).join(", "),
      special_notes: row.special_notes || "",
    });
    setShowGuestModal(true);
  };
  const closeGuestModal = () => {
    if (saving) return;
    setShowGuestModal(false);
  };

  const openViewModal = async (row) => {
    try {
      const res = await APICall.getT(`/restaurant/guest/${row.id}`);
      setViewData(res?.data || row);
      setShowViewModal(true);
    } catch (err) {
      setError(errMsg(err, "Failed to load guest profile."));
    }
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const saveGuest = async () => {
    if (!formData.first_name.trim() || !formData.mobile.trim()) {
      setFormError("First name and mobile number are required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    const payload = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name || null,
      mobile: formData.mobile.trim(),
      email: formData.email || null,
      guest_type: formData.guest_type,
      food_preferences: formData.food_preferences ? formData.food_preferences.split(",").map((s) => s.trim()).filter(Boolean) : null,
      special_notes: formData.special_notes || null,
    };
    try {
      if (editId) {
        await APICall.putT(`/restaurant/guest/${editId}`, payload);
      } else {
        await APICall.postT("/restaurant/guest", payload);
      }
      setShowGuestModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save guest."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {error && <div className="rmv-alert" role="alert"><span>{error}</span></div>}

      <TableTemplate
        title="Guests"
        searchable
        pagination
        loading={loading}
        actionButton={{ label: "Add Guest", variant: "primary", onClick: openAddModal }}
        columns={[
          { key: "guest_code", title: "Guest ID" },
          { key: "first_name", title: "Guest Name", type: "custom", render: (row) => `${row.first_name || ""} ${row.last_name || ""}`.trim() },
          { key: "mobile", title: "Mobile No" },
          { key: "guest_type", title: "Guest Type" },
          { key: "loyalty_points", title: "Loyalty Points", align: "center" },
          { key: "status", title: "Status", type: "badge", align: "center" },
          {
            key: "actions",
            title: "Action",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => openViewModal(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => openEditModal(row)}>
                  <Pencil size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={guests}
      />

      {showGuestModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "900px", width: "95%" }}>
            <div className="modal-header">
              <h3>{editId ? "Edit Guest" : "Add Guest"}</h3>
              <button onClick={closeGuestModal}><X size={18} /></button>
            </div>

            {formError && <div className="rmv-alert" role="alert"><span>{formError}</span></div>}

            <div className="modal-body single">
              <div className="grid-3">
                <div className="form-group">
                  <label>First Name <span className="required">*</span></label>
                  <input name="first_name" value={formData.first_name} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input name="last_name" value={formData.last_name} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Mobile Number <span className="required">*</span></label>
                  <input name="mobile" value={formData.mobile} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" name="email" value={formData.email} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Guest Type</label>
                  <select name="guest_type" value={formData.guest_type} onChange={handleChange}>
                    <option value="Walk-In">Walk-In</option>
                    <option value="Regular">Regular</option>
                    <option value="VIP">VIP</option>
                    <option value="Hotel Guest">Hotel Guest</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Food Preferences / Allergies</label>
                  <input name="food_preferences" value={formData.food_preferences} onChange={handleChange} placeholder="Veg, No nuts, ..." />
                </div>
                <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                  <label>Special Notes</label>
                  <input name="special_notes" value={formData.special_notes} onChange={handleChange} />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeGuestModal} disabled={saving}>Cancel</button>
              <button className="btn primary" onClick={saveGuest} disabled={saving}>{saving ? "Saving…" : "Save Guest"}</button>
            </div>
          </div>
        </div>
      )}

      {showViewModal && viewData && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: "500px", width: "95%" }}>
            <div className="modal-header">
              <h3>Guest Profile</h3>
              <button onClick={closeViewModal}><X size={18} /></button>
            </div>
            <div className="modal-body single">
              <p><strong>Name:</strong> {viewData.first_name} {viewData.last_name}</p>
              <p><strong>Mobile:</strong> {viewData.mobile}</p>
              <p><strong>Guest Type:</strong> {viewData.guest_type}</p>
              <p><strong>Total Visits:</strong> {(viewData.visit_history || []).length}</p>
              <p><strong>Loyalty Points:</strong> {viewData.loyalty_points}</p>
              <p><strong>Preferences:</strong> {(viewData.food_preferences || []).join(", ") || "-"}</p>
              <p><strong>Notes:</strong> {viewData.special_notes || "-"}</p>
            </div>
            <div className="modal-footer">
              <button className="btn secondary" onClick={closeViewModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default GuestManagement;

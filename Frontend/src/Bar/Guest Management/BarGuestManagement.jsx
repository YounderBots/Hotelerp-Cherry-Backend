import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import IconButton from "../../stories/IconButton";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Pencil } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const GUEST_TYPES = [
  { value: "Walk-In", label: "Walk-In" },
  { value: "Regular", label: "Regular" },
  { value: "VIP", label: "VIP" },
  { value: "Hotel Guest", label: "Hotel Guest" },
];

const BarGuestManagement = () => {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showGuestModal, setShowGuestModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

  const initialForm = { first_name: "", last_name: "", mobile: "", email: "", guest_type: "Walk-In", special_notes: "" };
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    APICall.getT("/bar/guest")
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
      const res = await APICall.getT(`/bar/guest/${row.id}`);
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
      special_notes: formData.special_notes || null,
    };
    try {
      if (editId) {
        await APICall.putT(`/bar/guest/${editId}`, payload);
      } else {
        await APICall.postT("/bar/guest", payload);
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
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Guests"
        hasActionButton
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
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openViewModal(row)} />
                <IconButton variant="subtle" size="small" icon={<Pencil size={16} />} ariaLabel="Edit" onClick={() => openEditModal(row)} />
              </div>
            ),
          },
        ]}
        data={guests}
      />

      {showGuestModal && (
        <Modal
          isOpen={showGuestModal}
          title={editId ? "Edit Guest" : "Add Guest"}
          onClose={closeGuestModal}
          size="large"
          bodyLayout="grid"
          showFooter
          actions={[
            { label: "Cancel", variant: "secondary", onClick: closeGuestModal, disabled: saving },
            { label: saving ? "Saving…" : "Save Guest", variant: "primary", onClick: saveGuest, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <Input label="First Name" required name="first_name" value={formData.first_name} onChange={handleChange} />
          <Input label="Last Name" name="last_name" value={formData.last_name} onChange={handleChange} />
          <Input label="Mobile Number" required name="mobile" value={formData.mobile} onChange={handleChange} />
          <Input label="Email" type="email" name="email" value={formData.email} onChange={handleChange} />
          <Select label="Guest Type" name="guest_type" value={formData.guest_type} onChange={handleChange} options={GUEST_TYPES} />
          <div style={{ gridColumn: "1 / -1" }}>
            <Input label="Special Notes" name="special_notes" value={formData.special_notes} onChange={handleChange} />
          </div>
        </Modal>
      )}

      {showViewModal && viewData && (
        <Modal
          isOpen={showViewModal}
          title="Guest Profile"
          onClose={closeViewModal}
          size="medium"
          bodyLayout="single"
          showFooter
          actions={[{ label: "Close", variant: "secondary", onClick: closeViewModal }]}
        >
          <p><strong>Name:</strong> {viewData.first_name} {viewData.last_name}</p>
          <p><strong>Mobile:</strong> {viewData.mobile}</p>
          <p><strong>Guest Type:</strong> {viewData.guest_type}</p>
          <p><strong>Total Visits:</strong> {(viewData.visit_history || []).length}</p>
          <p><strong>Loyalty Points:</strong> {viewData.loyalty_points}</p>
          <p><strong>Notes:</strong> {viewData.special_notes || "-"}</p>
        </Modal>
      )}
    </>
  );
};

export default BarGuestManagement;

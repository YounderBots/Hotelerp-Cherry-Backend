import React, { useRef, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import Input from "../../stories/Form/Input";
import PhoneInput from "../../stories/Form/PhoneInput";
import { regionOf } from "../../stories/Form/phone";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import Button from "../../stories/Button";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatCount, formatDate, formatPrecise } from "../../functions/formatters";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/**
 * Restaurant guest directory.
 *
 * The four guest types are the `guest_type_enum` the column is declared with
 * (models.py: Walk-In | Regular | VIP | Hotel Guest), not master data. Sourcing
 * them from an API would invent a second place for a value the database
 * already constrains, and any value not in the enum is rejected on write.
 */
const GUEST_TYPES = [
  { value: "Walk-In", label: "Walk-In" },
  { value: "Regular", label: "Regular" },
  { value: "VIP", label: "VIP" },
  { value: "Hotel Guest", label: "Hotel Guest" },
];

const initialForm = {
  // The country the number is typed in. It is sent with the number, not
  // stored with it: a national number with no country code is ambiguous
  // and the API refuses to guess one (C-086).
  phone_region: "IN",
  first_name: "",
  last_name: "",
  mobile: "",
  email: "",
  guest_type: "Walk-In",
  food_preferences: "",
  special_notes: "",
};

const fullName = (row) => `${row?.first_name || ""} ${row?.last_name || ""}`.trim() || "—";

const GuestManagement = () => {
  const perms = usePagePermissions("/guest_management");

  const {
    data: guests,
    loading,
    error,
    reload: load,
  } = useApiResource(() => APICall.getT("/restaurant/guest"), {
    select: readList,
    fallback: "Failed to load guests.",
  });

  const { toast, showToast } = useToast();

  const [showGuestModal, setShowGuestModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [viewData, setViewData] = useState(null);
  const [deleteRow, setDeleteRow] = useState(null);
  const [saving, setSaving] = useState(false);
  const savingRef = useRef(false);
  const deletingRef = useRef(false);
  const [deleting, setDeleting] = useState(false);
  const [formError, setFormError] = useState(null);
  // The phone field's own message, kept next to the field rather than
  // only in the form-level banner.
  const [phoneError, setPhoneError] = useState(null);
  const [formData, setFormData] = useState(initialForm);

  // C-066: Address, feedback, and loyalty management
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [showLoyaltyModal, setShowLoyaltyModal] = useState(false);
  const [addressForm, setAddressForm] = useState({ address: "", city: "", state: "", country: "", postal_code: "" });
  const [feedbackForm, setFeedbackForm] = useState({ rating: 5, comments: "" });
  const [loyaltyForm, setLoyaltyForm] = useState({ points: "", reason: "" });
  const [actionError, setActionError] = useState(null);
  const [actionSaving, setActionSaving] = useState(false);
  const actionSavingRef = useRef(false);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setPhoneError(null);
    setShowGuestModal(true);
  };

  const openEditModal = (row) => {
    setEditId(row.id);
    setFormError(null);
    setPhoneError(null);
    // Prefilled from the row itself, spread over initialForm so every key the
    // form reads exists (the phone field's `region` used to come out undefined
    // here, which dropped the selector back to the property's default country
    // and re-read somebody else's number as local). `regionOf` reads the
    // country back out of the stored E.164, so an international guest keeps
    // their own country in the selector.
    setFormData({
      ...initialForm,
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      mobile: row.mobile || "",
      phone_region: regionOf(row.mobile) || initialForm.phone_region,
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
    setEditId(null);
    setFormData(initialForm);
    setFormError(null);
    setPhoneError(null);
  };

  // The list row carries the guest but not their addresses or visit history,
  // so the profile is fetched. A failure falls back to the row rather than
  // opening an empty modal — the identity fields are all present on it.
  const openViewModal = async (row) => {
    try {
      const res = await APICall.getT(`/restaurant/guest/${row.id}`);
      setViewData(res?.data || row);
    } catch (err) {
      showToast(errMsg(err, "Failed to load the full profile; showing the list values."), "error");
      setViewData(row);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const saveGuest = async () => {
    // Guard plus the disabled Save below: without both, a double click posts
    // twice, and the server answers the second one with "a guest with this
    // mobile number already exists".
    if (saving || savingRef.current) return;
    if (!formData.first_name.trim() || !formData.mobile.trim()) {
      setFormError("First name and mobile number are required.");
      return;
    }

    savingRef.current = true;
    setSaving(true);
    setFormError(null);
    const payload = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim() || null,
      mobile: formData.mobile.trim(),
        phone_region: formData.phone_region,
      email: formData.email.trim() || null,
      guest_type: formData.guest_type,
      food_preferences: formData.food_preferences
        ? formData.food_preferences.split(",").map((s) => s.trim()).filter(Boolean)
        : null,
      special_notes: formData.special_notes.trim() || null,
    };

    try {
      if (editId) {
        await APICall.putT(`/restaurant/guest/${editId}`, payload);
        showToast("Guest updated successfully", "update");
      } else {
        await APICall.postT("/restaurant/guest", payload);
        showToast("Guest added successfully", "success");
      }
      setShowGuestModal(false);
      setEditId(null);
      setFormData(initialForm);
      await load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to save guest."));
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  };

  // DELETE deactivates rather than removing: the guest keeps their visit
  // history and bills, and simply drops out of the active directory.
  const confirmDelete = async () => {
    if (!deleteRow || deleting || deletingRef.current) return;
    deletingRef.current = true;
    setDeleting(true);
    try {
      await APICall.deleteT(`/restaurant/guest/${deleteRow.id}`);
      showToast("Guest deactivated successfully", "delete");
      await load();
      setDeleteRow(null);
    } catch (err) {
      showToast(errMsg(err, "Failed to deactivate guest."), "error");
    } finally {
      deletingRef.current = false;
      setDeleting(false);
    }
  };

  // C-066: Address management
  const openAddressModal = () => {
    setAddressForm({ address: "", city: "", state: "", country: "", postal_code: "" });
    setActionError(null);
    setShowAddressModal(true);
  };

  const saveAddress = async () => {
    if (actionSaving || actionSavingRef.current) return;
    actionSavingRef.current = true;
    setActionSaving(true);
    setActionError(null);
    try {
      await APICall.postT(`/restaurant/guest/${viewData.id}/address`, addressForm);
      showToast("Address added successfully", "success");
      setShowAddressModal(false);
      // Refresh the view data to show the new address
      const res = await APICall.getT(`/restaurant/guest/${viewData.id}`);
      setViewData(res?.data || viewData);
    } catch (err) {
      setActionError(errMsg(err, "Failed to add address."));
    } finally {
      actionSavingRef.current = false;
      setActionSaving(false);
    }
  };

  // C-066: Feedback management
  const openFeedbackModal = () => {
    setFeedbackForm({ rating: 5, comments: "" });
    setActionError(null);
    setShowFeedbackModal(true);
  };

  const saveFeedback = async () => {
    if (actionSaving || actionSavingRef.current) return;
    actionSavingRef.current = true;
    setActionSaving(true);
    setActionError(null);
    try {
      await APICall.postT(`/restaurant/guest/${viewData.id}/feedback`, feedbackForm);
      showToast("Feedback added successfully", "success");
      setShowFeedbackModal(false);
    } catch (err) {
      setActionError(errMsg(err, "Failed to add feedback."));
    } finally {
      actionSavingRef.current = false;
      setActionSaving(false);
    }
  };

  // C-066: Loyalty management
  const openLoyaltyModal = () => {
    setLoyaltyForm({ points: "", reason: "" });
    setActionError(null);
    setShowLoyaltyModal(true);
  };

  const saveLoyalty = async () => {
    if (actionSaving || actionSavingRef.current) return;
    const points = parseFloat(loyaltyForm.points);
    if (!Number.isFinite(points) || points === 0) {
      setActionError("Points must be a non-zero number.");
      return;
    }
    actionSavingRef.current = true;
    setActionSaving(true);
    setActionError(null);
    try {
      await APICall.postT(`/restaurant/guest/${viewData.id}/loyalty`, { points, reason: loyaltyForm.reason || null });
      showToast("Loyalty points updated successfully", "success");
      setShowLoyaltyModal(false);
      // Refresh the view data to show updated points
      const res = await APICall.getT(`/restaurant/guest/${viewData.id}`);
      setViewData(res?.data || viewData);
    } catch (err) {
      setActionError(errMsg(err, "Failed to update loyalty points."));
    } finally {
      actionSavingRef.current = false;
      setActionSaving(false);
    }
  };

  /* ================= UI ================= */

  const visits = viewData?.visit_history || [];
  const addresses = viewData?.addresses || [];

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Guests"
        loading={loading}
        emptyMessage="No guests yet. Add the first one to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Guest",
          variant: "primary",
          size: "medium",
          onClick: openAddModal,
        }}
        columns={[
          { key: "guest_code", title: "Guest ID", align: "left" },
          {
            key: "first_name",
            title: "Guest Name",
            align: "left",
            type: "custom",
            render: fullName,
            exportValue: fullName,
          },
          { key: "mobile", title: "Mobile No", align: "left" },
          { key: "guest_type", title: "Guest Type", align: "left" },
          {
            key: "loyalty_points",
            title: "Loyalty Points",
            align: "right",
            type: "custom",
            render: (row) => formatPrecise(row.loyalty_points),
            exportValue: (row) => formatPrecise(row.loyalty_points),
          },
          // The Status column was dropped: list_guests filters to ACTIVE, so
          // it could only ever render the single value "ACTIVE" on every row.
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label="guest"
                canEdit={perms.edit}
                canDelete={perms.delete}
                onView={() => openViewModal(row)}
                onEdit={() => openEditModal(row)}
                onDelete={() => setDeleteRow(row)}
              />
            ),
          },
        ]}
        data={guests}
      />

      {/* ================= ADD / EDIT ================= */}
      <Modal
        isOpen={showGuestModal}
        title={editId ? "Edit Guest" : "Add Guest"}
        onClose={closeGuestModal}
        size="large"
        bodyLayout="grid"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeGuestModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: saveGuest,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} className="field-full" />

        <Input
          label="First Name"
          required
          name="first_name"
          placeholder="e.g. Priya"
          value={formData.first_name}
          onChange={handleChange}
        />
        <Input
          label="Last Name"
          name="last_name"
          placeholder="e.g. Sharma"
          value={formData.last_name}
          onChange={handleChange}
        />
        <PhoneInput
          label="Mobile Number"
          required
          name="mobile"
          // Remounts per record: the field keeps the digits the user last saw
          // in local state, so a key tied to the record being edited is what
          // guarantees Add always opens empty and Edit always opens on that
          // guest's own number, even when the modal unmounts late (its close
          // animation) and the two records meet in the same field instance.
          key={editId ? `guest-${editId}` : "guest-new"}
          value={formData.mobile}
          region={formData.phone_region}
          error={Boolean(phoneError)}
          helperText={phoneError}
          onChange={(e164, region, result) => {
            setFormData((p) => ({ ...p, mobile: e164, phone_region: region }));
            setPhoneError(
              result && result.ok === false && !result.incomplete ? result.message : null,
            );
          }}
        />
        <Input
          label="Email"
          type="email"
          name="email"
          placeholder="guest@example.com"
          value={formData.email}
          onChange={handleChange}
        />
        <Select
          label="Guest Type"
          name="guest_type"
          value={formData.guest_type}
          onChange={handleChange}
          options={GUEST_TYPES}
        />
        <Input
          label="Food Preferences / Allergies"
          name="food_preferences"
          placeholder="Veg, No nuts, …"
          value={formData.food_preferences}
          onChange={handleChange}
        />
        <div className="field-full">
          <Textarea
            label="Special Notes"
            name="special_notes"
            rows={3}
            placeholder="Anything the floor should know before seating this guest."
            value={formData.special_notes}
            onChange={handleChange}
          />
        </div>
      </Modal>

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Guest Profile"
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
          { label: "Add Address", variant: "secondary", onClick: openAddressModal },
          { label: "Add Feedback", variant: "secondary", onClick: openFeedbackModal },
          { label: "Adjust Loyalty", variant: "secondary", onClick: openLoyaltyModal },
        ]}
      >
        <ViewSection title="Guest">
          <DetailList columns={3}>
            <DetailItem label="Guest ID" value={viewData?.guest_code} />
            <DetailItem label="Name" value={viewData && fullName(viewData)} />
            <DetailItem label="Guest Type" value={viewData?.guest_type} />
            <DetailItem label="Mobile" value={viewData?.mobile} />
            <DetailItem label="Email" value={viewData?.email} />
            <DetailItem
              label="Loyalty Points"
              value={viewData && formatPrecise(viewData.loyalty_points)}
            />
          </DetailList>
        </ViewSection>

        <ViewSection title="Preferences">
          <DetailList columns={2}>
            <DetailItem
              label="Food Preferences / Allergies"
              value={(viewData?.food_preferences || []).join(", ")}
            />
            <DetailItem label="Special Notes" value={viewData?.special_notes} />
          </DetailList>
        </ViewSection>

        {addresses.length > 0 && (
          <ViewSection title="Addresses">
            <DetailList columns={2}>
              {addresses.map((a) => (
                <DetailItem
                  key={a.id}
                  label={[a.city, a.state].filter(Boolean).join(", ") || "Address"}
                  value={[a.address, a.city, a.state, a.country, a.postal_code]
                    .filter(Boolean)
                    .join(", ")}
                />
              ))}
            </DetailList>
          </ViewSection>
        )}

        <ViewSection title={`Visit History (${formatCount(visits.length)})`}>
          {visits.length === 0 ? (
            <p className="view-section__empty">No recorded visits yet.</p>
          ) : (
            <DetailList columns={3}>
              {visits.slice(0, 12).map((v) => (
                <DetailItem
                  key={v.id}
                  label={formatDate(v.visit_date)}
                  value={[v.visit_type, v.total_amount != null ? formatPrecise(v.total_amount) : null]
                    .filter(Boolean)
                    .join(" · ")}
                />
              ))}
            </DetailList>
          )}
        </ViewSection>
      </Modal>

      {/* ================= ADDRESS MODAL ================= */}
      <Modal
        isOpen={showAddressModal}
        title="Add Address"
        onClose={() => setShowAddressModal(false)}
        size="medium"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: () => setShowAddressModal(false), disabled: actionSaving },
          { label: actionSaving ? "Saving…" : "Save", variant: "primary", onClick: saveAddress, disabled: actionSaving },
        ]}
      >
        <ErrorAlert message={actionError} className="field-full" />
        <Input label="Address" name="address" placeholder="Street address" value={addressForm.address} onChange={(e) => setAddressForm((p) => ({ ...p, address: e.target.value }))} />
        <Input label="City" name="city" placeholder="City" value={addressForm.city} onChange={(e) => setAddressForm((p) => ({ ...p, city: e.target.value }))} />
        <Input label="State" name="state" placeholder="State" value={addressForm.state} onChange={(e) => setAddressForm((p) => ({ ...p, state: e.target.value }))} />
        <Input label="Country" name="country" placeholder="Country" value={addressForm.country} onChange={(e) => setAddressForm((p) => ({ ...p, country: e.target.value }))} />
        <Input label="Postal Code" name="postal_code" placeholder="Postal code" value={addressForm.postal_code} onChange={(e) => setAddressForm((p) => ({ ...p, postal_code: e.target.value }))} />
      </Modal>

      {/* ================= FEEDBACK MODAL ================= */}
      <Modal
        isOpen={showFeedbackModal}
        title="Add Feedback"
        onClose={() => setShowFeedbackModal(false)}
        size="medium"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: () => setShowFeedbackModal(false), disabled: actionSaving },
          { label: actionSaving ? "Saving…" : "Save", variant: "primary", onClick: saveFeedback, disabled: actionSaving },
        ]}
      >
        <ErrorAlert message={actionError} className="field-full" />
        <Select
          label="Rating"
          name="rating"
          value={feedbackForm.rating}
          onChange={(e) => setFeedbackForm((p) => ({ ...p, rating: parseInt(e.target.value, 10) }))}
          options={[
            { value: 5, label: "5 - Excellent" },
            { value: 4, label: "4 - Good" },
            { value: 3, label: "3 - Average" },
            { value: 2, label: "2 - Poor" },
            { value: 1, label: "1 - Terrible" },
          ]}
        />
        <div className="field-full">
          <Textarea
            label="Comments"
            name="comments"
            rows={3}
            placeholder="Optional comments about the guest's experience"
            value={feedbackForm.comments}
            onChange={(e) => setFeedbackForm((p) => ({ ...p, comments: e.target.value }))}
          />
        </div>
      </Modal>

      {/* ================= LOYALTY MODAL ================= */}
      <Modal
        isOpen={showLoyaltyModal}
        title="Adjust Loyalty Points"
        onClose={() => setShowLoyaltyModal(false)}
        size="medium"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: () => setShowLoyaltyModal(false), disabled: actionSaving },
          { label: actionSaving ? "Saving…" : "Save", variant: "primary", onClick: saveLoyalty, disabled: actionSaving },
        ]}
      >
        <ErrorAlert message={actionError} className="field-full" />
        <Input
          label="Points (positive to earn, negative to redeem)"
          name="points"
          type="number"
          placeholder="e.g. 100 or -50"
          value={loyaltyForm.points}
          onChange={(e) => setLoyaltyForm((p) => ({ ...p, points: e.target.value }))}
        />
        <Input
          label="Reason (optional)"
          name="reason"
          placeholder="e.g. Stay reward, Redemption"
          value={loyaltyForm.reason}
          onChange={(e) => setLoyaltyForm((p) => ({ ...p, reason: e.target.value }))}
        />
      </Modal>

      {/* ================= DELETE ================= */}
      <ConfirmModal
        isOpen={!!deleteRow}
        onClose={() => (deleting ? null : setDeleteRow(null))}
        onConfirm={confirmDelete}
        title="Deactivate Guest"
        confirmText={deleting ? "Deactivating…" : "Deactivate"}
        size="small"
        destructive
      >
        {`Deactivate ${fullName(deleteRow)}? They will no longer appear in the guest directory. Their visit history and bills are kept.`}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default GuestManagement;

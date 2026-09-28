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
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatCount, formatDate, formatPrecise } from "../../functions/formatters";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/**
 * Bar guest directory.
 *
 * The four guest types are the `guest_type_enum` the column is declared with
 * (models.py `bar_guest_type_enum`: Walk-In | Regular | VIP | Hotel Guest), not
 * master data. Sourcing
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
  first_name: "",
  last_name: "",
  mobile: "",
  // The country the mobile is typed in. It travels with the number because a
  // national number with no country is ambiguous, and the API refuses to guess
  // one (C-086). It is not stored: the number itself is stored as E.164.
  phone_region: "IN",
  email: "",
  guest_type: "Walk-In",
  special_notes: "",
};

const fullName = (row) => `${row?.first_name || ""} ${row?.last_name || ""}`.trim() || "—";

const BarGuestManagement = () => {
  const perms = usePagePermissions("/bar_guest_management");

  const {
    data: guests,
    loading,
    error,
    reload: load,
  } = useApiResource(() => APICall.getT("/bar/guest"), {
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
  const [phoneError, setPhoneError] = useState(null);
  const [formData, setFormData] = useState(initialForm);

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
    setFormData({
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      mobile: row.mobile || "",
      // An existing row is stored as E.164, so the country is the one that
      // number belongs to. Shown in the selector rather than assumed, so editing
      // a guest from another country does not re-read their number as local.
      phone_region: regionOf(row.mobile) || "IN",
      email: row.email || "",
      guest_type: row.guest_type || "Walk-In",
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
  };

  // The list row carries the guest but not their addresses or visit history,
  // so the profile is fetched. A failure falls back to the row rather than
  // opening an empty modal — the identity fields are all present on it.
  const openViewModal = async (row) => {
    try {
      const res = await APICall.getT(`/bar/guest/${row.id}`);
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
    // A number that is still being typed is not an error yet, so the field's own
    // message is shown rather than a generic "invalid" at the top of the form.
    if (phoneError) {
      setFormError("Check the mobile number before saving.");
      return;
    }

    savingRef.current = true;
    setSaving(true);
    setFormError(null);
    const payload = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim() || null,
      // Already E.164 from PhoneInput; sent as typed, with the country that
      // says how to read a national one.
      mobile: formData.mobile.trim(),
      phone_region: formData.phone_region,
      email: formData.email.trim() || null,
      guest_type: formData.guest_type,
      special_notes: formData.special_notes.trim() || null,
    };

    try {
      if (editId) {
        await APICall.putT(`/bar/guest/${editId}`, payload);
        showToast("Guest updated successfully", "update");
      } else {
        await APICall.postT("/bar/guest", payload);
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
      await APICall.deleteT(`/bar/guest/${deleteRow.id}`);
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

  /* ================= UI ================= */

  const visits = viewData?.visit_history || [];
  const addresses = viewData?.addresses || [];

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Bar Guests"
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
          value={formData.mobile}
          region={formData.phone_region}
          error={Boolean(phoneError)}
          helperText={phoneError}
          onChange={(e164, region, result) => {
            setFormData((p) => ({ ...p, mobile: e164, phone_region: region }));
            setPhoneError(result && result.ok === false && !result.incomplete ? result.message : null);
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
        <div className="field-full">
          <Textarea
            label="Special Notes"
            name="special_notes"
            rows={3}
            placeholder="Anything the bar should know before serving this guest."
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
        actions={[{ label: "Close", variant: "secondary", onClick: () => setViewData(null) }]}
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

        <ViewSection title="Notes">
          <DetailList columns={1}>
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

export default BarGuestManagement;
